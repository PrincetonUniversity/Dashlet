import json
import sys

import io
import time

from kaitaistruct import KaitaiStream
from mitmproxy.contrib.kaitaistruct import google_protobuf


def _parse_proto(raw: bytes):
    """Parse a bytestring into protobuf pairs and make sure that all pairs have a valid wire type."""
    buf = google_protobuf.GoogleProtobuf(KaitaiStream(io.BytesIO(raw)))
    for pair in buf.pairs:
        if not isinstance(pair.wire_type, google_protobuf.GoogleProtobuf.Pair.WireTypes):
            raise ValueError("Not a protobuf.")
    return buf.pairs

def add_to_dict(dic, key, val):

    if key not in dic.keys():
        dic[key] = val
        return
    elif isinstance(dic[key], list) == False:
        tmp_val = dic[key]
        dic[key] = []
        dic[key].append(tmp_val)

    dic[key].append(val)


def parse_dfs(thispair, sub_dict):

    if thispair.wire_type == thispair.WireTypes.group_start:
        body = None
    elif thispair.wire_type == thispair.WireTypes.group_end:
        body = None
        thispair._m_field_tag = None
    elif thispair.wire_type == thispair.WireTypes.len_delimited:
        body = thispair.value.body
    elif thispair.wire_type == thispair.WireTypes.varint:
        body = thispair.value.value
    else:
        body = thispair.value

    try:
        pairs = _parse_proto(body)

        for pair in pairs:
            this_dict = {}
            parse_dfs(pair, this_dict)
            add_to_dict(sub_dict, pair.field_tag, this_dict)

    except:
        add_to_dict(sub_dict, thispair.field_tag, body)


def format_pbuf(raw):
    data_dict = {}

    try:
        pairs = _parse_proto(raw)
    except:
        return False

    for pair in pairs:
        this_dict = {}
        parse_dfs(pair, this_dict)
        add_to_dict(data_dict, pair.field_tag, this_dict)

    return data_dict




bit_rate_val_idx = 3
bit_rate_list_idx = 11
quality_type_idx = 2
gear_name_idx = 1
play_addr_idx = 4
url_list_idx = 2
url_inner_key = 2
uri_idx = 1
play_addr_out_idx = 1
duration_idx = 13
data_list_idx = 5
video_entry_idx = 7

realtime_idx = 126

