import gspread
import os
import json
from google.oauth2.service_account import Credentials
from pathlib import Path

def upload_to_sheets(data):
    try:
        # Determine the correct path for creds.json
        creds_path = Path('services/creds.json')
        
        # For GitHub Actions where file is created from secret
        if not creds_path.exists():
            creds_path = Path('creds.json')
            
        if not creds_path.exists():
            raise FileNotFoundError("❌ creds.json file not found in services/ or root directory")

        # Load credentials from file
        with open(creds_path, 'r') as f:
            creds_info = json.load(f)
            
        scope = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        
        # Create credentials
        creds = Credentials.from_service_account_info(creds_info, scopes=scope)
        gc = gspread.authorize(creds)

        # Get sheet ID from environment
        sheet_id = os.getenv('GOOGLE_SHEET_ID')
        if not sheet_id:
            raise ValueError("❌ GOOGLE_SHEET_ID environment variable not found!")

        spreadsheet = gc.open_by_key(sheet_id)

        # Helper function to update worksheets
        def update_worksheet(sheet_name, df):
            values = [df.columns.tolist()] + df.values.tolist()
            try:
                worksheet = spreadsheet.worksheet(sheet_name)
            except gspread.WorksheetNotFound:
                worksheet = spreadsheet.add_worksheet(sheet_name, rows="1000", cols="20")
            worksheet.clear()
            worksheet.update("A1", values)
            print(f"✅ {sheet_name} uploaded ({len(values)-1} rows)")

        # Upload all data sections
        update_worksheet("Raw Data", data["raw_data"])
        update_worksheet("Stats", data["stats"])
        
        if "top_brands" in data:
            update_worksheet("Top Brands", data["top_brands"])
        if "top_expensive" in data:
            update_worksheet("Top Expensive", data["top_expensive"])
        if "best_deals" in data:
            update_worksheet("Best Deals", data["best_deals"])

        return True

    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse credentials JSON: {e}")
        return False
    except Exception as e:
        print(f"❌ Google Sheets upload error: {str(e)}")
        return False