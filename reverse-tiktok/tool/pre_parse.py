import json
import sys

class Datalogger:
    def __init__(self):
        # log the playing sequence
        with open("../config.json") as fd:

            configurations = json.load(fd)

            exp_name = configurations["exp_name"]

            self.play_fd = open(f"../data/{exp_name}/{exp_name}-play.csv", "w")

            self.download_fd = open(f"../data/{exp_name}/{exp_name}-download.csv", "w")

            self.seqnum = 0


    def parse_json(self, data, flow):

        if 'data' not in data.keys():
            return

        lists = data['data']


        for i in range(len(lists)):

            if type(lists) is not list:
                continue

            if 'aweme_info' not in lists[i].keys():
                continue

            video_entry = lists[i]['aweme_info']['video']

            # print(video_entry['duration'])
            # print(video_entry['play_addr']['uri'])
            # print(len(video_entry['bit_rate']))

            bit_rates = []
            uri_hash = []
            gear_names = []
            quality_types = []


            for j in range(len(video_entry['bit_rate'])):

                bit_rates.append(str(video_entry['bit_rate'][j]['bit_rate']))
                gear_names.append(str(video_entry['bit_rate'][j]['gear_name']))
                quality_types.append(str(video_entry['bit_rate'][j]['quality_type']))

                url0 = video_entry['bit_rate'][j]['play_addr']['url_list'][0]
                url1 = video_entry['bit_rate'][j]['play_addr']['url_list'][1]


                entrys0 = url0.split("/")
                entrys1 = url1.split("/")

                uri_hash.append(entrys0[3])
                uri_hash.append(entrys1[3])

            download_addr = ""
            if len(bit_rates) > 0:
                download_addr = video_entry['bit_rate'][0]['play_addr']['url_list'][0]

            bit_rate_string = "&".join(bit_rates)
            uri_hash_string = "&".join(uri_hash)
            gear_name_string = "&".join(gear_names)
            quality_type_string = "&".join(quality_types)
            
            # print(bit_rate_string)
            # print(uri_hash_string)

            self.play_fd.write(str(self.seqnum))
            self.play_fd.write(",")
            self.play_fd.write(video_entry['play_addr']['uri'])
            self.play_fd.write(",")
            self.play_fd.write(str(video_entry['duration']))
            self.play_fd.write(",")
            self.play_fd.write(bit_rate_string)
            self.play_fd.write(",")
            self.play_fd.write(uri_hash_string)
            self.play_fd.write(",")
            self.play_fd.write(download_addr)
            self.play_fd.write(",")
            self.play_fd.write(gear_name_string)
            self.play_fd.write(",")
            self.play_fd.write(quality_type_string)
            self.play_fd.write(", ")


            self.play_fd.write(str(flow.request.timestamp_start))
            self.play_fd.write(", ")

            self.play_fd.write(str(flow.request.timestamp_end))
            self.play_fd.write(", ")

            self.play_fd.write(str(flow.response.timestamp_start))
            self.play_fd.write(", ")

            self.play_fd.write(str(flow.response.timestamp_end))
            self.play_fd.write("\n")

            self.play_fd.flush()

            self.seqnum += 1

    def log_play_seq(self, flow):

        if len(str(flow.response.content)) > 50000:

            jstr = flow.response.content.decode("utf-8")

            data = json.loads(jstr)
            self.parse_json(data, flow)



    def log_download_seq(self, flow):
        # print(flow.response.headers)
        content_type = flow.response.headers[b'Content-Type']

        self.download_fd.write(str(content_type))
        self.download_fd.write(", ")

        if (b'Accept-Ranges' in flow.response.headers):
            self.download_fd.write(str(flow.response.headers[b'Accept-Ranges']))

        if (b'Content-Range' in flow.response.headers):
            self.download_fd.write(str(flow.response.headers[b'Content-Range']))
        self.download_fd.write(", ")

        # print(b'Content-Range' in flow.response.headers)

        self.download_fd.write(str(flow.request.timestamp_start))
        self.download_fd.write(", ")
        

        self.download_fd.write(str(flow.request.timestamp_end))
        self.download_fd.write(", ")


        self.download_fd.write(str(flow.response.timestamp_start))
        self.download_fd.write(", ")


        self.download_fd.write(str(flow.response.timestamp_end))
        self.download_fd.write(", ")


        self.download_fd.write(str(flow.request.headers[b'Host']))
        self.download_fd.write(", ")

        
        rpath = flow.request.path
        rtiems = rpath.split("/")

        self.download_fd.write(str(rtiems[1]))
        self.download_fd.write(", ")

        self.download_fd.write(str(rpath))
        self.download_fd.write("\n")

        self.download_fd.flush()

    def response(self, flow):

        # if b'Content-Type' not in flow.response.headers.keys():
        #     return

        # print(flow.response.headers)

        # prevent policy notice from popping up
        if (flow.request.path.find("/policy/notice/") != -1):
            flow.response.content = b""

        content_type = flow.response.headers[b'Content-Type']


        print(content_type)

        if str(content_type) == "application/json; charset=utf-8":
            self.log_play_seq(flow)

        if str(content_type) == "video/mp4":
            self.log_download_seq(flow)



addons = [
    Datalogger()
]