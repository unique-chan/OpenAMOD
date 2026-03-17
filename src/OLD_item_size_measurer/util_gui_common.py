import os
from time import sleep
import glob
import shutil

import pyautogui as pag
import pydirectinput as pdi
from pyperclip import copy


def clickButton(fig_path, grayscale=False, confidence=0.7):
    i = pag.locateCenterOnScreen(fig_path, grayscale=grayscale, confidence=confidence)
    if i is None:
        return False
    sleep(0.5)
    pag.click(i, clicks=1, interval=1)
    sleep(1)
    return True


def myHotKey(*keys):
    for key in keys:
        pdi.keyDown(key)
        sleep(0.05)
    for key in keys:
        pdi.keyUp(key)
        sleep(0.05)


def open_play_init_scenario(env_name):
    sleep(0.01)
    clickButton(f'figs/arma3_logo.png', grayscale=True)
    clickButton(f'figs/scenario.png', grayscale=True)
    myHotKey('ctrl', 'o')
    copy(env_name)
    myHotKey('ctrl', 'v')
    sleep(2)
    myHotKey('enter')
    sleep(2)
    myHotKey('enter')


def full_dir_path(missions_path, env_name):
    dirs = glob.glob(f'{missions_path}/{env_name}*')
    assert len(dirs) > 0, f'At {missions_path}, there is no directory for {env_name}'
    return dirs[0]


def write_down(script, file_path):
    f = open(file_path, 'w')
    f.write(script)
    # f.flush()
    f.close()


def clear_buffer(buffer_path):
    while True:
        try:
            if len([shutil.rmtree(item) for item in glob.glob(f'{buffer_path}/**')]) == 0:
                break
        except Exception:
            continue


def remove_start_dummy_files(current_mission_path, is_arma3_on=False):
    print('(-: Remove all the unnecessary start*.dummy files. ', end=' ... ')
    if is_arma3_on:
        file_force_close_in_arma3()
    while True:
        try:
            if len([os.remove(item) for item in glob.glob(f'{current_mission_path}/**.dummy')]) == 0:
                break
        except Exception:
            continue
    print('DONE :-)')


def file_force_close_in_arma3(head='', fin_with_esc=False):
    myHotKey('esc')
    clickButton(f'{head}figs/arma3_logo.png', grayscale=True)
    pag.moveRel(0, -30)
    sleep(0.02)
    pag.click(clicks=1, interval=0.3)
    sleep(0.02)
    clickButton(f'{head}figs/arma3_logo.png', grayscale=True)
    if fin_with_esc:
        sleep(0.5)
        myHotKey('esc')
    sleep(0.02)


def prepare_to_start(buffer_path, current_mission_path, save_path):
    if os.path.isdir(buffer_path):
        if len(os.listdir(buffer_path)) > 0:
            clear_buffer(buffer_path)
    remove_start_dummy_files(current_mission_path, is_arma3_on=False)
    os.makedirs(save_path, exist_ok=False)
    print('[Note] Please go to any eden-editor map before running this code')
