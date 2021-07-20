from util import utils
from util.obstacle import Obstacle
from util.barrier_with_door import BarrierWithDoor
from util.occuluder import Occluder
from util.utils import SceneConfiguration
from util.pit import Pit

def create_based_config(**kwargs):
    config_file = kwargs["config_file"]
    tdw_object = kwargs["tdw_object"]
    high_scene = kwargs["high_scene"]
    camera_obj = kwargs["camera_obj"]
    scene_config = kwargs["scene_config"]
    agent = kwargs["agent_class"]
    target_color = kwargs["target_color"]
    target_shape = kwargs["target_shape"] if "target_shape" in kwargs else None
    args = kwargs["args"]
    occluder, target_obj, pit_obj = None, None, None
    obj_list, pit_ids = [], []
    pit_depth = scene_config.pit_depth_
    tdw_object.communicate({"$type": "send_log_messages"})
    ramp, obstacle = None, None
    if config_file["barrier_type"] in ["pit", "pit-with-bridge"]:
        if not high_scene:
            high_scene = True
            tdw_object.communicate(camera_obj.increase_height(1.009 + pit_depth))
    else:
        if high_scene:
            high_scene = False
            tdw_object.communicate(camera_obj.increase_height(-1.009 - pit_depth))
    # self.config_file = config_file
    if config_file["barrier_type"] in ["pit", "pit-with-bridge"]:
        pit_obj = Pit(config_file)
        pit_ids = pit_obj.create_pit(tdw_object, scene_config)
        obj_list.extend(pit_ids)
    elif config_file["barrier_type"] in ["cube", "barrier_with_door"]:
        obstacle_width = scene_config.obstacle_width[config_file["obstacle_width"]]
        obstacle_position = {
            "x": scene_config.positions_x_scene_1_2[2] - obstacle_width/2 - 0.25
                if config_file["obstacle_pos_x"] == -1 else
                scene_config.positions_x_scene_1_2[config_file["obstacle_pos_x"]],
            "y": scene_config.positions_y[config_file["obstacle_height"]],
            "z": scene_config.positions_z_scene_1_2[config_file["obstacle_pos_z"]]
        }

        if config_file["obstacle_height"] == 0:
            obstacle_height = 0
        else:
            obstacle_height = scene_config.obstacle_height[config_file["obstacle_height"] - 1]
        obstacle_depth = scene_config.obstacle_depth[config_file["obstacle_depth"]]
        if config_file["barrier_type"] == "cube":
            obstacle = Obstacle(tdw_object,
                                position=obstacle_position,
                                rotation={"x": 0, "y": 0, "z": 0}, height=obstacle_height,
                                width=obstacle_width, depth=obstacle_depth)
        elif config_file["barrier_type"] == "barrier_with_door":
            obstacle = BarrierWithDoor(
                position=obstacle_position, height=obstacle_height,
                width=obstacle_width, depth=obstacle_depth, tdw_object=tdw_object,
                door_depth=0.7, config_file=config_file
            )
        if config_file["obstacle_height"] != 0:
            obstacle.create_obstacle(kwargs["actually_create"])
            if config_file["barrier_type"] == "barrier_with_door":
                obj_list.append(obstacle.barrier_1)
                obj_list.append(obstacle.barrier_2)
                obj_list.append(obstacle.barrier_3)
            elif config_file["barrier_type"] == "cube":
                obj_list.append(obstacle.obstacle_id)
    elif config_file["barrier_type"] == "platform-cube":
        obstacle_position = {
            "x": scene_config.positions_x_scene_1_2[config_file["obstacle_pos_x"]],
            "y": scene_config.positions_y_platform_cube[config_file["obstacle_height"]],
            "z": scene_config.positions_z_scene_1_2[config_file["obstacle_pos_z"]]
        }
        obstacle = Obstacle(tdw_object, position=obstacle_position,rotation={"x": 0, "y": 0, "z": 0},
                            height=scene_config.platform_cube_height[config_file["obstacle_height"]], width=1,
                            depth=3)
        obstacle.create_obstacle(kwargs["actually_create"])
    agent_position = {
        "x": scene_config.positions_x_scene_1_2[config_file["agent_pos_x"]],
        "y": 1.016 + pit_depth if config_file["barrier_type"] in ["pit", "pit-with-bridge"] else scene_config.positions_y[0],
        "z": scene_config.positions_z_scene_1_2[config_file["agent_pos_z"]]
    }
    agent.create_agent_new(agent_position, kwargs["agent_color"], kwargs["agent_shape"])
    if config_file["barrier_type"] in ["pit", "pit-with-bridge", "cube", "barrier_with_door", "platform-cube"]:
        target_position = {
            "x": scene_config.positions_x_scene_1_2[config_file["obj_pos_x"]],
            "y": 1.016 + pit_depth if config_file["barrier_type"] in ["pit", "pit-with-bridge"] else scene_config.positions_y[0],
            "z": scene_config.positions_z_scene_1_2[config_file["obj_pos_z"]]
        }
        target_obj = utils.create_target(tdw_object, position=target_position,
                                         rotation={"x": 0, "y": 0, "z": 0}, color=target_color,
                                         object_type=target_shape)
        target_id = target_obj.target_id
    elif config_file["barrier_type"] in ["ramp", "platform"]:
        if config_file["barrier_type"] == "platform":
            config_file["ramp_rotation"] = 3
        if config_file["ramp_rotation"] in [1, 3]:
            offset = 0.4
        else:
            offset = 0.9

        if config_file["barrier_type"] == "platform":
            direction = -1 if config_file["obj_pos_ramp_x"] == 0 else 1
            ramp_position = {
                # "x": scene_config.positions_x_scene_1_2[0 if config_file["obj_pos_ramp_x"] == 0 else 2] ,
                "x": scene_config.positions_x_scene_1_2[0 if config_file["obj_pos_ramp_x"] == 0 else 2] + direction*0.344,
                "y": 0,
                "z": scene_config.positions_z_scene_1_2[config_file["obj_pos_ramp_z"]]
                # "z": scene_config.positions_z_scene_1_2[config_file["obj_pos_ramp_z"]] + 0.358
            }
        else:
            direction = -1 if config_file["obj_pos_ramp"] == 0 else 1
            ramp_position = {
                "x": scene_config.positions_x_scene_1_2[0 if config_file["obj_pos_ramp"] == 0 else 2] + direction *offset,
                "y": 0,
                "z": scene_config.positions_z_scene_1_2[1]
            }
        ramp = utils.create_slope_l(tdw_object, {"x": ramp_position["x"], "y": 0, "z": ramp_position["z"]},
                                    height=scene_config.ramp_height[config_file["ramp_height"]],
                                    rotation=scene_config.ramp_rotation[config_file["ramp_rotation"]],
                                    platform_only=config_file["barrier_type"] == "platform")
        target_position = ramp.target_position
        target_obj = utils.create_target(tdw_object, position=target_position,
                                         rotation={"x": 0, "y": 0, "z": 0}, color=target_color,
                                         object_type=target_shape)
        target_id = target_obj.target_id
        obj_list.append(ramp.ramp_base_id)
        if config_file["barrier_type"] in ["ramp"]:
            obj_list.append(ramp.ramp_slope_id)
    if "enable_image" in kwargs:
        if kwargs["enable_image"]:
            utils.enable_images(tdw_object, single_camera=True)
    obj_list.extend([target_id, agent.agent_id])
    # Temp code
    if "add_occuluder" in kwargs:
        add_occuluder = kwargs["add_occuluder"]
        if add_occuluder:
            scene_state_old = kwargs["scene_state_old"]

            if scene_state_old["barrier_type"] in ["pit", "pit-with-bridge"]:
                is_pit=True
                obstacle_height = scene_config.obstacle_height[0]
                obstacle_width = scene_config.bridge_width[scene_state_old["pit_width"]]
                obstacle_depth = scene_config.pit_depth[scene_state_old["pit_depth"]]
                obstacle_position = {
                    "x": scene_config.positions_x_scene_1_2[scene_state_old["obstacle_pos_x"]],
                    "y": scene_config.positions_y[0] + 1.009,
                    "z": scene_config.positions_z_scene_1_2[scene_state_old["obstacle_pos_z"]]
                }
            else:
                is_pit = False
                obstacle_position = {
                    "x": scene_config.positions_x_scene_1_2[scene_state_old["obstacle_pos_x"]],
                    "y": scene_config.positions_y[scene_state_old["obstacle_height"]],
                    "z": scene_config.positions_z_scene_1_2[scene_state_old["obstacle_pos_z"]]
                }
                obstacle_height = scene_config.obstacle_height[scene_state_old["obstacle_height"] - 1]
                obstacle_width = scene_config.obstacle_width[scene_state_old["obstacle_width"]]
                obstacle_depth = scene_config.obstacle_depth[scene_state_old["obstacle_depth"]]
            obstacle_ = Obstacle(tdw_object,
                                position=obstacle_position,
                                rotation={"x": 0, "y": 0, "z": 0}, height=obstacle_height,
                                width=obstacle_width, depth=obstacle_depth)

            occluder = Occluder(camera_obj, obstacle_, pit=is_pit)
            occluder.create(tdw_object=tdw_object)
            obj_list.append(occluder.occluder_id)

    cmd = [
            {"$type": "send_segmentation_colors", "ids": obj_list, "frequency": "always"},
                            {"$type": "send_bounds", "ids": obj_list, "frequency": "always"},
                            {"$type": "send_transforms", "ids": obj_list, "frequency": "always"},
                            {"$type": "send_rigidbodies", "ids": obj_list, "frequency": "always"},

                            ]
    if args.follow_camera:
        cmd.append(
            {"$type": "send_id_pass_segmentation_colors", "ids": ["agent_follow_camera"], "frequency": "always"}
        )
    resp = tdw_object.communicate(cmd)
    direction = 1 if agent_position["x"] > target_position["x"] else -1
    agent.direction = direction

    return_state = {
        "pit_ids": pit_ids,
        "obstacle": obstacle,
        "agent": agent,
        "target_position": target_position,
        "ramp": ramp,
        "target_id": target_id,
        "high_scene": high_scene,
        "direction": direction,
        "target_obj": target_obj,
        "pit_obj": pit_obj,
        "occluder": occluder
    }
    return return_state

