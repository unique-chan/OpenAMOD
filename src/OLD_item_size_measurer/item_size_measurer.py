from util_gui_common import *
from util_for_item_size_measurer import *
import os


# USER PARAMETERS ######################################################################################################
env_name = 'vr'
# win_pc_usr_name = 'mlv'
root_path = f'C:/Users/{os.getlogin()}/Documents/Arma 3'
csv_path = 'classes/CLASSES.csv'
save_path = f'C:/Users/{os.getlogin()}/Desktop/{os.path.basename(csv_path)[:-4]}'
########################################################################################################################

missions_path = f'{root_path}/missions'
buffer_path = f'{root_path}/Screenshots'
current_mission_path = f'{full_dir_path(missions_path, env_name)}'
prepare_to_start(buffer_path, current_mission_path, save_path)

df = read_csv_to_df(csv_path)
script = construct_scenario(df['arma3_class'])
write_down(script, f'{current_mission_path}/init.sqf')
# open_play_init_scenario(env_name)
remove_dummy_files_during_playback(buffer_path, save_path)
extract_measurement_info(df, buffer_path, clear_buffer=True)
store_csv_file(df, save_path, os.path.basename(csv_path))
remove_start_dummy_files(current_mission_path, is_arma3_on=True)

# radius_2d? sqrt(width^2 + height^2) / 2
