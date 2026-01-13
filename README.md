# Grant Tracker

Email campaign system for neighborhood grant support collection.

## Features
- Batch email sending with Gmail
- Google Forms integration with pre-filled names
- Automatic response tracking
- Reminder emails for non-responders
- Personalized thank you emails
- Status tracking in Google Sheets

## Quick Start
```bash
# 1. Activate environment
.venv\Scripts\Activate.ps1  # Windows
# or
source .venv/bin/activate   # Mac/Linux

# 2. Test with dry-run
python send_batch.py --size 5 --dry-run

# 3. Send for real
python send_batch.py --size 5

# See USAGE.md for complete workflow and troubleshooting
```

## Setup

### Prerequisites
- Python 3.8+
- Gmail account with App Password enabled
- Google Service Account for Sheets API
- Google Form linked to Google Sheet

### Installation
1. Clone the repository
2. Create virtual environment: `python -m venv .venv`
3. Activate: `.venv\Scripts\Activate.ps1` (Windows) or `source .venv/bin/activate` (Mac/Linux)
4. Install dependencies: `pip install -r requirements.txt`

### Configuration

1. **Google Service Account:**
   - Create project in Google Cloud Console
   - Enable Google Sheets API
   - Create Service Account and download credentials.json
   - Place credentials.json in project root
   - Share your Google Sheet with the service account email

2. **Gmail App Password:**
   - Enable 2FA on Gmail account
   - Generate App Password at myaccount.google.com/apppasswords
   - Create .env file with: `GMAIL_APP_PASSWORD=your16charpassword`

3. **config.json:**
   - Update with your Google Sheet ID
   - Update with your Form URL and field IDs
   - Update sender email and name

## Usage

### Send Initial Emails
```bash
python send_batch.py --size 50
```

### Send Reminders
```bash
python send_reminders.py --size 25
# Or send to all non-responders:
python send_reminders.py
```

### Send Thank You Emails
```bash
python send_thanks.py
```

## Workflow

1. **Initial Campaign:** Run send_batch.py to send emails, Status updates to "Sent"
2. **Track Responses:** Responses automatically captured in Form Responses sheet
3. **Follow Up:** Run send_reminders.py after a few days for non-responders
4. **Thank Responders:** Run send_thanks.py to thank everyone who responded

## Google Sheets Structure

**Master Sheet (Sheet1):**
- Columns: Name, Email, Address, UniqueID, Status, SentDate, ReminderSent, ThankYouSent

**Form Responses:**
- Columns: Timestamp, Your Name, Response, Response Text

## Files

- `email_generator.py` - Core functions for generating emails and form URLs
- `send_batch.py` - Initial campaign email sending
- `send_reminders.py` - Reminder emails for non-responders
- `send_thanks.py` - Thank you emails for responders
- `config.json` - Project settings and configuration
- `.env` - Gmail password (not committed to git)
- `credentials.json` - Google Service Account credentials (not committed to git)

## Troubleshooting

- **"Responses worksheet not found":** Check config.json tab name matches your sheet exactly
- **"SMTP Authentication failed":** Verify Gmail App Password in .env file
- **"No people found":** Check Status column values in master sheet
- **"Worksheet not found":** Run send_reminders.py to see available worksheet names

## Security

Never commit `.env` or `credentials.json` to git. These files are already in `.gitignore`.

## Developed with Claude and Cursor using vibe-coding workflow