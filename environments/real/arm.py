from .robotic_arm_package.robotic_arm import *
import sys


def init(joint=[45, 0, -120, 30, 90, 0]):
    def mcallback(data):
        print("MCallback MCallback MCallback")
        # 判断接口类型
        if data.codeKey == MOVEJ_CANFD_CB:  # 角度透传
            print("透传结果:", data.errCode)
            print("当前角度:", data.joint[0], data.joint[1], data.joint[2], data.joint[3], data.joint[4], data.joint[5])
        elif data.codeKey == MOVEP_CANFD_CB:  # 位姿透传
            print("透传结果:", data.errCode)
            print("当前角度:", data.joint[0], data.joint[1], data.joint[2], data.joint[3], data.joint[4], data.joint[5])
            print("当前位姿:", data.pose.position.x, data.pose.position.y, data.pose.position.z, data.pose.euler.rx,
                  data.pose.euler.ry, data.pose.euler.rz)
        elif data.codeKey == FORCE_POSITION_MOVE_CB:  # 力位混合透传
            print("透传结果:", data.errCode)
            print("当前力度：", data.nforce)


    # 连接机械臂，注册回调函数
    callback = CANFD_Callback(mcallback)
    arm = Arm(RM65, "192.168.1.18", callback)
    
    # 初始位置
    arm.Set_Gripper_Release(200, block=False)
    assert not arm.Movej_Cmd(joint, 20, 0)
    return arm

def init_pose(arm, pose=[45, 0, -120, 30, 90, 0]):
    arm.Set_Gripper_Release(200, block=False)
    arm.Movej_Cmd(pose, 20, 0)

def go_forward(arm, v=15):
    arm.Pos_Teach_Cmd(type=1, direction=0, v=v, block=False)
    
def go_backward(arm, v=15):
    arm.Pos_Teach_Cmd(type=1, direction=1, v=v, block=False)
    
def go_left(arm, v=15):
    arm.Pos_Teach_Cmd(type=0, direction=1, v=v, block=False)
    
def go_right(arm, v=15):
    arm.Pos_Teach_Cmd(type=0, direction=0, v=v, block=False)
    
def go_up(arm, v=15):
    arm.Pos_Teach_Cmd(type=2, direction=1, v=v, block=False)
    
def go_down(arm, v=15):
    arm.Pos_Teach_Cmd(type=2, direction=0, v=v, block=False)
    
def grasp_open_or_close():
    state = 1  # Open
    def grasp_open(arm):
        arm.Set_Gripper_Release(200, block=False)
        
    def grasp_close(arm):
        arm.Set_Gripper_Pick_On(500, 500, block=False)    
    
    def f(arm, v=None):
        nonlocal state
        state = -state
        if state == -1:
            grasp_close(arm)
        else:
            grasp_open(arm)
    
    return f

def grasp_open(arm):
    arm.Set_Gripper_Release(200, block=False)
    
def grasp_close(arm):
    arm.Set_Gripper_Pick_On(500, 500, block=False)

def stop(arm):
    arm.Teach_Stop_Cmd(block=False)
    