# from flask import Flask
# app = Flask(__name__)
#
# @app.route('/')
# def hello():
#     return 'Welcome to My Watchlist!'

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS

import time


import os
from DbHandler import DbHandler

app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

dbHandler = DbHandler()
#
# nextdict = {}
# predict = {}
#
#
# # replace with data base in the future
# def buildDict():
#     ids = os.listdir("../contentServer/dash/data/")
#
#     print(ids[0])
#
#     nlen = len(ids)
#
#     for i in range(nlen):
#         idxi = i
#         idxj = (i+1) % nlen
#
#
#         nextdict[ids[idxi]] = ids[idxj]
#
#         predict[ids[idxj]] = ids[idxi]
#
# buildDict()

def getNext(vid):
    return dbHandler.queryNext(vid)

def getPre(vid):
    return dbHandler.queryPre(vid)


@app.route('/svsd')
def json():
    return render_template('index-datacollection.html')


@app.route('/svs')
def svs():
    return render_template('index-exp.html')

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
    jsdata = request.args.get('vid', 0, type=str)
    return jsonify(result=getNext(jsdata))

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
    # return jsonify(result=getNext(jsdata))

@app.route('/getpre')
def getpre():
    jsdata = request.args.get('vid', 0, type=str)
    return jsonify(result=getPre(jsdata))

@app.route('/getNeighbour')
def getNeighbour():
    jsdata = request.args.get('vid', 0, type=str)
    ret = {}
    # print("======================")
    # print(jsdata)
    ret["uidPre"] = getPre(jsdata)
    ret["uidNext"] = getNext(jsdata)
    print(ret["uidNext"])
    return jsonify(ret)