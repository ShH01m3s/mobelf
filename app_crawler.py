# reference https://janakiev.com/blog/python-shell-commands/
# https://miguelbigueur.com/2017/06/28/python-security-scripting/
# https://www.python.org/dev/peps/pep-0324/
# https://stackabuse.com/pythons-os-and-subprocess-popen-commands/#:~:text=The%20Python%20documentation%20recommends%20the,program%20as%20a%20child%20process.&text=Thus%2C%20when%20we%20call%20subprocess.

import paramiko # for ssh
import os # for filesystem manips
import utils
import subprocess
import pexpect
import logger
import settings
import time


import pipes

import os.path as op
from ppadb.client import Client as AdbClient
from pathlib import Path



# https://pypi.org/project/pure-python-adb/
# application_name, case_dir
def fetch_all_app_data_android(package_name):
    settings.client = AdbClient(host="127.0.0.1", port=5037)
    settings.device = settings.client.device(settings.client.devices()[0].serial)
    result = os.popen("frida-ps -U | grep " + package_name)
    if result.read():
        logger.info2("Frida running")
    else:
        logger.error("Frida is not running!")
    settings.device.shell("su && cd /sbin && ./frida")

    logger.info("Device found: ", settings.device.serial)
    logger.info("Command executed with adb: ", "su && cd /sbin && ./frida")
           

    # run frida
    # adb shell && su && cd /sbin && ./frida
    # package_name = frida-ps -U | grep application_name 
    # path = adb shell pm path package_name
    # adb pull path case_dir

def dump_logcat(connection):
    while True:
        data = connection.read(1024)
        if not data:
            break
        print(data.decode('utf-8'))
    connection.close()

def fetch_app_logs_android():
    os.popen("adb logcat > " + settings.today + ".txt")


def fetch_app_backup(backup_pass = "1234"):
    os.popen("java -jar {} unpack backup_u.ab backup_u.tar".format(settings.path_to_abe))
    # assuming the password for backup was set to 1234
    os.popen("java -jar {} unpack backup_e.ab backup_e.tar {}".format(settings.path_to_abe, backup_pass))


# module check prerequisites
# module application recon
def fetch_all_app_data_ios(client, application_name, ip, passw):
    print("Running remote frida-server on iDevice. Default location - /usr/sbin")
    client.exec_command("cd /usr/sbin")
    client.exec_command("./frida-server -l " + ip + ":8989")

    application_pid = os.popen("frida-ps -H "+ ip + ":8989 | grep " + application_name + " | awk '{print $1}'").read()
    print("Application PID is " + application_pid)

    com = "ipainstaller -l | grep " + application_name
    stdin, stdout, stderr = client.exec_command(com)
    package_name = utils.read_std(stdout)
    print("Package name is: "  + package_name)
    com = "ipainstaller -i " + package_name + " | grep Data | awk '{print $2}'"
    stdin, stdout, stderr = client.exec_command(com)
    print("Data is here: ")
    data_dir = utils.read_std(stdout)
    print(data_dir)

    com = "ipainstaller -i " + package_name + " | grep Bundle | awk '{print $2}'"
    stdin, stdout, stderr = client.exec_command(com)
    print("Bundle is here: ")
    bundle_dir = utils.read_std(stdout)
    print(bundle_dir)

    try:
        get_bundledir = "scp -r root@" + ip + ":" + bundle_dir + " ."      
        get_datadir = "scp -r root@" + ip + ":" + data_dir + " ."

        '''fname = tempfile.mktemp()                                                                                                                                                  
        fout = open(fname, 'w')   '''

        print("Copying bundle dir into current dir.....")
        child = pexpect.spawnu(get_bundledir, timeout=30)  #spawnu for Python 3                                                                                                                          
        child.expect(['[pP]assword: '])                                                                                                                                                                                                                                                                                               
        child.sendline(passw)                                                                                                                                                   
        # child.logfile = fout                                                                                                                                                       
        child.expect(pexpect.EOF)                                                                                                                                                  
        child.close()                                                                                                                                                              
        # fout.close()                                                                                                                                                               

        '''fin = open(fname, 'r')                                                                                                                                                     
        stdout = fin.read()                                                                                                                                                        
        fin.close()                                                                                                                                                                

        if 0 != child.exitstatus:                                                                                                                                                  
            raise Exception(stdout)  '''

        print("Copying data dir into current dir.....")
        child = pexpect.spawnu(get_datadir, timeout=30)  #spawnu for Python 3                                                                                                                          
        child.expect(['[pP]assword: '])                                                                                                                                                                                                                                                                                               
        child.sendline(passw)                                                                                                                                                   
        # child.logfile = fout                                                                                                                                                       
        child.expect(pexpect.EOF)                                                                                                                                                  
        child.close()     
        
    except subprocess.CalledProcessError:
        print('Ooops, Something went awry!')


