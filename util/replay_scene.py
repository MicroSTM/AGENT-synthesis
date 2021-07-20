import json
import os
from os.path import join
from util.scene_configuration import SceneConfiguration
import random
from util import utils
from util.obstacle import Obstacle
from util.barrier_with_door import BarrierWithDoor
from util import replay_agent
import glob
import shutil
from util import create_scene


class ReplayScene:
    def __init__(self, tdw_object, camera_obj, output_dir, config_path, args):
        self.scene_state = None
        self.tdw_object = tdw_object
        self.camera_obj = camera_obj
        self.base_dir = output_dir
        self.scene_config = SceneConfiguration()
        self.scene_offset = self.scene_config.scene_offset
        self.agent_color = random.sample(self.scene_config.agent_colors, 1)[0]
        self.target_color = random.sample(self.scene_config.target_colors, 1)[0]
        self.target_shape = None
        self.high_scene = False
        self.config_path = config_path
        self.occluder = None
        self.scene_type = "scene_1"
        self.target_1_color, self.target_2_color = None, None
        self.target_1_shape, self.target_2_shape = None, None
        self.ramp_1, self.ramp_2, self.ramp = None, None, None
        self.obstacle_1, self.obstacle_2, self.obstacle = None, None, None
        self.path_data = {}
        self.agent = None
        self.agent_shape = None
        self.pit_ids = []
        self.pit_obj = []
        self.args = args
        self.scene_state_old = None
        self.scene_3_4 = True

    def load_config(self, sceneario_type="scene_1_2"):

        with open(os.path.join(self.config_path, "scene_config.json"), "r") as fp:
            self.scene_state = json.load(fp)


    def load_scene(self, sceneario_type="scene_1_2", add_occluder=False):
        self.agent = replay_agent.Agent(self.tdw_object, out_dir=self.base_dir, camera_obj=self.camera_obj,
                                        args=self.args)
        if sceneario_type == "scene_1_2":
            # self.create_based_config(self.scene_state, add_occuluder=add_occluder)
            return_state = create_scene.create_based_config(
                config_file=self.scene_state, tdw_object=self.tdw_object, high_scene=self.high_scene,
                camera_obj=self.camera_obj, agent_color=self.agent_color, scene_config=self.scene_config,
                agent_class=self.agent, target_color=self.target_color, add_occuluder=add_occluder,
                scene_state_old=self.scene_state_old, enable_image=self.args.enable_image, agent_shape=self.agent_shape,
                target_shape=self.target_shape, actually_create=False if self.scene_type != "scene_2" else True,
                args=self.args
            )
            self.agent = return_state["agent"]
            self.obstacle = return_state["obstacle"]
            self.agent_state_objects = {
                "obstacle": return_state["obstacle"],
                "target_obj": return_state["target_obj"],
                "look_around_twice": False
            }
            self.pit_ids = return_state["pit_ids"]
            self.pit_obj = return_state["pit_obj"]
            self.ramp = return_state["ramp"]
            self.high_scene = return_state["high_scene"]
            self.target_position = return_state["target_position"]
            self.target_id = return_state["target_id"]
            self.direction = return_state["direction"]
            self.occluder = return_state["occluder"]
        elif sceneario_type == "scene_3_4":
            create_scene_arguments = {
                "config_file": self.scene_state,
                "tdw_object": self.tdw_object,
                "high_scene": self.high_scene,
                "camera_obj": self.camera_obj,
                "target_1_color": self.target_1_color,
                "target_2_color": self.target_2_color,
                "target_1_shape": self.target_1_shape,
                "target_2_shape": self.target_2_shape,
                "agent_color": self.agent_color,
                "agent_shape": self.agent_shape,
                "agent": self.agent,
                "enable_image": self.args.enable_image,
                "actually_create": False
            }
            return_state = create_scene.create_based_config_2_goal(**create_scene_arguments)
            self.pit_ids = return_state["pit_ids"]
            self.pit_obj = return_state["pit_obj"]
            self.obstacle_1 = return_state["obstacle_1"]
            self.obstacle_2 = return_state["obstacle_2"]
            self.agent_state_objects = {
                "obstacle_1": return_state["obstacle_1"],
                "obstacle_2": return_state["obstacle_2"],
                "target_1_obj": return_state["target_1_obj"],
                "target_2_obj": return_state["target_2_obj"],
                "look_around_twice": False
            }
            if self.agent_state_objects["obstacle_1"] is not None:
                if isinstance(self.agent_state_objects["obstacle_1"], Obstacle):
                    if return_state["obstacle_1"].obstacle_id is not None:
                        self.agent_state_objects["look_around_twice"] = True
                elif isinstance(self.agent_state_objects["obstacle_1"], BarrierWithDoor):
                    if return_state["obstacle_1"].barrier_1 is not None:
                        self.agent_state_objects["look_around_twice"] = True
            if self.agent_state_objects["obstacle_2"] is not None:
                if isinstance(self.agent_state_objects["obstacle_2"], Obstacle):
                    if return_state["obstacle_2"].obstacle_id is not None:
                        self.agent_state_objects["look_around_twice"] = True
                elif isinstance(self.agent_state_objects["obstacle_2"], BarrierWithDoor):
                    if return_state["obstacle_2"].barrier_1 is not None:
                        self.agent_state_objects["look_around_twice"] = True
            self.ramp_1 = return_state["ramp_1"]
            self.ramp_2 = return_state["ramp_2"]
            self.high_scene = return_state["high_scene"]
            self.target_1_position = return_state["target_1_position"]
            self.target_2_position = return_state["target_2_position"]
            self.target_1_id = return_state["target_1_id"]
            self.target_2_id = return_state["target_2_id"]

    def load_path(self, path_dir, scene_3_4=False, do_nothing=False):
        os.makedirs(self.agent.base_dir, exist_ok=True)
        with open(os.path.join(self.agent.base_dir, "scene_config.json"), "w") as fp:
            json.dump(self.scene_state, fp)
        with open(os.path.join(path_dir, "../state_info.json"), "r") as fp:
            self.path_data = json.load(fp)
        # if not do_nothing:
        #     with open(os.path.join(self.agent.base_dir, "state_info.json"), "w") as fp:
        #         json.dump(data, fp)

        if type(self.path_data) == list:
            self.agent.agent_positions = []
            self.agent.agent_rotations = []
            for f in self.path_data:
                self.agent.forces.append(f["agent"]["force"])
                self.agent.agent_positions.append({"x": f["agent"]["position"][0], "y": f["agent"]["position"][1], "z":f["agent"]["position"][2]})
                self.agent.agent_rotations.append(f["agent"]["rotation"])
                self.agent.agent_velocities.append(f["agent"]["velocity"])
                self.agent.agent_angular_velocities.append(f["agent"]["angular_velocity"])
        else:
            self.agent.agent_positions = self.path_data["agent_positions"]
            self.agent.agent_rotations = self.path_data["agent_rotations"]

            self.agent.forces = self.path_data["agent_forces"]
        # self.agent.output_dir = os.path.join(self.base_dir, f"path_{self.agent.path_no}", "images")

    def execute_config(self):
        # Get list of paths
        self.paths = glob.glob(os.path.join(self.config_path, "path_*"))
        for path in self.paths:
            # Load path
            self.load_path(path)
            self.execute_path()

    def execute_path(self, reveal_occuluder=False, look_around=False, do_nothing=False, barrier_falling=True, scene_3_4=True, path_type="Jump"):
        utils.settle_objects(self.tdw_object, n=20)
        self.agent_state_objects["barrier_falling"] = barrier_falling
        if do_nothing or not scene_3_4:
            angle_1 = self.agent.calculate_angle([
                self.target_position["x"], self.target_position["z"]
            ])
            # Tilt up
            self.agent_state_objects["angle_1"] = angle_1
            self.agent_state_objects["angle_2"] = None
            self.agent.replay_agent(look_around, self.agent_state_objects, do_nothing=do_nothing, path_type=path_type,
                                    target_positions=[self.target_position])
        else:
            if look_around:
                angle_1 = self.agent.calculate_angle([
                    self.target_1_position["x"], self.target_1_position["z"]
                ])
                angle_2 = self.agent.calculate_angle([
                    self.target_2_position["x"], self.target_2_position["z"]
                ])
            else:
                angle_1, angle_2 = None, None
            self.agent_state_objects["angle_1"] = angle_1
            self.agent_state_objects["angle_2"] = angle_2
            self.agent.replay_agent(look_around, self.agent_state_objects, do_nothing=False, scene_3_4=scene_3_4,
                                    path_type=path_type, target_positions=[self.target_1_position,
                                                                           self.target_2_position])
        if reveal_occuluder:
            self.agent.reveal_occluder(self.occluder)
        if self.scene_3_4:
            meta_arguments = {
                "config_file": self.scene_state,
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
            object_meta = create_scene.construct_2_goal_object_meta_data(**meta_arguments)
        else:
            meta_arguments = {
                "obstacle": self.obstacle,
                "target_id" : self.target_id,
                "target_color" : self.target_color,
                "agent_color" : self.agent_color,
                "target_position": self.target_position,
                "ramp": self.ramp,
                "config_file": self.scene_state,
                "agent" : self.agent,
                "pit_ids" : self.pit_ids,
                "pit_obj": self.pit_obj,
                "agent_shape": self.agent_shape,
                "target_shape": self.target_shape,
                "occluder": self.occluder
            }
            object_meta = create_scene.construct_1_goal_object_meta_data(**meta_arguments)
        path_meta_data = "None"
        for e in self.path_data[0]:
            if "path_meta_data" in e:
                path_meta_data = e["path_meta_data"]
                with open(join(self.agent.base_dir, e["path_meta_data"][1]), "w") as fp:
                    meta_data = [str(element) for element in e["path_meta_data"]]
                    fp.write(" ".join(meta_data))
        if self.args.generate_video:
            utils.make_video(self.agent.output_dir + "_c", f"scene_c.mp4",
                             self.agent.base_dir, camera_obj=self.camera_obj)
            if self.args.clear_images:
                shutil.rmtree(self.agent.output_dir + "_c")

        state_data = create_scene.create_state_data(agent=self.agent, camera_obj=self.camera_obj,
                                                    object_meta=object_meta, metadata=path_meta_data, use_force=False)
        with open(join(self.agent.base_dir, "../state_info.json"), "w") as fp:
            json.dump(state_data, fp)


    def destroy_objects_scene_1(self):
        commands = [{"$type": "destroy_object", "id": self.agent.agent_id},
                    {"$type": "destroy_object", "id": self.target_id}
                    ]
        if self.scene_state["barrier_type"] == "cube":
            if self.obstacle.obstacle_id is not None:
                commands.append({"$type": "destroy_object", "id": self.obstacle.obstacle_id})
        if self.scene_state["barrier_type"] == "barrier_with_door":
            commands.append({"$type": "destroy_object", "id": self.obstacle.barrier_1})
            commands.append({"$type": "destroy_object", "id": self.obstacle.barrier_2})
            commands.append({"$type": "destroy_object", "id": self.obstacle.barrier_3})

        if self.scene_state["barrier_type"] in ["ramp", "platform"]:
            if self.scene_state["barrier_type"] == "ramp":
                commands.extend([{"$type": "destroy_object", "id": self.ramp.ramp_slope_id}])
            commands.extend([
                {"$type": "destroy_object", "id": self.ramp.ramp_base_id}
            ])

        for e in self.pit_ids:
            commands.append({"$type": "destroy_object", "id": e})
        if self.occluder is not None:
            commands.append({"$type": "destroy_object", "id": self.occluder.occluder_id})
        self.ramp = None
        # Destroy scene objects
        resp = self.tdw_object.communicate(commands)
        utils.print_log(resp)
        self.obstacle = None
        self.agent = None
        self.occluder = None
        self.scene_state_old = None
        self.agent_state_objects = {}
        self.pit_ids = []
        self.pit_obj = None

    def destroy_objects_scene_3_4(self):
        commands = [{"$type": "destroy_object", "id": self.agent.agent_id},
                    {"$type": "destroy_object", "id": self.target_1_id},
                    {"$type": "destroy_object", "id": self.target_2_id}
                    ]
        if isinstance(self.obstacle_1, Obstacle):
            if self.obstacle_1.obstacle_id is not None:
                commands.append({"$type": "destroy_object", "id": self.obstacle_1.obstacle_id})
        if isinstance(self.obstacle_2, Obstacle):
            if self.obstacle_2.obstacle_id is not None:
                commands.append({"$type": "destroy_object", "id": self.obstacle_2.obstacle_id})
        if isinstance(self.obstacle_1, BarrierWithDoor):
            if self.obstacle_1.barrier_1:
                commands.append({"$type": "destroy_object", "id": self.obstacle_1.barrier_1})
                commands.append({"$type": "destroy_object", "id": self.obstacle_1.barrier_2})
                commands.append({"$type": "destroy_object", "id": self.obstacle_1.barrier_3})
        if isinstance(self.obstacle_2, BarrierWithDoor):
            if self.obstacle_2.barrier_1:
                commands.append({"$type": "destroy_object", "id": self.obstacle_2.barrier_1})
                commands.append({"$type": "destroy_object", "id": self.obstacle_2.barrier_2})
                commands.append({"$type": "destroy_object", "id": self.obstacle_2.barrier_3})

        if self.ramp_1 is not None:
            commands.extend([
                {"$type": "destroy_object", "id": self.ramp_1.ramp_base_id},
            ])
            if self.ramp_1.ramp_slope_id:
                commands.extend([{"$type": "destroy_object", "id": self.ramp_1.ramp_slope_id}])
        if self.ramp_2 is not None:
            commands.extend([
                {"$type": "destroy_object", "id": self.ramp_2.ramp_base_id}
            ])
            if self.ramp_2.ramp_slope_id:
                commands.extend([{"$type": "destroy_object", "id": self.ramp_2.ramp_slope_id}])
        for e in self.pit_ids:
            commands.append({"$type": "destroy_object", "id": e})
        if self.occluder is not None:
            commands.append({"$type": "destroy_object", "id": self.occluder.occluder_id})
        self.ramp = None
        self.ramp_1, self.ramp_2 = None, None
        self.obstacle_1, self.obstacle_2 = None, None
        self.agent_state_objects = {}
        # Destroy scene objects

        resp = self.tdw_object.communicate(commands)
        utils.print_log(resp)
        self.obstacle = None
        self.agent = None
        self.occluder = None
        self.pit_obj = None
        self.pit_ids = []

    def resconstruct_3_d_trajectory(self):
        scene_path = "test_data/human_exp_v2_trimmed/"
        scene_dirs = os.listdir(scene_path)
        for scene_dir in scene_dirs:
            subtypes = os.listdir(join(scene_path, scene_dir))
            for subtype in subtypes:
                trials = os.listdir(join(scene_path, scene_dir, subtype, "Agent_0"))
                for trial in trials:
                    subdirs = os.listdir(join(scene_path, scene_dir, subtype, "Agent_0", trial))

    def scenario_2_action_efficiency(self, args):
        """
        Type 2: (Most basic): Find a configuration with height > 1 or depth > 1 . For Test A we take same video as fam
        and just remove the barrier. For Test B find the configuration with same agent and goal position but not barrier
        and straight path
        Type 2: Same as 1 but instead of making barrier disappear move it out of the way
        Type 3: Find a configuration with height > 3 or depth greater than 2. For Test A we take the same video as a fam
        and make obstacles smaller in height or depth. For Test B find the configuration with the same agent and barrier
        path and Test A barrier with most efficient path around it. In both cases, we keep the action constant across
        fam and test. The efficient path is either straight or the same action
        Type 4:  Find a configuration with height > 1 or depth > 1. If most efficient path is jumping than in Test A
        increase height and decrease depth and keep the same path. If most efficient path is going around than make
        barrier depth longer and height smaller. The agent path becomes in-efficient. In Test B agent uses efficient
        path around the new barrier. The action is different than before.
        :param args:
        :return:
        """
        NUM_OF_SETS = args.set_num
        NUM_OF_FAMILIRIZATION_VIDEOS = 4
        history = []
        self.scene_3_4 = False
        # Get list of available configuration and their paths
        scene_1_list = utils.get_single_goal_scenes()
        obstacle_type_dict = {
            "Type-2.1": ["barrier", "pit"],
            "Type-2.2": ["barrier", "pit"],
            "Type-2.3": ["barrier"],
            "Type-2.4": ["pit-with-bridge", "barrier_with_door"],
            "Type-2.5": ["barrier"]
        }
        obstacle_type_list = []

        for e in range(NUM_OF_SETS):
            obstacle_type_list.append( obstacle_type_dict[args.test_type][e % len(obstacle_type_dict[args.test_type])])

        for set_no in range(args.config_start, args.config_end):
                base_dir = join(args.out_dir, args.test_type.replace(".", "_"), f"Trial_{set_no}")
                os.makedirs(base_dir, exist_ok=True)
                scene_type = "barrier_scenes"
                test_type = args.test_type
                scene_mat = utils.get_scene_materials(self.tdw_object, self.args)

                self.target_color = scene_mat["goal_1_color"]
                self.agent_color = scene_mat["agent_color"]
                self.agent_shape = scene_mat["agent_shape"]
                self.target_shape = scene_mat["goal_1_shape"]

                fam_paths, test_paths, history = utils.get_scene_2_action_efficiency_paths(scene_type, scene_1_list,
                                                                                           NUM_OF_FAMILIRIZATION_VIDEOS, test_type, history,
                                                                                           obstacle_type_list[set_no - args.config_start])
                fam_config = None
                for j, fam_path in enumerate(fam_paths):
                    self.config_path = join( fam_path["scene_type"], fam_path["output"],
                                            fam_path["config"])
                    self.load_config()
                    self.scene_state = utils.change_scene_2_action_efficiency_config(test_type="Fam", test_no=j,
                                                                                     config=self.scene_state, test_paths=test_paths,
                                                                                     fam_config=None,
                                                                                     obstacle_type=obstacle_type_list[
                                                                       set_no - args.config_start])
                    fam_config = self.scene_state.copy()
                    self.load_scene()

                    if obstacle_type_list[set_no - args.config_start] in ["pit-with-bridge", "pit"]:
                        utils.set_wall_floor_material(self.tdw_object, scene_mat["floor_material"],
                                                      scene_mat["wall_material"], self.pit_obj)
                    if test_type == "Type-6":
                        utils.set_pit_material(self.pit_ids, scene_mat["floor_material"],
                                               pit_width=fam_path["obstacle_width"], tdw_object=self.tdw_object)
                    self.agent.base_dir = os.path.join(base_dir, f"Familarization_video_{j+1}")
                    self.agent.output_dir = os.path.join(self.agent.base_dir, "images")
                    path_dir = join( self.config_path, fam_path["path"])
                    self.load_path(path_dir)
                    self.execute_path(scene_3_4=False, path_type=fam_path["path_type"])
                    self.destroy_objects_scene_1()
                for test_path, test_no in zip(test_paths, ["A", "B"]):
                    self.config_path = join( test_path["scene_type"], test_path["output"],
                                            test_path["config"])
                    self.load_config()
                    self.scene_state = utils.change_scene_2_action_efficiency_config(test_type=test_type, test_no=test_no,
                                                                                     config=self.scene_state, test_paths=test_paths,
                                                                                     fam_config=fam_config,
                                                                                     obstacle_type=obstacle_type_list[
                                                                       set_no - args.config_start])
                    self.load_scene()
                    if obstacle_type_list[set_no - args.config_start] in ["pit-with-bridge", "pit"]:
                        utils.set_wall_floor_material(self.tdw_object, scene_mat["floor_material"],
                                                      scene_mat["wall_material"], self.pit_obj)
                    if test_type == "Type-6":
                        utils.set_pit_material(self.pit_ids, scene_mat["floor_material"],
                                               pit_width=self.scene_state["pit_width"], tdw_object=self.tdw_object)
                    self.agent.base_dir = os.path.join(base_dir, f"Test_video_{test_no}")
                    self.agent.output_dir = os.path.join(self.agent.base_dir, "images")
                    path_dir = join(self.config_path, test_path["path"])
                    self.load_path(path_dir)
                    self.execute_path(scene_3_4=False, path_type=test_path["path_type"])
                    self.destroy_objects_scene_1()
        return

    def scenario_3_unobserved_constraints(self, args):

        NUM_OF_SETS = args.set_num
        NUM_OF_FAMILIRIZATION_VIDEOS = 4
        history = []
        scene_1_list = utils.get_single_goal_scenes()
        self.scene_type = "scene_2"
        self.scene_3_4 = False

        self.tdw_object.communicate(self.camera_obj.move_camera_scene_2())
        obstacle_type_dict = {
            "Type-3.1": ["barrier"],
            "Type-3.2": ["barrier", "barrier_with_door"],
        }

        obstacle_type_list = []

        for e in range(NUM_OF_SETS):
            obstacle_type_list.append(obstacle_type_dict[args.test_type][e % len(obstacle_type_dict[args.test_type])])

        for set_no in range(args.config_start, args.config_end):
            # Create Set directory
            base_dir = join(args.out_dir, args.test_type.replace(".", "_"), f"Trial_{set_no}")
            os.makedirs(base_dir, exist_ok=True)
            scene_type = "barrier_scenes"
            test_type = args.test_type
            scene_mat = utils.get_scene_materials(self.tdw_object, self.args)
            self.target_color = scene_mat["goal_1_color"]
            self.agent_color = scene_mat["agent_color"]
            self.agent_shape = scene_mat["agent_shape"]
            self.target_shape = scene_mat["goal_1_shape"]
            fam_paths, test_paths, history = utils.get_scene_3_unobserved_constraints_paths(scene_type, scene_1_list,
                                                                                            None,
                                                                                            NUM_OF_FAMILIRIZATION_VIDEOS,
                                                                                            test_type,
                                                                                            history,
                                                                                            obstacle_type_list[
                                                                                                set_no - args.config_start])

            for j, fam_path in enumerate(fam_paths):

                self.config_path = join(fam_path["scene_type"], fam_path["output"],
                                        fam_path["config"])
                self.load_config()
                self.scene_state_old = self.scene_state.copy()
                self.scene_state, self.scene_state_old = utils.change_scene_3_unobserved_constraints_config(
                    test_type=test_type, test_no="Fam", config=self.scene_state, familirization=fam_paths,
                    obstacle_type=obstacle_type_list[set_no - args.config_start], occluder_state=self.scene_state_old,
                    fam_occluder_state=self.scene_state_old)
                fam_occluder_state = self.scene_state_old
                self.load_scene(add_occluder=True)

                self.agent.base_dir = os.path.join(base_dir, f"Familarization_video_{j+1}")
                self.agent.output_dir = os.path.join(self.agent.base_dir, "images")
                path_dir = join( self.config_path, fam_path["path"])

                self.load_path(path_dir)
                self.execute_path(barrier_falling=False, scene_3_4=False, path_type=fam_path["path_type"])
                self.destroy_objects_scene_1()

            for test_path, test_no, tmp in zip(test_paths, ["A", "B"],
                                          ["scene_config_Test_video_A.json", "scene_config_Test_video_B.json"]):
                self.config_path = join(test_path["scene_type"], test_path["output"],
                                        test_path["config"])
                self.load_config()
                self.scene_state_old = self.scene_state.copy()
                self.scene_state, self.scene_state_old = utils.change_scene_3_unobserved_constraints_config(
                    test_type=test_type, test_no=test_no, config=self.scene_state, familirization=fam_paths,
                    obstacle_type=obstacle_type_list[set_no - args.config_start], occluder_state=self.scene_state_old,
                    fam_occluder_state=fam_occluder_state)

                self.load_scene(add_occluder=True)

                self.agent.testing = True
                self.agent.base_dir = os.path.join(base_dir, f"Test_video_{test_no}")
                self.agent.output_dir = os.path.join(self.agent.base_dir, "images")
                path_dir = join(self.config_path, test_path["path"])
                self.load_path(path_dir)
                self.execute_path(reveal_occuluder=True, barrier_falling=False, scene_3_4=False, path_type=test_path["path_type"])
                self.destroy_objects_scene_1()
        return

    def scenario_1_goal_preferences(self, args):
        goal_2_list = utils.get_two_goal_scenes()
        NUM_OF_SETS = args.set_num
        self.scene_type = "scene_3"
        self.scene_3_4 = True
        history = []
        selected_targets = [
            ("2", True),
            ("2", False),
            ("1", True),
            ("1", False)
        ]
        selected_targets_switched = []
        for e in range(NUM_OF_SETS):
            selected_targets_switched.append(selected_targets[e%len(selected_targets)])
        # Get obstacle type

        obstacles_dict = {
            "Fam": ["ramp", "platform", "pit"],
            "Type-1.1": ["barrier", "ramp", "platform", "pit"],
            "Type-1.2.0__1.2": ["barrier", "ramp", "platform", "pit"],
            "Type-1.1.0__1.2": ["barrier"],
            "Type-1.3": ["barrier", "ramp", "platform", "pit"],
            "Type-2.2.0__1.4": ["barrier", "ramp", "platform", "pit"],
            "Type-2.1.0__1.4": ["barrier"],
        }
        obstacles_list_fam = []
        obstacles_list_test = []

        for e in range(NUM_OF_SETS):
            obj_ = random.choice(obstacles_dict["Fam"])
            if args.test_type in ["Type-1.1", "Type-1.2.0__1.2"]:
                obstacles_list_fam.append([obj_]*2)
            else:
                if obj_ in ["ramp", "platform"]:
                    obj__ = random.choice(["barrier", "barrier_with_door"])
                else:
                    obj__ = random.choice(["barrier", "pit-with-bridge"])
                obstacles_list_fam.append([obj_, obj__])
            if args.test_type in ["Type-1.1"]:
                obstacles_list_test.append(obstacles_list_fam[-1])
            elif args.test_type in ["Type-1.3"]:
                obstacles_list_test.append([obstacles_list_fam[-1][0]]*2)
            else:
                obj_1 = random.choice(obstacles_dict[args.test_type])
                if obj_1 in ["ramp", "platform"]:
                    obj_2 = random.choice(["barrier", "barrier_with_door"])
                else:
                    obj_2 = random.choice(["barrier", "pit-with-bridge"])
                obstacles_list_test.append([obj_2, obj_1])

        goal_2_list_cost = utils.calculate_distance(goal_2_list)
        for set_no in range(args.config_start, args.config_end):
            goal_colors = utils.get_scene_materials(self.tdw_object, self.args)
            self.target_1_color, self.target_2_color = goal_colors["goal_1_color"], goal_colors["goal_2_color"]
            self.agent_color = goal_colors["agent_color"]
            self.agent_shape = goal_colors["agent_shape"]
            self.target_1_shape = goal_colors["goal_1_shape"]
            self.target_2_shape = goal_colors["goal_2_shape"]
            base_dir = join(args.out_dir, f"Trial_{set_no}")
            if not os.path.isdir(base_dir):
                os.mkdir(join(args.out_dir, f"Trial_{set_no}"))
            scene_type = "barrier_scenes_3_4"
            test_type = args.test_type
            fam_paths, test_paths, history, switch_goal = \
                utils.get_scene_1_goal_preferences_paths(scene_type, goal_2_list_cost, test_type, history,
                                                         selected_targets_switched[set_no - args.config_start][1],
                                                         selected_targets_switched[set_no - args.config_start][0],
                                                         obstacles_list_fam[set_no - args.config_start],
                                                         obstacles_list_test[set_no - args.config_start])

            for j, fam_path in enumerate(fam_paths):
                self.config_path = join(fam_path["scene_type"], fam_path["output"],
                                        fam_path["config"])
                self.load_config(sceneario_type="scene_3_4")

                self.scene_state = utils.change_scene_1_goal_preferences_config(self.scene_state, None, fam_paths,
                                                                                test_type,
                                                                                fam=True,
                                                                                obstacles_list_fam=obstacles_list_fam[
                                                                                    set_no - args.config_start],
                                                                                obstacles_list_test=obstacles_list_test[
                                                                                    set_no - args.config_start])
                self.load_scene(sceneario_type="scene_3_4")

                if obstacles_list_fam[set_no-args.config_start][0] in ["pit-with-bridge", "pit"]:
                    utils.set_wall_floor_material(self.tdw_object, goal_colors["floor_material"],
                                                  goal_colors["wall_material"], self.pit_obj)
                path_dir = join(fam_path["scene_type"], fam_path["output"], fam_path["config"], fam_path["path"])
                self.agent.base_dir = os.path.join(base_dir, f"Familarization_video_{j + 1}")
                self.agent.output_dir = os.path.join(self.agent.base_dir, "images")
                self.load_path(path_dir)

                self.execute_path(look_around=True, scene_3_4=True, path_type=fam_path["path_type"])
                self.destroy_objects_scene_3_4()

            if switch_goal:
                self.target_1_color, self.target_2_color = self.target_2_color, self.target_1_color
                self.target_1_shape, self.target_2_shape = self.target_2_shape, self.target_1_shape

            for j, test_video in zip(["A", "B"], test_paths):

                self.config_path = join(test_video["scene_type"], test_video["output"],
                                        test_video["config"])
                self.load_config(sceneario_type="scene_3_4")
                self.scene_state = utils.change_scene_1_goal_preferences_config(self.scene_state, j, test_paths, test_type,
                                                                                obstacles_list_fam=obstacles_list_fam[
                                                                   set_no - args.config_start],
                                                                                obstacles_list_test=obstacles_list_test[
                                                                   set_no - args.config_start])

                self.load_scene(sceneario_type="scene_3_4")

                if obstacles_list_test[set_no-args.config_start][0] in ["pit-with-bridge", "pit"] or \
                        obstacles_list_test[set_no-args.config_start][1] in ["pit-with-bridge", "pit"]:
                    utils.set_wall_floor_material(self.tdw_object, goal_colors["floor_material"],
                                                  goal_colors["wall_material"], self.pit_obj)
                path_dir = join(test_video["scene_type"], test_video["output"], test_video["config"], test_video["path"])
                self.agent.base_dir = os.path.join(base_dir, f"Test_{j}")
                self.agent.output_dir = os.path.join(self.agent.base_dir, "images")
                self.load_path(path_dir)

                self.execute_path(look_around=True, scene_3_4=True, path_type=test_video["path_type"])
                self.destroy_objects_scene_3_4()

    def scenario_4_cost_reward_trade_offs(self, args):
        NUM_OF_SETS = args.set_num
        history = []
        # Get list of available configuration and their paths
        goal_1_list = utils.get_single_goal_scenes()
        goal_2_list = utils.get_two_goal_scenes()
        goal_2_list = utils.calculate_distance(goal_2_list)
        self.scene_type = "scene_4"
        selected_targets = []
        all_targets = [
            ("2", True),
            ("2", False),
            ("1", True),
            ("1", False)
        ]
        for i in range(NUM_OF_SETS):
            selected_targets.append(all_targets[i%len(all_targets)])
        with open("../agent/agents.json", "r") as fp:
            agent_list = json.load(fp)
        object_type_dict = {
            "Fam": ["barrier", "ramp", "platform", "pit"],
            "Type-4.1": ["barrier_with_door", "pit-with-bridge"],
            "Type-4.2": ["ramp", "platform", "pit"]
        }
        object_type_list = []
        object_type_list_test = []
        for e in range(NUM_OF_SETS):
            object_type_list.append(object_type_dict["Fam"][e%len(object_type_dict["Fam"])])
            if object_type_list[-1] == "barrier":
                object_type_list_test.append(["barrier", "barrier"])
            else:
                if args.test_type == "Type-4.1":
                    obj_1 = random.choice(object_type_dict[args.test_type])
                    if obj_1 in ["pit-with-bridge"]:
                        obj_2 = random.choice(["pit-with-bridge", "none"])
                    else:
                        obj_2 = random.choice(["barrier_with_door", "none"])
                else:
                    obj_2 = random.choice(object_type_dict[args.test_type])
                    if obj_2 in ["ramp", "platform"]:
                        obj_1 = random.choice(["barrier_with_door", "none"])
                    else:
                        obj_1 = random.choice(["pit-with-bridge", "none"])
                object_type_list_test.append([obj_1, obj_2])

        for set_no in range(args.config_start, args.config_end):
                # Create Set directory
                base_dir = join(args.out_dir, args.test_type.replace(".", "_"), f"Trial_{set_no}")
                os.makedirs(base_dir, exist_ok=True)

                scene_mat = utils.get_scene_materials(self.tdw_object, self.args)
                self.agent_color = scene_mat["agent_color"]
                self.agent_shape = scene_mat["agent_shape"]
                self.target_1_shape = scene_mat["goal_1_shape"]
                self.target_2_shape = scene_mat["goal_2_shape"]
                test_type = args.test_type
                self.scene_3_4 = False
                fam_paths, test_paths, history = utils.get_scene_4_cost_reward_trade_offs_paths(test_type, goal_1_list,
                                                                                                goal_2_list, history,
                                                                                                selected_targets[set_no-args.config_start][0],
                                                                                                selected_targets[set_no-args.config_start][1],
                                                                                                object_type_list[set_no-args.config_start],
                                                                                                object_type_list_test[set_no-args.config_start])
                self.current_barrier_list = object_type_list_test[set_no-args.config_start]

                if test_paths[0]["target"] == "Target-2":
                    fam_paths = fam_paths[2:] + fam_paths[:2]
                    target_shape_color = [[scene_mat["goal_2_shape"], scene_mat["goal_2_color"]]] * 2 + \
                                         [[scene_mat["goal_1_shape"], scene_mat["goal_1_color"]]] * 2
                    hight_priority = 2
                else:
                    target_shape_color = [[scene_mat["goal_1_shape"], scene_mat["goal_1_color"]]] * 2 + \
                                         [[scene_mat["goal_2_shape"], scene_mat["goal_2_color"]]] * 2
                    hight_priority = 0
                self.tdw_object.communicate(self.camera_obj.move_camera_scene_scene_1())
                self.high_scene = False
                test_configs = []
                for j, fam_path in enumerate(fam_paths):

                    self.config_path = join(fam_path["scene_type"], fam_path["output"],
                                            fam_path["config"])
                    self.target_shape = target_shape_color[j][0]
                    self.target_color = target_shape_color[j][1]
                    self.load_config()
                    self.scene_state = utils.change_scene_4_cost_reward_trade_offs_config_fam(self.scene_state,
                                                                                              is_high_priority=True if j == hight_priority
                                                                                              else False,
                                                                                              object_type=
                                                                                              object_type_list[
                                                                                                  set_no - args.config_start])
                    self.load_scene()

                    if object_type_list[set_no-args.config_start] in ["pit-with-bridge", "pit"]:
                        utils.set_wall_floor_material(self.tdw_object, scene_mat["floor_material"],
                                                      scene_mat["wall_material"], self.pit_obj)
                    self.agent.base_dir = os.path.join(base_dir, f"Familarization_video_{j+1}")
                    self.agent.output_dir = os.path.join(self.agent.base_dir, "images")
                    path_dir = join(self.config_path, fam_path["path"])
                    if j in [0, 2]:
                        self.load_path(path_dir, scene_3_4=False, do_nothing=True)
                        self.execute_path(do_nothing=True, scene_3_4=False, path_type=fam_path["path_type"])
                    else:
                        self.load_path(path_dir, scene_3_4=False)
                        self.execute_path(scene_3_4=False, path_type=fam_path["path_type"])
                    self.destroy_objects_scene_1()

                self.tdw_object.communicate(self.camera_obj.move_camera_scene_scene_3())
                self.high_scene = False
                if test_paths[0]["target"] == "Target-1":
                    self.target_1_color, self.target_2_color = scene_mat["goal_1_color"], scene_mat["goal_2_color"]
                    self.target_1_shape, self.target_2_shape = scene_mat["goal_1_shape"], scene_mat["goal_2_shape"]
                else:
                    self.target_2_color, self.target_1_color = scene_mat["goal_1_color"], scene_mat["goal_2_color"]
                    self.target_2_shape, self.target_1_shape = scene_mat["goal_1_shape"], scene_mat["goal_2_shape"]
                self.scene_3_4 = True

                for j, test_path in zip(["A", "B"], test_paths):
                    self.config_path = join(test_path["scene_type"], test_path["output"],
                                            test_path["config"])
                    self.load_config(sceneario_type="scene_3_4")
                    self.scene_state = utils.change_scene_4_cost_reward_trade_offs_config(test_type, self.scene_state,
                                                                                          test_paths,
                                                                                          test_configs=test_configs,
                                                                                          test_no=j,
                                                                                          object_type=
                                                                                          object_type_list_test[
                                                                                              set_no - args.config_start])
                    test_configs.append(self.scene_state.copy())
                    self.load_scene(sceneario_type="scene_3_4")
                    if object_type_list_test[set_no-args.config_start][0] in ["pit-with-bridge", "pit"] or \
                        object_type_list_test[set_no-args.config_start][1] in ["pit-with-bridge", "pit"]:
                        utils.set_wall_floor_material(self.tdw_object, scene_mat["floor_material"],
                                                      scene_mat["wall_material"], self.pit_obj)
                    path_dir = join(test_path["scene_type"], test_path["output"], test_path["config"], test_path["path"])
                    self.agent.base_dir = os.path.join(base_dir, f"Test_{j}")
                    self.agent.output_dir = os.path.join(self.agent.base_dir, "images")
                    self.load_path(path_dir, scene_3_4=True)
                    self.execute_path(look_around=True, scene_3_4=True, path_type=test_path["path_type"])
                    self.destroy_objects_scene_3_4()
