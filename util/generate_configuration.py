import json

RAMP_HEIGHTS = 3
RAMP_ROTATIONS = 4
OBSTACLE_HEIGHTS = 7
OBSTACLE_WIDTH = 4
OBSTACLE_DEPTH = 5
AGENT_POSITION_Z = 3
OBJECT_POSITON_Z = 3
OBJECT_POSITON_X = 3
configurations = []
# ramp_double_template = {
#     "barrier_type": "ramp",
#     "id": 0,
#     "agent_shape": 0,
#     "obj_shape": 0,
#     "agent_pos_z": 2,
#
#     "ramp_height_1": 1,
#     "ramp_rotation_1": 3,
#     "obj_pos_ramp_1": 0,
#     "ramp_height_2": 0,
#     "ramp_rotation_2": 1,
#     "obj_pos_ramp_2": 1
#   }
#
# for ramp_height_1 in range(RAMP_HEIGHTS):
#     for ramp_height_2 in range(RAMP_HEIGHTS):
#         for ramp_rotation_1 in range(RAMP_ROTATIONS):
#             for ramp_rotation_2 in range(RAMP_ROTATIONS):
#                 for agent_z in range(AGENT_POSITION_Z):
#                     ramp_double_template["agent_pos_z"] = agent_z
#                     ramp_double_template["ramp_rotation_1"] = ramp_rotation_1
#                     ramp_double_template["ramp_rotation_2"] = ramp_rotation_2
#                     ramp_double_template["ramp_height_1"] = ramp_height_1
#                     ramp_double_template["ramp_height_2"] = ramp_height_2
#                     configurations.append(ramp_double_template.copy())
#                     ramp_double_template["id"] += 1
#
# ramp_len = len(configurations)
# print("No of ramp scenes", len(configurations))
# with open("configuration_files/configurations_3_4_ramp.json", "w") as fp:
#     json.dump(configurations, fp)
#
# configurations = []
# cube_double_template = {
#     "id": 0,
#     "barrier_type": "cube",
#     "agent_shape": 0,
#     "obj_shape": 0,
#     "agent_pos_z": 2,
#
#     "obj_1_pos_x": 0,
#     "obj_1_pos_z": 1,
#     "obj_2_pos_x": 4,
#     "obj_2_pos_z": 1,
#
#     "obstacle_1_pos_x": 1,
#     "obstacle_1_pos_z": 1,
#     "obstacle_1_height": 2,
#     "obstacle_1_width": 0,
#     "obstacle_1_depth": 2,
#
#     "obstacle_2_pos_x": 3,
#     "obstacle_2_pos_z": 1,
#     "obstacle_2_height": 1,
#     "obstacle_2_width": 0,
#     "obstacle_2_depth": 2,
#
#     "target": 0
#   }
#
# for agent_z in range(AGENT_POSITION_Z):
#     for obstacle_height_1 in range(6):
#         for obstacle_height_2 in range(6):
#             for obstacle_depth_1 in range(OBSTACLE_DEPTH):
#                 for obstacle_depth_2 in range(OBSTACLE_DEPTH):
#                     for obstacle_width_1 in range(OBSTACLE_WIDTH):
#                         for obstacle_width_2 in range(OBSTACLE_WIDTH):
#                             if obstacle_height_1 == 6 and obstacle_height_2 == 4:
#                                 print(cube_double_template["id"])
#                             cube_double_template["obstacle_1_width"] = obstacle_width_1
#                             cube_double_template["obstacle_2_width"] = obstacle_width_2
#                             cube_double_template["obstacle_1_depth"] = obstacle_depth_1
#                             cube_double_template["obstacle_2_depth"] = obstacle_depth_2
#                             cube_double_template["obstacle_1_height"] = obstacle_height_1
#                             cube_double_template["obstacle_2_height"] = obstacle_height_2
#                             configurations.append(cube_double_template.copy())
#                             cube_double_template["id"] += 1
# print("No of obstacle scenes", len(configurations) )
# with open("configuration_files/configurations_3_4_cube.json", "w") as fp:
#     json.dump(configurations, fp)


