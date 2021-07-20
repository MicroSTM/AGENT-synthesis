import numpy as np
from util.utils import SceneConfiguration

scene_config = SceneConfiguration()
scene_offset = scene_config.scene_offset


def check_which_side_point_lies(p1, p2, point):
    return np.sign((point[0] - p1[0])*(p2[1] - p1[1]) - (point[1] - p1[1])*(p2[0] - p1[0]))


def line_intersection(line1, line2):
    xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
    ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])

    def det(a, b):
        return a[0] * b[1] - a[1] * b[0]

    div = det(xdiff, ydiff)
    if div == 0:
       raise Exception('lines do not intersect')

    d = (det(*line1), det(*line2))
    x = det(d, xdiff) / div
    y = det(d, ydiff) / div
    return [x, y]


def cross_barrier_with_door(obstacle_obj, target_position, agent_position):
    h_offset = 0.15
    target_direction = 1 if agent_position["x"] > target_position["x"] else -1
    paths = [
        [("goto", obstacle_obj.obstacle_position["x"] + target_direction * (h_offset + obstacle_obj.obstacle_width / 2),
         obstacle_obj.obstacle_position["z"], 0.01),
        ("goto", obstacle_obj.obstacle_position["x"] - target_direction * (h_offset + obstacle_obj.obstacle_width / 2)
         , obstacle_obj.obstacle_position["z"], 0.01),
        ("goto", target_position["x"], target_position["z"], 0.24),
        ("meta", "barrier-door", 0, 0)]
    ]

    return paths

def dist_btw_3d_pts(p1, p2):
    p1 = np.array([p1[0], p1[1], p1[2]])
    p2 = np.array([p2[0], p2[1], p2[2]])
    squared_dist = np.sum((p1 - p2) ** 2, axis=0)
    dist = np.sqrt(squared_dist)
    return dist


def cross_platform_cube(obstacle_obj, target_position, agent_position):
    paths = []
    h_offset = 0.15
    offset = 0.147
    target_direction = 1 if agent_position["x"] > target_position["x"] else -1
    top_corner_point = [
        np.array([obstacle_obj.obstacle_position["x"] + target_direction * (h_offset + obstacle_obj.obstacle_width / 2),
                  obstacle_obj.obstacle_position["z"] - (offset + obstacle_obj.obstacle_depth / 2)]),
        np.array(
            [obstacle_obj.obstacle_position["x"] + target_direction * (h_offset + obstacle_obj.obstacle_width / 2) * -1,
             obstacle_obj.obstacle_position["z"] - (offset + obstacle_obj.obstacle_depth / 2)])
    ]
    bottom_corner_point = [
        np.array([obstacle_obj.obstacle_position["x"] + target_direction * (h_offset + obstacle_obj.obstacle_width / 2),
                  obstacle_obj.obstacle_position["z"] + (offset + obstacle_obj.obstacle_depth / 2)]),
        np.array(
            [obstacle_obj.obstacle_position["x"] + target_direction * (h_offset + obstacle_obj.obstacle_width / 2) * -1,
             obstacle_obj.obstacle_position["z"] + (offset + obstacle_obj.obstacle_depth / 2)])
    ]
    vect_to_target = [
        np.array([agent_position["x"], agent_position["z"]]),
        np.array([target_position["x"], target_position["z"]])
    ]
    jump_point = line_intersection(vect_to_target, [top_corner_point[0], bottom_corner_point[0]])
    jump_point[0] += target_direction * 0.235
    points = [("goto", *jump_point, 0.01)]
    points.append(("jump", obstacle_obj.obstacle_height, 0))

    top_corner_point = [
        np.array([obstacle_obj.obstacle_position["x"] - target_direction * (obstacle_obj.obstacle_width / 2 - h_offset),
                  obstacle_obj.obstacle_position["z"] - (offset + obstacle_obj.obstacle_depth / 2)]),
        np.array(
            [obstacle_obj.obstacle_position["x"] - target_direction * (obstacle_obj.obstacle_width / 2 - h_offset) * -1,
             obstacle_obj.obstacle_position["z"] - (offset + obstacle_obj.obstacle_depth / 2)])
    ]
    bottom_corner_point = [
        np.array([obstacle_obj.obstacle_position["x"] - target_direction * (obstacle_obj.obstacle_width / 2 - h_offset),
                  obstacle_obj.obstacle_position["z"] + (offset + obstacle_obj.obstacle_depth / 2)]),
        np.array(
            [obstacle_obj.obstacle_position["x"] - target_direction * (obstacle_obj.obstacle_width / 2 - h_offset) * -1,
             obstacle_obj.obstacle_position["z"] + (offset + obstacle_obj.obstacle_depth / 2)])
    ]
    vect_to_target = [
        np.array([agent_position["x"], agent_position["z"]]),
        np.array([target_position["x"], target_position["z"]])
    ]
    jump_point = line_intersection(vect_to_target, [top_corner_point[0], bottom_corner_point[0]])
    # jump_point[0] += target_direction * 0.01
    points.append(("goto", *jump_point, 0.01))
    points.append(("jump", -1*obstacle_obj.obstacle_height, 0))
    points.append(("goto", target_position["x"], target_position["z"], 0.24))
    paths.append(points)
    # for e in points:
    #     print(e)
    return paths


