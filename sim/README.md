# 仿真模块

`sim/` 保存 Gazebo 自定义世界、云台相机模型、随机目标生成和随机航点任务。

## 结构

```text
sim/
├── configs/target_models.yaml
├── custom_gz/
│   ├── models/
│   └── worlds/
├── launch/
│   ├── animate_vehicles.py
│   └── spawn_targets.py
└── missions/random_waypoints.py
```

## 典型流程

```bash
# 启动完整环境
bash scripts/launch_all.sh

# 单独生成目标
python3 sim/launch/spawn_targets.py --world baylands_2026cv --seed 42

# 可选：执行随机航点任务
python3 sim/missions/random_waypoints.py --duration 600 --seed 7
```

`target_models.yaml` 定义目标类别、Gazebo Fuel 模型、AABB 大小和采样区域。`spawn_targets.py` 会将本次生成结果写入 `sim/runtime/`，供数据采集节点读取；运行文件不会提交到 Git。

数据采集代码已经存在，但当前仓库尚未发布经过完整验证的数据集。复现状态见 [docs/status.md](../docs/status.md)。
