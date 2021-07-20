import os
from tdw.tdw_utils import TDWUtils
from tdw.output_data import Images
import random
from util.scene_configuration import SceneConfiguration
from tdw.output_data import  OutputData, LogMessage
import numpy as np
from util.camera import Camera
from util.ramp import Ramp
import json
import pickle
from statistics import median
import pandas as pd
from tqdm import tqdm
import math
from util.target_object import TargetObject
from PIL import Image as images
import glob
from shutil import copyfile
from util import sample_trajectory
scene_config = SceneConfiguration()
scene_offset = scene_config.scene_offset
v = -0.03
h = 0.09


def create_agent(tdw_object, position, rotation):
    sphere_id = tdw_object.add_object("prim_sphere", position={"x": 5, "y": 10, "z": 5},
                                      rotation=rotation, library="models_special.json")
    tdw_object.communicate([{"$type": "scale_object", "scale_factor": {"x": 0.2, "y": 0.2, "z": 0.2}, "id": sphere_id},

                            {"$type": "set_physic_material", "dynamic_friction": 0.4, "static_friction": 0.4,
                             "bounciness": 0, "id": sphere_id},
                            {"$type": "set_mass", "id": sphere_id, "mass": 7.0},
                            {"$type": "teleport_object", "position": position, "id": sphere_id}
                      ])
    return sphere_id


def create_target(tdw_object, position, rotation={"x": 0, "y": 0, "z": 0}, color={"r": 0.219607845, "g": 0.0156862754, "b": 0.6901961, "a": 1.0},
                  object_type="sphere"):
    object_type = "sphere" if object_type is None else object_type
    if object_type == "bowl":
        scale = {"x": 0.2, "y": 0.25, "z": 0.2}
    else:
        scale = {"x": 0.2, "y": 0.2, "z": 0.2}
    if object_type in ["sphere", "cone", "cube"]:
        object_type = "prim_" + object_type
        sphere_id = tdw_object.add_object(object_type, position={"x": 5, "y": 10, "z": 5},
                                          rotation=rotation, library="models_special.json")
    else:
        sphere_id = tdw_object.add_object(object_type, position={"x": 5, "y": 10, "z": 5},
                                          rotation=rotation, library="models_flex.json")
    if object_type not in ["prim_sphere", "prim_cube"]:
        position["y"] = position["y"]-0.102
    resp = tdw_object.communicate([{"$type": "scale_object", "scale_factor": scale, "id": sphere_id},
                            {"$type": "set_color", "color":
                                color, "id": sphere_id},
                            {"$type": "set_physic_material", "dynamic_friction": 0, "static_friction": 0,
                             "bounciness": 0, "id": sphere_id},
                            {"$type": "teleport_object", "position": position, "id": sphere_id},
                            {"$type": "step_physics", "frames": 20}
                            ])
    print_log(resp)

    tdw_object.communicate({"$type": "set_kinematic_state", "id": sphere_id, "is_kinematic": True,
                             "use_gravity": False})
    tdw_object.communicate({"$type": "teleport_object", "position": position, "id": sphere_id})
    target_obj = TargetObject(position, sphere_id)
    return target_obj

def stop_obj(tdw_object, obj_id):
    return tdw_object.communicate(
        [{"$type": "set_object_drag", "id": obj_id, "drag": 100, "angular_drag": 100},
         {"$type": "step_physics", "frames": 1},
         {"$type": "set_object_drag", "id": obj_id, "drag": 0, "angular_drag": 100}
         ])


def create_obstacle(tdw_object, position, rotation, obstacle_height, obstacle_width, obstacle_depth):
    cube_id = tdw_object.add_object("prim_cube", position={"x": 5, "y": 10, "z": 5},
                                    rotation=rotation, library="models_special.json")
    height_to_y_map = {
        0.9: 0.453,
        0.7: 0.353,
        0.6: 0.303,
        0.4: 0.202,
        0.3: 0.202,
        0.2: 0.201,
        0.1: 0.201
    }
    position["y"] = height_to_y_map[obstacle_height]
    tdw_object.communicate(
        [{"$type": "scale_object", "scale_factor": {"x": obstacle_width, "y": obstacle_height, "z": obstacle_depth}, "id": cube_id},
         {"$type": "set_mass", "id": cube_id, "mass": 4.0},
         {"$type": "set_color", "color":
             {"r": 0.219607845, "g": 0.5156862754, "b": 0.2901961, "a": 1.0}, "id": cube_id},
         {"$type": "teleport_object", "position": position, "id": cube_id}
         ])

    return cube_id

# def create_obstacle(tdw_object, position, rotation, height=0.2, width=0.2):
#     cube_id = tdw_object.add_object("prim_cube", position={"x": 5, "y": 10, "z": 5},
#                                       rotation=rotation, library="models_special.json")
#
#     tdw_object.communicate([{"$type": "scale_object", "scale_factor": {"x": width, "y": height, "z": 2.7}, "id": cube_id},
#                             {"$type": "set_semantic_material", "id": cube_id},
#                             {"$type": "set_mass", "id": cube_id, "mass": 4.0},
#                             {"$type": "set_color", "color":
#                                 {"r": 0.219607845, "g": 0.5156862754, "b": 0.2901961, "a": 1.0}, "id": cube_id},
#                             {"$type": "teleport_object", "position": position, "id": cube_id}
#                             ])
#
#     return cube_id


def test_agent(self, agent_name):
    url = "file:///" + os.path.join(os.getcwd(), "../agent_models", agent_name.title(), "StandaloneOSX", agent_name)
    agent_id = self.get_unique_id()
    self.communicate({"$type": "add_object",
                   "name": agent_name,
                   "url": url,
                   "scale_factor": 1,
                   "id": agent_id,
                      "position": {"x": 0, "y": 0, "z": -3.902}})

    self.communicate({"$type": "set_color_in_substructure",
                      "color": {"r": 0.219607845, "g": 0.5156862754, "b": 0.2901961, "a": 1.0},
                      "object_name": agent_name.title(), "id": agent_id})


def create_occluder(tdw_object, cube_position, scale, rotation):
    cube_id = tdw_object.add_object("prim_cube", position={"x": 5, "y": 10, "z": 5},
                                    rotation=rotation, library="models_special.json")
    position = cube_position
    tdw_object.communicate([{"$type": "scale_object", "scale_factor": scale , "id": cube_id},
                            {"$type": "set_mass", "id": cube_id, "mass": 4.0},
                            {"$type": "set_color", "color":
                                {"r": 0.519607845, "g": 0.5156862754, "b": 0.2901961, "a": 1.0}, "id": cube_id},
                            {"$type": "teleport_object", "position": position, "id": cube_id}
                            ])
    return cube_id


def create_slope_l(tdw_object, position, height, rotation=90, platform_only=False):
    if not platform_only:
        slope_id = tdw_object.add_object("prim_cube", position={"x": 5, "y": 10, "z": 5},
                                        rotation={"x": 0, "y": 0, "z": 0}, library="models_special.json")
    else:
        slope_id = None
    platform_id = tdw_object.add_object("prim_cube", position={"x": 5, "y": 10, "z": 9},
                                     rotation={"x": 0, "y": 0, "z": 0}, library="models_special.json")
    ramp = Ramp(position=position, rotation=rotation, height=height, agent_start_position={})
    positions = ramp.get_positions(platform_only)
    ramp.ramp_slope_id = slope_id
    ramp.ramp_base_id = platform_id
    # Create slope
    if not platform_only:
        tdw_object.communicate(
                [{"$type": "scale_object", "scale_factor": positions["slope_scale"], "id": slope_id},
                 {"$type": "set_physic_material", "dynamic_friction": 0, "static_friction": 0,
                  "bounciness": 0, "id": slope_id},
                 {"$type": "set_kinematic_state", "id": slope_id, "is_kinematic": True, "use_gravity": False},
                 {"$type": "set_color", "color":
                     {"r": 0.219607845, "g": 0.5156862754, "b": 0.2901961, "a": 1.0}, "id": slope_id},
                 {"$type": "teleport_object", "position": positions["slope_position"], "id": slope_id},
                 {"$type": "rotate_object_to_euler_angles", "euler_angles": positions["slope_rotation"], "id": slope_id}
                 ])
    tdw_object.communicate(
            [{"$type": "scale_object", "scale_factor": positions["base_scale"], "id": platform_id},
             {"$type": "set_physic_material", "dynamic_friction": 0, "static_friction": 0,
              "bounciness": 0, "id": platform_id},
             {"$type": "set_kinematic_state", "id": platform_id, "is_kinematic": True, "use_gravity": False},
             {"$type": "set_color", "color":
                 {"r": 0.219607845, "g": 0.5156862754, "b": 0.2901961, "a": 1.0}, "id": platform_id},
             {"$type": "rotate_object_to_euler_angles", "euler_angles": {"x": 0, "y": 0.0, "z": 0},
              "id": platform_id},
             {"$type": "teleport_object", "position": positions["base_position"], "id": platform_id}
             ])
    return ramp


def create_slope_l_new(tdw_object, position, height):
    slope_id = tdw_object.add_object("prim_cube", position={"x": 5, "y": 10, "z": 5},
                                    rotation={"x": 0, "y": 0, "z": 0}, library="models_special.json")
    platform_id = tdw_object.add_object("prim_cube", position={"x": 5, "y": 10, "z": 9},
                                     rotation={"x": 0, "y": 0, "z": 0}, library="models_special.json")
    if height == 1:
        position["y"] = 0.427
        tdw_object.communicate(
            [{"$type": "scale_object", "scale_factor": {"x": 0.1, "y": 1.4, "z": 0.7}, "id": slope_id},
             {"$type": "set_kinematic_state", "id": slope_id, "is_kinematic": True, "use_gravity": False},
             {"$type": "set_color", "color":
                 {"r": 0, "g": 0.03, "b": 0.22, "a": 1.0}, "id": slope_id},
             {"$type": "teleport_object", "position": position, "id": slope_id},
             {"$type": "rotate_object_to_euler_angles", "euler_angles": {"x": 0.0, "y": 0.0, "z": -46.948}, "id": slope_id}
             ])

        position["y"] = 0.891
        position["x"] += 1.178
        tdw_object.communicate(
            [{"$type": "scale_object", "scale_factor": {"x": 0.1, "y": 1.4, "z": 0.7}, "id": platform_id},
             {"$type": "set_kinematic_state", "id": platform_id, "is_kinematic": True, "use_gravity": False},
             {"$type": "set_color", "color":
                 {"r": 0, "g": 0.03, "b": 0.22, "a": 1.0}, "id": platform_id},
             {"$type": "rotate_object_to_euler_angles", "euler_angles": {"x": 0.0, "y": 0.0, "z": -90},
              "id": platform_id},
             {"$type": "teleport_object", "position": position, "id": platform_id}
             ])

    if height == 0.6:
        position["y"] = 0.236
        tdw_object.communicate(
            [{"$type": "scale_object", "scale_factor": {"x": 0.1, "y": 1.4, "z": 0.7}, "id": slope_id},
             {"$type": "set_kinematic_state", "id": slope_id, "is_kinematic": True, "use_gravity": False},
             {"$type": "set_color", "color":
                 {"r": 0, "g": 0.03, "b": 0.22, "a": 1.0}, "id": slope_id},
             {"$type": "teleport_object", "position": {"x": position["x"] - 0.127, "y": position["y"], "z": position["z"]}, "id": slope_id},
             {"$type": "rotate_object_to_euler_angles", "euler_angles": {"x": 0.0, "y": 0.0, "z": -66.369}, "id": slope_id}
             ])

        position["y"] = 0.506
        position["x"] += 1.188
        tdw_object.communicate(
            [{"$type": "scale_object", "scale_factor": {"x": 0.1, "y": 1.4, "z": 0.7}, "id": platform_id},
             {"$type": "set_kinematic_state", "id": platform_id, "is_kinematic": True, "use_gravity": False},
             {"$type": "set_color", "color":
                 {"r": 0, "g": 0.03, "b": 0.22, "a": 1.0}, "id": platform_id},
             {"$type": "rotate_object_to_euler_angles", "euler_angles": {"x": 0.0, "y": 0.0, "z": -90},
              "id": platform_id},
             {"$type": "teleport_object", "position": position, "id": platform_id}
             ])


def create_slope_r_new(tdw_object, position, height):
    slope_id = tdw_object.add_object("prim_cube", position={"x": 5, "y": 10, "z": 5},
                                    rotation={"x": 0, "y": 0, "z": 0}, library="models_special.json")
    platform_id = tdw_object.add_object("prim_cube", position={"x": 5, "y": 10, "z": 9},
                                     rotation={"x": 0, "y": 0, "z": 0}, library="models_special.json")

    if height == 0.6:
        position["y"] = 0.236
        tdw_object.communicate(
            [{"$type": "scale_object", "scale_factor": {"x": 0.1, "y": 1.4, "z": 0.7}, "id": slope_id},
             {"$type": "set_kinematic_state", "id": slope_id, "is_kinematic": True, "use_gravity": False},
             {"$type": "set_color", "color":
                 {"r": 0, "g": 0.03, "b": 0.22, "a": 1.0}, "id": slope_id},
             {"$type": "teleport_object",
              "position": {"x": position["x"] + 0.127, "y": position["y"], "z": position["z"]}, "id": slope_id},
             {"$type": "rotate_object_to_euler_angles", "euler_angles": {"x": 0.0, "y": 0.0, "z": 66.369},
              "id": slope_id}
             ])

        position["y"] = 0.506
        position["x"] -= 1.188
        tdw_object.communicate(
            [{"$type": "scale_object", "scale_factor": {"x": 0.1, "y": 1.4, "z": 0.7}, "id": platform_id},
             {"$type": "set_kinematic_state", "id": platform_id, "is_kinematic": True, "use_gravity": False},
             {"$type": "set_color", "color":
                 {"r": 0, "g": 0.03, "b": 0.22, "a": 1.0}, "id": platform_id},
             {"$type": "rotate_object_to_euler_angles", "euler_angles": {"x": 0.0, "y": 0.0, "z": 90},
              "id": platform_id},
             {"$type": "teleport_object", "position": position, "id": platform_id}
             ])

    if height == 0.3:
        position["y"] = 0.074
        # position["z"] = -3.428

        tdw_object.communicate(
            [{"$type": "scale_object", "scale_factor": {"x": 0.1, "y": 1.4, "z": 0.7}, "id": slope_id},
             {"$type": "set_kinematic_state", "id": slope_id, "is_kinematic": True, "use_gravity": False},
             {"$type": "set_color", "color":
                 {"r": 0, "g": 0.03, "b": 0.22, "a": 1.0}, "id": slope_id},
             {"$type": "teleport_object", "position": {"x": position["x"] + 0.127, "y": position["y"], "z": position["z"]}, "id": slope_id},
             {"$type": "rotate_object_to_euler_angles", "euler_angles": {"x": 0.0, "y": 0.0, "z": 80}, "id": slope_id}
             ])

        position["y"] = 0.194
        position["x"] += -1.254
        tdw_object.communicate(
            [{"$type": "scale_object", "scale_factor": {"x": 0.1, "y": 1.4, "z": 0.7}, "id": platform_id},
             {"$type": "set_kinematic_state", "id": platform_id, "is_kinematic": True, "use_gravity": False},
             {"$type": "set_color", "color":
                 {"r": 0, "g": 0.03, "b": 0.22, "a": 1.0}, "id": platform_id},
             {"$type": "rotate_object_to_euler_angles", "euler_angles": {"x": 0.0, "y": 0.0, "z": 90},
              "id": platform_id},
             {"$type": "teleport_object", "position": position, "id": platform_id}
             ])


