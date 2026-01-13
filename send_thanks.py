"""
Thank You Email Sender Script for Grant Tracker

This script identifies people who responded to the grant support request,
matches them to the master sheet, and sends personalized thank you emails
based on their response (Yes/No/Other).
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

from email_generator import load_config


def create_thank_you_email_body(name, response):
    """
    Create personalized HTML thank you email body based on response type.
    
    Generates a thank you email template with:
    - Personalized greeting
    - Thank you message based on response (Yes/No/Other)
    - Brief closing message
    
    Args:
        name (str): Recipient's name for personalization
        response (str): Their response (Yes/No/Other)
        
    Returns:
        str: Complete HTML thank you email body as a string
    """
    # Determine thank you message based on response
    response_lower = str(response).strip().lower() if response else ""
    
    if "yes" in response_lower:
        thank_you_message = (
            "Thank you so much for your support! Your positive response means a great deal "
            "to our grant initiative. We truly appreciate you taking the time to respond."
        )
    elif "no" in response_lower:
        thank_you_message = (
            "Thank you for taking the time to respond. We appreciate your time and consideration, "
            "and we understand that not everyone can participate. Your feedback is valuable to us."
        )
    else:
        # For "Other" or any other response
        thank_you_message = (
            "Thank you for your response! We appreciate you taking the time to provide feedback. "
            "Your input helps us understand the community's perspective on this initiative."
        )
    
    email_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Thank You - Grant Support</title>
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
                            <!-- Thank you message -->
                            <p style="margin: 0 0 20px 0; color: #555555; font-size: 16px; line-height: 1.6;">
                                {thank_you_message}
                            </p>
                            
                            <p style="margin: 0; color: #555555; font-size: 16px; line-height: 1.6;">
                                We truly appreciate your engagement with our grant support initiative.
                            </p>
                        </td>
                    </tr>
                    
                    <!-- Closing section -->
                    <tr>
                        <td style="padding: 20px 30px 30px 30px;">
                            <p style="margin: 0; color: #555555; font-size: 16px; line-height: 1.6;">
                                Best regards,<br>
                                {name.split()[0] if ' ' in name else name}  <!-- Use first name if available -->
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


def get_email_subject(response):
    """
    Get email subject line based on response type.
    
    Args:
        response (str): The response (Yes/No/Other)
        
    Returns:
        str: Subject line for the email
    """
    response_lower = str(response).strip().lower() if response else ""
    
    if "yes" in response_lower:
        return "Thank You for Your Support"
    else:
        # For "No", "Other", or any other response
        return "Thank You for Your Feedback"


def main():
    """
    Main function to send thank you emails to responders.
    
    Workflow:
    1. Parse command-line arguments for batch size (optional)
    2. Load configuration and Gmail App Password
    3. Connect to Google Sheets
    4. Read master sheet and responses sheet
    5. Match responders to master sheet by name
    6. Identify people who need thank yous (responded but ThankYouSent is empty)
    7. Send thank you emails based on response type
    8. Update ThankYouSent column for successful sends
    9. Print summary of results
    """
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description='Send thank you emails to responders for grant support campaign'
    )
    parser.add_argument(
        '--size',
        type=int,
        default=None,
        help='Number of thank you emails to send (default: all responders who need thank yous)'
    )
    args = parser.parse_args()
    batch_size = args.size
    
    print("="*60)
    print("Grant Tracker - Thank You Email Sender")
    print("="*60)
    if batch_size:
        print(f"Batch size: {batch_size}")
    else:
        print("Batch size: All responders who need thank yous")
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
        print(f"Accessing master worksheet: {config['master_sheet_tab']}...")
        master_worksheet = sheet.worksheet(config['master_sheet_tab'])
        
        # Access the responses sheet tab
        print(f"Accessing responses worksheet: {config['responses_sheet_tab']}...")
        try:
            responses_worksheet = sheet.worksheet(config['responses_sheet_tab'])
        except gspread.exceptions.WorksheetNotFound:
            print(f"Error: Responses worksheet '{config['responses_sheet_tab']}' not found.")
            return
        
        # Column indices based on Master Sheet structure
        NAME_COLUMN = 0      # Column A
        EMAIL_COLUMN = 1     # Column B
        THANKYOUSENT_COLUMN = 7  # Column H
        
        # Column indices for Responses Sheet
        RESPONSE_TIMESTAMP_COLUMN = 0  # Column 0
        RESPONSE_NAME_COLUMN = 1       # Column 1
        RESPONSE_VALUE_COLUMN = 2      # Column 2
        RESPONSE_TEXT_COLUMN = 3       # Column 3
        
        # Read all rows from master sheet
        print("Reading data from master sheet...")
        master_all_rows = master_worksheet.get_all_values()
        
        if len(master_all_rows) < 2:
            print("Warning: Master sheet appears to be empty or only contains headers.")
            return
        
        # Read all rows from responses sheet
        print("Reading data from responses sheet...")
        responses_all_rows = responses_worksheet.get_all_values()
        
        if len(responses_all_rows) < 2:
            print("Warning: Responses sheet appears to be empty or only contains headers.")
            return
        
        # Build a mapping from master sheet: name (lowercase) -> (row_index, email, thankyou_sent)
        # Skip header row (index 0)
        master_name_map = {}
        master_data_rows = master_all_rows[1:]
        
        for i, row in enumerate(master_data_rows):
            row_index = i + 2  # Row 1 is header, row 2 is first data row
            
            # Safety check: Skip if Name column contains "Name"
            if len(row) > 0 and str(row[0]).strip().lower() == 'name':
                continue
            
            if len(row) > NAME_COLUMN:
                name = str(row[NAME_COLUMN]).strip() if row[NAME_COLUMN] else ""
                if name:
                    name_lower = name.lower()
                    email = str(row[EMAIL_COLUMN]).strip() if len(row) > EMAIL_COLUMN and row[EMAIL_COLUMN] else ""
                    thankyou_sent = str(row[THANKYOUSENT_COLUMN]).strip() if len(row) > THANKYOUSENT_COLUMN and row[THANKYOUSENT_COLUMN] else ""
                    master_name_map[name_lower] = (row_index, email, thankyou_sent)
        
        print(f"Found {len(master_name_map)} people in master sheet.")
        
        # Extract responder data from responses sheet
        # Skip header row (index 0)
        responders_needing_thanks = []
        
        for row in responses_all_rows[1:]:  # Skip header
            if len(row) > RESPONSE_NAME_COLUMN and row[RESPONSE_NAME_COLUMN]:
                # Extract name and normalize for matching
                name = str(row[RESPONSE_NAME_COLUMN]).strip()
                if name and name.lower() != 'name':  # Skip header if it leaked through
                    name_lower = name.lower()
                    
                    # Get response value
                    response = str(row[RESPONSE_VALUE_COLUMN]).strip() if len(row) > RESPONSE_VALUE_COLUMN and row[RESPONSE_VALUE_COLUMN] else ""
                    
                    # Try to match to master sheet
                    if name_lower in master_name_map:
                        row_index, email, thankyou_sent = master_name_map[name_lower]
                        
                        # Check if thank you hasn't been sent yet
                        if not thankyou_sent:
                            responders_needing_thanks.append((row_index, email, name, response))
        
        print(f"Found {len(responders_needing_thanks)} people who responded and need thank yous.")
        print()
        
        if not responders_needing_thanks:
            print("No thank yous to send. All responders have already received thank you emails.")
            return
        
        # Limit to batch size if specified
        if batch_size:
            people_to_process = responders_needing_thanks[:batch_size]
            print(f"Processing {len(people_to_process)} thank yous (limited by --size={batch_size}).")
        else:
            people_to_process = responders_needing_thanks
            print(f"Processing all {len(people_to_process)} thank yous.")
        print()
        
        # Initialize counters
        sent_count = 0
        failed_count = 0
        
        # Get today's date for ThankYouSent column
        today_date = date.today().strftime('%Y-%m-%d')
        
        # Process each responder
        print("="*60)
        print("Sending Thank You Emails:")
        print("="*60)
        
        for row_index, email_address, name, response in people_to_process:
            try:
                if not email_address:
                    print(f"Row {row_index} ({name}): Empty email field, skipping...")
                    failed_count += 1
                    continue
                
                # Validate email format (basic check)
                if '@' not in email_address:
                    print(f"Row {row_index} ({name}): Invalid email format ({email_address}), skipping...")
                    failed_count += 1
                    continue
                
                print(f"Sending thank you to: {name} ({email_address})...", end=' ', flush=True)
                
                # Create thank you email body HTML
                thank_you_email_html = create_thank_you_email_body(name, response)
                
                # Get subject line based on response
                subject = get_email_subject(response)
                
                # Create email message
                msg = MIMEMultipart('alternative')
                msg['From'] = f"{config['sender_name']} <{config['sender_email']}>"
                msg['To'] = email_address
                msg['Subject'] = subject
                
                # Attach HTML body
                html_part = MIMEText(thank_you_email_html, 'html')
                msg.attach(html_part)
                
                # Send email via Gmail SMTP
                try:
                    # Connect to Gmail SMTP server
                    server = smtplib.SMTP('smtp.gmail.com', 587)
                    server.starttls()  # Enable TLS encryption
                    server.login(config['sender_email'], gmail_app_password)
                    server.send_message(msg)
                    server.quit()
                    
                    # Update Google Sheet: Mark ThankYouSent with today's date
                    thankyousent_cell = f'H{row_index}'
                    master_worksheet.update_acell(thankyousent_cell, today_date)
                    
                    print("✓ Sent")
                    sent_count += 1
                    
                except smtplib.SMTPAuthenticationError as e:
                    error_msg = f"SMTP Authentication failed: {str(e)}"
                    print(f"✗ Failed: {error_msg}")
                    failed_count += 1
                    # Don't update ThankYouSent on failure
                    
                except smtplib.SMTPException as e:
                    error_msg = f"SMTP error: {str(e)}"
                    print(f"✗ Failed: {error_msg}")
                    failed_count += 1
                    # Don't update ThankYouSent on failure
                    
                except Exception as e:
                    error_msg = f"Unexpected error: {str(e)}"
                    print(f"✗ Failed: {error_msg}")
                    failed_count += 1
                    # Don't update ThankYouSent on failure
            
            except Exception as e:
                # Handle any unexpected errors in processing
                print(f"Row {row_index}: Error processing - {str(e)}")
                failed_count += 1
                continue
        
        # Print final summary
        print()
        print("="*60)
        print("Summary:")
        print("="*60)
        print(f"Thank yous sent: {sent_count}, Failed: {failed_count}")
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
