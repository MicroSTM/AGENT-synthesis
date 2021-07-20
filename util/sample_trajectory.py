import random

def get_scene_4_fam_wall(valid_fam_configs, selected_target):
    pos_x = 2 if selected_target == "1" else 0
    easy_fam = valid_fam_configs[
        (valid_fam_configs["obstacle_height"].isin([1, 2])) &
        (valid_fam_configs["obstacle_width"].isin([0])) &
        (valid_fam_configs["obstacle_pos_z"] == valid_fam_configs["obj_pos_z"]) &
        (valid_fam_configs["obstacle_pos_z"] == valid_fam_configs["agent_z"]) &
        (valid_fam_configs["obj_pos_x"] == pos_x) &
        (valid_fam_configs["cost"] < 9) &
        (valid_fam_configs["path_type"].isin(["Jump"]))
        ]

    easy_fam = easy_fam.iloc[random.choice(range(easy_fam.shape[0]))]

    med_fam_1 = valid_fam_configs[
        (valid_fam_configs["obj_pos_x"] == pos_x) &
        (valid_fam_configs["obj_pos_z"] == easy_fam["obj_pos_z"]) &
        (valid_fam_configs["agent_z"] == easy_fam["agent_z"])
        ]
    med_heights = [easy_fam["obstacle_height"] + 2]
    if easy_fam["obstacle_height"] + 3 < 5:
        med_heights.append(easy_fam["obstacle_height"] + 3)
    med_fam_1 = med_fam_1[
        (med_fam_1["obstacle_height"].isin(med_heights)) &
        (med_fam_1["obstacle_width"].isin([0])) &
        (med_fam_1["cost"] > easy_fam["cost"]) &
        (med_fam_1["path_type"].isin(["Jump"]))
        ]
    med_fam_1 = med_fam_1.iloc[random.choice(range(med_fam_1.shape[0]))]

    med_fam_2 = valid_fam_configs[
        (valid_fam_configs["agent_x"] == pos_x) &
        (valid_fam_configs["obj_pos_z"] == easy_fam["obj_pos_z"]) &
        (valid_fam_configs["agent_z"] == easy_fam["agent_z"])
        ]
    med_heights = [easy_fam["obstacle_height"] + 2]
    if easy_fam["obstacle_height"] + 3 < 5:
        med_heights.append(easy_fam["obstacle_height"] + 3)
    med_fam_2 = med_fam_2[
        (med_fam_2["obstacle_height"].isin(med_heights)) &
        (med_fam_2["obstacle_width"].isin([0])) &
        (med_fam_2["cost"] > easy_fam["cost"]) &
        (med_fam_2["path_type"].isin(["Jump"]))
        ]
    med_fam_2 = med_fam_2.iloc[random.choice(range(med_fam_2.shape[0]))]

    hard_heights = [med_fam_2["obstacle_height"] + 2]
    if med_fam_2["obstacle_height"] + 3 < 7:
        hard_heights.append(med_fam_2["obstacle_height"] + 3)
    hard_fam = valid_fam_configs[
        (valid_fam_configs["obj_pos_z"] == easy_fam["obj_pos_z"]) &
        (valid_fam_configs["agent_x"] == pos_x) &
        (valid_fam_configs["agent_z"] == easy_fam["agent_z"])
        ]
    hard_fam = hard_fam.iloc[random.choice(range(hard_fam.shape[0]))]
    return hard_fam, med_fam_2, med_fam_1, easy_fam


def get_scene_4_cost_reward_trade_offs_test_v1(test_type, valid_test_configs, selected_target, not_selected, switch_test_targets,
                                               target_1_pos_to_target_2_pos):
    valid_test_configs = valid_test_configs[valid_test_configs["scene_type"].isin(["barrier_scenes_3_4",
                                                                                   "barrier_scenes"])]
    
    if switch_test_targets:
        selected_target, not_selected = not_selected, selected_target
    if test_type == "Type-4.1":
        test_a_valid_configs = valid_test_configs[
            (valid_test_configs["target"] == f"Target-{selected_target}") &
            (valid_test_configs[f"obstacle_height_{selected_target}"] == 0) &
            (valid_test_configs[f"target-{selected_target}-distance"] > 1)
            ]

        test_a = test_a_valid_configs.iloc[random.choice(range(test_a_valid_configs.shape[0]))]
        test_b = valid_test_configs[
            (valid_test_configs["target"] == f"Target-{not_selected}") &
            (valid_test_configs[f"obj_{not_selected}_pos_z"] == test_a[f"obj_{selected_target}_pos_z"]) &
            (valid_test_configs[f"obj_{not_selected}_pos_x"] ==
             target_1_pos_to_target_2_pos[f"target_{selected_target}"][test_a[f"obj_{selected_target}_pos_x"]]) &
            (valid_test_configs[f"obstacle_height_{not_selected}"] == 0) &
            (valid_test_configs["agent_pos_z"] == test_a["agent_pos_z"]) &
            (valid_test_configs["path_type"].isin(["Straight-Target"]))
            ].iloc[0]
        return [test_a, test_b]
    if test_type == "Type-4.2":
        pos_x = 0 if not_selected == "2" else 6
        test_b_valid_configs = valid_test_configs[
            (valid_test_configs["target"] == f"Target-{not_selected}") &
            (valid_test_configs[f"obstacle_height_{not_selected}"].isin([5, 6])) &
            (valid_test_configs[f"obstacle_width_{not_selected}"].isin([0, 1])) &
            (valid_test_configs[f"obstacle_depth_{not_selected}"].isin([3, 4])) &
            (valid_test_configs["path_type"].isin(['Around-barrier-bottom']))
            ]
        test_b = test_b_valid_configs.iloc[random.choice(range(test_b_valid_configs.shape[0]))]

        test_a = valid_test_configs[
            (valid_test_configs["target"] == f"Target-{selected_target}") &
            (valid_test_configs[f"obj_{selected_target}_pos_x"] == pos_x) &
            (valid_test_configs[f"obj_{selected_target}_pos_z"] == test_b[f"obj_{not_selected}_pos_z"]) &
            (valid_test_configs[f"obstacle_height_{selected_target}"].isin([0])) &
            (valid_test_configs["agent_pos_z"] == test_b["agent_pos_z"]) &
            (valid_test_configs["cost"] < test_b["cost"])
            ].iloc[0]
        return [test_a, test_b]


