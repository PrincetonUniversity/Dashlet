from flask import Flask, render_template, jsonify, current_app, request
from flask_cors import CORS

import time

import argparse
import os
import sys
from DbHandler import DbHandler


this_folder_path = os.path.dirname(os.path.abspath(__file__))

sys.path.append(this_folder_path + '/../util')

import traceparser


app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

dbHandler = DbHandler()

next_vid_dict = {}
pre_vid_dict = {}


data_folder_path = this_folder_path + "/../reverse-tiktok/data/"


def getNextvidByTrace(tid, vid):
    if tid in next_vid_dict.keys():
        if vid in next_vid_dict[tid].keys():
            return next_vid_dict[tid][vid]
    return ""


def getPrevidByTrace(tid, vid):
    if tid in pre_vid_dict.keys():
        if vid in pre_vid_dict[tid].keys():
            return pre_vid_dict[tid][vid]
    return ""

def getNextvid(vid):
    return dbHandler.queryNext(vid)

def getPrevid(vid):
    return dbHandler.queryPre(vid)


@app.route('/svsd')
def json():
    return render_template('index-datacollection.html')


@app.route('/svs')
def svs():
    traceid = request.args.get('traceid')
    print("traceid: " + traceid)

    pparser = traceparser.playtraceparser()
    filepath = data_folder_path + traceid + "/" + traceid + "-play.csv"
    pparser.parse(filepath)
    uri_list = pparser.get_uri_list()

    next_vid_dict[traceid] = {}

    next_vid_dict[traceid]["startvideo"] = uri_list[0]

    for i in range(1, len(uri_list)):
        next_vid_dict[traceid][uri_list[i-1]] = uri_list[i]

    
    pre_vid_dict[traceid] = {}
    pre_vid_dict[traceid]["startvideo"] = uri_list[-1]
    pre_vid_dict[traceid][uri_list[0]] = "startvideo"

    for i in range(1, len(uri_list)):
        pre_vid_dict[traceid][uri_list[i]] = uri_list[i-1]

    return render_template('index-exp.html', serverip=app.config['serverip'])

#background process happening without any refreshing
@app.route('/background_process_test')
def background_process_test():
    print ("Hello")
    return jsonify(username="zhuqi")



@app.route('/postmethod')
def postmethod():
    jsdata = request.args.get('vid', 0, type=str)
    return jsonify(result="server: "+ jsdata)

@app.route('/getnext')
def getnext():
    vid = request.args.get('vid', 0, type=str)

    traceid = request.args.get('traceid', type=str)

    if traceid != None:
        return jsonify(result=getNextvidByTrace(traceid, vid))

    return jsonify(result=getNextvid(vid))

@app.route('/uploadPlayback')
def uploadPlayback():
    duration = request.args.get('duration', 0, type=str)
    playbackTime = request.args.get('currentTime', 0, type=str)
    vid = request.args.get('vid', 0, type=str)

    print(vid)
    print(duration)
    print(playbackTime)
    print(request.remote_addr)
    curtime = time.time()
    formattime = time.ctime(curtime)
    print(curtime)
    print(formattime)

    dbHandler.saveData(request.remote_addr, vid, duration, playbackTime, curtime, formattime)
    
    return jsonify(result=0)

@app.route('/getpre')
def getpre():
    jsdata = request.args.get('vid', 0, type=str)
    return jsonify(result=getPrevid(jsdata))

@app.route('/getNeighbour')
def getNeighbour():
    jsdata = request.args.get('vid', 0, type=str)
    ret = {}

    traceid = request.args.get('traceid', type=str)

    if traceid != None:
        ret["uidPre"] = getPrevidByTrace(traceid, jsdata)
        ret["uidNext"] = getNextvidByTrace(traceid, jsdata)
        print(ret["uidNext"])
        return jsonify(ret)

    ret["uidPre"] = getPrevid(jsdata)
    ret["uidNext"] = getNextvid(jsdata)
    print(ret["uidNext"])
    return jsonify(ret)

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--serverip', default="127.0.0.1")

    args = parser.parse_args()


    app.config['serverip'] = args.serverip

    app.run(port=5000, debug=True, host="0.0.0.0")