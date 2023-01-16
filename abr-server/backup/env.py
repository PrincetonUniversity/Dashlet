import os
import xml.etree.ElementTree as ET
import re
import numpy as np
import json

class chunk:
    def __init__(self):
        self.nchunks = 0
        self.vsize = []
        self.asize = []
        self.time = []

    def parseTime(self, path):
        tree = ET.parse(path + "/manifest.mpd")

        root = tree.getroot()

        field = root.attrib['mediaPresentationDuration']
        num_str = re.sub("[^0-9.]", "", field)

        return float(num_str)



    def loadFromFile(self, uid, folder):
        path = folder+uid
        nfiles = len(os.listdir(path))

        nseg = (nfiles // 6) - 1
        
        duration = self.parseTime(path)

        for i in range(nseg):

            segtime = min(duration - i * 5, 5)

            self.time.append(segtime)

            a_size = os.path.getsize(path + "/chunk-stream5-%05d.m4s"% (i + 1))

            self.asize.append(a_size)
            
            self.vsize.append([])

            for j in range(5):
                v_size = os.path.getsize(path + """/chunk-stream%d-%05d.m4s"""% (j, (i + 1)))
                self.vsize[i].append(v_size)



IDX_DURATION = 1

class env:
    def loadSwipe(self, tracename):
        self.swipe_trace = np.loadtxt(tracename)

    def loadSequence(self, seqname):
        fd = open(seqname)
        self.seq_map = json.load(fd)
        fd.close()

        self.sequence = list(self.seq_map.keys())

    # should be linked to abr algorithm later
    def getNextBuffer(self, view_vidx, view_cidx):

        if (view_vidx, view_cidx) not in self.buffer_map.keys:
            return (view_vidx, view_cidx, 4)

        
        
    # should be linked to mahimanhi later
    def timeToDownload(self, filesize, time):
        bandwidth = 2000 * 1000 / 8

        return filesize / bandwidth
    
    def __init__(self, seqname, traceanme):
        self.loadSwipe(traceanme)
        self.loadSequence(seqname)
        
        self.buffer_map = {}
        self.instance_map = {}
    
    def run(self):
        view_time = 0
        buffer_time = 0

        last_time = 0
        real_time = 0

        view_vidx = 0
        view_cidx = 0


        threshould = 10

        fd = open("simu.log", "w")

        while view_vidx <= threshould:
            duration = self.swipe_trace[view_vidx][IDX_DURATION]

            nchunk_viewed = int(duration / 5) + 1

            vseg = chunk()
            folder = "/home/acer/Documents/ttstream/contentServer/dash/data/"
            vid = self.sequence[view_vidx]
            vseg.loadFromFile(vid, folder)

            chunk_download_time = []
            play_start_time = []


            download_time = 0
            start_time = -5

            event_list = []


            for i in range(nchunk_viewed):
                v_size = vseg.vsize[i][4]
                a_size = vseg.asize[i]

                chunk_download_time.append([self.timeToDownload(v_size, real_time), self.timeToDownload(a_size, real_time)])

                download_time += chunk_download_time[i][0]

                event_list.append([download_time, "v", view_vidx, i])

                download_time += chunk_download_time[i][1]

                event_list.append([download_time, "a", view_vidx, i])


                next_start_time = max((start_time + 5), download_time)

                play_start_time.append(next_start_time)

                start_time = next_start_time

                event_list.append([next_start_time, "p", view_vidx, i])

                


            for item in event_list:
                fd.write(str(item[0] + real_time) + ", " + item[1] + ", " + str(item[2]) + ", " + str(item[3]) + "\n")
            # print(chunk_download_time)

            # print(play_start_time)

            # print(start_time)

            # print(duration)

            # print(nchunk_viewed)

            view_vidx += 1


            real_time += (start_time + (duration - (nchunk_viewed - 1) * 5))
        
        fd.close()

        # pass

# tracename = "../testing/dataclean/data/128.237.82.1-0.txt"

seqname = "../testing/dataclean/vid.json"
tracename = "../testing/dataclean/data/128.237.82.1-0.txt"

e = env(seqname, tracename)
e.run()




# vseg = chunk()

# folder = "/home/acer/Documents/ttstream/contentServer/dash/data/"
# vid = "5904810145583287557"
# vseg.loadFromFile(vid, folder)


# import numpy as np

# MILLISECONDS_IN_SECOND = 1000.0
# B_IN_MB = 1000000.0
# BITS_IN_BYTE = 8.0
# RANDOM_SEED = 42
# VIDEO_CHUNCK_LEN = 4000.0  # millisec, every time add this amount to buffer
# BITRATE_LEVELS = 6
# TOTAL_VIDEO_CHUNCK = 48
# BUFFER_THRESH = 60.0 * MILLISECONDS_IN_SECOND  # millisec, max buffer limit
# DRAIN_BUFFER_SLEEP_TIME = 500.0  # millisec
# PACKET_PAYLOAD_PORTION = 0.95
# LINK_RTT = 80  # millisec
# PACKET_SIZE = 1500  # bytes
# NOISE_LOW = 0.9
# NOISE_HIGH = 1.1
# VIDEO_SIZE_FILE = './video_size_'


# class Environment:
#     def __init__(self, all_cooked_time, all_cooked_bw, random_seed=RANDOM_SEED):
#         assert len(all_cooked_time) == len(all_cooked_bw)

#         np.random.seed(random_seed)

#         self.all_cooked_time = all_cooked_time
#         self.all_cooked_bw = all_cooked_bw

#         self.video_chunk_counter = 0
#         self.buffer_size = 0

#         # pick a random trace file
#         self.trace_idx = np.random.randint(len(self.all_cooked_time))
#         self.cooked_time = self.all_cooked_time[self.trace_idx]
#         self.cooked_bw = self.all_cooked_bw[self.trace_idx]

#         # randomize the start point of the trace
#         # note: trace file starts with time 0
#         self.mahimahi_ptr = np.random.randint(1, len(self.cooked_bw))
#         self.last_mahimahi_time = self.cooked_time[self.mahimahi_ptr - 1]

#         self.video_size = {}  # in bytes
#         for bitrate in xrange(BITRATE_LEVELS):
#             self.video_size[bitrate] = []
#             with open(VIDEO_SIZE_FILE + str(bitrate)) as f:
#                 for line in f:
#                     self.video_size[bitrate].append(int(line.split()[0]))

#     def get_video_chunk(self, quality):

#         assert quality >= 0
#         assert quality < BITRATE_LEVELS

#         video_chunk_size = self.video_size[quality][self.video_chunk_counter]
        
#         # use the delivery opportunity in mahimahi
#         delay = 0.0  # in ms
#         video_chunk_counter_sent = 0  # in bytes
        
#         while True:  # download video chunk over mahimahi
#             throughput = self.cooked_bw[self.mahimahi_ptr] \
#                          * B_IN_MB / BITS_IN_BYTE
#             duration = self.cooked_time[self.mahimahi_ptr] \
#                        - self.last_mahimahi_time
	    
#             packet_payload = throughput * duration * PACKET_PAYLOAD_PORTION

#             if video_chunk_counter_sent + packet_payload > video_chunk_size:

#                 fractional_time = (video_chunk_size - video_chunk_counter_sent) / \
#                                   throughput / PACKET_PAYLOAD_PORTION
#                 delay += fractional_time
#                 self.last_mahimahi_time += fractional_time
#                 assert(self.last_mahimahi_time <= self.cooked_time[self.mahimahi_ptr])
#                 break

#             video_chunk_counter_sent += packet_payload
#             delay += duration
#             self.last_mahimahi_time = self.cooked_time[self.mahimahi_ptr]
#             self.mahimahi_ptr += 1

#             if self.mahimahi_ptr >= len(self.cooked_bw):
#                 # loop back in the beginning
#                 # note: trace file starts with time 0
#                 self.mahimahi_ptr = 1
#                 self.last_mahimahi_time = 0

#         delay *= MILLISECONDS_IN_SECOND
#         delay += LINK_RTT

# 	# add a multiplicative noise to the delay
# 	delay *= np.random.uniform(NOISE_LOW, NOISE_HIGH)

#         # rebuffer time
#         rebuf = np.maximum(delay - self.buffer_size, 0.0)

#         # update the buffer
#         self.buffer_size = np.maximum(self.buffer_size - delay, 0.0)

#         # add in the new chunk
#         self.buffer_size += VIDEO_CHUNCK_LEN

#         # sleep if buffer gets too large
#         sleep_time = 0
#         if self.buffer_size > BUFFER_THRESH:
#             # exceed the buffer limit
#             # we need to skip some network bandwidth here
#             # but do not add up the delay
#             drain_buffer_time = self.buffer_size - BUFFER_THRESH
#             sleep_time = np.ceil(drain_buffer_time / DRAIN_BUFFER_SLEEP_TIME) * \
#                          DRAIN_BUFFER_SLEEP_TIME
#             self.buffer_size -= sleep_time

#             while True:
#                 duration = self.cooked_time[self.mahimahi_ptr] \
#                            - self.last_mahimahi_time
#                 if duration > sleep_time / MILLISECONDS_IN_SECOND:
#                     self.last_mahimahi_time += sleep_time / MILLISECONDS_IN_SECOND
#                     break
#                 sleep_time -= duration * MILLISECONDS_IN_SECOND
#                 self.last_mahimahi_time = self.cooked_time[self.mahimahi_ptr]
#                 self.mahimahi_ptr += 1

#                 if self.mahimahi_ptr >= len(self.cooked_bw):
#                     # loop back in the beginning
#                     # note: trace file starts with time 0
#                     self.mahimahi_ptr = 1
#                     self.last_mahimahi_time = 0

#         # the "last buffer size" return to the controller
#         # Note: in old version of dash the lowest buffer is 0.
#         # In the new version the buffer always have at least
#         # one chunk of video
#         return_buffer_size = self.buffer_size

#         self.video_chunk_counter += 1
#         video_chunk_remain = TOTAL_VIDEO_CHUNCK - self.video_chunk_counter

#         end_of_video = False
#         if self.video_chunk_counter >= TOTAL_VIDEO_CHUNCK:
#             end_of_video = True
#             self.buffer_size = 0
#             self.video_chunk_counter = 0

#             # pick a random trace file
#             self.trace_idx = np.random.randint(len(self.all_cooked_time))
#             self.cooked_time = self.all_cooked_time[self.trace_idx]
#             self.cooked_bw = self.all_cooked_bw[self.trace_idx]

#             # randomize the start point of the video
#             # note: trace file starts with time 0
#             self.mahimahi_ptr = np.random.randint(1, len(self.cooked_bw))
#             self.last_mahimahi_time = self.cooked_time[self.mahimahi_ptr - 1]

#         next_video_chunk_sizes = []
#         for i in xrange(BITRATE_LEVELS):
#             next_video_chunk_sizes.append(self.video_size[i][self.video_chunk_counter])

#         return delay, \
#             sleep_time, \
#             return_buffer_size / MILLISECONDS_IN_SECOND, \
#             rebuf / MILLISECONDS_IN_SECOND, \
#             video_chunk_size, \
#             next_video_chunk_sizes, \
#             end_of_video, \
#             video_chunk_remain