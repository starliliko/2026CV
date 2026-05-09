# 低空目标识别项目当前进展汇报

## 一、项目选题

项目题目：低空目标识别

项目背景：

本项目面向低空经济场景下的无人机视觉感知任务，目标是在无人机低空飞行视角中，对远距离、小目标、快速运动目标进行检测与识别，并为后续目标跟踪与闭环控制打下基础。

当前项目定位：

- 先完成无人机仿真环境搭建
- 再完成视觉输入获取
- 后续接入目标检测算法
- 最终形成“仿真平台 + 视觉识别”的完整系统

## 二、项目总体技术路线

当前规划的系统结构如下：

```text
Gazebo 仿真环境
    ↓
无人机模型与机载传感器
    ↓
PX4 SITL 飞控仿真
    ↓
QGroundControl 地面站通信
    ↓
相机图像获取
    ↓
YOLOv8 目标检测
    ↓
后续可扩展 ByteTrack 跟踪与闭环控制
```

说明：

- `PX4` 负责飞控逻辑与无人机状态控制
- `Gazebo Harmonic` 负责仿真世界、模型与传感器
- `QGroundControl` 负责地面站监控与参数交互
- 后续视觉算法将基于仿真相机图像完成目标识别

## 三、目前已经完成的工作

### 1. 完成 WSL2 环境搭建

已完成内容：

- 在 Windows 11 上安装 `WSL2`
- 安装 `Ubuntu-22.04`
- 完成 Ubuntu 初始化
- 配置基础开发环境

已执行的基础操作包括：

- `sudo apt update`
- `sudo apt upgrade -y`
- 安装 `git`、`curl`、`wget`、`zip`、`unzip`

### 2. 完成 WSL 磁盘迁移

为避免 Linux 环境持续占用 `C` 盘空间，已将 WSL 迁移到 `D` 盘。

迁移结果：

- WSL 发行版：`Ubuntu-22.04`
- 当前存储位置：`D:\WSL\Ubuntu-22.04`

这样做的好处：

- 避免 `C` 盘空间不足
- 便于后续存放 PX4 源码、依赖、编译缓存和仿真数据

### 3. 完成代理与 Git 下载环境配置

由于在 WSL 中直接访问 GitHub 速度较慢，因此完成了 WSL 代理联通。

已解决的问题：

- WSL 无法直接使用 Windows 本地 `127.0.0.1:7890`
- 通过 Windows `vEthernet (WSL)` 网卡地址实现 Clash Verge 代理转发

最终可用代理地址：

```text
172.26.208.1:7890
```

配置后，WSL 已能够正常访问 GitHub，并成功完成 PX4 源码下载。

### 4. 完成 PX4 源码下载与版本切换

已完成内容：

- 在 Ubuntu 主目录下重新下载 PX4 源码
- 初始化并同步全部子模块
- 将版本切换到稳定版 `v1.16.0`

选择 `v1.16.0` 的原因：

- 属于 PX4 稳定版本
- 文档支持更完整
- 与 `Gazebo Harmonic` 兼容性更好
- 比开发版 `main`/`alpha` 更适合课程项目

当前源码位置：

```text
/home/bo_love/PX4-Autopilot
```

### 5. 完成 PX4 依赖安装

已完成：

- 执行 `Tools/setup/ubuntu.sh`
- 安装 PX4 编译工具链
- 安装 Python 依赖
- 安装 NuttX 相关依赖
- 安装 SITL 所需开发环境

后续为解决仿真依赖问题，又补充安装了：

- `Gazebo Harmonic`
- `Protobuf`
- `OpenCV`

### 6. 完成 Gazebo Harmonic 仿真环境搭建

当前已成功安装并识别以下关键组件：

- `gz-transport`
- `gz-sim`
- `gz-sensors`
- `gz-plugin`
- `sdformat`
- `OpenCV`

说明：

这一步非常关键，说明 PX4 已经具备运行 `gz_x500` 仿真的基础环境。

### 7. 成功启动 PX4 SITL + Gazebo

已经成功执行：

```bash
make px4_sitl gz_x500
```

当前成功现象包括：

- PX4 成功启动
- Gazebo 世界成功加载
- 无人机模型 `x500_0` 成功生成
- 数据日志正常写入
- MAVLink 通信端口正常打开

