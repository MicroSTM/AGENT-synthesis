import random


class Obstacle:
    def __init__(self, tdw_object, position, height, width, rotation={"x": 0, "y": 0, "z": 0}, depth=2.7, door_depth=None, config_file=None):
        self.tdw_object = tdw_object
        self.obstacle_height = height
        self.obstacle_width = width
        self.obstacle_depth = depth
        self.obstacle_position = position
        self.obstacle_id = None
        self.current_position = None
        self.obstacle_rotation = rotation
        self.colors = [{"r": 0.219607845, "g": 0.5156862754, "b": 0.2901961, "a": 1.0}]
        self.cmd = []

    def create_obstacle(self, actually_create=False):


        self.obstacle_id = self.tdw_object.add_object("prim_cube", position={"x": 10, "y": 10, "z": 10},
                                        rotation=self.obstacle_rotation, library="models_special.json")
        self.current_position = {"x": self.obstacle_position["x"], "y": 2.243, "z": self.obstacle_position["z"]}
        self.tdw_object.communicate([
            {"$type": "set_kinematic_state", "id": self.obstacle_id, "is_kinematic": True,
             "use_gravity": False},
            {"$type": "scale_object", "scale_factor":
                {"x": self.obstacle_width, "y": self.obstacle_height, "z": self.obstacle_depth},
             "id": self.obstacle_id},
            {"$type": "set_mass", "id": self.obstacle_id, "mass": 4.0},
            {"$type": "set_color", "color":
                {"r": 0.219607845, "g": 0.5156862754, "b": 0.2901961, "a": 1.0}, "id": self.obstacle_id},
        ])

        if actually_create:
            self.tdw_object.communicate({"$type": "teleport_object", "position": self.obstacle_position, "id": self.obstacle_id})
        else:
            self.cmd = [
                {"$type": "teleport_object", "position": self.current_position, "id": self.obstacle_id},

            ]

        return self.obstacle_id

    def actually_create_obstacle(self):
        if self.cmd:
            self.tdw_object.communicate(self.cmd)

