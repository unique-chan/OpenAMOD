from os import path, remove, makedirs, listdir, getlogin, kill
from signal import SIGINT
from glob import glob
from shutil import rmtree, copy2
from time import sleep
from re import sub
from math import ceil

from tqdm import tqdm
from subprocess import Popen       # used to open Arma3_x64.exe based on CLI
from winsound import MessageBeep

import ray
import logging

def clear_buffer(del_fn, query):
    while True:
        try:
            if len([del_fn(item) for item in glob(query)]) == 0:
                break
            sleep(0.05)
        except:
            continue
    return True


def try_act(fn, *params):
    while True:
        try:
            fn(*params)
            break
        except:
            sleep(0.05)
            continue
    return True


def remove_start_dummy_files(args):
    clear_buffer(del_fn=remove, query=f'{args.mission_path}/**.dummy')


def highlighted_str(head_msg, body_msg):
    start_highlight, end_highlight = '\033[1;34;40m', '\033[0m'
    return f'{head_msg}: {start_highlight} {body_msg} {end_highlight}'


def prepare_to_start(args):
    def clear_buffer_and_flags(my_args):
        if path.isdir(my_args.buffer_path):
            # try_act(rmtree, f'{my_args.buffer_path}')
            # makedirs(f'{my_args.buffer_path}')
            # clear_buffer(del_fn=remove, query=f'{my_args.buffer_path}/**') # if img file is on Screenshot folder, it stop working
            clear_buffer(del_fn=rmtree, query=f'{my_args.buffer_path}/**')
        remove_start_dummy_files(my_args)
    
    print('🤖 ' + '\033[1m\033[4m' + 'DataGen for AMOD' + '\033[0m')
    checkup_list = [
        highlighted_str('Screen-size / sampling (scaling)', f'{round(args.screen_w/(int(args.sampling[:-1])/100))}x{round(args.screen_h/(int(args.sampling[:-1])/100))}, {args.sampling}'),
        highlighted_str('Details',
                        f'{args.map_name}, {args.mode}, {args.weather}, {args.start_hour}:00~{args.end_hour}:00, {args.n_times} scenes, '
                        f'[{"°, ".join(map(str, args.look_angles)) }°], {args.camera_moving}'),
        highlighted_str('Tip', '🖱️ When the mouse cursor is bound to ARMA, press [Alt]+[Tab] to escape')
    ]
    if args.data_creation_only:
        checkup_list.append(highlighted_str('Note', 'We will reuse scripts already generated '))
    print('\n'.join([f'   {i+1}. {msg}' for i, msg in enumerate(checkup_list)]))
    if args.data_creation_only:
        clear_buffer_and_flags(args)
        return
    if not args.via_gui:
        try:
            out = input('Press [Y] to run this code with current conditions: ').strip().upper()
            if not out.startswith('Y'):
                exit()
        except:
            exit()
    # warning_potential_game_freeze(args)
    clear_buffer_and_flags(args)
    clear_buffer(del_fn=remove, query=f'{args.mission_path}/**.sqf')
    clear_buffer(del_fn=remove, query=f'C:\Program Files (x86)\Steam\steamapps\common\Arma 3\!Workshop\@INIDBI2 - Official extension\db\{args.map_name}*.ini')
        
    
def prepare_to_end(args):
    # file_force_close_in_arma()
    # remove_start_dummy_files(args)
    MessageBeep()
    print('Data creation ended!')

    mission_name = path.basename(args.mission_path)
    steam_Mission_path = f'C:/Program Files (x86)/Steam/steamapps/common/Arma 3/Missions/{mission_name}'
    if path.exists(steam_Mission_path):
        clear_buffer(del_fn=rmtree, query=steam_Mission_path)
        print('↳ Removing mission files on Steam.')

    screenshot_folder = args.buffer_path + '/' + args.map_name
    if path.exists(screenshot_folder):
        clear_buffer(del_fn=rmtree, query=screenshot_folder)
        print('↳ Removing image files on Screenshot.')
    new_param_txt_path = f'{args.arma_root_path}/parameter_{mission_name}.txt'
    
    if path.exists(new_param_txt_path):
        remove(new_param_txt_path)
        print('↳ Removing parameter.txt.')


