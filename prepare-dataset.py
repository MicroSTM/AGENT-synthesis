from os.path import join
from os import listdir, makedirs
import random
from shutil import copytree, rmtree, copyfile
import os
from os.path import basename
import json
from pre_proccess_data import process_trajectory_state_data
import pickle
import shutil

def save_fam_video(fam_paths, target_path):
    for e in fam_paths:
        if os.path.isdir(join(target_path, basename(e))):
            rmtree(join(target_path, basename(e)))
        file_name = basename(e)
        file_name = file_name.replace("amilarization", "amiliarization")
        copytree(e, join(target_path, file_name))



def create_dataset(base_paths, target_base_path, test_only, size=[0], versions=["version 1"], surprise_expected_reversed=False):
    if not test_only:
        create_train_data(base_paths, target_base_path, size, versions, surprise_expected_reversed)
    else:
        create_test_data(base_paths, target_base_path, versions, surprise_expected_reversed)


def create_train_data(base_paths, target_base_path, sizes, versions, surprise_expected_reversed=False):
    train_set_no = 0
    val_set_no = 0
    train_path, val_path = join(target_base_path, "train_set"),   join(target_base_path, "validation_set")
    makedirs(train_path, exist_ok=True)
    makedirs(val_path, exist_ok=True)
    # makedirs(test_path, exist_ok=True)
    for base_path, size, version in zip(base_paths, sizes, versions):
        trials = [join(base_path, "Agent_0", e) for e in listdir(join(base_path, "Agent_0"))]
        # Temp
        random.shuffle(trials)
        trials = trials[:size]
        val_list, train_list = trials[0:round(0.2*len(trials))], trials[round(0.2*len(trials)):]
        for trial in trials:
            sub_dirs = listdir(join(trial))
            fam_dir = [join(trial, e) for e in sub_dirs if "fam" in e.lower()]
            test_a = [join(trial, e) for e in sub_dirs if "_A" in e][0]
            test_b = [join(trial, e) for e in sub_dirs if "_B" in e][0]
            if not surprise_expected_reversed:
                surprising, expected = test_a, test_b
            else:
                surprising, expected = test_b, test_a
            if trial in train_list:
                if os.path.isdir(join(train_path, f"Trial_{train_set_no}")):
                    rmtree(join(train_path, f"Trial_{train_set_no}"))
                makedirs(join(train_path, f"Trial_{train_set_no}"))
                save_fam_video(fam_dir, join(train_path, f"Trial_{train_set_no}"))
                copytree(join(trial, expected),
                         join(train_path, f"Trial_{train_set_no}", "expected"))
                open(join(train_path, f"Trial_{train_set_no}", version), "w")
                train_set_no += 1
            else:
                if os.path.isdir(join(val_path, f"Trial_{val_set_no}")):
                    rmtree(join(val_path, f"Trial_{val_set_no}"))
                makedirs(join(val_path, f"Trial_{val_set_no}"), exist_ok=True)
                save_fam_video(fam_dir, join(val_path, f"Trial_{val_set_no}"))
                copytree(join(trial, expected),
                         join(val_path, f"Trial_{val_set_no}", "expected"))
                open(join(val_path, f"Trial_{val_set_no}", version), "w")
                val_set_no += 1
            # if os.path.isdir(join(target_base_path, "test_set", f"Set_{test_set_no}")):
            #     rmtree(join(target_base_path, "test_set", f"Set_{test_set_no}"))
            # makedirs(join(target_base_path, "test_set", f"Set_{test_set_no}"), exist_ok=True)
            # save_fam_video(fam_dir, join(target_base_path, "test_set", f"Set_{test_set_no}"))
            # copytree(join(trial, surprising), join(target_base_path, "test_set", f"Set_{test_set_no}", "surprising"))
            # test_set_no += 1
            # if os.path.isdir(join(target_base_path, "test_set", f"Set_{test_set_no}")):
            #     rmtree(join(target_base_path, "test_set", f"Set_{test_set_no}"))
            # makedirs(join(target_base_path, "test_set", f"Set_{test_set_no}"), exist_ok=True)
            # save_fam_video(fam_dir, join(target_base_path, "test_set", f"Set_{test_set_no}"))
            # copytree(join(trial, expected), join(target_base_path, "test_set", f"Set_{test_set_no}", "expected"))
            # test_set_no += 1


