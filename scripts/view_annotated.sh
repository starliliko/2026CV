#!/usr/bin/env bash
# 用系统 python 启动 rqt_image_view, 订阅 /camera/annotated.
# 注意: rqt 依赖 python3-pyqt5, 必须用系统 python 而不是 vision/.venv-train.
#
# 用法:
#   bash scripts/view_annotated.sh                 # 查看 /camera/annotated
#   bash scripts/view_annotated.sh /camera/image_raw  # 查看其它话题
set -e

TOPIC="${1:-/camera/annotated}"
PROJ_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SYSTEM_PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

# 检查 PyQt5 是否安装
if ! /usr/bin/python3 -c "import PyQt5" 2>/dev/null; then
    echo "[view_annotated] 缺少 python3-pyqt5, 现在安装 (需要 sudo)..."
    sudo apt-get install -y python3-pyqt5 python3-pyqt5.qtsvg
fi

echo "[view_annotated] topic=$TOPIC"
echo "[view_annotated] clean launch: standalone rqt_image_view + clear-config"

exec env \
    -u VIRTUAL_ENV \
    -u PYTHONHOME \
    -u PYTHONPATH \
    -u LD_LIBRARY_PATH \
    -u GTK_PATH \
    -u GIO_EXTRA_MODULES \
    -u QT_PLUGIN_PATH \
    -u QT_QPA_PLATFORMTHEME \
    -u SNAP \
    -u SNAP_NAME \
    -u SNAP_REVISION \
    -u SNAP_ARCH \
    -u SNAP_LIBRARY_PATH \
    -u SNAP_INSTANCE_NAME \
    HOME="$HOME" \
    USER="${USER:-$(id -un)}" \
    LOGNAME="${LOGNAME:-${USER:-$(id -un)}}" \
    DISPLAY="${DISPLAY:-}" \
    XAUTHORITY="${XAUTHORITY:-}" \
    XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-}" \
    WAYLAND_DISPLAY="${WAYLAND_DISPLAY:-}" \
    PATH="$SYSTEM_PATH" \
    bash --noprofile --norc -lc '
        set -e
        source /opt/ros/jazzy/setup.bash
        if [[ -f "$1/ros2_ws/install/setup.bash" ]]; then
            source "$1/ros2_ws/install/setup.bash"
        fi
        exec ros2 run rqt_gui rqt_gui \
            --standalone rqt_image_view \
            --clear-config \
            --force-discover \
            --args "$2"
    ' bash "$PROJ_ROOT" "$TOPIC"
