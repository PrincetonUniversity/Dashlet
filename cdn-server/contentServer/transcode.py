import os


foldername = "../data_profile/video/"
videonames = os.listdir(foldername)


print(videonames[0])

videonames.sort()

cnt = 0

for vname in videonames:
    vprefix = vname.split(".")[0]
    
    cmd = "mkdir ./dash/data/%s"%vprefix

    os.system(cmd)

    cmd = """ffmpeg -i %s -c:v libx264 -x264opts \"keyint=24:min-keyint=24:no-scenecut\" -c:a aac -strict -2 -b:a 128k -bf 1 -b_strategy 0 -sc_threshold 0 -pix_fmt yuv420p -map 0:v:0 -map 0:v:0 -map 0:v:0 -map 0:v:0  -map 0:v:0 -map 0:a:0 -filter:v:0 \"scale=-2:240\" -filter:v:1 \"scale=-2:360\" -filter:v:2 \"scale=-2:480\" -filter:v:3 \"scale=-2:720\" -filter:v:4 \"scale=-2:1024\" -f dash \"%s\" """%(foldername+vname, "./dash/data/%s/manifest.mpd"%vprefix)



    os.system(cmd)

    cnt += 1

    # if cnt == 5:
    #     break

