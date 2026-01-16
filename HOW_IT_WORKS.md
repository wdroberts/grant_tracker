# How Grant Tracker Works - A Beginner's Guide

This guide explains how the Grant Tracker system works in simple, everyday language. Think of it like explaining how a car works to someone who's never driven before - we'll use analogies and simple explanations.

## The Big Picture

### What Problem Does This Solve?

Imagine you need to collect support from 200+ neighbors for a grant application. You could:
- **Option 1:** Manually send 200 emails, one by one, tracking who responded in a spreadsheet
- **Option 2:** Use Grant Tracker to automate everything while you focus on other important work

Grant Tracker is Option 2. It's like having a helpful assistant who:
- Sends personalized emails to everyone on your list
- Tracks who responded automatically
- Knows who needs reminders
- Sends thank you emails to everyone who responded
- Never makes mistakes or forgets someone

### How Email Campaigns Work

An email campaign is like a postal mail campaign, but faster and cheaper:

1. **You have a list** - Names and email addresses (like addresses on envelopes)
2. **You send messages** - Personalized emails (like personalized letters)
3. **People respond** - They click a link and fill out a form (like mailing back a reply card)
4. **You track responses** - See who responded in your spreadsheet (like checking off names on a list)
5. **You follow up** - Remind people who haven't responded (like a second mailing)
6. **You thank people** - Send appreciation to everyone who responded (like thank you cards)

The difference? Grant Tracker does steps 2, 4, 5, and 6 automatically!

### Why We Need Tracking