def update_class_df(args):
    df = args.class_structure_df
    df.loc[df['radius_2d'].isnull(), 'remark'] = 'TYPO'
    df.loc[~df['radius_2d'].isnull(), 'remark'] = ''
    df.to_csv(f'{args.class_path}', index=False)
    if len(df.loc[df['remark'] == 'TYPO']):
        print(f"[WARNING] {len(df.loc[df['remark'] == 'TYPO'])}, df.loc[df['remark'] == 'TYPO']")


def compress_sqf(sqf):
    sqf = sub('//.*?\n', '', sqf)   # no comment (//~)
    sqf = sub('\n+', '\n', sqf)     # no redundant newline (\n)
    sqf = sub('\n', '', sqf)        # no newline (\n)
    sqf = sub(' +', ' ', sqf)       # no redundant space
    sqf = sub(' (\W)', r'\1', sqf)  # no unnecessary space
    return sqf


def zero_pad(word, n, head=''):
    return head + "{:0{}d}".format(word, len(str(n-1)))


def write_init_sqf_script(sg):
    f = open(f'{sg.args.mission_path}/init.sqf', 'w')
    n_batches = ceil(sg.args.n_times / sg.args.batch_size)
    f.write(f'sleep 0.5;')
    # write_prepare_sqf()
    for i in range(-1, n_batches):
        f.write(f'private _handle = execVM "prepare.sqf";' if i == -1 else f'private _handle = execVM "play{i}.sqf";') # prepare.sqf for IR images
        f.write('waitUntil {isNull _handle};\n')
        f.write('sleep 1;\n')
    f.write('[\"Dataset Generation Ended\",true,1,false,true] call BIS_fnc_endMission;')
    f.close()
    f_prepare = open(f'{sg.args.mission_path}/prepare.sqf', 'w')
    f_prepare.write(f'sleep 0.1;')
    f_prepare.close()


def write_sqf_script_per_batch(sg):
    print()
    n_batches = ceil(sg.args.n_times / sg.args.batch_size)
    tqdm_loader = tqdm(range(n_batches))
    remainder = sg.args.n_times % sg.args.batch_size
    for i in tqdm_loader:
        scenarios = []
        start_idx, end_idx = i * sg.args.batch_size, (i + 1) * sg.args.batch_size
        if i + 1 == n_batches and remainder:
            end_idx = start_idx + remainder
        for idx in range(start_idx, end_idx):
            # tqdm_loader.set_description(f'① Scenario generation ({idx}/{sg.args.n_times - 1})')
            msg = f'① Scenario generation ({idx + 1}/{sg.args.n_times}) '
            msg = f'{msg} 🟡' if i % 2 else f'{msg} 🔴'
            tqdm_loader.set_description(msg)
            scenarios.append(sg.create_scenario(idx))
        f_i = open(f'{sg.args.mission_path}/play{i}.sqf', 'w')
        f_i.write(compress_sqf('\n'.join(scenarios)))
        f_i.close()

# Define a remote function for scenario generation
@ray.remote
def generate_scenario_batch(start_idx, end_idx, sg, batch_num, is_last_batch, remainder, bar):
    scenarios = []
    for idx in range(start_idx, end_idx):
        msg = f'① Scenario generation ({idx + 1}/{sg.args.n_times}) '
        msg = f'{msg} 🟡' if batch_num % 2 else f'{msg} 🔴'
        scenarios.append(sg.create_scenario(idx))
        bar.update.remote(1)  # Update the progress bar for each scenario generated
    
    file_name = f'{sg.args.mission_path}/play{batch_num}.sqf'
    with open(file_name, 'w') as f_i:
        f_i.write(compress_sqf('\n'.join(scenarios)))
    
    return file_name

# def write_sqf_script_per_batch_ray(sg):
#     # Initialize Ray
#     ray.init()
#     remote_tqdm = ray.remote(tqdm_ray.tqdm)

#     # Calculate the number of batches and remainder
#     n_batches = ceil(sg.args.n_times / sg.args.batch_size)
#     remainder = sg.args.n_times % sg.args.batch_size
#     futures = []

#     # Create a tqdm progress bar using Ray
#     bar = remote_tqdm.remote(total=sg.args.n_times)

#     for i in range(n_batches):
#         start_idx = i * sg.args.batch_size
#         end_idx = start_idx + sg.args.batch_size

#         # Adjust for the last batch if there is a remainder
#         if i + 1 == n_batches and remainder:
#             end_idx = start_idx + remainder