def create_slope_r(tdw_object, position, height):
    ramp_id = tdw_object.add_object("ramp_with_platform", position={"x": 5, "y": 10, "z": 5},
                                    rotation={"x": 0, "y": 180, "z": 0}, library="models_special.json")
    color = {"r": 0, "g": 0.03, "b": 0.22, "a": 1.0}
    # color = {"r": 85/255, "g": 34/255, "b": 68/255, "a": 1.0}
    rotation_correction = 0.402
    position["z"] += rotation_correction
    tdw_object.communicate([{"$type": "scale_object", "scale_factor": {"x": 0.4, "y": height, "z": 0.2}, "id": ramp_id},
                            {"$type": "set_color", "color": color
                                , "id": ramp_id},
                            {"$type": "teleport_object", "position": position, "id": ramp_id},
                            {"$type": "set_kinematic_state", "id": ramp_id, "is_kinematic": True, "use_gravity": False}
                            ])
    cube_id = tdw_object.add_object("prim_cube", position={"x": 5, "y": 10, "z": 5},
                                    rotation={"x": 0, "y": 0, "z": 0}, library="models_special.json")
    position["x"] -= 0.78
    if height == 1:
        p_height = 0.96
        p_y = 0.4742
    elif height == 0.6:
        p_height = 0.56
        p_y = 0.274
    else:
        p_height = 0.26
        p_y = 0.123

    # -4.119
    tdw_object.communicate(
        [{"$type": "scale_object", "scale_factor": {"x": 0.4, "y": p_height, "z": 0.39}, "id": cube_id},
         {"$type": "set_color", "color":
             color, "id": cube_id},
         {"$type": "teleport_object", "position": {"x": position["x"], "y": p_y, "z": position["z"] + -0.194},
          "id": cube_id},
         {"$type": "set_kinematic_state", "id": cube_id, "is_kinematic": True, "use_gravity": False}
         ])



def settle_objects(tdw_object, n=100, counter=0):
    for _ in range(n):
        resp = tdw_object.communicate({"$type": "do_nothing"})
        if counter != 0:
            images = Images(resp[0])
            TDWUtils.save_images(images, f"image-{counter}", output_directory="data")
            counter += 1


def enable_images(tdw_object, single_camera=False):
    cmd = []
    avatar_ids = ["c"] if single_camera else ["a", "b", "c"]
    for avatar_id in avatar_ids:
        cmd.append({"$type": "set_pass_masks", "avatar_id": avatar_id, "pass_masks": ["_img", "_id", "_depth"]})
        # cmd.append({"$type": "set_pass_masks", "avatar_id": avatar_id, "pass_masks": ["_img", "_id"]})
    cmd.append({"$type": "send_images", "frequency": "always"})
    tdw_object.communicate(cmd)


def make_video(data_dir, video_name, output_dir="videos", camera_obj=None):
    # os.system(f"ffmpeg -f image2 -framerate 35 -i {data_dir}/img_image-%01d.png -vcodec libx264 -y -vb 100M {output_dir}/{video_name}")
    #
    img_no = 35*1
    idx = 0
    if camera_obj is not None:
        for _ in range(img_no):
            img = np.zeros([camera_obj.height, camera_obj.width, 3]).astype(np.uint8)
            # img[:, :, :] = 255
            img = images.fromarray(img)
            img.save(os.path.join(data_dir, f"new_img_image-{idx}.png"))
            idx += 1
        for _ in range(img_no):
            copyfile(os.path.join(data_dir, f"img_image-{0}.png"), os.path.join(data_dir, f"new_img_image-{idx}.png"))
            idx += 1
        image_list = len(glob.glob(f"{data_dir}/img_image-*.png"))
        for img in range(image_list):
            copyfile(os.path.join(data_dir, f"img_image-{img}.png"), os.path.join(data_dir, f"new_img_image-{idx}.png"))
            idx += 1
        for _ in range(img_no):
            copyfile(os.path.join(data_dir, f"img_image-{image_list-1}.png"), os.path.join(data_dir, f"new_img_image-{idx}.png"))
            idx += 1
        # os.system(
        #     f"ffmpeg -f image2 -framerate 35 -i {data_dir}/new_img_image-%01d.png -vcodec mpeg4 -y -vb 100M {output_dir}/{video_name}")

        os.system(f"ffmpeg -framerate 35 -i {data_dir}/new_img_image-%01d.png -vcodec libx264 -pix_fmt yuv420p -y -profile:v baseline -level 3 {output_dir}/{video_name}")
        image_list = glob.glob(f"{data_dir}/new_img_image-*.png")
        os.system(f"ffmpeg -framerate 35 -i {data_dir}/id_image-%01d.png -vcodec libx264 -pix_fmt yuv420p -y -profile:v baseline -level 3 {output_dir}/mask_{video_name}")
        os.system(f"ffmpeg -framerate 35 -i {data_dir}/depth_image-%01d.png -vcodec libx264 -pix_fmt yuv420p -y -profile:v baseline -level 3 {output_dir}/depth_{video_name}")
        for img in image_list:
            os.remove(img)
    else:
        os.system(f"ffmpeg -f image2 -framerate 35 -i {data_dir}/img_image-%01d.png -vcodec mpeg4 -y -vb 100M {output_dir}/{video_name}")
        os.system(f"ffmpeg -f image2 -framerate 35 -i {data_dir}/id_image-%01d.png -vcodec mpeg4 -y -vb 100M {output_dir}/mask_{video_name}")




def teleport(tdw_object, position, obj_id):
    return tdw_object.communicate({"$type": "teleport_object", "position": position, "id": obj_id})


def turn_off_physics(tdw_object, obj_list):
    cmd = [{"$type": "set_kinematic_state", "id": objs, "is_kinematic": True, "use_gravity": False} for objs in obj_list]
    tdw_object.communicate(cmd)


def create_dangerous_objects(tdw_object, position):
    cone = tdw_object.add_object("prim_cone", position={"x": 5, "y": 10, "z": 5},
                                    rotation={"x": 0, "y": 0, "z": 0}, library="models_special.json")
    tdw_object.communicate(
        [{"$type": "scale_object", "scale_factor": {"x": 0.2, "y": 0.2, "z": 0.2}, "id": cone},
         {"$type": "set_kinematic_state", "id": cone, "is_kinematic": True, "use_gravity": False},
         {"$type": "set_color", "color":
             {"r": 1, "g": 0.5156862754, "b": 0, "a": 1.0}, "id": cone},
         {"$type": "teleport_object", "position": position, "id": cone}
         ])


def create_raised_ground(tdw_object, position, width, depth=7, height=0.9):
    cube_id = tdw_object.add_object("prim_cube", position={"x": 5, "y": 10, "z": 5},
                                    rotation={"x": 0, "y": 0, "z": 0}, library="models_special.json")
    height += scene_config.pit_depth_
    tdw_object.communicate(
        [{"$type": "scale_object", "scale_factor": {"x": width, "y": height, "z": depth}, "id": cube_id},
         {"$type": "set_kinematic_state", "id": cube_id, "is_kinematic": True, "use_gravity": False},
         {"$type": "set_color", "color":
             {"r": 0.4, "g": 0.6, "b": 0.6, "a": 1.0}, "id": cube_id},
         {"$type": "set_texture_scale", "object_name": "PrimCube", "id": cube_id, "scale": {"x": 1, "y": 1}},
         {"$type": "teleport_object", "position": position, "id": cube_id}
         ])
    return cube_id


def create_base_scene(tdw_object, args, single_camera=False, scene_3_camera=False):
    scene_config = SceneConfiguration()
    # Create the output directory.
    tdw_object.communicate(TDWUtils.create_empty_room(12, 12))
    walls = []
    tdw_object.communicate(
        {"$type": "set_proc_gen_walls_scale", "walls": [{"x": 0, "y": -1}],
         "scale": {"x": 1, "y": 5, "z": 1}}
    )
    # Create the avatar.
    screen_scale = args.screen_scale
    if scene_3_camera:
        # camera_3_pos = {"x": 1.287, "y": 1.45, "z": 3.5 + scene_offset[2]}
        # camera_3_rot = {"x": 23.06, "y": -160.861, "z": 0}
        camera_3_pos = {"x": 0, "y": 1.678, "z": 4.974 + scene_offset[2]}
        camera_3_rot = {"x": 14.451, "y": 180, "z": 0}
        aspect_ratio = [13, 8]
        width, height = aspect_ratio[0]*screen_scale, aspect_ratio[1]*screen_scale
        field_of_view = 53
    else:
        camera_3_pos = {"x": 1, "y": 1.45, "z": 4.496 + scene_offset[2]}
        camera_3_rot = {"x": 23.06, "y": -154.898, "z": 0}
        # width, height = 210, 140
        # width, height = 1080, 720
        if screen_scale == 40:
            width, height = 420, 280
        else:
            width, height = 1080, 720
        field_of_view = 53
    camera_obj = Camera(camera_1_pos={"x": 0, "y": 0.461, "z": 5.001 + scene_offset[2]},
                        camera_1_rot={"x": 0, "y": 180.0, "z": 0},
                        camera_2_pos={"x": 0, "y": 5.137, "z": 0.031 + scene_offset[2]},
                        camera_2_rot={"x": 90, "y": 180.0, "z": 0},
                        # camera_3_pos={"x": 0, "y": 1.45, "z": 4.496 + scene_offset[2]},
                        # camera_3_rot={"x": 23.06, "y": 180.0, "z": 0}, scene_offset=scene_offset)
                        # camera_3_pos={"x": 1.0, "y": 1.45, "z": 4.496 + scene_offset[2]},
                        # camera_3_rot={"x": 23.06, "y": 200.0, "z": 0}, scene_offset=scene_offset)
                        # camera_3_pos={"x": 1.0, "y": 1.45, "z": 4.496 + scene_offset[2]},
                        # camera_3_rot={"x": 23.06, "y": -164, "z": 0}, scene_offset=scene_offset)
                        # New camera angle to compensate pushing barrier behind
                        camera_3_pos=camera_3_pos,
                        camera_3_rot=camera_3_rot, scene_offset=scene_offset,
                        width=width, height=height, screen_scale=screen_scale)


    tdw_object.communicate(camera_obj.create_camera(single_camera))
    tdw_object.communicate({"$type": "set_field_of_view", "field_of_view": field_of_view, "avatar_id": "c"})
    floor_material = random.sample(scene_config.floor_material, 1)[0]
    wall_material = random.sample(scene_config.wall_material, 1)[0]
    sky_box_cmd = tdw_object.get_add_hdri_skybox("furry_clouds_4k")
    sky_box_cmd["initial_skybox_rotation"] = 270
    sky_box_cmd["sun_initial_angle"] = 330
    sky_box_cmd["sun_elevation"] = 90
    resp = tdw_object.communicate([
        sky_box_cmd,
                      tdw_object.get_add_material(floor_material, library="materials_high.json"),
                      tdw_object.get_add_material(wall_material, library="materials_high.json"),
                      {"$type": "set_proc_gen_floor_material", "name": floor_material},
                      {"$type": "set_proc_gen_walls_material", "name": wall_material},
                      {"$type": "set_proc_gen_walls_texture_scale", "scale": {"x": 1.5, "y": 1.5}},
                      {"$type": "set_proc_gen_floor_texture_scale", "scale": {"x": 5, "y": 5}}])
    print_log(resp)
    # Create thin cube
    cube_id = 3245678
    tdw_object.communicate(
        [
            tdw_object.get_add_object("prim_cube", cube_id, position={"x": 0, "y": 0, "z": -2.42},
                                      rotation={"x": 0, "y": 0, "z": 0}, library="models_special.json"),
            {"$type": "scale_object", "scale_factor": {"x": 13, "y": 0.004, "z": 6},
             "id": cube_id},
            {"$type": "set_visual_material", "material_index": 0, "material_name": floor_material, "object_name": "PrimCube",
             "id": cube_id},
            {"$type": "set_texture_scale", "object_name": "PrimCube", "id": 3245678, "scale": {"x": 5, "y": 5}},
            {"$type": "set_kinematic_state", "id": cube_id, "is_kinematic": True, "use_gravity": False},
            # {"$type": "set_physic_material", "dynamic_friction": 0.35, "static_friction": 0.35,
            {"$type": "set_physic_material", "dynamic_friction": 0.0, "static_friction": 0.0,
             "bounciness": 0, "id": cube_id}
        ])
    tdw_object.communicate([
        {"$type": "set_post_exposure", "post_exposure": 0.3},
        {"$type": "set_contrast", "contrast": 0},
        {"$type": "set_saturation", "saturation": 5},
        {"$type": "set_screen_space_reflections", "enabled": True},
        {"$type": "set_vignette", "enabled": False}])
    return camera_obj


def create_color_samples(tdw_object):
    pos = {"x": 1.2, "y": 0.102, "z": -1.917}
    shapes = ["cone", "cube", "sphere"]
    for i, colors in enumerate(scene_config.agent_colors):
        shape = shapes[i%len(shapes)]
        create_target(position=pos.copy(), color=colors, tdw_object=tdw_object, object_type=shape)
        pos["x"] = pos["x"] - 0.3

        if pos["x"] <= -1.2:
            pos["x"] = 1.2
            pos["z"] -= 0.5
    pos["x"] = 1.2
    pos["z"] -= 0.5
    idx = 0
    for colors in scene_config.target_colors_["set_1"] :
        shape = scene_config.target_objects_[idx%len(scene_config.target_objects_)]
        idx += 1
        create_target(position=pos.copy(), color=colors, tdw_object=tdw_object, object_type=shape)
        pos["x"] = pos["x"] - 0.3

        if pos["x"] <= -1.2:
            pos["x"] = 1.2
            pos["z"] -= 0.5
    pos["x"] = 1.2
    pos["z"] -= 0.5
    for colors in scene_config.target_colors_["set_2"]:
        shape = scene_config.target_objects_[idx % len(scene_config.target_objects_)]
        idx += 1
        create_target(position=pos.copy(), color=colors, tdw_object=tdw_object, object_type=shape)
        pos["x"] = pos["x"] - 0.3

        if pos["x"] <= -1.2:
            pos["x"] = 1.2
            pos["z"] -= 0.3

