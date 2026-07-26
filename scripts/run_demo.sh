#!/usr/bin/env bash
# 2026CV one-shot demo launcher.
# Run inside Ubuntu 24.04. Requires PX4 SITL already running in another terminal:
#   cd ~/PX4/PX4-Autopilot && PX4_GZ_WORLD=baylands make px4_sitl gz_x500_gimbal
set -e

PROJ_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WS_ROOT="${WS_ROOT:-$PROJ_ROOT/ros2_ws}"
MODEL_PATH="${MODEL_PATH:-$WS_ROOT/yolov8n.pt}"
RESULTS_DIR="${RESULTS_DIR:-$PROJ_ROOT/demo/ros2_outputs}"
export CV2026_ROOT="$PROJ_ROOT"

if [ ! -f "$WS_ROOT/install/setup.bash" ]; then
  echo "[run_demo] colcon install not found at $WS_ROOT/install. Building first..."
  (cd "$WS_ROOT" && source /opt/ros/jazzy/setup.bash && \
   colcon build --packages-select low_altitude_bringup --symlink-install)
fi

# shellcheck disable=SC1091
source "$PROJ_ROOT/scripts/activate_env.sh"

if [ ! -f "$MODEL_PATH" ]; then
  echo "[run_demo] Model not found at $MODEL_PATH. Downloading YOLOv8n..."
  MODEL_PATH="$MODEL_PATH" bash "$PROJ_ROOT/scripts/download_model.sh"
fi

mkdir -p "$RESULTS_DIR"

cat <<EOF
[run_demo] Launching: perception_yolo.launch.py
  - parameter_bridge   -> /clock
  - gz_camera_bridge   -> /camera/image_raw
  - yolo_detector      -> /detections/yolo + /camera/annotated (with HUD + rich dashboard)

View the annotated stream in another terminal:
  source /opt/ros/jazzy/setup.bash
  ros2 run rqt_image_view rqt_image_view /camera/annotated

Make sure PX4 SITL is already running:
  cd ~/PX4/PX4-Autopilot && PX4_GZ_WORLD=baylands make px4_sitl gz_x500_gimbal

Press Ctrl+C to stop.
EOF

ros2 launch low_altitude_bringup perception_yolo.launch.py \
  model_path:="$MODEL_PATH" \
  annotated_dir:="$RESULTS_DIR" \
  results_dir:="$RESULTS_DIR" \
  "$@"
