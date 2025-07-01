import gspread
from google.oauth2.service_account import Credentials

# Scope for reading/writing to Google Sheets
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# Authenticate
creds = Credentials.from_service_account_file('auth.json', scopes=SCOPES)
client = gspread.authorize(creds)

# Open the spreadsheet by URL
spreadsheet_url = 'https://docs.google.com/spreadsheets/d/1xkuqH3ECo4TN-LgewwVQZKpFYqKi7dEHIyw3XKCNNKs/edit?gid=0#gid=0'
spreadsheet = client.open_by_url(spreadsheet_url)

# Select the first worksheet
sheet = spreadsheet.get_worksheet(0)

# Read all values
data = sheet.get_all_values()
print(data)

# Read a specific cell (A1)
value = sheet.acell('A1').value
print("A1:", value)

# Update a cell (for example, A2)
sheet.update('A2', [['Hello from Python!']])
