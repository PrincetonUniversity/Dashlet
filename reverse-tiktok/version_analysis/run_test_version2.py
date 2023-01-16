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
            f"../traces/net-flat/trace-5.0.down",
            "--downlink-queue=droptail",
            '--downlink-queue-args="bytes=150000"',
            "--uplink-queue=infinite",
            "python",
            "../tool/run_proxy_pbuf.py"
        ]
    )

    fd.write(str(time.time()))
    fd.close()

    child_pid = proc_proxy.pid
    atexit.register(kill_child, cpid=child_pid)

    time.sleep(120)

    sudoPassword = 'qwertyui'
    command = 'sudo -S tcpdump -w dump.txt'.split()

    cmd1 = subprocess.Popen(['echo', sudoPassword], stdout=subprocess.PIPE)
    proc_tcpdump = subprocess.Popen(command, stdin=cmd1.stdout)

    # (out, err) = proc_ui_start.communicate()

    # enter the app
    # proc_ui_start = subprocess.Popen(
    #     [
    #         "python3",
    #         "../app-handler/play.py",
    #         "start_version_test.txt",
    #         "1"
    #     ]
    # )
    # (out, err) = proc_ui_start.communicate()

    # swipe 
    proc_swipe = subprocess.Popen(
        [
            "python3",
            "../scripts/swipe_trace_testversion.py",
            "--swipetrace",
            args.swipetrace
        ]
    )
    (out, err) = proc_swipe.communicate()

    os.system("echo qwertyui | sudo -S pkill -9 mitmdump")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--networktrace', default="../traces/network/trace-3.0.down", help='Viewing trace')
    parser.add_argument('--swipetrace', default="../traces/swipe/swipe-2.txt", help='The network trace')
    # parser.add_argument('--probabilitytraces', default='./data', help='The path to save processed data')

    args = parser.parse_args()
    run(args)