# cube_template = {
#     "barrier_type": "cube",
#     "id": 0,
#     "agent_shape": 0,
#     "obj_shape": 0,
#     "agent_pos_x": 0,
#     "agent_pos_z": 0,
#     "obj_pos_x": 4,
#     "obj_pos_z": 2,
#     "obstacle_pos_x": 1,
#     "obstacle_pos_z": 0,
#     "obstacle_height": 3,
#     "obstacle_width": 0,
#     "obstacle_depth": 1,
# }
# configurations = []
# idx = 0
# for agent_x in range(3):
#     for agent_z in range(3):
#         for obstacle_pos_x in range(3):
#             for obstacle_pos_z in range(3):
#                 for obstacle_height in range(OBSTACLE_HEIGHTS):
#                     for obstacle_depth in range(OBSTACLE_DEPTH):
#                         for obstacle_width in range(OBSTACLE_WIDTH):
#                             for obj_pos_x in range(3):
#                                 for obj_pos_z in range(3):
#                                     if agent_x != obj_pos_x and agent_x != obstacle_pos_x and obj_pos_x != obstacle_pos_x:
#                                         cube_template["agent_pos_x"] = agent_x
#                                         cube_template["agent_pos_z"] = agent_z
#                                         cube_template["obstacle_pos_x"] = obstacle_pos_x
#                                         cube_template["obstacle_pos_z"] = obstacle_pos_z
#                                         cube_template["obstacle_height"] = obstacle_height
#                                         cube_template["obstacle_depth"] = obstacle_depth
#                                         cube_template["obstacle_width"] = obstacle_width
#                                         cube_template["obj_pos_z"] = obj_pos_z
#                                         cube_template["obj_pos_x"] = obj_pos_x
#                                         configurations.append(cube_template.copy())
#                                         cube_template["id"] += 1
#                                         idx += 1

#
# ramp_template = {
#                 "barrier_type": "ramp",
#                 "id": 0,
#                 "agent_shape": 1,
#                 "obj_shape": 0,
#                 "agent_pos_x": 0,
#                 "agent_pos_z": 1,
#                 "obstacle_pos_x": 1,
#                 "obstacle_pos_z": 1,
#                 "ramp_height": 1,
#                 "ramp_rotation": 0,
#                 "obj_pos_ramp": 1,
#                 "obstacle_height": 0,
#                 "obstacle_width": 0,
#                 "obstacle_depth": 2,
#                 "approach": "jump_ramp_1"
#             }
# for agent_x in [0, 2]:
#     for agent_z in range(3):
#         for ramp_rotation in range(4):
#             for ramp_height in [0, 1, 3]:
#                 for ramp_pos in [0, 1]:
#                     if ramp_pos != 0 and agent_x != 0 or ramp_pos != 1 and agent_x != 2:
#                         ramp_template["agent_pos_x"] = agent_x
#                         ramp_template["agent_pos_z"] = agent_z
#                         ramp_template["ramp_rotation"] = ramp_rotation
#                         ramp_template["ramp_height"] = ramp_height
#                         ramp_template["obj_pos_ramp"] = ramp_pos
#                         configurations.append(ramp_template.copy())
#                         ramp_template["id"] += 1
# print(len(configurations))
# with open("configuration_files/configs_single_goal_cube.json", "w") as fp:
#     json.dump(configurations, fp)

#


def create_platform_3_4_trajectories():
    configurations = []
    cube_template = {
                "barrier_type": "platform",
                "id": 0,
                "agent_shape": 0,
                "obj_shape": 0,
                "agent_pos_z": 1,
                "obj_pos_ramp_x_1": 0,
                "obj_pos_ramp_z_1": 2,
                "obj_pos_ramp_x_2": 0,
                "obj_pos_ramp_z_2": 2,
                "ramp_height_1": -1,
                "ramp_height_2": 1,
            }
    for agent_z in range(3):
        for ramp_height_1 in range(3):
            cube_template["agent_pos_z"] = agent_z
            cube_template["ramp_height_1"] = ramp_height_1
            cube_template["ramp_height_2"] = -1
            cube_template["id"] += 1
            configurations.append(cube_template.copy())

            cube_template["agent_pos_z"] = agent_z
            cube_template["ramp_height_1"] = -1
            cube_template["ramp_height_2"] = ramp_height_1
            cube_template["id"] += 1
            configurations.append(cube_template.copy())
    print("No of obstacle scenes", len(configurations))
    with open("configuration_files/configs_platform_3_4.json", "w") as fp:
        json.dump(configurations, fp)


