from vision.summarize_results import build_report


def test_build_report_contains_metrics_and_classes() -> None:
    report = build_report(
        [
            {
                "status": "ok",
                "latency_ms": 20.0,
                "detections": [
                    {"label": "person", "confidence": 0.9},
                    {"label": "car", "confidence": 0.8},
                ],
            },
            {
                "status": "ok",
                "latency_ms": 30.0,
                "detections": [{"label": "person", "confidence": 0.7}],
            },
        ]
    )

    assert "Frames recorded: **2**" in report
    assert "Total detections: **3**" in report
    assert "| person | 2 |" in report
    assert "| car | 1 |" in report
    assert "avg **25.0**" in report


def test_build_report_handles_no_records() -> None:
    assert "No records found." in build_report([])
