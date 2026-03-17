from .util import get_random_item, get_item_radius
from src.my_util import zero_pad

from random import randint, choice, random

from numpy import where, zeros

def insert_camcenter_pos_code(scr, land_prob):
    # print('cs: ', land_prob)
    if random()>land_prob: 
        blacklist = "ground" 
    else: 
        blacklist = "water"
    scr.add(f'''
            center_sample = [nil, ["{blacklist}"]] call BIS_fnc_randomPos;
            while {{count center_sample == 2}} do {{center_sample = [nil, ["{blacklist}"]] call BIS_fnc_randomPos;}};
            cx = center_sample select 0;
            cy = center_sample select 1;
            cz = center_sample select 2;
            ''')
    
def insert_each_position_land_sea_check_code(scr, ixiys):
    # getAllEnvSoundControllers: 10+1: meadows, 12+1: trees, 14+1: houses, 16+1: forest, 18+1: sea
    for i, (ix, iy) in enumerate(ixiys):
        scr.add(f'''if (surfaceIsWater [cx + {ix}, cy + {iy}]) then {{
            is_land_{i} = false; is_sea_{i}=true;  
        }} else {{
            is_sea_{i} = false; is_land_{i} = true;
        }}''')
        scr.add(f'rot_degree_{i} = ""')
    scr.add('sleep 0.5')
    
def insert_random_items_placement_code(self, scr, land_or_sea, sampled_item_classes, ixiys, i_time):
    land_sea_item_pairs = []
    mask = zeros((self.args.plane_h, self.args.plane_w))
    insert_start_simulation_code(scr)
    insert_set_time_multiplier_code(scr, sec=60) # set time moves 60 times faster
    for cnt, item in enumerate(sampled_item_classes):
        ix, iy = ixiys[cnt]
        item_radius = int(get_item_radius(self, item))
        # if check_item_collision(mask, ix, iy, item_radius):
        #     land_sea_item_pairs.append((None, None))
        #     continue
        rot_degree = randint(0, 360)
        if land_or_sea == 'land_ok':
            land_item, sea_item = item, get_random_item(self, item_radius, land_or_sea='sea_ok')
        else:  # 'sea_ok'
            land_item, sea_item = get_random_item(self, item_radius, land_or_sea='land_ok'), item
        land_sea_item_pairs.append((land_item, sea_item))
        insert_item_placement_code(self, scr, cnt, ix, iy, rot_degree,
                                   land_item, sea_item, item_radius, i_time)
    insert_stop_simulation_code(scr)
    return land_sea_item_pairs

def insert_start_simulation_code(scr):
    scr.add('sleep 0.1')
    # scr.add(f'setAccTime 1')
    scr.add(f'setTimeMultiplier 1')
    scr.add('sleep 0.1')
    # for i in range(n):
    #     scr.add(f'my_var_{i} enableSimulationGlobal false')
    scr.add('enableDynamicSimulationSystem true')
    
def insert_stop_simulation_code(scr):
    # scr.add('sleep 2')
    # scr.add(f'setTimeMultiplier 1')
    # scr.add('sleep 1')
    # for i in range(n):
    #     scr.add(f'my_var_{i} enableSimulationGlobal false')
    scr.add('enableDynamicSimulationSystem false')
    # scr.add(f'setAccTime 0')

def insert_set_time_multiplier_code(scr, sec=5):
    # sec=10? -> 1sec ==> 10sec in ARMA
    # scr.add(f'setAccTime {sec}')
    scr.add(f'setTimeMultiplier {sec}')
    scr.add(f'sleep 2')
    
