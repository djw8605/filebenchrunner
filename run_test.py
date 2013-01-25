#!/usr/bin/python

import ConfigParser
import argparse
import sys
import subprocess
import urllib


def build_parser(parser):
    parser.add_argument('-c', '--config',
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
    
    

def main():
    
    # First, read in command line
    cmd_parser = argparse.ArgumentParser()
    cmd_parser = build_parser(cmd_parser)
    parsed_namespace = cmd_parser.parse_args()
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
        subprocess.call("unmount %s" % file_system_dir, shell=True)
        
        # Format the filesystem
        subprocess.call("mkfs.%s %s" % (file_system_type, raw_dev) , shell=True)
        
        # Mount the filesystem
        subprocess.call("mount %s %s" %  (raw_dev, file_system_dir))
        
        # Build the *.f file
        build_simulation(config, run)
        
        # Execute the simulation
        
        # Send the simulation results to s3
    


if __name__ == "__main__":
    main()
    