def get_scene_4_cost_reward_trade_offs_test_v2(test_type, valid_test_configs, selected_target, not_selected, switch_test_target,
                                               target_1_pos_to_target_2_pos, object_type_test):
    if switch_test_target:
        selected_target, not_selected = not_selected, selected_target
    pos_x = 0 if selected_target == "1" else 6
    if test_type == "Type-4.1":
        if object_type_test[0] == "pit-with-bridge" or object_type_test[1] == "pit-with-bridge":
            if object_type_test[0] == "pit-with-bridge":
                test_a = valid_test_configs[
                    (valid_test_configs["target"] == f"Target-{selected_target}") &
                    (valid_test_configs["scene_type"] == "pit_scenes_3_4") &
                    (valid_test_configs[f"obj_{selected_target}_pos_z"].isin([1, 2])) &
                    (valid_test_configs[f"obj_{selected_target}_pos_z"] == valid_test_configs["agent_pos_z"]) &
                    (valid_test_configs[f"obstacle_{selected_target}_pos_z"] == valid_test_configs["agent_pos_z"]) &
                    (valid_test_configs["path_type"] == "Cross-Bridge")
                ]
                test_a = test_a.iloc[random.choice(range(test_a.shape[0]))]
            else:
                test_a = valid_test_configs[
                    (valid_test_configs["target"] == f"Target-{selected_target}") &
                    (valid_test_configs["scene_type"] == "pit_scenes_3_4") &
                    (valid_test_configs["path_type"] == "Straight-Target")
                    ]
                test_a = test_a.iloc[random.choice(range(test_a.shape[0]))]
            if object_type_test[1] == "pit-with-bridge":
                test_b = valid_test_configs[
                    (valid_test_configs["target"] == f"Target-{not_selected}") &
                    (valid_test_configs["scene_type"] == "pit_scenes_3_4") &
                    (valid_test_configs["path_type"] == "Cross-Bridge")
                ]
                if object_type_test[0] == "pit-with-bridge":
                    test_b = test_b[
                        (test_b[f"obstacle_{not_selected}_pos_z"] == test_a[f"obstacle_{selected_target}_pos_z"] ) &
                        (test_b[f"obstacle_width_{not_selected}"] == test_a[f"obstacle_width_{selected_target}"] ) &
                        (test_b["agent_pos_z"] == test_a["agent_pos_z"]) &
                        (test_b[f"obj_{not_selected}_pos_z"] == test_a[f"obj_{selected_target}_pos_z"])
                    ]
                test_b = test_b.iloc[random.choice(range(test_b.shape[0]))]
            else:
                test_b = valid_test_configs[
                    (valid_test_configs["target"] == f"Target-{not_selected}") &
                    (valid_test_configs["scene_type"] == "pit_scenes_3_4") &
                    (valid_test_configs["path_type"] == "Straight-Target") &
                    (valid_test_configs["agent_pos_z"] == test_a["agent_pos_z"]) &
                    (valid_test_configs[f"obj_{not_selected}_pos_z"] == test_a[f"obj_{selected_target}_pos_z"])
                    ]
                test_b = test_b.iloc[random.choice(range(test_b.shape[0]))]
            return [test_a, test_b]
        elif object_type_test[0] == "barrier_with_door" or object_type_test[1] == "barrier_with_door":
            if object_type_test[0] == "barrier_with_door":
                test_a = valid_test_configs[
                    (valid_test_configs["target"] == f"Target-{selected_target}") &
                    (valid_test_configs["path_type"] == "barrier-door") &
                    (valid_test_configs[f"obstacle_{selected_target}_pos_z"] == 1) &
                    (valid_test_configs[f"obj_{selected_target}_pos_z"] == 1) &
                    (valid_test_configs[f"agent_pos_z"] == 1) &
                    (valid_test_configs[f"obstacle_height_{selected_target}"].isin([5, 6]))
                    ]
                test_a = test_a.iloc[random.choice(range(test_a.shape[0]))]

            else:
                test_a = valid_test_configs[
                    (valid_test_configs["target"] == f"Target-{selected_target}") &
                    (valid_test_configs["path_type"] == "Straight-Target") &
                    (valid_test_configs[f"obstacle_height_{selected_target}"].isin([0])) &
                    (valid_test_configs[f"obj_{selected_target}_pos_x"] == pos_x)
                    ]
                test_a = test_a.iloc[random.choice(range(test_a.shape[0]))]
            if object_type_test[1] == "barrier_with_door":
                test_b = valid_test_configs[
                    (valid_test_configs["target"] == f"Target-{not_selected}") &
                    (valid_test_configs["path_type"] == "barrier-door") &
                    (valid_test_configs[f"obstacle_{not_selected}_pos_z"] == 1) &
                    (valid_test_configs[f"obstacle_height_{not_selected}"].isin([5, 6])) &
                    (valid_test_configs[f"agent_pos_z"] == 1) &
                    (valid_test_configs[f"obj_{not_selected}_pos_z"] == 1)
                    ]
                test_b = test_b.iloc[random.choice(range(test_b.shape[0]))]
            else:
                pos_x_b = 6 if selected_target == "1" else 0
                test_b = valid_test_configs[
                    (valid_test_configs["target"] == f"Target-{not_selected}") &
                    (valid_test_configs["path_type"] == "Straight-Target") &
                    (valid_test_configs[f"obstacle_height_{not_selected}"].isin([0])) &
                    (valid_test_configs[f"obj_{not_selected}_pos_z"] == test_a[f"obj_{selected_target}_pos_z"]) &
                    (valid_test_configs[f"agent_pos_z"] == test_a[f"agent_pos_z"]) &
                    (valid_test_configs[f"obj_{not_selected}_pos_x"] == pos_x_b)
                    ]
                test_b = test_b.iloc[random.choice(range(test_b.shape[0]))]
            return [test_a, test_b]
    if test_type == "Type-4.2":
        if object_type_test[1] == "platform":
            test_b = valid_test_configs[
                (valid_test_configs["path_type"] == "Platform-jump") &
                (valid_test_configs["agent_pos_z"] == 1) &
                (valid_test_configs["target"] == f"Target-{not_selected}")
            ]
            test_b = test_b.iloc[random.choice(range(test_b.shape[0]))]
        elif object_type_test[1] == "ramp":
            test_b = valid_test_configs[
                (valid_test_configs["path_type"] == "Go-up-ramp") &
                (valid_test_configs["agent_pos_z"] == 1) &
                (valid_test_configs["target"] == f"Target-{not_selected}")
                ]
            test_b = test_b.iloc[random.choice(range(test_b.shape[0]))]
        # elif object_type_test[1] == "pit":
        else:
            test_b = valid_test_configs[
                (valid_test_configs["path_type"] == "Pit_Jump") &
                (valid_test_configs["target"] == f"Target-{not_selected}")
                ]

            if object_type_test[0] == "pit-with-bridge":
                test_b = test_b[
                    (test_b["agent_pos_z"] == test_b[f"obj_{not_selected}_pos_z"]) &
                    (test_b["agent_pos_z"] == test_b[f"obstacle_{not_selected}_pos_z"])
                ]
            test_b = test_b.iloc[random.choice(range(test_b.shape[0]))]
        if object_type_test[1] in ["pit", "pit-with-bridge"] and object_type_test[0] == "pit-with-bridge":
            test_a = valid_test_configs[
                (valid_test_configs["target"] == f"Target-{selected_target}") &
                (valid_test_configs["path_type"] == "Cross-Bridge") &
                (valid_test_configs["agent_pos_z"] == test_b["agent_pos_z"]) &
                (valid_test_configs[f"obstacle_width_{selected_target}"] == test_b[f"obstacle_width_{not_selected}"]) &
                (valid_test_configs[f"obj_{selected_target}_pos_z"] == test_b[f"obj_{not_selected}_pos_z"]) &
                (valid_test_configs[f"obstacle_{selected_target}_pos_z"] == test_b[f"obj_{not_selected}_pos_z"])
                ]
            test_a = test_a.iloc[random.choice(range(test_a.shape[0]))]
        elif object_type_test[1] in ["pit", "pit-with-bridge"] and object_type_test[0] == "none":
            test_a = valid_test_configs[
                (valid_test_configs["target"] == f"Target-{selected_target}") &
                (valid_test_configs["scene_type"] == "pit_scenes_3_4") &
                (valid_test_configs["path_type"] == "Straight-Target") &
                (valid_test_configs["agent_pos_z"] == test_b["agent_pos_z"]) &
                (valid_test_configs[f"obj_{selected_target}_pos_z"] == test_b[f"obj_{not_selected}_pos_z"])
                ]
            test_a = test_a.iloc[random.choice(range(test_a.shape[0]))]
        elif object_type_test[0] == "none":
            pox = 0 if selected_target == "1" else 6
            test_a = valid_test_configs[
                (valid_test_configs["target"] == f"Target-{selected_target}") &
                (valid_test_configs["scene_type"] == "barrier_scenes_3_4") &
                (valid_test_configs["path_type"] == "Straight-Target") &
                (valid_test_configs["agent_pos_z"] == 1) &
                # 1 Because both ramp and platform have fixed z values which is 1
                (valid_test_configs[f"obj_{selected_target}_pos_z"] == 1) &
                (valid_test_configs[f"obj_{selected_target}_pos_x"] == pox)
                ]
            test_a = test_a.iloc[random.choice(range(test_a.shape[0]))]
        elif object_type_test[0] == "barrier_with_door":
            test_a = valid_test_configs[
                (valid_test_configs["target"] == f"Target-{selected_target}") &
                (valid_test_configs["path_type"] == "barrier-door") &
                (valid_test_configs[f"obstacle_height_{selected_target}"].isin([5, 6])) &
                (valid_test_configs["agent_pos_z"] == 1) &
                (valid_test_configs[f"obstacle_{selected_target}_pos_z"] == 1) &
                (valid_test_configs[f"obj_{selected_target}_pos_z"] == 1)
                ]
            test_a = test_a.iloc[random.choice(range(test_a.shape[0]))]
        return [test_a, test_b]