def insert_item_placement_code(self, scr, i, ix, iy, rot_degree, land_item, sea_item, item_radius, i_time, z_atl=1):
    # changed z_atl into 1 because position is PositionATL or PositionAGL,
    # which means vehicle is placed right to surface of land/sea.
    # check https://community.bistudio.com/wiki/Position
    def rand_float(eps=0.1):
        return random() + eps
    engine_tmp = rand_float()
    tire_tmp = rand_float()
    firearm_tmp = rand_float()
    # engine_tmp = rand_float() / 10 if random() < 0.8 else random()
    # tire_tmp = rand_float() / 10 if random() < 0.8 else random()
    # firearm_tmp = rand_float() / 10 if random() < 0.8 else random()
    # check https://community.bistudio.com/wiki/AI_Behaviour for AI Behaviour
    # check https://community.bistudio.com/wiki/createVehicle for placement(NONE, CAN_COLLIDE, FLY)
    scr.add(f'nos = nearestObjects [[cx + {ix}, cy + {iy}, 0], [], {item_radius * 0.8}, true]') # change 2.0 to 0.8
    scr.add_no_col_end(f'''if (count(nos) == 0) then {{ if (is_land_{i}) then {{         
        my_var_{i} = createVehicle ["{land_item}",[cx + {ix}, cy + {iy}, {z_atl}],[],0,"NONE"];
        my_var_{i} setCombatBehaviour "CARELESS";
        my_var_{i} setVehicleTIPars [{engine_tmp}, {tire_tmp}, {firearm_tmp}];
        my_var_{i} addEventHandler ["hit", {{
            screenshot ('{self.args.map_name}\{zero_pad(i_time, self.args.n_times)}_DAMAGE\{land_item}.png'); 
            sleep 0.5;
        }}];
        my_var_{i} addEventHandler ["killed", {{
            screenshot ('{self.args.map_name}\{zero_pad(i_time, self.args.n_times)}_DEAD\{land_item}.png');
            sleep 0.5;
        }}];
        [my_var_{i}, [{rot_degree}, 0, 0]] call BIS_fnc_setObjectRotation;
        rot_degree_{i} = "{str(rot_degree)}";
    }}''')
    if sea_item is not None:
        scr.add(f'''else {{
            if (is_sea_{i}) then {{
                my_var_{i} = createVehicle ["{sea_item}",[cx + {ix}, cy + {iy}, {z_atl}],[],0,"NONE"];
                my_var_{i} setCombatBehaviour "CARELESS";
                my_var_{i} setVehicleTIPars [{engine_tmp}, {tire_tmp}, {firearm_tmp}];
                my_var_{i} addEventHandler ["hit", {{
                    screenshot ('{self.args.map_name}\{zero_pad(i_time, self.args.n_times)}_DAMAGE\{sea_item}.png');
                    sleep 0.5;
                }}];
                my_var_{i} addEventHandler ["killed", {{
                    screenshot ('{self.args.map_name}\{zero_pad(i_time, self.args.n_times)}_DEAD\{sea_item}.png');
                    sleep 0.5;
                }}];
                [my_var_{i}, [{rot_degree}, 0, 0]] call BIS_fnc_setObjectRotation;
                rot_degree_{i} = "{str(rot_degree)}";
            }};
        }}; }}''')
    else:
        scr.add(f' }} ;')
    # scr.add(f'sleep {sleep}')
    