def create_test_data(base_paths, target_base_path, versions, surprise_expected_reversed):
    test_set_no = 0
    test_path = join(target_base_path, "test_set")
    makedirs(test_path, exist_ok=True)
    for base_path, version in zip(base_paths, versions):
        trials = [join(base_path, "Agent_0", e) for e in listdir(join(base_path, "Agent_0"))]
        # Temp
        random.shuffle(trials)
        for trial in trials:
            sub_dirs = listdir(join(trial))
            fam_dir = [join(trial, e) for e in sub_dirs if "fam" in e.lower()]
            test_a = [join(trial, e) for e in sub_dirs if "_A" in e][0]
            test_b = [join(trial, e) for e in sub_dirs if "_B" in e][0]
            if not surprise_expected_reversed:
                surprising, expected = test_a, test_b
            else:
                surprising, expected = test_b, test_a
            if os.path.isdir(join(target_base_path, "test_set", f"Trial_{test_set_no}")):
                rmtree(join(target_base_path, "test_set", f"Trial_{test_set_no}"))
            makedirs(join(target_base_path, "test_set", f"Trial_{test_set_no}"), exist_ok=True)
            save_fam_video(fam_dir, join(target_base_path, "test_set", f"Trial_{test_set_no}"))
            copytree(join(trial, surprising), join(target_base_path, "test_set", f"Trial_{test_set_no}",
                                                   "surprising"))
            copytree(join(trial, expected), join(target_base_path, "test_set", f"Trial_{test_set_no}",
                                                 "expected"))
            open(join(target_base_path, "test_set", f"Trial_{test_set_no}", version), "w")
            # if os.path.isdir(join(target_base_path, "test_set", f"Set_{test_set_no}_Expected")):
            #     rmtree(join(target_base_path, "test_set", f"Set_{test_set_no}_Expected"))
            # makedirs(join(target_base_path, "test_set", f"Set_{test_set_no}_Expected"), exist_ok=True)
            # save_fam_video(fam_dir, join(target_base_path, "test_set", f"Set_{test_set_no}_Expected"))
            #
            test_set_no += 1


def process_scene_1(v1_base_path, v2_base_path, target_base_path, test_only):
    """
    scene 1 -> scene 2 action efficiency
    type 1 v1 and v2 -> type 2.1
    type 2 v1 and v2-> type 2.2
    type 3 v1 -> type 2.3
    type 4 v2 -> type 2.4
    type 5 v2 -> type 2.5
    :return:
    """

    makedirs(join(target_base_path, "final_dataset", "scenario_2_action_efficiency"), exist_ok=True)
    # Type 1 v1 and v2
    target_path = join(target_base_path, "final_dataset", "scenario_2_action_efficiency", "type_2.1")
    makedirs(target_path, exist_ok=True)
    create_dataset(base_paths=[join(v1_base_path, "type_1"), join(v2_base_path, "type_1")],
                   target_base_path=target_path, test_only=test_only, size=[50, 50], versions=["version_1", "version_2"])

    # Type 2 v1 and v2
    target_path = join(target_base_path, "final_dataset", "scenario_2_action_efficiency", "type_2.2")
    makedirs(target_path, exist_ok=True)
    create_dataset(base_paths=[join(v1_base_path, "type_2"), join(v2_base_path, "type_2")],
                   target_base_path=target_path, test_only=test_only, size=[50, 50], versions=["version_1", "version_2"])

    # Type 3 v1
    target_path = join(target_base_path, "final_dataset", "scenario_2_action_efficiency", "type_2.3")
    makedirs(target_path, exist_ok=True)
    create_dataset(base_paths=[join(v1_base_path, "type_3")],
                   target_base_path=target_path, test_only=test_only, size=[100], versions=["version_1"])

    # Type 4 v2
    target_path = join(target_base_path, "final_dataset", "scenario_2_action_efficiency", "type_2.4")
    makedirs(target_path, exist_ok=True)
    create_dataset(base_paths=[join(v2_base_path, "type_4")],
                   target_base_path=target_path, test_only=test_only, size=[200], versions=["version_2"])

    # Type 5 v2
    target_path = join(target_base_path, "final_dataset", "scenario_2_action_efficiency", "type_2.5")
    makedirs(target_path, exist_ok=True)
    create_dataset(base_paths=[join(v2_base_path, "type_5")],
                   target_base_path=target_path, test_only=test_only, size=[100], versions=["version_2"])


