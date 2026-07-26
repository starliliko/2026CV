#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MODEL_PATH="${MODEL_PATH:-$PROJECT_ROOT/ros2_ws/yolov8n.pt}"
MODEL_DIR="$(dirname "$MODEL_PATH")"
MODEL_NAME="$(basename "$MODEL_PATH")"
PYTHON_BIN="${PYTHON_BIN:-python}"

if [[ "$PYTHON_BIN" == "python" && -x "$PROJECT_ROOT/vision/.venv-train/bin/python" ]]; then
    PYTHON_BIN="$PROJECT_ROOT/vision/.venv-train/bin/python"
fi

if [[ -f "$MODEL_PATH" ]]; then
    echo "[download_model] Model already exists: $MODEL_PATH"
    exit 0
fi

mkdir -p "$MODEL_DIR"

if ! "$PYTHON_BIN" -c "import ultralytics" >/dev/null 2>&1; then
    echo "ERROR: ultralytics is unavailable." >&2
    echo "Activate the project environment first:" >&2
    echo "  source vision/.venv-train/bin/activate" >&2
    exit 1
fi

if [[ "$MODEL_NAME" != "yolov8n.pt" ]]; then
    echo "ERROR: automatic download only supports yolov8n.pt." >&2
    echo "Copy the custom model to: $MODEL_PATH" >&2
    exit 1
fi

echo "[download_model] Downloading YOLOv8n to $MODEL_PATH"
(
    cd "$MODEL_DIR"
    "$PYTHON_BIN" -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"
)

if [[ ! -f "$MODEL_PATH" ]]; then
    echo "ERROR: download completed without creating $MODEL_PATH" >&2
    exit 1
fi

echo "[download_model] Ready: $MODEL_PATH"