def insert_post_processing_code(self, scr, i_time, cam_dic, n_items, land_sea_item_pairs=None):
    insert_set_datetime_and_weather_code(self, scr, i_time)
    insert_stop_simulation_code(scr)
    if self.args.mode != 'IR-EO':
        for _, look_angle in enumerate(self.args.look_angles):
            # insert_start_flag_sign_waiting_code(scr, f'{i_time}_{look_angle}_{self.args.mode}',
            #                                     sleep=(10 if _ == 0 else 1))
            base_path = f'{self.args.map_name}\\{self.args.mode}_{zero_pad(i_time, self.args.n_times)}_{look_angle}\\'
            current_flag = f'{self.args.mode}_{zero_pad(i_time, self.args.n_times)}_{look_angle}'
            insert_camera_creation_code(scr, cam_dic['cam_points'][_], self.args.fov)
            insert_camera_tilting_code(scr, cam_dic['target_points'][_], sleep=1)
            # insert_bbox_labels_store_code(self, scr, n_items, land_sea_item_pairs, base_path)
            insert_bbox_labels_store_code_inidbi2(self, scr, n_items, land_sea_item_pairs, base_path)
            if (self.args.mode == 'IR'):
                scr.add('sleep 5')
            insert_set_datetime_and_weather_code(self, scr, i_time)
            insert_capture_code(scr, base_path + current_flag, sleep=1)
            insert_end_flag_sign_code(scr, self.args.map_name + '\\DONE_' + current_flag)
    else:
        for _, look_angle in enumerate(self.args.look_angles):
            # insert_start_flag_sign_waiting_code(scr, f'{i_time}_{look_angle}_IR',
            #                                     sleep=(10 if _ == 0 else 1))
            insert_camera_creation_code(scr, cam_dic['cam_points'][_], self.args.fov)
            insert_camera_tilting_code(scr, cam_dic['target_points'][_], sleep=1)

            # IR ->
            scr.add('true setCamUseTI 0')  # activate IR
            if _ == 0:
                scr.add('sleep 15')
            else:
                scr.add('sleep 7')
            base_path = f'{self.args.map_name}\\IR_{zero_pad(i_time, self.args.n_times)}_{look_angle}\\'
            current_flag = f'IR_{zero_pad(i_time, self.args.n_times)}_{look_angle}'
            # insert_bbox_labels_store_code(self, scr, n_items, land_sea_item_pairs, base_path)
            insert_bbox_labels_store_code_inidbi2(self, scr, n_items, land_sea_item_pairs, base_path)
            insert_set_datetime_and_weather_code(self, scr, i_time)
            insert_capture_code(scr, base_path + current_flag, sleep=1)
            insert_end_flag_sign_code(scr, self.args.map_name + '\\DONE_' + current_flag)

        for _, look_angle in enumerate(self.args.look_angles):
            # insert_start_flag_sign_waiting_code(scr, f'{i_time}_{look_angle}_IR',
            #                                     sleep=(10 if _ == 0 else 1))
            insert_camera_creation_code(scr, cam_dic['cam_points'][_], self.args.fov)
            insert_camera_tilting_code(scr, cam_dic['target_points'][_], sleep=1)           
            # EO ->
            # insert_start_flag_sign_waiting_code(scr, f'{i_time}_{look_angle}_EO', sleep=2)
            scr.add('false setCamUseTI 0')  # activate EO
            base_path = f'{self.args.map_name}\\EO_{zero_pad(i_time, self.args.n_times)}_{look_angle}\\'
            current_flag = f'EO_{zero_pad(i_time, self.args.n_times)}_{look_angle}'
            # insert_bbox_labels_store_code(self, scr, n_items, land_sea_item_pairs, base_path)
            insert_bbox_labels_store_code_inidbi2(self, scr, n_items, land_sea_item_pairs, base_path)
            insert_set_datetime_and_weather_code(self, scr, i_time)
            insert_capture_code(scr, base_path + current_flag, sleep=1)
            insert_end_flag_sign_code(scr, self.args.map_name + '\\DONE_' + current_flag)
    insert_items_removal_code(scr, n_items)
    insert_start_simulation_code(scr)