def construct_1_goal_object_meta_data(**kwargs):
    object_meta = {
        kwargs["target_id"]: {
            "type": "goal",
            "color": kwargs["target_color"],
            "size": {"x": 0.2, "y": 0.2, "z": 0.2}
        },
        kwargs["agent"].agent_id: {
            "type": "agent",
            "color": kwargs["agent_color"],
            "size": {"x": 0.2, "y": 0.2, "z": 0.2}
        },
    }
    if kwargs["config_file"]["barrier_type"] == "barrier_with_door":
        object_meta[kwargs["obstacle"].barrier_1] = {
            "type": "barrier_with_door_1",
            "color": {"r": 0.219607845, "g": 0.5156862754, "b": 0.2901961, "a": 1.0},
            "obstacle_height": kwargs["obstacle"].obstacle_height,
            "obstacle_width": kwargs["obstacle"].obstacle_width,
            "obstacle_depth": kwargs["obstacle"].gap
        }
        object_meta[kwargs["obstacle"].barrier_2] = {
            "type": "barrier_with_door_2",
            "color": {"r": 0.219607845, "g": 0.5156862754, "b": 0.2901961, "a": 1.0},
            "obstacle_height": kwargs["obstacle"].obstacle_height,
            "obstacle_width": kwargs["obstacle"].obstacle_width,
            "obstacle_depth": kwargs["obstacle"].gap
        }
        object_meta[kwargs["obstacle"].barrier_3] = {
            "type": "barrier_with_door_3",
            "color": {"r": 0.219607845, "g": 0.5156862754, "b": 0.2901961, "a": 1.0},
            "obstacle_height": kwargs["obstacle"].center_peice_height,
            "obstacle_width": kwargs["obstacle"].obstacle_width,
            "obstacle_depth": kwargs["obstacle"].door_depth
        }
    elif kwargs["config_file"]["barrier_type"] == "cube":
        if kwargs["obstacle"].obstacle_id is not None:
            object_meta[kwargs["obstacle"].obstacle_id] = {
                "type": "barrier",
                "color": {"r": 0.219607845, "g": 0.5156862754, "b": 0.2901961, "a": 1.0},
                "obstacle_height": kwargs["obstacle"].obstacle_height,
                "obstacle_width": kwargs["obstacle"].obstacle_width,
                "obstacle_depth": kwargs["obstacle"].obstacle_depth
            }
    elif kwargs["config_file"]["barrier_type"] in ["ramp", "platform"]:
        object_meta[kwargs["ramp"].ramp_base_id] = {
            "type": "ramp_platform",
            "color": {"r": 0, "g": 0.03, "b": 0.22, "a": 1.0},
            "size": kwargs["ramp"].positions["base_scale"]
        }
        if kwargs["config_file"]["barrier_type"] == "ramp":
            object_meta[kwargs["ramp"].ramp_slope_id] = {
                "type": "ramp_slope",
                "color": {"r": 0, "g": 0.03, "b": 0.22, "a": 1.0},
                "size": kwargs["ramp"].positions["slope_scale"]
            }
    elif kwargs["config_file"]["barrier_type"] in ["pit", "pit-with-bridge"]:
        j = 0
        for pit_id in kwargs["pit_ids"]:
            pit_id_taken = False
            if kwargs["pit_obj"].bridge_1 is not None:
                if pit_id == kwargs["pit_obj"].bridge_1:
                    object_meta[pit_id] = {
                        "type": f"pit_bridge"
                    }
                    pit_id_taken = True
            if not pit_id_taken:
                object_meta[pit_id] = {
                    "type": f"pit_side_{j}"
                }
                j += 1

    if kwargs["occluder"] is not None:
        object_meta[kwargs["occluder"].occluder_id] = {
            "type": "occluder",
            "height": kwargs["occluder"].scale["y"],
            "width": kwargs["occluder"].scale["x"],
            "depth": kwargs["occluder"].scale["z"],
            "position": kwargs["occluder"].occluder_position,
            "rotation": kwargs["occluder"].occluder_rotation,
            "color": {"r": 0.519607845, "g": 0.5156862754, "b": 0.2901961, "a": 1.0}
        }

    return object_meta

