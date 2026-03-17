import os
import os.path
from os import kill
import sys

import subprocess
from signal import SIGINT

from .my_overlap_rectangle_finder import find_overlap_small_rectangle_ids
from .my_minimum_bbox import minimum_bbox           # DO NOT REMOVE
from src.my_util import clear_buffer, try_act, zero_pad

from os import path, remove, makedirs, listdir
from shutil import rmtree, move
from csv import DictWriter
from time import sleep, time
from PIL import Image
from glob import glob

from pandas import DataFrame                        # DO NOT REMOVE
from tqdm import tqdm

# from src.my_auto_gui import myHotKey, file_force_close_in_arma

os.environ["PYTHONIOENCODING"] = "utf-8"


def rotate_img(target_img_path, angle=180):
    # I don't know the reason but image is rotated 180 degrees... so we need to fix it!
    with Image.open(target_img_path) as rotated_img:
        rotated_img = rotated_img.rotate(angle)
        rotated_img.save(target_img_path)


def remarks_tmp_list_update(self, msg):
    if msg not in self.remarks_tmp_list:
        self.remarks_tmp_list.append(msg)


def remove_redundancy(csv_df, p):
    ids, polygon_error = find_overlap_small_rectangle_ids(csv_df, p)
    state = None
    if ids:
        # csv_df = csv_df[~csv_df.index.isin(ids)]
        state = '2_overlapping_bboxes'
    if polygon_error:
        state = '3_polygon_failed'
    return csv_df, state


def save_metadata(self, i_time):
    metadata_tmp_dic = {
        'i_time': zero_pad(i_time, self.sg.args.n_times),
        # 'year': self.sg.timelines[i_time].year,
        # 'month': self.sg.timelines[i_time].month,
        # 'day': self.sg.timelines[i_time].day,
        'hour': self.sg.timelines[i_time].hour,
        'minute': self.sg.timelines[i_time].minute,
        'weather': self.sg.args.weather,
        'remarks': ','.join(map(str, sorted(self.remarks_tmp_list))),
        'scenario': self.sg.scenario_makers[i_time % len(self.sg.scenario_makers)].__name__,
    }
    meta_csv_file_name = f'meta_{path.basename(self.sg.args.save_path)}.csv'
    if i_time == 0:
        with open(f'{self.sg.args.save_path}/{meta_csv_file_name}', 'w', newline='') as f:
            w = DictWriter(f, metadata_tmp_dic.keys())
            w.writeheader()
            w.writerow(metadata_tmp_dic)
    else:
        with open(f'{self.sg.args.save_path}/{meta_csv_file_name}', 'a', newline='') as f:
            w = DictWriter(f, metadata_tmp_dic.keys())
            w.writerow(metadata_tmp_dic)
    self.remarks_tmp_list = []


def features_post_processing(self, features, rotate_bool):
    xy_sequences = list(map(float, features[1:-1]))
    if rotate_bool:
        # rotate each coordinate 180 degrees!!!
        xy_sequences_new = []
        for i in range(0, len(xy_sequences), 2):
            xy_sequences_new.append(self.sg.args.screen_w - xy_sequences[i])
            xy_sequences_new.append(self.sg.args.screen_h - xy_sequences[i+1])
        xy_sequences = xy_sequences_new
    return features[:1] + xy_sequences + features[-1:]


def check_init_arma3_resolution(self, img_file):
    with Image.open(img_file) as img:
        assert img.size == (self.sg.args.screen_w, self.sg.args.screen_h), \
               f'[WARNING] Current ARMA3 game resolution: {img.size} != ' \
               f'target resolution {(self.sg.args.screen_w, self.sg.args.screen_h)}'


def get_class_h_info(self, arma_class):
    result = self.sg.args.class_structure_df.query(f"(arma3_class == '{arma_class}')")   # if not result.empty:
    return [result[k].item() for k in ['main_class', 'middle_class', 'sub_class']]


def write_start_flag_file(self, flag_name):
    f = open(f'{self.sg.args.mission_path}/start{flag_name}.dummy', 'w')
    f.close()
    sleep(1)


def _is_not_checked(self, i_time, look_angle):
    if i_time == 0 and look_angle == self.sg.args.look_angles[0]:
        return True
    return False

