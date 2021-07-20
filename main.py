from tdw.controller import Controller
from util import utils
import os
import json
import tqdm
from util.onegoalscene import OneGoalScene
from util.twogoalscene import TwoGoalScene
from util.replay_scene import ReplayScene
import requests
import argparse
import random

v = -0.03
h = 0.09


class AGENTController(Controller):
    def run(self, args):
        self.start()
        # Create an empty room.
        if args.scene_type == "scene_1":
            camera_obj = utils.create_base_scene(self, args, single_camera=True)
            self.run_single_goal_scenario(camera_obj, args)
        elif args.scene_type == "scene_3_4":
            camera_obj = utils.create_base_scene(self, args, single_camera=True, scene_3_camera=True)
            self.run_two_goal_scenario(camera_obj, args)
        elif args.scene_type == "replay_scene":
            camera_obj = utils.create_base_scene(self, args, single_camera=True, scene_3_camera=True
            if args.replay_scene_type == "scene_3" else False)
            self.run_play_back(camera_obj, args)
        elif args.scene_type == "color_sampler":
            camera_obj = utils.create_base_scene(self, args, single_camera=True, scene_3_camera=True)
            utils.create_color_samples(self)
        self.communicate({"$type": "terminate"})
        # Procedural

    def run_play_back(self, camera_obj, args):
        replay_scene = ReplayScene(self, output_dir="replay_data/config_20", camera_obj=camera_obj, config_path="data/config_20", args=args)
        if args.replay_scene_type == "scene_1":
            replay_scene.scenario_2_action_efficiency(args)
        elif args.replay_scene_type == "scene_2":
            replay_scene.scenario_3_unobserved_constraints(args)
        elif args.replay_scene_type == "scene_3":
            replay_scene.scenario_1_goal_preferences(args)
        else:
            replay_scene.scenario_4_cost_reward_trade_offs(args)

    def run_single_goal_scenario(self, camera_obj, args):
        scene_1 = OneGoalScene(self, camera_obj, args)
        data = [
            # {
            #     "barrier_type": "pit-with-bridge",
            #     "id": 0,
            #     "agent_shape": 0,
            #     "obj_shape": 0,
            #     "agent_pos_x": 0,
            #     "agent_pos_z": 0,
            #     "obj_pos_x": 2,
            #     "obj_pos_z": 2,
            #     "pit_width": 1,
            #     "pit_depth": -1,
            #     "bridge_z": 1,
            #     "obstacle_pos_x": 1,
            #     "obstacle_pos_z": 1,
            # },
        # {
        #         "barrier_type": "barrier_with_door",
        #         "id": 3,
        #         "agent_shape": 2,
        #         "obj_shape": 2,
        #         "agent_pos_x": 0,
        #         "agent_pos_z": 1,
        #         "obj_pos_x": 2,
        #         "obj_pos_z": 1,
        #         "obstacle_pos_x": 1,
        #         "obstacle_pos_z": 1,
        #         "obstacle_height": 6,
        #         "obstacle_width": 0,
        #         "obstacle_depth": 5,
        #     },
        #     {
        #         "barrier_type": "barrier_with_door",
        #         "id": 4,
        #         "agent_shape": 2,
        #         "obj_shape": 0,
        #         "agent_pos_x": 0,
        #         "agent_pos_z": 1,
        #         "obj_pos_x": 2,
        #         "obj_pos_z": 1,
        #         "obstacle_pos_x": 1,
        #         "obstacle_pos_z": 1,
        #         "obstacle_height": 6,
        #         "obstacle_width": 0,
        #         "obstacle_depth": 5,
        #     },
        #     {
        #         "barrier_type": "platform-cube",
        #         "id": 6,
        #         "agent_shape": 2,
        #         "obj_shape": 0,
        #         "agent_pos_x": 0,
        #         "agent_pos_z": 2,
        #         "obj_pos_x": 2,
        #         "obj_pos_z": 0,
        #         "obstacle_pos_x": 1,
        #         "obstacle_pos_z": 0,
        #         "obstacle_height": 0
        #     },
            {
                "barrier_type": "cube",
                "id": 7,
                "agent_shape": 2,
                "obj_shape": 0,
                "agent_pos_x": 2,
                "agent_pos_z": 2,
                "obj_pos_x": 0,
                "obj_pos_z": 2,
                "obstacle_pos_x": 1,
                "obstacle_pos_z": 2,
                "obstacle_height": 6,
                "obstacle_width": 0,
                "obstacle_depth": 4,
            },
            # {
            #     "barrier_type": "cube",
            #     "id": 8,
            #     "agent_shape": 2,
            #     "obj_shape": 0,
            #     "agent_pos_x": 0,
            #     "agent_pos_z": 0,
            #     "obj_pos_x": 2,
            #     "obj_pos_z": 2,
            #     "obstacle_pos_x": 1,
            #     "obstacle_pos_z": 2,
            #     "obstacle_height": 4,
            #     "obstacle_width": 0,
            #     "obstacle_depth": 2,
            # },
            # {
            #     "barrier_type": "platform",
            #     "id": 19,
            #     "agent_shape": 0,
            #     "agent_pos_x": 0,
            #     "agent_pos_z": 2,
            #     "obj_shape": 0,
            #     "obj_pos_ramp_x": 2,
            #     "obj_pos_ramp_z": 2,
            #     "ramp_height": 1,
            # },
            # {
            #     "barrier_type": "platform",
            #     "id": 20,
            #     "agent_shape": 0,
            #     "agent_pos_x": 2,
            #     "agent_pos_z": 2,
            #     "obj_shape": 0,
            #     "obj_pos_ramp_x": 0,
            #     "obj_pos_ramp_z": 2,
            #     "ramp_height": 1,
            # },
            # {
            #     "barrier_type": "platform",
            #     "id": 21,
            #     "agent_shape": 0,
            #     "agent_pos_x": 0,
            #     "agent_pos_z": 2,
            #     "obj_shape": 0,
            #     "obj_pos_ramp_x": 2,
            #     "obj_pos_ramp_z": 2,
            #     "ramp_height": 2,
            # },
            # {
            #     "barrier_type": "ramp",
            #     "id": 22,
            #     "agent_shape": 0,
            #     "agent_pos_x": 0,
            #     "agent_pos_z": 0,
            #     "obj_shape": 0,
            #     "obj_pos_ramp": 1,
            #     "ramp_height": 1,
            #     "ramp_rotation": 2
            # },
            # {
            #     "barrier_type": "ramp",
            #     "id": 21,
            #     "agent_shape": 0,
            #     "agent_pos_x": 2,
            #     "agent_pos_z": 1,
            #     "obj_shape": 0,
            #     "obj_pos_ramp": 0,
            #     "ramp_height": 1,
            #     "ramp_rotation": 0
            # },
        #     {
        #         "barrier_type": "cube",
        #         "id": 10,
        #         "agent_shape": 0,
        #         "obj_shape": 10,
        #         "agent_pos_x": 0,
        #         "agent_pos_z": 1,
        #         "obj_pos_x": 2,
        #         "obj_pos_z": 1,
        #         "obstacle_pos_x": 1,
        #         "obstacle_pos_z": 1,
        #         "obstacle_height": 5,
        #         "obstacle_width": 0,
        #         "obstacle_depth": 3,
        #     },

            # {
            #     "barrier_type": "ramp",
            #     "id": 21,
            #     "agent_shape": 1,
            #     "obj_shape": 0,
            #     "agent_pos_x": 0,
            #     "agent_pos_z": 1,
            #     "obstacle_pos_x": 1,
            #     "obstacle_pos_z": 1,
            #     "ramp_height": 1,
            #     "ramp_rotation": 0,
            #     "obj_pos_ramp": 1,
            # },
        # #     {
        # #         "barrier_type": "ramp",
        # #         "id": 21,
        # #         "agent_shape": 1,
        # #         "obj_shape": 0,
        # #         "agent_pos_x": 0,
        # #         "agent_pos_z": 1,
        # #         "obstacle_pos_x": 1,
        # #         "obstacle_pos_z": 1,
        # #         "ramp_height": 0,
        # #         "ramp_rotation": 1,
        # #         "obj_pos_ramp": 1,
        # #     },
        # # #     # {
        # # #     #     "barrier_type": "ramp",
        # # #     #     "id": 22,
        # # #     #     "agent_shape": 1,
        # # #     #     "obj_shape": 0,
        # # #     #     "agent_pos_x": 0,
        # # #     #     "agent_pos_z": 1,
        # # #     #     "obstacle_pos_x": 1,
        # # #     #     "obstacle_pos_z": 1,
        # # #     #     "ramp_height": 0,
        # # #     #     "ramp_rotation": 2,
        # # #     #     "obj_pos_ramp": 1,
        # # #     #     "obstacle_height": 0,
        # # #     #     "obstacle_width": 0,
        # # #     #     "obstacle_depth": 2,
        # # #     #     "approach": "jump_ramp_1"
        # # #     # },
        #     {
        #         "barrier_type": "ramp",
        #         "id": 23,
        #         "agent_shape": 1,
        #         "obj_shape": 0,
        #         "agent_pos_x": 0,
        #         "agent_pos_z": 1,
        #         "obstacle_pos_x": 1,
        #         "obstacle_pos_z": 1,
        #         "ramp_height": 2,
        #         "ramp_rotation": 2,
        #         "obj_pos_ramp": 1,
        #     },
        #     {
        #         "barrier_type": "ramp",
        #         "id": 26,
        #         "agent_shape": 1,
        #         "obj_shape": 0,
        #         "agent_pos_x": 0,
        #         "agent_pos_z": 1,
        #         "obstacle_pos_x": 1,
        #         "obstacle_pos_z": 1,
        #         "ramp_height": 1,
        #         "ramp_rotation": 0,
        #         "obj_pos_ramp": 1,
        #     }
        # # #
        # # #     # {
        # # #     #     "barrier_type": "cube",
        # # #     #     "id": 13,
        # # #     #     "agent_shape": 0,
        # # #     #     "obj_shape": 0,
        # # #     #     "agent_pos_x": 0,
        # # #     #     "agent_pos_z": 1,
        # # #     #     "obj_pos_x": 3,
        # # #     #     "obj_pos_z": 0,
        # # #     #     "obstacle_pos_x": 1,
        # # #     #     "obstacle_pos_z": 0,
        # # #     #     "obstacle_height": 3,
        # # #     #     "obstacle_width": 0,
        # # #     #     "obstacle_depth": 2,
        # # #     #     "jump_height": 0,
        # # #     #     "go_around": "right"
        # # #     # },
        # # #     # {
        # # #     #     "barrier_type": "cube",
        # # #     #     "id": 14,
        # # #     #     "agent_shape": 0,
        # # #     #     "obj_shape": 0,
        # # #     #     "agent_pos_x": 0,
        # # #     #     "agent_pos_z": 1,
        # # #     #     "obj_pos_x": 3,
        # # #     #     "obj_pos_z": 0,
        # # #     #     "obstacle_pos_x": 1,
        # # #     #     "obstacle_pos_z": 0,
        # # #     #     "obstacle_height": 3,
        # # #     #     "obstacle_width": 0,
        # # #     #     "obstacle_depth": 2,
        # # #     #     "jump_height": 3,
        # # #     # },
        # # #     # {
        # # #     #     "barrier_type": "cube",
        # # #     #     "id": 15,
        # # #     #     "agent_shape": 0,
        # # #     #     "obj_shape": 0,
        # # #     #     "agent_pos_x": 0,
        # # #     #     "agent_pos_z": 1,
        # # #     #     "obj_pos_x": 3,
        # # #     #     "obj_pos_z": 0,
        # # #     #     "obstacle_pos_x": 1,
        # # #     #     "obstacle_pos_z": 0,
        # # #     #     "obstacle_height": 3,
        # # #     #     "obstacle_width": 0,
        # # #     #     "obstacle_depth": 2,
        # # #     #     "jump_height": 4,
        # # #     # },
        # # #     # {
        # # #     #     "barrier_type": "cube",
        # # #     #     "id": 16,
        # # #     #     "agent_shape": 0,
        # # #     #     "obj_shape": 0,
        # # #     #     "agent_pos_x": 0,
        # # #     #     "agent_pos_z": 1,
        # # #     #     "obj_pos_x": 3,
        # # #     #     "obj_pos_z": 0,
        # # #     #     "obstacle_pos_x": 1,
        # # #     #     "obstacle_pos_z": 0,
        # # #     #     "obstacle_height": 3,
        # # #     #     "obstacle_width": 0,
        # # #     #     "obstacle_depth": 2,
        # # #     #     "jump_height": 5,
        # # #     # },
        # # #
        #     {
        #         "barrier_type": "pit",
        #         "id": 0,
        #         "agent_shape": 0,
        #         "obj_shape": 0,
        #         "agent_pos_x": 0,
        #         "agent_pos_z": 1,
        #         "obj_pos_x": 2,
        #         "obj_pos_z": 0,
        #         "pit_width": 0,
        #         "pit_depth": -1,
        #         "obstacle_pos_x": 1,
        #         "obstacle_pos_z": 1,
        #     },
        #     {
        #         "barrier_type": "pit-with-bridge",
        #         "id": 1,
        #         "agent_shape": 0,
        #         "obj_shape": 0,
        #         "agent_pos_x": 0,
        #         "agent_pos_z": 1,
        #         "obj_pos_x": 2,
        #         "obj_pos_z": 1,
        #         "pit_width": 1,
        #         "bridge_z": 1,
        #         "pit_depth": -1,
        #         "obstacle_pos_x": 1,
        #         "obstacle_pos_z": 1
        #     },
        # #     # {
        # #     #     "barrier_type": "pit",
        # #     #     "id": 18,
        # #     #     "agent_shape": 0,
        # #     #     "obj_shape": 0,
        # #     #     "agent_pos_x": 0,
        # #     #     "agent_pos_z": 1,
        # #     #     "obj_pos_x": 3,
        # #     #     "obj_pos_z": 1,
        # #     #     "pit_width": 0,
        # #     #     "jump_width": 1,
        # #     # },
        # # #     # {
        # # #     #     "barrier_type": "pit",
        # # #     #     "id": 19,
        # # #     #     "agent_shape": 0,
        # # #     #     "obj_shape": 0,
        # # #     #     "agent_pos_x": 0,
        # # #     #     "agent_pos_z": 1,
        # # #     #     "obj_pos_x": 3,
        # # #     #     "obj_pos_z": 1,
        # # #     #     "pit_width": 0,
        # # #     #     "jump_width": 2,
        # # #     # },
        # # #
        # # #
        # # #
        ]
        # width -> code
        # 6 -> 0
        # 5.78 -> 1
        # 5.5 -> 2
        # 5.25 -> 3
        # 5 -> 4
        # pos_z -> code
        # -2.795 -> 0
        # -2.4 -> 1
        # -1.917 -> 2
        #
        # Pos_x -> code
        # -1.32 -> 2
        # 1.08 -> 0
        # with open(args.config_file, "r") as fp:
        #     data = json.load(fp)

        for i in tqdm.tqdm(range(args.config_start, args.config_end, 1)):
            e = data[i]
            e["id"] += 1
            file_id = e["id"]
            e["dir_name"] = os.path.join(args.out_dir, f"config_{file_id}")
            scene_1.execute_config(config_file=e, output_dir=args.out_dir)

    def run_two_goal_scenario(self, camera_obj, args):
        scene_3_4 = TwoGoalScene(self, camera_obj, args)
        data = [
            {
                "barrier_type": "ramp",
                "id": 1,
                "agent_shape": 0,
                "obj_shape": 0,
                "agent_pos_z": 0,
                "ramp_height_1": 0,
                "ramp_rotation_1": 0,
                "ramp_height_2": 1,
                "ramp_rotation_2": 2
            }
        #     {
        #         "barrier_type": "pit-with-bridge",
        #         "id": 0,
        #         "agent_shape": 0,
        #         "obj_shape": 0,
        #         "agent_pos_x": 0,
        #         "agent_pos_z": 1,
        #         "obj_1_pos_x": 0,
        #         "obj_1_pos_z": 1,
        #         "obj_shape_1": 1,
        #         "obj_shape_2": 1,
        #         "obj_2_pos_x": 4,
        #         "obj_2_pos_z": 1,
        #         "pit_width_1": 2,
        #         "pit_depth_1": 2,
        #         "pit_width_2": 0,
        #         "pit_depth_2": 2,
        #         "bridge_1_z": 1,
        #         "bridge_2_z": 1,
        #         "obstacle_1_pos_x": 1,
        #         "obstacle_1_pos_z": 1,
        #         "obstacle_2_pos_x": 3,
        #         "obstacle_2_pos_z": 1,
        #     },
            # {
            #         "barrier_type": "pit",
            #         "id": 0,
            #         "agent_shape": 0,
            #         "obj_shape": 0,
            #         "agent_pos_x": 0,
            #         "agent_pos_z": 2,
            #         "obj_1_pos_x": 0,
            #         "obj_1_pos_z": 1,
            #         "obj_2_pos_x": 4,
            #         "obj_2_pos_z": 1,
            #         "pit_width_1": 0,
            #         "pit_depth_1": 2,
            #         "pit_width_2": -1,
            #         "pit_depth_2": 2,
            #         "obstacle_1_pos_x": 1,
            #         "obstacle_1_pos_z": 1,
            #         "obstacle_2_pos_x": 3,
            #         "obstacle_2_pos_z": 1,
            #     },
            # {
            #     "barrier_type": "platform",
            #     "id": 1,
            #     "agent_shape": 0,
            #     "obj_shape_1": 1,
            #     "obj_shape_2": 3,
            #     "obj_shape": 0,
            #     "agent_pos_z": 1,
            #     "ramp_height_1": 1,
            #     "ramp_rotation_1": 2,
            #     "ramp_height_2": 1,
            #     "ramp_rotation_2": 0
            # }
        #     {
        #         "barrier_type": "platform",
        #         "id": 0,
        #         "agent_shape": 0,
        #         "obj_shape": 0,
        #         "agent_pos_z": 1,
        #         "obj_pos_ramp_x_1": 0,
        #         "obj_pos_ramp_z_1": 2,
        #         "obj_pos_ramp_x_2": 0,
        #         "obj_pos_ramp_z_2": 2,
        #         "ramp_height_1": -1,
        #         "ramp_height_2": 1,
        #     }
        #     {
        #         "barrier_type": "platform",
        #         "barrier_type_1": "barrier_with_door",
        #         "id": 1,
        #         "agent_shape": 0,
        #         "obj_shape": 0,
        #         "agent_pos_z": 1,
        #         "ramp_height_1": -1,
        #         "ramp_rotation_1": 0,
        #         "ramp_height_2": 1,
        #         "ramp_rotation_2": 3,
        #         "obstacle_1_pos_x": 1,
        #         "obstacle_1_pos_z": 1,
        #         "obstacle_1_height": 6,
        #         "obstacle_1_width": 0,
        #         "obstacle_1_depth": 3,
        #         # "obj_2_pos_x": 4,
        #         # "obj_2_pos_z": 1,
        #     },
        #     {
        #         "id": 2,
        #         "barrier_type": "cube",
        #         "agent_shape": 0,
        #         "obj_shape_1": 1,
        #         "obj_shape_2": 1,
        #         "agent_pos_z": 1,
        #
        #         "obj_1_pos_x": 0,
        #         "obj_1_pos_z": 0,
        #         "obj_2_pos_x": 4,
        #         "obj_2_pos_z": 0,
        #
        #         "obstacle_1_pos_x": 1,
        #         "obstacle_1_pos_z": 1,
        #         "obstacle_1_height": 1,
        #         "obstacle_1_width": 0,
        #         "obstacle_1_depth": 3,
        #
        #         "obstacle_2_pos_x": 3,
        #         "obstacle_2_pos_z": 1,
        #         "obstacle_2_height": 1,
        #         "obstacle_2_width": 0,
        #         "obstacle_2_depth": 3,
        #     },
        #     {
        #         "id": 3,
        #         "barrier_type": "barrier_with_door",
        #         "agent_shape": 0,
        #         "obj_shape": 0,
        #         "agent_pos_z": 2,
        #
        #         "obj_1_pos_x": 0,
        #         "obj_1_pos_z": 2,
        #         "obj_2_pos_x": 4,
        #         "obj_2_pos_z": 2,
        #
        #         "obstacle_1_pos_x": 1,
        #         "obstacle_1_pos_z": 2,
        #         "obstacle_1_height": 6,
        #         "obstacle_1_width": 0,
        #         "obstacle_1_depth": 3,
        #
        #         "obstacle_2_pos_x": 3,
        #         "obstacle_2_pos_z": 2,
        #         "obstacle_2_height": 0,
        #         "obstacle_2_width": 0,
        #         "obstacle_2_depth": 3,
        #     }
        #     {
        #         "id": 133,
        #         "barrier_type": "cube",
        #         "agent_shape": 0,
        #         "obj_shape": 0,
        #         "agent_pos_z": 1,
        #
        #         "obj_1_pos_x": 0,
        #         "obj_1_pos_z": 0,
        #         "obj_2_pos_x": 4,
        #         "obj_2_pos_z": 0,
        #
        #         "obstacle_1_pos_x": 1,
        #         "obstacle_1_pos_z": 2,
        #         "obstacle_1_height": 6,
        #         "obstacle_1_width": 3,
        #         "obstacle_1_depth": 4,
        #
        #         "obstacle_2_pos_x": 3,
        #         "obstacle_2_pos_z": 2,
        #         "obstacle_2_height": 6,
        #         "obstacle_2_width": 3,
        #         "obstacle_2_depth": 4,
        #
        #     }
        #     {
        #         "id": 14,
        #         "barrier_type": "cube",
        #         "agent_shape": 0,
        #         "obj_shape": 0,
        #         "agent_pos_z": 2,
        #
        #         "obj_1_pos_x": 0,
        #         "obj_1_pos_z": 1,
        #         "obj_2_pos_x": 4,
        #         "obj_2_pos_z": 1,
        #
        #         "obstacle_1_pos_x": 1,
        #         "obstacle_1_pos_z": 2,
        #         "obstacle_1_height": 5,
        #         "obstacle_1_width": 3,
        #         "obstacle_1_depth": 4,
        #
        #         "obstacle_2_pos_x": 3,
        #         "obstacle_2_pos_z": 2,
        #         "obstacle_2_height": 3,
        #         "obstacle_2_width": 1,
        #         "obstacle_2_depth": 4,
        #
        #     }
        ]
        # with open(args.config_file, "r") as fp:
        #     data = json.load(fp)
        for i in tqdm.tqdm(range(args.config_start, args.config_end, 1)):
            e = data[i]
            file_id = e["id"]
            e["dir_name"] = os.path. join(args.out_dir, f"config_{file_id}")
            scene_3_4.execute_config(config_file=e, output_dir=args.out_dir)


