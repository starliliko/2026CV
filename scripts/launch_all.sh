#!/usr/bin/env bash
# 2026CV 一键启动全流程 (精简版)
#
# 必须在 Ubuntu 系统终端 (Ctrl+Alt+T) 中运行, 不要在 VS Code Snap 终端运行.
#
# 用法:
#   bash scripts/launch_all.sh                 # 默认 world=default
#   WORLD=baylands bash scripts/launch_all.sh  # 切换 baylands 世界
#   WITH_MISSION=1 bash scripts/launch_all.sh  # 额外开窗口跑随机航点任务
#   EXTRA_GUI=1 bash scripts/launch_all.sh     # 在 PX4 自带 GUI 之外再开一个 gz sim -g
#   CONF=0.25 bash scripts/launch_all.sh       # 自定义 YOLO 置信度阈值 (默认 0.15)
#   IMGSZ=320 bash scripts/launch_all.sh       # 推理分辨率 (320/416/480/640, 默认 480, 越小越快)
#   SKIP=2 bash scripts/launch_all.sh          # 每 N 帧推理一次 (默认 1=每帧推理)
#   DEVICE=0 bash scripts/launch_all.sh        # 强制使用 GPU 0 (默认空=ultralytics 自动选)
#   DEVICE=cpu bash scripts/launch_all.sh      # 强制使用 CPU
#   PERF=1 bash scripts/launch_all.sh          # 性能优先: 关闭 HUD/仪表盘/结果落盘 (默认 1)
#
# 三/四个独立终端窗口:
#   1_px4_sitl         — PX4 + Gazebo server (含自带 GUI)
#   2_gz_gui_extra     — (可选, EXTRA_GUI=1) 第二个 gz sim -g 客户端
#   3_ros2_perception  — ros_gz_bridge (clock+image) + yolo_detector
#   4_mission          — (可选, WITH_MISSION=1) MAVSDK 随机航点任务
#
# 看注释后图像:  bash scripts/view_annotated.sh
# 一键停止:      bash scripts/stop_all.sh

set -e

PROJ_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PX4_DIR="${PX4_DIR:-$HOME/PX4/PX4-Autopilot}"
WORLD="${WORLD:-default}"
WITH_MISSION="${WITH_MISSION:-0}"
EXTRA_GUI="${EXTRA_GUI:-0}"
CONF="${CONF:-0.15}"
IMGSZ="${IMGSZ:-480}"
SKIP="${SKIP:-1}"
DEVICE="${DEVICE:-}"
PERF="${PERF:-1}"
LOG_DIR="$PROJ_ROOT/demo/ros2_outputs/launch_logs"
mkdir -p "$LOG_DIR"

if [[ "$PERF" == "1" ]]; then
    ENABLE_HUD="false"
    ENABLE_DASHBOARD="false"
    USE_RICH="false"
    RECORD_RESULTS="false"
else
    ENABLE_HUD="true"
    ENABLE_DASHBOARD="true"
    USE_RICH="true"
    RECORD_RESULTS="true"
fi

# ---- 选择终端模拟器 ----------------------------------------------------------
TERM_CMD=""
if command -v gnome-terminal >/dev/null 2>&1; then
    TERM_CMD="gnome-terminal"
elif command -v xterm >/dev/null 2>&1; then
    TERM_CMD="xterm"
fi

spawn() {
    local title="$1"; shift
    local logfile="$LOG_DIR/${title}.log"
    local cmd="$*"
    # 始终把 stdout/stderr tee 到日志, 方便派发失败时排查
    local wrapped="echo '== $title =='; { $cmd; } 2>&1 | tee '$logfile'; rc=\${PIPESTATUS[0]}; echo; echo \"[exit] $title rc=\$rc, 日志: $logfile\"; echo '按回车关闭窗口'; read"
    echo "[launch_all] -> $title  (log: $logfile)"
    case "$TERM_CMD" in
        gnome-terminal)
            gnome-terminal --title="$title" -- bash -lc "$wrapped" >/dev/null 2>&1 &
            ;;
        xterm)
            xterm -T "$title" -e bash -lc "$wrapped" &
            ;;
        *)
            echo "[launch_all]   (无终端模拟器, 后台运行)"
            nohup bash -lc "$cmd" > "$logfile" 2>&1 &
            ;;
    esac
}

# ---- 前置检查 ---------------------------------------------------------------
[[ -d "$PX4_DIR" ]] || { echo "ERROR: PX4 目录不存在: $PX4_DIR"; exit 1; }