def wait_until_detecting_end_flag_file(self, i_time, look_angle, tag='', time_limit=50, max_time_limit=250):
    s_time = time()
    cnt = 0
    while True:
        # try:
        #     [remove(file) for file in glob(f'{self.sg.args.buffer_path}/**/dummy.png', recursive=True)]
        # except:
        #     continue
        if time() - s_time >= time_limit:
            # myHotKey('enter') # do not need gui thingies
            # file_force_close_in_arma()
            s_time = time()
            cnt += 1
        end_flag_query = f'{self.sg.args.buffer_path}/{self.sg.args.map_name}/DONE{tag}_{zero_pad(i_time, self.sg.args.n_times)}_{look_angle}'
        if glob(end_flag_query):
            clear_buffer(del_fn=rmtree, query=end_flag_query) # block for debugging
            # sleep(1)
            return True
        if cnt * time_limit >= max_time_limit:
            print(f' ⚠️ Maximum time limit ({max_time_limit}sec) exceeded error '
                  f'@ i_time: {i_time}, look_angle: {look_angle}')
            remarks_tmp_list_update(self, '4_end_flag_wait_time_limit_exceeded')
            # clear_buffer(del_fn=rmtree, query=f'{self.sg.args.buffer_path}/**') # no need to remove
            # sleep(1)
            return False
        sleep(1)


def check_sync_between_ARMA_and_python(self, i_time):
    csv_eos, csv_irs, img_eos, img_irs, csv_files, img_files = '-', '-', '-', '-', '-', '-'
    try:
        csv_files = glob(f'{self.sg.args.save_path}/{zero_pad(i_time, self.sg.args.n_times)}/**/**.csv')
        img_files = glob(f'{self.sg.args.save_path}/{zero_pad(i_time, self.sg.args.n_times)}/**/**.png')
        
        csv_files = [os.path.basename(csv_file).replace('ANNOTATION-', '').replace('csv', '') for csv_file in csv_files]
        img_files = [os.path.basename(img_file).replace('png', '') for img_file in img_files]
        
        csv_eos, csv_irs = [_ for _ in csv_files if 'EO' in _], [_ for _ in csv_files if 'IR' in _]
        img_eos, img_irs = [_ for _ in img_files if 'EO' in _], [_ for _ in img_files if 'IR' in _]

        # csv_files = [str('_'.join(os.path.basename(csv_file).split('_')[1:]))[:-4] for csv_file in csv_files]
        # str(~.split('_')[1:])[:-4] ? 'ANNOTATION_001_0.csv'   -> '001_0'
        # img_files = [str('_'.join(os.path.basename(img_file).split('_')[1:]))[:-4] for img_file in img_files]
        # str(~.split('_')[1:])[:-4] ? 'EO_001_0.png'           -> '001_0'
        # assert csv_files == img_files
        if csv_eos:
            assert img_eos == csv_eos
        if csv_irs:
            assert img_irs == csv_irs
        if csv_eos and csv_irs:
            assert len(csv_eos) == len(csv_irs) == len(img_eos) == len(img_irs)
    except Exception as e:
        print('⛔  ERROR')
        print('\t🟡 The sync between ARMA and Python has been broken probably due to the PC overheating.')
        print('\t🟡 Therefore our data generation program is automatically turned off.')
        print('\t🟡 We highly recommend you to shut down the PC for a while to ensure rest and '
              'restart the program after proper inspection. :(')
        print(e)
        print('csv_eos', csv_eos)
        print('csv_irs', csv_irs)
        print('img_eos', img_eos)
        print('img_irs', img_irs)
        print('csv_files', csv_files)
        print('img_files', img_files)
        # exit(-1)
        force_rerun(self, i_time)


