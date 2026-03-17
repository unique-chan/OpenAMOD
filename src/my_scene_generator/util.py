from datetime import datetime
from random import random, randint, choice, choices

from numpy import unique, argmax, tan, cos, deg2rad


def get_timelines(args):
    # month = args.dict_options['months'][args.map_name]
    start = datetime(args.date.year, args.date.month, args.date.day, args.start_hour, 0)
    end = datetime(args.date.year, args.date.month, args.date.day, args.end_hour, 0)
    delta = (end - start) / args.n_times
    timelines = []
    for _ in range(args.n_times):
        start += delta
        timelines.append(start)
    return timelines


def random_split(k, m):
    if k <= 0 or m <= 0:
        return None
    if m == 1:
        return [k]
    result = []
    for i in range(m - 1):
        x = randint(1, k - (m - i - 1))
        result.append(x)
        k -= x
    result.append(k)
    return result


def sample_class_then_item(self, land_or_sea, n_classes, n_items):
    n_items_per_class = random_split(n_items, n_classes)
    if random() < 0.15:  # no_annot_classes should be inserted
        n_annot_classes, n_no_annot_classes = n_classes - 1, 1
    else:
        n_annot_classes, n_no_annot_classes = n_classes, 0
    try:    chosen_annot_classes = choices(self.land_sea_main_class_dic[land_or_sea], k=n_annot_classes)
    except: chosen_annot_classes = []
    try:    chosen_no_annot_classes = choices(self.land_sea_main_class_no_annot_dic[land_or_sea], k=n_no_annot_classes)
    except: chosen_no_annot_classes = []
    items = []
    for i, chosen_class in enumerate(chosen_annot_classes + chosen_no_annot_classes):
        my_query = f"(main_class == '{chosen_class}') and ({land_or_sea} == 'T')"
        my_output = self.args.class_structure_df.query(my_query)
        if not my_output.empty:
            items.extend(choices(list(my_output['arma3_class']), k=n_items_per_class[i]))
    return items


def sample_item_immediately(self, land_or_sea, n_classes, n_items):
    my_query = f"({land_or_sea} == 'T')"
    items = list(self.args.class_structure_df.query(my_query)['arma3_class'])
    return choices(choices(items, k=n_classes), k=n_items)


def get_item_radius(self, arma3_class):
    return self.args.class_structure_df.query(f"(arma3_class == '{arma3_class}')")['radius_2d'].item()


def get_random_item(self, item_radius, land_or_sea='land_ok'):
    candidates = list(self.args.class_structure_df.query(f"(radius_2d <= {item_radius}) and "
                                                         f"({land_or_sea} == 'T')")['arma3_class'])
    return choice(candidates) if candidates else None


