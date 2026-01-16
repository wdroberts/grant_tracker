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

## How It Works

Think of Grant Tracker like an automated postal mail campaign, but for email. Instead of manually writing and sending hundreds of emails, the system does it for you while keeping track of everything in a Google Sheet.

### The Overall Workflow

1. **You prepare your list** - Put names and emails in a Google Sheet
2. **System sends emails** - The script reads your list and sends personalized emails
3. **People respond** - They click a link that takes them to a Google Form (with their name already filled in!)
4. **System tracks responses** - Responses automatically appear in your Google Sheet
5. **You send reminders** - After a few days, remind people who haven't responded yet
6. **You thank responders** - Send personalized thank you emails to everyone who responded

### What Each Script Does

**send_batch.py** - The Initial Campaign
- **When to use:** Start of your campaign, when you want to reach everyone
- **What it does:** Reads your master list, creates personalized emails with form links, sends them via Gmail, and marks each person as "Sent" in your sheet
- **Think of it as:** The mail carrier delivering your first batch of letters

**send_reminders.py** - The Follow-Up
- **When to use:** 3-7 days after initial send, for people who haven't responded
- **What it does:** Compares your master list with responses, finds people who got the email but didn't respond, sends them a shorter reminder email
- **Think of it as:** A friendly "did you get our letter?" follow-up

**send_thanks.py** - The Gratitude
- **When to use:** After people respond, to thank them for their time
- **What it does:** Finds everyone who responded, matches them to your master list, sends personalized thank you based on their response (Yes/No)
- **Think of it as:** Sending thank you cards to everyone who replied

### How Google Sheets Tracks Everything

Your Google Sheet is like a master checklist that the system updates automatically:

- **Status column:** Shows "Sent" when an email was successfully sent
- **SentDate column:** Records the date the email was sent
- **Form Responses tab:** Automatically collects all responses from your Google Form
- **ReminderSent column:** Records when reminder emails were sent
- **ThankYouSent column:** Records when thank you emails were sent

The system reads and writes to this sheet to know who needs what, avoiding duplicates and keeping everything organized.

### Common Terminology

- **Dry-run:** A test mode where the script shows you what it WOULD do without actually sending emails or updating sheets. Like a fire drill - practice without the real thing.
- **Batch:** A group of emails sent together. You can send to everyone at once or in smaller batches (e.g., 50 at a time).
- **Pre-fill:** When someone clicks the link in their email, the Google Form automatically fills in their name so they don't have to type it.
- **Service Account:** A special Google account (like a robot assistant) that can read and write to your Google Sheet automatically.
- **App Password:** A special password for Gmail that lets programs send emails securely (more secure than your regular password).

## Understanding the System

### What Happens When You Send an Email (Step by Step)

1. **You run the script** - Type `python send_batch.py --size 50`
2. **Script connects to Google Sheets** - Uses the service account to read your master list
3. **Script finds people to email** - Looks for rows where Status is empty (not sent yet)
4. **Script creates personalized email** - For each person, it:
   - Takes their name from the sheet
   - Creates a special link to your Google Form with their name pre-filled
   - Builds a beautiful HTML email with their name, the form link, and your message
5. **Script sends via Gmail** - Connects to Gmail, sends the email
6. **Script updates the sheet** - Marks Status as "Sent" and records today's date in SentDate
7. **You see the results** - Script prints a summary: "Sent: 50, Failed: 0"

### How Responses Are Captured Automatically

When someone clicks the link in their email:
1. **Google Form opens** - Their name is already filled in (that's the "pre-fill" magic!)
2. **They answer the question** - Usually "Yes", "No", or "Other"
3. **They submit the form** - Google automatically saves their response
4. **Response appears in your sheet** - A new row appears in your "Form Responses" tab with their name, answer, and timestamp
5. **You can see it immediately** - Open your Google Sheet and check the Form Responses tab

### How the System Knows Who to Remind vs. Thank

The system is smart about tracking:

**For Reminders:**
- Looks for people where Status = "Sent" (they got the email)
- Checks if their name is NOT in the Form Responses tab (they haven't responded)
- Checks if ReminderSent is empty (they haven't gotten a reminder yet)
- If all three are true → they get a reminder

**For Thank Yous:**
- Looks for people whose name IS in the Form Responses tab (they responded)
- Matches their name to your master list to get their email
- Checks if ThankYouSent is empty (they haven't gotten a thank you yet)
- If all are true → they get a thank you email personalized to their response

This way, the system never sends duplicate emails and always knows who needs what!

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