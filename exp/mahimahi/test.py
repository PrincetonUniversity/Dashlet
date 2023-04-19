print("test")


import subprocess
import time

# Start the subprocess
process = subprocess.Popen(['ping', 'www.google.com'])

# Wait for 1 second
time.sleep(3)

# Terminate the subprocess
process.terminate()