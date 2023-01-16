import copy
from itertools import permutations

class bufferTraceGenerator:

    def __init__(self, curchunkIdx, buffered_lengths, total_lengths, nchunks, nvideos):
        self.all_traces = []
        self.remain_lengths = []
        self.min_lengths = []
        self.buffered_lengths = []

        self.nchunks = nchunks
        self.nvideos = nvideos

        self.curchunkIdx = curchunkIdx

        for i in range(len(buffered_lengths)):
            self.remain_lengths.append(total_lengths[i] - buffered_lengths[i])
            self.buffered_lengths.append(buffered_lengths[i])

            if (buffered_lengths[i] > 0):
                self.min_lengths.append(0)
            else:
                self.min_lengths.append(1)

        if self.curchunkIdx > buffered_lengths[0]:
            self.min_lengths[0] = 1

    def put_balls_into_boxes(self, n, m, l, idx):
        if m == 0:
            if n <= self.remain_lengths[idx]:
                l[idx] = n
                self.all_traces.append(copy.deepcopy(l))
            return

        if n == 0:
            self.all_traces.append(copy.deepcopy(l))
            return

        for i in range(self.min_lengths[idx], n+1):
            if i <= self.remain_lengths[idx]:
                l[idx] = i
                self.put_balls_into_boxes(n-i, m-1, l, idx+1)
                l[idx] = 0

    def enumerate_traces(self):
        l = [0] * self.nvideos
        self.all_traces = []
        self.put_balls_into_boxes(self.nchunks, self.nvideos-1, l, 0)

        bufferstrategy = []

        min_buffer_idx = -1

        for i in range(len(self.buffered_lengths)):
            if self.buffered_lengths[i] == 0:
                min_buffer_idx = i-1
                break

        # when the buffer is not drained, it should buffer the current playing short video immediately
        if self.curchunkIdx > self.buffered_lengths[0]:
            min_buffer_idx = -1


        idx = 0

        for i in range(len(self.all_traces)):
            tmp = []
            smap = {}
            for j in range(5):

                for k in range(self.all_traces[i][j]):
                    tmp.append(j)

            perm = permutations(tmp)

            perm = list(perm)
            for item in perm:
                bi = min_buffer_idx
                flag = False
                retstring = ""
                for k in range(5):
                    retstring += str(item[k])
                    if item[k] > bi + 1:
                        flag = True
                        break
                    else:
                        bi = max(item[k], bi)

                if flag == False:
                    smap[retstring] = 0


            for key in smap.keys():
                bufferstrategy.append([])

                for j in key:
                    bufferstrategy[idx].append(int(j))

                idx += 1

        return bufferstrategy
        # self.all_traces


class swipeTraceGenerator:

    def __init__(self, curchunkIdx, total_lengths, nchunks, nvideos, prob_all):
        self.all_traces = []
        self.curchunkIdx = curchunkIdx
        self.total_lengths = total_lengths

        self.nchunks = nchunks
        self.nvideos = nvideos
        self.prob_all = prob_all

    def put_balls_into_boxes(self, n, m, l, idx):

        if m == 0:
            if n <= self.total_lengths[idx]:
                l[idx] = n
                self.all_traces.append(copy.deepcopy(l))
            return

        if n == 0:
            self.all_traces.append(copy.deepcopy(l))
            return

        starting_offset = 0
        if idx == 0:
            starting_offset = self.curchunkIdx - 1
        for i in range(1, n+1):
            if i <= self.total_lengths[idx] - starting_offset:
                l[idx] = i
                self.put_balls_into_boxes(n-i, m-1, copy.deepcopy(l), idx+1)
                l[idx] = 0




    def attach_probability(self):
        # adjust the probability for the current playing video
        prob_adj = 0

        for i in range(self.curchunkIdx - 1, len(self.prob_all[0])):
            prob_adj += self.prob_all[0][i]

        for i in range(self.curchunkIdx - 1, len(self.prob_all[0])):
            if prob_adj > 0.00000001:
                self.prob_all[0][i] /= prob_adj
            else:
                tmp = 1
        prob_ret = []

        # calculate probability for all traces
        for i, trace in enumerate(self.all_traces):
            lastbufferidx = len(trace) - 1

            while lastbufferidx>0:
                if trace[lastbufferidx] != 0:
                    break
                lastbufferidx -= 1

            idx_padding = [0 for j in range(len(trace))]
            idx_padding[0] = self.curchunkIdx - 1


            total_prob = 1.0
            for j in range(lastbufferidx):
                idx_video = j
                idx_chunk = trace[idx_video] + idx_padding[j] - 1

                total_prob *= self.prob_all[idx_video][idx_chunk]

            last_prob = 1.0

            for idx_chunk in range(trace[lastbufferidx] - 1):
                last_prob -= self.prob_all[lastbufferidx][idx_chunk]

            total_prob *= last_prob

            prob_ret.append(total_prob)

        return prob_ret


    def enumerate_traces(self):
        l = [0] * self.nvideos
        self.all_traces = []
        self.put_balls_into_boxes(self.nchunks, self.nvideos-1, copy.deepcopy(l), 0)

        prob_ret = self.attach_probability()

        trace_filtered = []
        prob_filtered = []
        # filter out the zero probability trace
        for i in range(len(prob_ret)):

            if prob_ret[i] > 0.00000001:
                trace_filtered.append(self.all_traces[i])
                prob_filtered.append(prob_ret[i])

        return trace_filtered, prob_filtered