from .my_script import *
from .util_for_script import *
from .util import *
import src.my_scene_generator.script_arma_selection as sas


class SceneGenerator:
    def __init__(self, args):
        self.args = args
        self.timelines = get_timelines(args)
        self.land_sea_main_class_dic = get_land_sea_main_class_dic(self, type_query="type != 'no_annot'")
        self.land_sea_main_class_no_annot_dic = get_land_sea_main_class_dic(self, type_query="type == 'no_annot'")
        # add your scenario-generation functions to <scenario_makers>!
        # self.scenario_makers = [self.get_scenario_randomly_scattered, ]
        self.scenario_makers = [self.get_scenario_arma_selection, ]

    def create_scenario(self, i_time):
        return self.scenario_makers[i_time % len(self.scenario_makers)](i_time)

    def get_scenario_randomly_scattered(self, i_time):
        scr = Script()
        land_or_sea, sampled_items, ixiys, cam_dic = prepare_for_scenario_randomly_scattered(self)
        cx, cy, _ = cam_dic['target_points'][0]
        insert_each_position_land_sea_check_code(scr, cx, cy, ixiys)
        land_sea_item_pairs = insert_random_items_placement_code(self, scr, land_or_sea, sampled_items, cx, cy, ixiys, i_time)
        insert_post_processing_code(self, scr, i_time, cam_dic, len(sampled_items), land_sea_item_pairs)
        return scr.get_script()

    def get_scenario_arma_selection(self, i_time):
        scr = Script()
        land_prob, land_or_sea, sampled_items, ixiys, cam_dic = prepare_for_arma3_selection(self)
        # print(land_prob)
        sas.insert_camcenter_pos_code(scr, land_prob)
        sas.insert_each_position_land_sea_check_code(scr, ixiys)
        land_sea_item_pairs = sas.insert_random_items_placement_code(self, scr, land_or_sea, sampled_items, ixiys, i_time)
        sas.insert_post_processing_code(self, scr, i_time, cam_dic, len(sampled_items), land_sea_item_pairs)
        return scr.get_script()

    # add extra get_scenario!