def get_scene_4_fam_pit(valid_fam_configs, selected_target):
    pos_x = 2 if selected_target == "1" else 0
    easy_fam = valid_fam_configs[
        (valid_fam_configs["scene_type"] == "pit_scenes") &
        (valid_fam_configs["obj_pos_x"] == pos_x) &
        ( (valid_fam_configs["path_type"] == "Straight-Target") |
          ( (valid_fam_configs["obstacle_width"] == 0) & (valid_fam_configs["path_type"] == "Pit_Jump")) )
        ]

    easy_fam = easy_fam.iloc[random.choice(range(easy_fam.shape[0]))]

    med_fam_1 = valid_fam_configs[
        (valid_fam_configs["obj_pos_x"] == pos_x) &
        (valid_fam_configs["obj_pos_z"] == easy_fam["obj_pos_z"]) &
        (valid_fam_configs["agent_z"] == easy_fam["agent_z"]) &
        (valid_fam_configs["scene_type"] == "pit_scenes") &
        (valid_fam_configs["obstacle_width"] == 2) &
        (valid_fam_configs["path_type"] == "Pit_Jump")
        ]
    med_fam_1 = med_fam_1.iloc[random.choice(range(med_fam_1.shape[0]))]

    med_fam_2 = valid_fam_configs[
        (valid_fam_configs["agent_x"] == pos_x) &
        (valid_fam_configs["obj_pos_z"] == easy_fam["obj_pos_z"]) &
        (valid_fam_configs["agent_z"] == easy_fam["agent_z"]) &
        (valid_fam_configs["scene_type"] == "pit_scenes") &
        (valid_fam_configs["obstacle_width"] == 2) &
        (valid_fam_configs["path_type"] == "Pit_Jump")
        ]
    med_fam_2 = med_fam_2.iloc[random.choice(range(med_fam_2.shape[0]))]

    hard_fam = valid_fam_configs[
        (valid_fam_configs["obj_pos_z"] == easy_fam["obj_pos_z"]) &
        (valid_fam_configs["agent_x"] == pos_x) &
        (valid_fam_configs["agent_z"] == easy_fam["agent_z"]) &
        (valid_fam_configs["scene_type"] == "pit_scenes") &
        (valid_fam_configs["obstacle_width"] > 3) &
        (valid_fam_configs["path_type"] == "Pit_Jump")
        ]

    hard_fam = hard_fam.iloc[random.choice(range(hard_fam.shape[0]))]

    return hard_fam, med_fam_2, med_fam_1, easy_fam