def cross_barrier(obstacle_obj, target_position, agent_position, scene_config, config_file=None,inefficient=False):
    paths = []
    h_offset = 0.15
    offset = 0.147
    target_direction = 1 if agent_position["x"] > target_position["x"] else -1
    if agent_position["x"] < obstacle_obj.obstacle_position["x"] < target_position["x"] or \
            target_position["x"] < obstacle_obj.obstacle_position["x"] < agent_position["x"]:
        top_corner_point = [
            np.array([obstacle_obj.obstacle_position["x"] + target_direction * (h_offset + obstacle_obj.obstacle_width / 2),
                     obstacle_obj.obstacle_position["z"] - (offset + obstacle_obj.obstacle_depth / 2)]),
            np.array([obstacle_obj.obstacle_position["x"] + target_direction * (h_offset + obstacle_obj.obstacle_width / 2) * -1,
                     obstacle_obj.obstacle_position["z"] - (offset + obstacle_obj.obstacle_depth / 2)])
        ]
        bottom_corner_point = [
            np.array([obstacle_obj.obstacle_position["x"] + target_direction * (h_offset + obstacle_obj.obstacle_width / 2),
                     obstacle_obj.obstacle_position["z"] + (offset + obstacle_obj.obstacle_depth / 2)]),
            np.array([obstacle_obj.obstacle_position["x"] + target_direction * (h_offset + obstacle_obj.obstacle_width / 2) * -1,
                     obstacle_obj.obstacle_position["z"] + (offset + obstacle_obj.obstacle_depth / 2)])
        ]
        vect_to_target = [
            np.array([agent_position["x"], agent_position["z"]]),
            np.array([target_position["x"], target_position["z"]])
        ]
        # Check if all points are on same side
        get_sides = [check_which_side_point_lies(*vect_to_target, e) for e in top_corner_point + bottom_corner_point]
        # If top and bottom points lie on either side of vect to target than cross barrier
        if get_sides[0] != get_sides[2]:
            # Find best jump point

            jump_point = line_intersection(vect_to_target, [top_corner_point[0], bottom_corner_point[0]])
            jump_point[0] += target_direction * 0.235

            # Jump over barrier
            if obstacle_obj.obstacle_height == 0:
                if inefficient:
                    jump_heights = scene_config.obstacle_height
                else:
                    jump_heights = []
                paths.append([("goto", target_position["x"],target_position["z"], 0.24), ("meta", f"Straight-Target", 0, 0) ])
            else:
                if inefficient:
                    jump_heights = scene_config.obstacle_height[scene_config.obstacle_height.index(obstacle_obj.obstacle_height):]
                else:
                    jump_heights = [obstacle_obj.obstacle_height]
            for jump_height in jump_heights:
                points = [("goto", *jump_point, 0.01),
                          ("jump", jump_height, obstacle_obj.obstacle_width),
                          ("goto", target_position["x"], target_position["z"], 0.24),
                          ("meta", "Jump", jump_height, obstacle_obj.obstacle_width)
                          ]
                paths.append(points)

            if not ("obj_1_pos_x" in config_file and obstacle_obj.obstacle_height == 0):
                # Go around obstacle
                points = [
                    ("goto", obstacle_obj.obstacle_position["x"] + target_direction * (h_offset + obstacle_obj.obstacle_width / 2),
                     obstacle_obj.obstacle_position["z"] - (offset + obstacle_obj.obstacle_depth / 2), 0.01),
                    ("goto", obstacle_obj.obstacle_position["x"] + target_direction * (h_offset + obstacle_obj.obstacle_width / 2) * -1,
                     obstacle_obj.obstacle_position["z"] - (offset + obstacle_obj.obstacle_depth / 2), 0.01),
                    ("goto", target_position["x"], target_position["z"], 0.24),
                    ("meta", "Around-barrier-top", 0, 0)
                ]
                paths.append(points)
                points = [
                    ("goto", obstacle_obj.obstacle_position["x"] + target_direction * (h_offset + obstacle_obj.obstacle_width / 2),
                     obstacle_obj.obstacle_position["z"] + (offset + obstacle_obj.obstacle_depth / 2), 0.01),
                    ("goto", obstacle_obj.obstacle_position["x"] + target_direction * (h_offset + obstacle_obj.obstacle_width / 2) * -1,
                     obstacle_obj.obstacle_position["z"] + (offset + obstacle_obj.obstacle_depth / 2), 0.01),
                    ("goto", target_position["x"], target_position["z"], 0.24),
                    ("meta", "Around-barrier-bottom", 0, 0)
                ]
                paths.append(points)
        else:
            paths.append(
                [("goto", target_position["x"], target_position["z"], 0.24), ("meta", "Straight-Target", 0, 0)])

    else:
        if "obj_1_pos_x" not in config_file:
            if abs(config_file["obj_pos_x"] - config_file["agent_pos_x"]) == 2:
                vect = [-agent_position["x"] + target_position["x"], -agent_position["z"] + target_position["z"]]
                vect = vect/np.linalg.norm(vect)
                vect = 1.2*vect
            else:
                vect = [-agent_position["x"] + target_position["x"], -agent_position["z"] + target_position["z"]]
                vect = vect / np.linalg.norm(vect)
                vect = 0.4 * vect
            paths.append(
                [("goto", target_position["x"], target_position["z"], 0.24), ("meta", f"Straight-Target", 0, 0)])
            # Temp
            for height in [0.1, 0.2, 0.3, 0.4, 0.6, 0.7]:
                points = [("goto", agent_position["x"] + vect[0], agent_position["z"] + vect[1], 0.24),
                         ("jump", -1 * height, 0),
                         ("goto", target_position["x"], target_position["z"], 0.24),
                          ("meta", "No-barrier-jump", -1*height, 0)]
                paths.append(points)
        else:
            paths.append(
                [("goto", target_position["x"], target_position["z"], 0.24), ("meta", "Straight-Target", 0, 0)])
    # for p in paths:
    #     print(p)
    return paths


