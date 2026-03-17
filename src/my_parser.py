from argparse import ArgumentParser
from glob import glob
from datetime import datetime

from pandas import read_csv
from os import path


class Parser:
    def __init__(self, parser_list_type_options, parser_dict_type_options):
        self.parser = ArgumentParser()
        self.parser_list_type_options = parser_list_type_options
        self.parser_dict_type_options = parser_dict_type_options
        self.add_arguments()

    def add_arguments(self):
        self.parser.add_argument('-weather', type=str, help=f"option: {self.parser_list_type_options['weathers']}")
        self.parser.add_argument('-map_name', type=str, help="e.g. 'altis'")
        self.parser.add_argument('-arma_root_path', type=str, help="e.g. 'C:/Users/yechan/Documents/Arma 3'")
        self.parser.add_argument('-save_root_path', type=str, help="e.g. 'C:/Users/yechan/Desktop'")
        self.parser.add_argument('-class_path', type=str, help='e.g. classes/yechan/CLASSES.csv')
        self.parser.add_argument('-invalid_bbox_path', default='', type=str,
                                 help='e.g. classes/yechan/INVALID_BBOX.csv')
        self.parser.add_argument('-start_hour', default=6, type=int, help='e.g. 6')
        self.parser.add_argument('-end_hour', default=18, type=int, help='e.g. 18')
        self.parser.add_argument('-n_times', default=10, type=int, help='e.g. 1000')
        self.parser.add_argument('-resume_scene_idx', default=0, type=int, help='e.g. 0')
        self.parser.add_argument('-batch_size', default=1, type=int, help='e.g. 10')
        self.parser.add_argument('-z_atl', default=120, type=int, help='hint. [VGA & z_atl=120] -> 0.3m/pixel')
        self.parser.add_argument('-spatial_resolution', default=0.3, type=float, help='default: 0.3m/pixel')
        self.parser.add_argument('-screen_h', default=480, type=int, help='e.g. 480')
        self.parser.add_argument('-screen_w', default=640, type=int, help='e.g. 640')
        self.parser.add_argument('-look_angle_min', default=-60, type=int, help='e.g. -60')
        self.parser.add_argument('-look_angle_max', default=60, type=int, help='e.g. 60')
        self.parser.add_argument('-look_angle_interval', default=10, type=int, help='e.g. 10')
        self.parser.add_argument('-camera_moving', default='air_to_air', type=str,
                                 help=f"option: {self.parser_list_type_options['camera_movings']}")
        self.parser.add_argument('-mode', default='EO', type=str,
                                 help=f"imagery type -> option: {self.parser_list_type_options['modes']}")
        self.parser.add_argument('-data_creation_only', action='store_true',
                                 help='if you want to build data with already created scenarios -> '
                                      'this option will disable prepare_to_start() and write_scenarios()!')
        self.parser.add_argument('-date', default='2024-06-06', type=str,
                                 help='Date in ARMA3, Format: "YYYY-MM-dd" (e.g. "2024-06-01")')
        self.parser.add_argument('-fov', default=0.8, type=float,
                                 help='ARMA3 Camera FOV (e.g. 0.75)')
        self.parser.add_argument('-via_gui', action='store_true',
                                 help='do not use this option by yourselves')
        self.parser.add_argument('-sampling', default='100%', type=str,
                                 help='e.g. 640x480 & 200% -> 1280x960 (200% Higher Graphic Quality)')

    def parse_args(self):
        args, bool_error = self.check(self.parser.parse_args())
        if bool_error:
            print(args)
            exit(-1)
        try:
            args.class_structure_df = read_csv(args.class_path)
        except Exception as e:
            print(f'Error on reading Class csv files.\nError message: {e}')
            exit(-1) 
        args.class_structure_df['arma3_class'] = args.class_structure_df['arma3_class'].str.lower()
        args.list_options = self.parser_list_type_options
        args.dict_options = self.parser_dict_type_options
        args.buffer_path = f'{args.arma_root_path}/Screenshots'
        # for force-rerun ->
        args.screen_h_original, args.screen_w_original = args.screen_h, args.screen_w
        args.spatial_resolution_original = args.spatial_resolution
        if args.sampling != '100%':
            args.screen_h = round(int(args.screen_h) * (int(args.sampling[:-1])/100))
            args.screen_w = round(int(args.screen_w) * (int(args.sampling[:-1])/100))
            args.spatial_resolution = round(float(args.spatial_resolution) / (int(args.sampling[:-1])/100), 2)
        args.save_path = f'{args.save_root_path}/{args.mode}_{args.map_name}_{args.weather}_' \
                        f'{args.start_hour:02d}_{args.end_hour:02d}_{datetime.now().strftime("%y%m%d_%H%M%S")}'
        args.invalid_bbox_df = read_csv(args.invalid_bbox_path) if args.invalid_bbox_path else None
        args.plane_h = int(0.7 * args.screen_h * args.spatial_resolution)
        args.plane_w = int(0.7 * args.screen_w * args.spatial_resolution)
        args.look_angles = tuple(range(args.look_angle_min, args.look_angle_max + 1, args.look_angle_interval))
        try:
            args.mission_path = (lambda x, y: glob(f'{x}/{y}*')[0])(f'{args.arma_root_path}/missions', args.map_name)
        except:
            print(f'You need to make a mission file for `{args.map_name}` before running this code!')
            exit(-1)
        return args

    def check(self, args):
        bool_error = False
        try:
            assert args.weather in self.parser_list_type_options['weathers'], \
                f"Invalid weather {args.weather}, supported: {self.parser_list_type_options['weather']}"
            assert args.map_name in self.parser_list_type_options['map_names'], \
                f"Invalid map {args.map_name}, supported: {self.parser_list_type_options['map_names']}"
            assert path.isdir(args.arma_root_path), f'Invalid ARMA root path: {args.arma_root_path}'
            assert path.isfile(args.class_path), f'No class file exists: {args.class_path}'
            assert path.isfile(args.invalid_bbox_path) if args.invalid_bbox_path else True, \
                f'No invalid bbox file exists: {args.invalid_bbox_path}'
            assert args.start_hour < args.end_hour, 'Check args.start_hour < args.end_hour'
            assert 0 <= args.start_hour <= 23 and 0 <= args.end_hour <= 23, \
                'Check 0 <= args.start_hour <= 23 and 0 <= args.end_hour <= 23'
            assert 1 <= args.batch_size <= args.n_times, 'Check 1 <= args.batch_size <= args.n_times'
            assert args.z_atl > 0, 'Check args.z_atl > 0'
            assert args.screen_h >= 1 and args.screen_w >= 1, 'Check args.screen_h >= 1 and args.screen_w >= 1'
            assert args.spatial_resolution > 0, 'Check args.spatial_resolution > 0'
            assert args.look_angle_min <= args.look_angle_max and args.look_angle_interval > 0, \
                'Check args.look_angle_min <= args.look_angle_max and args.look_angle_interval > 0'
            assert args.camera_moving in self.parser_list_type_options['camera_movings'], \
                (f"Invalid camera moving {args.camera_moving}, "
                    f"supported: {self.parser_list_type_options['camera_movings']}")
            assert args.mode in self.parser_list_type_options['modes'], \
                f"Invalid imagery mode: {args.mode}, supported: {self.parser_list_type_options['modes']}"
            try:
                args.date = datetime.strptime(args.date, '%Y-%m-%d')
            except ValueError:
                raise f'Invalid date: {args.date}!'
        except Exception as e:
            bool_error = True
            print(e)
        finally:
            return args, bool_error
