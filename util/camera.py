class Camera:
    def __init__(self, camera_1_pos, camera_1_rot, camera_2_pos, camera_2_rot, camera_3_pos, camera_3_rot, scene_offset,
                 height, width, screen_scale):
        self.camera_side_pos = camera_1_pos
        self.camera_side_rot = camera_1_rot
        self.camera_top_pos = camera_2_pos
        self.camera_top_rot = camera_2_rot
        self.camera_top_side_pos = camera_3_pos
        self.camera_top_side_rot = camera_3_rot
        self.current_rotation = camera_3_rot
        self.current_position = camera_3_pos
        self.camera_top_id = "a"
        self.camera_side_id = "b"
        self.camera_top_side_id = "c"
        self.scene_offset = scene_offset
        self.single_camera = False
        self.camera_moved = False
        self.height = height
        self.width = width
        self.screen_scale = screen_scale

    def create_camera(self, single_camera=False):
        self.single_camera = single_camera
        cmd = [

            # Top camera
            {"$type": "create_avatar", "type": "A_Img_Caps_Kinematic", "id": self.camera_top_id},
            {"$type": "teleport_avatar_to", "avatar_id": self.camera_top_id, "position": self.camera_top_pos},
            {"$type": "rotate_avatar_to_euler_angles", "euler_angles": self.camera_top_rot,
             "avatar_id": self.camera_top_id},

            {"$type": "create_avatar", "type": "A_Img_Caps_Kinematic", "id": self.camera_side_id},
            {"$type": "teleport_avatar_to", "avatar_id": self.camera_side_id, "position": self.camera_side_pos},
            {"$type": "rotate_avatar_to_euler_angles", "euler_angles": self.camera_side_rot,
             "avatar_id": self.camera_side_id},

            {"$type": "create_avatar", "type": "A_Img_Caps_Kinematic", "id": self.camera_top_side_id},
            {"$type": "teleport_avatar_to", "avatar_id": self.camera_top_side_id,
             "position": self.camera_top_side_pos},
            {"$type": "rotate_avatar_to_euler_angles", "euler_angles": self.camera_top_side_rot,
             "avatar_id": self.camera_top_side_id},

            # {"$type": "set_screen_size", "width": 1080, "height": 720},
            # {"$type": "set_screen_size", "width": 480, "height": 320},
            {"$type": "set_screen_size", "width": self.width, "height": self.height},
            {"$type": "set_target_framerate", "framerate": 35},
              # {"$type": "set_screen_size", "width": 300, "height": 200}

             ]
        if single_camera:
            return cmd[-5:]
        else:
            return cmd

    def increase_height(self, height_delta):
        if not self.single_camera:
            self.camera_side_pos["y"] += height_delta
            self.camera_top_pos["y"] += height_delta
        self.camera_top_side_pos["y"] += height_delta
        cmd = [
            {"$type": "teleport_avatar_to", "avatar_id": self.camera_top_side_id,
             "position": self.camera_top_side_pos}
            ]
        if not self.single_camera:
            cmd.extend(
                [{"$type": "teleport_avatar_to", "avatar_id": self.camera_side_id, "position": self.camera_side_pos},
                 {"$type": "teleport_avatar_to", "avatar_id": self.camera_top_id,
                  "position": self.camera_top_pos}
                 ]
            )
        return cmd

    def move_camera_scene_scene_3(self):
        aspect_ratio = [13, 8]
        self.width, self.height = aspect_ratio[0]*self.screen_scale, aspect_ratio[1]*self.screen_scale
        cmd = self.move_camera(
            pos={"x": 0, "y": 1.678, "z": 4.974 + self.scene_offset[2]},
            rot={"x": 14.451, "y": 180, "z": 0},
            avatar_id="c"
        )
        cmd.extend([{"$type": "set_screen_size", "width": self.width, "height": self.height}])
        return cmd

    def move_camera_scene_scene_1(self):
        if self.screen_scale == 40:
            self.width, self.height = 420, 280
        else:
            self.width, self.height = 1080, 720
        cmd = self.move_camera(
            pos={"x": 1, "y": 1.45, "z": 4.496 + self.scene_offset[2]},
            rot={"x": 23.06, "y": -154.898, "z": 0},
            avatar_id="c"
        )
        cmd.extend([{"$type": "set_screen_size", "width": self.width, "height": self.height}])
        return cmd

    def move_camera_scene_2(self):
        cmd = self.move_camera(
            pos={"x": 0.612, "y": 1.45, "z": 4.496 + self.scene_offset[2]},
            rot={"x": 23.06, "y": -165.381, "z": 0},
            avatar_id="c"
        )
        self.current_position = {"x": 0.612, "y": 1.45, "z": 4.496 + self.scene_offset[2]}
        self.current_rotation = {"x": 23.06, "y": -165.381, "z": 0}
        return cmd


    def move_camera(self, pos, rot, avatar_id):
        cmd = [
            {"$type": "teleport_avatar_to", "avatar_id": avatar_id, "position": pos},
            {"$type": "rotate_avatar_to_euler_angles", "euler_angles": rot,
             "avatar_id": avatar_id},
        ]
        self.camera_top_side_pos = pos
        self.camera_top_side_rot = rot
        self.camera_moved = True
        return cmd