class Datalogger:
    def __init__(self):
        # log the playing sequence
        with open("../config.json") as fd:

            configurations = json.load(fd)

            exp_name = configurations["exp_name"]

            self.play_fd = open(f"../data/{exp_name}/{exp_name}-play.csv", "w")

            self.download_fd = open(f"../data/{exp_name}/{exp_name}-download.csv", "w")

            self.seqnum = 0

            self.download_start_fd = open(f"../data/{exp_name}/{exp_name}-downloadstart.log", "w")

            self.download_start_recorded = False


    def log_dict(self, data, flow):

        self.download_start_fd.close()

        if data_list_idx not in data.keys():
            return

        lists = data[data_list_idx]

        if type(lists) is not list:
            return

        for i in range(len(lists)):

            if video_entry_idx not in lists[i].keys():

                # skip real time streaming
                if realtime_idx in lists[i].keys():
                    self.play_fd.write(str(self.seqnum))
                    self.play_fd.write("\n")
                    self.play_fd.flush()
                    self.seqnum += 1

                continue

            video_entry = lists[i][video_entry_idx]

            bit_rates = []
            uri_hash = []
            gear_names = []
            quality_types = []

            if isinstance(video_entry[bit_rate_list_idx], list) == False:
                tmp_val = video_entry[bit_rate_list_idx]
                video_entry[bit_rate_list_idx] = []
                video_entry[bit_rate_list_idx].append(tmp_val)

            for j in range(len(video_entry[bit_rate_list_idx])):
                bit_rates.append(str(video_entry[bit_rate_list_idx][j][bit_rate_val_idx][bit_rate_val_idx]))

                gear_name_str = ""
                try:
                    gear_name_str = video_entry[bit_rate_list_idx][j][gear_name_idx][gear_name_idx].decode("utf-8")
                except:
                    print("gear name error, skip decode")
                gear_names.append(gear_name_str)
                quality_types.append(str(video_entry[bit_rate_list_idx][j][quality_type_idx][quality_type_idx]))

                url0 = video_entry[bit_rate_list_idx][j][play_addr_idx][url_list_idx][0][url_inner_key].decode("utf-8")
                url1 = video_entry[bit_rate_list_idx][j][play_addr_idx][url_list_idx][1][url_inner_key].decode("utf-8")

                entrys0 = url0.split("/")
                entrys1 = url1.split("/")

                uri_hash.append(entrys0[3])
                uri_hash.append(entrys1[3])

            download_addr = ""
            if len(bit_rates) > 0:
                download_addr = video_entry[bit_rate_list_idx][0][play_addr_idx][url_list_idx][0][url_inner_key].decode("utf-8")

            bit_rate_string = "&".join(bit_rates)
            uri_hash_string = "&".join(uri_hash)
            gear_name_string = "&".join(gear_names)
            quality_type_string = "&".join(quality_types)
            
            # print(bit_rate_string)
            # print(uri_hash_string)

            self.play_fd.write(str(self.seqnum))
            self.play_fd.write(",")
            self.play_fd.write(video_entry[play_addr_out_idx][uri_idx][1].decode("utf-8"))
            self.play_fd.write(",")
            self.play_fd.write(str(video_entry[duration_idx][duration_idx]))
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

            parsed_dict = format_pbuf(flow.response.content)
            self.log_dict(parsed_dict, flow)



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

        try:
            self.download_fd.write(str(flow.request.headers[b'Host']))
        except KeyError:
            self.download_fd.write("UNKNOWN")
        self.download_fd.write(", ")

        
        rpath = flow.request.path
        rtiems = rpath.split("/")

        self.download_fd.write(str(rtiems[1]))
        self.download_fd.write(", ")

        self.download_fd.write(str(rpath))
        self.download_fd.write("\n")

        self.download_fd.flush()

    def response(self, flow):
        if self.download_start_recorded is False:
            self.download_start_recorded = True
            ts = time.time()
            self.download_start_fd.write(str(ts))
            self.download_start_fd.flush()

        content_type = ""
        try:
            content_type = flow.response.headers[b'Content-Type']
        except KeyError:
            return

        # prevent policy notice from popping up
        if (flow.request.path.find("/policy/notice/") != -1):
            flow.response.content = b""

        if str(content_type) == "application/grpc":
            flow.response.content = b""

        if str(content_type) == "application/x-protobuf; charset=utf-8":
            self.log_play_seq(flow)

        if str(content_type) == "video/mp4":
            self.log_download_seq(flow)

    # def request(self, flow):
    #     content_type = ""
    #
    #     try:
    #         content_type = flow.request.headers[b'Content-Type']
    #     except KeyError:
    #         return
    #
    #     if str(content_type) == "application/x-protobuf":
    #         # print("pbuf catched\n\n")
    #
    #         parsed_dict = format_pbuf(flow.request.content)
    #
    #         flow.request.content = flow.request.content.replace(b'2021708040', b'2022603030')
    #
    #         # print(flow.request.content)
    #
    #         flow.request.headers[b'user-agent'] = flow.request.headers[b'user-agent'].replace("2021708040", "2022603030")
    #         # print(flow.request.headers[b'user-agent'])
    #
    #         flow.request.path = flow.request.path.replace("2021708040", "2022603030")
    #
    #         # print("before sleep")
    #     time.sleep(3)
    #         # print("after sleep")
    #         # print(flow.request.path)
    #
    #     # try:
    #     #     content_type = flow.request.headers
    #     # except KeyError:
    #     #     return
    #
    #
    #
    #     # if str()






addons = [
    Datalogger()
]