#!/usr/bin/python

import ConfigParser
import optparse
import sys
import subprocess
from boto.s3.connection import S3Connection
from boto.s3.key import Key


def build_parser(parser):
    parser.add_option('-c', '--config',
                       help='Configuration file', dest="config", metavar='file')
    return parser

def get_config_val(config, run, var):
    try:
        val = config.get('run-%s' % str(run), var)
        return val
    except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
        return config.get('general', var)
        


def build_simulation(config, run):
    # Get the model simulation file
    simulation_file = get_config_val(config, run, 'simfile')
    
    sim_config = open(simulation_file)
    sim_string = sim_config.read()
    variables = {}
    
    # Get all variables in the general
    for variable, value in config.items("general"):
        print "Adding %s = %s" % (variable, value)
        variables[variable] = value
    
    # get all variables in the run
    try:
        for variable, value in config.items("run-%s" % str(run)):
            print "Adding %s = %s" % (variable, value)
            variables[variable] = value
    except:
        pass
        
    sim_output = 'modified_simfile.f'
    open(sim_output, 'w').write(sim_string % variables)
    return sim_output
    

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
    
    # Next start the runs
    if config.get('general', 'runs') is None:
        print "Did not specify number of runs"
    num_runs = config.get('general', 'runs')
    for run in range(int(num_runs)):
        file_system_dir = get_config_val(config, run, 'fsdir')
        raw_dev = get_config_val(config, run, 'raw_dev')
        file_system_type = get_config_val(config, run, 'fstype')
        
        # Unmount the filesystem
        subprocess.call("umount %s" % file_system_dir, shell=True)
        
        # Format the filesystem
        subprocess.call("mkfs.%s %s" % (file_system_type, raw_dev) , shell=True)
        
        # Mount the filesystem
        subprocess.call("mount %s %s" %  (raw_dev, file_system_dir), shell=True)
        
        # Build the *.f file
        sim_file = build_simulation(config, run)
        
        # Execute the simulation
        subprocess.call("filebench -f %s > /tmp/simout.txt" % sim_file, shell=True)
        
        # Send the simulation results to s3
        access_key = open(get_config_val(config, run, 'access_key')).read().strip()
        secret_key = open(get_config_val(config, run, 'secret_key')).read().strip()
        conn = S3Connection(access_key, secret_key)
        bucket = conn.create_bucket("dweitzel")
        k = Key(bucket)
        k.key = "filebench/tests/%s-%s/simout.txt" % (get_config_val(config, run, 'uniqueid'), run)
        k.set_contents_from_filename('/tmp/simout.txt')


if __name__ == "__main__":
    main()
    

