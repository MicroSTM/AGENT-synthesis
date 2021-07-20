from util import physics_agent, utils
import random
import shutil
import os
from util.utils import SceneConfiguration
import json
import numpy as np
import time
import traceback
from util import trajectory_generation
from util import create_scene


class OneGoalScene:
    def __init__(self, tdw_object, camera_obj, args):
        self.tdw_object = tdw_object
        self.args = args
        self.direction = random.sample([-1, 1], 1)[0]
        self.scene_config = SceneConfiguration()
        self.scene_offset = self.scene_config.scene_offset
        self.obstacle_height = random.sample(self.scene_config.obstacle_height, 1)[0]
        self.obstacle_width = random.sample(self.scene_config.obstacle_width, 1)[0]

        self.agent_type = "cone"
        self.agent_color = random.sample(self.scene_config.agent_colors, 1)[0]
        self.target_color = random.sample(self.scene_config.target_colors, 1)[0]
        self.agent_color = {"r": 7 / 255, "g": 121 / 255, "b": 228 / 255, "a": 1.0}
        self.target_color = {"r": 255 / 255, "g": 87 / 255, "b": 51 / 255, "a": 1.0}
        # self.target_color = {"r": 133 / 255, "g": 102 / 255, "b": 170 / 255, "a": 1.0}
        self.config_file = None
        self.obstacle = None
        self.pit_obj = None
        self.camera_obj = camera_obj
        self.high_scene = False
        self.ramp = None
        self.pit_ids = []
        self.results = []
        self.idx = 0

    def execute_path(self, path):
        idx = 0
        meta_data = None
        for i, point in enumerate(path):
            if point[0] == "goto":
                if len(point) == 6:
                    angle = self.agent.calculate_angle([point[1], point[3]])

                    velocity_threshold = point[5]
                    self.agent.approach(till_x=point[1],
                                        till_y=point[2],
                                        till_z=point[3], approach_dist=point[4], speed_threshold=velocity_threshold,
                                        rotation=angle)
                elif len(point) == 5:
                    angle = self.agent.calculate_angle([point[1], point[2]])

                    velocity_threshold = point[4]
                    self.agent.approach(till_x=point[1],
                                        till_z=point[2], approach_dist=point[3], speed_threshold=velocity_threshold,
                                        rotation=angle)
                else:
                    if self.config_file["barrier_type"] == "pit":
                        angle = self.agent.calculate_angle([path[-2][1], path[-2][2]])
                    else:
                        angle = self.agent.calculate_angle([point[1], point[2]])
                    velocity_threshold = 1.3
                    self.agent.approach(till_x=point[1],
                                        till_z=point[2], approach_dist=point[3], speed_threshold=velocity_threshold,
                                        rotation=angle)
            elif point[0] == "jump":

                # look for next goto point and turn towards that
                for e in path[i:]:
                    if e[0] == "goto":
                        if len(e) == 6:
                            angle = self.agent.calculate_angle([e[1], e[3]])
                        else:
                            angle = self.agent.calculate_angle([e[1], e[2]])
                        self.agent.rotate_by_angle(angle)
                        break
                if self.config_file["barrier_type"] in ["ramp", "platform", "platform-cube"]:
                    direction_x_z = np.array([-self.target_position["x"] + self.agent.agent_position["x"],
                                              -self.target_position["z"] + self.agent.agent_position["z"]])
                    direction_x_z = direction_x_z / np.linalg.norm(direction_x_z)
                    self.agent.jump(height=point[1], width=point[2], direction_x_z=direction_x_z, hight_ground_height=point[1])
                else:
                    self.agent.jump(height=point[1], width=point[2])
            elif point[0] == "settle":
                self.agent.settle_drop_object(point[1], stop_at_base=False)
            elif point[0] == "meta":
                meta_data = point
            idx += 1

        # self.agent.reveal_occluder(self.occluder)

        # utils.make_video(self.agent.output_dir + "/images" + "_a", f"scene_a.mp4", os.path.join(self.agent.base_dir, f"path_{self.agent.path_no}"))
        # utils.make_video(self.agent.output_dir + "/images" + "_b", f"scene_b.mp4", os.path.join(self.agent.base_dir, f"path_{self.agent.path_no}"))
        if self.args.enable_image:
            utils.make_video(self.agent.output_dir + "_c", f"scene_c.mp4", os.path.join(self.agent.base_dir, f"path_{self.agent.path_no}"))
            # shutil.rmtree(self.agent.output_dir + "/images" + "_a")
            # shutil.rmtree(self.agent.output_dir + "/images" + "_b")
            shutil.rmtree(self.agent.output_dir + "_c")
        # Save data

        # Create object meta
        object_meta = create_scene.construct_1_goal_object_meta_data(
            obstacle=self.obstacle, target_id=self.target_id,
            target_color=self.target_color,
            agent_color=self.agent_color,
            target_position=self.target_position,
            ramp=self.ramp, config_file=self.config_file,
            agent=self.agent, pit_ids=self.pit_ids,
            occluder=None,
            pit_obj=self.pit_obj
        )
        state_data = create_scene.create_state_data(self.agent, object_meta, self.camera_obj, meta_data)

        self.total_force = [0, 0, 0]
        for i, e in enumerate(self.agent.forces):
            self.total_force[0] += abs(e["x"])
            self.total_force[1] += abs(e["y"])
            self.total_force[2] += abs(e["z"])

        self.results.append((self.total_force, sum(self.total_force), meta_data))
        file_path = os.path.join(self.agent.base_dir, f"path_{self.agent.path_no}")
        os.makedirs(file_path, exist_ok=True)
        with open(os.path.join(file_path, "state_info.json"), "w") as fp:
            json.dump(state_data, fp)

    def execute_config(self, config_file, output_dir):
        self.config_file = config_file
        self.agent = physics_agent.Agent(self.tdw_object, 1, config_file["dir_name"])
        self.target_shape = "sphere"

        # self.target_color = self.scene_config.target_colors[self.idx]
        # self.idx += 1
        return_state = create_scene.create_based_config(config_file=config_file, tdw_object=self.tdw_object,
                                                        high_scene=self.high_scene, camera_obj=self.camera_obj,
                                                        agent_color=self.agent_color, scene_config=self.scene_config,
                                                        agent_class=self.agent, target_color=self.target_color,
                                                        agent_shape=self.agent_type,
                                                        enable_image=self.args.enable_image, target_shape=self.target_shape,
                                                        actually_create=True, args=self.args)
                                                        # add_occuluder=True, scene_state_old=self.config_file)
        self.agent = return_state["agent"]

        self.obstacle = return_state["obstacle"]
        self.pit_ids = return_state["pit_ids"]
        self.ramp = return_state["ramp"]
        self.high_scene = return_state["high_scene"]
        self.target_position = return_state["target_position"]
        self.target_id = return_state["target_id"]
        self.direction = return_state["direction"]
        self.pit_obj = return_state["pit_obj"]
        # self.occluder = return_state["occluder"]
        try:
            paths = self.go_to_goal()
            # paths = [
            #     [("rotate", 90), ("rotate", -90)]
            # ]

            results = []
            time_required = []
            # materials = utils.select_material(self.args)
            # utils.set_wall_floor_material(self.tdw_object, materials["floor_material"],
            #                               materials["wall_material"], pit_obj=self.pit_obj
            #                         )
            for i, p in enumerate(paths):
                start_time = time.time()
                utils.settle_objects(self.tdw_object, n=30)
                self.agent.output_dir = os.path.join(self.agent.output_dir, "images")
                # self.agent.look_at_goal()
                resp = self.tdw_object.communicate({"$type": "do_nothing"})
                self.agent.forces.append({"x":0, "y":0, "z":0})
                self.agent.save_imag(resp)
                self.execute_path(p)
                time_required.append(time.time() - start_time)
                print(f"Took {time.time() - start_time} secs. Average time per trajectory {sum(time_required)/len(time_required)}")
                unique_str = config_file["dir_name"] + f"_path_no_{self.agent.path_no}"
                with open(os.path.join(output_dir, "time.txt"), "a") as fp:
                    fp.write(f"{unique_str} took {time.time() - start_time} secs. Average time per trajectory {sum(time_required)/len(time_required)} \n")
                if self.config_file["barrier_type"] == "ramp":
                    results.append( (
                        self.ramp.rotation, f"Agent path number {self.agent.path_no}", self.agent.total_force.copy()
                    ))
                elif self.config_file["barrier_type"] == "cube":
                    results.append((f"Agent path number {self.agent.path_no}", self.agent.total_force))
                self.reset()
        except Exception as err:
            with open("error.txt", "a") as fp:
                fp.write(f"Error in configuration {output_dir}\n")
            traceback.print_tb(err.__traceback__)
            print(str(err))
        with open("out.txt", "a") as fp:
            fp.write(f"-----------------\n")
        for e in self.results:
            with open("out.txt", "a") as fp:
                fp.write(f"{e}\n")
        with open("out.txt", "a") as fp:
            fp.write(f"-----------------\n")
        self.results = []
        os.makedirs(self.config_file["dir_name"], exist_ok=True)
        with open(os.path.join(self.config_file["dir_name"], "scene_config.json"), "w") as fp:
            json.dump(self.config_file, fp)
        # Destroy scene objects
        self.destroy_objects()
        self.ramp = None
        self.obstacle = None
        self.agent = None
        # for r in results:
        #     print(r)


    def destroy_objects(self):
        commands = [{"$type": "destroy_object", "id": self.agent.agent_id},
                    {"$type": "destroy_object", "id": self.target_id}
                    ]
        if self.config_file["barrier_type"] == "barrier_with_door":
            commands.append({"$type": "destroy_object", "id": self.obstacle.barrier_1})
            commands.append({"$type": "destroy_object", "id": self.obstacle.barrier_2})
            commands.append({"$type": "destroy_object", "id": self.obstacle.barrier_3})
        elif self.config_file["barrier_type"] == "cube":
            if self.obstacle.obstacle_id is not None:
                commands.append({"$type": "destroy_object", "id": self.obstacle.obstacle_id})
        elif self.config_file["barrier_type"] == "ramp":
            commands.extend([
                {"$type": "destroy_object", "id": self.ramp.ramp_base_id},
                {"$type": "destroy_object", "id": self.ramp.ramp_slope_id}
            ])
        elif self.config_file["barrier_type"] == "platform":
            commands.extend([
                {"$type": "destroy_object", "id": self.ramp.ramp_base_id}
            ])
        for pit_id in self.pit_ids:
            commands.append(
                {"$type": "destroy_object", "id": pit_id}
            )
        self.pit_ids = []
        resp = self.tdw_object.communicate(commands)
        utils.print_log(resp)

    def go_to_goal(self):
        if self.config_file["barrier_type"] in ["pit", "pit-with-bridge"]:
            return trajectory_generation.cross_pit(self.agent, self.config_file, self.target_position, self.pit_obj)
        elif self.config_file["barrier_type"] == "cube":
            # Find a way around or over barrier
            return trajectory_generation.cross_barrier(self.obstacle, self.target_position, self.agent.agent_start_position,
                                        self.scene_config, config_file=self.config_file)
        elif self.config_file["barrier_type"] == "barrier_with_door":
            return trajectory_generation.cross_barrier_with_door(self.obstacle, self.target_position,
                                                                 self.agent.agent_start_position)
        elif self.config_file["barrier_type"] == "platform-cube":
            return trajectory_generation.cross_platform_cube(self.obstacle, self.target_position,
                                                             self.agent.agent_start_position)
        elif self.config_file["barrier_type"] == "ramp":
            paths = trajectory_generation.cross_ramp(self.ramp, self.agent, self.config_file,
                                                     restrict_paths=[1, 2, 3])
            return paths
        elif self.config_file["barrier_type"] == "platform":
            paths = trajectory_generation.cross_platform(self.ramp, self.agent)
            return paths
        else:
            return [
                [("goto", self.target_position["x"],self.target_position["z"], 0.24)]
            ]

    def reset(self):
        self.agent.reset()
        utils.stop_obj(self.tdw_object, self.target_id)
        utils.teleport(self.tdw_object, self.target_position, self.target_id)
