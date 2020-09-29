#!/usr/bin/python
# -*- coding:UTF-8 -*-
"""\
Usage:

python repa_diff.py [--host1=host1] [--port1=port1] [--host2=host2] [--port2=port2] [--fname=fname] [--threadnum=threadnum]
"""

import os
import sys
import threading
import getopt
import time

REQ_URL = "curl -s -Afreewheel \'http://%s:%d/dispatch?command=repository::show_object&id=%s&type=%s\'"
SEPARATOR = ","

class DiffThread(threading.Thread):
    def __init__(self, _params, _host1, _port1, _host2, _port2, _idx):
        threading.Thread.__init__(self)
        self.params = _params
        self.host1 = _host1
        self.port1 = _port1
        self.host2 = _host2
        self.port2 = _port2
        self.idx = _idx
        self.res_file = None
        
    def __open_res_file(self):
        fname = "./result/response" + str(self.idx)
        if os.path.exists(fname) == True:
            os.unlink(fname)
        self.res_file = open(fname, 'w')

    def __close_res_file(self):
        self.res_file.close()

    def run(self):
        self.__open_res_file()
        for param in self.params:
            base_url = self.__build_req(self.host1, self.port1, param)
            if base_url == "":
                continue
            exp_url = self.__build_req(self.host2, self.port2, param)
            if exp_url == "":
                continue
            base_res_fd = os.popen(base_url, 'r')
            base_res = "".join(base_res_fd.readlines())
            exp_res_fd = os.popen(exp_url, 'r')
            exp_res = "".join(exp_res_fd.readlines())
            res = None
            if base_res != "" and exp_res != "" and base_res == exp_res:
                res = param + " = ok\n"
            else:
                res = param + "not\n" + base_res + "\n" + exp_res
                prefix = "./result/"
                diff_base = prefix + param + "base"
                diff_exp = prefix + param + "exp"
                diff_base_file = open(diff_base, 'w')
                diff_exp_file = open(diff_exp, 'w')
                diff_base_file.write(base_res)
                diff_exp_file.write(exp_res)
                diff_base_file.close()
                diff_exp_file.close()

            self.res_file.write(res)
            #print "[base_url] = %s, [exp_url] = %s, [base_res] = %s, [exp_res] = %s" % (base_url, exp_url, base_res, exp_res)
            time.sleep(1)

        self.__close_res_file()
            

    def __build_req(self, host, port, param):
        split_res = param.split(SEPARATOR)
        if len(split_res) != 2:
            return ""
        return REQ_URL % (host, port, split_res[1], split_res[0])


class RepaDiffer():
    def __init__(self, _host1, _port1, _host2, _port2, _fname, _threadnum):
        self.host1 = _host1
        self.port1 = _port1
        self.host2 = _host2
        self.port2 = _port2
        self.fname = _fname
        self.threadnum = _threadnum
        self.lines = []
        self.split_lines = []
        self.threads = []
        self.file_fd = None

    def run(self):
        self.__read_file()
        self.__split()
        
        for i in range(0, self.threadnum):
            self.threads.append(DiffThread(self.split_lines[i], self.host1, self.port1, self.host2, self.port2, i))
            
        for t in self.threads:
            t.start()
            print "thread %s started" % t.getName()

        for t in self.threads:
            t.join()

        self.__close_file()
        
    def __close_file(self):
        self.file_fd.close()
         

    def __read_file(self):
        self.file_fd = open(self.fname, 'r')
        for line in self.file_fd:
            self.lines.append(line.rstrip('\n'))

    def __split(self):
        batchsize = len(self.lines) / self.threadnum + 1 
        l = [self.lines[i:i+batchsize] for i in range(0, len(self.lines), batchsize)]
        for item in l:
            self.split_lines.append(item)


def main(argv):

    print "main start"

    host1, port1, host2, port2, fname, threadnum = '', 10000, '', 10000, '', 1

    try:
        opts, args = getopt.getopt(argv, 'a:b:c:d:e:f:', ['host1=', 'port1=', 'host2=', 'port2=', 'fname=', 'threadnum='])
    except:
        print __doc__
        sys.exit(-1)

    for opt, arg in opts:
        if opt in ('-a', '--host1'):
            host1 = arg
        elif opt in ('-b', '--port1')  : port1 = int(arg)
        elif opt in ('-c', '--host2')  : host2 = arg
        elif opt in ('-d', '--port2')  : port2 = int(arg)
        elif opt in ('-e', '--fname')  : fname = arg
        elif opt in ('-f', '--threadnum') : threadnum = int(arg)
        else: 
            print __doc__
            sys.exit(-2)

    repa_differ = RepaDiffer(host1, port1, host2, port2, fname, threadnum)
    repa_differ.run()

    print "main exit"


if __name__ == '__main__':
    main(sys.argv[1:])
