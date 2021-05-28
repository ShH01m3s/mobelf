import base64
import zlib
from urllib.parse import unquote, quote
import re
from yattag import indent
import logging
import warnings
import settings
import paramiko

def open_ssh_session(ip, passw):
    try:
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.connect(ip, username="root", password=passw)
        return client
    except:
        "Failed to establish connection to iDevice"

def open_adb_session():
    return

def read_std(stdout):
    stdout = stdout.readlines()
    output = ""
    for line in stdout:
        output=output+line
        if output!="":
            return output.strip()
        else:
            print("There was no output for this command")
            return ""     

# This is to beautify xml string
def pretty_print_xml(xml_str):
    pretty_string = indent(xml_str, indentation = '    ', newline = '\r\n')
    return pretty_string

def urlbase64_decode(enc):
    res = pretty_print_xml(str(base64.b64decode(unquote(enc))))
    print(res)
    return res

def decode_unicode(test):
    utf8_bytes = [int(hex(ord(char)), 16) for char in test]
    unicode_codes = []
    unicode_code = 0
    num_followed = 0
    for i in range(0, len(utf8_bytes)):
        utf8_byte = utf8_bytes[i]
        """ if (utf8_byte >= 0x100):
            print("Malformed utf8 byte ignored.") """
        if (utf8_byte & 0xC0) == 0x80:
            if num_followed > 0:
                unicode_code = (unicode_code << 6) | (utf8_byte & 0x3f)
                num_followed -= 1
            """ else:
                print("Malformed UTF-8 sequence ignored.") """
        else:
            if num_followed == 0:
                unicode_codes.append(unicode_code)
            """ else:
                print("Malformed UTF-8 sequence ignored.") """
            if (utf8_byte < 0x80):
                # 1-byte
                unicode_code = utf8_byte
                num_followed = 0
            elif (utf8_byte & 0xE0) == 0xC0: 
                # 2-byte
                unicode_code = utf8_byte & 0x1f
                num_followed = 1
            elif (utf8_byte & 0xF0) == 0xE0:
                # 3-byte
                unicode_code = utf8_byte & 0x0f
                num_followed = 2
            elif (utf8_byte & 0xF8) == 0xF0 : 
                # 4-byte
                unicode_code = utf8_byte & 0x07
                num_followed = 3
            """ else:
                print("Malformed UTF-8 sequence ignored.") """
    if num_followed == 0:
        unicode_codes.append(unicode_code)
    """ else:
        print("Malformed UTF-8 sequence ignored.") """
    decoded = ([chr(ch) for ch in unicode_codes])
    return "".join(decoded) 

