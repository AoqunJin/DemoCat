# DemoCat
An app and scripts based tool to collect human data from simulated or physical environments.

## Introduction

- ```2024/09/19``` Our project is currently in the process of building, Welcome PR! ^_^

### Demonstration Collection

![collection](assets/demonstration.png)

### Demonstration Management

![management](assets/manager.png)

## Installation

### MetaWorld

You can follow the [Installation](https://github.com/AoqunJin/Metaworld) in my MetaWorld folk.

### Gym

```bash
pip install "gym[atari, accept-rom-license]"
```

## Structural
```bash
DemoCat/
│
├── main.py                 # 主程序入口
├── app/
│   ├── __init__.py
│   ├── gui.py              # tkinter GUI 实现
│   ├── environment.py      # 环境管理和注册
│   ├── data_manager.py     # TODO 数据管理（HDF5操作）
│   └── demo_manager.py     # TODO 演示管理（记录、查看、删除）
│
├── environments/
│   ├── __init__.py
│   ├── base_env.py         # 基础环境类
│   ├── custom_env.py       # 自定义环境示例
│   └── gym_envs/           # Gym环境封装
│       ├── __init__.py
│       └── [specific_gym_envs].py
│
├── utils/
│   ├── __init__.py
│   ├── hdf5_utils.py       # HDF5 相关工具函数
│   └── input_handler.py    # 输入处理（键盘、鼠标）
│
└── data/
    └── demonstrations/     # 存储HDF5文件的目录
```