def get_scene_4_fam_platform(valid_fam_configs, selected_target):
    pos_x = 2 if selected_target == "1" else 0
    easy_fam = valid_fam_configs[
        (valid_fam_configs["obj_pos_x"] == pos_x) &
         ((valid_fam_configs["scene_type"] == "platform_scenes") &
          (valid_fam_configs["obstacle_height"] == 0) &
          (valid_fam_configs["path_type"] == "Platform-jump"))
        ]
    easy_fam = easy_fam.iloc[random.choice(range(easy_fam.shape[0]))]
    med_fam_1 = valid_fam_configs[
        (valid_fam_configs["obj_pos_x"] == pos_x) &
        (valid_fam_configs["agent_z"] == easy_fam["agent_z"]) &
        (valid_fam_configs["scene_type"] == "platform_scenes") &
        (valid_fam_configs["obstacle_height"] == 1) &
        (valid_fam_configs["path_type"] == "Platform-jump")
        ]
    med_fam_1 = med_fam_1.iloc[random.choice(range(med_fam_1.shape[0]))]

    med_fam_2 = valid_fam_configs[
        (valid_fam_configs["agent_x"] == pos_x) &
        (valid_fam_configs["agent_z"] == easy_fam["agent_z"]) &
        (valid_fam_configs["scene_type"] == "platform_scenes") &
        (valid_fam_configs["obstacle_height"] == 1) &
        (valid_fam_configs["path_type"] == "Platform-jump")
        ]

    med_fam_2 = med_fam_2.iloc[random.choice(range(med_fam_2.shape[0]))]

    hard_fam = valid_fam_configs[
        (valid_fam_configs["agent_x"] == pos_x) &
        (valid_fam_configs["agent_z"] == easy_fam["agent_z"]) &
        (valid_fam_configs["scene_type"] == "platform_scenes") &
        (valid_fam_configs["obstacle_height"] > 1) &
        (valid_fam_configs["path_type"] == "Platform-jump")
        ]

    hard_fam = hard_fam.iloc[random.choice(range(hard_fam.shape[0]))]
    return hard_fam, med_fam_2, med_fam_1, easy_fam


def get_scene_4_fam_ramp(valid_fam_configs, selected_target):
    pos_x = 2 if selected_target == "1" else 0
    ramp_pos_x = 1 if selected_target == "1" else 0
    easy_fam = valid_fam_configs[
        (valid_fam_configs["obj_pos_x"] == ramp_pos_x) &
         ((valid_fam_configs["scene_type"] == "ramp_scenes") &
          (valid_fam_configs["obstacle_height"] == 0) &
          (valid_fam_configs["path_type"] == "Go-up-ramp"))
        ]
    easy_fam = easy_fam.iloc[random.choice(range(easy_fam.shape[0]))]
    med_fam_1 = valid_fam_configs[
        (valid_fam_configs["obj_pos_x"] == ramp_pos_x) &
        (valid_fam_configs["agent_z"] == easy_fam["agent_z"]) &
        (valid_fam_configs["scene_type"] == "ramp_scenes") &
        (valid_fam_configs["obstacle_height"] == 1) &
        (valid_fam_configs["path_type"] == "Go-up-ramp")
        ]

    med_fam_1 = med_fam_1.iloc[random.choice(range(med_fam_1.shape[0]))]

    med_fam_2 = valid_fam_configs[
        (valid_fam_configs["agent_x"] == pos_x) &
        (valid_fam_configs["agent_z"] == easy_fam["agent_z"]) &
        (valid_fam_configs["scene_type"] == "ramp_scenes") &
        (valid_fam_configs["obstacle_height"] == 1) &
        (valid_fam_configs["path_type"] == "Go-up-ramp")
        ]

    med_fam_2 = med_fam_2.iloc[random.choice(range(med_fam_2.shape[0]))]

    hard_fam = valid_fam_configs[
        (valid_fam_configs["agent_x"] == pos_x) &
        (valid_fam_configs["agent_z"] == easy_fam["agent_z"]) &
        (valid_fam_configs["scene_type"] == "ramp_scenes") &
        (valid_fam_configs["obstacle_height"] > 1) &
        (valid_fam_configs["path_type"] == "Go-up-ramp")
        ]

    hard_fam = hard_fam.iloc[random.choice(range(hard_fam.shape[0]))]
    return hard_fam, med_fam_2, med_fam_1, easy_fam



