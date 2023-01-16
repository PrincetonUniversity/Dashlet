#!/bin/bash

# echo "Looking for touchscreen device..."
TOUCH_DEVICE=`../scripts/find_touchscreen_name.sh`

echo "$TOUCH_DEVICE"
adb shell getevent -lt "${TOUCH_DEVICE#*-> }" > ../scripts/recorded_touch_events.txt