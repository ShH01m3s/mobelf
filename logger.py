import settings
import re
import os


def info(description, data):
    settings.logging.info(settings.Color_Off + description + settings.Info + data + settings.Color_Off)
    print(settings.Color_Off + description + settings.Info + data + settings.Color_Off)

def info2(description):
    settings.logging.info(settings.Important + description + settings.Color_Off)
    print(settings.Important + description + settings.Color_Off)

def cmd(description, data):
    settings.logging.info(settings.Color_Off + description + settings.Cmd + data + settings.Color_Off)
    print(settings.Color_Off + description + settings.Cmd + data + settings.Color_Off)


def error(description, data):
    settings.logging.info(settings.Color_Off + description + settings.Error + data + settings.Color_Off)
    print(settings.Color_Off + description + settings.Error + data + settings.Color_Off)


def error2(description):
    settings.logging.info(settings.Error + description + settings.Color_Off)
    print(settings.Error + description + settings.Color_Off)
