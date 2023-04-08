import configparser
from pathlib import Path
import os

ginipath = Path(os.path.dirname(__file__)).parents[2] / 'yobot_data' / 'groups.ini'

def who_am_i(GID):
    '''Gimme a GID(int), return you a selfID(int) :)'''
    config=configparser.ConfigParser()
    config.read(str(ginipath))
    sid = config.get('GROUPS', str(GID))
    return int(sid)