def cross_pit_scene_3_4(agent_obj, config_file, target_positions, pit_obj):
    target_1_position, target_2_position = target_positions
    paths = []
    scene_config_pit = SceneConfiguration(scene_offset=(0, 1.016, -4.342))
    if "bridge_1_z" in config_file:
        if config_file["bridge_1_z"] != -1:
            l1 = [
                np.array([scene_config_pit.positions[1]["x"] - pit_obj.pit_width_1 / 2 - 0.2, -5]),
                np.array([scene_config_pit.positions[1]["x"] - pit_obj.pit_width_1 / 2 - 0.2, 5])
            ]
            vect_to_target = [
                np.array([agent_obj.agent_position["x"], agent_obj.agent_position["z"]]),
                np.array([target_1_position["x"], target_1_position["z"]])
            ]
            jump_point = line_intersection(l1, vect_to_target)
            points = [
                ("goto", jump_point[0], scene_config_pit.positions_z[config_file["bridge_1_z"]], 0.01),
                ("goto", jump_point[0] + pit_obj.pit_width_1 / 2 + 0.2, scene_config_pit.positions_z[config_file["bridge_1_z"]], 0.01),
                ("goto", jump_point[0] + pit_obj.pit_width_1 + 0.2*2, scene_config_pit.positions_z[config_file["bridge_1_z"]], 0.01),
                ("goto", target_1_position["x"], target_1_position["z"], 0.24),
                ("meta", "Cross-Bridge", 0, 0)
            ]
            paths.append(points)

    elif config_file["pit_width_1"] == -1:
        paths.append(
            [("goto", target_1_position["x"], target_1_position["z"], 0.24),
             ("meta", "Straight-Target", 0, 0)]
        )
    else:
        l1 = [
            np.array([scene_config_pit.positions[1]["x"] - pit_obj.pit_width_1/2 - 0.2, -5]),
            np.array([scene_config_pit.positions[1]["x"] - pit_obj.pit_width_1/2 - 0.2, 5])
        ]
        vect_to_target = [
            np.array([agent_obj.agent_position["x"], agent_obj.agent_position["z"]]),
            np.array([target_1_position["x"], target_1_position["z"]])
        ]
        jump_point = line_intersection(l1, vect_to_target)
        points = [
            ("goto", jump_point[0], jump_point[1], 0.01),
            ("jump", None, scene_config_pit.bridge_width_3_4[config_file["pit_width_1"]]),
            ("goto", target_1_position["x"], target_1_position["z"], 0.24),
            ("meta", "Pit_Jump", 0, 0)
        ]
        paths.append(points)

    if "bridge_2_z" in config_file:
        if config_file["bridge_2_z"] != -1:
            l1 = [
                np.array([scene_config_pit.positions[3]["x"] + pit_obj.pit_width_2 / 2 + 0.2, -5]),
                np.array([scene_config_pit.positions[3]["x"] + pit_obj.pit_width_2 / 2 + 0.2, 5])
            ]
            vect_to_target = [
                np.array([agent_obj.agent_position["x"], agent_obj.agent_position["z"]]),
                np.array([target_2_position["x"], target_2_position["z"]])
            ]
            jump_point = line_intersection(l1, vect_to_target)
            points = [
                ("goto", jump_point[0], scene_config_pit.positions_z[config_file["bridge_2_z"]], 0.01),
                ("goto", jump_point[0] - pit_obj.pit_width_2 / 2 - 0.2, scene_config_pit.positions_z[config_file["bridge_2_z"]], 0.01),
                ("goto", jump_point[0] - pit_obj.pit_width_2 - 0.2*2 , scene_config_pit.positions_z[config_file["bridge_2_z"]], 0.01),
                ("goto", target_2_position["x"], target_2_position["z"], 0.24),
                ("meta", "Cross-Bridge", 0, 0)
            ]
            paths.append(points)

    elif config_file["pit_width_2"] == -1:
        paths.append(
            [("goto", target_2_position["x"], target_2_position["z"], 0.24),
             ("meta", "Straight-Target", 0, 0)]
        )
    else:
        l1 = [
            np.array([scene_config_pit.positions[3]["x"] + pit_obj.pit_width_2 / 2 + 0.2, -5]),
            np.array([scene_config_pit.positions[3]["x"] + pit_obj.pit_width_2 / 2 + 0.2, 5])
        ]
        vect_to_target = [
            np.array([agent_obj.agent_position["x"], agent_obj.agent_position["z"]]),
            np.array([target_2_position["x"], target_2_position["z"]])
        ]
        jump_point = line_intersection(l1, vect_to_target)
        points = [
            ("goto", jump_point[0], jump_point[1], 0.01),
            ("jump", None, scene_config_pit.bridge_width_3_4[config_file["pit_width_2"]]),
            ("goto", target_2_position["x"], target_2_position["z"], 0.24),
            ("meta", "Pit_Jump", 0, 0)
        ]
        paths.append(points)
    return paths


