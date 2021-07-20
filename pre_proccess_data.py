import os
from os.path import join
import json
import pickle
from PIL import Image
import numpy as np
import random
import tqdm
from shutil import copyfile
from util import scene_configuration


def get_scene_labels(data_, scene_type):
    if scene_type == "scene_3":
        original_target_in_fam = 1 if data_["familiarization"][-1]["agent"]["center"][0] > 0 else 2
        opposite_side = 2 if original_target_in_fam == 1 else 1
        # data_0 = data_["test_a"][0]
        # print(json.dumps(data_0["goal_2"]["color"], indent=2))
        original_target_in_test = original_target_in_fam if data_["familiarization"][-1][f"goal_{original_target_in_fam}"]["object_label"] == \
                                           data_["test_a"][-1][f"goal_{original_target_in_fam}"][
                                               "object_label"] else opposite_side
        # print(json.dumps(data_0["goal_2"]["color"], indent=2))
        data_["scene_label"] = {
            "original_targetx_familirization": "left" if original_target_in_fam == 1 else "right",
            "original_target_in_test": "left" if original_target_in_test == 1 else "right"
        }
    if scene_type == "scene_4":
        original_target_in_fam = 1 if data_["familiarization_1"][-1]["agent"]["center"][0] > 0 else 2
        data_["scene_label"] = {
            "original_target_familirization": "left" if original_target_in_fam == 1 else "right",
            # "original_target_in_test": "left" if original_target_in_test == 1 else "right"
        }
    return data_


def process_trajectory_state_data(state_datas, base_dir):
    scene_config = scene_configuration.SceneConfiguration()
    state_data_new = []

    for i, e in enumerate(state_datas):
        mask = np.array(Image.open(join(base_dir, "images_c", f"id_image-{i}.png")))
        for scene_object in e.keys():
            if "segmentation_color" in e[scene_object]:
                seg_color = e[scene_object]["segmentation_color"]

                e[scene_object]["visibility"] = np.any(mask[
                                                             (mask[:, :, 0] == seg_color[0]) &
                                                              (mask[:, :, 1] == seg_color[1]) &
                                                            (mask[:, :, 2] == seg_color[2])
                                                                    ])

            if scene_object in ["goal", "goal_1", "goal_2"]:
                object_label = 1 + scene_config.target_colors.index(e[scene_object]["color"])
            elif scene_object in ["barrier", "barrier_1", "barrier_2", "barrier_with_door_1", "barrier_with_door_2",
                                  "barrier_with_door_3",
                                  "ramp_platform", "ramp_slope", "barrier_1_with_door_1", "barrier_1_with_door_2",
                                  "barrier_1_with_door_3", "barrier_2_with_door_1", "barrier_2_with_door_2",
                                  "barrier_2_with_door_3", "ramp_platform_1", "ramp_slope_1", "ramp_platform_2",
                                  "ramp_slope_2"] or "pit" in scene_object:
                object_label = len(scene_config.target_colors) + 2
            elif scene_object in ["agent"]:
                object_label = len(scene_config.target_colors) + 1
            elif scene_object in ["occluder"]:
                object_label = len(scene_config.target_colors) + 3
            else:
                object_label = 0
            e[scene_object]["object_label"] = object_label
        e_ = pre_proccess_state_data(e)
        e_ = process_bounds(e_)
        state_data_new.append(e_)

    return state_data_new

def process_dataset():
    data = {}
    for data_dir in ["scene_1_v2"]:
        scene_types = os.listdir(data_dir)
        if data_dir not in data:
            data[data_dir] = {}
        for scene_type in scene_types:
            if scene_type not in data[data_dir]:
                data[data_dir][scene_type] = {}
            trials = os.listdir(join(data_dir, scene_type, "Agent_0"))
            for trial in tqdm.tqdm(trials):
                data[data_dir][scene_type][trial] = {}
                if data_dir == "scene_3":
                    with open(join(data_dir, scene_type, "Agent_0", trial, "Familiarization_video_1",
                                   "state_info.json")) as fp:
                        with open(join(data_dir, scene_type, "Agent_0", trial, "Familiarization_video_1",
                                   "new_state_info.json"), "w") as new_fp:
                            json.dump(process_trajectory_state_data(json.load(fp)), new_fp)
                    with open(join(data_dir, scene_type, "Agent_0", trial, "Test_A", "state_info.json")) as fp:
                        new_data = process_trajectory_state_data(json.load(fp))
                        with open(join(data_dir, scene_type, "Agent_0", trial, "Test_A", "new_state_info.json"), "w") as new_fp:
                            json.dump(new_data, new_fp)
                    with open(join(data_dir, scene_type, "Agent_0", trial, "Test_B", "state_info.json")) as fp:
                        with open(join(data_dir, scene_type, "Agent_0", trial, "Test_B", "new_state_info.json"), "w") as new_fp:
                            json.dump(process_trajectory_state_data(json.load(fp)), new_fp)


