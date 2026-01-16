# Grant Tracker - Quick Reference

## First Time User Walkthrough

If you've never used this system before, follow these steps. This assumes you've already completed the Setup section in README.md (installed Python, set up credentials, etc.).

### Step 1: Open Your Project
1. Open a terminal/command prompt
2. Navigate to your project folder: `cd path/to/grant-tracker`
3. You should see files like `send_batch.py`, `config.json`, etc.

### Step 2: Activate Your Virtual Environment
**What this does:** Activates a special "toolbox" that has all the Python tools your project needs.

**Windows:**
```bash
.venv\Scripts\Activate.ps1
```

**Mac/Linux:**
```bash
source .venv/bin/activate
```

**What you'll see:** Your command prompt should now show `(.venv)` at the beginning. This means you're in the virtual environment.

**Why this matters:** Think of it like putting on special work gloves - you need the right tools for the job, and the virtual environment has them.

### Step 3: Test Your First Email (Dry-Run)
**What this does:** Tests the system without actually sending anything. It's like a fire drill - you practice without the real thing happening.

```bash
python send_batch.py --size 5 --dry-run
```

**What you'll see:**
- The script connects to your Google Sheet
- It finds 5 people who haven't been sent emails yet
- It shows you what emails it WOULD send
- It prints "[DRY RUN] Would send email (skipped)" for each one
- At the end, it shows a summary like "Sent: 5, Failed: 0"