def set_wall_floor_material(tdw_object, floor_material, wall_material, pit_obj, pit_width=0):
    cmd = [
            tdw_object.get_add_material(floor_material, library="materials_high.json"),
            tdw_object.get_add_material(wall_material, library="materials_high.json"),
            {"$type": "set_proc_gen_walls_material", "name": wall_material},
            {"$type": "set_proc_gen_walls_texture_scale", "scale": {"x": 1.5, "y": 1.5}},
        {"$type": "set_visual_material", "material_index": 0, "material_name": floor_material,
         "object_name": "PrimCube", "id": 3245678},
        {"$type": "set_texture_scale", "object_name": "PrimCube", "id": 3245678, "scale": {"x": 5, "y": 5}}
                           ]
    if pit_obj is not None:
        pit_ids = pit_obj.pit_ids
        pit_widths = pit_obj.pit_widths
    else:
        pit_ids = []
        pit_widths = []
    for pit_id, pit_width in zip(pit_ids, pit_widths):
        cmd.extend(
            [{"$type": "set_visual_material", "material_index": 0, "material_name": floor_material,
             "object_name": "PrimCube", "id": pit_id},
             {"$type": "set_texture_scale", "object_name": "PrimCube", "id": pit_id, "scale": {"x": pit_width*5/13, "y": 4.16}}
             ]
        )
    resp = tdw_object.communicate(cmd)
    print_log(resp)

def set_pit_material(pit_ids, floor_material, pit_width, tdw_object):
    cmd = []
    pit_width = scene_config.pit_width[pit_width] if pit_width != -1 else 12
    for pit_id in pit_ids:
        cmd.extend(
            [{"$type": "set_visual_material", "material_index": 0, "material_name": floor_material,
              "object_name": "PrimCube", "id": pit_id},
             {"$type": "set_texture_scale", "object_name": "PrimCube", "id": pit_id,
              "scale": {"x": pit_width * 5 / 13, "y": 4.16}}
             ]
        )
    resp = tdw_object.communicate(cmd)
    print_log(resp)


def select_material(args):
    wall_material = random.sample(scene_config.wall_material, k=1)[0]
    floor_material = random.sample(scene_config.floor_material, k=1)[0]
    agent_color = random.sample(scene_config.agent_colors, k=1)[0]
    target_color_sets = [1, 2]
    random.shuffle(target_color_sets)
    goal_1_color = random.choice(scene_config.target_colors_[f"set_{target_color_sets[0]}"])
    goal_2_color = random.choice(scene_config.target_colors_[f"set_{target_color_sets[1]}"])
    shapes = scene_config.agent_types.copy()
    random.shuffle(shapes)
    agent_shape = shapes[0]
    target_1_shape, target_2_shape = shapes[1], shapes[2]
    if args.use_novel_objects:
        shapes = [random.choice(scene_config.target_objects[f"target_objects_{target_color_sets[0]}"]),
                   random.choice(scene_config.target_objects[f"target_objects_{target_color_sets[1]}"]),
                   ]
        target_1_shape, target_2_shape = shapes[0], shapes[1]

    return {
        "agent_color": agent_color,
        "wall_material": wall_material,
        "agent_shape": agent_shape,
        "floor_material": floor_material,
        "goal_1_color": goal_1_color,
        "goal_2_color": goal_2_color,
        "goal_1_shape": target_1_shape,
        "goal_2_shape": target_2_shape
    }


def get_scene_materials(tdw_object, args):
    materials = select_material(args)
    set_wall_floor_material(tdw_object, materials["floor_material"], materials["wall_material"], None)
    return materials


def convert_to_radians(degrees):
    return (degrees/180) * math.pi


def euler_to_quaternion(roll, pitch, yaw):
    qx = np.sin(roll / 2) * np.cos(pitch / 2) * np.cos(yaw / 2) - np.cos(roll / 2) * np.sin(pitch / 2) * np.sin(
        yaw / 2)
    qy = np.cos(roll / 2) * np.sin(pitch / 2) * np.cos(yaw / 2) + np.sin(roll / 2) * np.cos(pitch / 2) * np.sin(
        yaw / 2)
    qz = np.cos(roll / 2) * np.cos(pitch / 2) * np.sin(yaw / 2) - np.sin(roll / 2) * np.sin(pitch / 2) * np.cos(
        yaw / 2)
    qw = np.cos(roll / 2) * np.cos(pitch / 2) * np.cos(yaw / 2) + np.sin(roll / 2) * np.sin(pitch / 2) * np.sin(
        yaw / 2)

    return [qx, qy, qz, qw]



def rotate_object(tdw_object, rotation_angle, obj_id):
    tdw_object.communicate({"$type": "rotate_object_to_euler_angles", "euler_angles": rotation_angle,
     "id": obj_id})

def rotate_point(origin, point, angle):
    """
    Rotate a point counterclockwise by a given angle around a given origin.

    The angle should be given in radians.
    """
    ox, oy = origin
    px, py = point

    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return np.array([qx, qy])
# def generate_video():
#     images = os.listdir("data")
#     print(images)
#
#
# generate_video()




def distance_of_point_from_line(p1, p2, point):
    return np.linalg.norm(np.cross(p2 - p1, p1 - point)) / np.linalg.norm(p2 - p1)

def comp_travel_3d(traj):
    """travel distance"""
    T = len(traj)
    dist = {'x': 0, 'y': 0, 'z': 0}
    for t in range(T - 1):
        for d in ['x', 'y', 'z']:
            dist[d] += abs(traj[t + 1][d] - traj[t][d])
    return dist


def list_single_goal_scenes():
    config_list = []

    if os.path.isfile("../scene_data/single_goal_scenes.pickle"):
        with open("../scene_data/single_goal_scenes.pickle", "rb") as fp:
            path_force_dist = pickle.load(fp)
            print("Found data")
            return path_force_dist
    for directory in ["barrier_scenes", "pit_scenes", "barrier_with_door_scenes", "platform_scenes", "ramp_scenes"]:
    # for directory in ["platform_scenes", "ramp_scenes"]:
        output_dirs = os.listdir(os.path.join(directory))
        for output_dir in output_dirs:
            if os.path.isdir(os.path.join(directory, output_dir)):
                config_list.extend([os.path.join(directory, output_dir, e)
                                    for e in os.listdir(os.path.join(directory, output_dir)) if
                                    os.path.isdir(os.path.join(directory, output_dir, e))])
    config_paths = []
    for config in config_list:
        config_paths.extend(
            [os.path.join(config, e).split("/") for e in os.listdir(config) if os.path.isdir(os.path.join(config, e))]
        )
    # Read force and distance
    idx = 0
    path_force_dist = []
    for path in tqdm(config_paths):
        # try:
        with open(os.path.join(*path[0:-1], "scene_config.json"), "r") as fp:
            scene_config_ = json.load(fp)
        with open(os.path.join(*path, "../state_info.json"), "r") as fp:
            state_data = json.load(fp)
        total_force = [0, 0, 0]
        pos = []
        obstacle_height, obstacle_width, obstacle_depth = None, None, None
        if scene_config_["barrier_type"] in ["cube", "barrier_with_door"]:
            obstacle_height = scene_config_["obstacle_height"]
            obstacle_width = scene_config_["obstacle_width"]
            obstacle_depth = scene_config_["obstacle_depth"]
            object_positions = [scene_config_["agent_pos_x"], scene_config_["agent_pos_z"],
                                scene_config_["obstacle_pos_x"], scene_config_["obstacle_pos_z"],
                                scene_config_["obj_pos_x"], scene_config_["obj_pos_z"]]
        elif scene_config_["barrier_type"] in ["pit", "pit-with-bridge"]:
            obstacle_height = 0
            obstacle_width = scene_config_["pit_width"]
            obstacle_depth = 0
            object_positions = [
                scene_config_["agent_pos_x"], scene_config_["agent_pos_z"],
                1, scene_config_["bridge_z"] if scene_config_["barrier_type"] == "pit-with-bridge" else 1,
                scene_config_["obj_pos_x"], scene_config_["obj_pos_z"]
            ]
        elif scene_config_["barrier_type"] in "ramp":
            obstacle_height = scene_config_["ramp_height"]
            obstacle_width = scene_config_["ramp_rotation"]
            object_positions = [scene_config_["agent_pos_x"], scene_config_["agent_pos_z"],
                                0, 0,
                                scene_config_["obj_pos_ramp"], 0]
        elif scene_config_["barrier_type"] in "platform":
            obstacle_height = scene_config_["ramp_height"]
            object_positions = [scene_config_["agent_pos_x"], scene_config_["agent_pos_z"],
                                0, 0,
                                scene_config_["obj_pos_ramp_x"], scene_config_["obj_pos_ramp_z"]]
        for f in state_data:
            total_force[0] += abs(f["agent"]["force"]["x"])
            total_force[1] += abs(f["agent"]["force"]["y"])
            total_force[2] += abs(f["agent"]["force"]["z"])
            meta_data = f["agent"]["path_meta_data"]
            pos.append({"x": f["agent"]["position"][0], "y": f["agent"]["position"][1], "z": f["agent"]["position"][2]})
        dist = comp_travel_3d(pos)
        dist = [round(dist["x"], 4), round(dist["y"], 4), round(dist["z"], 4)]
        path_force_dist.append((path, total_force, dist, obstacle_height, obstacle_width, obstacle_depth, *meta_data[1:], *object_positions))
        # except Exception as err:
        #     print(os.path.join(*path))
    with open("../scene_data/single_goal_scenes.pickle", "wb") as fp:
        pickle.dump(path_force_dist, fp)
    return path_force_dist


def get_single_goal_scenes():
    goal_list = list_single_goal_scenes()
    goal_list = [e[0] + e[1] + e[2] + list(e[3:]) for e in goal_list]
    goal_list = pd.DataFrame(goal_list, columns=["scene_type", "output", "config", "path", "force_x",
                                                       "force_y", "force_z", "distance_x", "distance_y",
                                                       "distance_z", "obstacle_height", "obstacle_width",
                                                 "obstacle_depth", "path_type", "path_val_1", "path_val_2",
                                                 "agent_x", "agent_z", "obstacle_pos_x", "obstacle_pos_z",
                                                 "obj_pos_x", "obj_pos_z"])

    return goal_list


def get_two_goal_scenes():
    goal_list = list_two_goal_scenes()

    goal_list = [e[0] + e[1] + e[2] + list(e[3:]) for e in goal_list]

    goal_list = pd.DataFrame(goal_list,
                               columns=["scene_type", "output", "config", "path", "force_x",
                                        "force_y", "force_z", "distance_x", "distance_y",
                                        "distance_z", "target", "obstacle_height_1","obstacle_width_1",
                                        "obstacle_depth_1", "obstacle_height_2", "obstacle_width_2",
                                        "obstacle_depth_2", "path_type", "path_val_1", "path_val_2",
                                        "obstacle_1_pos_x", "obstacle_1_pos_z", "obj_1_pos_x", "obj_1_pos_z",
                                        "obstacle_2_pos_x", "obstacle_2_pos_z", "obj_2_pos_x", "obj_2_pos_z", "agent_pos_z"
                                        ])

    return goal_list


def print_log(response):
    for r in response:
        r_id = OutputData.get_data_type_id(r)
        if r_id == "logm":
            l = LogMessage(r)
            print(l.get_message())

def In_history(element, history):
    fam, test = set(element[0]), set(element[1])
    for e in history:
        if fam == e[0] and test == e[1]:
            return True
    return False