def pre_process_trajectories():
    for data_dir in ["scene_2_v1", "scene_2_v2"]:
        scene_types = os.listdir(data_dir)
        data = {
            data_dir: {}
        }
        for scene_type in scene_types:
            if scene_type not in data[data_dir]:
                data[data_dir][scene_type] = {}
            trials = os.listdir(join(data_dir, scene_type, "Agent_0"))
            for trial in tqdm.tqdm(trials, postfix=scene_type):
                data[data_dir][scene_type][trial] = {}
                if trial == ".DS_Store":
                    continue
                if data_dir in ["scene_1", "scene_1_human_exp", "scene_1_train", "scene_1_test", "scene_2",
                                "scene_2_human_exp_new_camera", "scene_1_v2", "scene_1_human_exp_v2",
                                "scene_2_human_exp_v2", "scene_2_v2", "scene_2_human_exp_v1", "scene_2_v1"]:
                    for sub_dir, sub_key in zip(["Familarization_video_1", "Test_video_A", "Test_video_B"],
                                                ["familiarization", "test_a", "test_b"]):
                        base_dir = join(data_dir, scene_type, "Agent_0", trial, sub_dir)
                        with open(join(base_dir, "state_info.json")) as fp:
                            data[data_dir][scene_type][trial][sub_key] = process_trajectory_state_data(
                                json.load(fp), base_dir)
                elif data_dir in ["scene_3", "scene_3_human_exp", "scene_3_human_exp_v2", "scene_3_v2"]:
                    for sub_dir, sub_key in zip(["Familarization_video_1", "Test_A", "Test_B"],
                                                ["familiarization", "test_a", "test_b"]):
                        base_dir = join(data_dir, scene_type, "Agent_0", trial, sub_dir)
                        with open(join(base_dir, "state_info.json")) as fp:
                            data[data_dir][scene_type][trial][sub_key] = process_trajectory_state_data(
                                json.load(fp), base_dir)
                    get_scene_labels(data[data_dir][scene_type][trial], data_dir)
                elif data_dir in ["scene_4", "scene_4_human_exp", "scene_4_train", "scene_4_test",
                                  "scene_4_human_exp_v2", "scene_4_v2"]:
                    for sub_dir, sub_key in zip(["Familarization_video_1", "Familarization_video_2",
                                                 "Familarization_video_3", "Familarization_video_4", "Test_A",
                                                 "Test_B"],
                                                ["familiarization_1", "familiarization_2", "familiarization_3",
                                                 "familiarization_4", "test_a", "test_b"]):
                        base_dir = join(data_dir, scene_type, "Agent_0", trial, sub_dir)
                        with open(join(base_dir, "state_info.json")) as fp:
                            data[data_dir][scene_type][trial][sub_key] = process_trajectory_state_data(
                                json.load(fp), base_dir)
                    get_scene_labels(data[data_dir][scene_type][trial], data_dir)

        with open(join("proccessed_data", f"{data_dir}.pickle"), "wb") as fp:
            pickle.dump(data, fp)


def count_images():
    all_images = []
    for data_dir in ["scene_1", "scene_2", "scene_3", "scene_4"]:
        scene_types = os.listdir(data_dir)
        for scene_type in scene_types:
            if scene_type != ".DS_Store":
                trials = os.listdir(join(data_dir, scene_type, "Agent_0"))
                for trial in trials:
                    if trial != ".DS_Store":
                        trial_folders = os.listdir(join(data_dir, scene_type, "Agent_0", trial))
                        for trial_folder in trial_folders:
                            image_list = os.listdir(join(data_dir, scene_type, "Agent_0", trial, trial_folder,
                                                                 "images_c"))
                            image_list = [join(data_dir, scene_type, "Agent_0", trial, trial_folder,
                                                                 "images_c", e) for e in image_list if "id_" not in e]
                            all_images.extend(image_list)
    return len(all_images)


