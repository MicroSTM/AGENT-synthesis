from util.utils import euler_to_quaternion, convert_to_radians
import os
from tdw.tdw_utils import TDWUtils
from tdw.output_data import Images, OutputData, Transforms, Rigidbodies, Bounds, SegmentationColors
import math
import numpy as np
from util import utils
from util.jump import jump as jump_forces_list


class Agent:
    def __init__(self, tdw_object, direction, out_dir):
        self.tdw_object = tdw_object
        self.direction = direction
        self.idx = 0
        self.path_no = 1
        self.output_dir = os.path.join(out_dir, f"path_{self.path_no}")
        self.base_dir = out_dir
        self.agent_positions = []
        self.agent_position = None
        self.agent_rotations = []
        self.agent_velocities = []
        self.total_force = [0, 0, 0]
        self.forces = []
        self.state_data = []
        self.agent_start_position = None
        self.agent_angle = 0
        self.view_vector = [0, 1]
        self.image_data = {}
        self.agent_state = {
            "velocity": [0, 0, 0]
        }
        self.agent_state_data = []

    def reset(self):
        self.stop_agent()
        utils.teleport(self.tdw_object, self.agent_start_position, self.agent_id)
        utils.rotate_object(self.tdw_object, {"x": 0, "y": 0, "z": 0}, self.agent_id)
        self.agent_positions = []
        self.agent_position = self.agent_start_position.copy()
        self.agent_rotations = []
        self.agent_velocities = []
        self.state_data = []
        self.agent_rotation = {"x": 0, "y": 0, "z": 0}
        self.total_force = [0, 0, 0]
        self.forces = []
        self.view_vector = [0, 1]
        self.agent_angle = 0
        self.idx = 0
        self.path_no += 1
        self.image_data = {}
        self.agent_state_data = []
        self.output_dir = os.path.join(self.base_dir, f"path_{self.path_no}")

    def calculate_angle(self, position):
        vect_to_target = [position[0] - self.agent_position["x"],
                          position[1] - self.agent_position["z"]]
        vect_to_target = vect_to_target/np.linalg.norm(vect_to_target)
        angle = np.degrees(np.math.atan2(np.linalg.det([self.view_vector, vect_to_target]), np.dot(self.view_vector, vect_to_target)))
        self.view_vector = vect_to_target
        angle = -1*int(round(angle))
        return angle

    def create_agent_new(self, position, color, agent_name):
        selected_color = color
        # agent_name = "cone"
        # agent_name = available_agents[random.randint(0, len(available_agents) - 1)]
        url = "file:///" + os.path.join(os.getcwd(), "../agent_models", agent_name.title(), "StandaloneOSX",
                                        agent_name)
        # url = f"file:///agent_model/{agent_name.title()}/StandaloneLinux64/{agent_name}"
        self.agent_id = self.tdw_object.get_unique_id()
        self.agent_start_position = position.copy()
        self.agent_position = position
        self.agent_rotation = {"x": 0, "y": 0, "z": 0}
        # self.tdw_object.communicate({"$type": "add_object",
        #                              "name": "cone",
        #                              "url": url,
        #                              "scale_factor": 1,
        #                              "id": self.agent_id,
        #                              "position": position})
        self.agent_id = self.tdw_object.add_object("prim_cone", position=self.agent_position, rotation=self.agent_rotation,
                                   library="models_special.json")
        resp = self.tdw_object.communicate([
            {"$type": "scale_object", "scale_factor": {"x": 0.2, "y": 0.2, "z": 0.2}, "id": self.agent_id},
            {"$type": "set_color_in_substructure",
             "color": selected_color,
             "object_name": "prim_cone", "id": self.agent_id},
            {"$type": "set_mass", "id": self.agent_id, "mass": 1.0},
            {"$type": "step_physics", "frames": 10},
            {"$type": "set_physic_material", "dynamic_friction": 0.0, "static_friction": 0.0, "bounciness": 0.125,
             "id": self.agent_id},
            {"$type": "set_object_drag", "id": self.agent_id, "drag": 0, "angular_drag": 100}
        ])
        return

    def look_at_goal(self):
        for i in range(0, self.direction * -90, self.direction * -2):
            qo = euler_to_quaternion(0, convert_to_radians(i), 0)
            resp = self.tdw_object.communicate(
                {"$type": "rotate_object_to", "rotation": {"w": qo[3], "x": qo[0], "y": qo[1], "z": qo[2]},
                 "id": self.agent_id})

            self.forces.append({"x": 0.0, "y": 0.0, "z": 0.0})
            self.save_imag(resp)
            self.agent_angle = i

    def rotate_by_angle(self, angle):
        ang = 0
        return
        direction = 1 if angle < 0 else -1
        for i in range(self.agent_angle, self.agent_angle + angle, direction * -5):
            qo = euler_to_quaternion(0, convert_to_radians(i), 0)
            resp = self.tdw_object.communicate(
                {"$type": "rotate_object_to", "rotation": {"w": qo[3], "x": qo[0], "y": qo[1], "z": qo[2]},
                 "id": self.agent_id})

            self.forces.append({"x": 0.0, "y": 0.0, "z": 0.0})
            self.save_imag(resp)
            ang = i
        self.agent_angle = ang

    def look_back(self):
        for i in range(self.direction * -90, 0, self.direction * 2):
            self.agent_rotation = {"x": 0, "y": i, "z": 0}

            qo = euler_to_quaternion(0, convert_to_radians(i), 0)
            resp = self.tdw_object.communicate(
                {"$type": "rotate_object_to", "rotation": {"w": qo[3], "x": qo[0], "y": qo[1], "z": qo[2]},
                 "id": self.agent_id})
            self.forces.append({"x": 0.0, "y": 0.0, "z": 0.0})
            self.save_imag(resp)

    def get_agent_loc_vel(self, response, get_x=True, both=False, send_rotation=False):
        velocity, position = None, None
        for r in response:
            r_id = OutputData.get_data_type_id(r)
            if r_id == "tran":
                transform_data = Transforms(r)
                for object_index in range(transform_data.get_num()):
                    if transform_data.get_id(object_index) == self.agent_id:
                        pos = transform_data.get_position(object_index)
                        position = {"x": pos[0], "y": pos[1], "z": pos[2]}
                        rotation = transform_data.get_rotation(object_index)
            if r_id == "rigi":
                rigid_body_data = Rigidbodies(r)
                for object_index in range(rigid_body_data.get_num()):
                    if rigid_body_data.get_id(object_index) == self.agent_id:
                        if both:
                            velocity = (rigid_body_data.get_velocity(object_index)[0],
                                        rigid_body_data.get_velocity(object_index)[1],
                                        rigid_body_data.get_velocity(object_index)[2])
                        elif get_x:
                            velocity = rigid_body_data.get_velocity(object_index)[0]
                        else:
                            velocity = rigid_body_data.get_velocity(object_index)[2]

        if send_rotation:
            return velocity, position, rotation
        else:
            return velocity, position

    def save_imag(self, response):
        state_data = {}
        for r in response:
            r_id = OutputData.get_data_type_id(r)
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
            if r_id == "tran":
                transform_data = Transforms(r)
                for object_index in range(transform_data.get_num()):
                    if transform_data.get_id(object_index) not in state_data:
                        state_data[transform_data.get_id(object_index)] = {}
                    state_data[transform_data.get_id(object_index)].update({
                        "position": transform_data.get_position(object_index),
                        "rotation": transform_data.get_rotation(object_index)
                    })
                    if transform_data.get_id(object_index) == self.agent_id:
                        pos = transform_data.get_position(object_index)
                        self.agent_position = {"x": pos[0], "y": pos[1], "z": pos[2]}
                        self.agent_rotation = transform_data.get_rotation(object_index)
            if r_id == "rigi":
                rigid_body_data = Rigidbodies(r)
                for object_index in range(rigid_body_data.get_num()):
                    if rigid_body_data.get_id(object_index) == self.agent_id:
                        self.agent_state["velocity"] = (rigid_body_data.get_velocity(object_index)[0],
                                                        rigid_body_data.get_velocity(object_index)[1],
                                                        rigid_body_data.get_velocity(object_index)[2])
                    if rigid_body_data.get_id(object_index) not in state_data:
                        state_data[rigid_body_data.get_id(object_index)] = {}
                    state_data[rigid_body_data.get_id(object_index)].update({
                        "velocity": rigid_body_data.get_velocity(object_index),
                        "angular_velocity": rigid_body_data.get_angular_velocity(object_index)
                    })

            if r_id == "boun":
                bounding_box_data = Bounds(r)
                for object_index in range(bounding_box_data.get_num()):
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

        self.agent_state_data.append(state_data)
        self.idx += 1

    def stop_agent(self):
        self.agent_state["velocity"] = [0, 0, 0]
        return self.tdw_object.communicate(
            [{"$type": "set_object_drag", "id": self.agent_id, "drag": 100, "angular_drag": 100},
             {"$type": "step_physics", "frames": 1},
             {"$type": "set_object_drag", "id": self.agent_id, "drag": 0, "angular_drag": 100}
             ])

    def approach(self, till_x=None, till_y=None, till_z=None, approach_dist=0.01, speed_threshold=1.3, rotation=0):
        speed = 0
        force_magnitude = 0.8
        distance_to_travel = 10000
        rotated_angle = 0
        unit_rotation = 5

        if till_x is not None and till_y is not None and till_z is not None:
            total_force = [0, 0, 0]
            while True:
                # Find the required velocity
                # vect_to_target = np.array((-self.agent_position["x"] + till_x, -self.agent_position["y"] + till_y,
                #                            -self.agent_position["z"] + till_z))
                # v_hat_ = vect_to_target / np.linalg.norm(vect_to_target)
                #
                # v_hat = [v_hat_[0] * speed_threshold - self.agent_state["velocity"][0],
                #          v_hat_[1] * speed_threshold - self.agent_state["velocity"][1],
                #          v_hat_[2] * speed_threshold - self.agent_state["velocity"][2]]
                # force_applied = {"x": v_hat[0], "y": v_hat[1], "z": v_hat[2]}
                # # Calculate Rotation
                # direction = 1 if rotation - rotated_angle > 0 else -1
                # angle = direction * min(abs(rotation - rotated_angle), unit_rotation)
                # rotated_angle += angle
                # self.agent_angle += angle
                # qo = euler_to_quaternion(0, convert_to_radians(self.agent_angle), 0)
                #
                # total_force = [e + abs(force_applied[f]) for e, f in zip(total_force, ["x", "y", "z"])]
                # self.forces.append(force_applied.copy())
                # self.total_force = [e + abs(force_applied[f]) for e, f in zip(self.total_force, ["x", "y", "z"])]
                # resp = self.tdw_object.communicate(
                #     [{"$type": "apply_force_to_object", "force": force_applied.copy(),
                #       "id": self.agent_id},
                #      {"$type": "rotate_object_to", "rotation": {"w": qo[3], "x": qo[0], "y": qo[1], "z": qo[2]},
                #       "id": self.agent_id}
                #      ]
                # )
                # self.save_imag(resp)
                # velocity, _ = self.get_agent_loc_vel(resp, both=True)
                #
                # distance_to_travel = math.sqrt(
                #     (till_x - self.agent_position["x"]) ** 2 + (till_y - self.agent_position["y"]) ** 2
                #     + (till_z - self.agent_position["z"]) ** 2
                # )
                # new_vect = np.array((-self.agent_position["x"] + till_x, -self.agent_position["y"] + till_y,
                #                      -self.agent_position["z"] + till_z))
                # new_vect = new_vect / np.linalg.norm(new_vect)
                # if distance_to_travel < approach_dist or np.dot(new_vect, v_hat_) < 0:
                #     break
                # Calculate Rotation
                # direction = 1 if rotation - rotated_angle > 0 else -1
                # angle = direction * min(abs(rotation - rotated_angle), unit_rotation)
                # rotated_angle += angle
                # self.agent_angle += angle
                # qo = euler_to_quaternion(0, convert_to_radians(self.agent_angle), 0)
                if speed < speed_threshold:
                    vect_to_target = np.array((-self.agent_position["x"] + till_x,
                                               -self.agent_position["y"] + till_y,
                                               -self.agent_position["z"] + till_z))
                    v_hat = vect_to_target / np.linalg.norm(vect_to_target)
                    v_hat_ = [v_hat[0] * speed_threshold, v_hat[1] * speed_threshold, v_hat[2] * speed_threshold]
                    v_hat = [v_hat_[0] * speed_threshold - self.agent_state["velocity"][0],
                             v_hat_[1] * speed_threshold - self.agent_state["velocity"][1],
                             v_hat_[2] * speed_threshold - self.agent_state["velocity"][2],
                             ]
                    force_applied = {"x": v_hat[0], "y": v_hat[1], "z": v_hat[2]}
                    self.total_force = [e + abs(force_applied[f]) for e, f in
                                        zip(self.total_force, ["x", "y", "z"])]
                    resp = self.tdw_object.communicate(
                        [{"$type": "apply_force_to_object",
                          "force": force_applied.copy(),
                          "id": self.agent_id}
                         # {"$type": "rotate_object_to", "rotation": {"w": qo[3], "x": qo[0], "y": qo[1], "z": qo[2]},
                         #  "id": self.agent_id}
                         ]
                    )
                else:
                    resp = self.tdw_object.communicate([{"$type": "do_nothing"}
                                                        ])
                    force_applied = {"x": 0, "y": 0.0, "z": 0}

                velocity, _ = self.get_agent_loc_vel(resp, both=True)
                velocity_x, velocity_y, velocity_z = velocity[0], velocity[1], velocity[2]
                speed = math.sqrt(velocity_x ** 2 + velocity_y ** 2 + velocity_z ** 2)
                previous_distance = distance_to_travel
                distance_to_travel = math.sqrt(
                    (till_x - self.agent_position["x"]) ** 2 + (till_z - self.agent_position["z"]) ** 2
                )
                if distance_to_travel < approach_dist or previous_distance < distance_to_travel:
                    resp = self.stop_agent()
                    self.forces.append({"x": -1 * velocity_x, "y": 0.0, "z": -1 * velocity_z})
                    self.save_imag(resp)
                    break
                else:
                    self.save_imag(resp)
                    self.forces.append(force_applied.copy())

        elif till_x is not None and till_z is not None:

            total_force = [0, 0, 0]
            while True:
                # Find the required velocity
                vect_to_target = np.array((-self.agent_position["x"] + till_x, -self.agent_position["z"] + till_z))
                v_hat_ = vect_to_target / np.linalg.norm(vect_to_target)
                v_hat = [v_hat_[0]*speed_threshold - self.agent_state["velocity"][0], v_hat_[1]*speed_threshold - self.agent_state["velocity"][2]]
                force_applied = {"x": v_hat[0], "y": 0.0, "z": v_hat[1]}
                # Calculate Rotation
                direction = 1 if rotation - rotated_angle > 0 else -1
                angle = direction * min(abs(rotation - rotated_angle), unit_rotation)
                rotated_angle += angle
                self.agent_angle += angle
                qo = euler_to_quaternion(0, convert_to_radians(self.agent_angle), 0)

                total_force = [e + abs(force_applied[f]) for e, f in zip(total_force, ["x", "y", "z"])]
                self.forces.append(force_applied.copy())
                self.total_force = [e + abs(force_applied[f]) for e, f in zip(self.total_force, ["x", "y", "z"])]
                resp = self.tdw_object.communicate(
                    [{"$type": "apply_force_to_object", "force": force_applied.copy(),
                      "id": self.agent_id},
                     {"$type": "rotate_object_to", "rotation": {"w": qo[3], "x": qo[0], "y": qo[1], "z": qo[2]},
                      "id": self.agent_id}
                     ]
                )
                self.save_imag(resp)
                velocity, _ = self.get_agent_loc_vel(resp, both=True)

                distance_to_travel = math.sqrt(
                    (till_x - self.agent_position["x"])**2 + (till_z - self.agent_position["z"])**2
                )
                new_vect = np.array((-self.agent_position["x"] + till_x, -self.agent_position["z"] + till_z))
                new_vect = new_vect/np.linalg.norm(new_vect)
                if distance_to_travel < approach_dist or np.dot(new_vect, v_hat_) < 0:
                    break
        elif till_x is not None:
            force = self.direction * -force_magnitude
            while True:
                if abs(speed) < speed_threshold:
                    self.total_force[0] += force_magnitude
                    self.forces.append({"x": force, "y": 0.0, "z": 0})
                    resp = self.tdw_object.communicate(
                        {"$type": "apply_force_to_object", "force": {"x": force, "y": 0.0, "z": 0}, "id": self.agent_id})
                else:
                    resp = self.tdw_object.communicate({"$type": "do_nothing"})
                    self.forces.append({"x": 0, "y": 0.0, "z": 0})
                speed, _ = self.get_agent_loc_vel(resp)
                self.save_imag(resp)
                distance_to_travel = abs(till_x - self.agent_position["x"])
                if distance_to_travel < 0.01:
                    resp = self.tdw_object.communicate([{"$type": "set_object_drag", "id": self.agent_id, "drag": 100, "angular_drag": 100},
                                                 {"$type": "step_physics", "frames": 1},
                                                 {"$type": "set_object_drag", "id": self.agent_id, "drag": 0, "angular_drag": 100},
                                                 {"$type": "teleport_object", "position": {"x": till_x, "y": self.agent_position["y"], "z": self.agent_position["z"]}, "id": self.agent_id}])
                    self.save_imag(resp)
                    self.forces.append({"x": -1*speed, "y": 0.0, "z": 0})
                    break

        elif till_z is not None:
            force = force_magnitude if till_z > self.agent_position["z"] else -force_magnitude
            while True:
                if abs(speed) < speed_threshold:
                    self.total_force[2] += force_magnitude
                    self.forces.append({"x": 0.0, "y": 0.0, "z": force})
                    resp = self.tdw_object.communicate(
                        {"$type": "apply_force_to_object", "force": {"x": 0.0, "y": 0.0, "z": force}, "id": self.agent_id})
                else:
                    resp = self.tdw_object.communicate({"$type": "do_nothing"})
                    self.forces.append({"x": 0.0, "y": 0.0, "z": 0.0})
                speed, _ = self.get_agent_loc_vel(resp, get_x=False)
                self.save_imag(resp)
                distance_to_travel = abs(till_z - self.agent_position["z"])
                if distance_to_travel < 0.01:
                    resp = self.tdw_object.communicate([{"$type": "set_object_drag", "id": self.agent_id, "drag": 100, "angular_drag": 100},
                                                 {"$type": "step_physics", "frames": 1},
                                                 {"$type": "set_object_drag", "id": self.agent_id, "drag": 0, "angular_drag": 100},
                                                 {"$type": "teleport_object",
                                                  "position": {"x": self.agent_position["x"],
                                                               "y": self.agent_position["y"],
                                                               "z": till_z},
                                                  "id": self.agent_id}])
                    self.forces.append({"x": 0, "y": 0.0, "z": -1*speed})
                    self.save_imag(resp)
                    break

    def settle_drop_object(self, n=100, stop_at_base=False, ground_height=0.11, residual_force=None):
        for i in range(n):
            resp = self.tdw_object.communicate({"$type": "do_nothing"})
            self.save_imag(resp)
            if i == 0 and residual_force is not None:
                self.forces.append(residual_force)
            else:
                self.forces.append({"x": 0, "y": 0, "z": 0})
            speed = np.linalg.norm(self.agent_state["velocity"])
            if speed < 0.01:
                return
            if self.agent_position["y"] <= 1.01*ground_height and stop_at_base and i > 10:
                # breaking_force = [abs(e) for e in self.agent_state["velocity"]]
                # resp = self.stop_agent()
                # self.save_imag(resp)
                # self.forces.append({"x": breaking_force[0], "y": 0, "z": breaking_force[2]})
            #     print(i)
            #     exit()
            #     # self.forces[-1] = {"x": breaking_force[0], "y": 0, "z": breaking_force[2]}
                return

    def jump(self, height, width, direction_x_z=(1, 0), hight_ground_height=None):

        breaking_force = [abs(e) for e in self.agent_state["velocity"]]
        self.forces.append({"x": breaking_force[0], "y": breaking_force[1], "z": breaking_force[2]})
        self.save_imag(self.stop_agent())

        ground_height = self.agent_position["y"] if hight_ground_height is None else hight_ground_height
        jump_forces_list_obj = jump_forces_list(direction=self.direction, direction_x_z=direction_x_z)
        force_vect = jump_forces_list_obj.get_jump_force(self.agent_state["velocity"], height, width)

        resp = self.tdw_object.communicate(
                        {"$type": "apply_force_to_object", "force": {"x": force_vect[0], "y": force_vect[1], "z": force_vect[2]}, "id": self.agent_id})
        self.forces.append({"x": force_vect[0], "y": force_vect[1], "z": force_vect[2]})
        self.save_imag(resp)

        self.settle_drop_object(ground_height=ground_height, stop_at_base=True, n=200)
        self.total_force = [e + abs(f) for e, f in zip(self.total_force, force_vect)]


    def reveal_occluder(self, occluder):
        resp = self.tdw_object.communicate(
            {"$type": "apply_force", "origin": {"x": occluder.occluder_position["x"] - 0.5 * occluder.reveal_normal[0],
                                                "y": 0.55,
                                                "z": occluder.occluder_position["z"] - 0.5 * occluder.reveal_normal[2]},
             "target": {"x": occluder.occluder_position["x"] + 0.5 * occluder.reveal_normal[0],
                        "y": 0.55, "z": occluder.occluder_position["z"] + 0.5 * occluder.reveal_normal[2]},
             "magnitude": 2}
        )
        self.save_imag(resp)
        for i in range(92):
            resp = self.tdw_object.communicate({"$type": "do_nothing"})
