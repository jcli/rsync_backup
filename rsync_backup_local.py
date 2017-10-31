#!/usr/bin/python
import os
import sys
import commands
import datetime
import time
import subprocess

class Backup:
    def __latest_backup(self):
        remote_path = self.dst_root
        # check if folder exist
        time.sleep(1)
        output = commands.getoutput('ls ' + remote_path)
        if (output.find('No such file or directory')!=-1):
            print 'creating destination root path'
            time.sleep(1)
            output = commands.getoutput('mkdir ' + remote_path)
            return ''
        elif (output.replace('\n', '').replace(' ', '')==''):
            print "destination root empty"
            return ''
        else:
            #sort and return the latest backup
            output = output.split('\n')
            output.sort(reverse=True)
            return self.dst_root + output[0]
            
    def __init__(self, src, dst_root):
        if (src[-1]!='/'):
            src = src+'/';
        self.src = src
        if (dst_root[-1]!='/'):
            dst_root = dst_root + '/';
        self.dst_root = dst_root+src.split('/')[-2]+'/';
        self.current_date = str(datetime.datetime.utcfromtimestamp(time.time())).replace(' ', '_').replace(':','.')
        self.latest_backup_path = self.__latest_backup()
        self.log_file_name = '/tmp/' + self.src.split('/')[-2] + '_backup.log'
        
    def __create_backup_folder(self):
        remote_path = self.dst_root
        if (remote_path[-1]!='/'):
            remote_path += '/'
        remote_path += self.current_date
        time.sleep(1)
        output = commands.getoutput('mkdir -p ' + remote_path)
        return remote_path

    def __subprocess_rsync(self):
        # create the rsync command string
        if (self.latest_backup_path==''):
            link_dest = ''
        else:
            link_dest = '--link-dest=' + self.latest_backup_path
        rsync_command = 'rsync -avh --chmod a+rw -e --delete ' + link_dest + ' '\
                        + self.src + ' ' + self.target_path + ' | tee ' + self.log_file_name
        print '\n' + rsync_command + '\n'
        commands.getoutput(rsync_command)
        #append the backup date
        log_file = open(self.log_file_name, 'a')
        log_file.write('------------------------')
        log_file.write('date: ' + self.current_date)
        log_file.write('------------------------\n')
        log_file.write(rsync_command)
        log_file.close()
        log_move_command = 'cp ' + self.log_file_name + ' ' + self.src + self.log_file_name.split('/')[-1]
        print '\n' + log_move_command + '\n'
        commands.getoutput(log_move_command)
        log_move_command = 'cp ' + self.log_file_name + ' ' + self.target_path + '/' + self.log_file_name.split('/')[-1]
        print '\n' + log_move_command + '\n'
        commands.getoutput(log_move_command)
        
    def run_backup(self):
        self.target_path = self.__create_backup_folder()
        self.__subprocess_rsync()

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
    
    backup_objects = []
    for src_dir in src_dirs:
        backup_object = Backup(src_dir, dst_root)
        backup_objects.append(backup_object)

    for backup_objest in backup_objects:
        backup_objest.run_backup()
        
if __name__ == "__main__":
    main()