def get_train_test_set():
    total_number_of_inputs = count_images()
    train, test = 60, 40
    train_set_size = total_number_of_inputs*train/100
    test_set_size = total_number_of_inputs*test/100
    return train_set_size, test_set_size

def pre_proccess_state_data(state_data):
    new_state_data = {}
    for obj in state_data.keys():
        new_state_data[obj] = {}
        if obj == "barrier":
            new_state_data[obj]["height"] = state_data[obj]["obstacle_height"]
            new_state_data[obj]["width"] = state_data[obj]["obstacle_width"]
            new_state_data[obj]["depth"] = state_data[obj]["obstacle_depth"]
        if obj == ["agent", "goal"]:
            new_state_data[obj]["size"] = state_data[obj]["size"]
        if obj == "occluder":
            new_state_data[obj]["height"] = state_data[obj]["height"]
            new_state_data[obj]["width"] = state_data[obj]["width"]
            new_state_data[obj]["depth"] = state_data[obj]["depth"]
        if obj != "camera":
            new_state_data[obj] = state_data[obj]["bounding_box"]
            new_state_data[obj]["rotation"] = state_data[obj]["rotation"]
            new_state_data[obj]["velocity"] = state_data[obj]["velocity"]
            new_state_data[obj]["segmentation_color"] = state_data[obj]["segmentation_color"]
            new_state_data[obj]["angular_velocity"] = state_data[obj]["angular_velocity"]
            new_state_data[obj]["object_label"] = state_data[obj]["object_label"]
            new_state_data[obj]["visibility"] = state_data[obj]["visibility"]
            if obj == "agent":
                new_state_data[obj]["force"] = state_data[obj]["force"]
        else:
            new_state_data["camera"] = state_data["camera"]

    return new_state_data

def process_bounds(state):
    # print(json.dumps(state, indent=2))
    new_state = state.copy()
    # del new_state["camera"]
    for keys in new_state.keys():
        if keys != "camera":
            new_state[keys]["dimension_height"] = distance_between_points(new_state[keys]["top"], new_state[keys]["bottom"])
            new_state[keys]["dimension_width"] = distance_between_points(new_state[keys]["right"], new_state[keys]["left"])
            new_state[keys]["dimension_depth"] = distance_between_points(new_state[keys]["front"], new_state[keys]["back"])
            if isinstance(new_state[keys]["rotation"], list):
                new_state[keys]["orientation"] = quaternion_to_euler_angle_vectorized2(
                    new_state[keys]["rotation"][3], new_state[keys]["rotation"][0], new_state[keys]["rotation"][1],
                    new_state[keys]["rotation"][2])
            else:
                new_state[keys]["orientation"] = new_state[keys]["rotation"]
            del new_state[keys]["top"]
            del new_state[keys]["bottom"]
            del new_state[keys]["right"]
            del new_state[keys]["left"]
            del new_state[keys]["front"]
            del new_state[keys]["back"]
            del new_state[keys]["rotation"]
    return state

def clear_space_sep_videos():
    for scene_dir in ["scene_1_human_exp_v2"]:
        subtypes = os.listdir(scene_dir)
        os.makedirs(f"{scene_dir}_cleaned", exist_ok=True)
        for subtype in subtypes:
            set_folders = os.listdir(join(scene_dir, subtype, "Agent_0"))
            os.makedirs(join(f"{scene_dir}_cleaned", subtype), exist_ok=True)
            for set_folder in tqdm.tqdm(set_folders):
                os.makedirs(join(f"{scene_dir}_cleaned", subtype, set_folder), exist_ok=True)
                fam_test_folders = os.listdir(join(scene_dir, subtype, "Agent_0", set_folder))
                # copyfile(join(base_dirs, "inputs", e), join("new_" + base_dirs, "inputs", f"{img_counter}.npy"))
                for fam_test in fam_test_folders:
                    with open(join(scene_dir, subtype, "Agent_0", set_folder, fam_test, "state_info.json"),
                              "r") as fp:
                        copyfile(join(scene_dir, subtype, "Agent_0", set_folder, fam_test, "scene_c.mp4"),
                                 join(f"{scene_dir}_cleaned", subtype, set_folder, f"{fam_test}.mp4"))
                        copyfile(join(scene_dir, subtype, "Agent_0", set_folder, fam_test, "scene_config.json"),
                                 join(f"{scene_dir}_cleaned", subtype, set_folder, f"scene_config_{fam_test}.json"))
                        state_datas = json.load(fp)
                        state_datas_ids = random.sample(range(len(state_datas)), k=round(0.25 * len(state_datas)))
                        not_state_datas_ids = [e for e in range(len(state_datas)) if e not in state_datas_ids]
                        # Clear up 4/5 of images for each trial
                        # for state_datas_id in not_state_datas_ids:
                        #     os.remove(join(scene_dir, subtype, "Agent_0", set_folder, fam_test, "images_c",
                        #                           f"img_image-{state_datas_id}.png"))
                        #     os.remove(join(scene_dir, subtype, "Agent_0", set_folder, fam_test, "images_c",
                        #                    f"id_image-{state_datas_id}.png"))


