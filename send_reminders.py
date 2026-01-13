"""
Reminder Email Sender Script for Grant Tracker

This script identifies people who received the initial email but haven't responded,
and sends them shorter reminder emails via Gmail SMTP.
"""

import argparse
import os
import smtplib
from datetime import date
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import gspread
from dotenv import load_dotenv
from oauth2client.service_account import ServiceAccountCredentials

from email_generator import generate_form_url, load_config


def create_reminder_email_body(name, form_url, grant_deadline):
    """
    Create shorter HTML reminder email body.
    
    Generates a concise reminder email template with:
    - Personalized greeting
    - Brief reminder message
    - Call-to-action button linking to the form
    - Deadline urgency message
    
    Args:
        name (str): Recipient's name for personalization
        form_url (str): Pre-filled Google Form URL for the call-to-action
        grant_deadline (str): Deadline date for the grant application
        
    Returns:
        str: Complete HTML reminder email body as a string
    """
    email_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reminder: Grant Support Request</title>
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
                            <!-- Reminder message -->
                            <p style="margin: 0 0 20px 0; color: #555555; font-size: 16px; line-height: 1.6;">
                                We haven't received your response yet. Your support is important! 
                                This is a friendly reminder about the grant support request we sent earlier.
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
    Main function to send reminder emails to non-responders.
    
    Workflow:
    1. Parse command-line arguments for batch size (optional)
    2. Load configuration and Gmail App Password
    3. Connect to Google Sheets
    4. Read master sheet and responses sheet
    5. Identify non-responders (Status="Sent", not in responses, ReminderSent empty)
    6. Send reminder emails to non-responders
    7. Update ReminderSent column for successful sends
    8. Print summary of results
    """
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description='Send reminder emails to non-responders for grant support campaign'
    )
    parser.add_argument(
        '--size',
        type=int,
        default=None,
        help='Number of reminder emails to send (default: all non-responders)'
    )
    args = parser.parse_args()
    batch_size = args.size
    
    print("="*60)
    print("Grant Tracker - Reminder Email Sender")
    print("="*60)
    if batch_size:
        print(f"Batch size: {batch_size}")
    else:
        print("Batch size: All non-responders")
    print()
    
    try:
        # Load configuration
        print("Loading configuration...")
        config = load_config()
        print("Configuration loaded successfully.")
        
        # Debug output to verify config value
        print(f"Debug - responses_sheet_tab from config: '{config['responses_sheet_tab']}'")
        
        # Load environment variables from .env file
        print("Loading environment variables...")
        if not os.path.exists('.env'):
            raise FileNotFoundError(
                ".env file not found. Please create .env file with GMAIL_APP_PASSWORD."
            )
        
        load_dotenv()
        gmail_app_password = os.getenv('GMAIL_APP_PASSWORD')
        
        if not gmail_app_password:
            raise ValueError(
                "GMAIL_APP_PASSWORD not found in .env file. "
                "Please add GMAIL_APP_PASSWORD=your_password to .env"
            )
        
        print("Environment variables loaded successfully.")
        
        # Check if credentials file exists
        credentials_path = 'credentials.json'
        if not os.path.exists(credentials_path):
            raise FileNotFoundError(
                f"Google Service Account credentials file '{credentials_path}' not found. "
                "Please download credentials.json from Google Cloud Console and place it in the project root."
            )
        
        # Set up Google Sheets API authentication
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
        
        # Debug output: List all available worksheets
        print("Available worksheets in this spreadsheet:")
        for worksheet in sheet.worksheets():
            print(f"  - '{worksheet.title}'")
        print()
        
        # Access the master sheet tab
        print(f"Accessing master worksheet: {config['master_sheet_tab']}...")
        master_worksheet = sheet.worksheet(config['master_sheet_tab'])
        
        # Access the responses sheet tab
        print(f"Accessing responses worksheet: {config['responses_sheet_tab']}...")
        try:
            responses_worksheet = sheet.worksheet(config['responses_sheet_tab'])
        except gspread.exceptions.WorksheetNotFound:
            print(f"Warning: Responses worksheet '{config['responses_sheet_tab']}' not found.")
            print("Assuming no responses yet - all people with Status='Sent' are non-responders.")
            responses_worksheet = None
        
        # Column indices based on Master Sheet structure
        NAME_COLUMN = 0      # Column A
        EMAIL_COLUMN = 1     # Column B
        STATUS_COLUMN = 4    # Column E
        REMINDERSENT_COLUMN = 6  # Column G
        
        # Read all rows from master sheet
        print("Reading data from master sheet...")
        master_all_rows = master_worksheet.get_all_values()
        
        if len(master_all_rows) < 2:
            print("Warning: Master sheet appears to be empty or only contains headers.")
            return
        
        # Read all rows from responses sheet (if it exists)
        responder_names = set()
        if responses_worksheet:
            print("Reading data from responses sheet...")
            responses_all_rows = responses_worksheet.get_all_values()
            
            # Skip header row (index 0), extract names from responses sheet
            # Column 0 is Timestamp, Column 1 is Name field
            if len(responses_all_rows) > 1:
                for row in responses_all_rows[1:]:  # Skip header
                    if len(row) > 1 and row[1]:  # Check column 1 (Name field)
                        # Normalize name for comparison (strip and lowercase)
                        # Column 1 is the Name field (Column 0 is Timestamp)
                        name = str(row[1]).strip()
                        if name and name.lower() != 'name':  # Skip header if it leaked through
                            responder_names.add(name.lower())
            
            print(f"Found {len(responder_names)} unique responders in responses sheet.")
            # Debug output to show responder names
            print(f"Debug - Responder names found: {responder_names}")
        else:
            print("No responses sheet found - all people with Status='Sent' are non-responders.")
        
        # Skip header row (index 0), process data rows only
        # all_rows[0] is the header, all_rows[1:] are data rows
        master_data_rows = master_all_rows[1:]
        
        # Identify non-responders
        # Logic: Status="Sent" AND Name NOT in responder_names AND ReminderSent is empty
        print()
        print("Checking for non-responders...")
        non_responders = []
        
        for i, row in enumerate(master_data_rows):
            # Calculate actual row index in sheet (i+2 because row 1 is header, row 2 is first data row)
            row_index = i + 2
            
            # Safety check: Skip if Name column contains "Name" (in case header leaked through)
            if len(row) > 0 and str(row[0]).strip().lower() == 'name':
                continue
            
            # Extract name for comparison
            if len(row) <= NAME_COLUMN:
                continue
            
            name = str(row[NAME_COLUMN]).strip() if row[NAME_COLUMN] else ""
            if not name:
                continue
            
            # Check Status column (index 4, column E) - must be "Sent"
            if len(row) > STATUS_COLUMN:
                status = str(row[STATUS_COLUMN]).strip() if row[STATUS_COLUMN] else ""
            else:
                status = ""
            
            if status != "Sent":
                continue  # Skip if email wasn't sent yet
            
            # Check if name is in responder_names set (case-insensitive comparison)
            # Normalize name the same way as when building responder_names (name is already stripped, just lowercase)
            name_lower = name.lower()
            print(f"Debug - Checking name: '{name}' (lowercase: '{name_lower}')")
            print(f"Debug - Name in responder_names: {name_lower in responder_names}")
            if name_lower in responder_names:
                print(f"Debug - Skipping {name} - already responded")
                continue  # Skip if they already responded
            
            # Check ReminderSent column (index 6, column G) - must be empty
            if len(row) > REMINDERSENT_COLUMN:
                reminder_sent = str(row[REMINDERSENT_COLUMN]).strip() if row[REMINDERSENT_COLUMN] else ""
            else:
                reminder_sent = ""
            
            if reminder_sent:
                continue  # Skip if reminder already sent
            
            # All conditions met - this is a non-responder who needs a reminder
            non_responders.append((row_index, row))
        
        print(f"Found {len(non_responders)} people who haven't responded.")
        print()
        
        if not non_responders:
            print("No reminders to send. All people have either responded or already received reminders.")
            return
        
        # Limit to batch size if specified
        if batch_size:
            rows_to_process = non_responders[:batch_size]
            print(f"Processing {len(rows_to_process)} reminders (limited by --size={batch_size}).")
        else:
            rows_to_process = non_responders
            print(f"Processing all {len(rows_to_process)} reminders.")
        print()
        
        # Initialize counters
        sent_count = 0
        failed_count = 0
        
        # Get today's date for ReminderSent column
        today_date = date.today().strftime('%Y-%m-%d')
        
        # Process each non-responder
        print("="*60)
        print("Sending Reminders:")
        print("="*60)
        
        for row_index, row in rows_to_process:
            try:
                # Extract name and email from row
                if len(row) <= NAME_COLUMN:
                    print(f"Row {row_index}: Missing name column, skipping...")
                    failed_count += 1
                    continue
                
                name = str(row[NAME_COLUMN]).strip() if row[NAME_COLUMN] else ""
                
                if not name:
                    print(f"Row {row_index}: Empty name field, skipping...")
                    failed_count += 1
                    continue
                
                if len(row) <= EMAIL_COLUMN:
                    print(f"Row {row_index} ({name}): Missing email column, skipping...")
                    failed_count += 1
                    continue
                
                email_address = str(row[EMAIL_COLUMN]).strip() if len(row) > EMAIL_COLUMN else ""
                
                if not email_address:
                    print(f"Row {row_index} ({name}): Empty email field, skipping...")
                    failed_count += 1
                    continue
                
                # Validate email format (basic check)
                if '@' not in email_address:
                    print(f"Row {row_index} ({name}): Invalid email format ({email_address}), skipping...")
                    failed_count += 1
                    continue
                
                print(f"Sending reminder to: {name} ({email_address})...", end=' ', flush=True)
                
                # Generate personalized form URL
                form_url = generate_form_url(
                    name,
                    config['form_base_url'],
                    config['name_field_id']
                )
                
                # Create reminder email body HTML
                reminder_email_html = create_reminder_email_body(
                    name,
                    form_url,
                    config['grant_deadline']
                )
                
                # Create email message
                msg = MIMEMultipart('alternative')
                msg['From'] = f"{config['sender_name']} <{config['sender_email']}>"
                msg['To'] = email_address
                msg['Subject'] = f"Reminder: Grant Support Needed by {config['grant_deadline']}"
                
                # Attach HTML body
                html_part = MIMEText(reminder_email_html, 'html')
                msg.attach(html_part)
                
                # Send email via Gmail SMTP
                try:
                    # Connect to Gmail SMTP server
                    server = smtplib.SMTP('smtp.gmail.com', 587)
                    server.starttls()  # Enable TLS encryption
                    server.login(config['sender_email'], gmail_app_password)
                    server.send_message(msg)
                    server.quit()
                    
                    # Update Google Sheet: Mark ReminderSent with today's date
                    remindersent_cell = f'G{row_index}'
                    master_worksheet.update_acell(remindersent_cell, today_date)
                    
                    print("✓ Sent")
                    sent_count += 1
                    
                except smtplib.SMTPAuthenticationError as e:
                    error_msg = f"SMTP Authentication failed: {str(e)}"
                    print(f"✗ Failed: {error_msg}")
                    failed_count += 1
                    # Don't update ReminderSent on failure
                    
                except smtplib.SMTPException as e:
                    error_msg = f"SMTP error: {str(e)}"
                    print(f"✗ Failed: {error_msg}")
                    failed_count += 1
                    # Don't update ReminderSent on failure
                    
                except Exception as e:
                    error_msg = f"Unexpected error: {str(e)}"
                    print(f"✗ Failed: {error_msg}")
                    failed_count += 1
                    # Don't update ReminderSent on failure
            
            except Exception as e:
                # Handle any unexpected errors in processing a row
                print(f"Row {row_index}: Error processing row - {str(e)}")
                failed_count += 1
                continue
        
        # Print final summary
        print()
        print("="*60)
        print("Summary:")
        print("="*60)
        print(f"Reminders sent: {sent_count}, Failed: {failed_count}")
        print("="*60)
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
    except ValueError as e:
        print(f"Error: {e}")
    except gspread.exceptions.APIError as e:
        print(f"Error: Google Sheets API error: {e}")
    except gspread.exceptions.SpreadsheetNotFound:
        print(f"Error: Google Sheet not found. Please check the sheet_id in config.json.")
    except Exception as e:
        print(f"Unexpected error: {type(e).__name__}: {e}")


if __name__ == "__main__":
    main()