#         # Dispatch a batch to be processed with progress bar updates
#         futures.append(generate_scenario_batch.remote(start_idx, end_idx, sg, i, i + 1 == n_batches, remainder, bar))

#     # Wait for all tasks to complete
#     ray.get(futures)

#     # Close the progress bar when done
#     ray.get(bar.close.remote())
#     sleep(1)
#     # Don't forget to shut down Ray when done
#     ray.shutdown()

# Define a remote function for scenario generation
@ray.remote
def generate_scenario_batch(start_idx, end_idx, sg, batch_num, is_last_batch, remainder):
    scenarios = []
    for idx in range(start_idx, end_idx):
        msg = f'① Scenario generation ({idx + 1}/{sg.args.n_times}) '
        msg = f'{msg} 🟡' if batch_num % 2 else f'{msg} 🔴'
        scenarios.append(sg.create_scenario(idx))
    
    file_name = f'{sg.args.mission_path}/play{batch_num}.sqf'
    with open(file_name, 'w') as f_i:
        f_i.write(compress_sqf('\n'.join(scenarios)))
    
    return file_name

def write_sqf_script_per_batch_ray(sg):
    print('Using RAY to accelerate Scenario generation')
    
    # Initialize Ray
    ray.init(logging_level=logging.ERROR, log_to_driver=False)
    
    # Calculate the number of batches and remainder
    n_batches = ceil(sg.args.n_times / sg.args.batch_size)
    remainder = sg.args.n_times % sg.args.batch_size
    futures = []
    # Create a tqdm progress bar (leave=True ensures it stays after completion)
    with tqdm(total=sg.args.n_times, desc="① Scenario generation ", leave=True) as pbar:
        for i in range(n_batches):
            start_idx = i * sg.args.batch_size
            end_idx = start_idx + sg.args.batch_size

            # Adjust for the last batch if there is a remainder
            if i + 1 == n_batches and remainder:
                end_idx = start_idx + remainder

            # Dispatch a batch to be processed
            futures.append(generate_scenario_batch.remote(start_idx, end_idx, sg, i, i + 1 == n_batches, remainder))

        # Monitor the progress of all tasks and update tqdm manually
        while futures:
            done, futures = ray.wait(futures, timeout=1)
            for _ in done:
                pbar.update(sg.args.batch_size)

    # Don't forget to shut down Ray when done
    ray.shutdown()


def write_scenarios(sg):
    if sg.args.data_creation_only:
        return
    write_init_sqf_script(sg)
    # write_sqf_script_per_batch(sg)
    write_sqf_script_per_batch_ray(sg)