def insert_set_datetime_and_weather_code(self, scr, i_time):
    # ref: https://community.bohemia.net/wiki/setRain
    dtime = self.timelines[i_time]
    weather = self.args.weather
    scr.add(f'setDate [{dtime.year}, {dtime.month}, {dtime.day}, {dtime.hour}, {dtime.minute}]')
    if weather in ['sunny']:
        scr.add('0 setOvercast 0; 0 setRain 0; 0 setFog 0; forceWeatherChange;')
    elif weather in ['rain', 'snow']:
        scr.add('0 setOvercast 1; 0 setRain 1; forceWeatherChange;')
    elif weather in ['overcast']:
        overcast_ratio = choice([0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
        scr.add(f'0 setOvercast {overcast_ratio}; 0 setRain 0; forceWeatherChange; 999999 setRain 0;')
        
def insert_camera_creation_code(scr, cam_point, fov=0.75):
    scr.add('showCinemaBorder false')
    scr.add(f'cam = "camera" camCreate [cx + {cam_point[0]}, cy + {cam_point[1]}, {cam_point[2]}]')
    scr.add(f'cam camSetFov {fov}')
    # default: 0.75 means if you have altitude of 120m then you can see 120*0.75=90m on your left/right
    
def insert_camera_tilting_code(scr, target_point, sleep=0.8):
    scr.add(f'cam camSetTarget [cx, cy, 0]')
    scr.add(f'cam cameraEffect ["Internal", "BACK"]')
    scr.add(f'cam camCommit 0')
    scr.add(f'sleep {sleep}')
    
def insert_bbox_labels_store_code(self, scr, n_items, land_sea_item_pairs=None, base_path='', sleep=0.0, delimeter='='):
    deli = f' + "{delimeter}" + '
    bbox_coordinates = ['str cx_2d', 'str cy_2d'] + [f'str {xy}{k}_2d' for k in range(1, 8+1) for xy in ['x', 'y']]
    for i in range(n_items):
        bbox = [f'typeOf my_var_{i}'] + bbox_coordinates
        # bbox = [f'typeOf my_var_{i}'] + bbox_coordinates + [f'"id_{i}"']
        # bbox_label = deli.join(bbox) + ' + "/dummy.png"'
        script_list = [f'''if (!(isNil "my_var_{i}")) then {{ if ( (alive my_var_{i}) ) then {{ 
            cx_3d = worldToScreen Position my_var_{i} select 0; 
            cy_3d = worldToScreen Position my_var_{i} select 1; 
            cx_2d = (cx_3d-SafeZoneX) / SafeZoneW * {self.args.screen_w}; 
            cy_2d = (cy_3d-SafeZoneY) / SafeZoneH * {self.args.screen_h}; 
            cx_2d = round cx_2d;            cy_2d = round cy_2d;
            maxPoint = (boundingBoxReal [my_var_{i}, "ViewGeometry"]) select 1; 
            localMaxX = maxPoint select 0;  localMaxY = maxPoint select 1;   localMaxZ = maxPoint select 2; 
            localMinX = -localMaxX;         localMinY = -localMaxY;          localMinZ = -localMaxZ; 
        '''] # isNil means var not defined or no value
        if self.args.invalid_bbox_df is not None and land_sea_item_pairs:
            for arma3_class in land_sea_item_pairs[i]:
                if arma3_class and arma3_class in list(self.args.invalid_bbox_df['arma3_class']):
                    output = self.args.invalid_bbox_df.query(f"(arma3_class == '{arma3_class}')")
                    t_x, t_y, t_z = output['t_x'].item(), output['t_y'].item(), output['t_z'].item()
                    s_x, s_y, s_z = output['s_x'].item(), output['s_y'].item(), output['s_z'].item()
                    script_list.append(f'''
                        if ( typeOf my_var_{i} == "{arma3_class}" ) then {{
                            localMaxX = {s_x} * localMaxX + {t_x};    localMinX = {s_x} * localMinX - {t_x};
                            localMaxY = {s_y} * localMaxY + {t_y};    localMinY = {s_y} * localMinY - {t_y};  
                            localMaxZ = {s_z} * localMaxZ + {t_z};    localMinZ = {s_z} * localMinZ - {t_z};
                        }};
                    ''')
        scaling_factor = 1
        script_list.append(f'''
            localMaxX = localMaxX * {scaling_factor}; localMaxY = localMaxY * {scaling_factor}; localMaxZ = localMaxZ * {scaling_factor};
            localMinX = localMinX * {scaling_factor}; localMinY = localMinY * {scaling_factor}; localMinZ = localMinZ * {scaling_factor};
        ''')
        script_list.append('''
            p1 = [localMaxX, localMaxY, localMaxZ];   p2 = [localMaxX, localMinY, localMinZ];
            p3 = [localMinX, localMinY, localMinZ];   p4 = [localMinX, localMaxY, localMaxZ]; 
            p5 = [localMaxX, localMaxY, localMinZ];   p6 = [localMaxX, localMinY, localMaxZ];            
            p7 = [localMinX, localMinY, localMaxZ];   p8 = [localMinX, localMaxY, localMinZ]; 
        ''')
        for j in range(8):
            script_list.append(f'''
                xy_3d = worldToScreen (my_var_{i} modelToWorldVisual p{j+1}); 
                if (count xy_3d > 0) then  {{
                x_3d = xy_3d select 0;              y_3d = xy_3d select 1; 
                x{j+1}_2d = (x_3d - SafeZoneX) / SafeZoneW * {self.args.screen_w}; 
                y{j+1}_2d = (y_3d - SafeZoneY) / SafeZoneH * {self.args.screen_h}; 
                x{j+1}_2d = round x{j+1}_2d;        y{j+1}_2d = round y{j+1}_2d; 
                }};
            ''')
        # __Intmain__
        # add script for saving visibility score using checkVisibility.
        # checkVisibility: check visibility from one point to another point
        # for AMOD, use center point of an model to check visibility
        # modify this code for better way to check visibility!        
        
        script_list.append(f'''my_var_{i}_cnt_intersect = 0;''')
        
        for j in range(8):
            script_list.append(f'''
                                my_var_{i}_p{j+1} = my_var_{i} modelToWorldVisualWorld p{j+1};
                                my_var_{i}_p{j+1}_intersect = lineIntersectsObjs [getPosASL cam, my_var_{i}_p{j+1}, my_var_{i}, objNull, true, 32];
                                my_var_{i}_cnt_intersect = my_var_{i}_cnt_intersect + count my_var_{i}_p{j+1}_intersect;
                                ''')
        
        script_list.append(f'''
            my_var_{i}_center = getPosASLVisual my_var_{i};
            my_var_{i}_intersect = lineIntersectsObjs [getPosASL cam, my_var_{i}_center, my_var_{i}, objNull, true, 32];
            my_var_{i}_cnt_intersect = my_var_{i}_cnt_intersect + count my_var_{i}_intersect;
            ''')
        bbox = bbox + [f'str(my_var_{i}_cnt_intersect)'] + [f'"id_{i}"']
        bbox_label = deli.join(bbox) + ' + "/dummy.png"'
        label_path = "\"" + base_path + "\" + " + bbox_label
        script_list.append(f'''
            screenshot ({label_path}); 
        }}; }}''')
        scr.add(f'sleep {sleep}')
        scr.add(' \n'.join(script_list))
        
def insert_capture_code(scr, current_flag, sleep=0.01):
    scr.add(f'screenshot "{current_flag}.png"', f'sleep {sleep}')
    # scr.add(f'screenshot "okay.png"')
    
def insert_end_flag_sign_code(scr, tag='', sleep=1):
    scr.add(f'sleep {sleep}')  # I don't know the reason but when rainy, this code is definitely needed
    scr.add(f'screenshot "{tag}\dummy.png"')
    # scr.add(f'sleep {sleep}')
    # scr.add(f'screenshot "DONE__{tag}\dummy.png"')
    
def insert_items_removal_code(scr, n_items):
    for i in range(n_items):
        scr.add(f'''if (!(isNil "my_var_{i}")) then {{deleteVehicle my_var_{i}}}''')
        
def insert_bbox_labels_store_code_inidbi2(self, scr, n_items, land_sea_item_pairs=None, base_path='', sleep=0.0, delimeter='='):
    deli = f' + "{delimeter}" + '
    bbox_coordinates = ['str cx_2d', 'str cy_2d'] + [f'str {xy}{k}_2d' for k in range(1, 8+1) for xy in ['x', 'y']]   
    for i in range(n_items):
        bbox = [f'typeOf my_var_{i}'] + bbox_coordinates
        # bbox = [f'typeOf my_var_{i}'] + bbox_coordinates + [f'"id_{i}"']
        # bbox_label = deli.join(bbox) + ' + "/dummy.png"'
        script_list = [f'''if (!(isNil "my_var_{i}")) then {{ if ( (alive my_var_{i}) ) then {{ 
            cx_3d = worldToScreen Position my_var_{i} select 0; 
            cy_3d = worldToScreen Position my_var_{i} select 1; 
            cx_2d = (cx_3d-SafeZoneX) / SafeZoneW * {self.args.screen_w}; 
            cy_2d = (cy_3d-SafeZoneY) / SafeZoneH * {self.args.screen_h}; 
            cx_2d = round cx_2d;            cy_2d = round cy_2d;
            maxPoint = (boundingBoxReal [my_var_{i}, "ViewGeometry"]) select 1; 
            localMaxX = maxPoint select 0;  localMaxY = maxPoint select 1;   localMaxZ = maxPoint select 2; 
            localMinX = -localMaxX;         localMinY = -localMaxY;          localMinZ = -localMaxZ; 
        '''] # isNil means var not defined or no value
        if self.args.invalid_bbox_df is not None and land_sea_item_pairs:
            for arma3_class in land_sea_item_pairs[i]:
                if arma3_class and arma3_class in list(self.args.invalid_bbox_df['arma3_class']):
                    output = self.args.invalid_bbox_df.query(f"(arma3_class == '{arma3_class}')")
                    t_x, t_y, t_z = output['t_x'].item(), output['t_y'].item(), output['t_z'].item()
                    s_x, s_y, s_z = output['s_x'].item(), output['s_y'].item(), output['s_z'].item()
                    script_list.append(f'''
                        if ( typeOf my_var_{i} == "{arma3_class}" ) then {{
                            localMaxX = {s_x} * localMaxX + {t_x};    localMinX = {s_x} * localMinX - {t_x};
                            localMaxY = {s_y} * localMaxY + {t_y};    localMinY = {s_y} * localMinY - {t_y};  
                            localMaxZ = {s_z} * localMaxZ + {t_z};    localMinZ = {s_z} * localMinZ - {t_z};
                        }};
                    ''')
        scaling_factor = 1
        script_list.append(f'''
            localMaxX = localMaxX * {scaling_factor}; localMaxY = localMaxY * {scaling_factor}; localMaxZ = localMaxZ * {scaling_factor};
            localMinX = localMinX * {scaling_factor}; localMinY = localMinY * {scaling_factor}; localMinZ = localMinZ * {scaling_factor};
        ''')
        script_list.append('''
            p1 = [localMaxX, localMaxY, localMaxZ];   p2 = [localMaxX, localMinY, localMinZ];
            p3 = [localMinX, localMinY, localMinZ];   p4 = [localMinX, localMaxY, localMaxZ]; 
            p5 = [localMaxX, localMaxY, localMinZ];   p6 = [localMaxX, localMinY, localMaxZ];            
            p7 = [localMinX, localMinY, localMaxZ];   p8 = [localMinX, localMaxY, localMinZ]; 
        ''')
        for j in range(8):
            script_list.append(f'''
                xy_3d = worldToScreen (my_var_{i} modelToWorldVisual p{j+1}); 
                if (count xy_3d > 0) then  {{
                x_3d = xy_3d select 0;              y_3d = xy_3d select 1; 
                x{j+1}_2d = (x_3d - SafeZoneX) / SafeZoneW * {self.args.screen_w}; 
                y{j+1}_2d = (y_3d - SafeZoneY) / SafeZoneH * {self.args.screen_h}; 
                x{j+1}_2d = round x{j+1}_2d;        y{j+1}_2d = round y{j+1}_2d; 
                }};
            ''')
        # __Intmain__
        # add script for saving visibility score using checkVisibility.
        # checkVisibility: check visibility from one point to another point
        # for AMOD, use center point of an model to check visibility
        # modify this code for better way to check visibility!        
        
        script_list.append(f'''my_var_{i}_cnt_intersect = 0;''')
        
        for j in range(8):
            script_list.append(f'''
                                my_var_{i}_p{j+1} = my_var_{i} modelToWorldVisualWorld p{j+1};
                                my_var_{i}_p{j+1}_intersect = lineIntersectsObjs [getPosASL cam, my_var_{i}_p{j+1}, my_var_{i}, objNull, true, 32];
                                my_var_{i}_cnt_intersect = my_var_{i}_cnt_intersect + count my_var_{i}_p{j+1}_intersect;
                                ''')
        
        script_list.append(f'''
            my_var_{i}_center = getPosASLVisual my_var_{i};
            my_var_{i}_intersect = lineIntersectsObjs [getPosASL cam, my_var_{i}_center, my_var_{i}, objNull, true, 32];
            my_var_{i}_cnt_intersect = my_var_{i}_cnt_intersect + count my_var_{i}_intersect;
            ''')
        bbox = bbox + [f'str(my_var_{i}_cnt_intersect)'] + [f'"id_{i}"']
        bbox_label = deli.join(bbox) + ' + "/dummy.png"'
        label_path = "\"" + base_path + "\" + " + bbox_label
        

        
        keys = ['cx_2d', 'cy_2d'] + [f'{xy}{k}_2d' for k in range(1, 9) for xy in ['x', 'y']]
        
        base_path_wo_sl = base_path.replace('\\', '_')
        
        script_list.append(f'_inidbi = ["new", "{base_path_wo_sl}"] call OO_INIDBI;sleep 0.01;')
        script_list.append(f'diag_log ("inidbi works? " + str ("exists" call _inidbi));')
        for key in keys:
            script_list.append(f'["write", ["id_{i}", "{key}", {key}]] call _inidbi; sleep 0.01;')
        script_list.append(f'["write", ["id_{i}", "arma3_class", typeof my_var_{i}]] call _inidbi; sleep 0.01;')
        script_list.append(f'["write", ["id_{i}", "intersect_count", my_var_{i}_cnt_intersect]] call _inidbi; sleep 0.01;')
        # script_list.append(f'["write", [typeOf my_var_{i}, "id", {i}]] call _inidbi; sleep 0.01;')
        
        
        script_list.append(f'''
            // screenshot ({label_path}); 
        }}; }}''')
        
        scr.add(f'sleep {sleep}')
        scr.add(' \n'.join(script_list))