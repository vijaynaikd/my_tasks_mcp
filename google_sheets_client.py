import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Define the scope
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

# Add your service account credentials
creds = ServiceAccountCredentials.from_json_keyfile_name("googleserviceaccount.json", scope)

# Authorize the client
client = gspread.authorize(creds)

# Open the Google Sheet
sheet = client.open("MyTasks").sheet1
