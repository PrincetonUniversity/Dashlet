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


    proc_proxy = subprocess.Popen(
        [
            "mm-link",
            "../traces/network.up",
            f"../traces/user-study/trace-dashlet-{netsetting}.down",
            "--downlink-queue=droptail",
            '--downlink-queue-args="bytes=150000"',
            "--uplink-queue=infinite",
            "python",
            "../tool/run_proxy_vanilla.py"
        ]
    )

    child_pid = proc_proxy.pid
    atexit.register(kill_child, cpid=child_pid)

    (out, err) = proc_proxy.communicate()



if __name__ == '__main__':
    run()
