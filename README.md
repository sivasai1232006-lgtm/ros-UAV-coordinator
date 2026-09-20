# ROS 2 UAV Coordinator

A ROS 2 project demonstrating coordination between two UAV nodes using services and actions. A central Coordinator checks UAV battery status and assigns waypoints, while a Safety Monitor tracks UAV positions and warns when they get too close.

> **Note:** This project is a ROS 2 software simulation. UAV positions are represented internally as 2D `(x, y)` coordinates; no Gazebo or physical flight controller is used by the provided code.

## Project Structure

```text
src/
├── drone_controller/
│   ├── drone_controller/
│   │   ├── uav1_node.py
│   │   ├── uav2_node.py
│   │   ├── coordinator.py
│   │   └── safety_monitor.py
│   ├── launch/
│   │   └── drone_system.launch.py
│   ├── package.xml
│   ├── setup.py
│   └── setup.cfg
│
└── drone_interfaces/
    ├── msg/
    │   └── UavStatus.msg
    ├── srv/
    │   └── CheckBattery.srv
    └── action/
        └── GoToWaypoint.action
```
## Useful ROS 2 Commands

Inspect active nodes:

```bash
ros2 node list
```

Inspect topics:

```bash
ros2 topic list
ros2 topic echo /uav1/status
ros2 topic echo /uav2/status
```

Inspect services:

```bash
ros2 service list
```

Inspect actions:

```bash
ros2 action list
```

Run individual nodes if required:

```bash
ros2 run drone

## Features

* Two independent UAV nodes: `uav1` and `uav2`
* Battery readiness check through a ROS 2 service
* Waypoint navigation through a ROS 2 action
* UAV position, battery, and state status publishing
* Coordinator assigns alternating waypoints to the two UAVs
* Safety Monitor checks the distance between UAVs
* Single launch file for the complete system
* Custom ROS 2 message, service, and action interfaces

## System Architecture

```text
                         ┌─────────────────────┐
                         │     Coordinator      │
                         │                     │
                         │ Battery Services    │
                         │ Waypoint Actions     │
                         └───────┬───────┬─────┘
                                 │       │
                       Actions / │       │ \ Actions
                                 ▼       ▼
                          ┌─────────┐ ┌─────────┐
                          │  UAV 1  │ │  UAV 2  │
                          └────┬────┘ └────┬────┘
                               │           │
                         /uav1/status  /uav2/status
                               │           │
                               └─────┬─────┘
                                     ▼
                              Safety Monitor
```

### Nodes

* **`uav1`** — Provides `/uav1/status`, `uav1/check_battery`, and `/uav1/reach_target`.
* **`uav2`** — Provides `/uav2/status`, `uav2/check_battery`, and `/uav2/reach_target`.
* **`coordinator`** — Checks battery readiness and sends waypoint goals to both UAVs.
* **`safety_monitor`** — Subscribes to both UAV status topics and warns when their calculated distance is below `3.0` coordinate units.

### Custom Interfaces

**`UavStatus.msg`**

```text
string uav_id
float32 x
float32 y
float32 battery_percent
string state
```

**`CheckBattery.srv`**

```text
---
float32 battery_percent
bool ready_for_task
```

**`GoToWaypoint.action`**

```text
# Goal
float32 target_x
float32 target_y
---
# Result
bool success
float32 final_x
float32 final_y
---
# Feedback
float32[] position
float32 percent_complete
```

Each UAV starts with `100%` battery and is considered ready when its battery is at least `20%`. Completing a waypoint reduces its simulated battery by `20%`. UAV movement is simulated in 1-unit steps with a 1-second delay between steps.
The Coordinator uses these waypoints:

```text
(5, 5)
(10, 0)
(0, 10)
(10, 10)
```

UAV 1 receives waypoints 1 and 3, while UAV 2 receives waypoints 2 and 4.

## Requirements

* ROS 2 Humble
* Python 3
* `rclpy`
* `colcon`
* `drone_interfaces` package

The controller package uses `rclpy` and depends on `drone_interfaces`. No Gazebo dependency is declared or used by the provided implementation.

## Installation

Clone the repository into a ROS 2 workspace:

```bash
mkdir -p ~/uav_ws/src
cd ~/uav_ws/src

git clone https://github.com/sivasai1232006-lgtm/ros-UAV-coordinator.git
```

The workspace should contain both packages:

```text
uav_ws/
└── src/
    ├── drone_controller/
    └── drone_interfaces/
```

Source ROS 2 Humble and build the workspace:

```bash
cd ~/uav_ws

source /opt/ros/humble/setup.bash
colcon build
source install/setup.bash
```

## Running the Project

Launch the complete system:

```bash
ros2 launch drone_controller drone_system.launch.py
```

The launch file starts `uav1`, `uav2`, and `safety_monitor` immediately, then starts the Coordinator after a 2-second delay so the UAV services and action servers have time to start.

You should see logs showing:

1. The Coordinator starts the mission.
2. Battery checks are performed for both UAVs.
3. Waypoint goals are sent to the UAVs.
4. UAV positions and action feedback are updated while travelling.
5. UAVs report arrival and battery consumption.
6. The Safety Monitor warns if the UAVs come within `3.0` coordinate units.

_controller uav1_node
ros2 run drone_controller uav2_node
ros2 run drone_controller safety_monitor
ros2 run drone_controller coordinator
```