def create_ramp_3_4_trajectories():
    configurations = []
    cube_template = {
                "barrier_type": "ramp",
                "id": 1,
                "agent_shape": 0,
                "obj_shape": 0,
                "agent_pos_z": 1,
                "ramp_height_1": 1,
                "ramp_rotation_1": 0,
                "ramp_height_2": 1,
                "ramp_rotation_2": 2
            }
    for agent_z in range(3):
        for ramp_height_1 in range(3):
            cube_template["agent_pos_z"] = agent_z
            cube_template["ramp_height_1"] = ramp_height_1
            cube_template["ramp_height_2"] = -1
            cube_template["id"] += 1
            configurations.append(cube_template.copy())

            cube_template["agent_pos_z"] = agent_z
            cube_template["ramp_height_1"] = -1
            cube_template["ramp_height_2"] = ramp_height_1
            cube_template["id"] += 1
            configurations.append(cube_template.copy())
    print("No of obstacle scenes", len(configurations))
    with open("configuration_files/configs_ramp_3_4.json", "w") as fp:
        json.dump(configurations, fp)

def create_pit_3_4_trajectories():
    configurations = []
    cube_template = {
                    "barrier_type": "pit",
                    "id": 0,
                    "agent_shape": 0,
                    "obj_shape": 0,
                    "agent_pos_x": 0,
                    "agent_pos_z": 2,
                    "obj_1_pos_x": 0,
                    "obj_1_pos_z": 1,
                    "obj_2_pos_x": 4,
                    "obj_2_pos_z": 1,
                    "pit_width_1": 0,
                    "pit_depth_1": 2,
                    "pit_width_2": -1,
                    "pit_depth_2": -1,
                    "obstacle_1_pos_x": 1,
                    "obstacle_1_pos_z": 1,
                    "obstacle_2_pos_x": 3,
                    "obstacle_2_pos_z": 1,
                }
    for agent_z in [0, 1, 2]:
        for obj_1_z in range(OBJECT_POSITON_Z):
            for pit_width_1 in range(3):
                cube_template["barrier_type"] = "pit"
                cube_template["agent_pos_z"] = agent_z
                cube_template["pit_width_1"] = pit_width_1
                cube_template["pit_width_2"] = -1
                cube_template["obj_1_pos_z"] = obj_1_z
                cube_template["id"] += 1
                configurations.append(cube_template.copy())

                cube_template["agent_pos_z"] = agent_z
                cube_template["pit_width_1"] = -1
                cube_template["pit_width_2"] = pit_width_1
                cube_template["obj_2_pos_z"] = obj_1_z
                cube_template["id"] += 1
                configurations.append(cube_template.copy())

    for agent_z in [0, 1, 2]:
        for obj_1_z in range(OBJECT_POSITON_Z):
            for pit_width_1 in range(3):
                for bridge_1_z in range(3):
                    cube_template["barrier_type"] = "pit-with-bridge"
                    cube_template["agent_pos_z"] = agent_z
                    cube_template["pit_width_1"] = pit_width_1
                    cube_template["pit_width_2"] = -1
                    cube_template["obj_1_pos_z"] = obj_1_z
                    cube_template["bridge_1_z"] = bridge_1_z
                    cube_template["bridge_2_z"] = -1
                    cube_template["id"] += 1
                    configurations.append(cube_template.copy())

                    cube_template["agent_pos_z"] = agent_z
                    cube_template["pit_width_1"] = -1
                    cube_template["pit_width_2"] = pit_width_1
                    cube_template["obj_2_pos_z"] = obj_1_z
                    cube_template["bridge_1_z"] = -1
                    cube_template["bridge_2_z"] = bridge_1_z
                    cube_template["id"] += 1
                    configurations.append(cube_template.copy())

    print("No of obstacle scenes", len(configurations))
    with open("configuration_files/configs_pit_3_4.json", "w") as fp:
        json.dump(configurations, fp)