def get_train_test_split():
    train_test_ids = {
        "train_set": [],
        "test_set": []
    }
    for data_dir in ["scene_1_v2", "scene_2_v2", "scene_3_v2", "scene_4_v2"]:
        test_types = os.listdir(data_dir)
        for test_type in test_types:
            set_list = os.listdir(os.path.join(data_dir, test_type, "Agent_0"))
            test_set_ids = random.sample(range(len(set_list)), k=round(0.2 * len(set_list)))
            train_set_ids = [e for e in range(len(set_list)) if e not in test_set_ids]
            train_test_ids["train_set"].extend([[data_dir, test_type, "Agent_0", f"Set_{e}"] for e in train_set_ids])
            train_test_ids["test_set"].extend([[data_dir, test_type, "Agent_0", f"Set_{e}"] for e in test_set_ids])
    return train_test_ids



def pre_process_image():
    image_number = 0
    scene_config = scene_configuration.SceneConfiguration()
    # train_set_size, test_set_size = get_train_test_set()

    data_set_counter = {
        "train_set": 0,
        "test_set": 0
    }
    train_test_id = get_train_test_split()
    os.makedirs(join("train_set", "inputs"), exist_ok=True)
    os.makedirs(join("test_set", "inputs"), exist_ok=True)
    os.makedirs(join("train_set", "masks"), exist_ok=True)
    os.makedirs(join("test_set", "masks"), exist_ok=True)
    os.makedirs(join("train_set", "state"), exist_ok=True)
    os.makedirs(join("test_set", "state"), exist_ok=True)
    # train_test_id["train_set"] = [e for e in train_test_id["train_set"] if "scene_2" in e]
    # train_test_id["test_set"] = [e for e in train_test_id["test_set"] if "scene_2" in e]
    for data_split in ["train_set", "test_set"]:
        for elemen in tqdm.tqdm(train_test_id[data_split]):
            trial_folders = os.listdir(join(*elemen[0:2], "Agent_0", elemen[-1]))
            for trial_folder in trial_folders:
                with open(join(*elemen[0:2], "Agent_0", elemen[-1], trial_folder, "state_info.json"), "r") as fp:
                    state_datas = json.load(fp)
                    state_datas_ids = random.sample(range(len(state_datas)), k=round(0.05*len(state_datas)))
                    for state_datas_id in state_datas_ids:
                        state_data = state_datas[state_datas_id]
                        img = Image.open(join(*elemen[0:2], "Agent_0", elemen[-1], trial_folder, "images_c",
                                              f"img_image-{state_datas_id}.png"))
                        img = np.array(img)
                        img = img / 255
                        img = np.moveaxis(img, 2, 0)
                        np.save(os.path.join(data_split, "inputs", f"{data_set_counter[data_split]}.npy"), img)
                        mask = Image.open(join(*elemen[0:2], "Agent_0", elemen[-1], trial_folder, "images_c",
                                               f"id_image-{state_datas_id}.png"))
                        mask = np.array(mask)
                        mask_ = np.zeros(mask.shape[0:2])
                        for object_no, scene_object in enumerate(state_data.keys()):
                            if "segmentation_color" in state_data[scene_object]:
                                if scene_object in ["goal", "goal_1", "goal_2"]:
                                    object_label = 1 + scene_config.target_colors.index(
                                        state_data[scene_object]["color"])
                                elif scene_object in ["barrier", "barrier_1", "barrier_2", "barrier_with_door_1", "barrier_with_door_2",
                                  "ramp_platform", "ramp_slope", "barrier_1_with_door_1", "barrier_1_with_door_2",
                                  "barrier_1_with_door_3", "barrier_2_with_door_1", "barrier_2_with_door_2",
                                  "barrier_2_with_door_3", "ramp_platform_1", "ramp_slope_1", "ramp_platform_2",
                                  "ramp_slope_2"] or "pit" in scene_object:
                                    object_label = len(scene_config.target_colors) + 2
                                elif scene_object in ["agent"]:
                                    object_label = len(scene_config.target_colors) + 1
                                elif scene_object in ["occluder"]:
                                    object_label = len(scene_config.target_colors) + 3
                                else:
                                    object_label = 0
                                seg_color = state_data[scene_object]["segmentation_color"]
                                state_data[scene_object]["object_label"] = object_label
                                state_data[scene_object]["visibility"] = np.any(mask[
                                    (mask[:, :, 0] == seg_color[0]) &
                                    (mask[:, :, 1] == seg_color[1]) &
                                    (mask[:, :, 2] == seg_color[2])
                                    ] )
                                # mask_[
                                #     (mask[:, :, 0] == seg_color[0]) &
                                #     (mask[:, :, 1] == seg_color[1]) &
                                #     (mask[:, :, 2] == seg_color[2])
                                #     ] = object_label
                        # Save images
                        # mask_ = mask_.astype(np.uint8)
                        np.save(os.path.join(data_split, "masks", f"{data_set_counter[data_split]}.npy"), mask)

                        state_data = pre_proccess_state_data(state_data)

                        state_data = process_bounds(state_data)

                        with open(os.path.join(data_split, "state",
                                               f"{data_set_counter[data_split]}.pickle"), "wb") as fp:
                            pickle.dump(state_data, fp)
                        data_set_counter[data_split] += 1

    # for data_dir in ["old_data/scene_3"]:
    #     scene_types = os.listdir(data_dir)
    #     for scene_type in scene_types:
    #         if scene_type != ".DS_Store":
    #             trials = os.listdir(join(data_dir, scene_type, "Agent_0"))
    #             for trial in tqdm.tqdm(trials):
    #                 if trial != ".DS_Store":
    #                     trial_folders = os.listdir(join(data_dir, scene_type, "Agent_0", trial))
    #                     for trial_folder in trial_folders:
    #                         with open(join(data_dir, scene_type, "Agent_0", trial, trial_folder, "state_info.json"), "r") as fp:
    #                             state_datas = json.load(fp)
    #
    #                         for idx, state_data in enumerate(state_datas):
    #                             if np.random.choice([0, 1], p=[0.95, 0.05]) == 1:
    #                                 selected_set = random.choice(["train", "val"])
    #                                 selected_set = "train" if selected_set == "val" and data_set["val"] == 0 else selected_set
    #                                 img = Image.open(join(data_dir, scene_type, "Agent_0", trial, trial_folder, "images_c",
    #                                                       f"img_image-{idx}.png"))
    #                                 img = np.array(img)
    #                                 img = img/255
    #                                 img = np.moveaxis(img, 2, 0)
    #                                 np.save(os.path.join(selected_set, "inputs",f"{data_set_counter[selected_set]}.npy"), img)
    #                                 mask = Image.open(join(data_dir, scene_type, "Agent_0", trial, trial_folder, "images_c",
    #                                                        f"id_image-{idx}.png"))
    #                                 mask = np.array(mask)
    #                                 mask_ = np.zeros(mask.shape[0:2])
    #                                 for object_no, scene_object in enumerate(state_data.keys()):
    #                                     if "segmentation_color" in state_data[scene_object]:
    #                                         if scene_object in ["goal", "goal_1", "goal_2"]:
    #                                             object_label = 3 + scene_config.target_colors.index(state_data[scene_object]["color"])
    #                                         elif scene_object in ["barrier", "barrier_1", "barrier_2"]:
    #                                             object_label = 2
    #                                         elif scene_object in ["agent"]:
    #                                             object_label = 1
    #                                         elif scene_object in ["occluder"]:
    #                                             object_label = len(scene_config.target_colors) + 3
    #                                         else:
    #                                             object_label = 0
    #                                         seg_color = state_data[scene_object]["segmentation_color"]
    #                                         state_data[scene_object]["object_label"] = object_label
    #                                         mask_[
    #                                             (mask[:, :, 0] == seg_color[0]) &
    #                                             (mask[:, :, 1] == seg_color[1]) &
    #                                             (mask[:, :, 2] == seg_color[2])
    #                                         ] = object_label
    #                                 # Save images
    #                                 mask_ = mask_.astype(np.uint8)
    #                                 np.save(os.path.join(selected_set, "masks", f"{data_set_counter[selected_set]}.npy"), mask_)
    #                                 np.save(os.path.join(selected_set, "masks", f"{data_set_counter[selected_set]}.npy"),
    #                                         mask_)
    #                                 state_data = pre_proccess_state_data(state_data)
    #                                 state_data = process_bounds(state_data)
    #                                 with open(os.path.join(selected_set, "state",
    #                                                        f"{data_set_counter[selected_set]}.pickle"), "wb") as fp:
    #                                     pickle.dump(state_data, fp)
    #                                 image_number += 1
    #                                 data_set[selected_set] -= 1
    #                                 data_set_counter[selected_set] += 1
    #                                 if data_set["train"] < 0:
    #                                     exit()