def get_scene_2_action_efficiency_paths(scene_type, scene_1_list_cost,
                                        NUM_OF_FAMILIRIZATION_VIDEOS, test_type, history, obstacle_type):
    all_efficient_paths = scene_1_list_cost[
        (scene_1_list_cost["scene_type"] == scene_type) & (scene_1_list_cost["path_type"] != "Do-nothing")]
    all_efficient_paths_go_around = all_efficient_paths[
        all_efficient_paths["path_type"].isin(["Around-barrier-top", "Around-barrier-bottom"])]
    all_efficient_paths_go_around = all_efficient_paths_go_around.loc[
        all_efficient_paths_go_around.groupby(["config"])["cost"].idxmin()]

    while True:
        type_ = random.choice(["Jump", "go-around"])
        if test_type in ["Type-2.1", "Type-2.2"]:
            # try:
            if obstacle_type == "barrier":
                if type_ == "Jump":
                    slices_data = all_efficient_paths[
                        (all_efficient_paths["obstacle_height"] > 1) &
                        (all_efficient_paths["path_type"] == "Jump")
                           ]
                else:
                    slices_data = all_efficient_paths_go_around[
                       (all_efficient_paths_go_around["obstacle_depth"] > 3) &
                       (all_efficient_paths_go_around["obj_pos_z"] == all_efficient_paths_go_around["agent_z"]) &
                       (all_efficient_paths_go_around["obj_pos_z"] == all_efficient_paths_go_around[ "obstacle_pos_z"]) &
                       (all_efficient_paths_go_around["path_type"].isin(
                           ["Around-barrier-top", "Around-barrier-bottom"]))
                           ]
                if test_type == "Type-2":
                    slices_data = slices_data[
                        (slices_data["obstacle_width"] < 2) &
                        (slices_data["obstacle_pos_z"].isin([0, 1]))
                    ]
                fam = slices_data.iloc[random.choice(range(slices_data.shape[0]))]


                if test_type in ["Type-2.1", "Type-2.2"]:
                    slices_data = all_efficient_paths[
                        (all_efficient_paths["agent_x"] == fam["agent_x"]) &
                        (all_efficient_paths["agent_z"] == fam["agent_z"]) &
                        (all_efficient_paths["obj_pos_x"] == fam["obj_pos_x"]) &
                        (all_efficient_paths["obj_pos_z"] == fam["obj_pos_z"]) &
                        (all_efficient_paths["obstacle_pos_x"] == fam["obstacle_pos_x"]) &
                        (all_efficient_paths["obstacle_pos_z"] == fam["obstacle_pos_z"])
                        ]

                    test_b = slices_data[(slices_data["obstacle_height"] == 0) &
                                         (slices_data["path_type"] == "Straight-Target")]
                    test_b = test_b.iloc[random.choice(range(test_b.shape[0]))]
                    return [fam], [fam, test_b], history
            elif obstacle_type == "pit":

                slices_data = scene_1_list_cost[
                    (scene_1_list_cost["scene_type"] == "pit_scenes") &
                    (scene_1_list_cost["path_type"] == "Pit_Jump") &
                    (scene_1_list_cost["obj_pos_z"] == scene_1_list_cost["agent_z"])
                    ]

                if test_type == "Type-2.2":
                    slices_data = slices_data[
                        (slices_data["obstacle_width"] < 2)
                    ]
                fam = slices_data.iloc[random.choice(range(slices_data.shape[0]))]
                test_b = scene_1_list_cost[
                    (scene_1_list_cost["agent_x"] == fam["agent_x"]) &
                    (scene_1_list_cost["agent_z"] == fam["agent_z"]) &
                    (scene_1_list_cost["obj_pos_x"] == fam["obj_pos_x"]) &
                    (scene_1_list_cost["obj_pos_z"] == fam["obj_pos_z"]) &
                    (scene_1_list_cost["scene_type"] == "pit_scenes") &
                    (scene_1_list_cost["path_type"] == "Straight-Target")
                    ]
                test_b = test_b.iloc[random.choice(range(test_b.shape[0]))]
                return [fam], [fam, test_b], history
            # except:
            #     continue
        elif test_type in ["Type-2.3"]:
            try:
                if type_ == "Jump":
                    slices_data = all_efficient_paths[
                        (all_efficient_paths["obstacle_height"] > 3) &
                        (all_efficient_paths["path_type"] == "Jump")
                           ]
                else:
                    slices_data = all_efficient_paths_go_around[
                       (all_efficient_paths_go_around["obstacle_depth"] > 2) & (
                            all_efficient_paths_go_around["path_type"].isin(
                                ["Around-barrier-top", "Around-barrier-bottom"]))
                           ]

                if type_ == "Jump":
                    data_with_jump = slices_data[slices_data["path_type"] == "Jump"]
                    fam = data_with_jump.iloc[random.choice(range(data_with_jump.shape[0]))]
                    configs_with_same_positions = all_efficient_paths[
                        (all_efficient_paths["agent_x"] == fam["agent_x"]) &
                        (all_efficient_paths["agent_z"] == fam["agent_z"]) &
                        (all_efficient_paths["obj_pos_x"] == fam["obj_pos_x"]) &
                        (all_efficient_paths["obj_pos_z"] == fam["obj_pos_z"]) &
                        (all_efficient_paths["obstacle_pos_x"] == fam["obstacle_pos_x"]) &
                        (all_efficient_paths["obstacle_pos_z"] == fam["obstacle_pos_z"])
                        ]
                    data_with_jump_smaller_barrier = configs_with_same_positions[
                        (configs_with_same_positions["obstacle_height"] < (fam["obstacle_height"]-1)) &
                        (configs_with_same_positions["obstacle_width"] == fam["obstacle_width"]) &
                        (configs_with_same_positions["path_type"] == "Jump")
                    ]
                    test_b = data_with_jump_smaller_barrier.iloc[random.choice(range(data_with_jump_smaller_barrier.shape[0]))]
                    return [fam], [fam, test_b], history
                else:
                    data_with_go_around = slices_data[slices_data["path_type"].isin(["Around-barrier-top", "Around-barrier-bottom"])]
                    fam = data_with_go_around.iloc[random.choice(range(data_with_go_around.shape[0]))]
                    configs_with_same_positions = all_efficient_paths[
                        (all_efficient_paths["agent_x"] == fam["agent_x"]) &
                        (all_efficient_paths["agent_z"] == fam["agent_z"]) &
                        (all_efficient_paths["obj_pos_x"] == fam["obj_pos_x"]) &
                        (all_efficient_paths["obj_pos_z"] == fam["obj_pos_z"]) &
                        (all_efficient_paths["obstacle_pos_x"] == fam["obstacle_pos_x"]) &
                        (all_efficient_paths["obstacle_pos_z"] == fam["obstacle_pos_z"])
                        ]

                    data_with_go_around_smaller_barrier = configs_with_same_positions[
                        (configs_with_same_positions["obstacle_depth"] < 2) &
                        (configs_with_same_positions["obstacle_width"] == fam["obstacle_width"]) &
                        (configs_with_same_positions["path_type"] == fam["path_type"])
                        ]
                    test_b = data_with_go_around_smaller_barrier.iloc[random.choice(range(data_with_go_around_smaller_barrier.shape[0]))]
                    return [fam], [fam, test_b], history
            except:
                continue
        elif test_type in ["Type-2.4"]:
            try:
                # Find scenario with going around and decrease depth
                if obstacle_type == "barrier_scenes":
                    if type_ == "Jump":
                        slices_data = all_efficient_paths[
                            ((all_efficient_paths["obstacle_height"] < 6) &
                             (all_efficient_paths["obstacle_height"] > 1) &
                             (all_efficient_paths["path_type"] == "Jump"))
                            ]
                        row = slices_data.iloc[random.choice(range(slices_data.shape[0]))]
                        all_scenario_with_same_agent_goal = all_efficient_paths[
                            (all_efficient_paths["agent_x"] == row["agent_x"]) &
                            (all_efficient_paths["agent_z"] == row["agent_z"]) &
                            (all_efficient_paths["obj_pos_x"] == row["obj_pos_x"]) &
                            (all_efficient_paths["obj_pos_z"] == row["obj_pos_z"]) &
                            (all_efficient_paths["obstacle_pos_x"] == row["obstacle_pos_x"]) &
                            (all_efficient_paths["obstacle_pos_z"] == row["obstacle_pos_z"])
                            ]

                        all_scenario_with_opp_action = all_scenario_with_same_agent_goal[
                            ((all_scenario_with_same_agent_goal["obstacle_height"] == row["obstacle_height"]) &
                             (all_scenario_with_same_agent_goal["obstacle_width"] == row["obstacle_width"]) &
                             ((row["cost"] - all_scenario_with_same_agent_goal["cost"]) > 2) &
                             (all_scenario_with_same_agent_goal["path_type"].isin(["Around-barrier-top", "Around-barrier-bottom"])))
                        ]
                    else:

                        slices_data = all_efficient_paths[
                            (all_efficient_paths["obstacle_depth"] < 4) &
                            (all_efficient_paths["obstacle_depth"] > 1) &
                            (all_efficient_paths["obstacle_height"] > 4) &
                            (all_efficient_paths["path_type"].isin(["Around-barrier-top", "Around-barrier-bottom"]))
                        ]


                        # For every row check if the counter config exist with Jump path
                        slices_data["available"] = "no"
                        cnt = 0
                        for i in range(slices_data.shape[0]):
                            current_record = slices_data.iloc[i]

                            columns_with_same_positions = all_efficient_paths[
                                (all_efficient_paths["agent_x"] == current_record["agent_x"]) &
                                (all_efficient_paths["agent_z"] == current_record["agent_z"]) &
                                (all_efficient_paths["obj_pos_x"] == current_record["obj_pos_x"]) &
                                (all_efficient_paths["obj_pos_z"] == current_record["obj_pos_z"]) &
                                (all_efficient_paths["obstacle_pos_x"] == current_record["obstacle_pos_x"]) &
                                (all_efficient_paths["obstacle_pos_z"] == current_record["obstacle_pos_z"])
                            ]
                            columns_with_same_positions = columns_with_same_positions[
                                (columns_with_same_positions["path_type"] == "Jump") &
                                (columns_with_same_positions["cost"] < current_record["cost"])
                                ]
                            if columns_with_same_positions.shape[0] > 1:
                                slices_data.loc[current_record.name, ["available"]] = "yes"

                                cnt += 1

                        slices_data = slices_data[slices_data["available"] == "yes"]

                        row = slices_data.iloc[random.choice(range(slices_data.shape[0]))]
                        all_scenario_with_same_agent_goal = all_efficient_paths[
                            (all_efficient_paths["agent_x"] == row["agent_x"]) &
                            (all_efficient_paths["agent_z"] == row["agent_z"]) &
                            (all_efficient_paths["obj_pos_x"] == row["obj_pos_x"]) &
                            (all_efficient_paths["obj_pos_z"] == row["obj_pos_z"]) &
                            (all_efficient_paths["obstacle_pos_x"] == row["obstacle_pos_x"]) &
                            (all_efficient_paths["obstacle_pos_z"] == row["obstacle_pos_z"])
                            ]

                        all_scenario_with_opp_action = all_scenario_with_same_agent_goal[
                            (
                            (all_scenario_with_same_agent_goal["obstacle_width"] == row["obstacle_width"]) &
                            (all_scenario_with_same_agent_goal["obstacle_depth"] == row["obstacle_depth"]) &
                             (row["cost"] > all_scenario_with_same_agent_goal["cost"] ) &
                             (all_scenario_with_same_agent_goal["path_type"].isin(["Jump"]))
                            )
                        ]
                    opp_action_efficient = all_scenario_with_opp_action.iloc[random.choice(range(all_scenario_with_opp_action.shape[0]))]
                    # Find scenario with same
                    return [row], [row, opp_action_efficient], history
                elif obstacle_type == "pit-with-bridge":
                    slices_data = scene_1_list_cost[
                        (scene_1_list_cost["scene_type"] == "pit_scenes") &
                        (scene_1_list_cost["path_type"] == "Pit_Jump") &
                        (scene_1_list_cost["agent_z"] == scene_1_list_cost["obj_pos_z"])
                        ]

                    fam = slices_data.iloc[random.choice(range(slices_data.shape[0]))]
                    test_b = scene_1_list_cost[
                        (scene_1_list_cost["agent_x"] == fam["agent_x"]) &
                        (scene_1_list_cost["agent_z"] == fam["agent_z"]) &
                        (scene_1_list_cost["obj_pos_x"] == fam["obj_pos_x"]) &
                        (scene_1_list_cost["obj_pos_z"] == fam["obj_pos_z"]) &
                        (scene_1_list_cost["obstacle_pos_z"] == fam["obj_pos_z"]) &
                        (scene_1_list_cost["obstacle_width"] == fam["obstacle_width"]) &
                        (scene_1_list_cost["scene_type"] == "pit_scenes") &
                        (scene_1_list_cost["path_type"] == "Cross-Bridge")
                        ]
                    test_b = test_b.iloc[random.choice(range(test_b.shape[0]))]
                    return [fam], [fam, test_b], history
                elif obstacle_type == "barrier_with_door":
                    z_loc = random.choice([0, 1, 2])
                    slices_data = all_efficient_paths[
                        ((all_efficient_paths["obstacle_height"] > 4) &
                         (all_efficient_paths["obstacle_width"] < 2) &
                         (all_efficient_paths["path_type"] == "Jump"))
                           ]
                    slices_data = slices_data[
                        (slices_data["agent_z"] == z_loc) &
                        (slices_data["obj_pos_z"] == z_loc) &
                        (slices_data["obstacle_pos_z"] == z_loc)
                    ]
                    fam = slices_data.iloc[random.choice(range(slices_data.shape[0]))]

                    slices_data = scene_1_list_cost[
                        (scene_1_list_cost["agent_x"] == fam["agent_x"]) &
                        (scene_1_list_cost["agent_z"] == fam["agent_z"]) &
                        (scene_1_list_cost["obj_pos_x"] == fam["obj_pos_x"]) &
                        (scene_1_list_cost["obj_pos_z"] == fam["obj_pos_z"]) &
                        (scene_1_list_cost["obstacle_pos_x"] == fam["obstacle_pos_x"]) &
                        (scene_1_list_cost["obstacle_pos_z"] == fam["obstacle_pos_z"]) &
                        (scene_1_list_cost["path_type"] == "barrier-door")
                        ]

                    test_b = slices_data.iloc[random.choice(range(slices_data.shape[0]))]
                    return [fam], [fam, test_b], history
            except:
                continue
        elif test_type in ["Type-2.5"]:
            type_ = random.choice(["Jump", "go-around"])
            if type_ == "Jump":
                slices_data = all_efficient_paths[
                    (all_efficient_paths["obstacle_height"].isin([1, 2, 3])) &
                    (all_efficient_paths["path_type"] == "Jump")
                    ]
            else:
                slices_data = all_efficient_paths_go_around[
                    (all_efficient_paths_go_around["obstacle_depth"].isin([0, 1])) &
                    (all_efficient_paths_go_around["obstacle_width"].isin([0])) &
                    (all_efficient_paths_go_around["obj_pos_z"] == all_efficient_paths_go_around["agent_z"]) &
                    (all_efficient_paths_go_around["obj_pos_z"] == all_efficient_paths_go_around[
                        "obstacle_pos_z"]) &
                    (all_efficient_paths_go_around["path_type"].isin(
                        ["Around-barrier-top", "Around-barrier-bottom"]))
                    ]
            fam = slices_data.iloc[random.choice(range(slices_data.shape[0]))]
            if type_ == "Jump":
                slices_data = all_efficient_paths[
                    (all_efficient_paths["obstacle_height"].isin([5, 6])) &
                    (all_efficient_paths["path_type"] == "Jump")
                    ]
            else:
                slices_data = all_efficient_paths_go_around[
                    (all_efficient_paths_go_around["obstacle_depth"].isin([3])) &
                    (all_efficient_paths_go_around["obstacle_width"].isin([2, 3])) &
                    (all_efficient_paths_go_around["obj_pos_z"] == all_efficient_paths_go_around["agent_z"]) &
                    (all_efficient_paths_go_around["obj_pos_z"] == all_efficient_paths_go_around[
                        "obstacle_pos_z"]) &
                    (all_efficient_paths_go_around["path_type"].isin(
                        ["Around-barrier-top", "Around-barrier-bottom"]))
                    ]
            test_b = slices_data[
                (slices_data["agent_x"] == fam["agent_x"]) &
                (slices_data["agent_z"] == fam["agent_z"]) &
                (slices_data["obj_pos_x"] == fam["obj_pos_x"]) &
                (slices_data["obj_pos_z"] == fam["obj_pos_z"]) &
                (slices_data["obstacle_pos_x"] == fam["obstacle_pos_x"]) &
                (slices_data["obstacle_pos_z"] == fam["obstacle_pos_z"])
            ]
            test_b = test_b.iloc[random.choice(range(test_b.shape[0]))]
            return [fam], [fam, test_b], history