# import numpy as np
# def distance_between_points(p1, p2):
#     p1, p2 = np.array(p1), np.array(p2)
#     squared_dist = np.sum((p1 - p2) ** 2, axis=0)
#     dist = np.sqrt(squared_dist)
#     return dist

def create_state_data(agent, object_meta, camera_obj, metadata, use_force=True):
    state_datas = agent.agent_state_data.copy()
    # assert len(agent.forces) == len(state_datas)

    for i, state_data in enumerate(state_datas):
        for keys in state_data.keys():
            state_data[keys].update(object_meta[keys])
        state_data["camera"] = {
            "position": camera_obj.camera_top_side_pos,
            "rotation": camera_obj.camera_top_side_rot,
            "screen_height": camera_obj.height,
            "screen_width": camera_obj.width
        }
    state_datas_ = []

    if not use_force:
        for state_data in state_datas:
            state_data_element = {}
            obj_id_to_type = {}
            for key in state_data.keys():
                if "type" in state_data[key]:
                    state_data_element[state_data[key]["type"]] = state_data[key]
                    obj_id_to_type[key] = state_data[key]["type"]
                else:
                    state_data_element[key] = state_data[key]
            state_data_element["agent"]["path_meta_data"] = metadata
            state_data_element["agent"]["visible_objects"] = [obj_id_to_type[e] for e in
                                                              state_data_element["agent"]["visible_objects"]]
            state_datas_.append(state_data_element)
    else:
        for state_data, force in zip(state_datas, agent.forces):
            state_data_element = {}
            for key in state_data.keys():
                if "type" in state_data[key]:
                    state_data_element[state_data[key]["type"]] = state_data[key]
                else:
                    state_data_element[key] = state_data[key]

            state_data_element["agent"]["path_meta_data"] = metadata
            state_data_element["agent"]["force"] = force

            state_datas_.append(state_data_element)
    return state_datas_


