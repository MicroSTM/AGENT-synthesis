from util import physics_agent
import random
from util import utils
import shutil
import os
from util.scene_configuration import SceneConfiguration
import numpy as np
import json
import time
import traceback
from util import trajectory_generation
from util import create_scene


class TwoGoalScene:
    def __init__(self, tdw_object, camera_obj, args):
        self.tdw_object = tdw_object
        self.args = args
        self.camera_obj = camera_obj
        self.scene_config = SceneConfiguration()
        self.scene_offset = self.scene_config.scene_offset
        self.agent_shape = "cone"
        self.agent_color = random.sample(self.scene_config.agent_colors, 1)[0]
        self.target_1_color, self.target_2_color = random.sample(self.scene_config.target_colors, 2)
        self.target_1_color = {"r": 48 / 255, "g": 71 / 255, "b": 94 / 255, "a": 1.0}
        self.target_2_color = {"r": 216 / 255, "g": 52 / 255, "b": 95 / 255, "a": 1.0}
        self.agent_color = {"r": 7 / 255, "g": 121 / 255, "b": 228 / 255, "a": 1.0}
        self.high_scene = False
        self.pit_obj, self.pit_ids = None, []

    def go_to_goal(self):
        # Check if obstacle is between goal and agent
        h_offset = 0.15
        offset = 0.147
        paths = []
        # Cross barrier
        if self.config_file["barrier_type"] in ["pit", "pit-with-bridge"]:
            return trajectory_generation.cross_pit_scene_3_4(self.agent, self.config_file,
                                                      [self.target_1_position, self.target_2_position], self.pit_obj)
            # if self.config_file["agent_pos_x"] in [0, 1]:
            #     jump_point_x = self.scene_config.pit_positions[0][0]["x"] - self.scene_config.pit_width[
            #         self.config_file["pit_width"]] / 2 + 0.1
            # else:
            #     jump_point_x = self.scene_config.pit_positions[0][1]["x"] + self.scene_config.pit_width[
            #         self.config_file["pit_width"]] / 2 - 0.1
            # if self.config_file["obj_pos_z"] > self.config_file["agent_pos_z"] or \
            #         self.config_file["obj_pos_z"] < self.config_file["agent_pos_z"]:
            #     jump_point_z = self.scene_config.positions_z[1]
            # else:
            #     jump_point_z = self.scene_config.positions_z[self.config_file["agent_pos_z"]]
            #
            # self.agent.approach(till_x=jump_point_x, till_z=jump_point_z)
            # self.agent.jump(height=None, width=self.scene_config.pit_width[self.config_file["pit_width"]])

        elif self.config_file["barrier_type"] == "cube":
            paths.extend(self.cross_barrier())
            return paths
        elif self.config_file["barrier_type"] == "barrier_with_door":
            paths.extend(self.cross_barrier(with_door=True))
            return paths
        # # Go to goal object
        # if "obj_ramp_height" in self.config_file:
        #     if self.scene_config.ramp_height[self.config_file["obj_ramp_height"]] == 0.5:
        #         self.agent.approach(till_x=self.selected_target["x"],
        #                             till_z=self.selected_target["z"] + 1.26)
        #         self.agent.approach(till_z=self.selected_target["z"] + 0.18)
        #     if self.scene_config.ramp_height[self.config_file["obj_ramp_height"]] == 0.2:
        #         self.agent.approach(till_x=self.selected_target["x"],
        #                             till_z=self.selected_target["z"] + 1.32)
        #         self.agent.approach(till_z=self.selected_target["z"] + 0.18)
        # else:
        #     self.agent.approach(till_x=self.selected_target["x"],
        #                         till_z=self.selected_target["z"], approach_dist=0.2)
        elif self.config_file["barrier_type"] == "ramp":
            # Get path for each ramp
            for ramp_obj in [self.ramp_1, self.ramp_2]:
                restrict_paths = [1, 2, 3]
                # if self.agent.agent_start_position["x"] > ramp_obj.position["x"] and ramp_obj.rotation == 180:
                #     restrict_paths = [1, 2, 3]
                # elif self.agent.agent_start_position["x"] > ramp_obj.position["x"] and ramp_obj.rotation == 0:
                #     restrict_paths = [2, 3, "R"]
                # elif self.agent.agent_start_position["x"] < ramp_obj.position["x"] and ramp_obj.rotation == 0:
                #     restrict_paths = [1, 2, 3]
                # elif self.agent.agent_start_position["x"] < ramp_obj.position["x"] and ramp_obj.rotation == 180:
                #     restrict_paths = [2, 3, "R"]
                # elif self.agent.agent_start_position["x"] > ramp_obj.position["x"] and ramp_obj.rotation == 90:
                #     restrict_paths = [1, 3]
                # elif self.agent.agent_start_position["x"] > ramp_obj.position["x"] and ramp_obj.rotation == -90:
                #     restrict_paths = [1, 2]
                # elif self.agent.agent_start_position["x"] < ramp_obj.position["x"] and ramp_obj.rotation == 90:
                #     restrict_paths = [1, 2]
                # elif self.agent.agent_start_position["x"] < ramp_obj.position["x"] and ramp_obj.rotation == -90:
                #     restrict_paths = [1, 3]
                paths.extend(trajectory_generation.cross_ramp(ramp_obj, self.agent, self.config_file, restrict_paths=restrict_paths))

            return paths
        elif self.config_file["barrier_type"] == "platform":
            for ramp_obj, target_pos in zip([self.ramp_1, self.ramp_2], [self.target_1_position, self.target_2_position]):
                paths.extend(trajectory_generation.cross_platform(ramp_obj, self.agent, target_pos))
            return paths

    def cross_barrier(self, with_door=False):
        paths = []
        h_offset = 0.15
        offset = 0.147
        # Jump over barrier
        for obstacle, target in zip([self.obstacle_1, self.obstacle_2], [self.target_1_position, self.target_2_position]):

            if with_door:
                path = trajectory_generation.cross_barrier_with_door(obstacle, target, self.agent.agent_start_position)
            else:
                path = trajectory_generation.cross_barrier(obstacle, target, self.agent.agent_start_position,
                                                           self.scene_config, config_file=self.config_file,
                                                           inefficient=False)
            paths.extend(path)

        return paths

    def execute_config(self, config_file, output_dir):
        self.agent = physics_agent.Agent(self.tdw_object, 1, config_file["dir_name"])
        shapes = self.scene_config.target_objects["target_objects_1"] + self.scene_config.target_objects["target_objects_2"]
        create_scene_arguments = {
            "config_file": config_file,
            "tdw_object": self.tdw_object,
            "high_scene": self.high_scene,
            "camera_obj": self.camera_obj,
            "target_1_color": {"r": 88 / 255, "g": 141 / 255, "b": 168 / 255, "a": 1.0},
            "target_2_color": {"r": 148 / 255, "g": 252 / 255, "b": 19 / 255, "a": 1.0},
            "target_1_shape": "sphere",
            "target_2_shape": "sphere",
            "agent_color": self.agent_color,
            "agent_shape": self.agent_shape,
            "agent": self.agent,
            "enable_image": self.args.enable_image,
            "actually_create": True
        }
        self.config_file = config_file
        return_state = create_scene.create_based_config_2_goal(**create_scene_arguments)
        self.obstacle_1 = return_state["obstacle_1"]
        self.obstacle_2 = return_state["obstacle_2"]
        self.ramp_1 = return_state["ramp_1"]
        self.ramp_2 = return_state["ramp_2"]
        self.high_scene = return_state["high_scene"]
        self.target_1_position = return_state["target_1_position"]
        self.target_2_position = return_state["target_2_position"]
        self.target_1_id = return_state["target_1_id"]
        self.target_2_id = return_state["target_2_id"]
        self.pit_obj = return_state["pit_obj"]
        if self.pit_obj is not None:
            self.pit_ids = self.pit_obj.pit_ids
        try:
            utils.settle_objects(self.tdw_object, n=20)
            paths = self.go_to_goal()
            time_required = []
            for p in paths:
                start_time = time.time()
                self.agent.output_dir = os.path.join(self.agent.output_dir, "images")
                utils.settle_objects(self.tdw_object, n=10)
                self.execute_path(p)
                time_required.append(time.time() - start_time)
                # print(
                #     f"Took {time.time() - start_time} secs. Average time per trajectory {sum(time_required) / len(time_required)}")
                unique_str = config_file["dir_name"] + f"_path_no_{self.agent.path_no}"
                with open(os.path.join(output_dir, "time.txt"), "a") as fp:
                    fp.write(
                        f"{unique_str} took {time.time() - start_time} secs. Average time per trajectory {sum(time_required) / len(time_required)} \n")

                self.reset()
        except Exception as err:
            # with open("error.txt", "a") as fp:
            #     fp.write(f"Error in configuration {output_dir}\n")
            traceback.print_tb(err.__traceback__)
            print(err)

        commands = [{"$type": "destroy_object", "id": self.agent.agent_id},
                    {"$type": "destroy_object", "id": self.target_1_id},
                    {"$type": "destroy_object", "id": self.target_2_id}
                    ]
        if self.obstacle_1 is not None and self.obstacle_2 is not None:
            if config_file["barrier_type"] == "barrier_with_door":
                if self.obstacle_1.barrier_1 is not None:
                    commands.append({"$type": "destroy_object", "id": self.obstacle_1.barrier_1})
                    commands.append({"$type": "destroy_object", "id": self.obstacle_1.barrier_2})
                    commands.append({"$type": "destroy_object", "id": self.obstacle_1.barrier_3})
                if self.obstacle_2.barrier_1 is not None:
                    commands.append({"$type": "destroy_object", "id": self.obstacle_2.barrier_1})
                    commands.append({"$type": "destroy_object", "id": self.obstacle_2.barrier_2})
                    commands.append({"$type": "destroy_object", "id": self.obstacle_2.barrier_3})
            else:
                if self.obstacle_1.obstacle_id is not None:
                    commands.append({"$type": "destroy_object", "id": self.obstacle_1.obstacle_id})
                if self.obstacle_2.obstacle_id is not None:
                    commands.append({"$type": "destroy_object", "id": self.obstacle_2.obstacle_id})
        for pit_id in self.pit_ids:
            commands.append(
                {"$type": "destroy_object", "id": pit_id}
            )
        if self.ramp_1 is not None:
            if config_file["barrier_type"] == "ramp":
                commands.extend([
                    {"$type": "destroy_object", "id": self.ramp_1.ramp_slope_id},
                ])
            commands.extend([
                {"$type": "destroy_object", "id": self.ramp_1.ramp_base_id}
            ])
        if self.ramp_2 is not None:
            if config_file["barrier_type"] == "ramp":
                commands.extend([
                    {"$type": "destroy_object", "id": self.ramp_2.ramp_slope_id}

                ])
            commands.extend([
                {"$type": "destroy_object", "id": self.ramp_2.ramp_base_id}
            ])
        os.makedirs(self.config_file["dir_name"], exist_ok=True)
        with open(os.path.join(self.config_file["dir_name"], "scene_config.json"), "w") as fp:
            json.dump(self.config_file, fp)

        self.tdw_object.communicate(commands)
        self.ramp_1, self.ramp_2, self.obstacle_1, self.obstacle_2, self.pit_obj, self.pit_ids = None, None, None, None, None, []
        self.agent = None

    def reset(self):
        self.agent.reset()
        utils.teleport(self.tdw_object, self.target_1_position, self.target_1_id)
        utils.teleport(self.tdw_object, self.target_2_position, self.target_2_id)

    def execute_path(self, path):
        meta_data = None
        p1 = [e for e in path if e[0] == "goto"]
        ramp_obj = None

        if p1:
            self.agent.rotate_by_angle(90)
            self.agent.settle_drop_object(10, stop_at_base=False)
            self.agent.rotate_by_angle(-90)
            self.agent.settle_drop_object(3, stop_at_base=False)
            self.agent.rotate_by_angle(-90)
            self.agent.settle_drop_object(10, stop_at_base=False)
            self.agent.rotate_by_angle(90)
            self.agent.settle_drop_object(3, stop_at_base=False)
            p1 = p1[0]

            if p1[1] > self.agent.agent_position["x"]:
                self.agent.direction = -1
                if self.config_file["barrier_type"] in ["ramp", "platform"]:
                    ramp_obj = self.ramp_1
                # self.agent.rotate_by_angle(90)
            else:
                self.agent.direction = 1
                if self.config_file["barrier_type"] in ["ramp", "platform"]:
                    ramp_obj = self.ramp_2
                # self.agent.rotate_by_angle(-90)

        for point in path:
            if point[0] == "goto":
                if len(point) == 6:
                    velocity_threshold = point[5]
                    self.agent.approach(till_x=point[1],
                                        till_y=point[2],
                                        till_z=point[3], approach_dist=point[4], speed_threshold=velocity_threshold)
                elif len(point) == 5:
                    angle = self.agent.calculate_angle([point[1], point[2]])
                    velocity_threshold = point[4]
                    self.agent.approach(till_x=point[1],
                                        till_z=point[2], approach_dist=point[3], speed_threshold=velocity_threshold,
                                        rotation=angle)
                else:
                    angle = self.agent.calculate_angle([point[1], point[2]])
                    velocity_threshold = 1.3
                    self.agent.approach(till_x=point[1],
                                        till_z=point[2], approach_dist=point[3], speed_threshold=velocity_threshold,
                                        rotation=angle)
            elif point[0] == "jump":
                if self.config_file["barrier_type"] in ["ramp", "platform"]:
                    direction_x_z = np.array([-ramp_obj.target_position["x"] + self.agent.agent_position["x"],
                                     -ramp_obj.target_position["z"] + self.agent.agent_position["z"]])
                    direction_x_z = direction_x_z / np.linalg.norm(direction_x_z)

                    self.agent.jump(height=point[1], width=point[2], direction_x_z=direction_x_z,
                                    hight_ground_height=ramp_obj.height)
                else:
                    self.agent.jump(height=point[1], width=point[2])
            elif point[0] == "settle":
                self.agent.settle_drop_object(point[1], stop_at_base=False)
            elif point[0] == "meta":
                meta_data = point
        # utils.make_video(self.agent.output_dir + "/images" + "_a", f"scene_a.mp4", os.path.join(self.agent.base_dir, f"path_{self.agent.path_no}"))
        # utils.make_video(self.agent.output_dir + "/images" + "_b", f"scene_b.mp4", os.path.join(self.agent.base_dir, f"path_{self.agent.path_no}"))
        # shutil.rmtree(self.agent.output_dir + "/images" + "_a")
        # shutil.rmtree(self.agent.output_dir + "/images" + "_b")
        if self.args.enable_image:
            utils.make_video(self.agent.output_dir + "_c", f"scene_c.mp4",
                             os.path.join(self.agent.base_dir, f"path_{self.agent.path_no}"))
            shutil.rmtree(self.agent.output_dir + "_c")
        meta_data_arguments = {
            "config_file": self.config_file,
            "tdw_object": self.tdw_object,
            "high_scene": self.high_scene,
            "camera_obj": self.camera_obj,
            "target_1_color": self.target_1_color,
            "target_2_color": self.target_2_color,
            "target_1_id": self.target_1_id,
            "target_2_id": self.target_2_id,
            "obstacle_1": self.obstacle_1,
            "obstacle_2": self.obstacle_2,
            "ramp_1": self.ramp_1,
            "ramp_2": self.ramp_2,
            "target_1_position": self.target_1_position,
            "target_2_position": self.target_2_position,
            "agent_color": self.agent_color,
            "agent_shape": self.agent_shape,
            "agent": self.agent,
            "pit_ids": self.pit_ids,
            "pit_obj": self.pit_obj
        }
        object_meta = create_scene.construct_2_goal_object_meta_data(**meta_data_arguments)
        state_data = create_scene.create_state_data(self.agent, object_meta, self.camera_obj, meta_data)
        os.makedirs(os.path.join(self.agent.base_dir, f"path_{self.agent.path_no}"), exist_ok=True)
        with open(os.path.join(self.agent.base_dir, f"path_{self.agent.path_no}", "state_info.json"), "w") as fp:
            json.dump(state_data, fp)