def get_scene_3_unobserved_constraints_paths(scene_type, scene_1_list_cost, scene_1_list_cost_without_agent,
                                             NUM_OF_FAMILIRIZATION_VIDEOS, test_type, history, obstacle_type):
    sliced_scenes = scene_1_list_cost[
        (scene_1_list_cost["scene_type"] == scene_type) & (scene_1_list_cost["path_type"] != "Do-nothing")]
    sliced_scenes = sliced_scenes[(sliced_scenes["obstacle_height"] > 1) &
                                  # (sliced_scenes["obstacle_width"] < 4) &
                                  # (sliced_scenes["obstacle_depth"] < 3)]
                                  (sliced_scenes["obstacle_depth"].isin([3, 4]))]
    sliced_scenes = sliced_scenes[
        (abs(sliced_scenes["agent_z"] - sliced_scenes["obstacle_pos_z"]) < 2) &
        (abs(sliced_scenes["obj_pos_z"] - sliced_scenes["obstacle_pos_z"]) < 2)
        ]
    all_efficient_paths_go_around = sliced_scenes[
        sliced_scenes["path_type"].isin(["Around-barrier-top", "Around-barrier-bottom"])]
    all_efficient_paths_go_around = all_efficient_paths_go_around.loc[
        all_efficient_paths_go_around.groupby(["config"])["cost"].idxmin()]
    all_efficient_paths = sliced_scenes

    while True:
        if scene_type == "barrier_scenes":
            type_ = random.choice(["Jump", "go-around"])
            # try:
            if test_type in ["Type-3.1"]:
                if obstacle_type == "barrier":
                    if type_ == "Jump":
                        all_valid_paths = all_efficient_paths[
                            (all_efficient_paths["obstacle_height"] > 1) &
                            (all_efficient_paths["path_type"] == "Jump")
                            ]
                    else:
                        all_valid_paths = all_efficient_paths_go_around[
                            (all_efficient_paths_go_around["obstacle_depth"] > 1) &
                            (all_efficient_paths_go_around["obj_pos_z"] == all_efficient_paths_go_around["agent_z"]) &
                            (all_efficient_paths_go_around["obj_pos_z"] == all_efficient_paths_go_around["obstacle_pos_z"])
                            ]
                    fam = all_valid_paths.iloc[random.choice(range(all_valid_paths.shape[0]))]
                    return [fam], [fam, fam], history
                elif obstacle_type == "pit":
                    slices_data = scene_1_list_cost[
                        (scene_1_list_cost["scene_type"] == "pit_scenes") &
                        (scene_1_list_cost["path_type"] == "Pit_Jump")
                        ]
                    fam = slices_data.iloc[random.choice(range(slices_data.shape[0]))]
                    return [fam], [fam, fam], history
            elif test_type in ["Type-3.2"]:
                if obstacle_type == "barrier":
                    all_valid_paths = all_efficient_paths[
                        (all_efficient_paths["obstacle_height"] > 3) &
                        (all_efficient_paths["path_type"] == "Jump")
                        ]
                    fam = all_valid_paths.iloc[random.choice(range(all_valid_paths.shape[0]))]
                    return [fam], [fam, fam], history
                elif obstacle_type == "barrier_with_door":
                    all_valid_paths = scene_1_list_cost[
                        (scene_1_list_cost["obstacle_height"] > 4) &
                        (scene_1_list_cost["obstacle_width"].isin([0])) &
                        (scene_1_list_cost["obj_pos_z"] == scene_1_list_cost["agent_z"]) &
                        (scene_1_list_cost["path_type"] == "Straight-Target")
                        ]
                    fam = all_valid_paths.iloc[random.choice(range(all_valid_paths.shape[0]))]
                    return [fam], [fam, fam], history
                elif obstacle_type == "pit-with-bridge":
                    slices_data = scene_1_list_cost[
                        (scene_1_list_cost["scene_type"] == "pit_scenes") &
                        (scene_1_list_cost["path_type"] == "Pit_Jump")
                        ]
                    fam = slices_data.iloc[random.choice(range(slices_data.shape[0]))]
                    return [fam], [fam, fam], history
                elif obstacle_type in ["wall", "floating-wall"]:
                    all_valid_paths = scene_1_list_cost[
                        (scene_1_list_cost["scene_type"] == "barrier_scenes") &
                        (scene_1_list_cost["path_type"] == "Straight-Target")
                        ]
                    fam = all_valid_paths.iloc[random.choice(range(all_valid_paths.shape[0]))]
                    return [fam], [fam, fam], history


def get_scene_1_goal_preferences_paths(scene_type, goal_2_list_cost, scenario_sub_type, history, switch_goals, selected_target,
                                       obstacles_list_fam, obstacles_list_test):
    # "scene_type", "output", "config", "path", "force_x",
    # "force_y", "force_z", "distance_x", "distance_y",
    # "distance_z", "target", "obstacle_height_1", "obstacle_width_1",
    # "obstacle_depth_1", "obstacle_height_2", "obstacle_width_2",
    # "obstacle_depth_2", "path_type", "path_val_1", "path_val_2",
    # "obstacle_1_pos_x", "obstacle_1_pos_z", "obj_1_pos_x", "obj_1_pos_z",
    # "obstacle_2_pos_x", "obstacle_2_pos_z", "obj_2_pos_x", "obj_2_pos_z", "agent_pos_z"
    valid_configs = goal_2_list_cost[(goal_2_list_cost["scene_type"] == scene_type) &
                                     (goal_2_list_cost["path_type"] != "Do-nothing")]

    valid_configs_jumps = valid_configs[valid_configs["path_type"] == "Jump"]
    valid_configs = valid_configs.loc[valid_configs.groupby(["config", "target"])["cost"].idxmin()]

    # valid_configs.loc[(valid_configs["obj_2_pos_x"] == 3), ["obj_2_pos_x"]] = 1
    # valid_configs.loc[(valid_configs["obj_2_pos_x"] == 4), ["obj_2_pos_x"]] = 0
    target_1_pos_to_target_2_pos = {
        "target_1":
            {2: 4,
             1: 5,
             0: 6},
        "target_2":
            {4: 2,
             5: 1,
             6: 0}
    }
    while True:

        # try:
        if obstacles_list_test[0] == "barrier" and obstacles_list_test[1] == "barrier":
            return sample_trajectory.scene_1_goal_preference_v1(scenario_sub_type, selected_target, switch_goals, valid_configs,
                                                                target_1_pos_to_target_2_pos, history, valid_configs_jumps)
        else:
            return sample_trajectory.scene_1_goal_preference_v2(scenario_sub_type, selected_target, obstacles_list_fam,
                                                                obstacles_list_test, goal_2_list_cost, history, switch_goals)


def get_scene_4_cost_reward_trade_offs_paths(test_type, goal_1_list, goal_2_list, history, selected_target, switch_test_targets,
                                             object_type, object_type_test):
    goal_1_list = goal_1_list[goal_1_list["path_type"] != "Do-nothing"]
    goal_2_list_cost = goal_2_list.loc[goal_2_list.groupby(["scene_type", "config", "target"])["cost"].idxmin()]
    target_1_pos_to_target_2_pos = {
        "target_1":
            {2: 4,
             1: 5,
             0: 6},
        "target_2":
            {4: 2,
             5: 1,
             6: 0}
    }
    while True:
        action_type = random.choice(["Jump", "go-around"])
        # try:

        not_selected = "2" if selected_target == "1" else "1"
        if action_type == "Jump":
                #'Straight-Target', 'Around-barrier-bottom', 'Around-barrier-top'
                valid_fam_configs = goal_1_list[
                    (goal_1_list["path_type"].isin(["Jump", "Straight-Target"]))
                ]
                valid_test_configs = goal_2_list_cost
                max_try = 9
                while True:
                    try:
                        if object_type == "barrier":
                            hard_fam, med_fam_2, med_fam_1, easy_fam = sample_trajectory.get_scene_4_fam_wall(
                                valid_fam_configs, selected_target)
                        elif object_type == "pit":
                            hard_fam, med_fam_2, med_fam_1, easy_fam = sample_trajectory.get_scene_4_fam_pit(
                                goal_1_list, selected_target)
                        elif object_type == "platform":
                            hard_fam, med_fam_2, med_fam_1, easy_fam = sample_trajectory.get_scene_4_fam_platform(
                                goal_1_list, selected_target)
                        elif object_type == "ramp":
                            hard_fam, med_fam_2, med_fam_1, easy_fam = sample_trajectory.get_scene_4_fam_ramp(
                                goal_1_list, selected_target)
                        break
                    except:
                        continue
                # try:
                if object_type_test[0] == "barrier" and object_type_test[1] == "barrier":
                    return [hard_fam, med_fam_2, med_fam_1,
                            easy_fam], sample_trajectory.get_scene_4_cost_reward_trade_offs_test_v1(
                        test_type, valid_test_configs, selected_target, not_selected, switch_test_targets,
                        target_1_pos_to_target_2_pos), history
                else:
                    return [hard_fam, med_fam_2, med_fam_1, easy_fam], \
                           sample_trajectory.get_scene_4_cost_reward_trade_offs_test_v2(test_type, valid_test_configs,
                                                                                        selected_target, not_selected,
                                                                                        switch_test_targets,
                                                                                        target_1_pos_to_target_2_pos,
                                                                                        object_type_test), history
        return


    # while True:
    #     hard_scene = get_diff_lvl_scenes(goal_1_list_cost, diff_lvl="hard", no=1, scene_type=scene_type, all_scenes=goal_1_list)[0]
    #     fam_paths = [get_do_nothing_path(scene_type=hard_scene["scene_type"], scenes=goal_1_list,
    #                                            config=hard_scene["config"])]
    #
    #     med_fam = get_diff_lvl_scenes(goal_1_list_cost, diff_lvl="medium", no=2, scene_type=scene_type, all_scenes=goal_1_list)
    #
    #     fam_paths.append(med_fam[0])
    #     fam_paths.append(get_do_nothing_path(scene_type=med_fam[1]["scene_type"], scenes=goal_1_list,
    #                                                config=med_fam[1]["config"]))
    #     fam_paths.append(get_diff_lvl_scenes(goal_1_list_cost, diff_lvl="easy", no=1, scene_type=scene_type, all_scenes=goal_1_list)[0])
    #
    #     test_paths = select_scene_4_test_config(scene_type + "_3_4", goal_2_list_cost, goal_2_list)
    #
    #     fam_configs = [e["config"] for e in fam_paths]
    #     test_configs = [e["config"] for e in test_paths]
    #
    #     if not In_history([fam_configs, test_configs], history) and len(set(fam_configs+test_configs)) == 5:
    #         history.append([set(fam_configs), set(test_configs)])
    #         break


def get_configurations(no_config, height_pool, scenes, scene_type, meta=None, fam=False):
    sliced_scenes = scenes[scenes["scene_type"] == scene_type]
    idx = 0
    random.shuffle(height_pool)
    config_list = []
    while no_config > 0:
        if fam:
            selected_height = height_pool[idx]
            sliced_scenes_ = sliced_scenes[(sliced_scenes["obstacle_height"].isin(height_pool)) & (sliced_scenes["path_type"] != "No-barrier-jump")]
        elif meta is not None:
            sliced_scenes_ = sliced_scenes[(sliced_scenes["path_type"] == meta) | (sliced_scenes["obstacle_height"] == 0)]
        selected_config = random.sample(list(sliced_scenes_.config.unique()), k=1)[0]
        if len(sliced_scenes_[(sliced_scenes_["scene_type"] == scene_type) & (sliced_scenes_["config"] == selected_config)]) > 2 and selected_config not in config_list:
            config_list.append(selected_config)
            no_config -= 1
            idx = (idx + 1) % len(height_pool)
    return config_list


def change_scene_4_cost_reward_trade_offs_config_fam(scene_state, is_high_priority, object_type):
    if object_type == "barrier":
        if scene_state["agent_pos_z"] == 2 or scene_state["obj_pos_z"] == 2 and scene_state["obstacle_pos_z"] == 0:
            scene_state["obstacle_depth"] = 9
        else:
            scene_state["obstacle_depth"] = 8
        if is_high_priority:
            scene_state["obstacle_height"] = 6
            scene_state["obstacle_width"] = 0
    return scene_state


def change_scene_2_action_efficiency_config(test_type, config, test_no, test_paths, fam_config, obstacle_type):
    if test_type in ["Type-2.1"] and test_no == "A":
        if obstacle_type in ["barrier"]:
            config["obstacle_height"] = 0
        elif obstacle_type == "pit":
            config["pit_width"] = -1
    elif test_type in ["Type-2.2"]:
        if obstacle_type in ["barrier"]:
            if test_no in ["B", "A"]:
                config["obstacle_height"] = fam_config["obstacle_height"]
                config["obstacle_width"] = fam_config["obstacle_width"]
                config["obstacle_depth"] = fam_config["obstacle_depth"]
                config["obstacle_pos_z"] = fam_config["obstacle_pos_z"]
        if test_no == "B" and obstacle_type in ["pit"]:
            config["pit_width"] = fam_config["pit_width"]
            config["pit_depth"] = fam_config["pit_depth"]
        config["obstacle_pos_x"] = -1

    elif test_type in ["Type-2.3", "Type-2.4"]:
        if test_paths[1]["scene_type"] == "barrier_with_door_scenes":
            config["barrier_type"] = "barrier_with_door"
            config["obstacle_height"] = fam_config["obstacle_height"]
            config["obstacle_width"] = fam_config["obstacle_width"]
            config["obstacle_depth"] = fam_config["obstacle_depth"]
        elif test_paths[0]["scene_type"] == "barrier_scenes":
            if test_no == "A":
                test_b = test_paths[1]
                config["obstacle_height"] = int(test_b["obstacle_height"])
                config["obstacle_width"] = int(test_b["obstacle_width"])
                config["obstacle_depth"] = int(test_b["obstacle_depth"])
            if test_paths[0]["path_type"] == "Jump":
                config["obstacle_depth"] = fam_config["obstacle_depth"]
            elif test_paths[0]["path_type"] in ["Around-barrier-top", "Around-barrier-bottom"]:
                config["obstacle_height"] = fam_config["obstacle_height"]
        elif test_paths[0]["scene_type"] == "pit_scenes":
            if test_no == "A":
                config["bridge_z"] = int(test_paths[1]["obstacle_pos_z"])
                config["barrier_type"] = "pit-with-bridge"
    elif test_type == "Type-2.5":
        test_b = test_paths[1]
        config["obstacle_height"] = int(test_b["obstacle_height"])
        config["obstacle_width"] = int(test_b["obstacle_width"])
        config["obstacle_depth"] = int(test_b["obstacle_depth"])
        if test_paths[1]["path_type"] == "Jump":
            if config["obstacle_pos_z"] == 2:
                config["obstacle_depth"] = 7
            else:
                config["obstacle_depth"] = 8
        elif test_paths[1]["path_type"] in ["Around-barrier-top", "Around-barrier-bottom"]:
            config["obstacle_height"] = 6

    if test_type in ["Fam", "Type-2.2", "Type-2.3", "Type-2.4", "Type-2.5"]:
        if test_type == "Fam":
            selected_path = test_paths[test_no]
            if selected_path["path_type"] == "Jump":
                if config["obstacle_pos_z"] == 2:
                    config["obstacle_depth"] = 7
                else:
                    config["obstacle_depth"] = 8
            elif selected_path["path_type"] in ["Around-barrier-top", "Around-barrier-bottom"]:
                config["obstacle_height"] = 6
    return config


def change_scene_3_unobserved_constraints_config(test_type, config, test_no, familirization, obstacle_type, occluder_state, fam_occluder_state):

    if obstacle_type in ["pit", "pit-with-bridge"]:
        config["pit_depth"] = 2
    else:
        if test_type in ["Type-3.1"] and test_no == "A":
            if obstacle_type == "barrier":
                config["obstacle_height"] = 0
            elif obstacle_type == "pit" and test_no == "A":
                config["pit_width"] = -1
        elif test_type == "Type-3.2" and test_no == "A":
            if obstacle_type == "barrier":
                if familirization[0]["path_type"] == "Jump":
                    config["obstacle_height"] = random.choice(range(1, config["obstacle_height"]-1))
                else:
                    config["obstacle_depth"] = random.choice(range(0, config["obstacle_depth"] - 1))
            if obstacle_type == "barrier_with_door":
                config["barrier_type"] = "barrier_with_door"
            if obstacle_type in ["pit-with-bridge"] and test_no == "A":
                config["bridge_z"] = config["agent_pos_z"]
                config["barrier_type"] = "pit-with-bridge"
            if obstacle_type == "wall":
                occluder_state["obstacle_height"] = 6
                occluder_state["obstacle_depth"] = 4
                occluder_state["obstacle_pos_x"] = 1
                occluder_state["obstacle_pos_z"] = config["agent_pos_z"]
                config["obstacle_width"] = 0
                occluder_state["obstacle_width"] = 0
                if test_no == "A" or test_no == "Fam":
                    config["obstacle_height"] = 6
                    config["obstacle_depth"] = 4
                    config["obstacle_pos_x"] = 1
                    config["obstacle_pos_z"] = config["agent_pos_z"]

    return config, occluder_state