def construct_2_goal_object_meta_data(**kwargs):
    # Create object meta
    object_meta = {
        kwargs["target_1_id"]: {
            "type": "goal_1",
            "color": kwargs["target_1_color"],
            "position": kwargs["target_1_position"],
            "rotation": {"x": 0, "y": 0, "z": 0},
            "size": {"x": 0.2, "y": 0.2, "z": 0.2}
        },
        kwargs["target_2_id"]: {
            "type": "goal_2",
            "color": kwargs["target_2_color"],
            "position": kwargs["target_2_position"],
            "rotation": {"x": 0, "y": 0, "z": 0},
            "size": {"x": 0.2, "y": 0.2, "z": 0.2}
        },
        kwargs["agent"].agent_id: {
            "type": "agent",
            "color": kwargs["agent_color"],
            "size": {"x": 0.2, "y": 0.2, "z": 0.2}
        },
    }
    if isinstance(kwargs["obstacle_1"], BarrierWithDoor):
        if kwargs["obstacle_1"].barrier_1 is not None:
            object_meta[kwargs["obstacle_1"].barrier_1] = {
                "type": "barrier_1_with_door_1",
                "color": {"r": 0.219607845, "g": 0.5156862754, "b": 0.2901961, "a": 1.0},
                "obstacle_height": kwargs["obstacle_1"].obstacle_height,
                "obstacle_width": kwargs["obstacle_1"].obstacle_width,
                "obstacle_depth": kwargs["obstacle_1"].gap
            }
            object_meta[kwargs["obstacle_1"].barrier_2] = {
                "type": "barrier_1_with_door_2",
                "color": {"r": 0.219607845, "g": 0.5156862754, "b": 0.2901961, "a": 1.0},
                "obstacle_height": kwargs["obstacle_1"].obstacle_height,
                "obstacle_width": kwargs["obstacle_1"].obstacle_width,
                "obstacle_depth": kwargs["obstacle_1"].gap
            }
            object_meta[kwargs["obstacle_1"].barrier_3] = {
                "type": "barrier_1_with_door_3",
                "color": {"r": 0.219607845, "g": 0.5156862754, "b": 0.2901961, "a": 1.0},
                "obstacle_height": kwargs["obstacle_1"].center_peice_height,
                "obstacle_width": kwargs["obstacle_1"].obstacle_width,
                "obstacle_depth": kwargs["obstacle_1"].door_depth
            }
    if isinstance(kwargs["obstacle_2"], BarrierWithDoor):
        if kwargs["obstacle_2"].barrier_1 is not None:
            object_meta[kwargs["obstacle_2"].barrier_1] = {
                "type": "barrier_2_with_door_1",
                "color": {"r": 0.219607845, "g": 0.5156862754, "b": 0.2901961, "a": 1.0},
                "obstacle_height": kwargs["obstacle_2"].obstacle_height,
                "obstacle_width": kwargs["obstacle_2"].obstacle_width,
                "obstacle_depth": kwargs["obstacle_2"].gap
            }
            object_meta[kwargs["obstacle_2"].barrier_2] = {
                "type": "barrier_2_with_door_2",
                "color": {"r": 0.219607845, "g": 0.5156862754, "b": 0.2901961, "a": 1.0},
                "obstacle_height": kwargs["obstacle_2"].obstacle_height,
                "obstacle_width": kwargs["obstacle_2"].obstacle_width,
                "obstacle_depth": kwargs["obstacle_2"].gap
            }
            object_meta[kwargs["obstacle_2"].barrier_3] = {
                "type": "barrier_2_with_door_3",
                "color": {"r": 0.219607845, "g": 0.5156862754, "b": 0.2901961, "a": 1.0},
                "obstacle_height": kwargs["obstacle_2"].center_peice_height,
                "obstacle_width": kwargs["obstacle_2"].obstacle_width,
                "obstacle_depth": kwargs["obstacle_2"].door_depth
            }
    if isinstance(kwargs["obstacle_1"], Obstacle):
        if kwargs["obstacle_1"].obstacle_id is not None:
            object_meta[kwargs["obstacle_1"].obstacle_id] = {
                "type": "barrier_1",
                "color": {"r": 0.219607845, "g": 0.5156862754, "b": 0.2901961, "a": 1.0},
                "position": kwargs["obstacle_1"].obstacle_position,
                "rotation": {"x": 0, "y": 0, "z": 0},
                "obstacle_height": kwargs["obstacle_1"].obstacle_height,
                "obstacle_width": kwargs["obstacle_1"].obstacle_width,
                "obstacle_depth": kwargs["obstacle_1"].obstacle_depth
            }
    if isinstance(kwargs["obstacle_1"], Obstacle):
        if kwargs["obstacle_2"].obstacle_id is not None:
            object_meta[kwargs["obstacle_2"].obstacle_id] = {
                "type": "barrier_2",
                "color": {"r": 0.219607845, "g": 0.5156862754, "b": 0.2901961, "a": 1.0},
                "position": kwargs["obstacle_2"].obstacle_position,
                "rotation": {"x": 0, "y": 0, "z": 0},
                "obstacle_height": kwargs["obstacle_2"].obstacle_height,
                "obstacle_width": kwargs["obstacle_2"].obstacle_width,
                "obstacle_depth": kwargs["obstacle_2"].obstacle_depth
            }
    if kwargs["ramp_1"] is not None:
        object_meta[kwargs["ramp_1"].ramp_base_id] = {
            "type": "ramp_platform_1",
            "color": {"r": 0, "g": 0.03, "b": 0.22, "a": 1.0},
            "position": kwargs["ramp_1"].positions["base_position"],
            "rotation": kwargs["ramp_1"].positions["base_rotation"],
            "size": kwargs["ramp_1"].positions["base_scale"]
        }
        object_meta[kwargs["ramp_1"].ramp_slope_id] = {
            "type": "ramp_slope_1",
            "color": {"r": 0, "g": 0.03, "b": 0.22, "a": 1.0},
            "position": kwargs["ramp_1"].positions["slope_position"],
            "rotation": kwargs["ramp_1"].positions["slope_rotation"],
            "size": kwargs["ramp_1"].positions["slope_scale"]
        }
    if kwargs["ramp_2"] is not None:
        object_meta[kwargs["ramp_2"].ramp_base_id] = {
            "type": "ramp_platform_2",
            "color": {"r": 0, "g": 0.03, "b": 0.22, "a": 1.0},
            "position": kwargs["ramp_2"].positions["base_position"],
            "rotation": kwargs["ramp_2"].positions["base_rotation"],
            "size": kwargs["ramp_2"].positions["base_scale"]
        }
        object_meta[kwargs["ramp_2"].ramp_slope_id] = {
            "type": "ramp_slope_2",
            "color": {"r": 0, "g": 0.03, "b": 0.22, "a": 1.0},
            "position": kwargs["ramp_2"].positions["slope_position"],
            "rotation": kwargs["ramp_2"].positions["slope_rotation"],
            "size": kwargs["ramp_2"].positions["slope_scale"]
        }
    if kwargs["config_file"]["barrier_type"] in ["pit", "pit-with-bridge"]:
        j = 0
        for pit_id in kwargs["pit_ids"]:
            pit_id_taken = False
            if kwargs["pit_obj"].bridge_1 is not None:
                if pit_id == kwargs["pit_obj"].bridge_1:
                    object_meta[pit_id] = {
                        "type": f"pit_bridge_1"
                    }
                    pit_id_taken = True
            if kwargs["pit_obj"].bridge_2 is not None:
                if pit_id == kwargs["pit_obj"].bridge_2:
                    object_meta[pit_id] = {
                        "type": f"pit_bridge_2"
                    }
                    pit_id_taken = True
            if not pit_id_taken:
                object_meta[pit_id] = {
                    "type": f"pit_side_part_{j}"
                }
                j += 1
    return object_meta