def cross_pit(agent_obj, config_file, target_position, pit_obj):
    paths = []
    points = []
    if pit_obj.bridge:
        direction = 1 if pit_obj.bridge_position["x"] < agent_obj.agent_position["x"] else -1

        points.append(("goto", pit_obj.bridge_position["x"] + direction*(pit_obj.bridge_width/2+0.151),
                       pit_obj.bridge_position["z"], 0.01))

        points.append(("goto", pit_obj.bridge_position["x"] ,
                       pit_obj.bridge_position["z"], 0.01))
        points.append(("goto", pit_obj.bridge_position["x"] + -1*direction * (pit_obj.bridge_width/2+0.151),
                       pit_obj.bridge_position["z"], 0.01))
        points.append(("goto", target_position["x"], target_position["z"], 0.24))
        points.append(("meta", "Cross-Bridge", 0, 0))
        paths.append(points)

    elif config_file["pit_width"] != -1:
        if config_file["agent_pos_x"] == 0:
            jump_point_x = scene_config.pit_positions[0][0]["x"] - pit_obj.pit_side_width/2 + 0.2
        else:
            jump_point_x = scene_config.pit_positions[0][1]["x"] + pit_obj.pit_side_width/ 2 - 0.2

        if config_file["obj_pos_z"] == config_file["agent_pos_z"]:
            jump_point_z = agent_obj.agent_position["z"]
        else:
            jump_point_z = scene_config.positions_z[1] if "obstacle_1_pos_x" in config_file else scene_config.positions_z_scene_1_2[1]
        points.append(("goto", jump_point_x, jump_point_z, 0.01))
        points.append(("jump", None, pit_obj.pit_width))
        points.append(("goto", target_position["x"], target_position["z"], 0.24))
        points.append(("meta", "Pit_Jump", "None", pit_obj.pit_width))
        paths.append(points)
        if pit_obj.top_pt is not None:
            direction = 1 if pit_obj.top_pt["x"] < agent_obj.agent_position["x"] else -1
            points = []
            points.append(("goto", pit_obj.top_pt["x"] + direction*(pit_obj.pit_width/2 + 0.2), pit_obj.top_pt["z"], 0.01))
            points.append(("goto", pit_obj.top_pt["x"], pit_obj.top_pt["z"], 0.01))
            points.append(
                ("goto", pit_obj.top_pt["x"] - direction * (pit_obj.pit_width / 2 + 0.2), pit_obj.top_pt["z"], 0.01))
            points.append(("goto", target_position["x"], target_position["z"], 0.24))
            points.append(("meta", "Pit-Around-barrier-top", 0, 0))
            paths.append(points)
            points = []
            points.append(
                ("goto", pit_obj.bottom_pt["x"] + direction * (pit_obj.pit_width / 2 + 0.2), pit_obj.bottom_pt["z"], 0.01))
            points.append(("goto", pit_obj.bottom_pt["x"], pit_obj.bottom_pt["z"], 0.01))
            points.append(
                ("goto", pit_obj.bottom_pt["x"] - direction * (pit_obj.pit_width / 2 + 0.2), pit_obj.bottom_pt["z"], 0.01))
            points.append(("goto", target_position["x"], target_position["z"], 0.24))
            points.append(("meta", "Pit-Around-barrier-bottom", 0, 0))
            paths.append(points)

    else:
        paths = [
           [("goto", target_position["x"], target_position["z"], 0.24),
            ("meta", "Straight-Target", 0, 0)]
        ]
    return paths


