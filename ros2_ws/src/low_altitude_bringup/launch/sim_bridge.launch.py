from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description() -> LaunchDescription:
    bridge_config_arg = DeclareLaunchArgument(
        "bridge_config",
        default_value=PathJoinSubstitution(
            [FindPackageShare("low_altitude_bringup"), "config", "gz_bridge_clock.yaml"]
        ),
        description="Path to the ros_gz_bridge YAML config file used for non-image topics.",
    )

    image_topic_arg = DeclareLaunchArgument(
        "image_topic",
        default_value="/camera/image_raw",
        description="ROS 2 image topic name after bridging from Gazebo.",
    )

    gz_image_topic_arg = DeclareLaunchArgument(
        "gz_image_topic",
        default_value="/world/baylands/model/x500_gimbal_0/link/camera_link/sensor/camera/image",
        description="Gazebo Transport camera topic bridged into ROS 2 with ros_gz_image.",
    )

    bridge_node = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        name="low_altitude_bridge",
        output="screen",
        parameters=[
            {
                "config_file": LaunchConfiguration("bridge_config"),
            }
        ],
    )

    image_bridge_node = Node(
        package="low_altitude_bringup",
        executable="gz_camera_bridge",
        name="gazebo_camera_bridge",
        output="screen",
        parameters=[
            {
                "gz_image_topic": LaunchConfiguration("gz_image_topic"),
                "image_topic": LaunchConfiguration("image_topic"),
            }
        ],
    )

    return LaunchDescription(
        [
            bridge_config_arg,
            image_topic_arg,
            gz_image_topic_arg,
            bridge_node,
            image_bridge_node,
        ]
    )