def process_scene_2(v1_base_path, v2_base_path, target_base_path, test_only):
    """
    scene 2 -> scene 3 unobserved constraints
    type 1 v1 -> type 3.1
    type 2 v1 & v2 -> type 3.2
    :return:
    """

    makedirs(join(target_base_path, "final_dataset", "scenario_3_unobserved_constraints"), exist_ok=True)
    # Type 1 v1
    target_path = join(target_base_path, "final_dataset", "scenario_3_unobserved_constraints", "type_3.1")
    makedirs(target_path, exist_ok=True)
    create_dataset(base_paths=[join(v1_base_path, "type_1")],
                   target_base_path=target_path, test_only=test_only, size=[200], versions=["version_1"])

    # Type 2 v1 and v2
    target_path = join(target_base_path, "final_dataset", "scenario_3_unobserved_constraints", "type_3.2")
    makedirs(target_path, exist_ok=True)
    create_dataset(base_paths=[join(v1_base_path, "type_2"), join(v2_base_path, "type_2")],
                   target_base_path=target_path, test_only=test_only, size=[200, 100],
                   versions=["version_1", "version_2"])


def process_scene_3(v1_base_path, v2_base_path, target_base_path, test_only):
    """
    scene 3 -> scene 1 Goal preferences
    type 1.1.0, type 1.2.0 v1 and v2 -> type 1.2
    type 1.0 -> type 1.1
    type 2.0 -> type 1.3
    type 2.1.0, type 2.2.0 v1 and v2 -> type 1.4
    :return:
    """

    target_base_path = join(target_base_path, "final_dataset", "scenario_1_goal_preferences")
    makedirs(target_base_path, exist_ok=True)
    # Type 1.1.0 Type 1.2.0 v1 and v2
    target_path = join(target_base_path, "type_1.2")
    makedirs(target_path, exist_ok=True)
    create_dataset(base_paths=[join(v1_base_path, "type_1_1_0"), join(v1_base_path, "type_1_2_0"),
                               join(v2_base_path, "type_1_2_0")],
                   target_base_path=target_path, test_only=test_only, size=[50, 50, 100],
                   versions=["version_1", "version_1", "version_2"], surprise_expected_reversed=True)

    # Type 1.0 v1
    target_path = join(target_base_path, "type_1.1")
    makedirs(target_path, exist_ok=True)
    create_dataset(base_paths=[join(v1_base_path, "type_1_0"), join(v2_base_path, "type_1_0")],
                   target_base_path=target_path, test_only=test_only, size=[50, 100],
                   versions=["version_1", "version_2"], surprise_expected_reversed=True)

    # Type 2.0 v1
    target_path = join(target_base_path, "type_1.3")
    makedirs(target_path, exist_ok=True)
    create_dataset(base_paths=[join(v1_base_path, "type_2_0"), join(v2_base_path, "type_2_0")],
                   target_base_path=target_path, test_only=test_only, size=[50, 100],
                   versions=["version_1", "version_2"], surprise_expected_reversed=True)

    # Type 2.1.0 Type 2.2.0 v1 and v2
    target_path = join(target_base_path, "type_1.4")
    makedirs(target_path, exist_ok=True)
    create_dataset(base_paths=[join(v1_base_path, "type_2_1_0"), join(v1_base_path, "type_2_2_0"),
                               join(v2_base_path, "type_2_2_0")],
                   target_base_path=target_path, test_only=test_only, size=[50, 50, 100],
                   versions=["version_1", "version_1", "version_2"], surprise_expected_reversed=True)


def process_scene_4(v1_base_path, v2_base_path, target_base_path, test_only):
    """
    scene 4 -> scene 4 cost reward trade off
    type 1 v1 & v2 -> type 4.1
    type 2 v1 & v2 -> type 4.2
    :return:
    """

    target_base_path = join(target_base_path, "final_dataset", "scenario_4_cost_reward_trade_offs")
    makedirs(target_base_path, exist_ok=True)
    # Type 1 v1 and v2
    target_path = join(target_base_path, "type_4.1")
    makedirs(target_path, exist_ok=True)
    create_dataset(base_paths=[join(v1_base_path, "type_1"), join(v2_base_path, "type_1")],
                   target_base_path=target_path, test_only=test_only, size=[100, 200],
                   versions=["version_1", "version_2"], surprise_expected_reversed=True)

    # Type 1 v1 and v2
    target_path = join(target_base_path, "type_4.2")
    makedirs(target_path, exist_ok=True)
    create_dataset(base_paths=[join(v1_base_path, "type_2"), join(v2_base_path, "type_2")],
                   target_base_path=target_path, test_only=test_only, size=[100, 200],
                   versions=["version_1", "version_2"], surprise_expected_reversed=True)