def distance_between_points(p1, p2):
    p1, p2 = np.array(p1), np.array(p2)
    squared_dist = np.sum((p1 - p2) ** 2, axis=0)
    dist = np.sqrt(squared_dist)
    return dist

def quaternion_to_euler_angle_vectorized2(w, x, y, z):
    ysqr = y * y

    t0 = +2.0 * (w * x + y * z)
    t1 = +1.0 - 2.0 * (x * x + ysqr)
    X = np.degrees(np.arctan2(t0, t1))

    t2 = +2.0 * (w * y - z * x)

    t2 = np.clip(t2, a_min=-1.0, a_max=1.0)
    Y = np.degrees(np.arcsin(t2))

    t3 = +2.0 * (w * z + x * y)
    t4 = +1.0 - 2.0 * (ysqr + z * z)
    Z = np.degrees(np.arctan2(t3, t4))

    return {"x":X, "y":Y, "z":Z}



def temp_process_bounds():
    for base_dirs in ["train", "val"]:
        list_of_states = os.listdir(join(base_dirs, "state"))
        os.makedirs(join(base_dirs, "new_state"), exist_ok=True)
        for states in tqdm.tqdm(list_of_states):
            with open(join(base_dirs, "state", states), "rb") as fp:
                state_data = pickle.load(fp)
            new_state_data = process_bounds(state_data)
            with open(join(base_dirs, "new_state", states), "wb") as fp:
                pickle.dump(new_state_data, fp)