def change_scene_1_goal_preferences_config(config, test_no, test_paths, test_type, obstacles_list_fam, obstacles_list_test, fam=False):

    target_1_pos_to_target_2_pos = {
        "target_1":
            {2: 4,
             1: 5,
             0: 6},
        "target_2":
            {4: 2,
             5: 1,
             6: 0}
    }

    if obstacles_list_test[0] == "barrier" and obstacles_list_test[1] == "barrier" and obstacles_list_fam[0] == "barrier":
        if fam:
            if test_type in ["Type-1.1", "Type-1.1.0__1.2", "Type-1.2.0__1.2"]:
                config["obstacle_1_height"] = 0
                config["obstacle_2_height"] = 0
            # Put second target at same distance as first
            selected_target = 1 if test_paths[0]["target"] == "Target-1" else 2
            not_selected_target = 2 if selected_target == 1 else 1
            if test_type in ["Type-1.3", "Type-2.1.0__1.4", "Type-2.2.0__1.4"]:
                config[f"obstacle_{not_selected_target}_height"] = 0
                if test_paths[0]["path_type"] == "Target-2":
                    config["obj_1_pos_x"] = 0
            if config[f"obstacle_{selected_target}_height"] == 0 and config[f"obstacle_{not_selected_target}_height"] == 0 :
                config[f"obj_{not_selected_target}_pos_x"] = target_1_pos_to_target_2_pos[f"target_{selected_target}"][
                    config[f"obj_{selected_target}_pos_x"]]
            elif config[f"obstacle_1_height"] == 0 and config[f"obstacle_2_height"] != 0:
                config[f"obj_1_pos_x"] = 0
            elif config[f"obstacle_2_height"] == 0 and config[f"obstacle_1_height"] != 0:
                config[f"obj_2_pos_x"] = 6

            config[f"obj_{not_selected_target}_pos_z"] = config[f"obj_{selected_target}_pos_z"]
            if test_paths[0]["path_type"] == "Jump":
                config[f"obstacle_{selected_target}_depth"] = random.choice([3, 4])
            elif test_paths[0]["path_type"] in ['Around-barrier-bottom', 'Around-barrier-top']:
                config[f"obstacle_{selected_target}_height"] = random.choice([6, 7])
        if test_type in ["Type-1.1"]:
            if not fam:
                if test_type == "Type-1.1":
                    config["obstacle_1_height"] = 0
                    config["obstacle_2_height"] = 0
                test = test_paths[0] if test_no == "A" else test_paths[1]
                selected_target = 1 if test["target"] == "Target-1" else 2
                not_selected_target = 2 if selected_target == 1 else 1
                config[f"obj_{not_selected_target}_pos_x"] = target_1_pos_to_target_2_pos[f"target_{selected_target}"][
                    config[f"obj_{selected_target}_pos_x"]]
                config[f"obj_{not_selected_target}_pos_z"] = config[f"obj_{selected_target}_pos_z"]
        elif test_type in ["Type-1.1.0__1.2",  "Type-1.2.0__1.2", "Type-2.1.0__1.4",  "Type-2.2.0__1.4", "Type-1.3"]:
            if not fam:
                test_a_target = 1 if test_paths[0]["target"] == "Target-1" else 2
                test_b_target = 1 if test_paths[1]["target"] == "Target-1" else 2
                config[f"obj_{test_a_target}_pos_x"] = int(test_paths[0][f"obj_{test_a_target}_pos_x"])
                config[f"obj_{test_a_target}_pos_z"] = int(test_paths[0][f"obj_{test_a_target}_pos_z"])
                config[f"obj_{test_b_target}_pos_x"] = int(test_paths[1][f"obj_{test_b_target}_pos_x"])
                config[f"obj_{test_b_target}_pos_z"] = int(test_paths[1][f"obj_{test_b_target}_pos_z"])

                if test_type in ["Type-1.2.0__1.2", "Type-2.2.0__1.4"]:
                    config[f"obstacle_{test_a_target}_height"] = 0
                    # config[f"obstacle_{test_a_target}_width"] = int(test_paths[0][f"obstacle_width_{test_a_target}"])
                    # config[f"obstacle_{test_a_target}_depth"] = int(test_paths[0][f"obstacle_depth_{test_a_target}"])
                    config[f"obstacle_{test_b_target}_height"] = int(test_paths[1][f"obstacle_height_{test_b_target}"])
                    config[f"obstacle_{test_b_target}_width"] = int(test_paths[1][f"obstacle_width_{test_b_target}"])
                    config[f"obstacle_{test_b_target}_depth"] = int(test_paths[1][f"obstacle_depth_{test_b_target}"])
                elif test_type in ["Type-1.3"]:
                    config[f"obstacle_{test_a_target}_height"] = int(test_paths[0][f"obstacle_height_{test_a_target}"])
                    config[f"obstacle_{test_a_target}_width"] = int(test_paths[0][f"obstacle_width_{test_a_target}"])
                    config[f"obstacle_{test_a_target}_depth"] = int(test_paths[0][f"obstacle_depth_{test_a_target}"])
                    config[f"obstacle_{test_b_target}_height"] = int(test_paths[1][f"obstacle_height_{test_b_target}"])
                    config[f"obstacle_{test_b_target}_width"] = int(test_paths[1][f"obstacle_width_{test_b_target}"])
                    config[f"obstacle_{test_b_target}_depth"] = int(test_paths[1][f"obstacle_depth_{test_b_target}"])
                elif test_type in ["Type-1.1.0__1.2", "Type-2.1.0__1.4"]:
                    config[f"obstacle_{test_a_target}_height"] = 0
                    config[f"obstacle_{test_b_target}_height"] = 0
        if not fam:
            test_a_target = 1 if test_paths[0]["target"] == "Target-1" else 2
            test_b_target = 1 if test_paths[1]["target"] == "Target-1" else 2
            if test_paths[0]["path_type"] == "Jump":
                config[f"obstacle_{test_a_target}_depth"] = 4
            elif test_paths[0]["path_type"] in ['Around-barrier-bottom', 'Around-barrier-top']:
                config[f"obstacle_{test_a_target}_height"] = 7
            if test_paths[1]["path_type"] == "Jump":
                config[f"obstacle_{test_b_target}_depth"] = 4
            elif test_paths[1]["path_type"] in ['Around-barrier-bottom', 'Around-barrier-top']:
                config[f"obstacle_{test_b_target}_height"] = 7
    else:
        if fam:
            target_1 = 1 if test_paths[0]["target"] == "Target-1" else 2
            target_2 = 2 if test_paths[0]["target"] == "Target-1" else 1
            if test_type in ["Type-1.1", "Type-1.2.0__1.2"]:
                # Copy over the obstacle
                if obstacles_list_fam[0] in ["ramp", "platform"]:
                    config[f"ramp_height_{target_2}"] = int(test_paths[0][f"obstacle_height_{target_1}"])
                    if obstacles_list_fam[0] == "ramp":
                        config[f"ramp_rotation_{target_2}"] = 0
                        config["barrier_type"] = "ramp"
                    else:
                        config["barrier_type"] = "platform"
                elif obstacles_list_fam[0] == "pit":
                    config[f"pit_width_{target_2}"] = int(test_paths[0][f"obstacle_width_{target_1}"])
                    config[f"obj_{target_2}_pos_z"] = int(test_paths[0][f"obj_{target_1}_pos_z"])
                    config[f"bridge_{target_2}_z"] = -1
                    config[f"bridge_{target_1}_z"] = -1
                    config["barrier_type"] = "pit"
            if test_type in ["Type-1.3", "Type-2.2.0__1.4"]:
                if obstacles_list_fam[1] == "barrier":
                    config[f"obstacle_{target_2}_height"] = 0
                    if obstacles_list_fam[0] in ["pit", "pit-with-bridge"]:
                        config[f"obj_{target_2}_pos_x"] = 4 if target_2 == 2 else 0
                    else:
                        config[f"obj_{target_2}_pos_x"] = 6 if target_2 == 2 else 0
                    if obstacles_list_fam[1] in ["ramp", "platform"]:
                        config[f"ramp_height_{target_2}"] = -1
                    elif obstacles_list_fam[1] in ["pit"]:
                        config[f"pit_width_{target_2}"] = -1
                        config["barrier_type"] = "pit"
                elif obstacles_list_fam[1] == "barrier_with_door":
                    config[f"obstacle_{target_2}_height"] = random.choice([5, 6])
                    config[f"obstacle_{target_2}_width"] = random.choice([0, 1])
                    config[f"obstacle_{target_2}_depth"] = random.choice([3, 4, 5])
                    config[f"obstacle_{target_2}_pos_x"] = 1 if target_2 == 1 else 3
                    config[f"obstacle_{target_2}_pos_z"] = 0
                    config[f"barrier_type_{target_2}"] = "barrier_with_door"
                    config[f"obj_{target_2}_pos_x"] = 4 if target_2 == 2 else 0
                    if obstacles_list_fam[0] in ["ramp", "platform"]:
                        config[f"obj_{target_2}_pos_z"] = 1
                elif obstacles_list_fam[1] == "pit-with-bridge":
                    config[f"pit_width_{target_2}"] = config[f"pit_width_{target_1}"]
                    config[f"bridge_{target_2}_z"] = config[f"obj_{target_1}_pos_z"]
                    config[f"obj_{target_2}_pos_z"] = config[f"obj_{target_1}_pos_z"]
                    config[f"obj_{target_2}_pos_x"] = 4 if target_2 == 2 else 0
                    config["barrier_type"] = "pit-with-bridge"
        else:
            test_a_target = 1 if test_paths[0]["target"] == "Target-1" else 2
            test_b_target = 1 if test_paths[1]["target"] == "Target-1" else 2
            if test_type in ["Type-1.1", "Type-1.3"]:
                if obstacles_list_fam[0] in ["ramp", "platform"]:
                    config[f"ramp_height_{test_b_target}"] = int(test_paths[1][f"obstacle_height_{test_b_target}"])
                    config[f"ramp_height_{test_a_target}"] = int(test_paths[0][f"obstacle_height_{test_a_target}"])
                    if obstacles_list_fam[0] == "ramp":
                        config[f"ramp_rotation_{test_a_target}"] = 0
                        config[f"ramp_rotation_{test_b_target}"] = 0
                        config["barrier_type"] = "ramp"
                    else:
                        config["barrier_type"] = "platform"
                elif obstacles_list_fam[0] in ["pit"]:
                    config[f"pit_width_{test_a_target}"] = int(test_paths[0][f"obstacle_width_{test_a_target}"])
                    config[f"pit_width_{test_b_target}"] = int(test_paths[1][f"obstacle_width_{test_b_target}"])
                    config[f"obj_{test_a_target}_pos_z"] = int(test_paths[0][f"obj_{test_a_target}_pos_z"])
                    config[f"obj_{test_b_target}_pos_z"] = int(test_paths[1][f"obj_{test_b_target}_pos_z"])
                    config[f"bridge_{test_a_target}_z"] = -1
                    config[f"bridge_{test_b_target}_z"] = -1
                    config["barrier_type"] = "pit"
            elif test_type in ["Type-1.2.0__1.2", "Type-2.2.0__1.4"]:
                if obstacles_list_test[1] in ["ramp", "platform"]:
                    config[f"ramp_height_{test_b_target}"] = int(test_paths[1][f"obstacle_height_{test_b_target}"])
                    config[f"ramp_height_{test_a_target}"] = -1
                    if obstacles_list_test[1] == "ramp":
                        config[f"ramp_rotation_{test_a_target}"] = 0
                        config[f"ramp_rotation_{test_b_target}"] = 0
                        config["barrier_type"] = "ramp"
                    elif obstacles_list_test[1] == "platform":
                        config["barrier_type"] = "platform"
                elif obstacles_list_test[1] in ["pit"]:
                    config[f"pit_width_{test_b_target}"] = int(test_paths[1][f"obstacle_width_{test_b_target}"])
                    config[f"bridge_{test_b_target}_z"] = -1
                    config["barrier_type"] = "pit"
                if obstacles_list_test[0] == "barrier_with_door":
                    config[f"obstacle_{test_a_target}_height"] = int(test_paths[0][f"obstacle_height_{test_a_target}"])
                    config[f"obstacle_{test_a_target}_width"] = int(test_paths[0][f"obstacle_width_{test_a_target}"])
                    config[f"obstacle_{test_a_target}_depth"] = int(test_paths[0][f"obstacle_depth_{test_a_target}"])
                    config[f"obstacle_{test_a_target}_pos_x"] = int(test_paths[0][f"obstacle_{test_a_target}_pos_x"])
                    config[f"obstacle_{test_a_target}_pos_z"] = 1
                    config[f"obj_{test_a_target}_pos_z"] = int(test_paths[0][f"obj_{test_a_target}_pos_z"])
                    config[f"obj_{test_a_target}_pos_x"] = int(test_paths[0][f"obj_{test_a_target}_pos_x"])
                    config[f"barrier_type_{test_a_target}"] = "barrier_with_door"
                elif obstacles_list_test[0] == "pit-with-bridge":
                    config[f"pit_width_{test_a_target}"] = int(test_paths[0][f"obstacle_width_{test_a_target}"])
                    config[f"pit_width_{test_b_target}"] = int(test_paths[1][f"obstacle_width_{test_b_target}"])
                    config[f"bridge_{test_a_target}_z"] = int(test_paths[0][f"obstacle_{test_a_target}_pos_z"])
                    config[f"bridge_{test_b_target}_z"] = -1
                    config["barrier_type"] = "pit-with-bridge"
    return config