def cross_ramp(ramp_obj, agent_obj, config_file, restrict_paths=[]):
    """
    Get all possible paths
    :return:
    """
    paths = []
    paths_ = []
    points = []
    ramp_offset = 0.5
    if ramp_obj is not None:
        target_direction = 1 if agent_obj.agent_position["x"] > ramp_obj.target_position["x"] else -1
        # Go to jump point 1
        if 1 not in restrict_paths:
            if ((agent_obj.agent_position["x"] > ramp_obj.position["x"]) and ramp_obj.rotation == 0) or \
                    ((agent_obj.agent_position["x"] < ramp_obj.position["x"]) and ramp_obj.rotation == 180):
                points.append(("goto", ramp_obj.jump_point_1["x"], ramp_obj.jump_point_1["z"], 0.01))
                points.append(("jump", ramp_obj.height, 0))
                points.append(("goto", ramp_obj.target_position["x"], ramp_obj.target_position["z"], 0.24))
                paths.append(points)
            elif ramp_obj.rotation in [90, -90]:
                points.append(("goto", ramp_obj.jump_point_1["x"] + target_direction*0.438, ramp_obj.jump_point_1["z"], 0.01))
                points.append(("goto", ramp_obj.jump_point_1["x"], ramp_obj.jump_point_1["z"], 0.01))
                points.append(("rotate", target_direction*(90 if ramp_obj.rotation == 90 else -90)))
                points.append(("jump", ramp_obj.height, 0))
                points.append(("goto", ramp_obj.target_position["x"], ramp_obj.target_position["z"], 0.24))
                paths.append(points)
            elif ((agent_obj.agent_position["x"] > ramp_obj.position["x"]) and ramp_obj.rotation == 180) or \
                    ((agent_obj.agent_position["x"] < ramp_obj.position["x"]) and ramp_obj.rotation == 0):
                # There are multiple paths possible based on where z of agent is
                points = []
                if config_file["agent_pos_z"] in [1, 2]:
                    points.append(("goto",ramp_obj.ramp_start["x"], ramp_obj.ramp_start["z"] - ramp_offset, 0.01))
                points.append(("goto", ramp_obj.jump_point_1["x"], ramp_obj.jump_point_1["z"] - ramp_offset, 0.01))
                points.append(("rotate", target_direction * 90))
                points.append(("goto", ramp_obj.jump_point_1["x"], ramp_obj.jump_point_1["z"], 0.01))
                points.append(("rotate", target_direction * 90))
                points.append(("jump", ramp_obj.height, 0))
                points.append(("goto", ramp_obj.target_position["x"], ramp_obj.target_position["z"], 0.24))
                paths.append(points)


                points = []
                if config_file["agent_pos_z"] in [0, 1]:
                    points.append(("goto", ramp_obj.ramp_start["x"], ramp_obj.ramp_start["z"] + ramp_offset, 0.01))
                points.append(("goto", ramp_obj.jump_point_1["x"], ramp_obj.jump_point_1["z"] + ramp_offset, 0.01))
                points.append(("rotate", target_direction * -90))
                points.append(("goto", ramp_obj.jump_point_1["x"], ramp_obj.jump_point_1["z"], 0.01))
                points.append(("rotate", target_direction * -90))
                points.append(("jump", ramp_obj.height, 0))
                points.append(("goto", ramp_obj.target_position["x"], ramp_obj.target_position["z"], 0.24))
                paths.append(points)
        # Go to jump point 2
        if 2 not in restrict_paths:
            points = []
            if ((agent_obj.agent_position["x"] > ramp_obj.position["x"]) and ramp_obj.rotation == 90) or \
                ((agent_obj.agent_position["x"] < ramp_obj.position["x"]) and ramp_obj.rotation == -90):
                points.append(("goto", ramp_obj.jump_point_2["x"], ramp_obj.jump_point_2["z"], 0.01))
                points.append(("jump", ramp_obj.height, 0))
                points.append(("goto", ramp_obj.target_position["x"], ramp_obj.target_position["z"], 0.24))
                paths.append(points)
            elif ((agent_obj.agent_position["x"] < ramp_obj.position["x"]) and ramp_obj.rotation == 90) or \
                ((agent_obj.agent_position["x"] > ramp_obj.position["x"]) and ramp_obj.rotation == -90):
                points.append(("goto", ramp_obj.jump_point_3["x"], ramp_obj.jump_point_1["z"], 0.01))
                points.append(("goto", ramp_obj.jump_point_2["x"], ramp_obj.jump_point_1["z"], 0.01))
                points.append(("rotate", target_direction * (90 if ramp_obj.rotation == 90 else -90)))
                points.append(("goto", ramp_obj.jump_point_2["x"], ramp_obj.jump_point_2["z"], 0.01))
                points.append(("rotate", target_direction * (90 if ramp_obj.rotation == 90 else -90)))
                points.append(("jump", ramp_obj.height, 0))
                points.append(("goto", ramp_obj.target_position["x"], ramp_obj.target_position["z"], 0.24))
                paths.append(points)

                points = []
                points.append(("goto", ramp_obj.jump_point_3["x"], ramp_obj.ramp_start["z"], 0.01))
                points.append(("goto", ramp_obj.jump_point_2["x"], ramp_obj.ramp_start["z"], 0.01))
                points.append(("rotate", target_direction * (-90 if ramp_obj.rotation == 90 else 90)))
                points.append(("goto", ramp_obj.jump_point_2["x"], ramp_obj.jump_point_2["z"], 0.01))
                points.append(("rotate", target_direction * (-90 if ramp_obj.rotation == 90 else 90)))
                points.append(("jump", ramp_obj.height, 0))
                points.append(("goto", ramp_obj.target_position["x"], ramp_obj.target_position["z"], 0.24))
                paths.append(points)
            elif ramp_obj.rotation in [0, 180]:
                points = []
                # Check if it is facing away
                if config_file["agent_pos_z"] in [1, 2]:
                    if ramp_obj.rotation == 0 and agent_obj.agent_position["x"] < ramp_obj.position["x"]:
                        points.append(
                            ("goto", ramp_obj.ramp_start["x"], ramp_obj.ramp_start["z"] - ramp_offset, 0.01))
                    elif ramp_obj.rotation == 0 and agent_obj.agent_position["x"] > ramp_obj.position["x"]:
                        points.append(
                            ("goto", ramp_obj.jump_point_1["x"], ramp_obj.jump_point_1["z"] - ramp_offset, 0.01))
                if config_file["agent_pos_z"] in [0,1]:
                    if ramp_obj.rotation == 180 and agent_obj.agent_position["x"] < ramp_obj.position["x"]:
                        points.append(("goto", ramp_obj.ramp_start["x"], ramp_obj.ramp_start["z"] + ramp_offset, 0.01))
                    elif ramp_obj.rotation == 180 and agent_obj.agent_position["x"] > ramp_obj.position["x"]:
                        points.append(
                            ("goto", ramp_obj.jump_point_1["x"], ramp_obj.jump_point_1["z"] + ramp_offset, 0.01))
                points.append(("goto", ramp_obj.jump_point_2["x"], ramp_obj.jump_point_2["z"], 0.01))
                points.append(("rotate", target_direction * (90 if ramp_obj.rotation == 0 else -90)))
                points.append(("jump", ramp_obj.height, 0))
                points.append(("goto", ramp_obj.target_position["x"], ramp_obj.target_position["z"], 0.24, 0.7))
                paths.append(points)
        # Go to jump point 3
        if 3 not in restrict_paths:
            points = []
            if ((agent_obj.agent_position["x"] < ramp_obj.position["x"]) and ramp_obj.rotation == 90) or \
                    ((agent_obj.agent_position["x"] > ramp_obj.position["x"]) and ramp_obj.rotation == -90):
                points.append(("goto", ramp_obj.jump_point_3["x"], ramp_obj.jump_point_3["z"], 0.01))
                points.append(("jump", ramp_obj.height, 0))
                points.append(("goto", ramp_obj.target_position["x"], ramp_obj.target_position["z"], 0.24))
                paths.append(points)
            elif ((agent_obj.agent_position["x"] > ramp_obj.position["x"]) and ramp_obj.rotation == 90) or \
                    ((agent_obj.agent_position["x"] < ramp_obj.position["x"]) and ramp_obj.rotation == -90):
                points.append(("goto", ramp_obj.jump_point_2["x"], ramp_obj.jump_point_1["z"], 0.01))
                points.append(("goto", ramp_obj.jump_point_3["x"], ramp_obj.jump_point_1["z"], 0.01))
                points.append(("rotate", target_direction * (90 if ramp_obj.rotation == 90 else -90)))
                points.append(("goto", ramp_obj.jump_point_3["x"], ramp_obj.jump_point_3["z"], 0.01))
                points.append(("rotate", target_direction * (90 if ramp_obj.rotation == 90 else -90)))
                points.append(("jump", ramp_obj.height, 0))
                points.append(("goto", ramp_obj.target_position["x"], ramp_obj.target_position["z"], 0.24))
                paths.append(points)
                points = []
                points.append(("goto", ramp_obj.jump_point_2["x"], ramp_obj.ramp_start["z"], 0.01))
                points.append(("goto", ramp_obj.jump_point_3["x"], ramp_obj.ramp_start["z"], 0.01))
                points.append(("rotate", target_direction * (-90 if ramp_obj.rotation == 90 else 90)))
                points.append(("goto", ramp_obj.jump_point_3["x"], ramp_obj.jump_point_3["z"], 0.01))
                points.append(("rotate", target_direction * (-90 if ramp_obj.rotation == 90 else 90)))
                points.append(("jump", ramp_obj.height, 0))
                points.append(("goto", ramp_obj.target_position["x"], ramp_obj.target_position["z"], 0.24))
                paths.append(points)
            elif ramp_obj.rotation in [0, 180]:
                points = []
                # Check if it is facing away
                # Check if it is facing away
                if config_file["agent_pos_z"] in [1, 2]:
                    if ramp_obj.rotation == 0 and agent_obj.agent_position["x"] < ramp_obj.position["x"]:
                        points.append(
                            ("goto", ramp_obj.ramp_start["x"], ramp_obj.ramp_start["z"] + ramp_offset, 0.01))
                    elif ramp_obj.rotation == 0 and agent_obj.agent_position["x"] > ramp_obj.position["x"]:
                        points.append(
                            ("goto", ramp_obj.jump_point_1["x"], ramp_obj.jump_point_1["z"] + ramp_offset, 0.01))
                if config_file["agent_pos_z"] in [0, 1]:
                    if ramp_obj.rotation == 180 and agent_obj.agent_position["x"] < ramp_obj.position["x"]:
                        points.append(("goto", ramp_obj.ramp_start["x"], ramp_obj.ramp_start["z"] - ramp_offset, 0.01))
                    elif ramp_obj.rotation == 180 and agent_obj.agent_position["x"] > ramp_obj.position["x"]:
                        points.append(
                            ("goto", ramp_obj.jump_point_1["x"], ramp_obj.jump_point_1["z"] - ramp_offset, 0.01))
                points.append(("goto", ramp_obj.jump_point_3["x"], ramp_obj.jump_point_3["z"], 0.01))
                points.append(("rotate", target_direction * (-90 if ramp_obj.rotation == 0 else 90)))
                points.append(("jump", ramp_obj.height, 0))
                points.append(("goto", ramp_obj.target_position["x"], ramp_obj.target_position["z"], 0.24))
                paths.append(points)

        # Go up the ramp
        if "R" not in restrict_paths:
            points = []
            if ((agent_obj.agent_position["x"] < ramp_obj.position["x"]) and ramp_obj.rotation == 0) or \
                    ((agent_obj.agent_position["x"] > ramp_obj.position["x"]) and ramp_obj.rotation == 180):
                points.append(("goto", ramp_obj.ramp_start["x"], ramp_obj.ramp_start["z"], 0.01))
                points.append(("goto", ramp_obj.ramp_start_["x"], ramp_obj.ramp_start_["z"], 0.01))
                if ramp_obj.height == 0.8:
                    points.append(("goto", ramp_obj.target_position["x"],  ramp_obj.target_position["y"],
                                   ramp_obj.target_position["z"], 0.2, 0.7))
                else:
                    points.append(("goto", ramp_obj.target_position["x"], ramp_obj.target_position["y"],
                                   ramp_obj.target_position["z"], 0.2, 0.9))
                points.append(("settle", 25))
                points.append(("meta", "Go-up-ramp", 0, 0))
                paths.append(points)

            elif ramp_obj.rotation in [90, -90]:
                points.append(("goto", ramp_obj.ramp_start["x"] + target_direction*ramp_offset, ramp_obj.ramp_start["z"], 0.01))
                points.append(("goto", ramp_obj.ramp_start["x"], ramp_obj.ramp_start["z"], 0.01))
                points.append(("goto", ramp_obj.ramp_start_["x"], ramp_obj.ramp_start_["z"], 0.01))
                points.append(("rotate", target_direction*-90))
                points.append(("goto", ramp_obj.target_position["x"], ramp_obj.target_position["z"], 0.2, 0.7))
                points.append(("settle", 25))
                points.append(("meta", "Go-up-ramp", 0, 0))
                paths.append(points)
            elif ((agent_obj.agent_position["x"] > ramp_obj.position["x"]) and ramp_obj.rotation == 0) or \
                    ((agent_obj.agent_position["x"] < ramp_obj.position["x"]) and ramp_obj.rotation == 180):
                if config_file["agent_pos_z"] in [1, 2]:
                    points.append(("goto",ramp_obj.jump_point_1["x"], ramp_obj.jump_point_1["z"] - ramp_offset, 0.01))
                points.append(("goto", ramp_obj.ramp_start["x"], ramp_obj.jump_point_1["z"] - ramp_offset, 0.01))
                points.append(("goto", ramp_obj.ramp_start["x"], ramp_obj.ramp_start["z"], 0.01))
                points.append(("goto", ramp_obj.ramp_start_["x"], ramp_obj.ramp_start_["z"], 0.01))
                points.append(("goto", ramp_obj.target_position["x"], ramp_obj.target_position["z"], 0.2, 0.7))
                points.append(("settle", 25))
                points.append(("meta", "Go-up-ramp", 0, 0))
                paths.append(points)

                points = []
                if config_file["agent_pos_z"] in [0, 1]:
                    points.append(("goto", ramp_obj.jump_point_1["x"], ramp_obj.jump_point_1["z"] + ramp_offset, 0.01))

                points.append(("goto", ramp_obj.ramp_start["x"], ramp_obj.jump_point_1["z"] + ramp_offset, 0.01))
                # points.append(("rotate", target_direction*-90))
                points.append(("goto", ramp_obj.ramp_start["x"], ramp_obj.ramp_start["z"], 0.01))
                # points.append(("rotate", target_direction*-90))
                # points.append(("goto", ramp_obj.target_position["x"], ramp_obj.target_position["y"], ramp_obj.target_position["z"], 0.24, 0.7))
                points.append(("settle", 20))
                points.append(("meta", "Go-up-ramp", 0, 0))
                paths.append(points)
    # paths = paths_

    # exit()
    return paths