def set_max_item_num_for_scenario_randomly_scattered(self, obj_ratio=0.4):
    vals, counts = unique(self.args.class_structure_df['radius_2d'], return_counts=True)
    radius = vals[argmax(counts)]
    max_item_num = (self.args.plane_h // radius) * (self.args.plane_w // radius)
    max_item_num = int(max_item_num * obj_ratio)
    self.args.dict_options['scenario_randomly_scattered']['max_item_num'] = max_item_num
    assert self.args.dict_options['scenario_randomly_scattered']['min_item_num'] < max_item_num


def get_land_sea_main_class_dic(self, type_query="type != 'no_annot'"):
    return {key: list(self.args.class_structure_df.query(f"({key} == 'T') and ({type_query})")['main_class'].unique())
            for key in ['land_ok', 'sea_ok']}


def _set_cam_and_target_points_per_angle(dic, cx, cy, cz, delta_y):
    dic['cam_points'].append((cx, cy + delta_y, cz))
    dic['target_points'].append((cx, cy, 0))


def get_random_points(self, n_items):
    return [(randint(-self.args.plane_w // 2, self.args.plane_w // 2),
             randint(-self.args.plane_h // 2, self.args.plane_h // 2)) for _ in range(n_items)]


def get_all_cam_and_target_points(self):
    world_size = self.args.dict_options['world_sizes'][self.args.map_name]
    cx = randint(0 + (self.args.plane_w // 2), world_size - (self.args.plane_w // 2))
    cy = randint(0 + (self.args.plane_h // 2), world_size - (self.args.plane_h // 2))
    dic = {'cam_points': [], 'target_points': []}
    if self.args.camera_moving == 'air_to_air':  # default
        for look_angle in self.args.look_angles:
            _set_cam_and_target_points_per_angle(dic, cx, cy,
                                                 self.args.z_atl,
                                                #  int(self.args.z_atl / tan(deg2rad(90 - look_angle)) + 0.001)) # As camera can work with different xy coordinate, move slightly.
                                                 self.args.z_atl * tan(deg2rad(look_angle)) + 0.001) # cot(90-a)=tan(a)

    else:
        for look_angle in self.args.look_angles:
            _set_cam_and_target_points_per_angle(dic, cx, cy,
                                                 self.args.z_atl * cos(deg2rad(look_angle)) + 0.001, # actually no need to use abs(look_angle) to calculate cosine
                                                 self.args.z_atl * cos(deg2rad(90 - look_angle)) + 0.001)
    return dic

def get_all_cam_and_target_points_diff(self):
    world_size = self.args.dict_options['world_sizes'][self.args.map_name]
    cx = randint(0 + (self.args.plane_w // 2), world_size - (self.args.plane_w // 2))
    cy = randint(0 + (self.args.plane_h // 2), world_size - (self.args.plane_h // 2))
    dic = {'cam_points': [], 'target_points': []}
    if self.args.camera_moving == 'air_to_air':  # default
        for look_angle in self.args.look_angles:
            _set_cam_and_target_points_per_angle(dic, 0, 0,
                                                 self.args.z_atl,
                                                #  int(self.args.z_atl / tan(deg2rad(90 - look_angle)) + 0.001)) # As camera can work with different xy coordinate, move slightly.
                                                 self.args.z_atl * tan(deg2rad(look_angle)) + 0.001) # cot(90-a)=tan(a)

    else:
        for look_angle in self.args.look_angles:
            _set_cam_and_target_points_per_angle(dic, 0, 0,
                                                 self.args.z_atl * cos(deg2rad(look_angle)) + 0.001, # actually no need to use abs(look_angle) to calculate cosine
                                                 self.args.z_atl * cos(deg2rad(90 - look_angle)) + 0.001)
    return dic

def prepare_for_scenario_randomly_scattered(self):
    opt_src = self.args.dict_options['scenario_randomly_scattered']
    if not opt_src.get('max_item_num'):
        set_max_item_num_for_scenario_randomly_scattered(self)
    n_classes = randint(opt_src['min_class_num'], opt_src['max_class_num'])
    n_items = randint(opt_src['min_item_num'], opt_src['max_item_num'])
    land_prob = self.args.dict_options['land_probs'][self.args.map_name]
    land_or_sea = 'land_ok' if random() < land_prob else 'sea_ok'
    ixiys = get_random_points(self, n_items)
    cam_dic = get_all_cam_and_target_points(self)
    sampled_items = sample_class_then_item(self, land_or_sea, n_classes, n_items)
    return land_or_sea, sampled_items, ixiys, cam_dic

def prepare_for_arma3_selection(self):
    opt_src = self.args.dict_options['scenario_randomly_scattered']
    if not opt_src.get('max_item_num'):
        set_max_item_num_for_scenario_randomly_scattered(self)
    n_classes = randint(opt_src['min_class_num'], opt_src['max_class_num'])
    n_items = randint(opt_src['min_item_num'], opt_src['max_item_num'])
    land_prob = self.args.dict_options['land_probs'][self.args.map_name]
    land_or_sea = 'land_ok' if random() < land_prob else 'sea_ok'
    ixiys = get_random_points(self, n_items)
    cam_dic = get_all_cam_and_target_points_diff(self) # cam_dic = diff from center point
    sampled_items = sample_class_then_item(self, land_or_sea, n_classes, n_items)
    return land_prob, land_or_sea, sampled_items, ixiys, cam_dic