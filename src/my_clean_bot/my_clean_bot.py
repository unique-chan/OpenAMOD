from .util import *
from .util import _is_not_checked

from shutil import rmtree
import src.my_clean_bot.inireader as inir

class CleanBot:
    def __init__(self, sg):
        self.sg = sg
        self.remarks_tmp_list = []

    def clean_up_during_playback(self, i_time):
        def clean_up_by_angle(tag='EO'):
            # write_start_flag_file(self, f'{i_time}_{look_angle}_{tag}')
            # print(1)
            wait_until_detecting_end_flag_file(self, i_time, look_angle, tag=f'_{tag}')
            self.migrate_img_annot_files_to_save_path(i_time, tag=tag, look_angle=look_angle)
            clear_buffer(del_fn=rmtree, query=f'{self.sg.args.buffer_path}/{self.sg.args.map_name}/{tag}_{zero_pad(i_time, self.sg.args.n_times)}_{look_angle}')
        tags = self.sg.args.mode.split('-')  # ['EO'] | ['IR'] | ['IR', 'EO']
        for look_angle in self.sg.args.look_angles:
            for tag in tags:
                clean_up_by_angle(tag)
        check_sync_between_ARMA_and_python(self, i_time)
        save_metadata(self, i_time)

    def migrate_img_annot_files_to_save_path(self, i_time, tag='', **kwargs):
        look_angle = kwargs['look_angle']
        save_root_path = f'{self.sg.args.save_path}/{zero_pad(i_time, self.sg.args.n_times)}'
        save_path = f'{save_root_path}/{look_angle}'
        makedirs(f'{save_path}', exist_ok=True)
        csv_df = DataFrame()
        
        # First find DEAD
        for cnt, item in enumerate(glob(f'{self.sg.args.buffer_path}/{self.sg.args.map_name}/{zero_pad(i_time, self.sg.args.n_times)}_DEAD')):
            remarks_tmp_list_update(self, '0_dead')
            clear_buffer(del_fn=rmtree, query=item)
        # Second find DAMAGE
        for cnt, item in enumerate(glob(f'{self.sg.args.buffer_path}/{self.sg.args.map_name}/{zero_pad(i_time, self.sg.args.n_times)}_DAMAGE')):
            remarks_tmp_list_update(self, '1_damage')
            clear_buffer(del_fn=rmtree, query=item)

        # Third_1 find image and fix some errors then move it.
        try:
            item = glob(f'{self.sg.args.buffer_path}/{self.sg.args.map_name}/{tag}_{zero_pad(i_time, self.sg.args.n_times)}_{look_angle}/{tag}_{zero_pad(i_time, self.sg.args.n_times)}_{look_angle}.png')[0]
            target_img_path = f'{save_path}/{path.basename(item)}'
            # # at starting, check img resolution. But this is already check before running ARMA3 on /src/my_util.py
            # if _is_not_checked(self, i_time, look_angle):
            #     try_act(check_init_arma3_resolution, self, item)
            try_act(move, item, target_img_path)
            if look_angle < 0:
                rotate_img(target_img_path, angle=180)
            # if self.sg.args.mode != 'IR-EO' and (not path.basename(item).startswith(self.sg.args.mode)):
            #     rename(target_img_path, f'{save_path}/{self.sg.args.mode}_{"_".join(path.basename(item).split("_")[1:])}')
            #     remarks_tmp_list_update(self, f'force_type_changed:{path.basename(item).split("_")[0]}'
            #                             f'->{self.sg.args.mode}')
        except Exception as e:
            num_of_screenshot = len(glob(f'{self.sg.args.buffer_path}/{self.sg.args.map_name}/{tag}_{zero_pad(i_time, self.sg.args.n_times)}_{look_angle}/{tag}_{zero_pad(i_time, self.sg.args.n_times)}_{look_angle}.png'))
            print(f'💀 Error on reading created image. (DirectX Error) Image created: {num_of_screenshot}\n')
            # If you experience this error, this means you have problem on graphic card driver.
            # Please reinstall or update your graphic card driver.
            force_rerun(self, i_time)
            # return
        
        # # Third.2 find annotation info and save it. Only find folder and add info.
        # for cnt, item in enumerate(f for f in glob(f'{self.sg.args.buffer_path}/{self.sg.args.map_name}/{tag}_{zero_pad(i_time, self.sg.args.n_times)}_{look_angle}/**') if path.isdir(f)):
        #     self.extract_store_annot_info_to_csv_df(path.basename(item), csv_df, cnt, look_angle)
            
        # Third.2 with ini: find annotation info and save it.
        inidbi_path = r'C:\Program Files (x86)\Steam\steamapps\common\Arma 3\!Workshop\@INIDBI2 - Official extension\db'
        inifile_name = f'{self.sg.args.map_name}_{tag}_{zero_pad(i_time, self.sg.args.n_times)}_{look_angle}_.ini'
        # print('hey')
        try:
            self.extract_store_ini_annot_info_to_csv_df(csv_df, inidbi_path, inifile_name, look_angle)
        except Exception as e:
            print(e)
            force_rerun(self, i_time)

        # if csv_df has item, save into csv file
        if len(csv_df) and len(csv_df[csv_df['usable'] == 'T']):
            csv_file_path = f'{save_path}/ANNOTATION-{tag}_{zero_pad(i_time, self.sg.args.n_times)}_{look_angle}' 
            csv_df, stat = remove_redundancy(csv_df, p=0.4)
            if stat: # 2_overlapping_bboxes or 3_polygon_failed
                remarks_tmp_list_update(self, stat)
            csv_df.to_csv(f'{csv_file_path}.csv', index=False)
        # if csv_df has no item, then that scene does not contains meaningful data.
        else:
            remarks_tmp_list_update(self, '-1_no_object')
            clear_buffer(del_fn=rmtree, query=save_path)
            if len(listdir(save_root_path)) == 0:
                clear_buffer(del_fn=rmtree, query=save_root_path)

        try:
            os.remove(inidbi_path + '\\' + inifile_name)
        except:
            pass

        # for cnt, item in enumerate(glob(f'{self.sg.args.buffer_path}/{self.sg.args.map_name}/{zero_pad(i_time, self.args.n_times)}_{look_angle}')):
        #     basename = path.basename(item)            
        #     if basename == 'IMG':
        #         for img_file in glob(f'{item}/**'):
        #             target_img_path = f'{save_path}/{path.basename(img_file)}'
        #             if _is_not_checked(self, i_time, look_angle):
        #                 try_act(check_init_arma3_resolution, self, img_file)
        #             try_act(move, img_file, target_img_path)
        #             if look_angle < 0:
        #                 rotate_img(target_img_path, angle=180)
        #             if self.sg.args.mode != 'IR-EO' and (not path.basename(img_file).startswith(self.sg.args.mode)):
        #                 rename(target_img_path,
        #                        f'{save_path}/{self.sg.args.mode}_{"_".join(path.basename(img_file).split("_")[1:])}')
        #                 remarks_tmp_list_update(self,
        #                                         f'force_type_changed:{path.basename(img_file).split("_")[0]}'
        #                                         f'->{self.sg.args.mode}')
        #     elif basename == 'DEAD':
        #         remarks_tmp_list_update(self, '0_dead')
        #     elif basename == 'DAMAGE':
        #         remarks_tmp_list_update(self, '1_damage')
        #     else:
        #         self.extract_store_annot_info_to_csv_df(basename, csv_df, cnt, look_angle)
        # if len(csv_df):
        #     csv_file_path = f'{save_path}/ANNOTATION-{tag}_{zero_pad(i_time, self.sg.args.n_times)}_{look_angle}'
        #     csv_df, stat = remove_redundancy(csv_df, p=0.4)
        #     if stat:  # '2_overlapping_bboxes' or '3_polygon_failed'
        #         remarks_tmp_list_update(self, stat)
        #     csv_df.to_csv(f'{csv_file_path}.csv', index=False)
        # else:
        #     remarks_tmp_list_update(self, '-1_no_object')
        #     clear_buffer(del_fn=rmtree, query=save_path)
        #     if len(listdir(save_root_path)) == 0:
        #         clear_buffer(del_fn=rmtree, query=save_root_path)

    def extract_store_annot_info_to_csv_df(self, basename, csv_df, cnt, look_angle, deli='=', intersect_threshold=5):
        basename_split = basename.split(deli)
        try:  # if len(basename_split) > 1:  # [len == 1 --> DONE / DEAD ... flag folder]
            features = features_post_processing(self, basename_split, look_angle < 0)
            arma3_class = features[0].lower()
            cx, cy = features[1], features[2]
            # csv_df.loc[cnt, 'usable'] = 'T' if 0 <= cx <= self.sg.args.screen_w and \
            #                                    0 <= cy <= self.sg.args.screen_h and \
            #                                    features[-2] < intersect_threshold else 'F'
            csv_df.loc[cnt, 'usable'] = 'T' if 0 <= cx <= self.sg.args.screen_w and \
                                               0 <= cy <= self.sg.args.screen_h else 'F'
            csv_df.loc[cnt, ['main_class', 'middle_class', 'sub_class']] = get_class_h_info(self, arma3_class)
            csv_df.loc[cnt, ['cx', 'cy']] = [features[1], features[2]]
            xy_pairs = [(int(features[(i + 1) * 2 + 1]), int(features[(i + 1) * 2 + 2])) for i in range(8)]
            # for ordinary rectangle bbox (2 points)
            csv_df.loc[cnt, ['min_x', 'min_y']] = [min([xy[0] for xy in xy_pairs]), min([xy[1] for xy in xy_pairs])]
            csv_df.loc[cnt, ['max_x', 'max_y']] = [max([xy[0] for xy in xy_pairs]), max([xy[1] for xy in xy_pairs])]
            # for oriented rectangle bbox (4 points)
            o_bbox = minimum_bbox(xy_pairs)
            for i, (x, y) in enumerate(o_bbox.corner_points):
                csv_df.loc[cnt, [f'x{i + 1}', f'y{i + 1}']] = [int(x), int(y)]
            csv_df.loc[cnt, 'arma3_class'] = arma3_class
            csv_df.loc[cnt, 'id'] = features[-1]
            csv_df.loc[cnt, 'intersect_count'] = features[-2]
            return {'features': features, 'arma3_class': arma3_class}
        except:
            return None
        
    def extract_store_ini_annot_info_to_csv_df(self, csv_df, inidbi_path, inifile_name, look_angle):
        #print('*ini_path:', inidbi_path + '\\' + inifile_name)
        inifile = inir.IniReader(inidbi_path + '\\' + inifile_name)
        ids = inifile.get_all_sections()
        #print('*ids:', ids)
        for cnt, id in enumerate(ids):
            arma3_class = inifile.get_value(id, 'arma3_class')
            #print('*arma3_class:', arma3_class)
            arma3_class = arma3_class.replace('\"', '').lower()
            cx, cy = inifile.get_value(id, 'cx_2d'), inifile.get_value(id, 'cy_2d')
            cx = int(cx)
            cy = int(cy)
            if look_angle < 0:
                cx = self.sg.args.screen_w - cx
                cy = self.sg.args.screen_h - cy

            csv_df.loc[cnt, 'usable'] = 'T' if 0 <= cx <= self.sg.args.screen_w and \
                                               0 <= cy <= self.sg.args.screen_h else 'F'

            csv_df.loc[cnt, ['main_class', 'middle_class', 'sub_class']] = get_class_h_info(self, arma3_class)
            csv_df.loc[cnt, ['cx', 'cy']] = [cx, cy]
            # gain 8 points
            keys = [f'{xy}{k}_2d' for k in range(1, 9) for xy in ['x', 'y']]
            keyszip = list(zip(keys[::2], keys[1::2]))
            pointcoord = []
            for key in keyszip:
                x = int(inifile.get_value(id, key[0]))
                y = int(inifile.get_value(id, key[1]))
                if look_angle < 0:
                    x = self.sg.args.screen_w - x
                    y = self.sg.args.screen_h - y
                pointcoord.append([x, y])
            # for ordinary rectangle bbox (2 points)
            csv_df.loc[cnt, ['min_x', 'max_x']] = [min(point[0] for point in pointcoord), max(point[0] for point in pointcoord)]
            csv_df.loc[cnt, ['min_y', 'max_y']] = [min(point[1] for point in pointcoord), max(point[1] for point in pointcoord)]       
            
            # for oriented rectangle bbox (4 points)
            o_bbox = minimum_bbox(pointcoord)
            for i, (x, y) in enumerate(o_bbox.corner_points):
                csv_df.loc[cnt, [f'x{i + 1}', f'y{i + 1}']] = [x, y]
            csv_df.loc[cnt, 'arma3_class'] = arma3_class
            csv_df.loc[cnt, 'id'] = id
            csv_df.loc[cnt, 'intersect_count'] = inifile.get_value(id, 'intersect_count')