if [[ ! -f "$PROJ_ROOT/ros2_ws/install/setup.bash" ]]; then
    echo "[launch_all] ros2_ws 未构建, 现在构建..."
    (cd "$PROJ_ROOT/ros2_ws" && source /opt/ros/jazzy/setup.bash && \
     colcon build --packages-select low_altitude_bringup --symlink-install)
fi

if env | grep -qE '^SNAP(_|=)'; then
    echo "[launch_all] WARN: 当前 shell 检测到 SNAP 环境变量, Gazebo GUI 可能崩溃."
    echo "             请用系统终端 (Ctrl+Alt+T), 不要在 VS Code Snap 终端运行此脚本."
fi

# 修正 ament_python 入口脚本 shebang -> venv python (含 ultralytics+torch)
VENV_PY="$PROJ_ROOT/vision/.venv-train/bin/python"
if [[ -x "$VENV_PY" ]]; then
    for f in "$PROJ_ROOT/ros2_ws/install/low_altitude_bringup/lib/low_altitude_bringup"/*; do
        [[ -f "$f" ]] || continue
        if head -c 200 "$f" 2>/dev/null | head -1 | grep -qE '^#!.*python'; then
            sed -i "1c #!$VENV_PY" "$f"
        fi
    done
fi

# 根据 world 拼出 gz 相机话题
GZ_IMG="/world/${WORLD}/model/x500_gimbal_0/link/camera_link/sensor/camera/image"

cat <<EOF
============================================================
2026CV 一键启动
  PX4_DIR     = $PX4_DIR
  WORLD       = $WORLD
  GZ_IMG      = $GZ_IMG
  CONFIDENCE  = $CONF
  IMGSZ       = $IMGSZ
    SKIP        = $SKIP
    DEVICE      = ${DEVICE:-auto}
    PERF        = $PERF
  WITH_MISSION= $WITH_MISSION
  EXTRA_GUI   = $EXTRA_GUI
  日志目录    = $LOG_DIR
  终端        = ${TERM_CMD:-后台 (无窗口)}
============================================================
EOF

# ---- 1) PX4 SITL + Gazebo server (含自带 GUI) -------------------------------
spawn "1_px4_sitl" "cd '$PX4_DIR' && export GZ_CONFIG_PATH=/usr/share/gz && PX4_GZ_WORLD='$WORLD' make px4_sitl gz_x500_gimbal"

# ---- 2) (可选) 额外 Gazebo GUI 客户端 ---------------------------------------
if [[ "$EXTRA_GUI" == "1" ]]; then
    sleep 8
    spawn "2_gz_gui_extra" "export GZ_CONFIG_PATH=/usr/share/gz; export QT_QPA_PLATFORM=xcb; gz sim -g"
fi

# ---- 3) ROS2 感知 (ros_gz_bridge + yolo_detector) --------------------------
PERCEPTION_WAIT="${PERCEPTION_WAIT:-15}"
echo "[launch_all] 等待 ${PERCEPTION_WAIT} 秒让 PX4/Gazebo 启动并发布相机话题..."
sleep "$PERCEPTION_WAIT"
DEVICE_ARG=""
if [[ -n "$DEVICE" ]]; then
    DEVICE_ARG=" device:='$DEVICE'"
fi
ROS_CMD="source '$PROJ_ROOT/scripts/activate_env.sh' && cd '$PROJ_ROOT' && \
ros2 launch low_altitude_bringup perception_yolo.launch.py \
    gz_image_topic:='$GZ_IMG' confidence:='$CONF' imgsz:='$IMGSZ' report_every_n_frames:='$SKIP'${DEVICE_ARG} \
    enable_hud:='$ENABLE_HUD' enable_dashboard:='$ENABLE_DASHBOARD' use_rich:='$USE_RICH' \
    record_results:='$RECORD_RESULTS'"
spawn "3_ros2_perception" "$ROS_CMD"

# ---- 4) 随机航点任务 (可选) -------------------------------------------------
if [[ "$WITH_MISSION" == "1" ]]; then
    sleep 10
    MISSION_CMD="source '$PROJ_ROOT/scripts/activate_env.sh' && \
python3 '$PROJ_ROOT/sim/missions/random_waypoints.py' --duration 600 \
  --min-alt 30 --max-alt 80 --x-range -100 100 --y-range -100 100"
    spawn "4_mission" "$MISSION_CMD"
fi

cat <<EOF

[launch_all] 派发完毕. 后续:
  * 看注释后图像:    bash scripts/view_annotated.sh
  * 检测话题:        ros2 topic echo /detections/yolo --once
  * 帧率检查:        ros2 topic hz /camera/image_raw
  * 一键停止:        bash scripts/stop_all.sh

EOF