def change_scene_4_cost_reward_trade_offs_config(test_type, config, test_paths, test_configs, test_no, object_type):
    if test_type in ["Type-4.1", "Type-4.2"]:
        test_a_target = 1 if test_paths[0]["target"] == "Target-1" else 2
        test_b_target = 1 if test_paths[1]["target"] == "Target-1" else 2
        selected_test_path = 0 if test_no == "A" else "B"

        config[f"obj_{test_a_target}_pos_x"] = int(test_paths[0][f"obj_{test_a_target}_pos_x"])
        config[f"obj_{test_a_target}_pos_z"] = int(test_paths[0][f"obj_{test_a_target}_pos_z"])
        config[f"obj_{test_b_target}_pos_x"] = int(test_paths[1][f"obj_{test_b_target}_pos_x"])
        config[f"obj_{test_b_target}_pos_z"] = int(test_paths[1][f"obj_{test_b_target}_pos_z"])

        if object_type[0] == "barrier" and object_type[1] == "barrier":
            if test_type == "Type-4.2":
                config[f"obstacle_{test_a_target}_height"] = 0
                config[f"obstacle_{test_b_target}_height"] = int(test_paths[1][f"obstacle_height_{test_b_target}"])
                config[f"obstacle_{test_b_target}_width"] = int(test_paths[1][f"obstacle_width_{test_b_target}"])
                config[f"obstacle_{test_b_target}_depth"] = int(test_paths[1][f"obstacle_depth_{test_b_target}"])
            if test_type in ["Type-4.1"]:
                config[f"obstacle_{test_a_target}_height"] = 0
                config[f"obstacle_{test_b_target}_height"] = 0
        elif (object_type[0] == "barrier_with_door" or object_type[1] == "barrier_with_door") and test_type == "Type-4.1":
            config["barrier_type"] = "barrier_with_door"
            if test_no == "A":
                if object_type[0] == "barrier_with_door":
                    config[f"obstacle_{test_a_target}_width"] = random.choice([0, 1])
                    config[f"obstacle_{test_a_target}_depth"] = random.choice([3, 4])
                if object_type[0] == "barrier":
                    config[f"obstacle_{test_a_target}_height"] = 0
                if object_type[1] == "barrier":
                    config[f"obstacle_{test_b_target}_height"] = 0
                if object_type[1] == "barrier_with_door":
                    # Mirror the barrier shape from target_a if target_a is barrier with door
                    config[f"obstacle_{test_a_target}_pos_z"] = 1
                    config[f"obstacle_{test_b_target}_pos_z"] = 1
                    if object_type[0] == "barrier_with_door":
                        config[f"obstacle_{test_b_target}_height"] = config[f"obstacle_{test_a_target}_height"]
                        config[f"obstacle_{test_b_target}_width"] = config[f"obstacle_{test_a_target}_width"]
                        config[f"obstacle_{test_b_target}_depth"] = config[f"obstacle_{test_a_target}_depth"]
                        config[f"obj_{test_b_target}_pos_x"] = 4 if config[f"obj_{test_b_target}_pos_x"] == 6 else \
                            config[f"obj_{test_b_target}_pos_x"]
                        if config[f"obstacle_{test_a_target}_height"] != 0:
                            config[f"obj_{test_a_target}_pos_x"] = 4 if config[f"obj_{test_a_target}_pos_x"] == 6 else \
                                config[f"obj_{test_a_target}_pos_x"]
                    else: # Else just copy from config
                        config[f"obstacle_{test_b_target}_height"] = int(
                            test_paths[1][f"obstacle_height_{test_a_target}"])
                        config[f"obstacle_{test_b_target}_width"] = int(
                            test_paths[1][f"obstacle_width_{test_a_target}"])
                        config[f"obstacle_{test_b_target}_depth"] = int(
                            test_paths[1][f"obstacle_depth_{test_a_target}"])
                        if config[f"obstacle_{test_b_target}_height"] == 0:
                            config[f"obj_{test_b_target}_pos_x"] = 0 if test_b_target == 1 else 6
                        else:
                            config[f"obj_{test_b_target}_pos_x"] = 4 if config[f"obj_{test_b_target}_pos_x"] == 6 else \
                            config[f"obj_{test_b_target}_pos_x"]

            else:
                config[f"obstacle_{test_b_target}_height"] = test_configs[0][f"obstacle_{test_b_target}_height"]
                config[f"obstacle_{test_b_target}_width"] = test_configs[0][f"obstacle_{test_b_target}_width"]
                config[f"obstacle_{test_b_target}_depth"] = test_configs[0][f"obstacle_{test_b_target}_depth"]
                config[f"obstacle_{test_a_target}_height"] = test_configs[0][f"obstacle_{test_a_target}_height"]
                config[f"obstacle_{test_a_target}_width"] = test_configs[0][f"obstacle_{test_a_target}_width"]
                config[f"obstacle_{test_a_target}_depth"] = test_configs[0][f"obstacle_{test_a_target}_depth"]
                if object_type[0] == "barrier_with_door" :
                    config[f"obstacle_{test_a_target}_pos_z"] = 1
                if object_type[1] == "barrier_with_door":
                    config[f"obstacle_{test_b_target}_pos_z"] = 1
                if config[f"obstacle_{test_b_target}_height"] != 0:
                    config[f"obj_{test_b_target}_pos_x"] = 4 if config[f"obj_{test_b_target}_pos_x"] == 6 else \
                        config[f"obj_{test_b_target}_pos_x"]
                if config[f"obstacle_{test_a_target}_height"] != 0:
                    config[f"obj_{test_a_target}_pos_x"] = 4 if config[f"obj_{test_a_target}_pos_x"] == 6 else \
                        config[f"obj_{test_a_target}_pos_x"]
        elif (object_type[0] == "pit-with-bridge" or object_type[1] == "pit-with-bridge") and test_type == "Type-4.1":
            config[f"pit_width_{test_b_target}"] = int(test_paths[1][f"obstacle_width_{test_b_target}"])
            config["barrier_type"] = "pit-with-bridge"
            if config[f"pit_width_{test_b_target}"] == -1:
                config[f"bridge_{test_b_target}_z"] = -1
            else:
                config[f"bridge_{test_b_target}_z"] = int(test_paths[1][f"obstacle_{test_b_target}_pos_z"])
            config[f"pit_width_{test_a_target}"] = int(test_paths[0][f"obstacle_width_{test_a_target}"])
            if int(test_paths[0][f"obstacle_width_{test_a_target}"]) == -1:
                config[f"bridge_{test_a_target}_z"] = -1
            else:
                config[f"bridge_{test_a_target}_z"] = int(test_paths[0][f"obstacle_{test_a_target}_pos_z"])
        elif object_type[1] == "pit" and test_type == "Type-4.2":
            if test_no == "A":
                config["barrier_type"] = "pit-with-bridge" if object_type[0] == "pit-with-bridge" else "pit"
                config[f"pit_width_{test_b_target}"] = int(test_paths[1][f"obstacle_width_{test_b_target}"])
                config[f"bridge_{test_b_target}_z"] = -1
            if test_no == "B":
                config[f"pit_width_{test_a_target}"] = test_configs[0][f"pit_width_{test_a_target}"]
                if object_type[0] == "pit-with-bridge":
                    config["barrier_type"] = "pit-with-bridge"
                    config[f"bridge_{test_a_target}_z"] = test_configs[0][f"bridge_{test_a_target}_z"]
        elif object_type[1] in ["ramp", "platform"] and test_type == "Type-4.2":
            if test_no == "A":
                # Copy over the ramp/platform from test_b to test_a
                config[f"ramp_height_{test_b_target}"] = int(test_paths[1][f"obstacle_height_{test_b_target}"])
                config[f"ramp_height_{test_a_target}"] = -1
                if object_type[1] == "ramp":
                    config[f"ramp_rotation_{test_b_target}"] = int(test_paths[1][f"obstacle_width_{test_b_target}"])
                    config[f"ramp_rotation_{test_a_target}"] = 0
                    config["barrier_type"] = "ramp"
                else:
                    config["barrier_type"] = "platform"
            else:
                config[f"ramp_height_{test_a_target}"] = -1
            # If Target-A is wall with door :
            if object_type[0] == "barrier_with_door":
                config[f"barrier_type_{test_a_target}"] = "barrier_with_door"
                if test_no == "B": # Copy over the barrier from test A
                    config[f"obstacle_{test_a_target}_height"] = test_configs[0][f"obstacle_{test_a_target}_height"]
                    config[f"obstacle_{test_a_target}_width"] = test_configs[0][f"obstacle_{test_a_target}_width"]
                    config[f"obstacle_{test_a_target}_depth"] = test_configs[0][f"obstacle_{test_a_target}_depth"]
                    config[f"obstacle_{test_a_target}_pos_x"] = test_configs[0][f"obstacle_{test_a_target}_pos_x"]
                    config[f"obstacle_{test_a_target}_pos_z"] = test_configs[0][f"obstacle_{test_a_target}_pos_z"]

                elif test_no == "A": # Set the barrier width and height to some standard values
                    config[f"obstacle_{test_a_target}_width"] = random.choice([0, 1])
                    config[f"obstacle_{test_a_target}_depth"] = random.choice([3, 4])
            elif object_type[0] == "barrier": # If barrier than set obstacle height to 0 to hide the barrier
                config[f"obstacle_{test_a_target}_height"] = 0
                config[f"obj_{test_a_target}_pos_x"] = 0 if test_a_target == 1 else 6
                if object_type[1] != "wall":
                    config[f"obstacle_{test_b_target}_height"] = 0
                    config[f"obj_{test_b_target}_pos_x"] = 0 if test_b_target == 1 else 6
    return config


def select_config(scene_type, scenes):
    configs = scenes[scenes["scene_type"] == scene_type].config.unique()
    return configs[random.randint(0, len(configs) - 1)]

def check_valid_config(scene_type, scenes, config, scene_1_2):
    if scene_1_2:
        if len(scenes[(scenes["scene_type"] == scene_type) & (scenes["config"] == config) & (scenes["obstacle_height"] > 0) ])  > 2:
            return True
        else:
            return False
    else:
        if len(scenes[(scenes["scene_type"] == scene_type) & (scenes["config"] == config)])  > 2:
            return True
        else:
            return False


def calculate_cost(scenes, cost, type="force"):
    scenes["cost"] = scenes["force_x"]*cost[0] + scenes["force_y"]*cost[1] + scenes["force_z"]*cost[2]
    return scenes

def calculate_distance(scenes):
    scenes["target-1-distance"] = np.sqrt((scenes["obj_1_pos_x"] - 3)**2 +
                                             (scenes["obj_1_pos_z"] - scenes["agent_pos_z"])**2)
    scenes["target-2-distance"] = np.sqrt((scenes["obj_2_pos_x"] - 3)**2 +
                                             (scenes["obj_2_pos_z"] - scenes["agent_pos_z"])**2)
    return scenes

def get_efficient_path(scene_type, scenes, config):
    slices_data = scenes[(scenes["scene_type"] == scene_type) & (scenes["config"] == config) & (scenes["cost"] != 0.0)]
    slices_data = slices_data.sort_values(by=["cost"])
    return slices_data.iloc[0]


def get_in_efficient_path(scene_type, scenes, config):
    slices_data = scenes[(scenes["scene_type"] == scene_type) & (scenes["config"] == config)]
    slices_data = slices_data.sort_values(by=["cost"])
    slices_data = slices_data[(slices_data["path_val_1"] < -0.2) | (slices_data["path_val_1"] > 0.2)]
    try:
        return slices_data.iloc[random.randint(0, slices_data.shape[0]-1)]
    except:
        print(slices_data)
        exit()

def get_efficient_paths(scene_type, scenes, config_list):
    output = []
    for config in config_list:
        # if output is None:
        #     output = get_efficient_path(scene_type, scenes, config)
        # else:
        #     output.append(get_efficient_path(scene_type, scenes, config))
        output.append(get_efficient_path(scene_type, scenes, config))
    return output

def get_do_nothing_path(scene_type, scenes, config):
    slices_data = scenes[(scenes["scene_type"] == scene_type) & (scenes["config"] == config)]
    slices_data = slices_data.sort_values(by=["cost"])
    return slices_data.iloc[0]

def get_configs(no_configs, scene_type, scenes, scene_1_2=True, meta="No-barrier-jump"):
    configs = []
    while no_configs > 0:
        config = select_config(scene_type, scenes)
        if check_valid_config(scene_type, scenes, config, scene_1_2):
            configs.append(config)
            no_configs -= 1
    return configs


