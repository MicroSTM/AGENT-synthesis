from util import utils
from tdw.tdw_utils import TDWUtils
from tdw.output_data import Images, OutputData, Transforms, Rigidbodies, Bounds, SegmentationColors, IdPassSegmentationColors
import os
from util.utils import euler_to_quaternion, convert_to_radians
import numpy as np
from util.obstacle import Obstacle
from util.barrier_with_door import BarrierWithDoor
import math
from PIL import Image as images
from collections import deque
class Agent:
    def __init__(self, tdw_object, out_dir, camera_obj, args):
        self.tdw_object = tdw_object
        self.base_dir = out_dir
        self.agent_positions = []
        self.agent_rotations = []
        self.agent_velocities = []
        self.agent_angular_velocities = []
        self.path_no = 1
        self.camera_obj = camera_obj
        self.agent_start_position = None
        self.agent_angle_y = 0
        self.idx = 0
        self.forces = []
        self.target_pos = None
        self.angle = 0
        self.view_vector = np.array([0, 1])
        self.testing = False
        self.remote = args.remote
        self.args = args
        self.view_vector = [0, 1]
        self.agent_angle = 0
        self.agent_state_data = []


    def calculate_angle(self, position, tilt=False):
        # try:
        if tilt:
            vect_to_target = [position[0] - self.agent_position["x"],
                              position[1] - self.agent_position["y"],
                              position[2] - self.agent_position["z"],
                              ]
        else:
            vect_to_target = [position[0] - self.agent_position["x"],
                              position[1] - self.agent_position["z"]]

        vect_to_target = vect_to_target/np.linalg.norm(vect_to_target)
        if tilt:
            view_vector = vect_to_target.copy()
            view_vector[1] = 0
            view_vector = np.array(view_vector)
            dot_product = np.dot(vect_to_target, view_vector)
            angle = np.degrees(np.arccos(dot_product))

        else:
            angle = np.degrees(
                np.math.atan2(np.linalg.det([self.view_vector, vect_to_target]),
                              np.dot(self.view_vector, vect_to_target)))
        angle = -1 * int(round(angle))
        return angle

    def tilt_agent(self, target_position):
        rotated_angle = 0
        unit_rotation = 2
        if abs(target_position["y"] - self.agent_current_position[1]) < 0.15:
            return []
        rotation = self.calculate_angle([target_position["x"], target_position["y"], target_position["z"]],
                                        tilt=True)
        resp = self.tdw_object.communicate({"$type": "do_nothing"})
        self.save_imag(resp)
        rotation = -1*rotation
        vect_to_target = [target_position["x"] - self.agent_current_position[0],
                          target_position["z"] - self.agent_current_position[2]]
        r = 0.1
        d = np.linalg.norm(vect_to_target)
        c_x = (d + r)/d * (self.agent_current_position[0] - target_position["x"]) + target_position["x"]
        c_z = (d + r)/d * (self.agent_current_position[2] - target_position["z"]) + target_position["z"]
        c_y = self.agent_current_position[1]
        c = [c_x, c_y, c_z]
        replay_order = []
        starting_point = list(self.agent_current_position)
        while True:
            alpha =  min(abs(rotation - rotated_angle), unit_rotation)
            rotated_angle += alpha
            self.agent_angle_y += alpha
            qo = euler_to_quaternion(convert_to_radians(-1*self.agent_angle_y), convert_to_radians(self.agent_angle), 0)
            p = [starting_point[0], starting_point[1], starting_point[2]]
            if self.agent_name in ["cone", "cube"]:
                x_ = (p[0] - c[0])*math.cos(math.radians(self.agent_angle_y)) + c[0]
                y_ = math.sin(math.radians(self.agent_angle_y))*r + c[1]
                z_ = (p[2] - c[2])*math.cos(math.radians(self.agent_angle_y)) + c[2]
            else:

                x_ = -r*math.sin(math.radians(self.agent_angle_y))/d * (target_position["x"] - p[0]) + p[0]
                y_ = (1-math.cos(math.radians(self.agent_angle_y)))*r + p[1]
                z_ = -r*math.sin(math.radians(self.agent_angle_y))/d * (target_position["z"] - p[2]) + p[2]

            # resp = self.tdw_object.communicate(
            #     {"$type": "rotate_object_to", "rotation": {"w": qo[3], "x": qo[0], "y": qo[1], "z": qo[2]},
            #      "id": self.agent_id})
            resp = self.tdw_object.communicate([{"$type": "teleport_object",
                                                 "position": {"x": x_, "y": y_,
                                                              "z": z_}, "id": self.agent_id},
                                                {"$type": "rotate_object_to",
                                                 "rotation": {"w": qo[3], "x": qo[0], "y": qo[1], "z": qo[2]},
                                                 "id": self.agent_id}
                                                ])
            replay_order.append([{"$type": "teleport_object",
                                                 "position": {"x": x_, "y": y_,
                                                              "z": z_}, "id": self.agent_id},
                                                {"$type": "rotate_object_to",
                                                 "rotation": {"w": qo[3], "x": qo[0], "y": qo[1], "z": qo[2]},
                                                 "id": self.agent_id}
                                                ])
            self.save_imag(resp)
            if abs(rotated_angle) == abs(rotation):
                return replay_order

    def replay_tilt(self, replay_order):
        replay_order.reverse()
        self.agent_angle_y = 0
        for e in replay_order:
            resp = self.tdw_object.communicate(e)
            self.save_imag(resp)

    def rotate_agent(self, rotation, rotate_y=False):
        rotated_angle = 0
        unit_rotation = 5
        hard_stop = 72
        rotation_axis = self.agent_position.copy()
        direction_ = -1 if rotation - rotated_angle > 0 else 1

        while True:
            direction = 1 if rotation - rotated_angle > 0 else -1
            angle = direction * min(abs(rotation - rotated_angle), unit_rotation)
            rotated_angle += angle
            self.agent_angle += angle
            qo = euler_to_quaternion(0, convert_to_radians(self.agent_angle), 0)
            cmd = [
                {"$type": "rotate_object_to", "rotation": {"w": qo[3], "x": qo[0], "y": qo[1], "z": qo[2]},
                 "id": self.agent_id}
            ]
            cmd = self.follow_agent(cmd)
            resp = self.tdw_object.communicate(cmd)
            self.save_imag(resp)
            hard_stop -= 1
            if rotated_angle == rotation or hard_stop < 0:
                return

    def rotate_point(self, p1, agent_p, angle):
        agent_p[0] -= p1[0]
        agent_p[1] -= p1[1]
        agent_p_new = [agent_p[0] * math.cos(math.radians(angle)) - agent_p[1] * math.sin(math.radians(angle)),
                       agent_p[0] * math.sin(math.radians(angle)) - agent_p[1] * math.cos(math.radians(angle))]
        agent_p_new[0] += p1[0]
        agent_p_new[1] += p1[1]
        return agent_p_new

    def create_agent_new(self, position, color, agent_name):
        selected_color = color
        self.agent_start_position = position
        # agent_name = available_agents[random.randint(0, len(available_agents) - 1)]
        if self.remote:
            url = f"file:///agent_model/{agent_name.title()}/StandaloneLinux64/{agent_name}"
        else:
            url = "file:///" + os.path.join(os.getcwd(), "../agent_models", agent_name.title(), "StandaloneOSX",
                                            agent_name)
        self.agent_id = self.tdw_object.get_unique_id()
        self.agent_position = position
        self.agent_rotation = {"x": 0, "y": 0, "z": 0}
        self.agent_name = agent_name
        resp = self.tdw_object.communicate({"$type": "add_object",
                                     "name": agent_name,
                                     "url": url,
                                     "scale_factor": 1,
                                     "id": self.agent_id,
                                     "position": position})
        utils.print_log(resp)
        # self.agent_id = self.tdw_object.add_object("prim_cone", position=self.agent_position,
        #                                            rotation=self.agent_rotation,
        #                                            library="models_special.json")
        resp = self.tdw_object.communicate([
            {"$type": "scale_object", "scale_factor": {"x": 0.2, "y": 0.2, "z": 0.2}, "id": self.agent_id},
            {"$type": "set_color_in_substructure",
             "color": selected_color,
             "object_name": agent_name.title(), "id": self.agent_id},
            {"$type": "step_physics", "frames": 10},
            {"$type": "set_kinematic_state", "id": self.agent_id, "is_kinematic": True, "use_gravity": False}
        ])
        print("Agent created")
        if self.args.follow_camera:
            utils.print_log(resp)
            cmd = [
                {"$type": "create_avatar", "type": "A_Img_Caps_Kinematic", "id": "agent_follow_camera"}
            ]
            cmd = self.follow_agent(cmd)
            resp = self.tdw_object.communicate(cmd)
        return

    def add_black_frames(self):
        img_no = 10
        os.makedirs(self.output_dir + "_" + "c", exist_ok=True)
        for _ in range(img_no):
            img = np.zeros([self.camera_obj.width, self.camera_obj.height, 3]).astype(np.uint8)
            img[:, :, :] = 255
            img = images.fromarray(img)
            img.save(os.path.join(self.output_dir + "_" + "c", f"img_image-{self.idx}.png"))
            self.idx += 1

    def save_imag(self, response, force={"x":0, "y":0, "z":0}):
        state_data = {}
        visible_objects = []
        visible_objects_ = []
        obj_id_to_color_map = {}
        for r in response:
            r_id = OutputData.get_data_type_id(r)
            if r_id == "ipsc":
                colors = IdPassSegmentationColors(r)
                for obj_color_idx in range(colors.get_num_segmentation_colors()):
                    visible_objects.append(colors.get_segmentation_color(obj_color_idx))
            if r_id == "imag":
                images = Images(r)
                image_dir = self.output_dir + "_" + images.get_avatar_id()
                TDWUtils.save_images(images, f"image-{self.idx}",
                                     output_directory=image_dir)
            if r_id == "segm":
                seg_data = SegmentationColors(r)
                for i in range(seg_data.get_num()):
                    if seg_data.get_object_id(i) not in state_data:
                        state_data[seg_data.get_object_id(i)] = {}
                    state_data[seg_data.get_object_id(i)]["segmentation_color"] = seg_data.get_object_color(i)
                    obj_id_to_color_map[seg_data.get_object_id(i)] = seg_data.get_object_color(i)
            if r_id == "tran":
                transform_data = Transforms(r)
                for object_index in range(transform_data.get_num()):

                    if transform_data.get_id(object_index) not in state_data:
                        state_data[transform_data.get_id(object_index)] = {}
                    if transform_data.get_id(object_index) == self.agent_id:
                        self.agent_current_position = transform_data.get_position(object_index)
                    state_data[transform_data.get_id(object_index)].update( {
                        "position": transform_data.get_position(object_index),
                        "rotation": transform_data.get_rotation(object_index)
                    })

            if r_id == "rigi":
                rigid_body_data = Rigidbodies(r)
                for object_index in range(rigid_body_data.get_num()):
                    if rigid_body_data.get_id(object_index) not in state_data:
                        state_data[rigid_body_data.get_id(object_index)] = {}
                    state_data[rigid_body_data.get_id(object_index)].update( {
                        "velocity": rigid_body_data.get_velocity(object_index),
                        "angular_velocity": rigid_body_data.get_angular_velocity(object_index),
                        "force": force
                    })
            if r_id == "boun":
                bounding_box_data = Bounds(r)
                for object_index in range(bounding_box_data.get_num()):
                    if bounding_box_data.get_id(object_index) == self.agent_id:
                        self.agent_bounding_box = {
                    "center": bounding_box_data.get_center(object_index),
                    "top": bounding_box_data.get_top(object_index),
                    "bottom": bounding_box_data.get_bottom(object_index),
                    "back": bounding_box_data.get_back(object_index),
                    "front": bounding_box_data.get_front(object_index),
                    "left": bounding_box_data.get_left(object_index),
                    "right": bounding_box_data.get_right(object_index)
                }
                    if bounding_box_data.get_id(object_index) not in state_data:
                        state_data[bounding_box_data.get_id(object_index)] = {}

                    state_data[bounding_box_data.get_id(object_index)]["bounding_box"] = {
                        "center": bounding_box_data.get_center(object_index),
                        "top": bounding_box_data.get_top(object_index),
                        "bottom": bounding_box_data.get_bottom(object_index),
                        "back": bounding_box_data.get_back(object_index),
                        "front": bounding_box_data.get_front(object_index),
                        "left": bounding_box_data.get_left(object_index),
                        "right": bounding_box_data.get_right(object_index)
                    }
        for visible_object in visible_objects:
            for obj_id_to_color_map_key, obj_id_to_color_map_val in obj_id_to_color_map.items():
                if obj_id_to_color_map_val[0] == visible_object[0] and obj_id_to_color_map_val[1] == visible_object[1] \
                        and obj_id_to_color_map_val[2] == visible_object[2]:
                    visible_objects_.append(obj_id_to_color_map_key)
        state_data[self.agent_id]["visible_objects"] = visible_objects_
        self.agent_state_data.append(state_data)
        self.idx += 1

    def bounce_goal_object(self, agent_state_objects):
        targets = []
        if "target_obj" in agent_state_objects:
            targets.append(agent_state_objects["target_obj"])
        if "target_1_obj" in agent_state_objects:
            targets.append(agent_state_objects["target_1_obj"])
        if "target_2_obj" in agent_state_objects:
            targets.append(agent_state_objects["target_2_obj"])
        for e in targets:
            resp = self.tdw_object.communicate([
                {"$type": "apply_force_to_object",
                 "force": {"x": 0, "y": 3, "z": 0}, "id": e.target_id}
            ])
            self.save_imag(resp)
            for _ in range(50):
                resp = self.tdw_object.communicate({"$type": "do_nothing"})
                self.save_imag(resp)
                print(self.agent_state_data[-1][e.target_id]["position"])
            resp = self.tdw_object.communicate([
                {"$type": "set_kinematic_state", "id": e.target_id, "is_kinematic": True,
                 "use_gravity": False}])

    def bring_down_barrier(self, agent_state_objects):
        obstacles = []
        speed_y = 0.1
        if "obstacle" in agent_state_objects:
            if agent_state_objects["obstacle"] is not None:
                if isinstance(agent_state_objects["obstacle"], Obstacle):
                    if agent_state_objects["obstacle"].obstacle_id is not None:
                        obstacles.append(agent_state_objects["obstacle"])
                elif isinstance(agent_state_objects["obstacle"], BarrierWithDoor):
                    if agent_state_objects["obstacle"].barrier_1 is not None:
                        obstacles.append(agent_state_objects["obstacle"])
        if "obstacle_1" in agent_state_objects:
            if agent_state_objects["obstacle_1"] is not None:
                if isinstance(agent_state_objects["obstacle_1"], Obstacle):
                    if agent_state_objects["obstacle_1"].obstacle_id is not None:
                        obstacles.append(agent_state_objects["obstacle_1"])
                elif isinstance(agent_state_objects["obstacle_1"], BarrierWithDoor):
                    if agent_state_objects["obstacle_1"].barrier_1 is not None:
                        obstacles.append(agent_state_objects["obstacle_1"])
        if "obstacle_2" in agent_state_objects:
            if agent_state_objects["obstacle_2"] is not None:
                if isinstance(agent_state_objects["obstacle_2"], Obstacle):
                    if agent_state_objects["obstacle_2"].obstacle_id is not None:
                        obstacles.append(agent_state_objects["obstacle_2"])
                elif isinstance(agent_state_objects["obstacle_2"], BarrierWithDoor):
                    if agent_state_objects["obstacle_2"].barrier_1 is not None:
                        obstacles.append(agent_state_objects["obstacle_2"])
        obstacles_status = [1 for _ in obstacles]
        for e in obstacles:
            e.actually_create_obstacle()
        while sum(obstacles_status) != 0:
            for i, e in enumerate(obstacles):
                if not agent_state_objects["barrier_falling"]:
                    if isinstance(e, Obstacle):
                        resp = self.tdw_object.communicate({"$type": "teleport_object", "position": e.obstacle_position,
                                                            "id": e.obstacle_id})
                        self.save_imag(resp)
                        obstacles_status[i] = 0
                    elif isinstance(e, BarrierWithDoor):
                        resp = self.tdw_object.communicate([{"$type": "teleport_object", "position": e.center_1,
                                                             "id": e.barrier_1},
                                                            {"$type": "teleport_object", "position": e.center_2,
                                                             "id": e.barrier_2},
                                                            {"$type": "teleport_object", "position": e.center_3,
                                                             "id": e.barrier_3}
                                                            ])
                        self.save_imag(resp)
                        obstacles_status[i] = 0
                else:
                    if isinstance(e, Obstacle):
                        if e.current_position["y"] > e.obstacle_position["y"]:
                            e.current_position["y"] -= speed_y
                            if e.current_position["y"] < e.obstacle_position["y"]:
                                e.current_position["y"] = e.obstacle_position["y"]
                                obstacles_status[i] = 0
                            resp = self.tdw_object.communicate({"$type": "teleport_object", "position": e.current_position,
                                                         "id": e.obstacle_id})
                            self.save_imag(resp)
                    elif isinstance(e, BarrierWithDoor):
                        if e.center_1_current["y"] > e.center_1["y"]:
                            e.center_1_current["y"] -= speed_y
                            e.center_2_current["y"] -= speed_y
                            e.center_3_current["y"] -= speed_y
                            if e.center_1_current["y"] < e.center_1["y"]:
                                e.center_1_current["y"] = e.center_1["y"]
                                e.center_2_current["y"] = e.center_2["y"]
                                e.center_3_current["y"] = e.center_3["y"]
                                obstacles_status[i] = 0
                            resp = self.tdw_object.communicate([{"$type": "teleport_object",
                                                                 "position": e.center_1_current,
                                                                 "id": e.barrier_1},
                                                                {"$type": "teleport_object",
                                                                 "position": e.center_2_current,
                                                                 "id": e.barrier_2},
                                                                {"$type": "teleport_object",
                                                                 "position": e.center_3_current,
                                                                 "id": e.barrier_3}
                                                                ])
                            self.save_imag(resp)

    def quaternion_to_euler_angle_vectorized(self, w, x, y, z):
        ysqr = y * y

        t0 = +2.0 * (w * x + y * z)
        t1 = +1.0 - 2.0 * (x * x + ysqr)
        X = np.degrees(np.arctan2(t0, t1))

        t2 = +2.0 * (w * y - z * x)
        t2 = np.where(t2 > +1.0, +1.0, t2)
        # t2 = +1.0 if t2 > +1.0 else t2

        t2 = np.where(t2 < -1.0, -1.0, t2)
        # t2 = -1.0 if t2 < -1.0 else t2
        Y = np.degrees(np.arcsin(t2))

        t3 = +2.0 * (w * z + x * y)
        t4 = +1.0 - 2.0 * (ysqr + z * z)
        Z = np.degrees(np.arctan2(t3, t4))

        return X, Y, Z

    def quaternion_to_euler(self, q):
        (x, y, z, w) = (q[0], q[1], q[2], q[3])
        t0 = +2.0 * (w * x + y * z)
        t1 = +1.0 - 2.0 * (x * x + y * y)
        roll = math.atan2(t0, t1)
        t2 = +2.0 * (w * y - z * x)
        t2 = +1.0 if t2 > +1.0 else t2
        t2 = -1.0 if t2 < -1.0 else t2
        pitch = math.asin(t2)
        t3 = +2.0 * (w * z + x * y)
        t4 = +1.0 - 2.0 * (y * y + z * z)
        yaw = math.atan2(t3, t4)
        return [math.degrees(yaw), math.degrees(pitch), math.degrees(roll)]

    def quaternion_to_euler_(self, w, x, y, z):
        """Converts quaternions with components w, x, y, z into a tuple (roll, pitch, yaw)"""
        sinr_cosp = 2 * (w * x + y * z)
        cosr_cosp = 1 - 2 * (x ** 2 + y ** 2)
        roll = np.arctan2(sinr_cosp, cosr_cosp)

        sinp = 2 * (w * y - z * x)
        pitch = np.where(np.abs(sinp) >= 1,
                         np.sign(sinp) * np.pi / 2,
                         np.arcsin(sinp))

        siny_cosp = 2 * (w * z + x * y)
        cosy_cosp = 1 - 2 * (y ** 2 + z ** 2)
        yaw = np.arctan2(siny_cosp, cosy_cosp)
        return roll, pitch, yaw

    def find_first_angle(self, rotation_list, positions_list):
        angle = 0
        pre_angle = deque(maxlen=3)
        for i, rot in enumerate(rotation_list):
            pre_angle.append(angle)
            angle = self.quaternion_to_euler_angle_vectorized(rot[3], rot[0], rot[1], rot[2])[1]
            if len(pre_angle) == 3:
                if pre_angle[0] == pre_angle[1] == pre_angle[2]:
                    to_return_anlge = pre_angle[0]
                    return to_return_anlge, i

        return None

    def move_agent(self, position):
        cmd = [
            {"$type": "teleport_object", "position": position, "id": self.agent_id},
        ]
        return cmd

    def change_agent_angle(self, rotation):
        cmd = [
            {"$type": "rotate_object_to", "rotation": {"w": rotation[3], "x": rotation[0],
                                                       "y": rotation[1], "z": rotation[2]},
             "id": self.agent_id}
        ]
        return cmd

    def follow_agent(self, cmd):
        if self.args.follow_camera:
            cmd.append(
                {"$type": "follow_object", "object_id": self.agent_id, "position": {"x": 0, "y": 0.2, "z": 0},
                 "rotation": True, "avatar_id": "agent_follow_camera"}
            )
        return cmd

    def replay_agent(self, look_around=False, agent_state_objects=None, do_nothing=False, scene_3_4=False,
                     path_type="Jump", target_positions=None):
        plain_object_offset = 0.1019
        idx = 0
        replay_order = []
        # temp
        prev_pos = None
        angle_matched, angle_changed, angle_matched_complete = False, False, False
        angle_1, angle_2 = agent_state_objects["angle_1"], agent_state_objects["angle_2"]
        unit_rotation = 5
        rotated_angle = 0
        if not scene_3_4 and path_type not in ["Jump", "Straight-Target"]:
            target_angle, match_angle_index = self.find_first_angle(self.agent_rotations, self.agent_positions)
            difference_in_angle = target_angle - angle_1
            direction = -1 if target_angle > 0 else 1
            current_angle = angle_1
        def agent_wait(counter):
            for wait_iter in range(counter):
                resp = self.tdw_object.communicate({"$type": "do_nothing"})
                self.save_imag(resp)
        for pos, rot, force in zip(self.agent_positions, self.agent_rotations, self.forces):
            # pos["y"] -= plain_object_offset

            if idx == 1:
                # self.bounce_goal_object(agent_state_objects)
                if look_around:
                    self.rotate_agent(angle_1)
                    replay_order = self.tilt_agent(target_positions[0])
                    agent_wait(10)
                    self.replay_tilt(replay_order)
                    agent_wait(5)
                    self.rotate_agent(-1 * angle_1)
                    agent_wait(20)
                    self.rotate_agent(angle_2)
                    replay_order = self.tilt_agent(target_positions[1])
                    agent_wait(10)
                    self.replay_tilt(replay_order)
                    agent_wait(5)
                    self.rotate_agent(-1* angle_2)
                elif do_nothing or not scene_3_4:
                    self.rotate_agent(angle_1)
                    # Tilt up
                    replay_order = self.tilt_agent(target_positions[0])
                    agent_wait(10)
                # Bring down barriers
                self.bring_down_barrier(agent_state_objects)
                agent_wait(35)
                if look_around and agent_state_objects["look_around_twice"]:
                    self.rotate_agent(angle_1)
                    replay_order = self.tilt_agent(target_positions[0])
                    agent_wait(10)
                    self.replay_tilt(replay_order)
                    agent_wait(5)
                    self.rotate_agent(-1 * angle_1)
                    agent_wait(20)
                    self.rotate_agent(angle_2)
                    replay_order = self.tilt_agent(target_positions[1])
                    agent_wait(10)
                    self.replay_tilt(replay_order)
                    agent_wait(5)
                    self.rotate_agent(-1* angle_2)
                if do_nothing or not scene_3_4:
                    # Look back
                    self.replay_tilt(replay_order)
                    if do_nothing:
                        self.rotate_agent(-1 * angle_1)
                        agent_wait(20)
                        return
            cmd = self.move_agent(pos)
            # The agent is already turned so wait until the pre-cooked angles are same as current angle and then
            # rotate it
            if not scene_3_4:
                if not angle_changed and idx > 0 and path_type not in ["Jump", "Straight-Target"]:
                    angle = direction * min(abs(difference_in_angle - rotated_angle), unit_rotation)
                    rotated_angle += angle
                    angle_ = angle
                    if self.agent_positions[1]["z"] > self.agent_positions[20]["z"]:
                        if self.agent_positions[1]["x"] > self.agent_positions[20]["x"]:
                            if angle_ > 0:
                                angle_ = -1*angle_
                        else:
                            if angle_ < 0:
                                angle_ = -1*angle_
                    else:
                        if self.agent_positions[1]["x"] > self.agent_positions[20]["x"]:
                            if angle_ < 0:
                                angle_ = -1*angle_
                        else:
                            if angle_ > 0:
                                to_return_anlge = -1 * to_return_anlge
                    current_angle = current_angle + angle_
                    if abs(difference_in_angle) <= abs(rotated_angle):
                        angle_changed = True
                    rot_angle = euler_to_quaternion(0, convert_to_radians(current_angle), 0)
                    if angle_changed:
                        current_angle = target_angle
                    # print(angle, angle_, current_angle, target_angle, difference_in_angle)
                    cmd.extend(self.change_agent_angle(rot_angle))

                if angle_changed and not angle_matched:
                    if (abs(abs(self.quaternion_to_euler_angle_vectorized(rot[3], rot[0], rot[1], rot[2])[1]) - abs(
                            current_angle)) < 2) and idx >= match_angle_index:
                        angle_matched = True

                if angle_matched and path_type not in ["Jump", "Straight-Target"]:
                    cmd.extend(self.change_agent_angle(rot))
            else:
                cmd.extend(self.change_agent_angle(rot))
            cmd = self.follow_agent(cmd)
            resp = self.tdw_object.communicate(cmd)
            self.save_imag(resp, force)
            idx += 1

    def reset(self):
        self.agent_positions = []
        self.agent_position = self.agent_start_position.copy()
        self.agent_rotations = []
        self.agent_angular_velocities = []
        self.agent_velocities = []
        self.agent_rotation = {"x": 0, "y": 0, "z": 0}
        utils.teleport(self.tdw_object, self.agent_position, self.agent_id)
        utils.rotate_object(self.tdw_object, rotation_angle=self.agent_rotation, obj_id=self.agent_id)
        self.idx = 0
        self.path_no += 1
        self.agent_angle = 0
        self.output_dir = os.path.join(self.base_dir, f"path_{self.path_no}", "images")

    def look_at_goal(self, target_pos):

        vector_to_target = np.array([target_pos["x"] - self.agent_position["x"],
                                   target_pos["z"] - self.agent_position["z"]])
        vector_to_target = vector_to_target/np.linalg.norm(vector_to_target)
        view_vector = np.array([0, 1])
        angle = -1*round(abs(math.degrees(np.arccos(np.dot(view_vector, vector_to_target)))))
        self.direction = 1
        for i in range(0, angle, self.direction * -2):
            self.agent_rotation = {"x": 0, "y": i, "z": 0}
            qo = euler_to_quaternion(0, convert_to_radians(i), 0)
            resp = self.tdw_object.communicate(
                {"$type": "rotate_object_to", "rotation": {"w": qo[3], "x": qo[0], "y": qo[1], "z": qo[2]},
                 "id": self.agent_id})

            self.save_imag(resp)

    def look_at_goal_(self):
        df = 3
        vector_to_target = np.array([self.target_pos["x"] - self.agent_position["x"],
                                     self.target_pos["z"] - self.agent_position["z"]])
        vector_to_target = vector_to_target / np.linalg.norm(vector_to_target)
        angle = -1 * round(abs(math.degrees(np.arccos(np.dot(self.view_vector, vector_to_target)))))

        self.direction = 1
        idx = 0
        if abs(angle) <=2:
            return
        for i in range(self.angle, self.angle + angle, self.direction * -2):
            self.agent_rotation = {"x": 0, "y": i, "z": 0}
            qo = euler_to_quaternion(0, convert_to_radians(i), 0)
            resp = self.tdw_object.communicate(
                {"$type": "rotate_object_to", "rotation": {"w": qo[3], "x": qo[0], "y": qo[1], "z": qo[2]},
                 "id": self.agent_id})
            self.view_vector = utils.rotate_point(origin=(0, 0), point=(self.view_vector[0], self.view_vector[1]), angle=math.radians(-1 * i))
            print(-1 * round(abs(math.degrees(np.arccos(np.dot(self.view_vector, vector_to_target))))))
            self.save_imag(resp)
            idx += 1
            if idx > 2:
                self.angle += 3*(self.direction * -2)
                return

    def settle_drop_object(self, n=100):
        for i in range(n):
            resp = self.tdw_object.communicate({"$type": "do_nothing"})
            self.save_imag(resp)

    def reveal_occluder(self, occluder):

        resp = self.tdw_object.communicate(
            {"$type": "apply_force", "origin": {"x": occluder.occluder_position["x"] - 0.5*occluder.reveal_normal[0],
                        "y": 0.55, "z": occluder.occluder_position["z"] - 0.5*occluder.reveal_normal[2]},
             "target": {"x": occluder.occluder_position["x"] + 0.5*occluder.reveal_normal[0],
                        "y": 0.55, "z": occluder.occluder_position["z"] + 0.5*occluder.reveal_normal[2]},
             "magnitude": 2})

        self.save_imag(resp)
        self.settle_drop_object(n=92)


