from .my_parser import *
from .my_util import *
from .my_scene_generator.my_scene_generator import *
from .my_clean_bot.my_clean_bot import *

list_options = {
    'weathers': ['sunny', 'rain', 'overcast', 'snow'],
    'map_names': ['altis', 'livonia', 'malden2035', 'stratis', 'tanoa', 'weferlingen', 'weferlingen_winter', 'VR',
                  'bukovina', 'bystrica', 'chernarus_autumn', 'chernarus_summer', 'chernarus_winter',
                  'everon', 'kolgujev', 'malden', 'nogova', 'proving_grounds', 'sahrani', 'shapur',
                  'southern_sahrani', 'takistan', 'takistan_mountains', 'united_sahrani'],
    'camera_movings': ['air_to_air', 'air_to_land'],
    # DO NOT USE '_' in string for the list 'modes'  e.g. A3_TI (X) -> A3TI (O)
    'modes': ['EO',              # ARMA3 Default
              'IR-EO',           # IR-EO
              'IR'],             # ARMA3 Default Thermal Vision
    'samplings': ['100%', '200%', '300%', '400%', '500%', '600%',
                  '50%', '67%', '75%', '80%', '83%', '88%', '114%', '120%', '125%', '133%', '150%']
}

dict_options = {
    'world_sizes': {'altis': 30720, 'livonia': 12800, 'malden2035': 8192, 'stratis': 8192,
                    'tanoa': 15360, 'weferlingen': 20480, 'weferlingen_winter': 20480,
                    'bukovina': 3840, 'bystrica': 7680, 'chernarus_autumn': 15360,
                    'chernarus_summer': 15360, 'chernarus_winter': 15360, 'everon': 12800,
                    'kolgujev': 12800, 'malden': 12800, 'nogova': 12800, 'proving_grounds': 2048,
                    'sahrani': 20480, 'shapur': 2048, 'southern_sahrani': 10240,
                    'takistan': 12800, 'takistan_mountains': 6400, 'united_sahrani': 20480},
    'land_probs': {'altis': 1, 'livonia': 1, 'malden2035': 0.7, 'stratis': 0.5,
                   'tanoa': 0.7, 'weferlingen': 1, 'weferlingen_winter': 1,
                   'bukovina': 1, 'bystrica': 1, 'chernarus_autumn': 0.9,
                   'chernarus_summer': 0.9, 'chernarus_winter': 0.9, 'everon': 0.5,
                   'kolgujev': 0.4, 'malden': 0.4, 'nogova': 0.7, 'proving_grounds': 1,
                   'sahrani': 0.4, 'shapur': 1, 'southern_sahrani': 0.5,
                   'takistan': 1, 'takistan_mountains': 1, 'united_sahrani': 0.4},
    # 'months': {'altis': 6, 'livonia': 6, 'malden2035': 6, 'stratis': 6,
    #            'tanoa': 6, 'weferlingen': 6, 'weferlingen_winter': 6,
    #            'bukovina': 6, 'bystrica': 6, 'chernarus_autumn': 6,
    #            'chernarus_summer': 6, 'chernarus_winter': 6, 'everon': 6,
    #            'kolgujev': 6, 'malden': 6, 'nogova': 6, 'proving_grounds': 6,
    #            'sahrani': 6, 'shapur': 6, 'southern_sahrani': 6,
    #            'takistan': 6, 'takistan_mountains': 6, 'united_sahrani': 6},
    'scenario_randomly_scattered': {'min_class_num': 2, 'max_class_num': 8,
                                    'min_item_num': 8},  # 'max_item_num' calculated automatically
}