def rename_version_files(dataset_files):
    scenario_list = listdir(dataset_files)
    for scenario in scenario_list:
        subtypes = listdir(join(dataset_files, scenario))
        for subtype in subtypes:
            train_tests = listdir(join(dataset_files, scenario, subtype))
            for train_test in train_tests:
                trials = listdir(join(dataset_files, scenario, subtype, train_test))
                for trial in trials:
                    if os.path.isfile(join(dataset_files, scenario, subtype, train_test, trial, "version_1")):
                        os.rename(join(dataset_files, scenario, subtype, train_test, trial, "version_1"),
                                  join(dataset_files, scenario, subtype, train_test, trial, "basic"))
                    if os.path.isfile(join(dataset_files, scenario, subtype, train_test, trial, "version_2")):
                        os.rename(join(dataset_files, scenario, subtype, train_test, trial, "version_2"),
                                  join(dataset_files, scenario, subtype, train_test, trial, "extended"))
                    os.rename(join(dataset_files, scenario, subtype, train_test, trial),
                              join(dataset_files, scenario, subtype, train_test, trial.replace("Set", "Trial")))


def process_state_data(dataset_path):
    scenario_list = listdir(dataset_path)
    os.makedirs("final_dataset", exist_ok=True)
    for scenario in ["scenario_4_cost_reward_trade_offs"]:
        data = {
            scenario: {}
        }
        subtypes = listdir(join(dataset_path, scenario))
        for subtype in subtypes:
            data[scenario][subtype] = {}
            train_tests = listdir(join(dataset_path, scenario, subtype))
            for train_test in train_tests:
                data[scenario][subtype][train_test] = {}
                trials = listdir(join(dataset_path, scenario, subtype, train_test))
                for trial in trials:
                    if "Set" in trial:
                        new_name = trial.replace("Set", "Trial")
                        os.rename(join(dataset_path, scenario, subtype, train_test, trial),
                                  join(dataset_path, scenario, subtype, train_test, new_name))
                        trial = new_name
                    data[scenario][subtype][train_test][trial] = {}
                    sub_dirs = listdir(join(dataset_path, scenario, subtype, train_test, trial))
                    for sub_dir in sub_dirs:
                        if sub_dir in ["version_1", "version_2", "basic", "extended"]:
                            # rename the file
                            os.rename(join(dataset_path, scenario, subtype, train_test, trial, sub_dir),
                                      join(dataset_path, scenario, subtype, train_test, trial, "version.txt"))
                            if sub_dir == "version_1":
                                version = "basic"
                            elif sub_dir == "version_2":
                                version = "extended"
                            else:
                                version = sub_dir
                            sub_dir = "version.txt"
                            # Write to the file
                            with open(join(dataset_path, scenario, subtype, train_test, trial, sub_dir), "w") as fp:
                                fp.write(version)
                            data[scenario][subtype][train_test][trial]["version"] = version
                        elif sub_dir == "version.txt":
                            with open(join(dataset_path, scenario, subtype, train_test, trial, "version.tx"), "r") as fp:
                                version = fp.read()
                            data[scenario][subtype][train_test][trial]["version"] = version
                        else:
                            data[scenario][subtype][train_test][trial][sub_dir] = {}
                        base_dir = join(dataset_path, scenario, subtype, train_test, trial, sub_dir)
                        if os.path.isfile(base_dir):
                            continue
                        with open(join(base_dir, "state_info.json")) as fp:
                            data[scenario][subtype][train_test][trial][sub_dir] = process_trajectory_state_data(
                                json.load(fp), base_dir)
        with open(join("final_dataset", f"{scenario}.pickle"), "wb") as fp:
            pickle.dump(data, fp)