def get_scene_3_test_(test_type, valid_test_configs, selected_target, target_1_pos_to_target_2_pos,
                      object_type_test):
    pos_x = 0 if selected_target == "1" else 6
    not_selected = 1 if selected_target == 2 else 2
    if test_type in ["Type-1.1", ""]:
        if object_type_test[0] == "pit-with-bridge" or object_type_test[1] == "pit-with-bridge":
            if object_type_test[0] == "pit-with-bridge":
                test_a = valid_test_configs[
                    (valid_test_configs["target"] == f"Target-{selected_target}") &
                    (valid_test_configs["scene_type"] == "pit_scenes_3_4") &
                    (valid_test_configs["path_type"] == "Cross-Bridge")
                ]
                test_a = test_a.iloc[random.choice(range(test_a.shape[0]))]
            else:
                test_a = valid_test_configs[
                    (valid_test_configs["target"] == f"Target-{selected_target}") &
                    (valid_test_configs["scene_type"] == "pit_scenes_3_4") &
                    (valid_test_configs["path_type"] == "Straight-Target")
                    ]
                test_a = test_a.iloc[random.choice(range(test_a.shape[0]))]
            if object_type_test[1] == "pit-with-bridge":
                test_b = valid_test_configs[
                    (valid_test_configs["target"] == f"Target-{not_selected}") &
                    (valid_test_configs["scene_type"] == "pit_scenes_3_4") &
                    (valid_test_configs["path_type"] == "Cross-Bridge") &
                    (valid_test_configs[f"obj_{not_selected}_pos_z"] == test_a[f"obj_{selected_target}_pos_z"])
                ]
                if object_type_test[0] == "pit-with-bridge":
                    test_b = test_b[
                        test_b[f"obstacle_{not_selected}_pos_z"] == test_a[f"obstacle_{selected_target}_pos_z"]
                    ]
                test_b = test_b.iloc[random.choice(range(test_b.shape[0]))]
            else:
                test_b = valid_test_configs[
                    (valid_test_configs["target"] == f"Target-{not_selected}") &
                    (valid_test_configs["scene_type"] == "pit_scenes_3_4") &
                    (valid_test_configs["path_type"] == "Straight-Target") &
                    (valid_test_configs[f"obj_{not_selected}_pos_z"] == test_a[f"obj_{selected_target}_pos_z"])
                    ]
                test_b = test_b.iloc[random.choice(range(test_b.shape[0]))]
            return [test_a, test_b]
        elif object_type_test[0] == "barrier_with_door" or object_type_test[1] == "barrier_with_door":
            if object_type_test[0] == "barrier_with_door":
                test_a = valid_test_configs[
                    (valid_test_configs["target"] == f"Target-{selected_target}") &
                    (valid_test_configs["path_type"] == "barrier-door") &
                    (valid_test_configs[f"obstacle_{selected_target}_pos_z"] == valid_test_configs["agent_pos_z"]) &
                    (valid_test_configs[f"obstacle_height_{selected_target}"].isin([5, 6]))
                    ]
                test_a = test_a.iloc[random.choice(range(test_a.shape[0]))]
            else:
                test_a = valid_test_configs[
                    (valid_test_configs["target"] == f"Target-{selected_target}") &
                    (valid_test_configs["path_type"] == "Straight-Target") &
                    (valid_test_configs[f"obstacle_height_{selected_target}"].isin([0])) &
                    (valid_test_configs[f"obj_{selected_target}_pos_x"] == pos_x)
                    ]
                test_a = test_a.iloc[random.choice(range(test_a.shape[0]))]
            if object_type_test[1] == "barrier_with_door":
                test_b = valid_test_configs[
                    (valid_test_configs["target"] == f"Target-{not_selected}") &
                    (valid_test_configs["path_type"] == "barrier-door") &
                    (valid_test_configs[f"obstacle_{not_selected}_pos_z"] == valid_test_configs["agent_pos_z"]) &
                    (valid_test_configs[f"obstacle_height_{not_selected}"].isin([5, 6])) &
                    (valid_test_configs[f"obj_{not_selected}_pos_z"] == test_a[f"obj_{selected_target}_pos_z"])
                    ]
                test_b = test_b.iloc[random.choice(range(test_b.shape[0]))]
            else:
                test_b = valid_test_configs[
                    (valid_test_configs["target"] == f"Target-{not_selected}") &
                    (valid_test_configs["path_type"] == "Straight-Target") &
                    (valid_test_configs[f"obstacle_height_{not_selected}"].isin([0])) &
                    (valid_test_configs[f"obj_{not_selected}_pos_z"] == test_a[f"obj_{selected_target}_pos_z"]) &
                    (valid_test_configs[f"obj_{not_selected}_pos_x"] ==
                     target_1_pos_to_target_2_pos[f"target_{selected_target}"][test_a[f"obj_{selected_target}_pos_x"]])
                    ]
                test_b = test_b.iloc[random.choice(range(test_b.shape[0]))]
            return [test_a, test_b]
    if test_type == "Type-2":
        if object_type_test[1] == "platform":
            test_b = valid_test_configs[
                (valid_test_configs["path_type"] == "Platform-jump") &
                (valid_test_configs["target"] == f"Target-{not_selected}")
            ]
            test_b = test_b.iloc[random.choice(range(test_b.shape[0]))]
        elif object_type_test[1] == "ramp":
            test_b = valid_test_configs[
                (valid_test_configs["path_type"] == "Go-up-ramp") &
                (valid_test_configs["target"] == f"Target-{not_selected}")
                ]
            test_b = test_b.iloc[random.choice(range(test_b.shape[0]))]
        # elif object_type_test[1] == "pit":
        else:
            test_b = valid_test_configs[
                (valid_test_configs["path_type"] == "Pit_Jump") &
                (valid_test_configs["target"] == f"Target-{not_selected}")
                ]
            if object_type_test[0] == "pit-with-bridge":
                test_b = test_b[
                    (test_b["agent_pos_z"] == test_b[f"obj_{not_selected}_pos_z"])
                ]
            test_b = test_b.iloc[random.choice(range(test_b.shape[0]))]
        if object_type_test[1] in ["pit", "pit-with-bridge"] and object_type_test[0] == "pit-with-bridge":
            test_a = valid_test_configs[
                (valid_test_configs["target"] == f"Target-{selected_target}") &
                (valid_test_configs["path_type"] == "Cross-Bridge") &
                (valid_test_configs["agent_pos_z"] == test_b["agent_pos_z"]) &
                (valid_test_configs[f"obj_{selected_target}_pos_z"] == test_b[f"obj_{not_selected}_pos_z"]) &
                (valid_test_configs[f"obstacle_{selected_target}_pos_z"] == test_b[f"obj_{not_selected}_pos_z"])
                ]
            test_a = test_a.iloc[random.choice(range(test_a.shape[0]))]
        elif object_type_test[1] in ["pit", "pit-with-bridge"] and object_type_test[0] == "none":
            test_a = valid_test_configs[
                (valid_test_configs["target"] == f"Target-{selected_target}") &
                (valid_test_configs["scene_type"] == "pit_scenes_3_4") &
                (valid_test_configs["path_type"] == "Straight-Target") &
                (valid_test_configs[f"obj_{selected_target}_pos_z"] == test_b[f"obj_{not_selected}_pos_z"])
                ]
            test_a = test_a.iloc[random.choice(range(test_a.shape[0]))]
        elif object_type_test[0] == "none":
            pox = 0 if selected_target == "1" else 6
            test_a = valid_test_configs[
                (valid_test_configs["target"] == f"Target-{selected_target}") &
                (valid_test_configs["scene_type"] == "barrier_scenes_3_4") &
                (valid_test_configs["path_type"] == "Straight-Target") &
                # 1 Because both ramp and platform have fixed z values which is 1
                (valid_test_configs[f"obj_{selected_target}_pos_z"] == 1) &
                (valid_test_configs[f"obj_{selected_target}_pos_x"] == pox)
                ]
            test_a = test_a.iloc[random.choice(range(test_a.shape[0]))]
        elif object_type_test[0] == "barrier_with_door":
            test_a = valid_test_configs[
                (valid_test_configs["target"] == f"Target-{selected_target}") &
                (valid_test_configs["path_type"] == "barrier-door") &
                (valid_test_configs[f"obstacle_height_{selected_target}"].isin([5, 6])) &
                (valid_test_configs["agent_pos_z"] == test_b["agent_pos_z"]) &
                (valid_test_configs[f"obstacle_{selected_target}_pos_z"] == test_b ["agent_pos_z"]) &
                (valid_test_configs[f"obj_{selected_target}_pos_z"] == test_b["agent_pos_z"])
                ]
            test_a = test_a.iloc[random.choice(range(test_a.shape[0]))]
        return [test_a, test_b]


