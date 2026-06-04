"""
This module contains configurations needed for the script to work.
SITE_URL -- the url of the site, ends with /sites/{site_name}
EXCEL_RELATIVE -- the relative path of the excel sheet in sharepoint
BROWSER_PROFILE_DIR - the path to the msedge profile which the script use
"""

import os
from dotenv import load_dotenv

load_dotenv()  # gives the script access to the .env file in project root
# we use os.environ because these configs are required, as opposed to os.getenv which can return None

# this is the sharepoint site URL
SITE_URL = os.environ["SITE_URL"]

# this is a server-relative path, not the URL
EXCEL_URL = os.environ["EXCEL_URL"]

# this is the path to the browser profile, which playwright needs to open a persistent context and
# make requests using the cookies from that login.
BROWSER_PROFILE_DIR = os.environ["BROWSER_PROFILE_DIR"]

# this is the current letter of the companies that we are checking (ranges from [A-Z])
CURRENT_LETTER = os.environ["CURRENT_LETTER"]

# this is the raw url of the company list ("Credence - Corp Sec -> List from A-Z")
COMPANY_LIST_BY_LETTER_PATH = os.environ["COMPANY_LIST_BY_LETTER_PATH"]

# path to local folder where files will be downloaded
WORKSPACE_PATH = os.environ["WORKSPACE_PATH"]

# the current year. determines the name of folder created in 'Sentroweb Search'
CURRENT_YEAR = os.environ["CURRENT_YEAR"]
