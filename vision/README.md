# 视觉模块

`vision/` 提供 YOLOv8 环境配置、离线推理、Windows 训练和检测结果汇总工具。实时 ROS 2 推理节点位于 `ros2_ws/src/low_altitude_bringup/low_altitude_bringup/yolo_detector.py`。

## 文件

| 文件 | 用途 |
|---|---|
| `setup_infer_env.sh` | Ubuntu 推理环境，默认安装 CPU 版 PyTorch |
| `setup_train_env.ps1` | Windows CUDA 训练环境 |
| `run_detection.py` | 图片、目录或视频的离线检测 |
| `train_sim.py` | 使用 Ultralytics 训练模型 |
| `summarize_results.py` | 将 ROS 2 JSONL 结果转换为 Markdown 报告 |
| `requirements.txt` | 通用推理依赖 |
| `requirements-train.txt` | 训练和分析依赖 |

## Ubuntu 推理

```bash
bash vision/setup_infer_env.sh
source vision/.venv-train/bin/activate
bash scripts/download_model.sh

python vision/run_detection.py path/to/image.jpg \
  --model ros2_ws/yolov8n.pt \
  --output demo/offline_outputs
```

Ubuntu 运行在 VirtualBox 中，默认无法访问宿主机 RTX 4050，因此使用 CPU 推理。

## Windows 训练

```powershell
pwsh -File vision\setup_train_env.ps1
.\vision\.venv-train\Scripts\Activate.ps1
python vision\train_sim.py --data path\to\dataset.yaml
```

模型权重、数据集和 `runs/` 目录均由 Git 忽略。当前仓库没有发布经过完整验证的自建数据集或微调权重。

完整步骤见 [docs/reproduction.md](../docs/reproduction.md)。