def play_scenarios(args, cb):
    assert path.exists(f'{args.mission_path}/init.sqf'), 'No scenario scripts for play_scenarios()'
    assert not glob(f'{args.mission_path}/**.dummy'), \
        f'Before play_scenarios(), any <start**.dummy> files should be eliminated in {args.mission_path}'
    # EO_IR_setting_for_play_scenarios(args)
    if args.mode == 'IR':
        with open(f'{args.mission_path}/prepare.sqf', 'w',encoding='UTF-8') as f:
            f.write('true setCamUseTI 0;')  # activate arma dtv (default thermal vision)
        sleep(0.2)
    copy_mission_to_steam_arma3_folder(args)
    
    # Check Screenshot buffer size before running program.
    arma3_profile_path = f'{args.arma_root_path}' + f'/{getlogin()}.Arma3Profile'
    with open(arma3_profile_path, 'r', encoding='UTF-8') as f:
        lines = f.readlines()
    for i, line in enumerate(lines):
        if 'maxScreenShotFolderSizeMB' in line:
            lines[i] = f'maxScreenShotFolderSizeMB=100000;\n'  # 100 GB
            break
    else:
        lines.append(f'maxScreenShotFolderSizeMB=100000;\n')
    with open(arma3_profile_path, 'w') as f:
        f.writelines(lines)

    # Change rendering resolution and window resolution before running program.
    arma3_cfg_path = f'{args.arma_root_path}/Arma3.cfg'
    with open(arma3_cfg_path, 'r', encoding='UTF-8') as f:
        lines = f.readlines()
    winWidth = round(args.screen_w/(int(args.sampling[:-1])/100))
    winHeight = round(args.screen_h/(int(args.sampling[:-1])/100))
    for i, line in enumerate(lines):
        for key, val in {'renderWidth': args.screen_w, 'renderHeight': args.screen_h,
                         'winWidth': winWidth, 'winHeight': winHeight}.items():
            if key in line:
                lines[i] = f'{key}={val};\n'
    with open(arma3_cfg_path, 'w', encoding='UTF-8') as f:
        f.writelines(lines)
    
    # Before starting ARMA3 program, prepare parameters.
    # Be careful because ARMA3 safely accepts path with \.
    # It sometimes makes error with path consists of /. IDK the reason,
    # if you know the reason or truth, fix the code!
    arma3_x64_path = r"C:\Program Files (x86)\Steam\steamapps\common\Arma 3\arma3_x64.exe"
    
    # Parameters that changes H/W or System setting may not work if they are in parameter.txt
    # So they are directly passed to Arma3_x64.exe . Also, -hugePages does not work well but mimalloc works very well.
    # basic_params = (r'-skipIntro -noSplash -window -enableHT -malloc=mimalloc_v212_lock_pages '
    #                 r'-hugePages -noPause -noPauseAudio -filePatching -maxFileCacheSize=2048 -debug')
    basic_params = (r'-skipIntro -noSplash -window -cpuCount=6 -exThreads=7 '
                    r'-hugePages -noPause -noPauseAudio -filePatching -maxMem=32768 -malloc=system -world=empty -maxFileCacheSize=4096 -debug')
    # add -debug option for specific debug
    # add -noLogs option for stop writing logs on C:\Users\{username}\AppData\Local\Arma 3\
    mission_name = path.basename(args.mission_path)
    basic_param_txt_path = './parameter.txt'
    new_param_txt_path = f'{args.arma_root_path}/parameter_{mission_name}.txt'

    # create new parameter_missioname.txt with add -init statement.
    # example) -init=playMission["","240116test.Stratis",true]
    # you should put `\n` for executing mission automatically.
    try:
        with open(basic_param_txt_path, 'r', encoding='utf-8') as basic:
            basic_param_lines = basic.readlines()
        with open(new_param_txt_path, 'w', encoding='utf-8') as added:
            added.writelines(basic_param_lines)
            added.write(f'-init=playMission["","{mission_name}",true]\n')          
    except Exception as e:
        print(f'An error occured on copying parameter.txt\n Error: {e}')
    
    # open arma3_x64.exe with prepared parameter and execute scenarios automatically.
    new_param_txt_path = new_param_txt_path.replace('/', '\\')
    par_txt = '-par=' + new_param_txt_path
        
    armaProcess = Popen([arma3_x64_path, basic_params, par_txt])
    args.armaProcessID = armaProcess.pid  # Register arma3 process id for force kill

    time_pass = 0
    start_flag_path = f'{args.buffer_path}/**'
    while True:
        min, sec = divmod(time_pass, 60)
        msg = f'\tWaiting ARMA3 to be loaded → ⌛ Time passed: {min:02} min {sec:02} sec.'
        msg = f'{msg} 🟡' if time_pass % 2 else f'{msg} 🔴'
        print(msg, end='\r')
        time_pass = time_pass + 1
        sleep(1)
        if len(glob(start_flag_path)):
            break

    print()
    tqdm_loader = tqdm(range(args.resume_scene_idx, args.n_times))

    for idx in tqdm_loader:        
        msg = f'③ Scenario played ({idx}/{args.n_times})'
        msg = f'{msg} 🟡' if idx % 2 else f'{msg} 🔴'
        tqdm_loader.set_description(msg)
        cb.clean_up_during_playback(idx)
        # sleep(1)
    sleep(1)
    kill(armaProcess.pid, SIGINT)


def copy_mission_to_steam_arma3_folder(args):
    # copy created mission into steam Mission folder
    mission_name = path.basename(args.mission_path)
    files_list_on_mission = [f for f in listdir(args.mission_path) if path.isfile(path.join(args.mission_path, f))]
    steam_Mission_path = path.join(r'C:\Program Files (x86)\Steam\steamapps\common\Arma 3\Missions', mission_name)
    try:
        makedirs(steam_Mission_path)
    except:
        rmtree(steam_Mission_path)
        makedirs(steam_Mission_path)
    for file_name in tqdm(files_list_on_mission, desc=f'② Copying missions to other folder to execute'):
        src_file_path = path.join(args.mission_path, file_name)
        dest_file_path = path.join(steam_Mission_path, file_name)
        copy2(src_file_path, dest_file_path)
    makedirs(args.save_path)
    sleep(1)
