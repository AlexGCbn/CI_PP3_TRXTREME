"""
Google services module, used to store all Google services API data.
"""

import gspread
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials

"""
Scope required for Google Sheets, Calendar and Drive to work
"""
SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/calendar",
]

"""
Global variables used for Google Sheets and Calendar
"""
CREDS = Credentials.from_service_account_file("creds.json")  # Credentials file
SCOPED_CREDS = CREDS.with_scopes(SCOPE)  # Scoped credentials
GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)  # Google Sheets authorization
SHEET = GSPREAD_CLIENT.open("trxtreme")  # Opens selected Google Sheet
SHEET_ID = "1izyPTgGIt_uKegNn2I0lFUdrAuXPJisNeXgvzN2EG_g"  # The selected Google Sheet ID, used in some functions
CALENDAR = build("calendar", "v3", credentials=CREDS)  # Google Calendar service build
CALENDAR_ID = "trxtreme2021@gmail.com"  # Google Calendar ID
