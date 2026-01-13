# Grant Tracker - Quick Reference

## Daily Commands

### Send Initial Campaign
```bash
# Always test first!
python send_batch.py --size 50 --dry-run

# Then send for real
python send_batch.py --size 50
```

### Send Reminders (after 3-7 days)
```bash
# Test first
python send_reminders.py --dry-run

# Send reminders
python send_reminders.py
```

### Send Thank Yous
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
