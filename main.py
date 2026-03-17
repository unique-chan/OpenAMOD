import traceback

from src import *

try:
    args = Parser(list_options, dict_options).parse_args()
    sg = SceneGenerator(args)
    cb = CleanBot(sg)
    prepare_to_start(args)
    write_scenarios(sg)
    play_scenarios(args, cb)
    prepare_to_end(args)
except Exception as e:
    print('Error:', e)
    traceback.print_exc()
finally:
    #if args.resume_scene_idx == 0:
    input('\n🔒 Press any key to exit: ')
