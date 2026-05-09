"""Display the latest shared Gazebo camera frame on Windows."""

from __future__ import annotations

import argparse
import pathlib
import time

import cv2


DEFAULT_IMAGE_DIR = r"D:\2026CV\demo\outputs"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Display the latest shared Gazebo camera frame."
    )
    parser.add_argument(
        "--image-dir",
        default=DEFAULT_IMAGE_DIR,
        help="Path to the shared frame directory.",
    )
    parser.add_argument(
        "--window-name",
        default="Gazebo Onboard Camera",
        help="OpenCV display window title.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    image_dir = pathlib.Path(args.image_dir)
    index_path = image_dir / "latest_index.txt"

    cv2.namedWindow(args.window_name, cv2.WINDOW_NORMAL)
    last_index = None
    last_time = time.time()
    fps = 0.0
    frame_count = 0

    while True:
        if index_path.exists():
            try:
                current_index = index_path.read_text(encoding="ascii").strip()
            except PermissionError:
                current_index = None
            except OSError:
                current_index = None

            if current_index and current_index != last_index:
                last_index = current_index
                frame_path = image_dir / f"frame_{current_index}.jpg"
                frame = cv2.imread(str(frame_path))
                if frame is not None:
                    now = time.time()
                    elapsed = max(now - last_time, 1e-6)
                    fps = 1.0 / elapsed
                    last_time = now
                    frame_count += 1

                    status = f"frame={frame_count} fps={fps:.1f}"
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

        time.sleep(0.01)

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