def correct_version(dataset_path):
    scenario_list = listdir(dataset_path)
    os.makedirs("final_dataset_corrected", exist_ok=True)
    for scenario in scenario_list:
        with open(join("final_dataset", f"{scenario}.pickle"), "rb") as fp:
            data = pickle.load(fp)
        subtypes = listdir(join(dataset_path, scenario))
        data_ = {
            scenario: {}
        }
        for subtype in subtypes:
            data_[scenario][subtype] = {}
            train_tests = listdir(join(dataset_path, scenario, subtype))
            for train_test in train_tests:
                data_[scenario][subtype][train_test] = {}
                trials = listdir(join(dataset_path, scenario, subtype, train_test))
                for trial in trials:
                    if "Set" in trial:
                        new_name = trial.replace("Set", "Trial")
                        os.rename(join(dataset_path, scenario, subtype, train_test, trial),
                                  join(dataset_path, scenario, subtype, train_test, new_name))
                        trial = new_name

                    sub_dirs = listdir(join(dataset_path, scenario, subtype, train_test, trial))
                    # Rename wrong keys in pickle
                    for k in data[scenario][subtype][train_test].keys():
                        data_[scenario][subtype][train_test][k.replace("Set", "Trial")] = data[scenario][subtype][train_test][k]
                    for sub_dir in sub_dirs:
                        if sub_dir == "version.txt":
                            version = data_[scenario][subtype][train_test][trial]["version"]
                            with open(join(dataset_path, scenario, subtype, train_test, trial, sub_dir), "w") as fp:
                                fp.write(version)
                        if sub_dir == "version.tx":
                            os.remove(join(dataset_path, scenario, subtype, train_test, trial, "version.tx"))

        with open(join("final_dataset_corrected", f"{scenario}.pickle"), "wb") as fp:
            pickle.dump(data, fp)


def create_final_dataset():
    if os.path.isdir("/media/data/final_dataset"):
        dataset_path = "/media/data/final_dataset"
        # makedirs(join("media", "data", "final_dataset"), exist_ok=True)
        # process_scene_1(v1_base_path="/media/data/AGENT/human_exp_v1/scene_1_human_exp_v1",
        #                 v2_base_path="/media/data/AGENT/human_exp_v2/scene_1_human_exp_v2",
        #                 target_base_path=os.path.join("/", "media", "data"),
        #                 test_only=True)
        # process_scene_2(v1_base_path="/media/data/AGENT/human_exp_v1/scene_2_human_exp_v1",
        #                 v2_base_path="/media/data/AGENT/human_exp_v2/scene_2_human_exp_v2",
        #                 target_base_path=os.path.join("/", "media", "data"),
        #                 test_only=True)
        # process_scene_3(v1_base_path="/media/data/AGENT/human_exp_v1/scene_3_human_exp_v1",
        #                 v2_base_path="/media/data/AGENT/human_exp_v2/scene_3_human_exp_v2",
        #                 target_base_path=os.path.join("/", "media", "data"),
        #                 test_only=True)
        # process_scene_4(v1_base_path="/media/data/AGENT/human_exp_v1/scene_4_human_exp_v1",
        #                 v2_base_path="/media/data/AGENT/human_exp_v2/scene_4_human_exp_v2",
        #                 target_base_path=os.path.join("/", "media", "data"),
        #                 test_only=True)
    else:
        dataset_path = "/media/data3/final_dataset"
        # makedirs(join("media", "data3", "final_dataset"), exist_ok=True)
        # process_scene_1(v1_base_path = "/media/data2/machinecommonsense/scene_1_train",
        #                 v2_base_path = "/media/data2/machinecommonsense_v2/machinecommonsense/scene_1_v2",
        #                 target_base_path=os.path.join("/", "media", "data3"),
        #                 test_only=False)
        # process_scene_2(v1_base_path = "/media/data2/machinecommonsense/scene_2",
        #                 v2_base_path = "/media/data2/machinecommonsense_v2/machinecommonsense/scene_2_v2",
        #                 target_base_path=os.path.join("/", "media", "data3"),
        #                 test_only=False)
        # process_scene_3(v1_base_path = "/media/data2/machinecommonsense/scene_3",
        #                 v2_base_path = "/media/data2/machinecommonsense_v2/machinecommonsense/scene_3_v2",
        #                 target_base_path=os.path.join("/", "media", "data3"),
        #                 test_only=False)
        # process_scene_4(v1_base_path = "/media/data2/machinecommonsense/scene_4",
        #                 v2_base_path = "/media/data2/machinecommonsense_v2/machinecommonsense/scene_4_v2",
        #                 target_base_path=os.path.join("/", "media", "data3"),
        #                 test_only=False)



    # rename_version_files(dataset_path)
    correct_version(dataset_path)
    # process_state_data(dataset_path)


