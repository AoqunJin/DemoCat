import numpy as np
from functools import partial
import jax
from vlasuite.octo.model.octo_model import OctoModel
from vlasuite.octo.utils.train_callbacks import supply_rng


def normalize_gripper_action(action, binarize=True):
    """
    Changes gripper action (last dimension of action vector) from [0,1] to [-1,+1].
    Necessary for some environments (not Bridge) because the dataset wrapper standardizes gripper actions to [0,1].
    Note that unlike the other action dimensions, the gripper action is not normalized to [-1,+1] by default by
    the dataset wrapper.

    Normalization formula: y = 2 * (x - orig_low) / (orig_high - orig_low) - 1
    """
    # Just normalize the last action to [-1,+1].
    orig_low, orig_high = 0.0, 1.0
    action[..., -1] = 2 * (action[..., -1] - orig_low) / (orig_high - orig_low) - 1

    if binarize:
        # Binarize to -1 or +1.
        action[..., -1] = np.sign(action[..., -1])

    return action


def invert_gripper_action(action):
    """
    Flips the sign of the gripper action (last dimension of action vector).
    This is necessary for some environments where -1 = open, +1 = close, since
    the RLDS dataloader aligns gripper actions such that 0 = close, 1 = open.
    """
    action[..., -1] = action[..., -1] * -1.0
    return action


class OctoInf():
    def __init__(self, model_dir):
        print("Loading model")
        self.model = OctoModel.load_pretrained(model_dir)

        self.policy_fn = supply_rng(
            partial(
                self.model.sample_actions,
                unnormalization_statistics=self.model.dataset_statistics["metaworld_mt10"]["action"],
            ),
        )
        self.dataset_statistics = self.model.dataset_statistics["metaworld_mt10"]
        print("Model loaded")

    def run(self, obs, language_instruction):
        # horizon must be <= max_horizon
        task = self.model.create_tasks(texts=language_instruction)
        action = self.policy_fn(jax.tree_map(lambda x: x[None], obs), task)[0]  # (bs, l, 4)[0]
        action = np.array(action)
        action = invert_gripper_action(normalize_gripper_action(action, binarize=False))
        # print(action)
        return action
