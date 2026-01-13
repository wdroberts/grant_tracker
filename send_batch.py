"""
Batch Email Sender Script for Grant Tracker

This script sends personalized emails via Gmail SMTP, tracks sending status
in Google Sheets, and supports batch processing with configurable size.
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

from email_generator import create_email_body, generate_form_url, load_config


def main():
    """
    Main function to send batch emails via Gmail SMTP.
    
    Workflow:
    1. Parse command-line arguments for batch size
    2. Load configuration and Gmail App Password
    3. Connect to Google Sheets
    4. Filter rows with empty Status column
    5. Send emails to selected recipients
    6. Update Google Sheets with send status
    7. Print summary of results
    """
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description='Send batch emails for grant support campaign'
    )
    parser.add_argument(
        '--size',
        type=int,
        default=50,
        help='Number of emails to send in this batch (default: 50)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Run in dry-run mode (no emails sent, no sheet updates)'
    )
    args = parser.parse_args()
    batch_size = args.size
    
    print("="*60)
    print("Grant Tracker - Batch Email Sender")
    print("="*60)
    print(f"Batch size: {batch_size}")
    print()
    
    try:
        # Load configuration
        print("Loading configuration...")
        config = load_config()
        print("Configuration loaded successfully.")
        
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
        
        # Access the master sheet tab
        print(f"Accessing worksheet: {config['master_sheet_tab']}...")
        worksheet = sheet.worksheet(config['master_sheet_tab'])
        
        # Read all rows from the sheet
        print("Reading data from sheet...")
        all_rows = worksheet.get_all_values()
        
        if len(all_rows) < 2:
            print("Warning: Sheet appears to be empty or only contains headers.")
            return
        
        # Column indices based on Master Sheet structure
        NAME_COLUMN = 0      # Column A
        EMAIL_COLUMN = 1     # Column B
        STATUS_COLUMN = 4    # Column E
        SENTDATE_COLUMN = 5  # Column F
        
        # Skip header row (index 0), process data rows only
        # all_rows[0] is the header, all_rows[1:] are data rows
        data_rows = all_rows[1:]
        
        # Filter rows where Status column is empty (not yet sent)
        # Status column is at index 4 (column E)
        unsent_rows = []
        
        for i, row in enumerate(data_rows):
            # Calculate actual row index in sheet (i+2 because row 1 is header, row 2 is first data row)
            row_index = i + 2
            
            # Safety check: Skip if Name column contains "Name" (in case header leaked through)
            if len(row) > 0 and str(row[0]).strip().lower() == 'name':
                continue
            
            # Check if Status column exists and is empty/blank
            if len(row) > STATUS_COLUMN:
                status = str(row[STATUS_COLUMN]).strip() if row[STATUS_COLUMN] else ""
            else:
                status = ""
            
            # Only include rows with empty status
            if not status:
                unsent_rows.append((row_index, row))
        
        print(f"Found {len(unsent_rows)} rows with empty Status.")
        
        # Take first N rows based on batch size
        rows_to_process = unsent_rows[:batch_size]
        print(f"Processing {len(rows_to_process)} rows in this batch.")
        print()
        
        if not rows_to_process:
            print("No rows to process. All emails have been sent or no valid rows found.")
            return
        
        # Confirmation prompt (if not dry_run)
        if not args.dry_run:
            print()
            print("="*60)
            confirmation = input(f"Ready to send {len(rows_to_process)} emails. Continue? (yes/no): ")
            if confirmation.lower() not in ['y', 'yes']:
                print("Cancelled by user.")
                return
            print()
        
        # Initialize counters
        sent_count = 0
        failed_count = 0
        
        # Get today's date for SentDate column
        today_date = date.today().strftime('%Y-%m-%d')
        
        # Process each row
        print("="*60)
        print("Sending Emails:")
        print("="*60)
        
        for row_index, row in rows_to_process:
            try:
                # Extract name and email from row
                if len(row) <= NAME_COLUMN:
                    print(f"Row {row_index}: Missing name column, skipping...")
                    failed_count += 1
                    continue
                
                name = row[NAME_COLUMN].strip() if row[NAME_COLUMN] else ""
                
                if not name:
                    print(f"Row {row_index}: Empty name field, skipping...")
                    failed_count += 1
                    continue
                
                if len(row) <= EMAIL_COLUMN:
                    print(f"Row {row_index} ({name}): Missing email column, skipping...")
                    failed_count += 1
                    # Update status to indicate missing email
                    if not args.dry_run:
                        status_cell = f'E{row_index}'
                        worksheet.update_acell(status_cell, f"Failed - Missing email address")
                    continue
                
                email_address = str(row[EMAIL_COLUMN]).strip() if len(row) > EMAIL_COLUMN else ""
                
                if not email_address:
                    print(f"Row {row_index} ({name}): Empty email field, skipping...")
                    failed_count += 1
                    # Update status to indicate missing email
                    if not args.dry_run:
                        status_cell = f'E{row_index}'
                        worksheet.update_acell(status_cell, f"Failed - Empty email address")
                    continue
                
                # Validate email format (basic check)
                if '@' not in email_address:
                    print(f"Row {row_index} ({name}): Invalid email format ({email_address}), skipping...")
                    failed_count += 1
                    # Update status to indicate invalid email
                    if not args.dry_run:
                        status_cell = f'E{row_index}'
                        worksheet.update_acell(status_cell, f"Failed - Invalid email format")
                    continue
                
                print(f"Sending to: {name} ({email_address})...", end=' ', flush=True)
                
                # Generate personalized form URL
                form_url = generate_form_url(
                    name,
                    config['form_base_url'],
                    config['name_field_id']
                )
                
                # Create email body HTML
                email_body_html = create_email_body(
                    name,
                    form_url,
                    config['grant_deadline'],
                    config['image_url']
                )
                
                # Create email message
                msg = MIMEMultipart('alternative')
                msg['From'] = f"{config['sender_name']} <{config['sender_email']}>"
                msg['To'] = email_address
                msg['Subject'] = "Support Needed: Historic Holliday Park Grant Initiative"
                
                # Attach HTML body
                html_part = MIMEText(email_body_html, 'html')
                msg.attach(html_part)
                
                # Send email via Gmail SMTP
                try:
                    if args.dry_run:
                        print("  [DRY RUN] Would send email (skipped)")
                        # Simulate success for dry run
                        sent_count += 1
                    else:
                        # Connect to Gmail SMTP server
                        server = smtplib.SMTP('smtp.gmail.com', 587)
                        server.starttls()  # Enable TLS encryption
                        server.login(config['sender_email'], gmail_app_password)
                        server.send_message(msg)
                        server.quit()
                        
                        # Update Google Sheet: Mark as Sent
                        status_cell = f'E{row_index}'
                        sentdate_cell = f'F{row_index}'
                        
                        worksheet.update_acell(status_cell, 'Sent')
                        worksheet.update_acell(sentdate_cell, today_date)
                        
                        print("✓ Sent successfully")
                        sent_count += 1
                    
                except smtplib.SMTPAuthenticationError as e:
                    error_msg = f"SMTP Authentication failed: {str(e)}"
                    print(f"✗ Failed: {error_msg}")
                    failed_count += 1
                    
                    # Update status with error message
                    status_cell = f'E{row_index}'
                    worksheet.update_acell(status_cell, f"Failed - {error_msg}")
                    
                except smtplib.SMTPException as e:
                    error_msg = f"SMTP error: {str(e)}"
                    print(f"✗ Failed: {error_msg}")
                    failed_count += 1
                    
                    # Update status with error message
                    status_cell = f'E{row_index}'
                    worksheet.update_acell(status_cell, f"Failed - {error_msg}")
                    
                except Exception as e:
                    error_msg = f"Unexpected error: {str(e)}"
                    print(f"✗ Failed: {error_msg}")
                    failed_count += 1
                    
                    # Update status with error message
                    status_cell = f'E{row_index}'
                    worksheet.update_acell(status_cell, f"Failed - {error_msg}")
            
            except Exception as e:
                # Handle any unexpected errors in processing a row
                print(f"Row {row_index}: Error processing row - {str(e)}")
                failed_count += 1
                
                # Try to update status if possible
                if not args.dry_run:
                    try:
                        status_cell = f'E{row_index}'
                        worksheet.update_acell(status_cell, f"Failed - Processing error: {str(e)}")
                    except:
                        pass  # If we can't update, continue anyway
                continue
        
        # Print final summary
        print()
        print("="*60)
        print("Summary:")
        print("="*60)
        print(f"Sent: {sent_count}, Failed: {failed_count}")
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