**What's happening behind the scenes:**
1. Script reads your Google Sheet
2. Finds people with empty Status column
3. Creates email content for each person
4. Shows you what it would do (but doesn't actually send)
5. Doesn't update your Google Sheet

**Common questions:**
- **"Why only 5?"** - We're testing! Start small to make sure everything works.
- **"What if it says 'Failed'?"** - Check your setup (credentials.json, .env file, etc.)
- **"Nothing happened"** - Make sure you activated the virtual environment (see Step 2)

### Step 4: Send Your First Real Emails
**What this does:** Actually sends emails to real people. This is the real deal!

```bash
python send_batch.py --size 5
```

**What you'll see:**
- Same as dry-run, but this time it asks: "Ready to send 5 emails. Continue? (yes/no):"
- Type `y` or `yes` to continue
- For each email, you'll see: "Sending to: John Doe (john@example.com)... ✓ Sent successfully"
- At the end: "Sent: 5, Failed: 0"

**What's happening behind the scenes:**
1. Script connects to Gmail using your App Password
2. For each person, it sends a real email
3. Updates your Google Sheet: Status = "Sent", SentDate = today's date
4. If something fails, it marks Status = "Failed - [reason]"

**What the recipient sees:**
- An email from you with their name in the greeting
- A beautiful HTML email with your grant message
- A button/link that says "Complete Your Response"
- When they click it, a Google Form opens with their name already filled in

### Step 5: Check Your Results
**What to do:** Open your Google Sheet

**What you'll see:**
- Status column now shows "Sent" for the 5 people
- SentDate column shows today's date
- If someone responded, check the "Form Responses" tab

**Congratulations!** You've sent your first batch of emails! 🎉

## Pre-Flight Check

Before sending any campaign, always validate your email list:

```bash
# Validate email addresses
python validate_emails.py

# Or with DNS checking (slower but thorough)
python validate_emails.py --check-dns
```

This checks for:
- Invalid email formats
- Missing email addresses
- Duplicate entries
- Suspicious test patterns
- (Optional) Domain existence via DNS

Fix any issues in your Google Sheet before sending.

## Daily Commands

### Send Initial Campaign

**What this does:** Sends personalized emails to people on your list who haven't been contacted yet.

**When to use it:** 
- Start of your campaign
- When you want to reach new people
- After adding new names to your sheet

**Expected output:**
```
============================================================
Grant Tracker - Batch Email Sender
============================================================
Batch size: 50
Loading configuration...
Configuration loaded successfully.
...
Found 50 rows with empty Status.
Processing 50 rows in this batch.

Ready to send 50 emails. Continue? (yes/no): y

Sending to: John Doe (john@example.com)... ✓ Sent successfully
Sending to: Jane Smith (jane@example.com)... ✓ Sent successfully
...
============================================================
Summary:
============================================================
Sent: 50, Failed: 0
============================================================
```

**What's happening behind the scenes:**
- Script reads your master sheet
- Finds rows where Status column is empty
- For each person: creates personalized email, generates form link, sends via Gmail
- Updates Status to "Sent" and records date in SentDate column

```bash
# Always test first!
python send_batch.py --size 50 --dry-run

# Then send for real
python send_batch.py --size 50
```

### Send Reminders (after 3-7 days)

**What this does:** Finds people who received your initial email but haven't responded yet, and sends them a shorter reminder email.

**When to use it:**
- 3-7 days after sending initial emails
- When you want to follow up with non-responders
- Before the grant deadline approaches

**Expected output:**
```
============================================================
Grant Tracker - Reminder Email Sender
============================================================
Batch size: All non-responders
...
Found 2 unique responders in responses sheet.
Found 15 people who haven't responded.
Processing all 15 reminders.

Ready to send 15 reminder emails. Continue? (yes/no): y

Sending reminder to: John Doe (john@example.com)... ✓ Sent
Sending reminder to: Jane Smith (jane@example.com)... ✓ Sent
...
============================================================
Summary:
============================================================
Reminders sent: 15, Failed: 0
============================================================
```

**What's happening behind the scenes:**
- Script reads your master sheet AND your Form Responses sheet
- Compares the two: finds people where Status="Sent" but their name is NOT in responses
- Checks ReminderSent column is empty (haven't sent reminder yet)
- Sends shorter reminder email to those people
- Updates ReminderSent column with today's date

**Why wait 3-7 days?** People need time to read and respond. Sending reminders too soon can seem pushy.

```bash
# Test first
python send_reminders.py --dry-run

# Send reminders
python send_reminders.py
```

### Send Thank Yous

**What this does:** Finds everyone who responded to your campaign and sends them a personalized thank you email based on their response (Yes/No/Other).

**When to use it:**
- After people start responding
- At the end of your campaign
- To show appreciation for people's time

**Expected output:**
```
============================================================
Grant Tracker - Thank You Email Sender
============================================================
Batch size: All responders who need thank yous
...
Found 25 people who responded and need thank yous.
Processing all 25 thank yous.

Ready to send 25 thank you emails. Continue? (yes/no): y

Sending thank you to: John Doe (john@example.com)... ✓ Sent
Sending thank you to: Jane Smith (jane@example.com)... ✓ Sent
...
============================================================
Summary:
============================================================
Thank yous sent: 25, Failed: 0
============================================================
```

**What's happening behind the scenes:**
- Script reads Form Responses sheet to see who responded
- Matches responder names to your master sheet to get their email addresses
- Checks ThankYouSent column is empty (haven't sent thank you yet)
- Creates personalized thank you based on their response:
  - If they said "Yes": "Thank You for Your Support"
  - If they said "No" or "Other": "Thank You for Your Feedback"
- Sends thank you email
- Updates ThankYouSent column with today's date

**Why personalize?** People who said "Yes" get thanked for support, while people who said "No" get thanked for their time and consideration. It's more thoughtful!

```bash
# Test first
python send_thanks.py --dry-run

# Send thank yous
python send_thanks.py
```

## Before You Start

1. **Activate virtual environment:**
   - Windows: `.venv\Scripts\Activate.ps1`
   - Mac/Linux: `source .venv/bin/activate`
   - You should see `(.venv)` in your prompt

2. **Check your setup:**
   - Gmail App Password in `.env` file
   - `credentials.json` in project folder
   - Google Sheet shared with service account

## Typical Campaign Workflow
```bash
# Day 1: Send initial emails
python send_batch.py --size 221 --dry-run  # Review
python send_batch.py --size 221            # Send (type 'y' to confirm)

# Day 4-5: Send reminders to non-responders
python send_reminders.py --dry-run         # Review
python send_reminders.py                   # Send

# Day 7: Thank everyone who responded
python send_thanks.py --dry-run            # Review
python send_thanks.py                      # Send
```

## Checking Status

Open your Google Sheet to see:
- **Status column:** Shows "Sent" for emails sent
- **Form Responses tab:** Shows who responded
- **ReminderSent column:** Shows who got reminders
- **ThankYouSent column:** Shows who got thank yous

## Troubleshooting

**"ModuleNotFoundError: No module named 'gspread'"**
→ Activate virtual environment first

**"SMTP Authentication failed"**
→ Check `.env` file has correct Gmail App Password

**"Responses worksheet not found"**
→ Check `config.json` has correct tab name (with spaces)

## Flags

- `--size N` - Send to first N people only
- `--dry-run` - Test mode (no emails sent, no updates)

## Safety Tips

✅ **ALWAYS dry-run first**
✅ Test with small batches (--size 5) before full send
✅ Keep backup of your Google Sheet
✅ Check spam folder if emails don't arrive
