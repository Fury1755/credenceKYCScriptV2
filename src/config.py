'''
This module contains configurations needed for the script to work.
SITE_URL -- the url of the site, ends with /sites/{site_name}
EXCEL_RELATIVE -- the relative path of the excel sheet in sharepoint
BROWSER_PROFILE_DIR - the path to the msedge profile which the script use
'''
import os
from dotenv import load_dotenv

load_dotenv() #gives the script access to the .env file in project root
#we use os.environ because these configs are required, as opposed to os.getenv

def get_env(key: str) -> str:
    env_value = os.environ[key] #guaranteed to return a string or raise an exception, so no error checking needed
    return env_value

#this is the sharepoint site URL
SITE_URL = get_env("SITE_URL")

#this is a server-relative path, not the URL
EXCEL_RELATIVE_PATH = get_env("EXCEL_RELATIVE_PATH")

#this is the path to the browser profile, which playwright needs to open a persistent context and
#make requests using the cookies from that login.
BROWSER_PROFILE_DIR = get_env("BROWSER_PROFILE_DIR")

#this is the current letter of the companies that we are checking (ranges from [A-Z])
CURRENT_LETTER = get_env("CURRENT_LETTER")