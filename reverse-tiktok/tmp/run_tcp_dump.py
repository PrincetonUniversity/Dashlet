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

    fd = open(f"./start-tcpdump.log", "w")
    fd.write(str(time.time()))
    fd.close()

    os.system("sudo tcpdump -nS src port 9989 and dst 10.8.57.38 > trace.txt")


if __name__ == '__main__':
    run()
