import os
import subprocess
import time
import atexit


def kill_child(cpid):
    if cpid is None:
        pass
    else:
        os.kill(cpid, signal.SIGTERM)




proc = subprocess.Popen(["../tool/mitmdump", "-p", "9989", "--allow-hosts", "www.baidu.com"],
    # stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )

child_pid = proc.pid
atexit.register(kill_child, cpid=child_pid)

(out, err) = proc.communicate()


# os.system("../tool/mitmdump -p 9989 -s ../tool/pre_parse.py")