def cross_platform(ramp_obj, agent_obj, target_position=None):
    """
    Get all possible paths
    :return:
    """
    paths = []

    points = []

    if ramp_obj is not None:
        dist_p1 = dist_btw_3d_pts([agent_obj.agent_position["x"], agent_obj.agent_position["y"],
                               agent_obj.agent_position["z"]],[ ramp_obj.jump_point_1["x"],
                              ramp_obj.jump_point_1["y"], ramp_obj.jump_point_1["z"]])

        dist_p2 = dist_btw_3d_pts([agent_obj.agent_position["x"], agent_obj.agent_position["y"],
                               agent_obj.agent_position["z"]], [ramp_obj.jump_point_2["x"],
                                                                ramp_obj.jump_point_2["y"], ramp_obj.jump_point_2["z"]])

        dist_p3 = dist_btw_3d_pts([agent_obj.agent_position["x"], agent_obj.agent_position["y"],
                               agent_obj.agent_position["z"]], [ramp_obj.jump_point_3["x"],
                                                                ramp_obj.jump_point_3["y"], ramp_obj.jump_point_3["z"]])
        if dist_p1 < dist_p2 and dist_p1 < dist_p3:
            selected_point = ramp_obj.jump_point_1
            selected_point_ = ramp_obj.jump_point_1_
        elif dist_p2 < dist_p1 and dist_p2 < dist_p3:
            selected_point = ramp_obj.jump_point_2
            selected_point_ = ramp_obj.jump_point_2_
        else:
            selected_point = ramp_obj.jump_point_3
            selected_point_ = ramp_obj.jump_point_3_
        points.append(("goto", selected_point_["x"], selected_point_["z"], 0.01))
        points.append(("goto", selected_point["x"], selected_point["z"], 0.01))
        points.append(("jump", ramp_obj.height, 0))
        points.append(("goto", ramp_obj.target_position["x"], ramp_obj.target_position["z"], 0.24))
        points.append(("meta", "Platform-jump", 0, 0))
        paths.append(points)
    else:
        points.append(("goto", target_position["x"], target_position["z"], 0.24))
        points.append(("meta", "Straight-Target", 0, 0))
        paths.append(points)

    return paths