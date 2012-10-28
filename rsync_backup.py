import os
import sys
import commands
import datetime
import time
import subprocess

class Backup:

    def latest_backup(self):
        remote_ip = self.dst_root.split(':')[0]
        remote_path = self.dst_root.split(':')[-1]
        # check if folder exist
        time.sleep(1)
        output = commands.getoutput('ssh -p ' + self.port + ' ' + remote_ip + ' \"ls ' + remote_path + '\"')
        if (output.find('No such file or directory')!=-1):
            print 'creating destination root path'
            time.sleep(1)
            output = commands.getoutput('ssh -p ' + self.port + ' ' + remote_ip + ' \"mkdir ' + remote_path + '\"')
            return ''
        elif (output.replace('\n', '').replace(' ', '')==''):
            print "destination root empty"
            return ''
        else:
            #sort and return the latest backup
            output = output.split('\n')
            output.sort(reverse=True)
            return output[0]

    def __init__(self, src, dst_root, port):
        self.src = src
        self.dst_root = dst_root+src.split('/')[-2]+'/'
        self.port = port
        self.current_date = str(datetime.datetime.utcfromtimestamp(time.time())).replace(' ', '_').replace(':','.')
        self.latest_backup_path = self.latest_backup()
        self.log_file_name = '/tmp/' + self.src.split('/')[-2] + '_backup.log'
        
    def __create_backup_folder(self):
        remote_ip = self.dst_root.split(':')[0]
        remote_path = self.dst_root.split(':')[-1]
        if (remote_path[-1]!='/'):
            remote_path += '/'
        remote_path += self.current_date
        time.sleep(1)
        output = commands.getoutput('ssh -p ' + self.port + ' ' + remote_ip + ' \"mkdir ' + remote_path + '\"')
        return remote_ip + ':' + remote_path

    def __subprocess_remote_sync(self):
        if (self.src[-1]=='/'):
            src_dir = self.src[0:-1]            
#        remote_sync_log_name = self.log_file_name.split('.')[0] + '_remote_sync.' + self.log_file_name.split('.')[1]
        rsync_command = 'rsync -avh --chmod a+rwx -e "ssh -p ' + self.port + '" --delete ' + ' ' + self.dst_root + \
                        self.latest_backup_path + '/' + ' ' + src_dir + ' &> ' + self.log_file_name
        print '\n' + rsync_command + '\n'
#        subprocess.call(rsync_command, shell=True)
        commands.getoutput(rsync_command)
        log_file = open(self.log_file_name, 'a')
        log_file.write(self.current_date)
        log_move_command = 'mv ' + self.log_file_name + ' ' + self.src + self.log_file_name.split('/')[-1]
        print '\n' + log_move_command + '\n'
        commands.getoutput(log_move_command)
        
    def __subprocess_rsync_to_remote(self):
        # create the rsync command string
        if (self.latest_backup_path==''):
            link_dest = ''
        else:
            link_dest = '--link-dest=' + self.dst_root.split(':')[-1] + self.latest_backup_path
        rsync_command = 'rsync -avh --chmod a+rwx -e "ssh -p ' + self.port + '" --delete ' + link_dest + ' '\
                        + self.src + ' ' + self.target_path + ' &> ' + self.log_file_name
        print '\n' + rsync_command + '\n'
#        subprocess.call(rsync_command, shell=True)
        commands.getoutput(rsync_command)
        #append the backup date
        log_file = open(self.log_file_name, 'a')
        log_file.write(self.current_date)
        log_move_command = 'mv ' + self.log_file_name + ' ' + self.src + self.log_file_name.split('/')[-1]
        print '\n' + log_move_command + '\n'
        commands.getoutput(log_move_command)

    def __src_outdate(self):
        if (self.latest_backup_path==''):
            return False
        # get date of the last src backup
        try:
            local_log = open(self.src + self.log_file_name.split('/')[-1], 'r')
        except:
            print self.src, " no local backup log file."
            return True
        local_log_content = local_log.readlines()
        local_log.close()
        if (self.latest_backup_path > local_log_content[-1]):
            return True
        else:
            return False
            
    def run_backup(self):
        if (self.__src_outdate()):
            print self.src, ' out of date!'
            self.__subprocess_remote_sync()
        else:
            self.target_path = self.__create_backup_folder()
            self.__subprocess_rsync_to_remote()

def parse_config(filename, isremote):
    try:
        config_file = open(filename, 'r')
    except:
        print 'config file does not exist!'
        exit

    config_file_data = config_file.readlines()
    if(isremote):
        port=config_file_data[0].split(" ")[1]
        dst_root=config_file_data[0].split(" ")[2].replace('\n', '')
    else:
        port=config_file_data[1].split(" ")[1]
        dst_root=config_file_data[1].split(" ")[2].replace('\n', '')

    src_dirs = []
    for line in config_file_data[2:]:
        line = line.replace('\n', '')
        if (line[-1]!='/'):
            line += '/'
        if (not os.path.exists(line)):
            print line, "does not exist!"
            exit()
        src_dirs.append(line)

    return port, dst_root, src_dirs
    
def main():
    if (len(sys.argv)<2):
        print "usage: python rsync_backup.py \"config_file_name\""
        exit()

    isremote = False
    if (len(sys.argv)>2):
        if (sys.argv[2]=="remote"):
            isremote=True
            
    # parse the file
    port, dst_root, src_dirs = parse_config(sys.argv[1], isremote)

    backup_objects = []
    for src_dir in src_dirs:
        backup_object = Backup(src_dir, dst_root, port)
        backup_objects.append(backup_object)

    for backup_objest in backup_objects:
        backup_objest.run_backup()
        

if __name__ == "__main__":
    main()