def scene_1_goal_preference_v1(scenario_sub_type, selected_target, switch_goals, valid_configs, target_1_pos_to_target_2_pos, history,
                               valid_configs_jumps):
    while True:
        type_ = random.choice(["jump", "go-around"])
        not_selected = "2" if selected_target == "1" else "1"
        if scenario_sub_type in ["Type-1.1", "Type-1.1.0__1.2",  "Type-1.2.0__1.2"]:

            valid_configs_for_subtype = valid_configs[(valid_configs[f"obstacle_height_{selected_target}"] == 0)
            ]
            valid_configs_for_subtype_target = valid_configs_for_subtype[
                (valid_configs_for_subtype["target"] == f"Target-{selected_target}") &
                (valid_configs_for_subtype[f"target-{selected_target}-distance"] > 1.5)
                ]
            fam = valid_configs_for_subtype_target.iloc[
                random.choice(range(valid_configs_for_subtype_target.shape[0]))]
            # Switch the goals positions

            if scenario_sub_type == "Type-1.1":
                target_2_test = valid_configs_for_subtype[
                    (valid_configs_for_subtype[f"obj_{not_selected}_pos_x"] ==
                     target_1_pos_to_target_2_pos[f"target_{selected_target}"][fam[f"obj_{selected_target}_pos_x"]]) &
                    (valid_configs_for_subtype[f"obj_{not_selected}_pos_z"] == fam[f"obj_{selected_target}_pos_z"]) &
                    (valid_configs_for_subtype[f"obstacle_height_{not_selected}"] == 0) &
                    (valid_configs_for_subtype["agent_pos_z"] == fam["agent_pos_z"]) &
                    (valid_configs_for_subtype["target"] == f"Target-{not_selected}")
                    ].iloc[0]
                if switch_goals:
                    return [fam], [target_2_test, fam], history, switch_goals
                else:
                    return [fam], [fam, target_2_test], history, switch_goals
            if switch_goals:
                selected_target, not_selected = not_selected, selected_target

            if scenario_sub_type == "Type-1.1.0__1.2":

                try:
                    valid_configs_for_testing = valid_configs[
                        (valid_configs[f"target-{selected_target}-distance"] < 2) &
                        (valid_configs[f"obstacle_height_{selected_target}"] == 0) &
                        (valid_configs["path_type"] == "Straight-Target") &
                        (valid_configs["agent_pos_z"] == fam["agent_pos_z"])
                        ]
                    test_a = valid_configs_for_testing[
                        (valid_configs_for_testing["target"] == f"Target-{selected_target}")
                    ]

                    test_a = test_a.iloc[random.choice(range(test_a.shape[0]))]
                    test_b = valid_configs[
                        (valid_configs[f"target-{not_selected}-distance"] > 3) &
                        (valid_configs["target"] == f"Target-{not_selected}") &
                        (valid_configs["path_type"] == "Straight-Target") &
                        (valid_configs["agent_pos_z"] == fam["agent_pos_z"])
                        ].iloc[0]
                    return [fam], [test_a, test_b], history, switch_goals
                except:
                    continue


            elif scenario_sub_type == "Type-1.2.0__1.2":
                pos_x = 0 if selected_target == "1" else 6
                valid_configs_for_testing = valid_configs[
                    (valid_configs[f"obstacle_height_{selected_target}"] == 0) &
                    (valid_configs[f"obj_{selected_target}_pos_x"] == pos_x) &
                    (valid_configs["path_type"] == "Straight-Target") &
                    (valid_configs["agent_pos_z"] == fam["agent_pos_z"])
                    ]
                test_a = valid_configs_for_testing[
                    (valid_configs_for_testing["target"] == f"Target-{selected_target}")
                ]
                test_a = test_a.iloc[random.choice(range(test_a.shape[0]))]
                test_b = valid_configs[
                    (valid_configs["target"] == f"Target-{not_selected}") &
                    (valid_configs[f"obstacle_height_{not_selected}"] != 0) &
                    (valid_configs[f"obstacle_depth_{not_selected}"].isin(
                        [3, 4, 5])) &
                    (valid_configs["agent_pos_z"] == fam["agent_pos_z"]) &
                    (valid_configs[f"obj_{not_selected}_pos_z"] == test_a[f"obj_{selected_target}_pos_z"])
                    ].iloc[0]
                return [fam], [test_a, test_b], history, switch_goals

        elif scenario_sub_type in ["Type-1.3", "Type-2.1.0__1.4", "Type-2.2.0__1.4"]:
            if type_ == "jump":
                valid_configs_fam, valid_config_test = valid_configs_jumps, valid_configs
            else:
                valid_configs_fam, valid_config_test = valid_configs, valid_configs_jumps
            valid_configs_for_subtype = valid_configs_fam[
                (valid_configs_fam[f"obstacle_height_{selected_target}"] != 0) &
                (valid_configs_fam[f"obstacle_depth_{selected_target}"].isin([3, 4, 5]))
                ]
            valid_configs_for_subtype_target = valid_configs_for_subtype[
                valid_configs_for_subtype["target"] == f"Target-{selected_target}"]
            fam = valid_configs_for_subtype_target.iloc[random.choice(range(valid_configs_for_subtype_target.shape[0]))]
            if switch_goals:
                selected_target, not_selected = not_selected, selected_target
            if scenario_sub_type == "Type-1.3":
                pos_x = 0 if not_selected == "1" else 6
                valid_configs_for_testing = valid_config_test[
                    (valid_config_test[f"obstacle_height_{selected_target}"] != 0) &
                    (valid_config_test[f"obstacle_depth_{selected_target}"].isin(
                        [3, 4, 5])) &
                    (valid_config_test["agent_pos_z"] == fam["agent_pos_z"])
                    ]
                test_a = valid_configs_for_testing[
                    (valid_configs_for_testing["target"] == f"Target-{selected_target}")
                ]
                test_a = test_a.iloc[random.choice(range(test_a.shape[0]))]
                test_b = valid_config_test[
                    (valid_config_test[f"obstacle_height_{not_selected}"] == test_a[f"obstacle_height_{selected_target}"]) &
                    (valid_config_test[f"obstacle_width_{not_selected}"] == test_a[f"obstacle_width_{selected_target}"]) &
                    (valid_config_test[f"obstacle_depth_{not_selected}"] == test_a[f"obstacle_depth_{selected_target}"]) &
                    (valid_config_test[f"obj_{not_selected}_pos_z"] == test_a[f"obj_{selected_target}_pos_z"]) &
                    (valid_config_test["target"] == f"Target-{not_selected}") &
                    (valid_config_test["agent_pos_z"] == fam["agent_pos_z"]) &
                    (valid_config_test[f"obj_{not_selected}_pos_z"] == test_a[f"obj_{selected_target}_pos_z"])
                    ].iloc[0]
                return [fam], [test_a, test_b], history, switch_goals
            elif scenario_sub_type == "Type-2.1.0__1.4":
                try:
                    valid_configs_for_testing = valid_configs[
                        (valid_configs[f"target-{selected_target}-distance"] < 2) &
                        (valid_configs["obstacle_height_1"] == 0) &
                        (valid_configs["obstacle_height_2"] == 0) &
                        (valid_configs["path_type"] == "Straight-Target") &
                        (valid_configs["agent_pos_z"] == fam["agent_pos_z"])
                        ]
                    test_a = valid_configs_for_testing[
                        (valid_configs_for_testing["target"] == f"Target-{selected_target}")
                    ]

                    test_a = test_a.iloc[random.choice(range(test_a.shape[0]))]
                    test_b = valid_configs[
                        (valid_configs[f"target-{not_selected}-distance"] > 3) &
                        (valid_configs["target"] == f"Target-{not_selected}") &
                        (valid_configs["agent_pos_z"] == fam["agent_pos_z"]) &
                        (valid_configs["path_type"] == "Straight-Target") &
                        (valid_configs[f"obj_{not_selected}_pos_z"] == test_a[f"obj_{selected_target}_pos_z"])
                        ].iloc[0]
                    return [fam], [test_a, test_b], history, switch_goals
                except:
                    continue
            elif scenario_sub_type == "Type-2.2.0__1.4":
                pos_x = 0 if selected_target == "1" else 6
                valid_configs_for_testing = valid_configs[
                    (valid_configs[f"obstacle_height_{selected_target}"] == 0) &
                    (valid_configs[f"obj_{selected_target}_pos_x"] == pos_x) &
                    (valid_configs["path_type"] == "Straight-Target") &
                    (valid_configs["agent_pos_z"] == fam["agent_pos_z"])
                    ]
                test_a = valid_configs_for_testing[
                    (valid_configs_for_testing["target"] == f"Target-{selected_target}")
                ]
                test_a = test_a.iloc[random.choice(range(test_a.shape[0]))]
                test_b = valid_config_test[
                    (valid_config_test["target"] == f"Target-{not_selected}") &
                    (valid_config_test[f"obstacle_height_{not_selected}"] != 0) &
                    (valid_config_test[f"obstacle_depth_{not_selected}"].isin(
                        [3, 4, 5])) &
                    (valid_config_test["agent_pos_z"] == fam["agent_pos_z"]) &
                    (valid_config_test[f"obj_{not_selected}_pos_z"] == test_a[f"obj_{selected_target}_pos_z"])
                    ].iloc[0]
                return [fam], [test_a, test_b], history, switch_goals
            else:  # scenario_sub_type == "Type-2.2.1"
                pos_x = 0 if not_selected == "1" else 6
                valid_configs_for_testing = valid_config_test[
                    (valid_config_test[f"obstacle_height_{selected_target}"] != 0) &
                    (valid_config_test[f"obstacle_depth_{selected_target}"].isin(
                        [3, 4, 5])) &
                    (valid_config_test["agent_pos_z"] == fam["agent_pos_z"])
                    ]
                test_a = valid_configs_for_testing[
                    (valid_configs_for_testing["target"] == f"Target-{selected_target}")
                ]
                test_a = test_a.iloc[random.choice(range(test_a.shape[0]))]
                test_b = valid_configs[
                    (valid_configs["target"] == f"Target-{not_selected}") &
                    (valid_configs[f"obstacle_height_{not_selected}"] == 0) &
                    (valid_configs["path_type"] == "Straight-Target") &
                    (valid_configs[f"obj_{not_selected}_pos_x"] == pos_x) &
                    (valid_configs["agent_pos_z"] == fam["agent_pos_z"]) &
                    (valid_configs[f"obj_{not_selected}_pos_z"] == test_a[f"obj_{selected_target}_pos_z"])
                    ].iloc[0]
                return [fam], [test_a, test_b], history, switch_goals


