"""Run YOLO inference on an image, directory, video, or camera source."""

from __future__ import annotations

import argparse
import pathlib


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "source",
        help="Image, directory, video, URL, or camera index accepted by Ultralytics.",
    )
    parser.add_argument(
        "--model",
        default="ros2_ws/yolov8n.pt",
        help="YOLO model path. Run scripts/download_model.sh for the baseline model.",
    )
    parser.add_argument(
        "--output",
        default="demo/offline_outputs",
        help="Directory for annotated prediction outputs.",
    )
    parser.add_argument("--confidence", type=float, default=0.25)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument(
        "--device",
        default="",
        help="Ultralytics device, for example cpu or 0. Empty means automatic.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()

    try:
        from ultralytics import YOLO
    except ImportError as exc:
        raise SystemExit(
            "ultralytics is not installed. Run vision/setup_infer_env.sh first."
        ) from exc

    model_path = pathlib.Path(args.model).expanduser()
    if not model_path.exists():
        raise SystemExit(
            f"Model not found: {model_path}. Run scripts/download_model.sh first."
        )

    output_dir = pathlib.Path(args.output).expanduser().resolve()
    output_dir.parent.mkdir(parents=True, exist_ok=True)

    model = YOLO(str(model_path))
    model.predict(
        source=args.source,
        conf=args.confidence,
        imgsz=args.imgsz,
        device=args.device or None,
        save=True,
        project=str(output_dir.parent),
        name=output_dir.name,
        exist_ok=True,
    )
    print(f"Prediction outputs: {output_dir}")


if __name__ == "__main__":
    main()
