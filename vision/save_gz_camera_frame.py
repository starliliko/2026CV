"""Save Gazebo onboard camera frames into a small shared ring buffer.

Run inside Ubuntu / WSL where gz transport Python bindings exist.
Frames are continuously written to a shared Windows-visible directory.
"""

from __future__ import annotations

import argparse
import io
import pathlib
import time

import numpy as np
from gz.msgs10.image_pb2 import Image as GzImage
from gz.transport13 import Node
from PIL import Image


DEFAULT_WORLD = "default"
DEFAULT_MODEL = "x500_gimbal_0"
DEFAULT_OUTPUT_DIR = "/mnt/d/2026CV/demo/outputs"
DEFAULT_BUFFER_SIZE = 5


def build_topic(world: str, model: str) -> str:
    return f"/world/{world}/model/{model}/link/camera_link/sensor/camera/image"


class LatestFrameWriter:
    """Write Gazebo frames into a shared JPEG ring buffer."""

    def __init__(
        self,
        output_dir: pathlib.Path,
        jpeg_quality: int,
        buffer_size: int,
    ) -> None:
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.jpeg_quality = jpeg_quality
        self.buffer_size = buffer_size
        self.frame_count = 0
        self._cleanup_old_frames()

    def _cleanup_old_frames(self) -> None:
        """Remove old buffered frames from previous runs."""
        for temp_file in self.output_dir.glob("frame_*.jpg"):
            try:
                temp_file.unlink()
            except OSError:
                pass
        latest_index = self.output_dir / "latest_index.txt"
        try:
            latest_index.unlink()
        except OSError:
            pass

    def callback(self, msg: GzImage) -> None:
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

        if channels == 4:
            image = Image.fromarray(frame[:, :, :3], mode="RGB")
        elif channels == 3:
            image = Image.fromarray(frame, mode="RGB")
        else:
            image = Image.fromarray(frame[:, :, 0], mode="L").convert("RGB")

        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", quality=self.jpeg_quality)
        slot = self.frame_count % self.buffer_size
        frame_path = self.output_dir / f"frame_{slot}.jpg"
        frame_path.write_bytes(buffer.getvalue())
        index_path = self.output_dir / "latest_index.txt"
        temp_index_path = self.output_dir / "latest_index.tmp"
        temp_index_path.write_text(str(slot), encoding="ascii")
        temp_index_path.replace(index_path)
        self.frame_count += 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Save Gazebo onboard camera frames to a shared file."
    )
    parser.add_argument(
        "--world",
        default=DEFAULT_WORLD,
        help="Gazebo world name.",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help="Gazebo model name.",
    )
    parser.add_argument(
        "--topic",
        default=None,
        help="Gazebo image topic. If omitted, it is built from --world and --model.",
    )
    parser.add_argument(
        "--output-dir",
        default=DEFAULT_OUTPUT_DIR,
        help="Shared output directory.",
    )
    parser.add_argument(
        "--jpeg-quality",
        type=int,
        default=90,
        help="JPEG quality in [1, 95].",
    )
    parser.add_argument(
        "--buffer-size",
        type=int,
        default=DEFAULT_BUFFER_SIZE,
        help="Number of shared frame files in the ring buffer.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    output_dir = pathlib.Path(args.output_dir)
    topic = args.topic or build_topic(args.world, args.model)

    writer = LatestFrameWriter(
        output_dir=output_dir,
        jpeg_quality=args.jpeg_quality,
        buffer_size=args.buffer_size,
    )
    node = Node()
    if not node.subscribe(GzImage, topic, writer.callback):
        raise SystemExit(f"Failed to subscribe to topic: {topic}")

    print(f"Subscribed to Gazebo image topic: {topic}")
    print(f"Writing frame ring buffer to: {output_dir}")
    print(f"Buffer size: {args.buffer_size}")
    print("Press Ctrl+C to stop.")

    last_count = -1
    try:
        while True:
            if writer.frame_count != last_count:
                last_count = writer.frame_count
                print(f"saved frame {last_count}", end="\r", flush=True)
            time.sleep(0.05)
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
