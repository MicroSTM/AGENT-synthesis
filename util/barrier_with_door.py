
class BarrierWithDoor:
    def __init__(self, position, height, width, depth, door_depth, tdw_object, config_file):
        self.obstacle_position = position
        self.obstacle_height = height
        self.obstacle_width = width
        self.obstacle_depth = depth
        self.door_depth = door_depth
        self.tdw_object = tdw_object
        self.barrier_1, self.barrier_2, self.barrier_3 = None, None, None
        self.config_file = config_file
        self.cmd = []

    def create_obstacle(self, actually_create=False,):
        gap = self.obstacle_depth / 2 - self.door_depth / 2
        self.center_1 = {"x": self.obstacle_position["x"], "y": self.obstacle_position["y"],
                         "z": self.obstacle_position["z"] - (self.door_depth / 2 + gap / 2)}
        self.center_2 = {"x": self.obstacle_position["x"], "y": self.obstacle_position["y"],
                         "z": self.obstacle_position["z"] + (self.door_depth / 2 + gap / 2)}
        self.center_peice_height = 0.45* self.obstacle_height if "floating" in self.config_file else 0.3*self.obstacle_height
        self.center_3 = {"x": self.obstacle_position["x"], "y": self.obstacle_position["y"] + self.obstacle_height/2 -
                                                                self.center_peice_height/2,
                         "z": self.obstacle_position["z"]}

        self.center_1_current = {"x": self.obstacle_position["x"], "y": 2.243,
                         "z": self.obstacle_position["z"] - (self.door_depth / 2 + gap / 2)}
        self.center_2_current = {"x": self.obstacle_position["x"], "y": 2.243,
                         "z": self.obstacle_position["z"] + (self.door_depth / 2 + gap / 2)}
        self.center_3_current = {"x": self.obstacle_position["x"], "y": 2.243 + self.obstacle_height / 2 -
                                                                self.center_peice_height / 2,
                         "z": self.obstacle_position["z"]}
        if "floating" in self.config_file:
            self.center_1_current["z"] += 10
            self.center_2_current["z"] += 10
            self.center_1["z"] += 10
            self.center_2["z"] += 10
        self.barrier_1 = self.create_barrier_(
            positon={"x": 10, "y": 10, "z": 10}, rotation={"x": 0, "y": 0, "z": 0},
            scale={"x": self.obstacle_width, "y": self.obstacle_height, "z": gap}
        )
        self.barrier_2 = self.create_barrier_(
            positon={"x": 11, "y": 10, "z": 10}, rotation={"x": 0, "y": 0, "z": 0},
            scale={"x": self.obstacle_width, "y": self.obstacle_height, "z": gap}
        )
        self.barrier_3 = self.create_barrier_(
            positon={"x": 12, "y": 10, "z": 10}, rotation={"x": 0, "y": 0, "z": 0},
            scale={"x": self.obstacle_width, "y": self.center_peice_height, "z": self.obstacle_depth if "floating" in self.config_file else self.door_depth }
        )
        self.gap = gap
        if actually_create:
            self.cmd = [
                {"$type": "teleport_object", "position": self.center_1, "id": self.barrier_1},
                {"$type": "teleport_object", "position": self.center_2, "id": self.barrier_2},
                {"$type": "teleport_object", "position": self.center_3, "id": self.barrier_3}
            ]
            self.tdw_object.communicate(self.cmd)
        else:
            self.cmd = [
                {"$type": "teleport_object", "position": self.center_1_current, "id": self.barrier_1},
                {"$type": "teleport_object", "position": self.center_2_current, "id": self.barrier_2},
                {"$type": "teleport_object", "position": self.center_3_current, "id": self.barrier_3}
            ]




    def create_barrier_(self, positon, rotation, scale):
        obstacle_id = self.tdw_object.add_object("prim_cube", position=positon,
                                                      rotation=rotation, library="models_special.json")
        self.tdw_object.communicate(
            [{"$type": "scale_object", "scale_factor":
                scale,
              "id": obstacle_id},

             {"$type": "set_mass", "id": obstacle_id, "mass": 4.0},
             {"$type": "set_color", "color":
                 {"r": 0.219607845, "g": 0.5156862754, "b": 0.2901961, "a": 1.0}, "id": obstacle_id},
             # {"$type": "teleport_object", "position": positon, "id": obstacle_id},
             {"$type": "set_kinematic_state", "id": obstacle_id, "is_kinematic": True, "use_gravity": False}
             ])
        return obstacle_id

    def actually_create_obstacle(self):
        if self.cmd:
            self.tdw_object.communicate(self.cmd)