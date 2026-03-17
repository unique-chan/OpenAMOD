import os
import time
import glob
import shutil
import ast
import sys

import numpy as np
import pandas as pd
import cv2 as cv

import pyautogui as pag
import pydirectinput as pdi


class Script:
    def __init__(self, init_comment=''):
        self.script = init_comment + '\n'

    def add(self, *codes):
        for code in codes:
            code = code.strip()
            if code[-1] == ';':
                code = code[:-1]
            self.script = self.script + code + '; \n'


def clickButton(fig_path, grayscale=False, confidence=0.7, clicks=1, interval=1, sleep_sec=1):
    i = pag.locateCenterOnScreen(fig_path, grayscale=grayscale, confidence=confidence)
    if i is None:
        return False
    time.sleep(0.5)
    pag.click(i, clicks=clicks, interval=interval)
    time.sleep(sleep_sec)
    return True


def myHotKey(*keys):
    for key in keys:
        pdi.keyDown(key)
        time.sleep(0.05)
    for key in keys:
        pdi.keyUp(key)
        time.sleep(0.05)


def read_csv_to_df(csv_path, usable_in_python=False):
    df = pd.read_csv(csv_path)
    df = df.drop_duplicates()
    # if usable_in_python:
    #     df = df[df['usable_in_python'] == 'T']
    return df


def construct_scenario(target_classes):
    print(f'{sys._getframe().f_code.co_name}()', end=' >> ')
    print(f'number of target_classes: {len(target_classes)}', end=' >> ')
    scr = Script()
    insert_camera_creation_code(scr)
    for i, target_class in enumerate(target_classes):
        insert_valid_class_check_code(scr, i, target_class)
    insert_end_flag_sign_code(scr)
    print('DONE')
    return scr.script


def insert_camera_creation_code(scr, x=0, y=0, z_atl=200, sleep=1):
    scr.add(f'sleep {sleep}')
    scr.add('showCinemaBorder false')
    scr.add(f'cam = "camera" camCreate [{x}, {y}, {z_atl}]')
    scr.add(f'cam camSetTarget [{x}, {y + 1}, 0]')
    scr.add(f'cam cameraEffect ["Internal", "BACK"]')
    scr.add(f'cam camCommit 0')
    scr.add(f'sleep {sleep}')


def insert_valid_class_check_code(scr, i, sampled_item, ix=0, iy=0, sleep=1):
    scr.add(f'my_var = "{sampled_item}" createVehicle ([{ix},{iy},0])')
    scr.add(f'tmp_bool = isNull my_var;')
    scr.add(f'''if tmp_bool then {{
        screenshot "{i} + {sampled_item} + INVALID/dummy.png";
    }} else {{ 
        bbox_size = boundingBox my_var;
        screenshot ("{i} + {sampled_item} + " + str bbox_size + "/IMG_{sampled_item}.png");
    }}''')
    scr.add(f'deleteVehicle my_var')
    scr.add(f'sleep {sleep}')


def insert_end_flag_sign_code(scr):
    scr.add('screenshot "DONE\dummy.png"')


def remove_dummy_files_during_playback(buffer_path, save_path, time_limit=50):
    print(f'{sys._getframe().f_code.co_name}()', end=' >> ')
    s_time = time.time()
    while True:
        # remove dummy.png
        try: [os.remove(file) for file in glob.glob(f'{buffer_path}/**/dummy.png', recursive=True)]
        except Exception: time.sleep(1); continue
        if time.time() - s_time >= time_limit:
            myHotKey('enter')
            s_time = time.time()
        # migrate item img file
        for img_file in glob.glob(f'{buffer_path}/**/IMG_**.png'):
            try: shutil.move(img_file, f'{save_path}/{os.path.basename(img_file)}')
            except Exception: time.sleep(1); continue
        # check end_flag
        if glob.glob(f'{buffer_path}/DONE'):
            if glob.glob(f'{buffer_path}/**/IMG_**.png'):
                continue
            else:
                print('DONE')
                break


