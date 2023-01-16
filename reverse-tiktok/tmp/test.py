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

    # proc_tcpdump = subprocess.Popen(
    #     "sudo tcpdump > dump.txt", shell=True, stdin=subprocess.PIPE
    # )
    #
    # print("tset point 1")
    #
    # proc_tcpdump.communicate(input=b'qwertyui\n')
    #
    # print("tset point 2")

    # fd = open("dump.txt", "w")

    sudoPassword = 'qwertyui'
    command = 'sudo -S tcpdump -w dump.txt'.split()

    cmd1 = subprocess.Popen(['echo', sudoPassword], stdout=subprocess.PIPE)
    proc_tcpdump = subprocess.Popen(command, stdin=cmd1.stdout)

    tcpdump_pid = proc_tcpdump.pid
    # atexit.register(kill_child, cpid=tcpdump_pid)


    # echo qwertyui | sudo -S tcpdump > dump.txt

    # enter the app

    # "echo qwertyui | sudo -S tcpdump > dump.txt"

    time.sleep(15)

    os.system("echo qwertyui | sudo -S pkill -9 tcpdump")

    # fd.close()

    # (out, err) = proc_ui_start.communicate()



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--networktrace', default="../traces/network/trace-3.0.down", help='Viewing trace')
    parser.add_argument('--swipetrace', default="../traces/swipe/swipe-2.txt", help='The network trace')
    # parser.add_argument('--probabilitytraces', default='./data', help='The path to save processed data')

    args = parser.parse_args()
    run(args)
