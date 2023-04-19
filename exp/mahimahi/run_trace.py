import argparse
import os
import sys
import signal
import time
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

from webdriver_manager.chrome import ChromeDriverManager

this_folder_path = os.path.dirname(os.path.abspath(__file__))

sys.path.append(this_folder_path + '/../../util')

import traceparser

# TO RUN: download https://pypi.python.org/packages/source/s/selenium/selenium-2.39.0.tar.gz
# run sudo apt-get install python-setuptools
# run sudo apt-get install xvfb
# after untar, run sudo python setup.py install
# follow directions here: https://pypi.python.org/pypi/PyVirtualDisplay to install pyvirtualdisplay

# For chrome, need chrome driver: https://code.google.com/p/selenium/wiki/ChromeDriver
# chromedriver variable should be path to the chromedriver
# the default location for firefox is /usr/bin/firefox and chrome binary is /usr/bin/google-chrome
# if they are at those locations, don't need to specify


def timeout_handler(signum, frame):
    raise Exception("Timeout")




def main(args):
    abr_server_script_path = this_folder_path + f"/../../abr-server/empc_server_dashlet_j.py"

    probability_distribution_path = this_folder_path + f"/../../abr-server/probability/lamda2/"

    cmd_abr_server = f"python3 {abr_server_script_path} --probabilitytraces {probability_distribution_path}"

    print(cmd_abr_server)

    process_abr_server = subprocess.Popen(cmd_abr_server.split())

    run_time= 2400

    # timeout signal
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(run_time + 30)

    exp_id = args.expid
    swipetracename = this_folder_path + f"/../../reverse-tiktok/data/{exp_id}/{exp_id}-swipe.log"

    sparser = traceparser.swipetraceparser()

    sparser.parse(swipetracename)

    watch_time = sparser.get_watch_time()

    s=Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-ssl-errors=yes')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--allow-insecure-localhost')
    # solve the cors issue
    options.add_argument('--disable-web-security')
    
    driver = webdriver.Chrome(service=s, options=options)
    driver.maximize_window()
    
    driver.get(f"http://{args.serverip}:5000/svs?traceid={args.expid}")
    time.sleep(5)

    # skip the init video
    driver.find_element(By.ID, 'nextbutton').click()
    time.sleep(5)

    for i in range(len(watch_time)):

        driver.find_element(By.ID, 'nextbutton').click()
        print("next")
        print(watch_time[i])
    
        time.sleep(watch_time[i])
   
    driver.save_screenshot('ss.png')
        
    driver.quit()

    process_abr_server.terminate()

    # display.stop()
    

# ip = sys.argv[1]
# abr_algo = sys.argv[2]
# run_time = int(sys.argv[3])
# process_id = sys.argv[4]
# trace_file = sys.argv[5]
# sleep_time = sys.argv[6]

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('--expid', default="trace-15.0-swipe-2", help='Experiment Id')
    parser.add_argument('--serverip', default="127.0.0.1", help='127.0.0.1 for local host and 100.64.0.1 for shell within mahimahi')

    args = parser.parse_args()

    main(args)


# sudo /usr/local/nginx/sbin/nginx
# sudo sysctl -w net.ipv4.ip_forward=1
# mm-link ../../reverse-tiktok/traces/network.up ../../reverse-tiktok/traces/net-flat/trace-5.0.down --downlink-queue=droptail --downlink-queue-args="bytes=150000" --uplink-queue=infinite
