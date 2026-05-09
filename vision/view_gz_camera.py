"""Display the Gazebo onboard camera stream with OpenCV.

This first version is intentionally simple:
1. Subscribe to a Gazebo image topic through gz transport bindings.
2. Convert the incoming RGB frame to an OpenCV image.
3. Show the live camera view in a window.

Recommended runtime:
    Run inside Ubuntu / WSL where `python3-gz-transport13` is installed.
"""

from __future__ import annotations

import argparse
import threading
import time

import cv2
import numpy as np
from gz.msgs10.image_pb2 import Image
from gz.transport13 import Node


DEFAULT_TOPIC = (
    "/world/default/model/x500_gimbal_0/link/camera_link/sensor/camera/image"
)


class CameraViewer:
    """Thread-safe Gazebo camera frame cache."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._frame: np.ndarray | None = None
        self._frame_count = 0

    def callback(self, msg: Image) -> None:
        """Receive Gazebo Image messages and cache the newest frame."""
        width = int(msg.width)
        height = int(msg.height)
        step = int(msg.step)

        if width <= 0 or height <= 0 or step <= 0:
            return

        channels = step // width
        if channels not in (1, 3, 4):
            return

        raw = np.frombuffer(msg.data, dtype=np.uint8)
        expected_size = height * step
        if raw.size < expected_size:
            return

        frame = raw[:expected_size].reshape((height, width, channels))

        if channels == 3:
            # Gazebo is currently publishing RGB_INT8 for the gimbal camera.
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        elif channels == 4:
            frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2BGR)
        else:
            frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)

        with self._lock:
            self._frame = frame
            self._frame_count += 1

    def latest_frame(self) -> tuple[np.ndarray | None, int]:
        with self._lock:
            if self._frame is None:
                return None, self._frame_count
            return self._frame.copy(), self._frame_count


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Display the Gazebo onboard camera stream."
    )
    parser.add_argument(
        "--topic",
        default=DEFAULT_TOPIC,
        help="Gazebo image topic to subscribe to.",
    )
    parser.add_argument(
        "--window-name",
        default="Gazebo Onboard Camera",
        help="OpenCV display window name.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()

    viewer = CameraViewer()
    node = Node()

    if not node.subscribe(Image, args.topic, viewer.callback):
        raise SystemExit(f"Failed to subscribe to topic: {args.topic}")

    print(f"Subscribed to Gazebo image topic: {args.topic}")
    print("Press 'q' in the image window to quit.")

    cv2.namedWindow(args.window_name, cv2.WINDOW_NORMAL)

    last_count = -1
    last_frame_time = time.time()

    try:
        while True:
            frame, frame_count = viewer.latest_frame()

            if frame is not None:
                if frame_count != last_count:
                    last_count = frame_count
                    last_frame_time = time.time()

                elapsed = max(time.time() - last_frame_time, 1e-6)
                status = f"Frames: {frame_count} | topic alive: {elapsed:.2f}s ago"
                cv2.putText(
                    frame,
                    status,
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 255, 0),
                    2,
                    cv2.LINE_AA,
                )
                cv2.imshow(args.window_name, frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break

            time.sleep(0.001)
    finally:
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
