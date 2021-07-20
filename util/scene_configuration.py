

class SceneConfiguration:
    def __init__(self, scene_offset=(0, 0, -3.806)):
        # self.scene_offset = (0, 0, -4.026)
        # self.scene_offset = (0, 0, -4.032)
        self.pit_depth_ = 0.8
        self.scene_offset = scene_offset
        self.agent_colors = [
            {"r": 240 / 255, "g": 19 / 255, "b": 77 / 255, "a": 1.0},
            {"r": 7 / 255, "g": 121 / 255, "b": 228 / 255, "a": 1.0},
            {"r": 52 / 255, "g": 46 / 255, "b": 173 / 255, "a": 1.0},
            {"r": 253 / 255, "g": 46 / 255, "b": 179 / 255, "a": 1.0},
            {"r": 237 / 255, "g": 12 / 255, "b": 239 / 255, "a": 1.0},
                             ]
        # self.target_colors = [
        #
        #     {"r": 149 / 255, "g": 56 / 255, "b": 158 / 255, "a": 1.0},
        #     {"r": 216 / 255, "g": 52 / 255, "b": 95 / 255, "a": 1.0},
        #     {"r": 148 / 255, "g": 252 / 255, "b": 19 / 255, "a": 1.0},
        #     {"r": 255 / 255, "g": 87 / 255, "b": 34 / 255, "a": 1.0},
        #     {"r": 210 / 255, "g": 230 / 255, "b": 3 / 255, "a": 1.0},
        #     {"r": 244 / 255, "g": 89 / 255, "b": 5 / 255, "a": 1.0},
        #     {"r": 243 / 255, "g": 14 / 255, "b": 92 / 255, "a": 1.0},
        #
        #     {"r": 67 / 255, "g": 216 / 255, "b": 210 / 255, "a": 1.0},
        #     {"r": 88 / 255, "g": 141 / 255, "b": 168 / 255, "a": 1.0},
        #     {"r": 48 / 255, "g": 71 / 255, "b": 94 / 255, "a": 1.0},
        #     {"r": 0 / 255, "g": 188 / 255, "b": 212 / 255, "a": 1.0},
        #     {"r": 217 / 255, "g": 191 / 255, "b": 119 / 255, "a": 1.0},
        #     {"r": 85 / 255, "g": 34 / 255, "b": 68 / 255, "a": 1.0},
        #     {"r": 8 / 255, "g": 255 / 255, "b": 200 / 255, "a": 1.0},
        #
        #                       ]
        self.target_colors_ = {
            "set_1": [
                {"r": 216 / 255, "g": 52 / 255, "b": 95 / 255, "a": 1.0},
                {"r": 148 / 255, "g": 252 / 255, "b": 19 / 255, "a": 1.0},
                {"r": 255 / 255, "g": 87 / 255, "b": 34 / 255, "a": 1.0},
                {"r": 210 / 255, "g": 230 / 255, "b": 3 / 255, "a": 1.0},
            ],
            "set_2": [
                {"r": 88 / 255, "g": 141 / 255, "b": 168 / 255, "a": 1.0},
                {"r": 48 / 255, "g": 71 / 255, "b": 94 / 255, "a": 1.0},
                {"r": 0 / 255, "g": 188 / 255, "b": 212 / 255, "a": 1.0},
                {"r": 85 / 255, "g": 34 / 255, "b": 68 / 255, "a": 1.0},
        ]
        }

        self.target_colors = self.target_colors_["set_1"] + self.target_colors_["set_2"]

        self.ramp_position = [
            {"x": 0 + self.scene_offset[0] + 1.66, "y": 0, "z": 0 + self.scene_offset[2]},
            {"x": 0 + self.scene_offset[0] - 1.66, "y": 0, "z": 0 + self.scene_offset[2]}
        ]
        self.positions_x = [
            0 + self.scene_offset[0] + 1.66,
            0 + self.scene_offset[0] + 0.83,
            0 + self.scene_offset[0],
            0 + self.scene_offset[0] - 0.83,
            0 + self.scene_offset[0] - 1.66
        ]
        self.positions_x_without_barrier = [
            0 + self.scene_offset[0] + 1.66,
            0 + self.scene_offset[0] + 1.106,
            0 + self.scene_offset[0] + 0.5533,
            0 + self.scene_offset[0],
            0 + self.scene_offset[0] - 0.5533,
            0 + self.scene_offset[0] - 1.106,
            0 + self.scene_offset[0] - 1.66
        ]
        # self.positions_x = [
        #     0 + self.scene_offset[0] + 1.86,
        #     0 + self.scene_offset[0] + 0.93,
        #     0 + self.scene_offset[0],
        #     0 + self.scene_offset[0] - 0.93,
        #     0 + self.scene_offset[0] - 1.86
        # ]
        # self.target_objects = [
        #     "bowl",
        #     "cylinder",
        #     "dumbbell",
        #     "octahedron",
        #     "pentagon",
        #     "pipe",
        #     "platonic",
        #     "pyramid",
        #     "torus",
        #     "triangular_prism"
        # ]
        self.target_objects = {
            "target_objects_1": [
                "pyramid",
                "bowl"
            ],
            "target_objects_2":[
                "cylinder",
                "octahedron"
            ]
        }
        self.target_objects_ = self.target_objects["target_objects_1"] + self.target_objects["target_objects_2"]
        self.positions_x_scene_1_2 = [
            0 + (self.scene_offset[0] - 0.12) + 1.2,
            0 + (self.scene_offset[0] - 0.12),
            0 + (self.scene_offset[0] - 0.12) - 1.2,
        ]
        self.positions_x_scene_1_2_extended = [
            0 + (self.scene_offset[0] - 0.12) + 1.8,
            0 + (self.scene_offset[0] - 0.12) - 1.8,
        ]
        self.positions_z_scene_1_2 = [
            (self.scene_offset[2] + 1.56) - 0.549,
            0 + (self.scene_offset[2] + 1.34),
            (self.scene_offset[2] + 1.34) + 0.549
        ]
        self.ramp_rotation = [0, 90, 180, -90]
        self.positions_z = [
            self.scene_offset[2] - 0.549,
            0 + self.scene_offset[2],
            self.scene_offset[2] + 0.549
        ]
        self.positions_y = [
            scene_offset[1] + 0.102,
            0.052,
            0.102,
            0.152,
            0.202,
            0.302,
            0.352,
            0.458,
            0.509
        ]
        self.positions_y_platform_cube = [
            0.102,
            0.2,
        ]
        self.platform_cube_height = [
            0.2,
            0.4
        ]
        self.obstacle_z = [
            self.scene_offset[2] - 0.222,
            0 + self.scene_offset[2],
            self.scene_offset[2] + 0.222
        ]
        # x_pos -> Width -> Height -> Depth


        # x_pos -> occ position
        self.occluder_position = {
            "occ_z_0": {'x': 0.683, 'y': 0.617018, 'z': -0.295},
            "occ_z_1": {'x': 0.645, 'y': 0.617018, 'z': -0.302},
            "occ_z_2": {'x': 0.645, 'y': 0.617018, 'z': -0.302}
        }

        self.positions = [
            {"x": 0 + self.scene_offset[0] + 1.66, "y": scene_offset[1] + 0.0011,
             "z": 0 + self.scene_offset[2]},
            {"x": 0 + self.scene_offset[0] + 0.83, "y": scene_offset[1] + 0.0011,
             "z": 0 + self.scene_offset[2]},
            {"x": 0 + self.scene_offset[0], "y": scene_offset[1] + 0.0011,
             "z": 0 + self.scene_offset[2]},
            {"x": 0 + self.scene_offset[0] - 0.83, "y": scene_offset[1] + 0.0011,
             "z": 0 + self.scene_offset[2]},
            {"x": 0 + self.scene_offset[0] - 1.66, "y": scene_offset[1] + 0.0011,
             "z": 0 + self.scene_offset[2]}
        ]
        self.pit_positions = [
            (
                {"x": (self.scene_offset[0] - 0.12) + 3.19, "y": 0.462 + self.pit_depth_/2, "z": 0 + scene_offset[2] + 0.896},
                {"x": (self.scene_offset[0] - 0.12) - 3.19, "y": 0.462 + self.pit_depth_/2, "z": 0 + scene_offset[2] + 0.896},
                {"x": (self.scene_offset[0] - 0.12), "y": 0.462 + self.pit_depth_/2, "z": 0 + scene_offset[2] + 0.896}
            ),
            (
                {"x": self.scene_offset[0] + 3.75, "y": 0.462 + self.pit_depth_/2, "z": 0 + scene_offset[2] },
                {"x": self.scene_offset[0], "y": 0.462 + self.pit_depth_/2, "z": 0 + scene_offset[2]},
                {"x": self.scene_offset[0] - 3.75, "y": 0.462 + self.pit_depth_/2, "z": 0 + scene_offset[2]}
            ),
            (
                {"x": 0 + (self.scene_offset[0] - 0.12), "y": 0.462 + self.pit_depth_/2, "z": 0 + scene_offset[2] + 1.122},
                {"x": 0 + (self.scene_offset[0] - 0.12), "y": 0.462 + self.pit_depth_/2, "z": 0 + scene_offset[2] - 1.122}
            )
        ]
        # 3.806
        self.bridge_position = [
            {"x": (self.scene_offset[0] - 0.12), "y": 0.462 + self.pit_depth_/2 , "z": 0 + scene_offset[2] + 0.896},
        ]
        # self.pit_width = [3.95, 3.35, 2.75]
        self.pit_width = [6, 5.5, 5]
        self.pit_width_3_4 = [(3, 2), (3, 2), (3, 2)]
        self.pit_depth = [1.1, 1.6, 2.1]
        self.bridge_width = [0.38, 0.6, 0.88, 1.13, 1.38]
        self.bridge_width_3_4 = [0.3, 0.5, 0.7]
        self.obstacle_height = [0.1, 0.2, 0.3, 0.4, 0.6, 0.7, 0.9, 1.0]
        # self.obstacle_height_pool = [
        #     [0.1, 0.4, 0.7],
        #     [0.2, 0.6],         #     [0.2, 0.4, 0.7],
        #     [0.3, 0.7],
        # ]
        self.obstacle_height_pool = [
            [0.1, 0.3, 0.6],
            [0.2, 0.6],
            [0.3, 0.6],
        ]
        self.obstacle_depth_pool = [
            [0.7, 1.5, 2.1],
            [0.6, 1.5, 2.0],
            [0.6, 1.1, 1.7, 2.1]
        ]
        self.obstacle_width_pool = [
            [0.1, 0.4],
            [0.2, 0.5],
            [0.1, 0.5],
            [0.2, 0.4],
            [0.1, 0.2]
        ]
        self.obstacle_width = [0.1, 0.2, 0.4, 0.5]
        self.obstacle_depth = [0.6, 0.7, 1.1, 1.6, 2.1, 2.4, 2.6, 2.8, 3.0, 4.0]
        self.agent_types = ["cube", "sphere", "cone"]
        self.ramp_height = [0.2, 0.5, 0.8]
        self.floor_material = ["ceramic_tiles_beige_tan", "ceramic_tiles_copper", "ceramic_tiles_floral_white", "ceramic_tiles_brown_tomato", "tiles_hexagon_white", "ceramic_tiles_golden_sand", "ceramic_tiles_grey", "ceramic_tiles_green"]
        self.wall_material = ["square_padded_wall", "cinderblock_wall", "church_wall_chamfered_cracks"]