def copy_data():
    for base_dirs in ["val"]:
        img_counter = 0
        os.makedirs("new_" + base_dirs, exist_ok=True)
        os.makedirs(join("new_" + base_dirs, "inputs"), exist_ok=True)
        os.makedirs(join("new_" + base_dirs, "masks"), exist_ok=True)
        os.makedirs(join("new_" + base_dirs, "state"), exist_ok=True)
        image_list = os.listdir(join(base_dirs, "inputs"))
        if base_dirs == "train":
            image_list = random.sample(image_list, 20000)
        for e in tqdm.tqdm(image_list):
            copyfile(join(base_dirs, "inputs", e), join("new_" + base_dirs, "inputs", f"{img_counter}.npy"))
            copyfile(join(base_dirs, "masks", e), join("new_" + base_dirs, "masks", f"{img_counter}.npy"))
            state_name = e.replace(".npy", "") + ".pickle"
            copyfile(join(base_dirs, "state", state_name), join("new_" + base_dirs, "state", f"{img_counter}.pickle"))
            img_counter += 1

def merge_data_set():
    data_set_1 = "/media/data2/machinecommonsense"
    data_set_2 = "/media/data2/machinecommonsense_v2/machinecommonsense"
    data_set_1_train = os.listdir(os.path.join(data_set_1, "train_set", "inputs"))

    data_set_1_train = random.sample(data_set_1_train, k=round(0.21 * len(data_set_1_train)))
    data_set_1_test = os.listdir(os.path.join(data_set_1, "test_set", "inputs"))
    data_set_1_test = random.sample(data_set_1_test, k=round(0.21 * len(data_set_1_test)))

    data_set_2_train = os.listdir(os.path.join(data_set_2, "train_set", "inputs"))
    data_set_2_train = random.sample(data_set_2_train, k=round(0.4 * len(data_set_2_train)))
    data_set_2_test = os.listdir(os.path.join(data_set_2, "test_set", "inputs"))
    data_set_2_test = random.sample(data_set_2_test, k=round(0.4 * len(data_set_2_test)))

    os.makedirs("merged_dataset", exist_ok=True)
    os.makedirs(os.path.join("merged_dataset", "train_set"))
    os.makedirs(os.path.join("merged_dataset", "train_set", "inputs"))
    os.makedirs(os.path.join("merged_dataset", "train_set", "masks"))
    os.makedirs(os.path.join("merged_dataset", "train_set", "state"))
    os.makedirs(os.path.join("merged_dataset", "test_set", "inputs"))
    os.makedirs(os.path.join("merged_dataset", "test_set", "masks"))
    os.makedirs(os.path.join("merged_dataset", "test_set", "state"))
    train_img_counter = 0
    for file_ids in tqdm.tqdm(data_set_1_train):
        copyfile(join(os.path.join(data_set_1, "train_set", "inputs", file_ids)),
                 join("merged_dataset", "train_set", "inputs", f"{train_img_counter}.npy"))
        copyfile(join(os.path.join(data_set_1, "train_set", "masks", file_ids)),
                 join("merged_dataset", "train_set", "masks", f"{train_img_counter}.npy"))
        state_name = file_ids.replace(".npy", "") + ".pickle"
        copyfile(join(os.path.join(data_set_1, "train_set", "state", state_name)),
                 join("merged_dataset", "train_set", "state", f"{train_img_counter}.pickle"))
        train_img_counter += 1
    for file_ids in tqdm.tqdm(data_set_2_train):
        copyfile(join(os.path.join(data_set_2, "train_set", "inputs",file_ids)),
                 join("merged_dataset", "train_set", "inputs", f"{train_img_counter}.npy"))
        copyfile(join(os.path.join(data_set_2, "train_set", "masks", file_ids)),
                 join("merged_dataset", "train_set", "masks", f"{train_img_counter}.npy"))
        state_name = file_ids.replace(".npy", "") + ".pickle"
        copyfile(join(os.path.join(data_set_2, "train_set", "state", state_name)),
                 join("merged_dataset", "train_set", "state", f"{train_img_counter}.pickle"))
        train_img_counter += 1
    test_img_counter = 0
    for file_ids in tqdm.tqdm(data_set_1_test):
        copyfile(join(os.path.join(data_set_1, "test_set", "inputs", file_ids)),
                 join("merged_dataset", "test_set", "inputs", f"{test_img_counter}.npy"))
        copyfile(join(os.path.join(data_set_1, "test_set", "masks", file_ids)),
                 join("merged_dataset", "test_set", "masks", f"{test_img_counter}.npy"))
        state_name = file_ids.replace(".npy", "") + ".pickle"
        copyfile(join(os.path.join(data_set_1, "test_set", "state", state_name)),
                 join("merged_dataset", "test_set", "state", f"{test_img_counter}.pickle"))
        test_img_counter += 1
    for file_ids in tqdm.tqdm(data_set_2_test):
        copyfile(join(os.path.join(data_set_2, "test_set", "inputs", file_ids)),
                 join("merged_dataset", "test_set", "inputs", f"{test_img_counter}.npy"))
        copyfile(join(os.path.join(data_set_2, "test_set", "masks", file_ids)),
                 join("merged_dataset", "test_set", "masks", f"{test_img_counter}.npy"))
        state_name = file_ids.replace(".npy", "") + ".pickle"
        copyfile(join(os.path.join(data_set_2, "test_set", "state", state_name)),
                 join("merged_dataset", "test_set", "state", f"{test_img_counter}.pickle"))
        test_img_counter += 1
    print(f"Total train images {train_img_counter}")
    print(f"Total test images {test_img_counter}")


