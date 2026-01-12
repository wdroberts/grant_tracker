"""
Email Generator Script for Grant Tracker

This script reads contact information from a Google Sheet, generates personalized
Google Form pre-fill URLs, and creates HTML email content with inline images.
"""

import json
import os
import urllib.parse

import gspread
from oauth2client.service_account import ServiceAccountCredentials


def load_config():
    """
    Load configuration from config.json file.
    
    Reads the config.json file from the project root and returns it as a dictionary.
    Includes error handling for missing file and JSON parsing errors.
    
    Returns:
        dict: Configuration dictionary containing all settings
        
    Raises:
        FileNotFoundError: If config.json does not exist
        json.JSONDecodeError: If config.json contains invalid JSON
    """
    config_path = 'config.json'
    
    # Check if config file exists
    if not os.path.exists(config_path):
        raise FileNotFoundError(
            f"Configuration file '{config_path}' not found. "
            "Please create config.json in the project root."
        )
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(
            f"Error parsing config.json: {e.msg}",
            e.doc,
            e.pos
        )


def generate_form_url(name, form_base_url, name_field_id):
    """
    Generate a Google Form pre-fill URL with the person's name pre-filled.
    
    Google Forms supports pre-filling form fields using URL parameters.
    The format is: base_url + "?usp=pp_url&entry." + field_id + "=" + encoded_value
    
    Args:
        name (str): The person's name to pre-fill in the form
        form_base_url (str): The base URL of the Google Form
        name_field_id (str): The entry ID of the name field in the Google Form
        
    Returns:
        str: Complete pre-fill URL with the name parameter encoded
        
    Example:
        >>> generate_form_url("John Doe", "https://forms.google.com/form", "123456")
        'https://forms.google.com/form?usp=pp_url&entry.123456=John+Doe'
    """
    # URL encode the name to handle special characters and spaces
    # This converts spaces to '+' or '%20' and handles special characters
    encoded_name = urllib.parse.quote(name)
    
    # Construct the pre-fill URL
    # Format: base_url?usp=pp_url&entry.FIELD_ID=ENCODED_VALUE
    prefill_url = f"{form_base_url}?usp=pp_url&entry.{name_field_id}={encoded_name}"
    
    return prefill_url


def create_email_body(name, form_url, grant_deadline, image_url):
    """
    Create HTML email body with personalized content and inline image.
    
    Generates a mobile-responsive HTML email template with:
    - Personalized greeting
    - Placeholder paragraphs for grant information
    - Inline image display
    - Call-to-action button linking to the form
    - Deadline urgency message
    
    Args:
        name (str): Recipient's name for personalization
        form_url (str): Pre-filled Google Form URL for the call-to-action
        grant_deadline (str): Deadline date for the grant application
        image_url (str): URL of the image to display inline in the email
        
    Returns:
        str: Complete HTML email body as a string
    """
    # HTML email template with inline CSS for email client compatibility
    # Using inline styles ensures better rendering across different email clients
    email_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Grant Support Request</title>
</head>
<body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #f4f4f4;">
    <!-- Main container with max-width for desktop and full-width on mobile -->
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color: #f4f4f4;">
        <tr>
            <td align="center" style="padding: 20px 0;">
                <!-- Email content container -->
                <table role="presentation" width="600" cellpadding="0" cellspacing="0" 
                       style="background-color: #ffffff; border-radius: 8px; max-width: 100%;">
                    
                    <!-- Header section -->
                    <tr>
                        <td style="padding: 30px 30px 20px 30px;">
                            <h1 style="margin: 0; color: #333333; font-size: 24px;">
                                Hi {name},
                            </h1>
                        </td>
                    </tr>
                    
                    <!-- Content section -->
                    <tr>
                        <td style="padding: 0 30px 20px 30px;">
                            <!-- First paragraph placeholder -->
                            <p style="margin: 0 0 15px 0; color: #555555; font-size: 16px; line-height: 1.6;">
                                [GRANT_PARAGRAPH_1]
                            </p>
                            
                            <!-- Second paragraph placeholder -->
                            <p style="margin: 0 0 15px 0; color: #555555; font-size: 16px; line-height: 1.6;">
                                [GRANT_PARAGRAPH_2]
                            </p>
                            
                            <!-- Inline image with responsive styling -->
                            <!-- Using table for image ensures better email client compatibility -->
                            <table role="presentation" width="100%" cellpadding="0" cellspacing="0" 
                                   style="margin: 20px 0;">
                                <tr>
                                    <td align="center">
                                        <img src="{image_url}" 
                                             alt="Grant Information" 
                                             style="max-width: 100%; height: auto; border-radius: 4px; display: block;"
                                             width="540">
                                    </td>
                                </tr>
                            </table>
                            
                            <!-- Third paragraph placeholder -->
                            <p style="margin: 0 0 20px 0; color: #555555; font-size: 16px; line-height: 1.6;">
                                [GRANT_PARAGRAPH_3]
                            </p>
                        </td>
                    </tr>
                    
                    <!-- Call-to-action button section -->
                    <tr>
                        <td align="center" style="padding: 0 30px 30px 30px;">
                            <!-- Button styled as a table for maximum email client compatibility -->
                            <table role="presentation" cellpadding="0" cellspacing="0">
                                <tr>
                                    <td align="center" style="background-color: #007bff; border-radius: 5px;">
                                        <a href="{form_url}" 
                                           style="display: inline-block; padding: 14px 30px; color: #ffffff; 
                                                  text-decoration: none; font-size: 16px; font-weight: bold;
                                                  border-radius: 5px;">
                                            Complete Your Response
                                        </a>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    
                    <!-- Deadline urgency message -->
                    <tr>
                        <td style="padding: 0 30px 30px 30px;">
                            <p style="margin: 0; color: #d9534f; font-size: 14px; font-weight: bold; text-align: center;">
                                Please respond by {grant_deadline}
                            </p>
                        </td>
                    </tr>
                    
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""
    return email_html


