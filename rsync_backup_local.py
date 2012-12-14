import os
import sys
import commands
import datetime
import time
import subprocess

class Backup:

    def __init__(self, src, dst_root, port):
        self.src = src
        self.dst_root = dst_root+src.split('/')[-2]+'/'
        self.port = port
        self.current_date = str(datetime.datetime.utcfromtimestamp(time.time())).replace(' ', '_').replace(':','.')
        self.latest_backup_path = self.latest_backup()
        self.log_file_name = '/tmp/' + self.src.split('/')[-2] + '_backup.log'
        
    def run_backup(self):
        if (self.__src_outdate()):
            print self.src, ' out of date!'
            self.__subprocess_remote_sync()
        else:
            self.target_path = self.__create_backup_folder()
            self.__subprocess_rsync_to_remote()

def parse_config(filename):
    try:
        config_file = open(filename, 'r')
    except:
        print 'config file does not exist!'
        exit

    config_file_data = config_file.readlines()

    for line in config_file_data:
        line = line.replace('\n', '')
        line = line.split(" ");
        if (line[0]=="dst_root"):
            if (not os.path.exists(line[1])):
                print line, "does not exist!"
                exit()
            dst_root = line[1];
            break;
            
    src_dirs = []
    for line in config_file_data:
        line = line.replace('\n', '')
        line = line.split(" ");
        if (line[0]=="src"):
            if (not os.path.exists(line[1])):
                print line, "does not exist!"
                exit()
            src_dirs.append(line[1])

    return dst_root, src_dirs
    
def main():
    if (len(sys.argv)<2):
        print "usage: python rsync_backup_local.py \"config_file_name\""
        exit()

    # parse the file
    dst_root, src_dirs = parse_config(sys.argv[1])

    print dst_root
    print src_dirs
    
    # backup_objects = []
    # for src_dir in src_dirs:
    #     backup_object = Backup(src_dir, dst_root)
    #     backup_objects.append(backup_object)

    # for backup_objest in backup_objects:
    #     backup_objest.run_backup()
        
if __name__ == "__main__":
    main()
