from util import utils


class Pit:
    def __init__(self, config_file):
        self.config_file = config_file
        self.pit_width = 0
        self.pit_ids = []
        self.pit_widths = []
        self.bridge = False
        self.top_pt, self.bottom_pt = None, None
        self.bridge_1, self.bridge_2 = None, None
        self.scene_3_4 = False
    def create_pit(self, tdw_object, scene_config, scene_3_4=False):
        self.scene_3_4 = scene_3_4
        if not scene_3_4:
            if self.config_file["pit_width"] != -1:
                self.pit_width = scene_config.bridge_width[self.config_file["pit_width"]]
                pit_side_1 = scene_config.pit_positions[0][0].copy()
                pit_side_2 = scene_config.pit_positions[0][1].copy()
                self.pit_side_width = abs(pit_side_1["x"] - scene_config.positions_x_scene_1_2[1])
                self.pit_side_width -= (self.pit_width/2)
                self.pit_side_width *= 2
                if self.config_file["obstacle_pos_x"] == -1:
                    pit_side_1["x"] -= (1.2 + 0.16 + self.pit_width)
                    pit_side_2["x"] -= (1.2 + 0.16 + self.pit_width)
                self.pit_ids.append(utils.create_raised_ground(tdw_object, pit_side_1,
                                                               width=self.pit_side_width))
                self.pit_widths.append(self.pit_side_width)
                self.pit_ids.append(utils.create_raised_ground(tdw_object, pit_side_2,
                                                               width=self.pit_side_width))
                self.pit_widths.append(self.pit_side_width)
            else:
                self.pit_ids.append(utils.create_raised_ground(tdw_object, scene_config.pit_positions[0][1],
                                                               width=12))
                self.pit_widths.append(12)
            if self.config_file["pit_depth"] != -1:
                side_1_pos = scene_config.pit_positions[2][0].copy()
                side_2_pos = scene_config.pit_positions[2][1].copy()
                if self.config_file["obstacle_pos_x"] == -1:
                    side_1_pos["x"] -= (1.2 + 0.16 + self.pit_width)
                    side_2_pos["x"] -= (1.2 + 0.16 + self.pit_width)
                side_1_pos["z"] = scene_config.positions_z_scene_1_2[self.config_file["obstacle_pos_z"]] + 2.5
                side_2_pos["z"] = scene_config.positions_z_scene_1_2[self.config_file["obstacle_pos_z"]] - 2.5
                dist_btw_pts = abs(side_1_pos["z"] - side_2_pos["z"])
                sides_depth = dist_btw_pts - scene_config.pit_depth[self.config_file["pit_depth"]]
                side_width = scene_config.bridge_width[self.config_file["pit_width"]]
                self.bottom_pt = side_1_pos.copy()
                self.bottom_pt["z"] -= (sides_depth/2 - 0.2)
                self.top_pt = side_2_pos.copy()
                self.top_pt["z"] += (sides_depth / 2 - 0.2)
                self.pit_ids.append(utils.create_raised_ground(tdw_object, side_1_pos,
                                                               width=side_width, depth=sides_depth))
                self.pit_widths.append(side_width)
                self.pit_ids.append(utils.create_raised_ground(tdw_object, side_2_pos,
                                                               width=side_width, depth=sides_depth))
                self.pit_widths.append(side_width)
        else:
            assert not (self.config_file["pit_width_1"] == -1 and self.config_file[
                "pit_width_2"] == -1), "Don't use pit " \
                                       "barrier when you" \
                                       " don't intend " \
                                       "to have a pit"
            pit_side_1 = scene_config.pit_positions[1][0].copy()
            pit_side_2 = scene_config.pit_positions[1][2].copy()
            if self.config_file["pit_width_1"] != -1:
                dist_1 = abs(pit_side_1["x"] - scene_config.positions[1]["x"])
                self.pit_width_1 = scene_config.bridge_width_3_4[self.config_file["pit_width_1"]]
                self.side_1_width = (dist_1 - self.pit_width_1/2)*2
            else:
                dist_1 = abs(pit_side_1["x"] - scene_config.positions[3]["x"])
                self.side_1_width = (dist_1 - scene_config.bridge_width_3_4[self.config_file["pit_width_2"]] / 2) * 2
            if self.config_file["pit_width_2"] != -1:
                dist_2 = abs(pit_side_2["x"] - scene_config.positions[3]["x"])
                self.pit_width_2 = scene_config.bridge_width_3_4[self.config_file["pit_width_2"]]
                self.side_2_width = (dist_2 - self.pit_width_2 / 2)*2
            else:
                dist_2 = abs(pit_side_2["x"] - scene_config.positions[1]["x"])
                self.side_2_width = (dist_2 - scene_config.bridge_width_3_4[self.config_file["pit_width_1"]] / 2) * 2

            self.pit_ids.append(utils.create_raised_ground(tdw_object, pit_side_1,
                                                           width=self.side_1_width))
            self.pit_widths.append(self.side_1_width)
            self.pit_ids.append(utils.create_raised_ground(tdw_object, pit_side_2,
                                                           width=self.side_2_width))
            self.pit_widths.append(self.side_2_width)

            if self.config_file["pit_width_1"] != -1 and self.config_file["pit_width_2"] != -1:
                self.side_mid_width = abs(scene_config.positions[1]["x"] - scene_config.positions[3]["x"]) - \
                                      (self.pit_width_1/2 + self.pit_width_2/2)

                pit_mid = pit_side_1.copy()
                pit_mid["x"] = scene_config.positions[1]["x"] - (self.side_mid_width/2 + self.pit_width_1/2)
                self.pit_ids.append(utils.create_raised_ground(tdw_object, pit_mid,
                                                               width=self.side_mid_width))
                self.pit_widths.append(self.side_mid_width)
            if self.config_file["barrier_type"] == "pit-with-bridge":
                self.bridge = True
                if "bridge_1_z" in self.config_file:
                    if self.config_file["bridge_1_z"] != -1:
                        self.bridge_1_position = pit_side_1.copy()
                        self.bridge_1_position["x"] = scene_config.positions[1]["x"]
                        self.bridge_1_position["z"] = scene_config.positions_z[self.config_file["bridge_1_z"]]
                        self.pit_ids.append(utils.create_raised_ground(tdw_object, self.bridge_1_position,
                                                                       width=self.pit_width_1, depth=0.6))
                        self.pit_widths.append(self.pit_width_1)
                        self.bridge_1 = self.pit_ids[-1]
                if "bridge_2_z" in self.config_file:
                    if self.config_file["bridge_2_z"] != -1:
                        self.bridge_2_position = pit_side_1.copy()
                        self.bridge_2_position["x"] = scene_config.positions[3]["x"]
                        self.bridge_2_position["z"] = scene_config.positions_z[self.config_file["bridge_2_z"]]
                        self.pit_ids.append(utils.create_raised_ground(tdw_object, self.bridge_2_position,
                                                                       width=self.pit_width_2, depth=0.6))
                        self.pit_widths.append(self.pit_width_2)
                        self.bridge_2 = self.pit_ids[-1]

            # self.pit_ids.append(utils.create_raised_ground(tdw_object, {"x": 1.009, "y":0.462, "z":-6.34},
            #                                                width=1.26, depth=2))
            # self.pit_ids.append(utils.create_raised_ground(tdw_object, {"x": -0.69, "y": 0.462, "z": -6.34},
            #                                                width=1.26, depth=2))
            # self.pit_ids.append(utils.create_raised_ground(tdw_object, {"x": 1.009, "y": 0.462, "z": 1.31},
            #                                                width=1.26, depth=7))
            # self.pit_ids.append(utils.create_raised_ground(tdw_object, {"x": -0.69, "y": 0.462, "z": 1.31},
            #                                                width=1.26, depth=7))



        if self.config_file["barrier_type"] == "pit-with-bridge":
            if not scene_3_4:
                self.bridge = True
                self.bridge_position = scene_config.bridge_position[0]
                self.bridge_width = scene_config.bridge_width[self.config_file["pit_width"]]
                self.bridge_position["z"] = scene_config.positions_z_scene_1_2[self.config_file["bridge_z"]]
                self.pit_ids.append(utils.create_raised_ground(tdw_object, self.bridge_position,
                                                               width=self.bridge_width,
                                                               depth=0.6))
                self.pit_widths.append(self.bridge_width)
                self.bridge_1 = self.pit_ids[-1]
        return self.pit_ids
