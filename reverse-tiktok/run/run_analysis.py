import os
import signal
import subprocess
import time
import atexit
import argparse
import json

def kill_child(cpid):
    if cpid is None:
        pass
    else:
        os.kill(cpid, signal.SIGTERM)

def run(args):

    cdf = open("../config.json")
    configurations = json.load(cdf)
    cdf.close()

    exp_name = configurations["exp_name"]

    fd = open(f"../data/{exp_name}/{exp_name}-start-time.log", "w")

    proc_proxy = subprocess.Popen(
        [
            "mm-link",
            "../traces/network.up",
            args.networktrace,
            "--downlink-queue=droptail",
            '--downlink-queue-args="bytes=150000"',
            "--uplink-queue=infinite",
            "python",
            "../tool/run_proxy.py"
        ]
    )

    fd.write(str(time.time()))
    fd.close()

    child_pid = proc_proxy.pid
    atexit.register(kill_child, cpid=child_pid)

    time.sleep(2)

    # enter the app
    proc_ui_start = subprocess.Popen(
        [
            "python3",
            "../app-handler/play.py",
            "startaccount",
            "1"
        ]
    )
    (out, err) = proc_ui_start.communicate()




    # proc_rebuffer = subprocess.Popen(
    #     [
    #         "python3",
    #         "../scripts/determine_buffer.py"
    #     ]
    # )
    # child_pid = proc_rebuffer.pid
    # atexit.register(kill_child, cpid=child_pid)



    # swipe 
    proc_swipe = subprocess.Popen(
        [
            "python3",
            "../scripts/swipe_trace.py",
            "--swipetrace",
            args.swipetrace
        ]
    )
    (out, err) = proc_swipe.communicate()



    # exit and clear cache
    proc_ui_end = subprocess.Popen(
        [
            "python3",
            "../app-handler/play.py",
            "end",
            "1"
        ]
    )
    (out, err) = proc_ui_end.communicate()



    # exit and clear cache
    proc_download = subprocess.Popen(
        [
            "python3",
            "../scripts/download.py"
        ]
    )
    (out, err) = proc_download.communicate()

    os.system("echo qwertyui | sudo -S pkill -9 mitmdump")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--networktrace', default="../traces/network/trace-3.0.down", help='Viewing trace')
    parser.add_argument('--swipetrace', default="../traces/swipe/swipe-2.txt", help='The network trace')
    # parser.add_argument('--probabilitytraces', default='./data', help='The path to save processed data')

    args = parser.parse_args()
    run(args)
