import os
from os.path import join, dirname
from dotenv import load_dotenv
from logging import DEBUG, INFO, WARN, ERROR

def if_env(str):
    if str.upper() == 'TRUE':
        return True
    else:
        return False

def get_log_level(str):
    upper_str = str.upper()
    if upper_str == 'DEBUG':
        return DEBUG
    elif upper_str == 'INFO':
        return INFO
    elif upper_str == 'ERROR':
        return ERROR
    else:
        return WARN

load_dotenv(verbose=True)
dotenv_path = join(dirname(__file__), 'files' + os.sep + '.env')
load_dotenv(dotenv_path)

DISCORD_TOKEN = os.environ.get('DISCORD_TOKEN')
LOG_LEVEL = get_log_level(os.environ.get('LOG_LEVEL'))
AUDIT_LOG_SEND_CHANNEL = os.environ.get('AUDIT_LOG_SEND_CHANNEL')
IS_HEROKU = if_env(os.environ.get('IS_HEROKU'))
SAVE_FILE_MESSAGE = os.environ.get('SAVE_FILE_MESSAGE')
FIRST_REACTION_CHECK = if_env(os.environ.get('FIRST_REACTION_CHECK'))
SCRAPBOX_SID_AND_PROJECTNAME = os.environ.get('SCRAPBOX_SID_AND_PROJECTNAME')