def scene_1_goal_preference_v2(scenario_sub_type, selected_target, object_type_fam, object_type_test, valid_test_configs, history, switch_goals):
    """
            type 1.1.0, type 1.2.0 v1 and v2 -> type 1.2
       type 1.0 -> type 1.1
       type 2.0 -> type 1.3
       type 2.1.0, type 2.2.0 v1 and v2 -> type 1.4

        "Fam": ["ramp", "platform", "pit"],
               "Type-1.1": ["barrier", "ramp", "platform", "pit"],
               "Type-1.2.0__1.2": ["barrier", "ramp", "platform", "pit"],
               "Type-1.1.0__1.2": ["barrier"],
               "Type-1.3": ["barrier", "ramp", "platform", "pit"],
               "Type-2.2.0__1.4": ["barrier", "ramp", "platform", "pit"],
               "Type-2.1.0__1.4": ["barrier"],
       """
    not_selected = "2" if selected_target == "1" else "1"
    if scenario_sub_type in ["Type-1.1", "Type-1.2.0__1.2", "Type-1.3", "Type-2.2.0__1.4"]:
        fam_target = selected_target
        if object_type_fam[0] == "platform":
            fam = valid_test_configs[
                (valid_test_configs["path_type"] == "Platform-jump") &
                (valid_test_configs[f"obstacle_height_{not_selected}"] < 2) &
                (valid_test_configs["target"] == f"Target-{selected_target}")
                ]
            if object_type_fam[1] == "barrier_with_door":
                fam = fam[
                    fam["agent_pos_z"] == 1
                ]
            fam = fam.iloc[random.choice(range(fam.shape[0]))]
        elif object_type_fam[0] == "ramp":
            fam = valid_test_configs[
                (valid_test_configs["path_type"] == "Go-up-ramp") &
                (valid_test_configs["target"] == f"Target-{selected_target}")
                ]
            if object_type_fam[1] == "barrier_with_door":
                fam = fam[
                    fam["agent_pos_z"] == 1
                ]
            fam = fam.iloc[random.choice(range(fam.shape[0]))]
        elif object_type_fam[0] == "pit":
            fam = valid_test_configs[
                (valid_test_configs["path_type"] == "Pit_Jump") &
                (valid_test_configs["target"] == f"Target-{selected_target}")
                ]
            if object_type_fam[1] == "pit-with-bridge":
                fam = fam[
                    fam[f"agent_pos_z"] == fam[f"obj_{selected_target}_pos_z"]
                ]
            fam = fam.iloc[random.choice(range(fam.shape[0]))]
        if scenario_sub_type in ["Type-1.1", "Type-1.3"]:
            if object_type_fam[0] == "platform":
                test_a = valid_test_configs[
                    (valid_test_configs["path_type"] == "Platform-jump") &
                    (valid_test_configs[f"obstacle_height_{not_selected}"] == fam[f"obstacle_height_{fam_target}"]) &
                    (valid_test_configs[f"agent_pos_z"] == fam[f"agent_pos_z"]) &
                    (valid_test_configs["target"] == f"Target-{not_selected}")
                    ]
                test_a = test_a.iloc[random.choice(range(test_a.shape[0]))]
            elif object_type_fam[0] == "ramp":
                test_a = valid_test_configs[
                    (valid_test_configs["path_type"] == "Go-up-ramp") &
                    (valid_test_configs[f"obstacle_height_{not_selected}"] == fam[f"obstacle_height_{fam_target}"]) &
                    (valid_test_configs[f"agent_pos_z"] == fam[f"agent_pos_z"]) &
                    (valid_test_configs["target"] == f"Target-{not_selected}")
                    ]
                test_a = test_a.iloc[random.choice(range(test_a.shape[0]))]
            elif object_type_fam[0] == "pit":
                test_a = valid_test_configs[
                    (valid_test_configs["path_type"] == "Pit_Jump") &
                    (valid_test_configs[f"obstacle_width_{not_selected}"] == fam[f"obstacle_width_{fam_target}"]) &
                    (valid_test_configs[f"obj_{not_selected}_pos_z"] == fam[f"obj_{fam_target}_pos_z"]) &
                    (valid_test_configs[f"agent_pos_z"] == fam[f"agent_pos_z"]) &
                    (valid_test_configs["target"] == f"Target-{not_selected}")
                    ]
                test_a = test_a.iloc[random.choice(range(test_a.shape[0]))]
            if scenario_sub_type == "Type-1.1":
                if switch_goals:
                    return [fam], [test_a, fam], history, switch_goals
                else:
                    return [fam], [fam, test_a], history, switch_goals
            elif scenario_sub_type == "Type-1.3":
                if switch_goals:
                    return [fam], [test_a, fam], history, switch_goals
                else:
                    return [fam], [fam, test_a], history, switch_goals
    # Testing
    if scenario_sub_type in ["Type-1.2.0__1.2", "Type-2.2.0__1.4"]:
        if switch_goals:
            selected_target, not_selected = not_selected, selected_target
        if object_type_test[1] == "platform":
            test_b = valid_test_configs[
                (valid_test_configs["path_type"] == "Platform-jump") &
                (valid_test_configs["agent_pos_z"] == 1) &
                (valid_test_configs[f"obstacle_height_{not_selected}"] < 2) &
                (valid_test_configs["target"] == f"Target-{not_selected}")
            ]
            test_b = test_b.iloc[random.choice(range(test_b.shape[0]))]
        elif object_type_test[1] == "ramp":
            test_b = valid_test_configs[
                (valid_test_configs["path_type"] == "Go-up-ramp") &
                (valid_test_configs["agent_pos_z"] == 1) &
                (valid_test_configs["target"] == f"Target-{not_selected}")
                ]
            test_b = test_b.iloc[random.choice(range(test_b.shape[0]))]
        # elif object_type_test[1] == "pit":
        else:
            test_b = valid_test_configs[
                (valid_test_configs["path_type"] == "Pit_Jump") &
                (valid_test_configs["target"] == f"Target-{not_selected}")
                ]
            if object_type_test[0] == "pit-with-bridge":
                test_b = test_b[
                    (test_b["agent_pos_z"] == test_b[f"obj_{not_selected}_pos_z"])
                ]
            test_b = test_b.iloc[random.choice(range(test_b.shape[0]))]
        if object_type_test[1] in ["pit", "pit-with-bridge"] and object_type_test[0] == "pit-with-bridge":

            test_a = valid_test_configs[
                (valid_test_configs["target"] == f"Target-{selected_target}") &
                (valid_test_configs["path_type"] == "Cross-Bridge") &
                (valid_test_configs["agent_pos_z"] == test_b["agent_pos_z"]) &
                (valid_test_configs[f"obstacle_width_{selected_target}"] == test_b[f"obstacle_width_{not_selected}"]) &
                (valid_test_configs[f"obj_{selected_target}_pos_z"] == test_b[f"obj_{not_selected}_pos_z"]) &
                (valid_test_configs[f"obstacle_{selected_target}_pos_z"] == test_b[f"obj_{not_selected}_pos_z"])
                ]
            test_a = test_a.iloc[random.choice(range(test_a.shape[0]))]
        elif object_type_test[1] in ["pit", "pit-with-bridge"] and object_type_test[0] == "none":
            test_a = valid_test_configs[
                (valid_test_configs["target"] == f"Target-{selected_target}") &
                (valid_test_configs["scene_type"] == "pit_scenes_3_4") &
                (valid_test_configs["path_type"] == "Straight-Target") &
                (valid_test_configs[f"obj_{selected_target}_pos_z"] == test_b[f"obj_{not_selected}_pos_z"]) &
                (valid_test_configs["agent_pos_z"] == test_b["agent_pos_z"])
                ]
            test_a = test_a.iloc[random.choice(range(test_a.shape[0]))]
        elif object_type_test[0] == "none":
            pox = 0 if selected_target == "1" else 6
            test_a = valid_test_configs[
                (valid_test_configs["target"] == f"Target-{selected_target}") &
                (valid_test_configs["scene_type"] == "barrier_scenes_3_4") &
                (valid_test_configs["path_type"] == "Straight-Target") &
                # 1 Because both ramp and platform have fixed z values which is 1
                (valid_test_configs[f"obj_{selected_target}_pos_z"] == 1) &
                (valid_test_configs[f"obj_{selected_target}_pos_x"] == pox) &
                (valid_test_configs["agent_pos_z"] == 1)

                ]
            test_a = test_a.iloc[random.choice(range(test_a.shape[0]))]
        elif object_type_test[0] == "barrier_with_door":
            test_a = valid_test_configs[
                (valid_test_configs["target"] == f"Target-{selected_target}") &
                (valid_test_configs["path_type"] == "barrier-door") &
                (valid_test_configs[f"obstacle_height_{selected_target}"].isin([5, 6])) &
                (valid_test_configs[f"obstacle_{selected_target}_pos_z"] == 1) &
                (valid_test_configs[f"obj_{selected_target}_pos_z"] == 1) &
                (valid_test_configs["agent_pos_z"] == 1)
                ]
            test_a = test_a.iloc[random.choice(range(test_a.shape[0]))]
        return [fam], [test_a, test_b], history, switch_goals