def create_based_config_2_goal(**kwargs):
    obj_list = []
    obstacle_1, obstacle_2, ramp_1, ramp_2, target_1_obj, target_1_obj, pit_obj, target_1_id, target_2_id = \
        None, None, None, None, None, None, None, None, None
    pit_ids = []
    config_file = kwargs["config_file"]
    tdw_object = kwargs["tdw_object"]
    high_scene = kwargs["high_scene"]
    camera_obj = kwargs["camera_obj"]
    agent = kwargs["agent"]
    target_1_color = kwargs["target_1_color"]
    target_2_color = kwargs["target_2_color"]
    target_1_shape = None if "target_1_shape" not in kwargs else kwargs["target_1_shape"]
    target_2_shape = None if "target_2_shape" not in kwargs else kwargs["target_2_shape"]
    tdw_object.communicate({"$type": "send_log_messages"})
    if config_file["barrier_type"] in ["pit", "pit-with-bridge"]:
        scene_config = SceneConfiguration(scene_offset=(0, 1.016, -4.342))
        pit_depth = scene_config.pit_depth_
        if not high_scene:
            high_scene = True
            tdw_object.communicate(camera_obj.increase_height(1.009 + pit_depth))
    else:
        scene_config = SceneConfiguration()
        pit_depth = scene_config.pit_depth_
        if high_scene:
            high_scene = False
            tdw_object.communicate(camera_obj.increase_height(-1.009 - pit_depth))
    agent_position = {
        "x": scene_config.positions_x[2],
        "y": 1.016 + pit_depth if config_file["barrier_type"] in ["pit", "pit-with-bridge"] else scene_config.positions_y[0],
        "z": scene_config.positions_z[config_file["agent_pos_z"]]
    }
    agent.create_agent_new(agent_position, kwargs["agent_color"], kwargs["agent_shape"])
    if config_file["barrier_type"] in ["pit", "pit-with-bridge"]:
        pit_obj = Pit(config_file)
        pit_ids = pit_obj.create_pit(tdw_object, scene_config, scene_3_4=True)
        obj_list.extend(pit_ids)
    if "barrier_with_door" in config_file.values() or "cube" in config_file.values():
        # Create barrier
        if config_file["barrier_type"] in ["cube", "barrier_with_door"]:
            enable_barrier_1 = True
            enable_barrier_2 = True
            barrier_type_1 = config_file["barrier_type"]
            barrier_type_2 = config_file["barrier_type"]
        else:
            enable_barrier_1 = False
            enable_barrier_2 = False
        if "barrier_type_1" in config_file:
            if config_file["barrier_type_1"] in ["cube", "barrier_with_door"]:
                enable_barrier_1 = True
                barrier_type_1 = config_file["barrier_type_1"]
        if "barrier_type_2" in config_file:
            if config_file["barrier_type_2"] in ["cube", "barrier_with_door"]:
                enable_barrier_2 = True
                barrier_type_2 = config_file["barrier_type_2"]
        if enable_barrier_1:
            obstacle_1_position = {
                "x": scene_config.positions_x[config_file["obstacle_1_pos_x"]],
                "y": scene_config.positions_y[config_file["obstacle_1_height"]],
                "z": scene_config.obstacle_z[config_file["obstacle_1_pos_z"]]
            }
            obstacle_1_height = 0 if config_file["obstacle_1_height"] == 0 else scene_config.obstacle_height[
                config_file["obstacle_1_height"] - 1]
            obstacle_1_width = scene_config.obstacle_width[config_file["obstacle_1_width"]]
            obstacle_1_depth = scene_config.obstacle_depth[config_file["obstacle_1_depth"]]
            selected_barrier_obj = BarrierWithDoor if barrier_type_1 == "barrier_with_door" else Obstacle
            obstacle_1 = selected_barrier_obj(
                position=obstacle_1_position, height=obstacle_1_height,
                width=obstacle_1_width, depth=obstacle_1_depth, tdw_object=tdw_object,
                door_depth=0.7, config_file=config_file
            )
            if obstacle_1_height != 0:
                obstacle_1.create_obstacle(kwargs["actually_create"])
                if barrier_type_1 == "cube":
                    obj_list.extend([obstacle_1.obstacle_id])
                else:
                    obj_list.extend([obstacle_1.barrier_1, obstacle_1.barrier_2, obstacle_1.barrier_3])

        if enable_barrier_2:
            obstacle_2_position = {
                "x": scene_config.positions_x[config_file["obstacle_2_pos_x"]],
                "y": scene_config.positions_y[config_file["obstacle_2_height"]],
                "z": scene_config.obstacle_z[config_file["obstacle_2_pos_z"]]
            }
            obstacle_2_height = 0 if config_file["obstacle_2_height"] == 0 else scene_config.obstacle_height[
                config_file["obstacle_2_height"] - 1]
            obstacle_2_width = scene_config.obstacle_width[config_file["obstacle_2_width"]]
            obstacle_2_depth = scene_config.obstacle_depth[config_file["obstacle_2_depth"]]
            selected_barrier_obj = BarrierWithDoor if barrier_type_2 == "barrier_with_door" else Obstacle
            obstacle_2 = selected_barrier_obj(
                position=obstacle_2_position, height=obstacle_2_height,
                width=obstacle_2_width, depth=obstacle_2_depth, tdw_object=tdw_object,
                door_depth=0.7, config_file=config_file
            )
            if obstacle_2_height != 0:
                obstacle_2.create_obstacle(kwargs["actually_create"])
                if barrier_type_2 == "cube":
                    obj_list.extend([obstacle_2.obstacle_id])
                else:
                    obj_list.extend([obstacle_2.barrier_1, obstacle_2.barrier_2, obstacle_2.barrier_3])

    if "ramp" in config_file.values() or "platform" in config_file.values():
        if config_file["barrier_type"] == "platform":
            config_file["ramp_rotation_1"] = scene_config.ramp_rotation[3]
            config_file["ramp_rotation_2"] = scene_config.ramp_rotation[3]
        else:
            config_file["ramp_rotation_1"] = scene_config.ramp_rotation[0]
            config_file["ramp_rotation_2"] = scene_config.ramp_rotation[2]
        if config_file["ramp_height_1"] != -1:
            ramp_position_1 = scene_config.ramp_position[0].copy()
            ramp_1 = utils.create_slope_l(tdw_object,
                                          {"x": ramp_position_1["x"], "y": 0, "z": ramp_position_1["z"]},
                                          height=scene_config.ramp_height[config_file["ramp_height_1"]],
                                          rotation=config_file["ramp_rotation_1"],
                                          platform_only=config_file["barrier_type"] == "platform"
                                          )
            target_1_position = ramp_1.target_position
            obj_list.extend([ramp_1.ramp_base_id])
            if config_file["barrier_type"] == "ramp":
                obj_list.extend([ramp_1.ramp_slope_id])
        else:
            target_1_position = scene_config.ramp_position[0].copy()
            target_1_position["y"] = scene_config.positions_y[0]
        target_1_obj = utils.create_target(tdw_object, position=target_1_position,
                                           rotation={"x": 0, "y": 0, "z": 0}, color=target_1_color,
                                           object_type=target_1_shape)
        target_1_id = target_1_obj.target_id
        if config_file["ramp_height_2"] != -1:
            ramp_position_2 = scene_config.ramp_position[1].copy()
            ramp_2 = utils.create_slope_l(tdw_object,
                                          {"x": ramp_position_2["x"], "y": 0, "z": ramp_position_2["z"]},
                                          height=scene_config.ramp_height[config_file["ramp_height_2"]],
                                          rotation=config_file["ramp_rotation_2"],
                                          platform_only=config_file["barrier_type"] == "platform")
            target_2_position = ramp_2.target_position
            obj_list.extend([ramp_2.ramp_base_id])
            if config_file["barrier_type"] == "ramp":
                obj_list.extend([ramp_2.ramp_slope_id])
        else:
            target_2_position = scene_config.ramp_position[1].copy()
            target_2_position["y"] = scene_config.positions_y[0]

        target_2_obj = utils.create_target(tdw_object, position=target_2_position,
                                           rotation={"x": 0, "y": 0, "z": 0}, color=target_2_color,
                                           object_type=target_2_shape)
        target_2_id = target_2_obj.target_id
    if "obj_1_pos_x" in config_file:
        if target_1_id is None:
            if "pit" in config_file.values() or "pit-with-bridge" in config_file.values():
                target_1_position = {
                    "x": scene_config.positions_x[config_file["obj_1_pos_x"]],
                    "y": 1.016 + pit_depth,
                    "z": scene_config.positions_z[config_file["obj_1_pos_z"]]
                }
            else:
                target_1_position = {
                    "x": scene_config.positions_x[config_file["obj_1_pos_x"]] if config_file["obstacle_1_height"] != 0 else
                    scene_config.positions_x_without_barrier[config_file["obj_1_pos_x"]],
                    "y": scene_config.positions_y[0],
                    "z": scene_config.positions_z[config_file["obj_1_pos_z"]]
                }
            target_1_obj = utils.create_target(tdw_object, position=target_1_position,
                                               rotation={"x": 0, "y": 0, "z": 0}, color=target_1_color,
                                               object_type=target_1_shape)
            target_1_id = target_1_obj.target_id
    if "obj_2_pos_x" in config_file:
        if target_2_id is None:
            if "pit" in config_file.values() or "pit-with-bridge" in config_file.values():
                target_2_position = {
                    "x": scene_config.positions_x[config_file["obj_2_pos_x"]],
                    "y": 1.016 + pit_depth,
                    "z": scene_config.positions_z[config_file["obj_2_pos_z"]]
                }
            else:
                if config_file["obstacle_2_height"] != 0 and scene_config.positions_x[config_file["obj_2_pos_x"]] == 6:
                    scene_config.positions_x[config_file["obj_2_pos_x"]] = 4
                target_2_position = {
                    "x": scene_config.positions_x[config_file["obj_2_pos_x"]] if config_file["obstacle_2_height"] != 0 else
                    scene_config.positions_x_without_barrier[config_file["obj_2_pos_x"]],
                    "y": scene_config.positions_y[0],
                    "z": scene_config.positions_z[config_file["obj_2_pos_z"]]
                }
            target_2_obj = utils.create_target(tdw_object, position=target_2_position,
                                               rotation={"x": 0, "y": 0, "z": 0}, color=target_2_color,
                                               object_type=target_2_shape)
            target_2_id = target_2_obj.target_id
    obj_list.extend([agent.agent_id, target_1_id, target_2_id])
    tdw_object.communicate({"$type": "send_segmentation_colors", "ids": obj_list, "frequency": "always"})
    resp = tdw_object.communicate(
        [{"$type": "send_segmentation_colors", "ids": obj_list, "frequency": "always"},
        {"$type": "send_bounds", "ids": obj_list, "frequency": "always"},
        {"$type": "send_transforms", "ids": obj_list, "frequency": "always"},
        {"$type": "send_rigidbodies", "ids": obj_list, "frequency": "always"},
        {"$type": "send_id_pass_segmentation_colors", "ids": ["agent_follow_camera"], "frequency": "always"}
         ]
    )

    if "enable_image" in kwargs:
        if kwargs["enable_image"]:
            utils.enable_images(tdw_object, single_camera=True)
    return_state = {
        "obstacle_1": obstacle_1,
        "obstacle_2": obstacle_2,
        "ramp_1": ramp_1,
        "ramp_2": ramp_2,
        "agent": agent,
        "target_1_position": target_1_position,
        "target_2_position": target_2_position,
        "target_1_id": target_1_id,
        "target_2_id": target_2_id,
        "target_1_obj": target_1_obj,
        "target_2_obj": target_2_obj,
        "high_scene": high_scene,
        "pit_obj": pit_obj,
        "pit_ids": pit_ids
    }
    return return_state