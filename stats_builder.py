#!/usr/bin/python

import sys
import re
import os


def build_parser(parser):
    parser.add_option('-c', '--config',
                       help='Configuration file', dest="config", metavar='file')
    parser.add_option('-d', '--directory', help="Directory to parse", dest="directory",
                        metavar='directory')
    return parser
    

def main():
    file_re = re.compile(".*IO\sSummary:.*\s(\d+\.\d+)mb\/s.*")
    
    if len(sys.argv) != 2:
        print "Please give the directory to parse"
        sys.exit(1)
        
    directory = sys.argv[1]
    if not os.path.isdir(directory):
        print "Directory %s does not exist!" % directory
        
    for filename in os.listdir(directory):
        fp = open(os.path.join(directory, filename), 'r')
        throughput = file_re.search(fp.read())
        print throughput.group(1)
        fp.close()
    
    
    
    


if __name__ == "__main__":
    main()
    