def create_tdw(port):
    url = "http://localhost:5000/get_tdw"
    data = {
        'ip_address': "localhost",
        'port': port
    }
    response = requests.post(url, json=json.dumps(data))
    print(response.status_code, response.reason)
    docker_id = response.json()['docker_id']
    return docker_id


def kill_tdw(docker_id):
    url = "http://localhost:5000/kill_tdw"
    data = {
        "container_id": docker_id
    }
    response = requests.post(url, json=json.dumps(data))
    print(response.status_code, response.reason)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='ProcGen')
    parser.add_argument(
        '--out-dir',
        default="data",
        help='Output directory')
    parser.add_argument(
        '--config-file',
        default="configuration.json",
        help='Configuration file for scene generation')
    parser.add_argument(
        '--config-start',
        default=0,
        type=int,
        help='Configuration file for scene generation')
    parser.add_argument(
        '--config-end',
        default=1,
        type=int,
        help='Configuration file for scene generation')
    parser.add_argument(
        '--port',
        default=1071,
        type=int,
        help='Configuration file for scene generation')
    parser.add_argument(
        '--set-num',
        default=1,
        type=int,
        help='Number of sets')
    parser.add_argument(
        '--screen-scale',
        default=80,
        type=int,
        help='Size of display')
    parser.add_argument(
        '--random-seed',
        default="saf203jdnflk",
        type=str,
        help='Random seed')
    parser.add_argument(
        '--input-dir',
        default="data",
        help='Input directory path for replay agent')
    parser.add_argument(
        '--scene-type',
        default="scene_1",
        help='Input directory path for replay agent')
    parser.add_argument(
        '--replay-scene-type',
        default="scene_1",
        help='Replay scene type')
    parser.add_argument(
        '--test-type',
        default="Type_1_0",
        help='Replay scene type')
    parser.add_argument(
        '--remote',
        action='store_true',
        default=False,
        help='Input directory path for replay agent')
    parser.add_argument(
        '--generate-video',
        action='store_true',
        default=False,
        help='Should video be generated?')
    parser.add_argument(
        '--use-novel-objects',
        action='store_true',
        default=False,
        help='Should novel objects be used ?')
    parser.add_argument(
        '--enable-image',
        action='store_true',
        default=False,
        help='Should novel objects be used ?')
    parser.add_argument(
        '--clear-images',
        action='store_true',
        default=False,
        help='Should novel objects be used ?')
    parser.add_argument(
        '--tmp',
        action='store_true',
        default=False,
        help='Tmp ?')
    parser.add_argument(
        '--reconstruct-3d',
        action='store_true',
        default=False,
        help='Reconstruct trajectory from data')
    parser.add_argument(
        '--follow-camera',
        action='store_true',
        default=False,
        help='Enable first person perspective')
    parser.add_argument(
        '--version',
        default="v2",
        help='Replay scene type')
    args = parser.parse_args()
    random.seed(args.random_seed)
    docker_id = None
    if args.scene_type == "replay_scene":
        args.config_end = args.config_start + args.set_num
    config_start = args.config_start
    config_end = args.config_end
    started = False
    for start in range(config_start, config_end, 50):
        args.config_end = start + 50 if start + 50 <= config_end else config_end
        args.config_start = start
        args.set_num = args.config_end - args.config_start
        if args.remote:
            AGENTController(port=args.port, launch_build=False).run(args)
        else:
            if not started:
                started = True
            AGENTController(port=args.port, launch_build=True).run(args)