import argparse
import os
import sys
import paramiko
import time
import app_crawler 
import utils
import forensic_crawler
import settings




# Create the parser
my_parser = argparse.ArgumentParser(prog="MobElf", 
                                    description='This program is designed to automate some routine tasks when aseessing or investigating mobile devices. For full analysis jailbreaking/rooting is required.')

# Add the arguments
# May be reading from a file is better
my_parser.add_argument('OS',
                        type=str,
                        help="Specify OS type to get correct analysis and crawling: iOS and Android are currently supported: os or android.")

my_parser.add_argument('-i', '--ip',
                       type=str,
                       help='the IP of iDevice in question',
                       action= "store", 
                       default="192.168.1.2")

my_parser.add_argument('-p', '--password',
                       type=str,
                       action= "store", 
                       help='SSH password for iDevice',
                       default="alpine")

# TODO here set some var to enter many application names
my_parser.add_argument('-a', '--application', 
                        type=str, 
                        action= "store", 
                        help="Specifify application for recon and secrets collection. By default, all applications are analyzed")

# my_parser.add_argument('-f', '--forensics', 
#                         action= "store_true", 
#                         help="For forensics crawl add this option")

my_parser.add_argument('-c', '--casedir', 
                        action= "store", 
                        help="Specify the directory to save collected data. Default is current directory.",
                        default=".")

my_parser.add_argument('-n', '--project_name', 
                        action= "store", 
                        help="Specify the directory to save collected data. Default is current directory.",
                        default=".")



# Execute the parse_args() method
args = my_parser.parse_args()
settings.os = args.OS
ip = args.ip
passw = args.password
case_dir, settings.project_dir = args.casedir
settings.project_name = args.project_name

# For iOS 
if args.OS == "ios":
    # client = utils.open_ssh_session(ip, passw)
    # stdin, stdout, stderr = client.exec_command("pwd")

    # forensic_crawler.device_info(case_dir)

    # if args.application:
    #    app_crawler.fetch_all_app_data_ios(client, args.application, ip, passw)

    # if args.forensics:
    #    forensic_crawler.crawl()
    # client.close()
    app_crawler.analyse_app_data(settings.secrets_file, settings.results_dir)

elif args.OS == "android":
    # app_crawler.fetch_all_app_data_android("ru.safmar.android")
    app_crawler.analyse_app_data(settings.secrets_file, settings.results_dir)
    # get package name
    # get base.apk
    # adb shell && su && cd 

else: 
    print("Please specify OS: iOS or Android")