Without tracking, you'd have to:
- Remember who you already emailed (did I send to John? Or was that someone else?)
- Manually check who responded (open 200 emails one by one?)
- Figure out who needs reminders (who hasn't responded in 5 days?)
- Avoid sending duplicates (did I already thank Jane?)

With tracking, the Google Sheet does all this automatically. It's like having a smart checklist that updates itself.

## The Components

Think of Grant Tracker like a team of workers, each with a specific job. Let's meet the team:

### Google Sheets (The Database)

**What it is:** A spreadsheet in Google Drive that stores all your information.

**What it does:**
- Stores your master list (names, emails, addresses)
- Tracks status (who got emails, who responded)
- Records dates (when emails were sent, when reminders went out)
- Collects responses automatically from your Google Form

**How it connects:** All the Python scripts read from and write to this sheet. It's the "source of truth" - everything the system knows comes from here.

**Real-world analogy:** Think of it like a filing cabinet where you keep all your campaign records. But instead of paper files, it's a digital spreadsheet that can update itself automatically.

**What you see:**
- **Master Sheet (Sheet1):** Your main list with columns like Name, Email, Status, SentDate, etc.
- **Form Responses tab:** Automatically collects all responses from your Google Form

### Google Forms (The Response Collector)

**What it is:** An online form that people fill out to respond to your campaign.

**What it does:**
- Displays questions (usually: "Do you support this grant? Yes/No/Other")
- Collects responses when people submit
- Automatically saves responses to your Google Sheet
- Can pre-fill information (like the person's name) when they click a special link

**How it connects:** When someone clicks the link in their email, the form opens with their name already filled in. When they submit, their response appears in your Google Sheet automatically.

**Real-world analogy:** Think of it like a survey card that people mail back, but it's online and the results automatically appear in your filing cabinet (Google Sheet).

**The magic of pre-filling:** When you create a special link with someone's name encoded in it, Google Forms automatically fills in their name when they open it. They don't have to type it - it's already there! This makes responding easier and ensures names match correctly.

### Service Account (The Robot Assistant)

**What it is:** A special Google account that acts like a robot assistant with permission to read and write to your Google Sheet.

**What it does:**
- Connects to your Google Sheet automatically
- Reads names, emails, and status information
- Updates the sheet (marks Status as "Sent", records dates)
- Works 24/7 without needing you to log in

**How it connects:** You create this account in Google Cloud Console, download a special file (`credentials.json`), and share your Google Sheet with the service account's email address. Then the Python scripts use this file to access your sheet.

**Real-world analogy:** Think of it like giving a trusted assistant a key to your filing cabinet. They can read files and update records, but they can't do anything else (like delete your files or access your email). It's a limited, safe permission.

**Why not use your regular Google account?** For security and automation. The service account can work automatically without you needing to log in each time, and it has limited permissions (can only access the sheets you share with it).

### Gmail App Password (The Secure Email Key)

**What it is:** A special 16-character password that lets programs send emails through your Gmail account securely.

**What it does:**
- Allows Python scripts to send emails via Gmail's servers
- More secure than using your regular password
- Works even if you have 2-Factor Authentication enabled

**How it connects:** You generate this password in your Google Account settings, save it in a `.env` file, and the Python scripts use it to log into Gmail and send emails.

**Real-world analogy:** Think of it like a special key card for a building. Your regular password is like the main entrance key, but the App Password is like a key card that only works for the mailroom - it can send mail but can't access your other accounts or files.

**Why not use your regular password?** Security! If someone gets your App Password, they can only send emails - they can't access your account, read your emails, or change your settings. It's a limited permission, like the service account.

### Python Scripts (The Automation Workers)

**What they are:** Computer programs written in Python that automate the email campaign tasks.

**What they do:**
- `email_generator.py`: Creates personalized emails and form links (the content creator)
- `send_batch.py`: Sends initial campaign emails (the mail carrier)
- `send_reminders.py`: Sends follow-up emails to non-responders (the reminder service)
- `send_thanks.py`: Sends thank you emails to responders (the gratitude department)

**How they connect:** They all read from `config.json` (your settings), use the service account to access Google Sheets, use the App Password to send emails via Gmail, and work together to run your campaign.

**Real-world analogy:** Think of them like specialized workers in a mailroom:
- One worker creates personalized letters
- Another worker addresses and mails them
- Another worker checks who hasn't responded and sends reminders
- Another worker sends thank you cards to everyone who replied

**Why Python?** Python is a programming language that's great for automation. It can easily connect to Google Sheets, send emails, and process data. But you don't need to know Python to use this system - the scripts are already written!

## The Workflow - Explained Simply

Let's walk through a complete campaign from start to finish, with detailed explanations of what happens at each step.

### Step 1: Initial Send (send_batch.py)

**What happens when you run the script:**

1. **You type the command:**
   ```bash
   python send_batch.py --size 50
   ```
   This tells the script: "Send emails to 50 people."

2. **Script loads your settings:**
   - Reads `config.json` to get your Google Sheet ID, form URL, sender info
   - Reads `.env` to get your Gmail App Password
   - Loads `credentials.json` to connect to Google Sheets
   - **Think of it as:** The script getting its instructions and tools ready

3. **Script connects to Google Sheets:**
   - Uses the service account (from credentials.json) to log into Google
   - Opens your specific Google Sheet (using the Sheet ID from config.json)
   - Finds the master sheet tab (usually "Sheet1")
   - **Think of it as:** The script walking into your filing cabinet and opening the right drawer

4. **Script finds people to email:**
   - Reads all rows from your master sheet
   - Skips the header row (row 1 with "Name", "Email", etc.)
   - Looks for rows where the Status column (column E) is empty or blank
   - Takes the first 50 people it finds (because you said `--size 50`)
   - **Think of it as:** The script looking through your list and finding 50 people who haven't been contacted yet

5. **For each person, the script creates a personalized email:**
   - Takes their name from column A
   - Takes their email from column B
   - Creates a special Google Form link with their name pre-filled (using `generate_form_url()`)
   - Builds a beautiful HTML email with:
     - Personalized greeting: "Dear [Name],"
     - Your grant message
     - A button/link to the form
     - Deadline information
   - **Think of it as:** The script writing a personalized letter for each person, with their name and a special reply card that already has their name on it

6. **Script sends the email via Gmail:**
   - Connects to Gmail's email server (smtp.gmail.com)
   - Logs in using your email address and App Password
   - Sends the email with:
     - From: Your Name <your-email@gmail.com>
     - To: The person's email address
     - Subject: "Support Needed: Historic Holliday Park Grant Initiative"
     - Body: The beautiful HTML email it created
   - **Think of it as:** The script putting the letter in an envelope, addressing it, and dropping it in the mailbox

7. **Script updates the Google Sheet:**
   - If email sent successfully:
     - Updates Status column to "Sent"
     - Updates SentDate column to today's date (format: YYYY-MM-DD)
   - If email failed:
     - Updates Status column to "Failed - [error message]"
     - Leaves SentDate empty
   - **Think of it as:** The script checking off names on your list and writing down the date

8. **Script shows you the results:**
   - Prints progress for each email: "Sending to: John Doe (john@example.com)... ✓ Sent successfully"
   - At the end, shows summary: "Sent: 50, Failed: 0"
   - **Think of it as:** The script giving you a report of what it did

**What the recipient sees:**
- An email in their inbox from you
- A beautifully formatted email with their name in the greeting
- Your grant campaign message
- A prominent button or link that says "Complete Your Response" or similar
- When they click it, a Google Form opens with their name already filled in

**Behind the scenes - the pre-fill magic:**
When the script creates the form link, it encodes the person's name in the URL. For example:
- Regular form link: `https://docs.google.com/forms/d/e/.../viewform`
- Pre-filled link: `https://docs.google.com/forms/d/e/.../viewform?entry.1392369941=John+Doe`

When someone clicks the pre-filled link, Google Forms sees the name in the URL and automatically fills it in the "Your Name" field. They don't have to type it!

### Step 2: Response Capture (Automatic)

**What happens when someone responds:**

1. **Person receives your email:**
   - They see your personalized email in their inbox
   - They read your grant message
   - They click the "Complete Your Response" button/link

2. **Google Form opens:**
   - The form opens in their web browser
   - Their name is already filled in (the pre-fill magic!)
   - They see the question: "Do you support this grant initiative?"
   - They see options: Yes, No, or Other (with a text box)

3. **Person submits their response:**
   - They select their answer (Yes/No/Other)
   - If "Other", they type additional comments
   - They click "Submit"

4. **Google automatically saves the response:**
   - Google Forms processes the submission
   - Creates a new row in your "Form Responses" tab in Google Sheets
   - Records:
     - Timestamp: When they submitted (Column A)
     - Your Name: Their name (Column B) - already filled in!
     - Response: Their answer - Yes/No/Other (Column C)
     - Response Text: Any additional comments (Column D)

5. **You can see it immediately:**
   - Open your Google Sheet
   - Click on the "Form Responses" tab
   - See the new row with their response
   - **Think of it as:** A reply card automatically appearing in your filing cabinet

**The beauty of automation:**
You don't have to do anything! The response appears automatically. No need to:
- Check your email for replies
- Manually enter responses into a spreadsheet
- Match names to your master list
- Worry about typos or missing information

**How the system matches names:**
When someone responds, their name appears in the Form Responses tab. The system can match this name to your master sheet to:
- Find their email address (for sending thank yous)
- Update their status
- Avoid sending duplicate emails

The matching is case-insensitive and handles whitespace, so "John Doe", "john doe", and "  John Doe  " all match correctly.

### Step 3: Reminders (send_reminders.py)

**What happens when you run the script:**

1. **You type the command:**
   ```bash
   python send_reminders.py
   ```
   This tells the script: "Find people who haven't responded and send them reminders."

2. **Script loads settings and connects to Google Sheets:**
   - Same as Step 1: loads config, credentials, connects to your sheet
   - Opens TWO tabs:
     - Master sheet (Sheet1): Your main list
     - Form Responses tab: All the responses collected so far

3. **Script finds responders:**
   - Reads all rows from the Form Responses tab
   - Extracts names from column B (the "Your Name" column)
   - Creates a set of all responder names (normalized: lowercase, trimmed)
   - **Example:** If 25 people responded, you get a set like: {"john doe", "jane smith", "bob jones", ...}
   - **Think of it as:** The script making a list of everyone who mailed back their reply card

4. **Script finds non-responders:**
   - Reads all rows from the master sheet
   - For each person, checks:
     - Status = "Sent" (they got the initial email)
     - Their name is NOT in the responder names set (they haven't responded)
     - ReminderSent column is empty (they haven't gotten a reminder yet)
   - If all three are true, adds them to the "non-responders" list
   - **Think of it as:** The script comparing your mailing list to your reply cards and finding people who got the letter but didn't respond

5. **Script creates reminder emails:**
   - For each non-responder, creates a SHORTER email:
     - Subject: "Reminder: Grant Support Needed by [deadline]"
     - Body: One paragraph explaining this is a reminder
     - Same personalized form link (with their name pre-filled)
     - Urgency message: "Please respond by [deadline]"
   - **Think of it as:** The script writing a shorter, more urgent follow-up letter

6. **Script sends reminder emails:**
   - Same process as Step 1: connects to Gmail, sends emails
   - Updates ReminderSent column with today's date for successful sends
   - **Think of it as:** The script sending out the follow-up letters

7. **Script shows you the results:**
   - Prints: "Found X people who haven't responded"
   - Shows progress for each reminder sent
   - Summary: "Reminders sent: X, Failed: Y"

**Why reminders are important:**
- People are busy and might miss the first email
- A gentle reminder increases response rates
- Shows you're organized and serious about the campaign
- Helps you reach your goal before the deadline

**Why wait 3-7 days?**
- Gives people time to read and respond
- Avoids seeming pushy or spammy
- Respects people's time and inbox
- Industry best practice for email campaigns

**How it avoids bothering people who already responded:**
The script checks if someone's name is in the responder names set BEFORE adding them to the non-responders list. If they responded, their name is in the set, so they're skipped. Simple and effective!

### Step 4: Thank Yous (send_thanks.py)

**What happens when you run the script:**

1. **You type the command:**
   ```bash
   python send_thanks.py
   ```
   This tells the script: "Find everyone who responded and send them thank you emails."

2. **Script loads settings and connects to Google Sheets:**
   - Same as previous steps: loads config, credentials, connects
   - Opens both master sheet and Form Responses tab

3. **Script finds responders who need thank yous:**
   - Reads all rows from Form Responses tab
   - For each responder:
     - Gets their name from column B
     - Gets their response (Yes/No/Other) from column C
     - Matches their name to the master sheet to get their email address
     - Checks if ThankYouSent column is empty (haven't sent thank you yet)
     - If all match, adds them to the "need thank you" list
   - **Think of it as:** The script finding everyone who mailed back a reply card and checking if you've already sent them a thank you

4. **Script creates personalized thank you emails:**
   - For each responder, creates a personalized email based on their response:
     - **If they said "Yes":**
       - Subject: "Thank You for Your Support"
       - Body: Thanks them for supporting the grant initiative
     - **If they said "No" or "Other":**
       - Subject: "Thank You for Your Feedback"
       - Body: Thanks them for taking the time to respond and provide feedback
   - **Think of it as:** The script writing personalized thank you cards - different messages for supporters vs. people who said no

5. **Script sends thank you emails:**
   - Connects to Gmail, sends personalized thank yous
   - Updates ThankYouSent column with today's date
   - **Think of it as:** The script mailing out the thank you cards

6. **Script shows you the results:**
   - Prints: "Found X people who responded and need thank yous"
   - Shows progress for each thank you sent
   - Summary: "Thank yous sent: X, Failed: Y"

**Why personalize thank yous:**
- People who said "Yes" get thanked for their support (they're helping you!)
- People who said "No" get thanked for their time and consideration (still respectful!)
- Shows you read their responses and care about their feedback
- Professional and thoughtful

**How it avoids sending duplicates:**
The script checks the ThankYouSent column before sending. If it's not empty, it means you already sent a thank you, so they're skipped. Simple!

## Technical Concepts - Simplified

### What is a Virtual Environment and Why Do We Need It?

**Simple explanation:** A virtual environment is like a separate toolbox for your project. It keeps all the Python tools (called "packages" or "libraries") that your project needs, separate from other projects on your computer.

**Why it matters:**
- Different projects might need different versions of the same tool
- Keeps your project organized and self-contained
- Makes it easy to share your project (others can recreate the same toolbox)
- Prevents conflicts between projects

**Real-world analogy:** Think of it like having separate toolboxes for different jobs. Your car repair toolbox has different tools than your woodworking toolbox. You wouldn't want to mix them up!

**How it works:**
- You create it: `python -m venv .venv`
- You activate it: `.venv\Scripts\Activate.ps1` (Windows) or `source .venv/bin/activate` (Mac/Linux)
- You install tools: `pip install -r requirements.txt`
- Now your project has its own isolated toolbox!

**What you see:** When activated, your command prompt shows `(.venv)` at the beginning, like putting on your work gloves.

### What is an API and Why Do We Use Google Sheets API?

**Simple explanation:** An API (Application Programming Interface) is like a menu at a restaurant. It's a list of things you can ask a service to do, and how to ask for them.

**Why it matters:**
- Google Sheets has an API that lets programs read and write to sheets
- Without it, you'd have to manually copy/paste data
- With it, Python scripts can automatically update your sheet

**Real-world analogy:** Think of it like a drive-through menu. You can't go into the kitchen, but you can order from the menu (the API). The restaurant (Google) prepares your order (reads/writes data) and gives it to you.

**How it works:**
- Google provides the Google Sheets API (the menu)
- Your Python scripts use the `gspread` library (like a waiter who knows how to read the menu)
- The service account (your robot assistant) has permission to use the API
- Together, they let your scripts read and write to your sheet automatically

**What you don't see:** All the complex communication happening behind the scenes. You just see your sheet updating automatically!

### What is a Service Account (The Robot Helper)?

**Simple explanation:** A service account is a special Google account that acts like a robot assistant. It's not a real person - it's a program that can access your Google Sheet on your behalf.

**Why it matters:**
- Programs can't log in like humans (they can't type passwords or do 2FA)
- Service accounts have special "keys" (credentials.json) that let them access Google services
- They have limited permissions (can only access what you share with them)

**Real-world analogy:** Think of it like giving a robot assistant a key card to your office building. The key card only works for specific rooms (the Google Sheets you share), and the robot can only do specific tasks (read and write data). It can't access your email, delete files, or do anything else.

**How it works:**
1. You create a service account in Google Cloud Console
2. Google gives you a special file (credentials.json) - this is the "key card"
3. You share your Google Sheet with the service account's email address (like giving the robot permission to enter)
4. Your Python scripts use credentials.json to "be" the service account
5. Now the scripts can read and write to your sheet automatically

**Security:** Service accounts are safer than using your personal account because:
- They have limited permissions (only what you share)
- They can't access your other Google services
- If someone gets the credentials file, they can only access the sheets you've shared (not your entire Google account)

### What is an App Password vs. Regular Password?

**Simple explanation:** An App Password is a special 16-character password that lets programs send emails through your Gmail account. It's different from your regular password and more secure for automation.

**Why it matters:**
- Your regular password is for logging into Gmail in a browser
- App Passwords are for programs that need to send emails automatically
- They're more secure because they have limited permissions

**Real-world analogy:** Think of your regular password like the master key to your house. The App Password is like a key that only works for the mailbox - it can send mail but can't unlock your front door or access anything else.

**How it works:**
1. You enable 2-Factor Authentication on your Gmail account (for security)
2. You generate an App Password in your Google Account settings
3. Google gives you a 16-character password (like: `abcd efgh ijkl mnop`)
4. You save it in a `.env` file: `GMAIL_APP_PASSWORD=abcdefghijklmnop`
5. Your Python scripts use this password to log into Gmail and send emails

**Why not use your regular password?**
- Security: If someone gets your App Password, they can only send emails - they can't read your emails, change your settings, or access your account
- Compatibility: Programs can't handle 2FA prompts, so App Passwords work around that
- Best practice: Google recommends using App Passwords for automated email sending

### What Does "Dry-Run" Mean?

**Simple explanation:** A dry-run is a test mode where the script shows you what it WOULD do without actually doing it. Like a fire drill - you practice the procedure without the real emergency.

**Why it matters:**
- Lets you test before sending real emails
- Shows you who would get emails
- Helps you catch mistakes before they happen
- Gives you confidence that everything is set up correctly

**Real-world analogy:** Think of it like a dress rehearsal for a play. You go through all the motions, but it's not the real performance. You can see what will happen, make adjustments, and then do it for real.

**How it works:**
- You add `--dry-run` flag: `python send_batch.py --size 50 --dry-run`
- Script runs normally but:
  - Doesn't actually send emails (prints "[DRY RUN] Would send email (skipped)")
  - Doesn't update Google Sheets (doesn't mark Status as "Sent")
  - Shows you everything it WOULD do
- You review the output, make sure it looks right
- Then run it for real (without `--dry-run`)

**What you see:**
```
[DRY RUN] Would send email to: John Doe (john@example.com) (skipped)
[DRY RUN] Would update Status to 'Sent' (skipped)
```

**Best practice:** Always dry-run first, especially with large batches!

### What Does "Batch" Mean?

**Simple explanation:** A batch is a group of emails sent together. You can send to everyone at once, or in smaller groups (batches).

**Why it matters:**
- Sending in batches helps you:
  - Test with small groups first (start with 5, then 50, then everyone)
  - Avoid overwhelming Gmail's servers
  - Catch errors early (if batch 1 fails, you know before sending batch 2)
  - Process large lists gradually

**Real-world analogy:** Think of it like mailing letters. You could mail all 200 at once, or you could mail 50 today, 50 tomorrow, etc. Batching gives you more control.

**How it works:**
- You specify batch size: `python send_batch.py --size 50`
- Script finds people who need emails
- Takes the first 50 it finds
- Sends to those 50
- Next time you run it, it finds the next 50 (who still have empty Status)
- Repeat until everyone is sent

**Example workflow:**
```bash
# Day 1: Test with 5
python send_batch.py --size 5 --dry-run
python send_batch.py --size 5

# Day 2: Send to 50
python send_batch.py --size 50

# Day 3: Send to remaining 150
python send_batch.py --size 150
```

### What is a Pre-Filled URL?

**Simple explanation:** A pre-filled URL is a special link to your Google Form that has information already encoded in it. When someone clicks it, the form opens with their name (or other info) already filled in.

**Why it matters:**
- Makes responding easier (people don't have to type their name)
- Ensures names match correctly (no typos)
- Reduces friction (one less thing to do = more responses)
- Professional and thoughtful

**Real-world analogy:** Think of it like a reply card that already has your address printed on it. You don't have to write it - it's already there!

**How it works:**
1. Script takes person's name: "John Doe"
2. Encodes it for URL: "John+Doe" (spaces become + signs)
3. Adds it to form URL: `https://docs.google.com/forms/.../viewform?entry.1392369941=John+Doe`
4. Person clicks link
5. Google Forms sees the name in the URL
6. Automatically fills in the "Your Name" field
7. Person just needs to answer the question and submit

**The technical part:** The `entry.1392369941` part is the field ID - it tells Google Forms which field to fill. This comes from your `config.json` file.

**What the person sees:**
- They click the link
- Form opens
- "Your Name" field already says "John Doe"
- They just select Yes/No/Other and submit
- Done!

## Troubleshooting - With Explanations

### "ModuleNotFoundError: No module named 'gspread'"

**What it means in plain English:** Python can't find the `gspread` tool it needs to connect to Google Sheets.

**Why it happened:** You're either:
- Not in the virtual environment (the toolbox isn't open)
- Haven't installed the required tools yet

**How to fix it:**
1. Make sure you activated the virtual environment:
   ```bash
   .venv\Scripts\Activate.ps1  # Windows
   # or
   source .venv/bin/activate   # Mac/Linux
   ```
   You should see `(.venv)` in your prompt.

2. Install the tools:
   ```bash
   pip install -r requirements.txt
   ```

**How to prevent it:** Always activate the virtual environment before running scripts. It's like putting on your work gloves before starting work!

### "SMTP Authentication failed"

**What it means in plain English:** Gmail rejected your login attempt. The email and password combination didn't work.

**Why it happened:**
- Wrong App Password in `.env` file
- App Password has extra spaces or characters
- `.env` file is in the wrong location
- Using regular password instead of App Password

**How to fix it:**
1. Check your `.env` file exists in the project root (same folder as `send_batch.py`)
2. Open `.env` and verify the line: `GMAIL_APP_PASSWORD=your16charpassword`
   - No spaces around the `=`
   - No quotes around the password
   - Exactly 16 characters (might have spaces: `abcd efgh ijkl mnop` - remove spaces or keep them, but be consistent)
3. Regenerate App Password if needed:
   - Go to myaccount.google.com/apppasswords
   - Generate a new App Password
   - Copy it exactly (no extra spaces)
   - Update `.env` file
4. Make sure you're using App Password, not your regular Gmail password

**How to prevent it:** Double-check your `.env` file setup. The App Password should be exactly as Google generated it, with no modifications.

### "Responses worksheet not found"

**What it means in plain English:** The script can't find the "Form Responses" tab in your Google Sheet.

**Why it happened:**
- The tab name in `config.json` doesn't match your actual sheet tab name
- Tab name has different capitalization or spacing
- Tab doesn't exist yet (no one has responded to your form)

**How to fix it:**
1. Open your Google Sheet
2. Look at the tab names at the bottom
3. Find the exact name of your Form Responses tab (might be "Form Responses", "Form_Responses", "Form Responses 1", etc.)
4. Open `config.json`
5. Update `responses_sheet_tab` to match exactly:
   ```json
   "responses_sheet_tab": "Form Responses"
   ```
   (Use the exact name, including spaces and capitalization)
6. Save `config.json`
7. Run the script again

**How to prevent it:** When setting up, double-check the tab name matches exactly. You can also run `send_reminders.py --dry-run` to see a list of available worksheet names.

### "No people found"

**What it means in plain English:** The script looked for people to email but couldn't find anyone who matches the criteria.

**Why it happened:**
- For `send_batch.py`: Everyone already has a Status (all are "Sent" or "Failed")
- For `send_reminders.py`: Everyone either responded or already got a reminder
- For `send_thanks.py`: Everyone who responded already got a thank you

**How to fix it:**
- **For send_batch.py:** Check your master sheet. If Status column has values for everyone, you've already sent to everyone! If you want to send again, you'd need to clear the Status column (but be careful - this might send duplicates).
- **For send_reminders.py:** This is actually good news! It means everyone either responded or already got a reminder. Check your Form Responses tab to see who responded.
- **For send_thanks.py:** Everyone who responded already got thanked! Check the ThankYouSent column in your master sheet.

**How to prevent it:** This isn't really an error - it's the script telling you there's nothing to do. Review your sheet to understand the current status.

### "Worksheet not found"

**What it means in plain English:** The script can't find a specific tab in your Google Sheet.

**Why it happened:** Similar to "Responses worksheet not found" - the tab name doesn't match.

**How to fix it:**
1. Run `send_reminders.py --dry-run` - it will show you all available worksheet names
2. Compare the list to what's in your `config.json`
3. Update `config.json` with the correct tab name
4. Make sure the sheet is shared with your service account email

**How to prevent it:** When setting up, verify all tab names match between your Google Sheet and `config.json`.

## Visual Aids

### Data Flow Diagram

```
┌─────────────────┐
│   You (User)    │
│  Run Scripts    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Python Scripts │
│  (send_batch,   │
│   reminders,    │
│   thanks)        │
└────────┬────────┘
         │
         ├──────────────────┬──────────────────┐
         ▼                  ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ Google Sheets│  │  Gmail API   │  │ Google Forms │
│  (Database)   │  │ (Send Email) │  │ (Collect     │
│              │  │              │  │  Responses)   │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       │                 │                 │
       │                 │                 │
       └─────────────────┴─────────────────┘
                         │
                         ▼
              ┌──────────────────┐
              │   Recipients     │
              │  (Your Neighbors)│
              └──────────────────┘
```

### Decision Logic: Who Gets What Email?

```
START: Run Script
  │
  ▼
Read Master Sheet
  │
  ▼
For send_batch.py:
  ├─ Status empty? → Send initial email
  └─ Status = "Sent"? → Skip (already sent)

For send_reminders.py:
  ├─ Status = "Sent"? → Check next condition
  │   ├─ Name in responses? → Skip (they responded)
  │   └─ Name NOT in responses? → Check next condition
  │       ├─ ReminderSent empty? → Send reminder
  │       └─ ReminderSent filled? → Skip (already reminded)

For send_thanks.py:
  ├─ Name in responses? → Check next condition
  │   ├─ ThankYouSent empty? → Send thank you
  │   └─ ThankYouSent filled? → Skip (already thanked)
  └─ Name NOT in responses? → Skip (they didn't respond)
```

### Component Relationships

```
┌─────────────────────────────────────────────────────────┐
│                    Grant Tracker System                  │
└─────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ config.json  │    │ credentials. │    │    .env      │
│ (Settings)   │    │    json      │    │ (Gmail Pass) │
│              │    │ (Service Acct│    │              │
│ - Sheet ID   │    │  Credentials)│    │ - App Pass   │
│ - Form URL   │    │              │    │              │
│ - Sender Info│    │              │    │              │
└──────┬───────┘    └──────┬───────┘    └──────┬───────┘
       │                   │                   │
       └───────────────────┼───────────────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │  Python Scripts │
                  │                 │
                  │ - email_gen     │
                  │ - send_batch    │
                  │ - reminders     │
                  │ - thanks        │
                  └────────┬────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ Google Sheets│  │  Gmail SMTP  │  │ Google Forms │
│              │  │              │  │              │
│ Reads:       │  │ Sends:       │  │ Collects:    │
│ - Names      │  │ - Emails     │  │ - Responses  │
│ - Emails     │  │              │  │              │
│ - Status     │  │              │  │              │
│              │  │              │  │              │
│ Writes:      │  │              │  │              │
│ - Status     │  │              │  │              │
│ - Dates      │  │              │  │              │
└──────────────┘  └──────────────┘  └──────────────┘
```

## Conclusion

Grant Tracker is like having a team of helpful assistants working together:
- **Google Sheets** is your filing cabinet (stores everything)
- **Google Forms** is your reply card collector (gathers responses)
- **Service Account** is your robot assistant (accesses files automatically)
- **Gmail App Password** is your mailbox key (sends emails securely)
- **Python Scripts** are your workers (automate all the tasks)

Together, they handle the entire email campaign from start to finish, leaving you free to focus on other important work.

Remember:
- Always dry-run first to test
- Start with small batches to verify everything works
- Check your Google Sheet regularly to see progress
- The system is smart - it won't send duplicates or bother people who already responded

Happy campaigning! 🎉
