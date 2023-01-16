import os
import signal
import subprocess
import time
import atexit
import json
import atexit
import argparse

def kill_child(cpid):
    if cpid is None:
        pass
    else:
        os.kill(cpid, signal.SIGTERM)


def run(networkfoler, swipefoler):

    networkfiles = os.listdir(networkfoler)
    swipefiles = os.listdir(swipefoler)

    networkfiles.sort()
    swipefiles.sort()

    print(networkfiles)
    print(swipefiles)


    for networkfile in networkfiles:
        for swipefile in swipefiles:

            expname = networkfile.strip(".down") + "-" + swipefile.strip(".txt")

            dumpfolder = "../data/" + expname
            if os.path.exists(dumpfolder) == False:
                os.system("mkdir " + dumpfolder)

            else:

                print(dumpfolder)

                continue


            configs = {
                "exp_name": expname,
                "iterations": 50
            }

            with open('../config.json', 'w') as outfile:
                json.dump(configs, outfile)


            proc_run = subprocess.Popen(
                [
                    "python3",
                    "run_analysis.py",
                    "--networktrace",
                    networkfoler + networkfile,
                    "--swipetrace",
                    swipefoler + swipefile,
                ]
            )


            child_pid = proc_run.pid
            atexit.register(kill_child, cpid=child_pid)
            
            (out, err) = proc_run.communicate()






if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--networktrace', default="../traces/network/", help='Viewing trace')
    parser.add_argument('--swipetrace', default="../traces/swipe/", help='The network trace')
    # parser.add_argument('--probabilitytraces', default='./data', help='The path to save processed data')

    args = parser.parse_args()
    run(args.networktrace, args.swipetrace)
