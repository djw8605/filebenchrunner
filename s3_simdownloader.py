#!/usr/bin/python

from boto.s3.connection import S3Connection
from boto.s3.key import Key
import sys, optparse, ConfigParser
import re
import os


def build_parser(parser):
    parser.add_option('-c', '--config',
                       help='Configuration file', dest="config", metavar='file')
    return parser


# filebench/tests/2b-twothird-ext4-3-5/simout.txt
def group_runs(rs):
    """
    
    @return: dictionary of {job: [key, key, key...]}
    """
    key_re = re.compile("filebench/tests/([\w\-]+)[\-\d]+")
    strip_run = re.compile("([\w\-]+)\-\d")
    runs = {}
    
    for key in rs:
        # Get the runs
        match_object = key_re.search(key.name)
        if match_object:
            job = match_object.group(1)
        else:
            print "Not Match"
            continue
        
        job = job.rstrip('-')
        job_match = strip_run.search(job)
        if job_match:
            job = job_match.group(1)
        
        if job not in runs:
            runs[job] = []
        runs[job].append(key)
    
    return runs
    
    

def main():
    
    # First, read in command line
    cmd_parser = optparse.OptionParser()
    cmd_parser = build_parser(cmd_parser)
    (parsed_namespace, args) = cmd_parser.parse_args()
    if parsed_namespace.config is None:
        print "Did not specify config file"
        sys.exit(1)
    
    # Second, read in config file
    config = ConfigParser.ConfigParser()
    config.read(parsed_namespace.config)
    
    # Get the access and secret keys
    access_key = open(config.get('general', 'access_key')).read().strip()
    secret_key = open(config.get('general', 'secret_key')).read().strip()
    conn = S3Connection(access_key, secret_key)
    bucket = conn.get_bucket("dweitzel")
    rs = bucket.list("filebench/tests")
    
    # Group the runs in a dictionary
    runs = group_runs(rs)
    print runs
    
    # Download the files into the appropriate directory
    for job in runs:
        for run in range(len(runs[job])):
            # job is the name of the run
            current_run_key = runs[job][run]
            print job
            if not os.path.exists(job):
                os.mkdir(job)
            fp = open(os.path.join(job, "simout.txt.%i" % run), 'w')
            current_run_key.get_contents_to_file(fp)
            fp.close()
    


if __name__ == "__main__":
    main()
    