def extract_measurement_info(df, buffer_path, clear_buffer=True):
    print(f'{sys._getframe().f_code.co_name}()', end=' >> ')
    while True:
        try:
            if len([shutil.rmtree(item) for item in glob.glob(f'{buffer_path}/DONE')]) == 0:
                break
        except Exception:
            time.sleep(1)
            continue
    items = sorted(os.listdir(buffer_path))
    for i, item in enumerate(items):
        features = item.split(' + ')
        assert len(features) == 3, f'Wrong {item} ...'
        idx = df.index[df['arma3_class'] == features[1]].tolist()
        if len(idx):
            idx = idx[0]
            if features[2] != 'INVALID':
                bbox = ast.literal_eval(features[2])
                bottom_left_xyz, top_right_xyz = np.array(bbox[0]), np.array(bbox[1])
                difs = top_right_xyz - bottom_left_xyz
                # info we finally want to grasp
                x_dif, y_dif, z_dif = difs[0], difs[1], difs[2]
                #radius_2d = np.sqrt(np.power(x_dif, 2) + np.power(y_dif, 2)) / 2
                #radius_3d = np.sqrt(np.power(x_dif, 2) + np.power(y_dif, 2) + np.power(z_dif, 2)) / 2  # bbox[2]
                # memo info into df
                df.loc[idx, 'width'] = x_dif
                df.loc[idx, 'height'] = y_dif
                #df.loc[idx, 'radius_2d'] = radius_2d
                #df.loc[idx, 'radius_3d'] = radius_3d
            else:
                df.loc[idx, 'width'] = 'INVALID'
                df.loc[idx, 'height'] = 'INVALID'
                #df.loc[idx, 'radius_2d'] = 'INVALID'
                #df.loc[idx, 'radius_3d'] = 'INVALID'
    if clear_buffer:
        [shutil.rmtree(item) for item in glob.glob(f'{buffer_path}/**')]
    print('DONE')


def store_csv_file(df, save_path, basename):
    print(f'{sys._getframe().f_code.co_name}()', end=' >> ')
    os.makedirs(save_path, exist_ok=True)
    df.to_csv(f'{save_path}/{basename}', index=False)
    print('DONE')


def draw_bbox(save_path, img_w=1280, img_h=720, bbox_size_weight=2):
    csv_file_path = glob.glob(f'{save_path}/**.csv')
    if csv_file_path:
        csv_file_path = csv_file_path[0]
        csv_df = pd.read_csv(csv_file_path)
        csv_df = csv_df[csv_df['usable_in_python'] == 'T']
        csv_df = csv_df.drop_duplicates()
        if len(csv_df):
            os.makedirs(f'{save_path}/bbox', exist_ok=True)
            center_x, center_y = img_w//2, img_h//2
            red_color, blue_color = (0, 0, 255), (255, 255, 0)

            for i, img_file_path in enumerate(glob.glob(f'{save_path}/IMG_**.png')):
                i_img = cv.imread(img_file_path)
                arma3_class_name = os.path.basename(img_file_path)[4:][:-4]
                row = csv_df[csv_df['arma3_class'] == arma3_class_name]
                if len(row):
                    item_w, item_h = int(row['width'] * bbox_size_weight), \
                                     int(row['height'] * bbox_size_weight)
                    min_x, min_y = int(center_x - item_w // 2), int(center_y - item_h // 2)
                    max_x, max_y = int(center_x + item_w // 2), int(center_y + item_h // 2)
                    i_img = cv.circle(i_img, (center_x, center_y), 1, red_color, -1)
                    i_img = cv.rectangle(i_img, (min_x, min_y), (max_x, max_y), blue_color, 1)
                    cv.imwrite(f'{save_path}/bbox/bbox_{arma3_class_name}.png', i_img)
                else:
                    print(f'No info for [{arma3_class_name}]. Failed to draw bbox. Check {csv_file_path}.')
    else:
        print(f'No CSV annotation file in {save_path}.')


# draw_bbox(r'C:\Users\mlv\PycharmProjects\ADS\scene_generator\classes_C', img_w=1280, img_h=720, bbox_size_weight=3.5)
# draw_bbox(r'C:\Users\mlv\PycharmProjects\ADS\scene_generator\classes_E', img_w=1280, img_h=720, bbox_size_weight=3.5)
# draw_bbox(r'C:\Users\mlv\PycharmProjects\ADS\scene_generator\classes_W', img_w=1280, img_h=720, bbox_size_weight=3.5)
# draw_bbox(r'C:\Users\mlv\PycharmProjects\ADS\scene_generator\temp_EE', img_w=1280, img_h=720, bbox_size_weight=3.5)
# draw_bbox(r'C:\Users\mlv\PycharmProjects\ADS\scene_generator\temp_WW', img_w=1280, img_h=720, bbox_size_weight=3.5)