def create_val_set():
    test_set_path = "merged_dataset/test_set"
    base_path = "merged_dataset"
    img_list = os.listdir(os.path.join(test_set_path, "inputs"))
    img_list = random.sample(img_list, k=5000)
    img_counter = 0
    os.makedirs(os.path.join(base_path, "val_set"))
    os.makedirs(os.path.join(base_path, "val_set", "inputs"))
    os.makedirs(os.path.join(base_path, "val_set", "masks"))
    os.makedirs(os.path.join(base_path, "val_set", "state"))
    for file_ids in tqdm.tqdm(img_list):
        copyfile(join(os.path.join(test_set_path, "inputs", file_ids)),
                 join(base_path, "val_set", "inputs", f"{img_counter}.npy"))
        copyfile(join(os.path.join(test_set_path, "masks", file_ids)),
                 join(base_path, "val_set", "masks", f"{img_counter}.npy"))
        state_name = file_ids.replace(".npy", "") + ".pickle"
        copyfile(join(os.path.join(test_set_path, "state", state_name)),
                 join(base_path, "val_set", "state", f"{img_counter}.pickle"))
        img_counter += 1

def trim_dataset():
    scene_config = scene_configuration.SceneConfiguration()
    for base_dir in ["human_exp_v2"]:
        scene_dirs = os.listdir(join(base_dir))
        new_base_dir = join("/media/data3/derender/test_data", base_dir + "_trimmed")
        os.makedirs(new_base_dir, exist_ok=True)
        for scene_dir in tqdm.tqdm(scene_dirs):
            subtypes = os.listdir(join(base_dir, scene_dir))
            os.makedirs(join(new_base_dir, scene_dir), exist_ok=True)
            for subtype in tqdm.tqdm(subtypes):
                trials = os.listdir(join(base_dir, scene_dir, subtype, "Agent_0"))
                os.makedirs(join(new_base_dir, scene_dir, subtype), exist_ok=True)
                for trial in tqdm.tqdm(trials):
                    os.makedirs(join(new_base_dir, scene_dir, subtype, "Agent_0", trial), exist_ok=True)
                    sub_dirs = os.listdir(join(base_dir, scene_dir, subtype, "Agent_0", trial))
                    for sub_dir in sub_dirs:
                        os.makedirs(join(new_base_dir, scene_dir, subtype, "Agent_0", trial, sub_dir), exist_ok=True)
                        os.makedirs(join(new_base_dir, scene_dir, subtype, "Agent_0", trial, sub_dir, "images_c"),
                                    exist_ok=True)
                        with open(
                                join(base_dir, scene_dir, subtype, "Agent_0", trial, sub_dir, "state_info.json"), "r") as fp:
                            state_datas = json.load(fp)
                        img_counter = 0
                        new_state_datas = []
                        for state_datas_id in tqdm.tqdm(range(0, len(state_datas), 5)):
                            copyfile(
                                join(base_dir, scene_dir, subtype, "Agent_0", trial, sub_dir, "images_c",
                                     f"img_image-{state_datas_id}.png"),
                                join(new_base_dir, scene_dir, subtype, "Agent_0", trial, sub_dir, "images_c",
                                     f"img_image-{img_counter}.png"))
                            copyfile(
                                join(base_dir, scene_dir, subtype, "Agent_0", trial, sub_dir, "images_c",
                                     f"id_image-{state_datas_id}.png"),
                                join(new_base_dir, scene_dir, subtype, "Agent_0", trial, sub_dir, "images_c",
                                     f"id_image-{img_counter}.png"))
                            img_counter += 1
                            new_state_datas.append(state_datas[state_datas_id])
                        with open(join(new_base_dir, scene_dir, subtype, "Agent_0", trial, sub_dir, "state_info.json"), "w") as fp:
                            json.dump(new_state_datas, fp)


if __name__ == '__main__':
    # a = np.zeros([2,3,3])
    # a[1,1,0] = 20
    # a[1,2,0] = 20
    # a[1,1,1] = 21
    # a[1,1,2] = 22
    # b = np.zeros(a.shape[0:2])
    # b[(a[:, :, 0] == 20) & (a[:, : , 1] == 21) & (a[:, :, 2] == 22)] = 3
    # print(a)
    # print(b)
    # copy_data()
    # temp_process_bounds()
    # process_dataset()
    # pre_process_trajectories()
    # merge_data_set()
    create_val_set()
    # clear_space_sep_videos()
    # pre_process_image()
    # trim_dataset()