def validate():
    # f_name = "final_dataset/scenario_1_goal_preferences.pickle"
    f_name = "/Users/Abhi.B@ibm.com/rotation_projects/extra_projects/cora-derenderer/proccessed_data_new/output.pickle"
    with open(f_name, "rb") as fp:
        data = pickle.load(fp)
    scene_key = "scenario_1_goal_preferences"
    for scene_sub_types in data[scene_key].keys():
        for set_types in data[scene_key][scene_sub_types].keys():
            for set_no in data[scene_key][scene_sub_types][set_types].keys():
                sub_dirs = data[scene_key][scene_sub_types][set_types][set_no].keys()
                fam_data = [e for e in sub_dirs if "fam" in e.lower()]
                fam_data = [data[scene_key][scene_sub_types][set_types][set_no][e] for e in fam_data]
                expected = data[scene_key][scene_sub_types][set_types][set_no]["expected"]
                check_target(fam_data, expected, scene_key)


def validate_versioning():
    f_name = "final_dataset"
    scene_name = ["scenario_1_goal_preferences.pickle", "scenario_2_action_efficiency.pickle",
                  "scenario_3_unobserved_constraints.pickle", "scenario_4_cost_reward_trade_offs.pickle"]
    selected_scene = scene_name[2]
    with open(join(f_name, selected_scene), "rb") as fp:
        data = pickle.load(fp)
    scene_key = selected_scene.replace(".pickle", "")
    for scene_sub_types in data[scene_key].keys():
        for set_types in data[scene_key][scene_sub_types].keys():
            for set_no in data[scene_key][scene_sub_types][set_types].keys():
                sub_dirs = data[scene_key][scene_sub_types][set_types][set_no].keys()
                print(sub_dirs)


def do_random_sample():
    if os.path.isdir("/media/data/final_dataset"):
        dataset_path = "/media/data/final_dataset"
    else:
        dataset_path = "/media/data3/final_dataset"
    dataset_path = join(dataset_path, "scenario_4_cost_reward_trade_offs")
    new_path = join("random_dataset", "scenario_4_cost_reward_trade_offs")
    for scene_sub_types in os.listdir(dataset_path):
        for set_types in os.listdir(os.path.join(dataset_path, scene_sub_types)):
            sets = os.listdir(os.path.join(dataset_path, scene_sub_types, set_types))
            random.shuffle(sets)
            sets = sets[0:10]
            for e in sets:
                sub_dirs = os.listdir(os.path.join(dataset_path, scene_sub_types, set_types, e))
                for sub_dir in sub_dirs:
                    if sub_dir in ["version_2", "version_1"]:
                        continue
                    # Copy
                    os.makedirs(join(new_path, scene_sub_types, set_types, e, sub_dir), exist_ok=True)
                    copyfile(join(dataset_path, scene_sub_types, set_types, e, sub_dir, "scene_c.mp4"),
                             join(new_path, scene_sub_types, set_types, e, sub_dir, "scene_c.mp4"))

    shutil.make_archive(f"random_dataset.zip", 'zip', new_path)
    print(f"zip created at random_dataset.zip")


def check_target(fam_data, expected, scene_key):
    if scene_key == "scenario_1_goal_preferences":
        assert len(fam_data) == 1
        fam_data = fam_data[0]
        agent_pos = fam_data[-1]["agent"]["center"]
        fam_target = 1 if agent_pos[0] > 0 else 2
        if fam_target == 1:
            fam_goal = fam_data[-1]["goal_1"]["object_label"] if fam_data[-1]["goal_1"]["center"][0] > 0 \
                else fam_data[-1]["goal_2"]["object_label"]
        else:
            fam_goal = fam_data[-1]["goal_2"]["object_label"] if fam_data[-1]["goal_1"]["center"][0] > 0 \
                else fam_data[-1]["goal_1"]["object_label"]
        agent_pos = expected[-1]["agent"]["center"]
        test_target = 1 if agent_pos[0] > 0 else 2
        if test_target == 1:
            expected_goal = expected[-1]["goal_1"]["object_label"] if expected[-1]["goal_1"]["center"][0] > 0 \
                else expected[-1]["goal_2"]["object_label"]
        else:
            expected_goal = expected[-1]["goal_2"]["object_label"] if expected[-1]["goal_1"]["center"][0] > 0 \
                else expected[-1]["goal_1"]["object_label"]
        assert fam_goal == expected_goal
    else:
        assert len(fam_data) == 4


if __name__ == '__main__':
    create_final_dataset()
    # validate()
    # do_random_sample()
    # validate_versioning()