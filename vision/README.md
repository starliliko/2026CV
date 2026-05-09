# 视觉模块说明

## 目标

`vision/` 目录用于放置目标检测与后续跟踪相关代码。

当前计划：

1. 从仿真环境中获取图像
2. 使用 `YOLOv8` 做目标检测
3. 使用 `OpenCV` 显示与保存检测结果
4. 后续可扩展 `ByteTrack`

## 当前建议结构

```text
vision/
├─ requirements.txt
├─ Dockerfile
├─ run_detection.py
├─ save_gz_camera_frame.py
└─ view_shared_camera_windows.py
```

## 当前状态

目前已经拿到了 Gazebo 中的机载相机图像话题：

```text
/world/default/model/x500_gimbal_0/link/camera_link/sensor/camera/image
```

由于仿真端和显示端在同一台机器上，所以当前采用“共享文件 + 循环缓冲区”方案：

1. WSL 订阅 Gazebo 图像话题
2. 持续把图像写入 5 张图片组成的循环缓冲区
3. Windows `conda` 环境读取最新索引并显示

## 脚本说明

### 1. WSL 端保存脚本

文件：

```text
vision/save_gz_camera_frame.py
```

作用：

1. 订阅 Gazebo 图像话题
2. 将图像保存到共享目录中的 5 张循环缓冲图片
3. 持续更新最新帧索引

推荐运行方式：

```bash
python3 vision/save_gz_camera_frame.py
```

如果更换了 Gazebo 世界，例如 `baylands`，推荐显式指定：

```bash
python3 vision/save_gz_camera_frame.py --world baylands --model x500_gimbal_0
```

### 2. Windows 端显示脚本

文件：

```text
vision/view_shared_camera_windows.py
```

作用：

1. 从共享目录读取最新索引指向的图像
2. 用 OpenCV 实时显示机载相机画面
3. 为后续 YOLOv8 接入做准备

推荐运行方式：

```powershell
python vision\view_shared_camera_windows.py
```

## 建议启动顺序

1. 启动 `make px4_sitl gz_x500_gimbal`
2. 在 WSL 里运行 `python3 vision/save_gz_camera_frame.py`
3. 在 Windows 的 `conda` 环境里运行 `python vision\view_shared_camera_windows.py`

## 下一步

1. 先确认 Windows 端可以稳定显示机载相机画面
2. 再将接收到的图像帧接入 `YOLOv8`
3. 最后在画面上叠加检测结果
