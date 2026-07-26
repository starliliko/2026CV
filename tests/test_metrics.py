from collections import deque

from low_altitude_bringup.metrics import PerceptionMetrics, fps_from_window, percentile


def test_fps_from_window() -> None:
    assert fps_from_window(deque([1.0, 1.5, 2.0])) == 2.0
    assert fps_from_window(deque([1.0])) == 0.0


def test_percentile_and_detection_totals() -> None:
    assert percentile([10.0, 20.0, 30.0, 40.0], 95.0) == 40.0

    metrics = PerceptionMetrics(window_size=5)
    metrics.mark_input(now=10.0)
    metrics.mark_inference(
        12.5,
        [
            {"label": "person"},
            {"label": "person"},
            {"label": "car"},
        ],
    )

    assert metrics.frame_count == 1
    assert metrics.latency_avg_ms() == 12.5
    assert metrics.class_totals == {"person": 2, "car": 1}
