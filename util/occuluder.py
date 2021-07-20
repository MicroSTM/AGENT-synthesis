from util import utils
from util.utils import SceneConfiguration
import numpy as np
import util.trajectory_generation

class Occluder:
    def __init__(self, camera_obj, obstacle, pit=False):
        self.scene_config = SceneConfiguration()
        self.camera_obj = camera_obj
        self.obstacle = obstacle
        self.reveal_normal = []
        self.calculate_occuluder_properties(pit)

    def y_rotation(self, vector, theta):
        """Rotates 3-D vector around y-axis"""
        R = np.array([[np.cos(theta), 0, np.sin(theta)], [0, 1, 0], [-np.sin(theta), 0, np.cos(theta)]])
        return np.dot(R, vector)

    def calculate_occuluder_properties(self, pit=False):
        camera_pos = self.camera_obj.current_position.copy()
        camera_rot = self.camera_obj.current_rotation.copy()

        # Find center of obstacle
        front_right_point = np.array([
            self.obstacle.obstacle_position["x"] - self.obstacle.obstacle_width/2,
            self.obstacle.obstacle_position["y"] + self.obstacle.obstacle_height/2,
            self.obstacle.obstacle_position["z"] + self.obstacle.obstacle_depth / 2
        ])
        back_left_point = np.array([
            self.obstacle.obstacle_position["x"] + self.obstacle.obstacle_width / 2,
            self.obstacle.obstacle_position["y"] - self.obstacle.obstacle_height / 2,
            self.obstacle.obstacle_position["z"] - self.obstacle.obstacle_depth / 2
        ])
        back_right_point = np.array([
            self.obstacle.obstacle_position["x"] - self.obstacle.obstacle_width / 2,
            self.obstacle.obstacle_position["y"] + self.obstacle.obstacle_height / 2,
            self.obstacle.obstacle_position["z"] - self.obstacle.obstacle_depth / 2
        ])

        normal_vect = self.y_rotation(np.array([0, 0, 1]), np.radians(camera_rot["y"]))
        normal_vect_normal = self.y_rotation(normal_vect, np.radians(-90))
        self.reveal_normal = -1*normal_vect
        projected_point = np.array([
            [front_right_point[0] + 5 * normal_vect_normal[0], front_right_point[2] + 5 * normal_vect_normal[2]],
            [front_right_point[0], front_right_point[2]]
        ])
        p = trajectory_generation.line_intersection(
            projected_point,
            [
                [camera_pos["x"], camera_pos["z"]],
                [back_left_point[0], back_left_point[2]],
            ]
        )
        vect_to_target = np.array([
            (p[0] + front_right_point[0]) / 2 - camera_pos["x"],
            (p[1] + front_right_point[2]) / 2 - camera_pos["z"]
        ])
        vect_to_target = vect_to_target/np.linalg.norm(vect_to_target)
        self.occluder_position = {
            "x": camera_pos["x"] + vect_to_target[0],
            "y": 0,
            "z": camera_pos["z"] + vect_to_target[1]
        }
        dist = utils.distance_of_point_from_line(np.array([camera_pos["x"], camera_pos["z"]]),
                                                 np.array([front_right_point[0], front_right_point[2]]),
                                                 np.array([self.occluder_position["x"], self.occluder_position["z"]]))

        height = trajectory_generation.line_intersection(
            [
                [camera_pos["y"], camera_pos["z"]],
                [back_right_point[1], back_right_point[2]]
            ],
            [
                [self.occluder_position["y"], self.occluder_position["z"]],
                [self.occluder_position["y"] + 5*1, self.occluder_position["z"]],
            ]
        )[0]
        x_correction = 0.023
        self.occluder_position["y"] = height/2
        self.occluder_position["y"] += 0 if not pit else 1.009
        self.scale = {"x": 2*dist + x_correction, "y": height, "z": 0.01}
        self.occluder_rotation = {"x":0, "y":camera_rot["y"], "z":0}
        print(self.occluder_position)


    def create(self, tdw_object):
        self.occluder_id = utils.create_occluder(tdw_object, self.occluder_position, self.scale, self.occluder_rotation)

        # tdw_object.communicate(
        #     {"$type": "set_kinematic_state", "id": self.occluder_id, "is_kinematic": True,
        #      "use_gravity": False}
        # )