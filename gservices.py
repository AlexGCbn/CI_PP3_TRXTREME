"""Google services module, used to store all Google services API data."""

# gspread -> Google Spreadsheets import
# build -> Used to build calendar
# Credentials -> Used with our credentials file, for access to Google APIs

import gspread
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials


# Scope required for Google Sheets, Calendar and Drive to work

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/calendar",
]


# Global variables used for Google Sheets and Calendar

# Credentials file
CREDS = Credentials.from_service_account_file("creds.json")
# Scoped credentials
SCOPED_CREDS = CREDS.with_scopes(SCOPE)
# Google Sheets authorization
GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)
# Opens selected Google Sheet
SHEET = GSPREAD_CLIENT.open("trxtreme")
# The selected Google Sheet ID
SHEET_ID = "1izyPTgGIt_uKegNn2I0lFUdrAuXPJisNeXgvzN2EG_g"
# Google Calendar service build
CALENDAR = build("calendar", "v3", credentials=CREDS)
# Google Calendar ID
CALENDAR_ID = "trxtreme2021@gmail.com"
