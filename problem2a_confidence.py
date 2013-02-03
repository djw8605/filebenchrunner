#!/usr/bin/python

import sys
import re
import os
from numpy.random import standard_t
import numpy
import math


def build_parser(parser):
    parser.add_option('-c', '--config',
                       help='Configuration file', dest="config", metavar='file')
    parser.add_option('-d', '--directory', help="Directory to parse", dest="directory",
                        metavar='directory')
    return parser
    

def main():
    #  1267: 657.471: IO Summary: 584010 ops, 968.789 ops/s, (88/176 r/w),  22.9mb/s,   1020us cpu/op, 182.7ms latency
    file_re = re.compile(".*IO\sSummary:.*\s(\d+\.\d+)mb\/s.*")
    
    if len(sys.argv) != 2:
        print "Please give the directory to parse"
        sys.exit(1)
        
    directory = sys.argv[1]
    if not os.path.isdir(directory):
        print "Directory %s does not exist!" % directory
        
    throughput_list = []
    for filename in os.listdir(directory):
        fp = open(os.path.join(directory, filename), 'r')
        throughput_match = file_re.search(fp.read())
        fp.close()
        throughput = float(throughput_match.group(1))
        throughput_list.append(throughput)
    
    throughputs = numpy.array(throughput_list)
    
    # estimated std deviation
    estimated_std = throughputs.std() / math.sqrt(len(throughput_list))
    
    # critical values
    crit_50 = 0.703	
    crit_75 = 1.230
    crit_90 = 1.833
    crit_95 = 2.262
    
    def calcInterval(crit):
        return  (throughputs.mean() - (crit * estimated_std), throughputs.mean() + (crit * estimated_std))
        
    interval_50 = calcInterval(crit_50)
    interval_75 = calcInterval(crit_75)
    interval_90 = calcInterval(crit_90)
    interval_95 = calcInterval(crit_95)
    
    print "50%%: %s" % str(interval_50)
    print "75%%: %s" % str(interval_75)
    print "90%%: %s" % str(interval_90)
    print "95%%: %s" % str(interval_95)
    
    
    
    
    


if __name__ == "__main__":
    main()
    