def analyse_app_data(f_secrets, case_dir):
    logger.info2("================================================================================================")
    logger.info2("====================================RUNNING GREP================================================")
    logger.info2("================================================================================================") 

    with open(f_secrets, "r") as f:
        secrets_hashtable = {k:str(v).lstrip("[").rstrip("]").strip("\'") for k, *v in (line.strip().split(":") for line in f)}

    # for local data analysis
    for secret in secrets_hashtable:
        logger.info("Running grep to search app data for {}={} leak: ".format(secret,secrets_hashtable[secret]), "grep -ri " + secrets_hashtable[secret] + " \"" + os.path.join(settings.project_dir, settings.os) + "/app_data" + "\"" + " > " + "\"" + case_dir + "/app_data" + "/" + secret + ".txt\" --color=always") 
        result = os.popen("grep -ria " + secrets_hashtable[secret] + " \"" + os.path.join(settings.project_dir, settings.os) + "/app_data" + "\"" + " > " + "\"" + case_dir + "app_data/" + secret + ".txt\" --color=always") 
    
    print("")
    for secret in secrets_hashtable:
        logger.info("Running grep to search logs for {}={} leak: ".format(secret,secrets_hashtable[secret]), "grep -ri " + secrets_hashtable[secret] + " \"" + os.path.join(settings.project_dir, settings.os) + "/logs" + "\"" + " > " + "\"" + case_dir + "/logs" + "/" + secret + ".txt\" --color=always") 
        os.popen("grep -ria " + secrets_hashtable[secret] + " \"" + os.path.join(settings.project_dir, settings.os) + "/logs" + "\"" + " > " + "\"" + case_dir + "logs/" + secret + ".txt\" --color=always") 
    
    print("")
    for secret in secrets_hashtable:
        logger.info("Running grep to search memory dump for {}={} leak: ".format(secret,secrets_hashtable[secret]), "grep -ri " + secrets_hashtable[secret] + " \"" + os.path.join(settings.project_dir, settings.os) + "/memory" + "\"" + " > " + "\"" + case_dir + "/memory" + "/" + secret + ".txt\" --color=always") 
        os.popen("grep -ria " + secrets_hashtable[secret] + " \"" + os.path.join(settings.project_dir, settings.os) + "/memory" + "\"" + " > " + "\"" + case_dir + "memory/" + secret + ".txt\" --color=always") 
    
    print("")
    for secret in secrets_hashtable:
        logger.info("Running grep to search backups for {}={} leak: ".format(secret,secrets_hashtable[secret]), "grep -ri " + secrets_hashtable[secret] + " \"" + os.path.join(settings.project_dir, settings.os) + "/backup" + "\"" + " > " + "\"" + case_dir + "/backup" + "/" + secret + ".txt\" --color=always") 
        os.popen("grep -ria " + secrets_hashtable[secret] + " \"" + os.path.join(settings.project_dir, settings.os) + "/backup" + "\"" + " > " + "\"" + case_dir + "backup/" + secret + ".txt\" --color=always") 
    
    if settings.os == "ios/":
        print("")
        for secret in secrets_hashtable:
            logger.info("Running grep to search keychain data for {}={} leak: ".format(secret,secrets_hashtable[secret]), "grep -ri " + secrets_hashtable[secret] + " \"" + os.path.join(settings.project_dir, settings.os) + "/backup" + "\"" + " > " + "\"" + case_dir + "/backup" + "/" + secret + ".txt\" --color=always") 
            os.popen("grep -ria " + secrets_hashtable[secret] + " \"" + os.path.join(settings.project_dir, settings.os) + "/keychain.json" + "\"" + " > " + "\"" + case_dir + "keychain/" + secret + ".txt\" --color=always") 
    delete_empty_files(secrets_hashtable, case_dir)
    

