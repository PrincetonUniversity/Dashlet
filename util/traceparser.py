import csv


class swipetraceparser:
    def __init__(self) -> None:
        self.IDX_TIME_STRING = 0
        self.IDX_TS = 1

        self.time_string_list = []
        self.ts_list = []
    
    def parse(self, filename):
        self.time_string_list = []
        self.ts_list = []

        with open(filename, newline='') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
            
            for row in spamreader:
                self.time_string_list.append(row[self.IDX_TIME_STRING])
                self.ts_list.append(float(row[self.IDX_TS]))
    
    def get_time_string_list(self):
        return self.time_string_list

    def get_ts_list(self):
        return self.ts_list

    def get_watch_time(self):
        watch_time_list = [60]

        for i in range(1, len(self.ts_list)):
            watch_time_list.append(self.ts_list[i] - self.ts_list[i-1])
        
        return watch_time_list


class downloadtraceparser:

    def __init__(self) -> None:
        self.IDX_CONTENT_TYPE = 0
        self.IDX_RANGE = 1
        self.IDX_REQ_START = 2
        self.IDX_REQ_END = 3
        self.IDX_RES_START = 4
        self.IDX_RES_END = 5
        self.IDX_HOST = 6
        self.IDX_URI = 7
        self.IDX_RPATH = 8

        self.content_type_list = []
        self.range_list = []
        self.req_start_list = []
        self.req_end_list = []
        self.res_start_list = []
        self.res_end_list = []
        self.host_list = []
        self.uri_list = []
        self.rpath_list = []
    
    def parse(self, filename):
        self.content_type_list = []
        self.range_list = []
        self.req_start_list = []
        self.req_end_list = []
        self.res_start_list = []
        self.res_end_list = []
        self.host_list = []
        self.uri_list = []
        self.rpath_list = []
        
        with open(filename, newline='') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
            
            for row in spamreader:

                self.content_type_list.append(row[self.IDX_CONTENT_TYPE])

                rowstr = row[self.IDX_RANGE].strip().split()[1]
                c_range = rowstr.split("/")[0]
                c_total = int(rowstr.split("/")[1])
                c_start = int(c_range.split("-")[0])
                c_end = int(c_range.split("-")[1])
                self.range_list.append((c_start, c_end, c_total))

                self.req_start_list.append(float(row[self.IDX_REQ_START]))
                self.req_end_list.append(float(row[self.IDX_REQ_END]))
                self.res_start_list.append(float(row[self.IDX_RES_START]))
                self.res_end_list.append(float(row[self.IDX_RES_END]))

                self.host_list.append(row[self.IDX_HOST])
                self.uri_list.append(row[self.IDX_URI])
                self.rpath_list.append(row[self.IDX_RPATH])


    def get_content_type_list(self):
        return self.content_type_list
    
    def get_range_list(self):
        return self.range_list
    
    def get_req_start_list(self):
        return self.req_start_list
    
    def get_req_end_list(self):
        return self.req_end_list
        
    def get_res_start_list(self):
        return self.res_start_list
        
    def get_res_end_list(self):
        return self.res_end_list
    
    def get_host_list(self):
        return self.host_list
    
    def get_uri_list(self):
        return self.uri_list
    
    def get_rpath_list(self):
        return self.rpath_list



class playtraceparser:

    def __init__(self) -> None:
        self.IDX_SEQNUM = 0
        self.IDX_URI = 1
        self.IDX_DURATION = 2
        self.IDX_BITRATE = 3
        self.IDX_URIHASH = 4
        self.IDX_DOWNLOAD_ADDR = 5
        self.IDX_GEAR_NAME = 6
        self.IDX_QUALITY = 7
        self.IDX_REQ_START = 8
        self.IDX_REQ_END = 9
        self.IDX_RES_START = 10
        self.IDX_RES_END = 11

        self.seqnum_list = []
        self.uri_list = []
        self.duration_list = []
        self.bit_rate_list = []
        self.uri_hash_list = []
        self.download_addr_list = []
        self.gear_name_list = []
        self.quality_list = []
        self.req_start_list = []
        self.req_end_list = []
        self.res_start_list = []
        self.res_end_list = []

    def parse(self, filename):
        self.seqnum_list = []
        self.uri_list = []
        self.duration_list = []
        self.bit_rate_list = []
        self.uri_hash_list = []
        self.download_addr_list = []
        self.gear_name_list = []
        self.quality_list = []
        self.req_start_list = []
        self.req_end_list = []
        self.res_start_list = []
        self.res_end_list = []

        with open(filename, newline='') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
            
            for row in spamreader:
                self.seqnum_list.append(int(row[self.IDX_SEQNUM]))
                self.uri_list.append(row[self.IDX_URI])
                self.duration_list.append(int(row[self.IDX_DURATION]) / 1000.0)
                self.bit_rate_list.append(row[self.IDX_BITRATE].split("&"))
                self.uri_hash_list.append(row[self.IDX_URIHASH].split("&"))                
                self.download_addr_list.append(row[self.IDX_DOWNLOAD_ADDR])
                self.gear_name_list.append(row[self.IDX_GEAR_NAME].split("&"))

                self.quality_list.append([int(quality) for quality in row[self.IDX_QUALITY].split("&")])

                if len(row) > self.IDX_RES_END:
                    self.req_start_list.append(float(row[self.IDX_REQ_START]))
                    self.req_end_list.append(float(row[self.IDX_REQ_END]))
                    self.res_start_list.append(float(row[self.IDX_RES_START]))
                    self.res_end_list.append(float(row[self.IDX_RES_END]))

    def get_seqnum_list(self):
        return self.seqnum_list

    def get_uri_list(self):
        return self.uri_list
    
    def get_duration_list(self):
        return self.duration_list
    
    def get_bit_rate_list(self):
        return self.bit_rate_list
        
    def get_uri_hash_list(self):
        return self.uri_hash_list
        
    def get_download_addr_list(self):
        return self.download_addr_list
        
    def get_gear_name_list(self):
        return self.gear_name_list
        
    def get_quality_list(self):
        return self.quality_list
        
    def get_req_start_list(self):
        return self.req_start_list
    
    def get_req_end_list(self):
        return self.req_end_list
        
    def get_res_start_list(self):
        return self.res_start_list
        
    def get_res_end_list(self):
        return self.res_end_list
