import json
import os
import gspread
from google.oauth2.service_account import Credentials
import re

def sanitize_filename(filename):
    """Replace / with _ for safe filenames or folder names."""
    return filename.replace('/', '_')

def get_failed_files(json_path):
    """Extract 'file' values where success == False."""
    failed_files = []
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    for element in data:
        if not element.get('success', True):
            failed_files.append(element['file'])

            # # Optional: Write files locally as in your original script
            # file_comment = f"# {element['file']}\n"
            # safe_folder = sanitize_filename(element['file'])
            # os.makedirs(safe_folder, exist_ok=True)
            # with open(os.path.join(safe_folder, 'input.txt'), 'w', encoding='utf-8') as fi:
            #     fi.write(file_comment)
            #     fi.write(element.get('input', ''))
            # with open(os.path.join(safe_folder, 'pred.txt'), 'w', encoding='utf-8') as fp:
            #     fp.write(file_comment)
            #     fp.write(element.get('pred', ''))
            # with open(os.path.join(safe_folder, 'gd.txt'), 'w', encoding='utf-8') as fg:
            #     fg.write(file_comment)
            #     fg.write(element.get('gt', ''))
    return failed_files

def update_sheet_with_failed_files(sheet, files):
    """Write the failed file names to column A, starting from A2."""
    # Prepare data as a column
    values = [[file] for file in files]
    # Update column A, starting at A2
    cell_range = f'A2:A{len(values)+1}'
    sheet.update(cell_range, values)

#Sort the col A -> dile names
def natural_key(s):
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]

def sort_column_a_naturally(sheet):
    values = sheet.col_values(1)[1:]  # Skip header A1
    values = [v for v in values if v.strip()]
    values_sorted = sorted(values, key=natural_key)
    # Overwrite sorted values to A2:A...
    cell_range = f'A2:A{len(values_sorted)+1}'
    sheet.update(cell_range, [[v] for v in values_sorted])

if __name__ == '__main__':

    # --- 1. Setup Google Sheets connection
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file('auth.json', scopes=SCOPES)
    client = gspread.authorize(creds)
    spreadsheet_url = 'https://docs.google.com/spreadsheets/d/1xkuqH3ECo4TN-LgewwVQZKpFYqKi7dEHIyw3XKCNNKs/edit?gid=0#gid=0'
    spreadsheet = client.open_by_url(spreadsheet_url)
    sheet = spreadsheet.get_worksheet(0)

    # # --- 2. Parse JSON and get failed file names
    # failed_files = get_failed_files('results_armv8_O2 1.json')

    # # --- 3. Write to Google Sheet (A2:A...)
    # update_sheet_with_failed_files(sheet, failed_files)

    # print(f"Wrote {len(failed_files)} failed files to sheet column A.")

    # --- 4 Sort the column A
    sort_column_a_naturally(sheet)

