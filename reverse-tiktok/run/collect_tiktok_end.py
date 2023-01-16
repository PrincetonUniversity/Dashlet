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

    cdf = open("../config.json")
    configurations = json.load(cdf)
    cdf.close()

    exp_name = configurations["exp_name"]

    # exit and clear cache
    proc_download = subprocess.Popen(
        [
            "python3",
            "../scripts/download.py"
        ]
    )
    (out, err) = proc_download.communicate()


    # exit and clear cache
    proc_parse_swpie = subprocess.Popen(
        [
            "python3",
            "../scripts/swipe_post_process.py"
        ]
    )
    (out, err) = proc_parse_swpie.communicate()

    os.system("echo qwertyui | sudo -S pkill -9 mitmdump")


if __name__ == '__main__':
    run()