def create_scene_2_goal_barrier_trajectores():
    configurations = []
    cube_double_template = {
        "id": 0,
        "barrier_type": "cube",
        "agent_shape": 0,
        "obj_shape": 0,
        "agent_pos_z": 2,

        "obj_1_pos_x": 0,
        "obj_1_pos_z": 1,
        "obj_2_pos_x": 4,
        "obj_2_pos_z": 1,

        "obstacle_1_pos_x": 1,
        "obstacle_1_pos_z": 1,
        "obstacle_1_height": 0,
        "obstacle_1_width": 0,
        "obstacle_1_depth": 2,

        "obstacle_2_pos_x": 3,
        "obstacle_2_pos_z": 1,
        "obstacle_2_height": 0,
        "obstacle_2_width": 0,
        "obstacle_2_depth": 0,
      }

    for agent_z in [0, 1, 2]:
        for obj_1_z in range(OBJECT_POSITON_Z):
            for obstacle_height_1 in range(1, 6):
                for obstacle_width_1 in range(4):
                    for obstacle_depth_1 in range(5):
                        cube_double_template["agent_pos_z"] = agent_z
                        cube_double_template["obj_1_pos_x"] = 0
                        cube_double_template["obj_1_pos_z"] = obj_1_z
                        cube_double_template["obstacle_1_height"] = obstacle_height_1
                        cube_double_template["obstacle_1_width"] = obstacle_width_1
                        cube_double_template["obstacle_1_depth"] = obstacle_depth_1
                        cube_double_template["obstacle_2_height"] = 0
                        configurations.append(cube_double_template.copy())
                        cube_double_template["id"] += 1

                        cube_double_template["agent_pos_z"] = agent_z
                        cube_double_template["obj_2_pos_x"] = 4
                        cube_double_template["obj_2_pos_z"] = obj_1_z
                        cube_double_template["obstacle_2_height"] = obstacle_height_1
                        cube_double_template["obstacle_2_width"] = obstacle_width_1
                        cube_double_template["obstacle_2_depth"] = obstacle_depth_1
                        cube_double_template["obstacle_1_height"] = 0
                        configurations.append(cube_double_template.copy())
                        cube_double_template["id"] += 1

    cube_double_template["obstacle_1_height"] = 0
    cube_double_template["obstacle_2_height"] = 0
    for agent_z in [0, 1, 2]:
        for obj_1_z in range(OBJECT_POSITON_Z):
            for obj_1_x in [0, 1, 2]:
                cube_double_template["agent_pos_z"] = agent_z
                cube_double_template["obj_1_pos_x"] = obj_1_x
                cube_double_template["obj_1_pos_z"] = obj_1_z
                configurations.append(cube_double_template.copy())
                cube_double_template["id"] += 1
                cube_double_template["agent_pos_z"] = agent_z
                cube_double_template["obj_2_pos_x"] = 4 + obj_1_x
                cube_double_template["obj_2_pos_z"] = obj_1_z

                configurations.append(cube_double_template.copy())
                cube_double_template["id"] += 1


    print("No of obstacle scenes", len(configurations) )
    with open("configuration_files/configurations_3_4_cube.json", "w") as fp:
        json.dump(configurations, fp)

def create_barrier_with_door_3_4_trajectores():
    configurations = []
    cube_double_template = {
        "id": 0,
        "barrier_type": "barrier_with_door",
        "agent_shape": 0,
        "obj_shape": 0,
        "agent_pos_z": 2,

        "obj_1_pos_x": 0,
        "obj_1_pos_z": 1,
        "obj_2_pos_x": 4,
        "obj_2_pos_z": 1,

        "obstacle_1_pos_x": 1,
        "obstacle_1_pos_z": 1,
        "obstacle_1_height": 6,
        "obstacle_1_width": 2,
        "obstacle_1_depth": 2,

        "obstacle_2_pos_x": 3,
        "obstacle_2_pos_z": 1,
        "obstacle_2_height": 6,
        "obstacle_2_width": 2,
        "obstacle_2_depth": 2,
      }

    for agent_z in range(3):
        for obj_1_z in range(3):
            for obstacle_z in range(3):
                cube_double_template["agent_pos_z"] = agent_z
                cube_double_template["obj_1_pos_x"] = 0
                cube_double_template["obj_1_pos_z"] = obj_1_z
                cube_double_template["obstacle_1_pos_z"] = obstacle_z
                configurations.append(cube_double_template.copy())
                cube_double_template["id"] += 1

                cube_double_template["agent_pos_z"] = agent_z
                cube_double_template["obj_2_pos_x"] = 4
                cube_double_template["obj_2_pos_z"] = obj_1_z
                cube_double_template["obstacle_2_pos_z"] = obstacle_z
                configurations.append(cube_double_template.copy())
                cube_double_template["id"] += 1


    print("No of obstacle scenes", len(configurations) )
    with open("configuration_files/configs_barrier_with_door_3_4.json", "w") as fp:
        json.dump(configurations, fp)

