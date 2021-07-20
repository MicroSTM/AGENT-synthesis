class jump:
    def __init__(self, direction=None, direction_x_z=None):
        self.direction = 0 if direction is None else direction
        self.direction_x_z = [0, 0] if direction_x_z is None else direction_x_z
        self.jump_forces = {
            "0.1_0.1": [self.direction * -2.0, 2.2, 0],
            "0.2_0.1": [self.direction * -1.7, 2.5, 0],
            "0.3_0.1": [self.direction * -1.6, 2.9, 0],
            "0.4_0.1": [self.direction * -1.4, 3.5, 0],
            "0.6_0.1": [self.direction * -1.0, 4.2, 0],
            "0.7_0.1": [self.direction * -1.0, 4.4, 0],
            "0.1_0.2": [self.direction * -2.2, 2.2, 0],
            "0.2_0.2": [self.direction * -1.8, 2.5, 0],
            "0.3_0.2": [self.direction * -1.6, 2.9, 0],
            "0.4_0.2": [self.direction * -1.3, 3.5, 0],
            "0.6_0.2": [self.direction * -1.05, 4.3, 0],
            "0.7_0.2": [self.direction * -1.0, 4.5, 0],
            "0.1_0.4": [self.direction * -2.1, 2.57, 0],
            "0.2_0.4": [self.direction * -1.9, 3.0, 0],
            "0.3_0.4": [self.direction * -1.7, 3.2, 0],
            "0.4_0.4": [self.direction * -1.4, 3.87, 0],
            "0.6_0.4": [self.direction * -1.3, 4.5, 0],
            "0.7_0.4": [self.direction * -1.13, 4.87, 0],
            "0.1_0.5": [self.direction * -2.25, 2.57, 0],
            "0.2_0.5": [self.direction * -2.0, 3.1, 0],
            "0.3_0.5": [self.direction * -1.8, 3.35, 0],
            "0.4_0.5": [self.direction * -1.6, 3.77, 0],
            "0.6_0.5": [self.direction * -1.45, 4.65, 0],
            "0.7_0.5": [self.direction * -1.25, 4.87, 0],
            "0.8_0": [direction_x_z[0] * -0.6, 4.2, direction_x_z[1] * -1.1],
            "0.5_0": [direction_x_z[0] * -1.1, 3.3, direction_x_z[1] * -1.1],
            "0.4_0": [direction_x_z[0] * -1.1, 3.0, direction_x_z[1] * -1.1],
            "0.2_0": [direction_x_z[0] * -1.5, 2.2, direction_x_z[1] * -1.5],
            "-0.7_0": [self.direction * -0.7, 4.2, 0],
            "-0.6_0": [self.direction * -0.7, 3.8, 0],
            "-0.4_0": [self.direction * -1.5, 1.1, 0],
            "-0.3_0": [self.direction * -0.9, 2.7, 0],
            "-0.2_0": [self.direction * -1.5,  1.1, 0],
            "-0.1_0": [self.direction * -0.9, 2.2, 0],
            "None_0.38": [self.direction * -1.7, 2, 0],
            "None_0.6": [self.direction * -2.2, 2.1, 0],
            "None_0.88": [self.direction * -2.7, 2.2, 0],
            "None_1.13": [self.direction * -2.9, 2.5, 0],
            "None_1.38": [self.direction * -3.1, 2.7, 0],
            "None_0.7": [self.direction * -1.9, 2.5, 0],
            "None_0.5": [self.direction * -1.7, 2.3, 0],
            "None_0.3": [self.direction * -1.4, 2.2, 0],
        }

    def get_jump_force(self, agent_velocity, jump_height, jump_width):
        jump_key = f"{jump_height}_{jump_width}"
        jump_force = self.jump_forces[jump_key]
        return [e - f for e, f in zip(jump_force, agent_velocity)]