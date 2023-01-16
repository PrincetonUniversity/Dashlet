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

    fd = open(f"./start-time.log", "w")

    proc_proxy = subprocess.Popen(
        [
            "mm-link",
            "../traces/network.up",
            "../traces/4.5.down",
            "--downlink-queue=droptail",
            '--downlink-queue-args="bytes=150000"',
            "--uplink-queue=infinite",
            "python",
            "../tool/run_proxy.py"
        ]
    )

    fd.write(str(time.time()))
    fd.close()

    fd = open(f"./start-tcpdump.log", "w")
    fd.write(str(time.time()))
    fd.close()

    os.system("sudo tcpdump -nS > trace.txt")

    (out, err) = proc_proxy.communicate()

    child_pid = proc_proxy.pid
    atexit.register(kill_child, cpid=child_pid)

    # os.system("echo qwertyui | sudo -S pkill -9 mitmdump")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--networktrace', default="../traces/network/trace-4.5.down", help='Viewing trace')
    parser.add_argument('--swipetrace', default="../traces/swipe/swipe-2.txt", help='The network trace')
    # parser.add_argument('--probabilitytraces', default='./data', help='The path to save processed data')

    args = parser.parse_args()
    run(args)