def force_rerun(self, i_time):
    def get_command(start_idx):
        return ' '.join([
            f'python main.py',
            f'-mode "{self.sg.args.mode}"',
            f'-map_name "{self.sg.args.map_name}"',
            f'-weather "{self.sg.args.weather}"',
            f'-start_hour {self.sg.args.start_hour}',
            f'-end_hour {self.sg.args.end_hour}',
            f'-n_times {self.sg.args.n_times}',
            f'-camera_moving "{self.sg.args.camera_moving}"',
            f'-class_path "{self.sg.args.class_path}"',
            f'-invalid_bbox_path "{self.sg.args.invalid_bbox_path}"',
            f'-look_angle_min {self.sg.args.look_angle_min}',
            f'-look_angle_max {self.sg.args.look_angle_max}',
            f'-look_angle_interval {self.sg.args.look_angle_interval}',
            f'-arma_root_path "{self.sg.args.arma_root_path}"',
            f'-save_root_path "{self.sg.args.save_root_path}"',
            f'-z_atl {self.sg.args.z_atl}',
            f'-spatial_resolution {self.sg.args.spatial_resolution_original}',
            f'-screen_h {self.sg.args.screen_h_original}',
            f'-screen_w {self.sg.args.screen_w_original}',
            f'-sampling "{self.sg.args.sampling}"',
            # f'-date "{self.sg.args.date}"',
            f'-fov {self.sg.args.fov}',
            f'-resume_scene_idx {start_idx}',
            f'-data_creation_only',
        ])

    def get_command_list(start_idx):
        return [
            f'python', 'main.py',
            f'-mode', f'{self.sg.args.mode}',
            f'-map_name', f'{self.sg.args.map_name}',
            f'-weather', f'{self.sg.args.weather}',
            f'-start_hour', f'{self.sg.args.start_hour}',
            f'-end_hour', f'{self.sg.args.end_hour}',
            f'-n_times', f'{self.sg.args.n_times}',
            f'-camera_moving', f'{self.sg.args.camera_moving}',
            f'-class_path', f'{self.sg.args.class_path}',
            f'-invalid_bbox_path', f'{self.sg.args.invalid_bbox_path}',
            f'-look_angle_min', f'{self.sg.args.look_angle_min}',
            f'-look_angle_max', f'{self.sg.args.look_angle_max}',
            f'-look_angle_interval', f'{self.sg.args.look_angle_interval}',
            f'-arma_root_path', f'{self.sg.args.arma_root_path}',
            f'-save_root_path', f'{self.sg.args.save_root_path}',
            f'-z_atl', f'{self.sg.args.z_atl}',
            f'-spatial_resolution', f'{self.sg.args.spatial_resolution_original}',
            f'-screen_h', f'{self.sg.args.screen_h_original}',
            f'-screen_w', f'{self.sg.args.screen_w_original}',
            f'-sampling', f'{self.sg.args.sampling}',
            f'-fov', f'{self.sg.args.fov}',
            f'-resume_scene_idx', f'{start_idx}',
            f'-data_creation_only',
        ]

    # remove
    print('* remove:', f'{self.sg.args.save_path}/{zero_pad(i_time, self.sg.args.n_times)}')
    clear_buffer(del_fn=rmtree, query=f'{self.sg.args.save_path}/{zero_pad(i_time, self.sg.args.n_times)}')

    # turn-off arma3 forcely
    sleep(1)
    kill(self.sg.args.armaProcessID, SIGINT)

    # offset coordination to skip the scenes already generated
    new_offset = int(i_time / self.sg.args.batch_size)
    start_idx = int(new_offset * self.sg.args.batch_size)
    if new_offset > 0:
        init_sqf_path = f'{self.sg.args.mission_path}/init.sqf'

        with open(init_sqf_path, 'r') as f:
            lines = f.readlines()

        output_lines = [lines[0]]
        is_skip = True
        is_appended = False
        for line in lines[1:]:
            if f'play{new_offset-1}.sqf' in line:
                is_skip = False
                continue
            if not is_skip:
                is_appended = True
                output_lines.append(line)

        if not is_appended:
            print('⚠️ Warning: Might not be skipped for already generated scenarios!')
            output_lines.extend(lines[1:])

        with open(init_sqf_path, 'w') as f:
            f.writelines(output_lines)

    # re-run the code (for remaining scenes)
    # print('✋ Please wait for a moment to resume:', end=' ')
    # for i in tqdm(range(600)):
    #     sleep(0.1)
    sleep(1)
    os.system(get_command(start_idx))
    # with subprocess.Popen(get_command_list(start_idx), shell=False, encoding='utf-8', stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as proc:
    #     for line in proc.stdout:
    #         print(line, end='')
    exit(-1)
    
    #result = subprocess.run(f'start {get_command(start_idx)}', shell=True)
    #sys.exit(result.returncode)
