import csv
import os
import subprocess




metadatafolder = "/home/acer/Documents/ttstream/reverse-tiktok/data"
videofolder = "/home/acer/Documents/ttstream/reverse-tiktok/video"
outfolder = "./dash/data/"

IDX_URI = 1
IDX_BITRATE = 3
IDX_URL = 5
IDX_RESOLUTION = 6

CHUNK_IN_SECONDS = 5

for uid in range(1, 12):


    net_condition_list = ["low", "mid", "high"]

    for nc in net_condition_list:

        exp_name = f"tt-{uid}-{nc}"

        table_list = []

        with open(f"{metadatafolder}/{exp_name}/{exp_name}-play.csv", newline='') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')

            for row in spamreader:
                table_list.append(row)

        for i in range(len(table_list)):

            if len(table_list[i]) < IDX_RESOLUTION:
                continue

            inputVideoName = f"{videofolder}/{table_list[i][IDX_URI]}.mp4"


            if os.path.exists(inputVideoName) == False:
                continue

            outVideoName = f"{outfolder}{table_list[i][IDX_URI]}"


            if os.path.exists(outVideoName) == True:
                continue

            os.mkdir(outVideoName)


            proc = subprocess.Popen(f"ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=s=x:p=0 {inputVideoName}", stdout=subprocess.PIPE, shell=True)
            (out, err) = proc.communicate()
            outstr = out.decode()

            outstr = outstr.strip()

            origin_bitrate = outstr.split("x")

            resolution_x = int(origin_bitrate[0])
            resolution_y = int(origin_bitrate[1])

            bitrates = table_list[i][IDX_BITRATE].split("&")
            resolutions = table_list[i][IDX_RESOLUTION].split("&")

            for idx in range(len(bitrates)):
                bitrates[idx] = int(int(bitrates[idx]) / 1000) - 128

            bitrates = sorted(bitrates)

            # for idx in range(len(resolutions)):
            #     rlist = resolutions[idx].split("_")

            #     resolutions[idx] = int(rlist[-2])


            parameter_map_list = ["-map 0:v:0" for idx in range(len(bitrates))]
            parameter_filter_list = [f"-filter:v:{idx} \"scale={resolution_x}:{resolution_y}\"" for idx in range(len(bitrates))]
            parameter_bitrate_list = [f"-b:v:{idx} {bitrates[idx]}K" for idx in range(len(bitrates))]



            cmd_str = f"ffmpeg -i {inputVideoName} -r 30 -c:v libx264 -x264opts \"keyint=30:min-keyint=30:no-scenecut\" "\
                      + f"-c:a aac -strict -2 -b:a 128k -bf 1 -b_strategy 0 -sc_threshold 0 -pix_fmt yuv420p " \
                      + " ".join(parameter_map_list) + " -map 0:a:0 "\
                      + " ".join(parameter_filter_list) + " "\
                      + " ".join(parameter_bitrate_list) + " "\
                      + f"-seg_duration {CHUNK_IN_SECONDS} -adaptation_sets \"id=0,streams=v id=1,streams=a\" -f dash {outVideoName}/manifest.mpd"

            os.system(cmd_str)