启动日志中出现了以下关键信息：

```text
INFO [init] Gazebo world is ready
INFO [init] Spawning model
INFO [gz_bridge] world: default, model: x500_0
INFO [px4] Startup script returned successfully
```

说明仿真主链路已经跑通。

### 8. 成功连接 QGroundControl

在 Windows 端启动 `QGroundControl` 后，已经成功与 WSL 中的 PX4 建立通信。

连接成功的关键信号：

```text
INFO [mavlink] partner IP: 172.26.208.1
INFO [commander] Ready for takeoff!
```

这说明：

- 地面站已经成功连接仿真飞控
- 基本控制链路建立完成
- 当前仿真无人机已经可以进入后续实验阶段

## 四、目前遇到并已解决的问题

### 1. WSL 未安装

问题：

- 初始状态下 Windows 虽然存在 `wsl.exe`，但没有 Ubuntu 发行版

解决：

- 安装 `Ubuntu-22.04`

### 2. WSL 占用系统盘空间

问题：

- 默认安装路径位于 `C` 盘

解决：

- 将 WSL 导出并迁移到 `D` 盘

### 3. GitHub 下载慢或失败

问题：

- `git clone` 过程中出现超时与 TLS 失败

解决：

- 通过 Clash Verge 的局域网代理能力，使 WSL 能通过 Windows 代理访问 GitHub

### 4. Gazebo 目标 `gz_x500` 无法识别

问题：

- 初始编译时出现 `unknown target 'gz_x500'`

原因：

- 缺少 `Gazebo Harmonic` 相关依赖包

解决：

- 安装 `gz-harmonic` 及相关开发库

### 5. OpenCV 缺失导致编译失败

问题：

- CMake 无法找到 `OpenCV`

解决：

- 安装 `libopencv-dev` 和相关组件

### 6. QGroundControl 无法连接

问题：

- 启动后出现 `No connection to the ground control station`

原因：

- MAVLink 初始仅面向本地地址

解决：

- 设置 MAVLink 广播参数
- 手动确认 WSL 与 Windows 之间的通信方式
- 最终成功建立 QGC 与 PX4 连接

## 五、当前项目状态

截至目前，项目已经完成“环境搭建与基础仿真链路打通”。

当前可认为已经完成的阶段：

1. WSL2 + Ubuntu 环境建立
2. PX4 稳定版源码搭建完成
3. Gazebo Harmonic 仿真环境搭建完成
4. PX4 SITL 启动成功
5. QGroundControl 成功连接

换句话说，目前已经拥有一个可运行的无人机仿真平台。

## 六、当前尚未完成的部分

虽然仿真环境已经跑通，但视觉识别主任务还没有正式接入。

目前尚未完成的内容包括：

1. 仿真相机图像获取
2. 图像流保存或转发
3. YOLOv8 检测模块接入
4. 目标跟踪模块接入
5. 面向低空小目标场景的实验设计与指标评估

## 七、下一步计划

下一阶段准备按照以下顺序推进：

### 1. 获取仿真相机图像

目标：

- 确认 Gazebo 中相机传感器可用
- 获取图像帧或视频流
- 为视觉算法输入做准备

### 2. 接入 YOLOv8 检测模型

目标：

- 对仿真画面中的目标进行检测
- 输出检测框与类别结果

### 3. 完成基础实验

目标：

- 在仿真环境中验证目标识别可行性
- 记录识别结果和运行状态

### 4. 视情况扩展目标跟踪

目标：

- 后续可加入 `ByteTrack`
- 实现连续目标跟踪

## 八、阶段性结论

目前项目已经完成了最核心、最耗时的前期准备工作，即：

“从零搭建 PX4 + Gazebo + QGroundControl 的无人机仿真平台，并成功运行起来。”

这意味着后续可以把主要精力从“环境配置”转向“视觉算法与实验结果”。

当前阶段的成果可以概括为：

- 已具备完整仿真运行环境
- 已具备飞控与地面站闭环通信能力
- 已具备后续接入视觉识别算法的技术基础

## 九、总结

目前我们已经完成了低空目标识别项目的基础环境搭建，成功跑通了 `PX4 v1.16.0 + Gazebo Harmonic + QGroundControl` 的无人机仿真系统，下一步将进入仿真相机图像获取与 `YOLOv8` 目标检测接入阶段。
