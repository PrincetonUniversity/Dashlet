import os
import sqlite3

class DbHandler:

    def loadData(self):
        nextdict = {}
        predict = {}


        files = os.listdir("../contentServer/dash/data/")


        ids = []
        for i in range(len(files)):
            if len(files[i]) > 10:
                ids.append(files[i])

        ids.sort()

        print(ids[0])

        nlen = len(ids)

        for i in range(nlen):
            idxi = i
            idxj = (i + 1) % nlen

            nextdict[ids[idxi]] = ids[idxj]

            predict[ids[idxj]] = ids[idxi]


        c = self.conn.cursor()

        c.execute("DELETE FROM IDS")

        self.conn.commit()

        for i in range(nlen):

            c.execute("INSERT INTO IDS VALUES (?, ?, ?)", (ids[i], predict[ids[i]], nextdict[ids[i]]))

        # Save (commit) the changes
        self.conn.commit()

        # We can also close the connection if we are done with it.
        # Just be sure any changes have been committed or they will be lost.
        self.conn.close()

    def saveData(self, ip, uid, duration, playbacktime, time, timefmt):

        c = self.conn.cursor()

        c.execute("INSERT INTO DATASET VALUES (?, ?, ?, ?, ?, ?)", (ip, uid, float(duration), float(playbacktime), float(time), timefmt))

        self.conn.commit()


    def __init__(self):
        self.conn = sqlite3.connect('main.db', check_same_thread=False)


    def queryNext(self, uid):

        cur = self.conn.cursor()
        cur.execute("SELECT NEXT FROM IDS WHERE NAME=?", (uid,))

        row = cur.fetchone()
        # print(type(row[0]))

        return row[0]

    def queryPre(self, uid):
        cur = self.conn.cursor()
        cur.execute("SELECT PRE FROM IDS WHERE NAME=?", (uid,))

        row = cur.fetchone()



        # print(type(row[0]))

        return row[0]

# dbHandler = DbHandler()
#
# print(dbHandler.queryPre("6870061462866496774"))
# dbHandler.loadData()