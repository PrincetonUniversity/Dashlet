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

def run():
    userid = input("Enter user id: ")

    netsetting = input("Enter network setting: ")

    expname = f"tt-{userid}-{netsetting}"

    configs = {
        "exp_name": expname,
        "iterations": 50
    }

    dumpfolder = "../data/" + expname
    if os.path.exists(dumpfolder) == False:
        os.system("mkdir " + dumpfolder)

    with open('../config.json', 'w') as outfile:
        json.dump(configs, outfile)

    configurations = configs

    exp_name = configurations["exp_name"]

    fd = open(f"../data/{exp_name}/{exp_name}-start-time.log", "w")

    proc_proxy = subprocess.Popen(
        [
            "mm-link",
            "../traces/network.up",
            f"../traces/user-study/trace-{netsetting}.down",
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


    proc_swipe = subprocess.Popen(
        [
            "sh",
            "../scripts/record_touch_events.sh"
        ]
    )

    child_pid = proc_swipe.pid
    atexit.register(kill_child, cpid=child_pid)

    (out, err) = proc_swipe.communicate()


    os.system("echo qwertyui | sudo -S pkill -9 mitmdump")


if __name__ == '__main__':
    run()
