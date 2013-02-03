#!/usr/bin/python

import sys
import re
import os
from numpy.random import standard_t
import numpy
import math
import optparse



def build_parser(parser):
    
    parser.add_option('-c', '--config',
                       help='Configuration file', dest="config", metavar='file')
    parser.add_option('-d', '--directory', help="Directory to parse", dest="directory",
                        metavar='directory')
    parser.add_option('-t', '--tdist', help="Use t distribution to create confidence interval", dest='tdist', action='store_true', default=False)
    parser.add_option('-a', '--average', help="Print out the average from the tests", dest='average', action='store_true', default=False)
    return parser
    

def calculateTDist(throughputs):
    # estimated std deviation
    estimated_std = throughputs.std() / math.sqrt(len(throughputs))
    
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
    

def main():
    #  1267: 657.471: IO Summary: 584010 ops, 968.789 ops/s, (88/176 r/w),  22.9mb/s,   1020us cpu/op, 182.7ms latency
    file_re = re.compile(".*IO\sSummary:.*\s(\d+\.\d+)mb\/s.*")
    
    # First, read in command line
    usage = "usage: %prog [options] directory"
    cmd_parser = optparse.OptionParser(usage = usage)
    cmd_parser = build_parser(cmd_parser)
    (parsed_namespace, args) = cmd_parser.parse_args()
    if parsed_namespace.tdist is False and parsed_namespace.average is False:
        print "You did not specify what to do with the throughput data"
        cmd_parser.print_help()
        sys.exit(1)
        
    
    if len(args) != 1:
        print "Please give the directory to parse"
        sys.exit(1)
        
    directory = args[0]
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
    
    if parsed_namespace.tdist:
        calculateTDist(throughputs)
    
    if parsed_namespace.average:
        print "Average: %lf" % (throughputs.mean())
        print "Standard Deviation: %lf" % (throughputs.std())
    
    
    
    


if __name__ == "__main__":
    main()
    