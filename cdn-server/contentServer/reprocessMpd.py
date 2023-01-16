import xml.etree.ElementTree as ET
from xml.etree import ElementTree as etree

import os


dataDir = "./dash/data/"
fileList = os.listdir(dataDir)

etree.register_namespace("", "urn:mpeg:dash:schema:mpd:2011")

# fileList = fileList[0:2]


print(fileList)

for folderName in fileList:

    if folderName[0] == ".":
        continue

    backmpd = dataDir + folderName + "/manifest-back.mpd"
    curmpd = dataDir + folderName + "/manifest.mpd"

    if os.path.exists(backmpd):
        os.system("rm "+backmpd)

    os.system("""mv %s %s"""%(curmpd, backmpd))


    tree = ET.parse(backmpd)
    root = tree.getroot()

    for i in range(len(root[1])):
        AdaptationSet = root[1][i]

        if (AdaptationSet.attrib['contentType'] != "video"):
            continue

        Representation = root[1][i][0]
        SegmentTemplate = root[1][i][0][0]
        SegmentTimeline = root[1][i][0][0][0]

        timescale = int(SegmentTemplate.attrib['timescale'])
        duration = int(SegmentTimeline[0].attrib['d'])

        count = 1
        if 'r' in SegmentTimeline[0].attrib.keys():
            count += int(SegmentTimeline[0].attrib['r'])

        # chunk length in seconds
        chunkLength = duration/timescale

        bitrate_max = 0
        for j in range(1, count+1):

            fileName = dataDir+folderName+"/"+"""chunk-stream%d-%05d.m4s""" % (i, j)

            fsize = os.path.getsize(fileName)

            bitrate = fsize * 8 / chunkLength

            bitrate_max = max(bitrate_max, bitrate)

        root[1][i][0].attrib['bandwidth'] = str(int(bitrate_max))

    totalvbtis = len(root[1])
    itemlist = []

    for i in range(1, totalvbtis-1):
        root[1][0].insert(i, root[1][i][0])
        itemlist.append(root[1][i])


    for i in range(1, totalvbtis-1):
        root[1].remove(itemlist[i-1])

    # print(len(root[1]))

    # print(ET.tostring(root, encoding="utf8", method="xml"))
    outstr = ET.tostring(root, encoding="utf8", method="xml")


    fd = open(curmpd, "wb")
    fd.write(outstr)
    fd.close()