def create_ramp_trajectories():
    configurations = []
    cube_template = {
                "barrier_type": "ramp",
                "id": 0,
                "agent_shape": 0,
                "agent_pos_x": 2,
                "agent_pos_z": 1,
                "obj_shape": 0,
                "obj_pos_ramp": 0,
                "ramp_height": 1,
                "ramp_rotation": 0
    }
    for agent_x in [0, 2]:
        for agent_z in range(3):
            for obj_pos_ramp in [0, 2]:
                for ramp_height in range(3):
                    for ramp_rotation in [0, 2]:
                        if agent_x != obj_pos_ramp:
                            if (agent_x == 0 and ramp_rotation == 2) or (agent_x == 2 and ramp_rotation == 0):
                                cube_template["agent_pos_x"] = agent_x
                                cube_template["agent_pos_z"] = agent_z
                                cube_template["ramp_height"] = ramp_height
                                cube_template["obj_pos_ramp"] = 0 if obj_pos_ramp == 0 else 1
                                cube_template["ramp_rotation"] = ramp_rotation
                                cube_template["id"] += 1

                                configurations.append(cube_template.copy())
    print("No of obstacle scenes", len(configurations))
    with open("configuration_files/configs_ramps.json", "w") as fp:
        json.dump(configurations, fp)

def create_platform_trajectories():
    configurations = []
    cube_template = {
                "barrier_type": "platform",
                "id": 0,
                "agent_shape": 0,
                "agent_pos_x": 2,
                "agent_pos_z": 2,
                "obj_shape": 0,
                "obj_pos_ramp_x": 0,
                "obj_pos_ramp_z": 2,
                "ramp_height": 0,
            }
    for agent_x in [0, 2]:
        for agent_z in range(3):
            for obj_pos_x in [0, 2]:
                for obj_pos_z in range(3):
                    for ramp_height in range(3):
                        if agent_x != obj_pos_x:
                            cube_template["agent_pos_x"] = agent_x
                            cube_template["agent_pos_z"] = agent_z
                            cube_template["ramp_height"] = ramp_height
                            cube_template["obj_pos_ramp_z"] = obj_pos_z
                            cube_template["obj_pos_ramp_x"] = obj_pos_x
                            cube_template["id"] += 1
                            configurations.append(cube_template.copy())
    print("No of obstacle scenes", len(configurations))
    with open("configuration_files/configs_platform.json", "w") as fp:
        json.dump(configurations, fp)

def create_pit_trajectories():
    cube_template = {
        "barrier_type": "pit",
        "id": 0,
        "agent_shape": 0,
        "obj_shape": 0,
        "agent_pos_x": 0,
        "agent_pos_z": 0,
        "obj_pos_x": 4,
        "obj_pos_z": 2,
        "pit_width": 0,
        "pit_depth": -1,
        "obstacle_pos_x": 1,
        "obstacle_pos_z": 1,
    }
    configurations = []
    idx = 0
    for agent_x in [0, 2]:
        for agent_z in range(3):
            for obj_pos_x in [0, 2]:
                for obj_pos_z in range(3):
                    for pit_width in [-1, 0, 1, 2, 3, 4]:
                        if agent_x != obj_pos_x:
                            cube_template["agent_pos_x"] = agent_x
                            cube_template["agent_pos_z"] = agent_z
                            cube_template["pit_width"] = pit_width
                            cube_template["obj_pos_z"] = obj_pos_z
                            cube_template["obj_pos_x"] = obj_pos_x
                            configurations.append(cube_template.copy())
                            cube_template["id"] += 1
                            idx += 1
    cube_template["barrier_type"] = "pit-with-bridge"
    for agent_x in [0, 2]:
        for agent_z in range(3):
            for obj_pos_x in [0, 2]:
                for obj_pos_z in range(3):
                    for bridge_z in range(3):
                        for pit_width in [0, 1, 2]:
                            if agent_x != obj_pos_x:
                                cube_template["agent_pos_x"] = agent_x
                                cube_template["agent_pos_z"] = agent_z
                                cube_template["pit_width"] = pit_width
                                cube_template["obj_pos_z"] = obj_pos_z
                                cube_template["obj_pos_x"] = obj_pos_x
                                cube_template["bridge_z"] = bridge_z
                                configurations.append(cube_template.copy())
                                cube_template["id"] += 1
                                idx += 1
    print("No of obstacle scenes", len(configurations) )
    with open("configuration_files/configs_pit.json", "w") as fp:
        json.dump(configurations, fp)


