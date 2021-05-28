import os

def crawl():
    return

def device_info(case_dir):
    udid = os.popen("idevice_id -l").read()
    os.popen("ideviceinfo > " + case_dir + "/device" + udid + "_info.txt")
    print("Device UDID: " + udid)
    print("All data is saved in txt in case directory")    

def collect(device, case_dir):
    os.popen("frida-ps -H " + device + " > " + case_dir + "/processes.txt")