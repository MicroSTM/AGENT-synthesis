
class Ramp:
    def __init__(self, position, rotation, height, agent_start_position):
        self.position = position
        self.rotation = rotation
        self.ramp_start = position
        self.height = height
        self.jump_point_1 = position
        self.jump_point_2 = position
        self.jump_point_3 = position
        self.agent_start_position = agent_start_position
        self.ramp_base_id, self.ramp_slope_id = [None]*2

    def get_positions(self, platform_only):
        self.platform_side = (0, 1) if self.rotation in [90, -90] else (1, 0)
        self.direction = 1 if self.rotation in [90, 180] else -1
        if self.height == 0.8:
            slope_position = {"x": self.position["x"] + self.platform_side[0]*self.direction*0.268,
                              "y": 0.388,
                              "z": self.position["z"] + self.platform_side[1]*self.direction*0.268}
            slope_rotation = {"x": 0, "y": self.rotation, "z": -36.342}
            slope_scale = {"x": 0.05, "y": 1.0, "z": 0.7}
            if platform_only:
                base_position = self.position.copy()
                base_position["y"] = 0.409
            else:
                base_position = {"x": self.position["x"] - self.platform_side[0]*self.direction*0.358,
                                 "y": 0.409, "z": self.position["z"] - self.platform_side[1]*self.direction*-0.358}
            base_scale = {"x": 0.7, "y": 0.8, "z": 0.7}
            self.ramp_start = {"x": slope_position["x"] + self.platform_side[0] * self.direction * 0.565, "y": 0,
                               "z": slope_position["z"] + self.platform_side[1] * self.direction * 0.565}
            self.ramp_start_ = {"x": slope_position["x"] + self.platform_side[0] * self.direction * 0.4, "y": 0,
                               "z": slope_position["z"] + self.platform_side[1] * self.direction * 0.4}

            # self.jump_point_1 = {"x": base_position["x"] - self.platform_side[0] * self.direction * 0.387, "y": 0,
            #                    "z": base_position["z"] - self.platform_side[1] * self.direction * 0.387}
            self.target_position = base_position.copy()
            self.target_position["y"] = 0.905
        elif self.height == 0.5:
            slope_position = {"x": self.position["x"] + self.platform_side[0]*self.direction*0.418,
                              "y": 0.229,
                              "z": self.position["z"] + self.platform_side[1]*self.direction*0.418}
            slope_rotation = {"x": 0, "y": self.rotation, "z": -60}
            slope_scale = {"x": 0.05, "y": 1.0, "z": 0.7}
            if platform_only:
                base_position = self.position.copy()
                base_position["y"] = 0.25
            else:
                base_position = {"x": self.position["x"] - self.platform_side[0]*self.direction*0.358,
                                 "y": 0.25, "z": self.position["z"] - self.platform_side[1]*self.direction*0.358}
            base_scale = {"x": 0.7, "y": 0.5, "z": 0.7}
            self.ramp_start = {"x": slope_position["x"] + self.platform_side[0] * self.direction * 0.565, "y": 0,
                               "z": slope_position["z"] + self.platform_side[1] * self.direction * 0.565}
            self.ramp_start_ = {"x": slope_position["x"] + self.platform_side[0] * self.direction * 0.42, "y": 0,
                                "z": slope_position["z"] + self.platform_side[1] * self.direction * 0.42}
            # self.jump_point_1 = {"x": base_position["x"] - self.platform_side[0] * self.direction * 0.387, "y": 0,
            #                    "z": base_position["z"] - self.platform_side[1] * self.direction * 0.387}
            self.target_position = base_position.copy()
            self.target_position["y"] = 0.6
        elif self.height == 0.2:
            slope_position = {"x": self.position["x"] + self.platform_side[0]*self.direction*0.474,
                              "y": 0.077,
                              "z": self.position["z"] + self.platform_side[1]*self.direction*0.474}
            slope_rotation = {"x": 0.0, "y": self.rotation, "z": -77.979}
            slope_scale = {"x": 0.05, "y": 1.0, "z": 0.7}
            if platform_only:
                base_position = self.position.copy()
                base_position["y"] = 0.103
            else:
                base_position = {"x": self.position["x"] - self.platform_side[0]*self.direction*0.358,
                                 "y": 0.103, "z": self.position["z"] - self.platform_side[1]*self.direction*0.358}
            base_scale = {"x": 0.7, "y": 0.2, "z": 0.7}
            self.ramp_start = {"x": slope_position["x"] + self.platform_side[0]*self.direction*0.738, "y": 0,
                               "z": slope_position["z"] + self.platform_side[1]*self.direction*0.738}
            self.ramp_start_ = {"x": slope_position["x"] + self.platform_side[0] * self.direction * 0.6, "y": 0,
                                "z": slope_position["z"] + self.platform_side[1] * self.direction * 0.6}
            # self.jump_point_1 = {"x": base_position["x"] - self.platform_side[0] * self.direction * 0.387, "y": 0,
            #                      "z": base_position["z"] - self.platform_side[1] * self.direction * 0.387}
            self.target_position = base_position.copy()
            self.target_position["y"] = 0.303

        self.calculate_platform_points(base_position)
        self.positions = {
            "slope_position": slope_position,
            "slope_rotation": slope_rotation,
            "slope_scale": slope_scale,
            "base_position" : base_position,
            "base_rotation": {"x": 0.0, "y": 0.0, "z": 0.0},
            "base_scale": base_scale
        }
        return self.positions

    def calculate_platform_points(self, base_position):
        offset = 0.76
        offset_ = 0.898
        self.jump_point_1 = {"x": base_position["x"] - self.platform_side[0] * self.direction * offset, "y": 0,
                             "z": base_position["z"] - self.platform_side[1] * self.direction * offset}
        self.jump_point_1_ = {"x": base_position["x"] - self.platform_side[0] * self.direction * offset_, "y": 0,
                             "z": base_position["z"] - self.platform_side[1] * self.direction * offset}
        self.jump_point_2 = {"x": base_position["x"] + self.platform_side[1] * self.direction * offset, "y": 0,
                             "z": base_position["z"] + self.platform_side[0] * self.direction * offset}
        self.jump_point_2_ = {"x": base_position["x"] + self.platform_side[1] * self.direction * offset_, "y": 0,
                             "z": base_position["z"] + self.platform_side[0] * self.direction * offset}
        self.jump_point_3 = {"x": base_position["x"] - self.platform_side[1] * self.direction * offset, "y": 0,
                             "z": base_position["z"] - self.platform_side[0] * self.direction * offset}
        self.jump_point_3_ = {"x": base_position["x"] - self.platform_side[1] * self.direction * offset_, "y": 0,
                             "z": base_position["z"] - self.platform_side[0] * self.direction * offset}
