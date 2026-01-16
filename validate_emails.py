"""
Email Validation Script for Grant Tracker

This script validates all email addresses in the Master Sheet and generates
a comprehensive report of issues including invalid formats, missing emails,
suspicious patterns, DNS failures, and duplicates.
"""

import argparse
import os
import re
import socket
from collections import defaultdict

import gspread
from oauth2client.service_account import ServiceAccountCredentials

from email_generator import load_config

# Email validation regex pattern
EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

# Common test/suspicious domains
SUSPICIOUS_DOMAINS = [
    'example.com', 'example.org', 'test.com', 'localhost',
    'invalid', 'fake.com', 'test.org', 'example.net'
]

# DNS lookup timeout (seconds)
DNS_TIMEOUT = 5


def validate_email_format(email):
    """
    Validate email format using regex pattern.
    
    Args:
        email (str): Email address to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not email or not isinstance(email, str):
        return False, "Email is empty or not a string"
    
    email = email.strip()
    
    # Check for spaces
    if ' ' in email:
        return False, "Email contains spaces"
    
    # Check for exactly one @ symbol
    if email.count('@') != 1:
        if email.count('@') == 0:
            return False, "Email missing @ symbol"
        else:
            return False, "Email contains multiple @ symbols"
    
    # Split into local and domain parts
    parts = email.split('@')
    local_part = parts[0]
    domain_part = parts[1]
    
    # Check local part is not empty
    if not local_part:
        return False, "Email missing local part (before @)"
    
    # Check domain part is not empty
    if not domain_part:
        return False, "Email missing domain part (after @)"
    
    # Check domain has at least one dot
    if '.' not in domain_part:
        return False, "Domain part missing dot (e.g., .com)"
    
    # Check domain has valid TLD (at least 2 characters after last dot)
    domain_parts = domain_part.split('.')
    if len(domain_parts[-1]) < 2:
        return False, "Domain TLD too short (must be at least 2 characters)"
    
    # Use regex pattern to validate overall format
    if not EMAIL_PATTERN.match(email):
        return False, "Email format does not match standard pattern"
    
    return True, ""


def is_suspicious_email(email):
    """
    Check if email matches suspicious/test patterns.
    
    Args:
        email (str): Email address to check
        
    Returns:
        tuple: (is_suspicious, reason)
    """
    if not email or '@' not in email:
        return False, ""
    
    email_lower = email.lower().strip()
    parts = email_lower.split('@')
    
    if len(parts) != 2:
        return False, ""
    
    local_part = parts[0]
    domain_part = parts[1]
    
    # Check for test domains
    for test_domain in SUSPICIOUS_DOMAINS:
        if domain_part == test_domain or domain_part.endswith('.' + test_domain):
            return True, f"Test domain: {test_domain}"
    
    # Check if local part equals domain part (e.g., test@test.com)
    if local_part == domain_part.split('.')[0]:
        return True, "Local part matches domain part"
    
    # Check if both parts contain "test"
    if 'test' in local_part and 'test' in domain_part:
        return True, "Contains 'test' in both local and domain parts"
    
    # Check for repeated patterns (e.g., abc@abc.com)
    if local_part == domain_part.split('.')[0] and len(local_part) > 2:
        return True, "Repeated pattern detected"
    
    return False, ""


def check_dns(domain):
    """
    Check if domain exists by performing DNS lookup.
    
    Args:
        domain (str): Domain name to check (e.g., 'example.com')
        
    Returns:
        tuple: (domain_exists, error_message)
    """
    try:
        # Set socket timeout
        socket.setdefaulttimeout(DNS_TIMEOUT)
        
        # Try to resolve the domain
        socket.gethostbyname(domain)
        return True, ""
    except socket.gaierror:
        return False, "Domain not found (DNS lookup failed)"
    except socket.timeout:
        return False, "DNS lookup timed out"
    except Exception as e:
        return False, f"DNS error: {str(e)}"


def main():
    """
    Main function to validate all emails in the Master Sheet.
    
    Workflow:
    1. Load configuration and connect to Google Sheets
    2. Read all email addresses from the master sheet
    3. Validate each email (format, suspicious patterns, optional DNS)
    4. Detect duplicate emails
    5. Generate comprehensive report
    """
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description='Validate all email addresses in the Master Sheet'
    )
    parser.add_argument(
        '--check-dns',
        action='store_true',
        help='Enable DNS checking to verify domains exist (slower but more thorough)'
    )
    args = parser.parse_args()
    
    print("="*60)
    print("Grant Tracker - Email Validation Report")
    print("="*60)
    if args.check_dns:
        print("DNS checking: ENABLED")
    else:
        print("DNS checking: DISABLED (use --check-dns to enable)")
    print()
    
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
        
        # Skip header row (index 0), process data rows only
        data_rows = all_rows[1:]
        
        # Initialize tracking dictionaries
        valid_emails = []
        invalid_format = []  # List of (row_index, email, error_message)
        missing_emails = []  # List of (row_index, name)
        suspicious_emails = []  # List of (row_index, email, reason)
        dns_failures = []  # List of (row_index, email, error_message)
        email_to_rows = defaultdict(list)  # Map email to list of row indices
        
        print("Validating emails...")
        print()
        
        # Process each data row
        for i, row in enumerate(data_rows):
            row_index = i + 2  # Row 1 is header, row 2 is first data row
            
            # Extract name
            name = ""
            if len(row) > NAME_COLUMN:
                name = str(row[NAME_COLUMN]).strip() if row[NAME_COLUMN] else ""
            
            # Extract email
            email = ""
            if len(row) > EMAIL_COLUMN:
                email = str(row[EMAIL_COLUMN]).strip() if row[EMAIL_COLUMN] else ""
            
            # Check if email is missing
            if not email:
                missing_emails.append((row_index, name))
                continue
            
            # Track email for duplicate detection (normalize to lowercase)
            email_lower = email.lower()
            email_to_rows[email_lower].append((row_index, name, email))
            
            # Validate email format
            is_valid, error_msg = validate_email_format(email)
            if not is_valid:
                invalid_format.append((row_index, email, error_msg))
                continue
            
            # Check for suspicious patterns
            is_suspicious, suspicious_reason = is_suspicious_email(email)
            if is_suspicious:
                suspicious_emails.append((row_index, email, suspicious_reason))
            
            # Optional DNS check
            if args.check_dns:
                domain = email.split('@')[1]
                domain_exists, dns_error = check_dns(domain)
                if not domain_exists:
                    dns_failures.append((row_index, email, dns_error))
            
            # If we got here, email is valid
            valid_emails.append((row_index, email))
        
        # Detect duplicates
        duplicate_emails = []
        for email_lower, rows_list in email_to_rows.items():
            if len(rows_list) > 1:
                # Extract row indices and original email
                row_indices = [r[0] for r in rows_list]
                original_email = rows_list[0][2]  # Get original case email
                duplicate_emails.append((original_email, row_indices))
        
        # Generate report
        print("="*60)
        print("Summary Statistics:")
        print("="*60)
        total_checked = len(data_rows)
        print(f"Total emails checked: {total_checked}")
        print(f"Valid emails: {len(valid_emails)}")
        print(f"Invalid format: {len(invalid_format)}")
        print(f"Missing emails: {len(missing_emails)}")
        print(f"Suspicious/test emails: {len(suspicious_emails)}")
        if args.check_dns:
            print(f"DNS failures: {len(dns_failures)}")
        print(f"Duplicate emails: {len(duplicate_emails)}")
        print()
        
        # Detailed issues
        print("="*60)
        print("Detailed Issues:")
        print("="*60)
        print()
        
        # Invalid format
        if invalid_format:
            print("INVALID FORMAT:")
            for row_index, email, error_msg in invalid_format:
                print(f"  Row {row_index}: {email} ({error_msg})")
            print()
        
        # Missing emails
        if missing_emails:
            print("MISSING EMAILS:")
            for row_index, name in missing_emails:
                name_display = name if name else "(no name)"
                print(f"  Row {row_index}: {name_display} (empty email field)")
            print()
        
        # Suspicious emails
        if suspicious_emails:
            print("SUSPICIOUS/TEST EMAILS:")
            for row_index, email, reason in suspicious_emails:
                print(f"  Row {row_index}: {email} ({reason})")
            print()
        
        # DNS failures
        if args.check_dns and dns_failures:
            print("DNS FAILURES (--check-dns enabled):")
            for row_index, email, error_msg in dns_failures:
                print(f"  Row {row_index}: {email} ({error_msg})")
            print()
        
        # Duplicate emails
        if duplicate_emails:
            print("DUPLICATE EMAILS:")
            for email, row_indices in duplicate_emails:
                rows_str = ", ".join(str(r) for r in row_indices)
                print(f"  {email} appears in rows: {rows_str}")
            print()
        
        # Recommendations
        print("="*60)
        print("Recommendations:")
        print("="*60)
        recommendations = []
        
        if invalid_format:
            recommendations.append(f"Fix {len(invalid_format)} invalid format email(s) before sending")
        
        if missing_emails:
            recommendations.append(f"Add email addresses for {len(missing_emails)} missing entry/entries")
        
        if suspicious_emails:
            recommendations.append(f"Review {len(suspicious_emails)} suspicious/test email(s)")
        
        if args.check_dns and dns_failures:
            recommendations.append(f"Verify {len(dns_failures)} DNS failure(s) if using --check-dns")
        
        if duplicate_emails:
            recommendations.append(f"Remove or update {len(duplicate_emails)} duplicate email(s)")
        
        if not recommendations:
            print("✓ All emails are valid! No issues found.")
        else:
            for rec in recommendations:
                print(f"- {rec}")
        
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