def delete_empty_files(secrets_hashtable, case_dir):
    logger.info2("================================================================================================")
    logger.info2("====================================CLEANING UP=================================================")
    logger.info2("================================================================================================") 
    
    for secret in secrets_hashtable:
        data_dir = os.path,join(settings.project_dir, settings.os)
        app_data_results = os.path,join(settings.results_dir, "app_data/")
        log_results = os.path,join(settings.results_dir, "logs/")
        memory_results = os.path,join(settings.results_dir, "memory/")
        backup_results = os.path,join(settings.results_dir, "backup/")
        keychain_results = os.path,join(settings.results_dir, "keychain/")

        if Path(app_data_results + secret + ".txt").stat().st_size <= 0:
            logger.error("No result for {} in {}. Deleting the file with ".format(secret, "app_data"), "rm \"" + app_data_results + secret + ".txt\"") 
            os.popen("rm \"" + app_data_results + secret + ".txt\"")
        else:
            time.sleep(1) # Sleep for 3 seconds
            logger.cmd("Cleaning with sed....", "sed -i'.original' " + "'s/" + data_dir.replace("/", "\/") + "/ /g' \"" + app_data_results +  secret + ".txt\"")
            os.popen("sed -i'.original' " + "'s/" + data_dir.replace("/", "\/") + "/ /g' \"" + app_data_results +  secret + ".txt\"")
            #logger.cmd("Deleting stupid sed backups: ", "cd \"" + app_data_results + "\" && rm *.original")
            #os.popen("cd \"" + app_data_results + "\" && rm *.original")
        print("")

        if Path(log_results + secret + ".txt").stat().st_size <= 0:
            logger.error("No result for {} in {}. Deleting the file with ".format(secret, "logs"), "rm \"" + log_results + secret + ".txt\"") 
            os.popen("rm \"" + log_results + secret + ".txt\"")
        else:
            time.sleep(1) # Sleep for 3 seconds
            logger.cmd("Cleaning with sed....", "sed -i'.original' " + "'s/" + data_dir.replace("/", "\/") + "/ /g' \"" + log_results +  secret + ".txt\"")
            os.popen("sed -i'.original' " + "'s/" + data_dir.replace("/", "\/") + "/ /g' \"" + log_results +  secret + ".txt\"")
            #logger.cmd("Deleting stupid sed backups: ", "cd \"" + log_results + "\" && rm *.original")
            #os.popen("cd \"" + log_results + "\" && rm *.original")
        
        print("")
        if Path(memory_results + secret + ".txt").stat().st_size <= 0:
            logger.error("No result for {} in {}. Deleting the file with ".format(secret, "memory dumps"), "rm \"" + memory_results + secret + ".txt\"") 
            os.popen("rm \"" + memory_results + secret + ".txt\"")
        else:
            time.sleep(1) # Sleep for 3 seconds
            logger.cmd("Cleaning with sed....", "sed -i'.original' " + "'s/" + data_dir.replace("/", "\/") + "/ /g' \"" + memory_results +  secret + ".txt\"")
            os.popen("sed -i'.original' " + "'s/" + data_dir.replace("/", "\/") + "/ /g' \"" + memory_results +  secret + ".txt\"")

        print("")
        if Path(backup_results + secret + ".txt").stat().st_size <= 0:
            logger.error("No result for {} in {}. Deleting the file with ".format(secret, "backup"), "rm \"" + backup_results + secret + ".txt\"") 
            os.popen("rm \"" + backup_results + secret + ".txt\"")
        else:
            time.sleep(1) # Sleep for 3 seconds
            logger.cmd("Cleaning with sed....", "sed -i'.original' " + "'s/" + data_dir.replace("/", "\/") + "/ /g' \"" + backup_results +  secret + ".txt\"")
            os.popen("sed -i'.original' " + "'s/" + data_dir.replace("/", "\/") + "/ /g' \"" + backup_results +  secret + ".txt\"")


        print("")
        if Path(keychain_results + secret + ".txt").stat().st_size <= 0:
            logger.error("No result for {} in {}. Deleting the file with ".format(secret, "backup"), "rm \"" + keychain_results + secret + ".txt\"") 
            os.popen("rm \"" + keychain_results + secret + ".txt\"")
        else:
            time.sleep(1) # Sleep for 3 seconds
            logger.cmd("Cleaning with sed....", "sed -i'.original' " + "'s/" + data_dir.replace("/", "\/") + "/ /g' \"" + keychain_results +  secret + ".txt\"")
            os.popen("sed -i'.original' " + "'s/" + data_dir.replace("/", "\/") + "/ /g' \"" + keychain_results +  secret + ".txt\"")

        
    print("")
    time.sleep(1) # Sleep for 3 seconds
    logger.cmd("Deleting stupid sed backups: ", "cd \"" + settings.results_dir + "\" && ./clean.sh")
    os.popen("cd \"" + settings.results_dir + "\" && ./clean.sh")