def main():
    """
    Main function to orchestrate the email generation process.
    
    Workflow:
    1. Load configuration from config.json
    2. Authenticate with Google Sheets API using Service Account credentials
    3. Open the specified Google Sheet
    4. Read the first 5 rows from the master sheet tab
    5. Generate pre-fill URLs for each person
    6. Create and preview email body for the first person
    
    Includes comprehensive error handling for:
    - Missing configuration file
    - Missing credentials file
    - Google Sheets API errors
    - Missing or malformed sheet data
    """
    try:
        # Load configuration
        print("Loading configuration...")
        config = load_config()
        print("Configuration loaded successfully.")
        
        # Check if credentials file exists
        credentials_path = 'credentials.json'
        if not os.path.exists(credentials_path):
            raise FileNotFoundError(
                f"Google Service Account credentials file '{credentials_path}' not found. "
                "Please download credentials.json from Google Cloud Console and place it in the project root."
            )
        
        # Set up Google Sheets API authentication
        # Using Service Account credentials for server-to-server authentication
        print("Authenticating with Google Sheets API...")
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            credentials_path,
            scope
        )
        client = gspread.authorize(credentials)
        print("Authentication successful.")
        
        # Open the Google Sheet using the sheet ID from config
        print(f"Opening Google Sheet (ID: {config['sheet_id']})...")
        sheet = client.open_by_key(config['sheet_id'])
        
        # Access the master sheet tab
        print(f"Accessing worksheet: {config['master_sheet_tab']}...")
        worksheet = sheet.worksheet(config['master_sheet_tab'])
        
        # Read rows from the sheet
        # Skip header row (index 0), read next 5 data rows
        print("Reading first 5 data rows from sheet (skipping header)...")
        all_rows = worksheet.get_all_values()
        
        if len(all_rows) < 2:
            print("Warning: Sheet appears to be empty or only contains headers.")
            return
        
        # Extract headers from first row
        headers = all_rows[0]
        print(f"Found columns: {', '.join(headers)}")
        
        # Skip header row (index 0), read next 5 data rows (indices 1-5)
        rows = all_rows[1:6]
        
        # Try to find the name column (common variations)
        name_column_index = None
        name_column_variations = ['name', 'Name', 'NAME', 'full name', 'Full Name', 'FULL NAME']
        
        for i, header in enumerate(headers):
            if header.strip() in name_column_variations:
                name_column_index = i
                break
        
        if name_column_index is None:
            print("Warning: Could not find a 'name' column. Using first column as name.")
            name_column_index = 0
        
        # Process each data row (header already skipped)
        print("\n" + "="*60)
        print("Generating form URLs for each person:")
        print("="*60)
        
        for i, row in enumerate(rows, start=1):  # Process data rows (header already skipped)
            try:
                # Extract name from the row, handling missing columns gracefully
                if name_column_index < len(row):
                    name = row[name_column_index].strip()
                else:
                    print(f"Row {i}: No name found (row too short)")
                    continue
                
                if not name:
                    print(f"Row {i}: Empty name field, skipping")
                    continue
                
                # Generate pre-fill URL for this person
                form_url = generate_form_url(
                    name,
                    config['form_base_url'],
                    config['name_field_id']
                )
                
                print(f"\nRow {i}: {name}")
                print(f"  Form URL: {form_url}")
                
                # For the first person, also generate and preview the email body
                if i == 1:
                    print("\n" + "="*60)
                    print("Email Body Preview (for first person):")
                    print("="*60)
                    email_body = create_email_body(
                        name,
                        form_url,
                        config['grant_deadline'],
                        config['image_url']
                    )
                    print(email_body)
                    print("="*60)
                    
            except Exception as e:
                print(f"Error processing row {i}: {str(e)}")
                continue
        
        print("\n" + "="*60)
        print("Email generation complete!")
        print("="*60)
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in config.json: {e}")
    except gspread.exceptions.APIError as e:
        print(f"Error: Google Sheets API error: {e}")
    except gspread.exceptions.SpreadsheetNotFound:
        print(f"Error: Google Sheet not found. Please check the sheet_id in config.json.")
    except Exception as e:
        print(f"Unexpected error: {type(e).__name__}: {e}")


if __name__ == "__main__":
    main()

