from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description() -> LaunchDescription:
    bridge_config_arg = DeclareLaunchArgument(
        "bridge_config",
        default_value=PathJoinSubstitution(
            [FindPackageShare("low_altitude_bringup"), "config", "gz_bridge_clock.yaml"]
        ),
    )
    image_topic_arg = DeclareLaunchArgument("image_topic", default_value="/camera/image_raw")
    annotated_image_topic_arg = DeclareLaunchArgument(
        "annotated_image_topic", default_value="/camera/annotated"
    )
    gz_image_topic_arg = DeclareLaunchArgument(
        "gz_image_topic",
        default_value="/world/baylands/model/x500_gimbal_0/link/camera_link/sensor/camera/image",
    )
    model_path_arg = DeclareLaunchArgument("model_path", default_value="yolov8n.pt")
    confidence_arg = DeclareLaunchArgument("confidence", default_value="0.25")
    report_every_n_frames_arg = DeclareLaunchArgument(
        "report_every_n_frames", default_value="5"
    )
    annotated_dir_arg = DeclareLaunchArgument(
        "annotated_dir", default_value="/mnt/d/2026CV/demo/ros2_outputs"
    )
    heartbeat_interval_sec_arg = DeclareLaunchArgument(
        "heartbeat_interval_sec", default_value="5.0"
    )
    log_every_n_status_arg = DeclareLaunchArgument(
        "log_every_n_status", default_value="20"
    )
    enable_hud_arg = DeclareLaunchArgument(
        "enable_hud", default_value="true",
        description="Draw FPS/latency/status HUD onto /camera/annotated frames.",
    )
    enable_dashboard_arg = DeclareLaunchArgument(
        "enable_dashboard", default_value="true",
        description="Run rich/text dashboard inside the detector process.",
    )
    use_rich_arg = DeclareLaunchArgument(
        "use_rich", default_value="true",
        description="Use rich Live UI when available; otherwise fall back to plain log lines.",
    )
    dashboard_refresh_hz_arg = DeclareLaunchArgument(
        "dashboard_refresh_hz", default_value="2.0"
    )
    record_results_arg = DeclareLaunchArgument(
        "record_results", default_value="true",
        description="Append per-frame detections to JSONL and refresh summary.json.",
    )
    results_dir_arg = DeclareLaunchArgument(
        "results_dir", default_value="/mnt/d/2026CV/demo/ros2_outputs",
        description="Directory where detections.jsonl and summary.json are written.",
    )
    summary_interval_sec_arg = DeclareLaunchArgument(
        "summary_interval_sec", default_value="5.0",
    )

    bridge_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [FindPackageShare("low_altitude_bringup"), "launch", "sim_bridge.launch.py"]
            )
        ),
        launch_arguments={
            "bridge_config": LaunchConfiguration("bridge_config"),
            "image_topic": LaunchConfiguration("image_topic"),
            "gz_image_topic": LaunchConfiguration("gz_image_topic"),
        }.items(),
    )

    yolo_detector = Node(
        package="low_altitude_bringup",
        executable="yolo_detector",
        name="yolo_detector",
        output="screen",
        parameters=[
            {
                "image_topic": LaunchConfiguration("image_topic"),
                "detection_topic": "/detections/yolo",
                "annotated_image_topic": LaunchConfiguration("annotated_image_topic"),
                "model_path": LaunchConfiguration("model_path"),
                "confidence": LaunchConfiguration("confidence"),
                "device": "",
                "report_every_n_frames": LaunchConfiguration("report_every_n_frames"),
                "publish_annotated": True,
                "save_annotated": False,
                "save_every_n_frames": 30,
                "annotated_dir": LaunchConfiguration("annotated_dir"),
                "publish_startup_status": True,
                "heartbeat_interval_sec": LaunchConfiguration("heartbeat_interval_sec"),
                "log_every_n_status": LaunchConfiguration("log_every_n_status"),
                "enable_hud": LaunchConfiguration("enable_hud"),
                "enable_dashboard": LaunchConfiguration("enable_dashboard"),
                "use_rich": LaunchConfiguration("use_rich"),
                "dashboard_refresh_hz": LaunchConfiguration("dashboard_refresh_hz"),
                "record_results": LaunchConfiguration("record_results"),
                "results_dir": LaunchConfiguration("results_dir"),
                "summary_interval_sec": LaunchConfiguration("summary_interval_sec"),
            }
        ],
    )

    return LaunchDescription(
        [
            bridge_config_arg,
            image_topic_arg,
            annotated_image_topic_arg,
            gz_image_topic_arg,
            model_path_arg,
            confidence_arg,
            report_every_n_frames_arg,
            annotated_dir_arg,
            heartbeat_interval_sec_arg,
            log_every_n_status_arg,
            enable_hud_arg,
            enable_dashboard_arg,
            use_rich_arg,
            dashboard_refresh_hz_arg,
            record_results_arg,
            results_dir_arg,
            summary_interval_sec_arg,
            bridge_launch,
            yolo_detector,
        ]
    )
