import random
import json
import itertools

barrier_type = 'cube'
NUM_AGENT_SHAPE = 1
NUM_OBJECT_SHAPE = 1
NUM_POS_X = 3
NUM_POS_Z = 3
NUM_OBSTACLE_HEIGHT = 4
NUM_OBSTACLE_WIDTH = 2
NUM_OBSTACLE_DEPTH = 4

configs = []

valid = []

efficient = []
valid_efficient = []

for agent_shape in range(NUM_AGENT_SHAPE):
    for obj_shape in range(NUM_OBJECT_SHAPE):
        for agent_pos_x in range(NUM_POS_X):
            for obj_pos_x in range(NUM_POS_X):
                if agent_pos_x == obj_pos_x: continue
                for obstacle_pos_x in range(NUM_POS_X):
                    if agent_pos_x == obstacle_pos_x or obj_pos_x == obstacle_pos_x: continue
                    pos_z_lists = [list(range(NUM_POS_Z)), list(range(NUM_POS_Z)), list(range(NUM_POS_Z))]
                    all_pos_z = list(itertools.product(*pos_z_lists))
                    for pos_z in all_pos_z:
                      agent_pos_z, obj_pos_z, obstacle_pos_z = pos_z[0], pos_z[1], pos_z[2]
                      for obstacle_height in range(NUM_OBSTACLE_HEIGHT):
                          for obstacle_width in range(NUM_OBSTACLE_WIDTH):
                            if obstacle_height == 0 and obstacle_width > 0: continue
                            for obstacle_depth in range(NUM_OBSTACLE_DEPTH):
                                config = {'barrier_type': barrier_type,
                                          'id': len(configs),
                                          'agent_shape': agent_shape,
                                          'obj_shape': obj_shape,
                                          'agent_pos_x': agent_pos_x,
                                          'agent_pos_z': agent_pos_z,
                                          'obj_pos_x': obj_pos_x,
                                          'obj_pos_z': obj_pos_z,
                                          'obstacle_pos_x': obstacle_pos_x,
                                          'obstacle_pos_z': obstacle_pos_z,
                                          'obstacle_height': obstacle_height,
                                          'obstacle_width': obstacle_width,
                                          'obstacle_depth': obstacle_depth}
                                configs.append(config)
                    
                                
print(len(configs))

with open('configs_single_goal_{}.json'.format(barrier_type), 'w') as outfile:
    json.dump(configs, outfile, indent=4)


# barrier_type = 'ramp'
# NUM_AGENT_SHAPE = 1
# NUM_OBJECT_SHAPE = 1
# NUM_POS_X = 3
# NUM_POS_Z = 3
# NUM_RAMP_HEIGHT = 2
# NUM_RAMP_ROTATION = 4
# NUM_OBJ_POS_RAMP = 2

# configs = []

# valid = []

# efficient = []
# valid_efficient = []

# for agent_shape in range(NUM_AGENT_SHAPE):
#     for obj_shape in range(NUM_OBJECT_SHAPE):
#         for agent_pos_x in range(NUM_POS_X):
#               for obstacle_pos_x in range(NUM_POS_X):
#                 if agent_pos_x == obstacle_pos_x: continue
#                 pos_z_lists = [list(range(NUM_POS_Z)), list(range(NUM_POS_Z))]
#                 all_pos_z = list(itertools.product(*pos_z_lists))
#                 for pos_z in all_pos_z:
#                   agent_pos_z, obstacle_pos_z = pos_z[0], pos_z[1]
#                   for ramp_height in range(NUM_RAMP_HEIGHT):
#                       for ramp_rotation in range(NUM_RAMP_ROTATION):
#                         for obj_pos_ramp in range(NUM_OBJ_POS_RAMP):
#                             config = {'barrier_type': barrier_type,
#                                       'id': len(configs),
#                                       'agent_shape': agent_shape,
#                                       'obj_shape': obj_shape,
#                                       'agent_pos_x': agent_pos_x,
#                                       'agent_pos_z': agent_pos_z,
#                                       'obstacle_pos_x': obstacle_pos_x,
#                                       'obstacle_pos_z': obstacle_pos_z,
#                                       'ramp_height': ramp_height,
#                                       'ramp_rotation': ramp_rotation,
#                                       'obj_pos_ramp': obj_pos_ramp}
#                             configs.append(config)
                    
                                
# print(len(configs))

# with open('configs_single_goal_{}.json'.format(barrier_type), 'w') as outfile:
#     json.dump(configs, outfile, indent=4)
