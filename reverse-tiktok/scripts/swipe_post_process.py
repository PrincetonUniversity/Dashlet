import subprocess
import datetime
import sys
import csv
import os
import argparse
import json

def main(args):

    event_idx = -1
    event_list = []

    event_decomposed = []

    cdf = open("../config.json")
    configurations = json.load(cdf)
    cdf.close()

    exp_name = configurations["exp_name"]

    fd = open(f"../data/{exp_name}/{exp_name}-swipe-time.log", "w")

    with open(args.tracename) as fp:

        Lines = fp.readlines()
        for line in Lines:
            
            items = line.split()

            if items[3] == "BTN_TOUCH" and items[4] == "DOWN":
                
                event_list.append([])
                event_idx += 1

                continue

            if items[3] == "BTN_TOUCH" and items[4] == "UP":

                continue


            if items[3] == "ABS_MT_POSITION_X" or items[3] == "ABS_MT_POSITION_Y":

                ts = float(items[1].strip("]"))
                event_list[event_idx].append([ts, items[3], int(items[4], 16)])

    for event in event_list:
        # print(event)

        event_decomposed.append({})


        for i in range(len(event)):
            if event[i][1] == "ABS_MT_POSITION_X":
                event_decomposed[-1]["startx"] = event[i][2]
                event_decomposed[-1]["startt"] = event[i][0]
                break

        for i in range(len(event)):
            if event[i][1] == "ABS_MT_POSITION_Y":
                event_decomposed[-1]["starty"] = event[i][2]
                break

        for i in reversed(range(len(event))):
            if event[i][1] == "ABS_MT_POSITION_X":
                event_decomposed[-1]["endx"] = event[i][2]
                event_decomposed[-1]["endt"] = event[i][0]
                break

        for i in reversed(range(len(event))):
            if event[i][1] == "ABS_MT_POSITION_Y":
                event_decomposed[-1]["endy"] = event[i][2]
                break

        # print(event_decomposed[-1])

        fd.write(f"{event_decomposed[-1]['startt']} {event_decomposed[-1]['startx']} {event_decomposed[-1]['starty']} {event_decomposed[-1]['endt']} {event_decomposed[-1]['endx']} {event_decomposed[-1]['endy']}\n")

        # event_decomposed[-1][]

    fd.close()




if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--tracename', default="../scripts/recorded_touch_events.txt", help='Raw swipe trace')

    args = parser.parse_args()
    main(args)