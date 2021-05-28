import re
import logging
import warnings
from random import choice
from urllib.parse import unquote
import base64
from datetime import date


project_name = ""
project_dir = ""
path_to_abe = ""
os = ""
secrets_file = os.path.join(project_dir, "secrets.txt")
results_dir = os.path.join(project_dir, os, "secrets_found/")
today = str(date.today())

# logging to file
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s [%(levelname)s] - %(message)s',
    filename= os.path.join(project_dir,os) + "/mobelflog_" + today + ".txt")

test_desc = """ """

client = ""
device = ""

# to ignore cert error
# warnings.filterwarnings("ignore")

# =============================================
# ====================PATTERNS=================
# =============================================
# regex для параметров POST запросов


# all requests are logged in Burp as well
proxies = {
 "https": "http://127.0.0.1:8080"
}

# Colors  https://gist.github.com/vratiu/9780109
Color_Off="\033[0m"
Black="\033[0;30m"        
Red="\033[0;31m"    
Green="\033[0;32m"        
Yellow="\033[0;33m"  
Blue="\033[0;34m"         
Purple="\033[0;35m"       
Cyan="\033[0;36m"         
White="\033[0;37m" 