def get_high_low_catergory(scenes, goal_2=False):
    slices_data = scenes[scenes["cost"] != 0.0]
    if goal_2:
        slices_data = slices_data.loc[slices_data.groupby(["scene_type", "config", "target"])["cost"].idxmin()]
        threshold_easy = 0.2
        threshold_mid = 0.3
        threshold_hard = 0.4
    else:
        slices_data = slices_data.loc[slices_data.groupby(["scene_type", "config"])["cost"].idxmin()]
        threshold_easy = 0.4
        threshold_mid = 0.05
        threshold_hard = 0.25
    slices_data = slices_data.sort_values(by=["cost"])
    slices_data["category"] = "None"
    print(slices_data.columns)
    for path_type in [ ['Jump'], ['Straight-Target', 'Around-barrier-bottom', 'Around-barrier-top'] ]:
        cost = list(slices_data[slices_data["path_type"].isin(path_type)]["cost"])
        mid_val = median(cost)
        max_val = max(cost)
        min_val = min(cost)
        min_mid_dist = mid_val - min_val
        mid_max_dist = max_val - mid_val
        # print(min_val, min_val + min_mid_dist/2, path_type)
        # print(mid_val - min_mid_dist/3, mid_val + mid_max_dist/3, path_type)
        # print(max_val - mid_max_dist/2, max_val, path_type)
        # cost = list(slices_data[
        #           (slices_data["path_type"].isin(path_type)) &
        #           (slices_data["obstacle_height"].isin([3, 4, 5]))
        #           ]["cost"])
        # mid_val = median(cost)
        # max_val = max(cost)
        # min_val = min(cost)
        # print(max_val, mid_val, min_val)
        # 16.741837650193652 13.54965372189156 11.885609296901206
        print(slices_data[
                  (12 < slices_data["cost"]) &
                  (slices_data["path_type"].isin(path_type)) &
                  (slices_data["cost"] < 14)].obstacle_height.unique(), path_type)

        slices_data.loc[
            (slices_data["cost"] > min_val) &
            (slices_data["path_type"].isin(path_type)) &
            (slices_data["cost"] < (min_val + min_mid_dist/3)), "category"] = "easy"
        slices_data.loc[
            ((mid_val - min_mid_dist/3) < slices_data["cost"]) &
            (slices_data["path_type"].isin(path_type)) &
            (slices_data["cost"] < (mid_val + mid_max_dist/3)), "category"] = "medium"
        slices_data.loc[
            ((max_val - mid_max_dist/2) < slices_data["cost"]) &
            (slices_data["path_type"].isin(path_type)) &
            (slices_data["cost"] < (max_val)), "category"] = "hard"




    # Temp
    # if goal_2:
    #     slices_data.loc[
    #         (slices_data["scene_type"] == "barrier_scenes_3_4") & (slices_data["obstacle_height_1"] >= 0.6) & (
    #                     slices_data["target"] == "Target-1"), "category"] = "hard"
    #     slices_data.loc[
    #         (slices_data["scene_type"] == "barrier_scenes_3_4") & (slices_data["obstacle_width_1"] >= 0.4) & (
    #                 slices_data["target"] == "Target-1"), "category"] = "hard"
    #     slices_data.loc[
    #         (slices_data["scene_type"] == "barrier_scenes_3_4") & (slices_data["obstacle_depth_1"] >= 1.5) & (
    #                 slices_data["target"] == "Target-1"), "category"] = "hard"
    #     slices_data.loc[(slices_data["scene_type"] == "barrier_scenes_3_4") & (slices_data["obstacle_height_2"] >= 0.6) & (slices_data["target"] == "Target-2"), "category"] = "hard"
    #     slices_data.loc[(slices_data["scene_type"] == "barrier_scenes_3_4") & (slices_data["obstacle_width_2"] >= 0.4) & (slices_data["target"] == "Target-2"), "category"] = "hard"
    #     slices_data.loc[(slices_data["scene_type"] == "barrier_scenes_3_4") & (slices_data["obstacle_depth_2"] >= 1.5) & (slices_data["target"] == "Target-2"), "category"] = "hard"
    #
    #
    #     slices_data.loc[(slices_data["scene_type"] == "barrier_scenes_3_4") & (slices_data["obstacle_height_1"] >= 0.3) & (0.6 > slices_data["obstacle_height_1"]) & (slices_data["target"] == "Target-1"), "category"] = "medium"
    #     slices_data.loc[(slices_data["scene_type"] == "barrier_scenes_3_4") & (slices_data["obstacle_width_1"] >= 0.2) & (0.4 > slices_data["obstacle_width_1"]) & (slices_data["target"] == "Target-1"), "category"] = "medium"
    #     slices_data.loc[(slices_data["scene_type"] == "barrier_scenes_3_4") & (slices_data["obstacle_depth_1"] >= 1.1) & (1.5 > slices_data["obstacle_depth_1"]) & (slices_data["target"] == "Target-1"), "category"] = "medium"
    #     slices_data.loc[(slices_data["scene_type"] == "barrier_scenes_3_4") & (slices_data["obstacle_height_2"] >= 0.3) & (0.6 > slices_data["obstacle_height_2"]) & (slices_data["target"] == "Target-2"), "category"] = "medium"
    #     slices_data.loc[(slices_data["scene_type"] == "barrier_scenes_3_4") & (slices_data["obstacle_width_2"] >= 0.2) & (0.4 > slices_data["obstacle_width_2"]) & (slices_data["target"] == "Target-2"), "category"] = "medium"
    #     slices_data.loc[(slices_data["scene_type"] == "barrier_scenes_3_4") & (slices_data["obstacle_depth_2"] >= 1.1) & (1.5 > slices_data["obstacle_depth_2"]) & (slices_data["target"] == "Target-2"), "category"] = "medium"
    #
    #     slices_data.loc[
    #         (slices_data["scene_type"] == "barrier_scenes_3_4") & (0.3 > slices_data["obstacle_height_1"]) & (
    #                     slices_data["target"] == "Target-1"), "category"] = "easy"
    #     slices_data.loc[
    #         (slices_data["scene_type"] == "barrier_scenes_3_4") & (0.2 > slices_data["obstacle_width_1"]) & (
    #                 slices_data["target"] == "Target-1"), "category"] = "easy"
    #     slices_data.loc[
    #         (slices_data["scene_type"] == "barrier_scenes_3_4") & (1.1 > slices_data["obstacle_depth_1"]) & (
    #                 slices_data["target"] == "Target-1"), "category"] = "easy"
    #     slices_data.loc[
    #         (slices_data["scene_type"] == "barrier_scenes_3_4") & (0.3 > slices_data["obstacle_height_2"]) & (
    #                     slices_data["target"] == "Target-2"), "category"] = "easy"
    #     slices_data.loc[
    #         (slices_data["scene_type"] == "barrier_scenes_3_4") & (0.2 > slices_data["obstacle_width_2"]) & (
    #                 slices_data["target"] == "Target-2"), "category"] = "easy"
    #     slices_data.loc[
    #         (slices_data["scene_type"] == "barrier_scenes_3_4") & (1.1 > slices_data["obstacle_depth_2"]) & (
    #                 slices_data["target"] == "Target-2"), "category"] = "easy"
    # else:
    #     slices_data.loc[(slices_data["scene_type"] == "barrier_scenes") & (slices_data["obstacle_height"] >= 0.6), "category"] = "hard"
    #     slices_data.loc[(slices_data["scene_type"] == "barrier_scenes") & (slices_data["obstacle_height"] >= 0.3) & (0.6 > slices_data["obstacle_height"]), "category"] = "medium"
    #     slices_data.loc[(slices_data["scene_type"] == "barrier_scenes") & (slices_data["obstacle_height"] < 0.3), "category"] = "easy"
    return slices_data


def get_diff_lvl_scenes(scenes, diff_lvl, no, scene_type, all_scenes):
    slices_data = scenes[(scenes["category"] == diff_lvl) & (scenes["scene_type"] == scene_type) ]
    output = slices_data.iloc[random.sample(range(slices_data.shape[0]), k=no)]
    output = []
    while no > 0:
        selected_data = slices_data.iloc[random.sample(range(slices_data.shape[0]), k=1)]
        if len(all_scenes[(all_scenes["config"] == selected_data["config"].iloc[0]) & (all_scenes["path_val_1"] >= 0)]) > 2:
            output.append(selected_data.iloc[0])
            no -= 1
    return output

def get_2_goal_path(scene_type, scenes,efficient=False, target="Target-1", same_obstacle=False, height=None, height_pool=None):

    if target == "Both":
        sliced_data = scenes[ (scenes["scene_type"] == scene_type) & (scenes["obstacle_height_1"] > 0)
                              &(scenes["obstacle_height_2"] > 0)]
    else:
        sliced_data = scenes[
            (scenes["scene_type"] == scene_type) & (scenes["target"] == target) & (scenes["obstacle_height_1"] > 0) & (
                        scenes["obstacle_height_2"] > 0)]
    if efficient:
        while True:
            config = select_config(scene_type, sliced_data)
            if same_obstacle:
                if sliced_data[(sliced_data["config"] == config) ]["obstacle_height_1"].iloc[0] != \
                        sliced_data[(sliced_data["config"] == config) ]["obstacle_height_2"].iloc[0]:
                    continue
            if scene_type == "barrier_scenes_3_4":
                sliced_data_ = sliced_data[
                    (sliced_data["obstacle_height_1"] == height) & (sliced_data["obstacle_height_2"] != height)]
                config = random.sample(list(sliced_data_.config.unique()), k=1)[0]
            if target == "Both":
                sliced_data = scenes[
                    (scenes["scene_type"] == scene_type) &
                    (scenes["obstacle_height_2"] < 0.3) ]
                config = random.sample(list(sliced_data.config.unique()), k=1)[0]
                sliced_data = sliced_data.loc[sliced_data.groupby(["config", "target"])["cost"].idxmin()]
                return [sliced_data[(sliced_data["config"] == config) & (sliced_data["target"] == "Target-1")].iloc[0],
                        sliced_data[(sliced_data["config"] == config) & (sliced_data["target"] == "Target-2")].iloc[0]]
            else:
                sliced_data = sliced_data.loc[sliced_data.groupby(["config"])["cost"].idxmin()]
                return sliced_data[sliced_data["config"] == config].iloc[0]


def list_two_goal_scenes():
    config_list = []
    if os.path.isfile("../scene_data/two_goal_scenes.pickle"):
        with open("../scene_data/two_goal_scenes.pickle", "rb") as fp:
            path_force_dist = pickle.load(fp)
            print("Found data")
            return path_force_dist
    for directory in ["barrier_scenes_3_4", "platform_scenes_3_4", "pit_scenes_3_4", "ramp_scenes_3_4",
                      "barrier_with_door_scenes_3_4"]:
        output_dirs = os.listdir(os.path.join(directory))
        for output_dir in output_dirs:
            config_list.extend([os.path.join(directory, output_dir, e)
                                for e in os.listdir(os.path.join(directory, output_dir)) if
                                os.path.isdir(os.path.join(directory, output_dir, e))])
    config_paths = []
    for config in config_list:
        config_paths.extend(
            [os.path.join(config, e).split("/") for e in os.listdir(config) if os.path.isdir(os.path.join(config, e))]
        )
    # Read force and distance
    idx = 0
    path_force_dist = []
    for path in tqdm(config_paths):
        # try:
        with open(os.path.join(*path, "../state_info.json"), "r") as fp:
            state_data = json.load(fp)
        with open(os.path.join(*path[:-1], "scene_config.json"), "r") as fp:
            scene_config_ = json.load(fp)
        total_force = [0, 0, 0]
        pos = []
        for f in state_data:
            total_force[0] += abs(f["agent"]["force"]["x"])
            total_force[1] += abs(f["agent"]["force"]["y"])
            total_force[2] += abs(f["agent"]["force"]["z"])
            pos.append({"x": f["agent"]["position"][0], "y": f["agent"]["position"][1], "z": f["agent"]["position"][2]})
            meta_data = f["agent"]["path_meta_data"]

        dist = comp_travel_3d(pos)
        dist = [round(dist["x"], 4), round(dist["y"], 4), round(dist["z"], 4)]
        if (dist[0] + dist[1] + dist[2]) == 0:
            objective = "Do-nothing"
        else:
            x_dir = pos[-1]["x"]
            objective = "Target-1" if x_dir > 0 else "Target-2"

        if scene_config_["barrier_type"] in ["cube", "barrier_with_door"]:
            obstacle_height_1 = scene_config_["obstacle_1_height"]
            obstacle_width_1 = scene_config_["obstacle_1_width"]
            obstacle_depth_1 = scene_config_["obstacle_1_depth"]
            obstacle_height_2 = scene_config_["obstacle_2_height"]
            obstacle_width_2 = scene_config_["obstacle_2_width"]
            obstacle_depth_2 = scene_config_["obstacle_2_depth"]
            object_positions = [scene_config_["obstacle_1_pos_x"], scene_config_["obstacle_1_pos_z"],
                                scene_config_["obj_1_pos_x"], scene_config_["obj_1_pos_z"],
                                scene_config_["obstacle_2_pos_x"], scene_config_["obstacle_2_pos_z"],
                                scene_config_["obj_2_pos_x"], scene_config_["obj_2_pos_z"],
                                scene_config_["agent_pos_z"]]
        elif scene_config_["barrier_type"] in ["pit", "pit-with-bridge"]:
            obstacle_height_1 = 0
            obstacle_width_1 = scene_config_["pit_width_1"]
            obstacle_depth_1 = 0
            obstacle_height_2 = 0
            obstacle_width_2 = scene_config_["pit_width_2"]
            obstacle_depth_2 = 0
            object_positions = [1, scene_config_["bridge_1_z"] if scene_config_["barrier_type"] == "pit-with-bridge" else 1,
                                scene_config_["obj_1_pos_x"], scene_config_["obj_1_pos_z"],
                                3, scene_config_["bridge_2_z"] if scene_config_["barrier_type"] == "pit-with-bridge" else 1,
                                scene_config_["obj_2_pos_x"], scene_config_["obj_2_pos_z"],
                                scene_config_["agent_pos_z"]]
        elif scene_config_["barrier_type"] in ["ramp", "platform"]:
            obstacle_height_1 = scene_config_["ramp_height_1"]
            obstacle_width_1 = scene_config_["ramp_rotation_1"] if scene_config_["barrier_type"] == "ramp" else -1
            obstacle_depth_1 = 0
            obstacle_height_2 = scene_config_["ramp_height_2"]
            obstacle_width_2 = scene_config_["ramp_rotation_2"] if scene_config_["barrier_type"] == "ramp" else -1
            obstacle_depth_2 = 0
            object_positions = [1, 1,
                                0, 1,
                                3, 1,
                                4, 1,
                                scene_config_["agent_pos_z"]]
        meta_data = ["meta", "Do-nothing", 0, 0] if meta_data is None else meta_data

        path_force_dist.append((path, total_force, dist, objective, float(obstacle_height_1),
                                float(obstacle_width_1), float(obstacle_depth_1),
                                float(obstacle_height_2), float(obstacle_width_2), float(obstacle_depth_2),
                                *meta_data[1:],
                                *object_positions))
        # except:
        #     print(path)

    with open("../scene_data/two_goal_scenes.pickle", "wb") as fp:
        pickle.dump(path_force_dist, fp)
    return path_force_dist


def select_scene_4_test_config(scene_type, scenes_cost_label, all_scenes):
    slices_data = scenes_cost_label[(scenes_cost_label["scene_type"] == scene_type)]
    config_list = slices_data.config.unique()
    idx = 10
    while True:
        selected_config = config_list[random.randint(0, len(config_list)-1)]
        # Check for validity of seleted config
        selected_slice_t1 = slices_data[(slices_data["config"] == selected_config) & (slices_data["target"] == "Target-1")]
        selected_slice_t2 = slices_data[(slices_data["config"] == selected_config) & (slices_data["target"] == "Target-2")]
        idx -= 1
        # if idx == 0:
        #     exit()
        # if len(selected_slice_t1[selected_slice_t1["category"] == "hard"]) > 0 and len(selected_slice_t2[selected_slice_t2["category"] == "medium"]):
        #     return [
        #         selected_slice_t1[selected_slice_t1["category"] == "hard"],
        #         # all_scenes[(all_scenes["scene_type"] == scene_type) & (all_scenes["config"] == selected_config) & (all_scenes["target"] == "Target-1") & (all_scenes["category"] == "Do-nothing")],
        #         selected_slice_t2[selected_slice_t2["category"] == "medium"]
        #     ]
        if len(selected_slice_t1[selected_slice_t1["category"] == "medium"]) > 0 and len(selected_slice_t2[selected_slice_t2["category"] == "high"]):
            return [
                selected_slice_t1[selected_slice_t1["category"] == "medium"].iloc[0],
                selected_slice_t2[selected_slice_t2["category"] == "high"].iloc[0]
            ]
        elif len(selected_slice_t1[selected_slice_t1["category"] == "medium"]) > 0 and len(selected_slice_t2[selected_slice_t2["category"] == "low"]):
            return [
                selected_slice_t1[selected_slice_t1["category"] == "medium"].iloc[0],
                selected_slice_t2[selected_slice_t2["category"] == "low"].iloc[0]
            ]
        elif len(selected_slice_t1[selected_slice_t1["category"] == "medium"]) > 0 and len(selected_slice_t2[selected_slice_t2["category"] == "medium"]):
            return [
                selected_slice_t1[selected_slice_t1["category"] == "medium"].iloc[0],
                selected_slice_t2[selected_slice_t2["category"] == "medium"].iloc[0]
            ]
        elif len(selected_slice_t1[selected_slice_t1["category"] == "low"]) > 0 and len(selected_slice_t2[selected_slice_t2["category"] == "low"]):
            return [
                selected_slice_t1[selected_slice_t1["category"] == "low"].iloc[0],
                selected_slice_t2[selected_slice_t2["category"] == "low"].iloc[0]
            ]