def create_barrier_trajectories():
    cube_template = {
        "barrier_type": "cube",
        "id": 0,
        "agent_shape": 0,
        "obj_shape": 0,
        "agent_pos_x": 0,
        "agent_pos_z": 0,
        "obj_pos_x": 4,
        "obj_pos_z": 2,
        "obstacle_pos_x": 1,
        "obstacle_pos_z": 0,
        "obstacle_height": 3,
        "obstacle_width": 0,
        "obstacle_depth": 1,
    }
    configurations = []
    idx = 0
    for agent_x in [0, 2]:
        for agent_z in range(3):
            for obstacle_pos_x in [1]:
                for obstacle_pos_z in range(3):
                    for obstacle_height in range(OBSTACLE_HEIGHTS):
                        for obstacle_depth in range(OBSTACLE_DEPTH):
                            for obstacle_width in range(OBSTACLE_WIDTH):
                                for obj_pos_x in [0, 2]:
                                    for obj_pos_z in range(3):
                                        if agent_x != obj_pos_x:
                                            if agent_z == obj_pos_z and obj_pos_z == obstacle_pos_z and obstacle_height != 0:
                                                print(cube_template["id"])
                                            cube_template["agent_pos_x"] = agent_x
                                            cube_template["agent_pos_z"] = agent_z
                                            cube_template["obstacle_pos_x"] = obstacle_pos_x
                                            cube_template["obstacle_pos_z"] = obstacle_pos_z
                                            cube_template["obstacle_height"] = obstacle_height
                                            cube_template["obstacle_depth"] = obstacle_depth
                                            cube_template["obstacle_width"] = obstacle_width
                                            cube_template["obj_pos_z"] = obj_pos_z
                                            cube_template["obj_pos_x"] = obj_pos_x
                                            configurations.append(cube_template.copy())
                                            cube_template["id"] += 1
                                            idx += 1
    print("No of obstacle scenes", len(configurations))
    with open("configuration_files/configs_barrier.json", "w") as fp:
        json.dump(configurations, fp)


def create_barrier_with_door_trajectories():
    cube_template = {
        "barrier_type": "barrier_with_door",
        "id": 0,
        "agent_shape": 0,
        "obj_shape": 0,
        "agent_pos_x": 0,
        "agent_pos_z": 0,
        "obj_pos_x": 4,
        "obj_pos_z": 2,
        "obstacle_pos_x": 1,
        "obstacle_pos_z": 1,
        "obstacle_height": 6,
        "obstacle_width": 0,
        "obstacle_depth": 0,
    }
    idx = 0
    for agent_x in [0, 2]:
        for agent_z in range(3):
            for obj_pos_x in [0, 2]:
                for obj_pos_z in range(3):
                    for obstacle_pos_z in [0, 1, 2]:
                        for obstacle_width in [0, 1, 2, 3]:
                            if agent_x != obj_pos_x:
                                cube_template["agent_pos_x"] = agent_x
                                cube_template["agent_pos_z"] = agent_z
                                cube_template["obstacle_width"] = obstacle_width
                                cube_template["obj_pos_z"] = obj_pos_z
                                cube_template["obj_pos_x"] = obj_pos_x
                                cube_template["obstacle_pos_z"] = obstacle_pos_z
                                configurations.append(cube_template.copy())
                                cube_template["id"] += 1
                                idx += 1
    print("No of obstacle scenes", len(configurations))
    with open("configuration_files/configs_barrier_with_door.json", "w") as fp:
        json.dump(configurations, fp)

if __name__ == '__main__':
    create_pit_trajectories()
