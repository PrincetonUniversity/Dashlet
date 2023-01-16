import io

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

def write_buf(out, field_tag, body, indent_level):
    if body is not None:
        out.write(
            "{: <{level}}{}: {}\n".format(
                "",
                field_tag,
                body if isinstance(body, int) else str(body, "utf-8"),
                level=indent_level,
            )
        )
    elif field_tag is not None:
        out.write(" " * indent_level + str(field_tag) + " {\n")
    else:
        out.write(" " * indent_level + "}\n")

def format_pbuf2(raw):
    out = io.StringIO()
    stack = []

    try:
        pairs = _parse_proto(raw)
    except:
        return False
    stack.extend([(pair, 0) for pair in pairs])

    while len(stack):
        pair, indent_level = stack.pop()

        if pair.wire_type == pair.WireTypes.group_start:
            body = None
        elif pair.wire_type == pair.WireTypes.group_end:
            body = None
            pair._m_field_tag = None
        elif pair.wire_type == pair.WireTypes.len_delimited:
            body = pair.value.body
        elif pair.wire_type == pair.WireTypes.varint:
            body = pair.value.value
        else:
            body = pair.value

        try:
            pairs = _parse_proto(body)
            stack.extend([(pair, indent_level + 2) for pair in pairs])
            write_buf(out, pair.field_tag, None, indent_level)
        except:
            write_buf(out, pair.field_tag, body, indent_level)

        if stack:
            prev_level = stack[-1][1]
        else:
            prev_level = 0

        if prev_level < indent_level:
            levels = int((indent_level - prev_level) / 2)
            for i in range(1, levels + 1):
                write_buf(out, None, None, indent_level - i * 2)

    return out.getvalue()

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

def log_dict(self, data, flow):

    if 5 not in data.keys():
        return

    lists = data[5]

    if type(lists) is not list:
        return

    self_play_fd = open("tmp.csv", "w")

    for i in range(len(lists)):

        if 7 not in lists[i].keys():
            continue

        video_entry = lists[i][7]

        # print(video_entry['duration'])
        # print(video_entry['play_addr']['uri'])
        # print(len(video_entry['bit_rate']))

        bit_rates = []
        uri_hash = []
        gear_names = []
        quality_types = []

        print(i)

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

        kk = video_entry[bit_rate_list_idx][j]
        tmp = video_entry[play_addr_out_idx][uri_idx]



        self_play_fd.write(str(0))
        self_play_fd.write(",")
        self_play_fd.write(video_entry[play_addr_out_idx][uri_idx][1].decode("utf-8"))
        self_play_fd.write(",")
        self_play_fd.write(str(video_entry[duration_idx][duration_idx]))
        self_play_fd.write(",")
        self_play_fd.write(bit_rate_string)
        self_play_fd.write(",")
        self_play_fd.write(uri_hash_string)
        self_play_fd.write(",")
        self_play_fd.write(download_addr)
        self_play_fd.write(",")
        self_play_fd.write(gear_name_string)
        self_play_fd.write(",")
        self_play_fd.write(quality_type_string)
        self_play_fd.write(", ")

        self_play_fd.write(str(0))
        self_play_fd.write(", ")

        self_play_fd.write(str(1))
        self_play_fd.write(", ")

        self_play_fd.write(str(1000))
        self_play_fd.write(", ")

        self_play_fd.write(str(1001))
        self_play_fd.write("\n")

        self_play_fd.flush()

        # self.seqnum += 1

    self_play_fd.close()


with open("protobuf.data", mode='rb') as file: # b is important -> binary
    rawCotent = file.read()
    parsed_dict = format_pbuf(rawCotent)

    video_list = []

    log_dict("", parsed_dict, "")
    # for i in range(len(parsed_dict[5])):
    #     kk = parsed_dict[5][i]
    #     tmp = 1