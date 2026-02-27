#!/usr/bin/env python3
"""Auto-sort Gmail using rules + AI fallback for ambiguous emails."""

import subprocess, json, re, sys, os

ACCOUNT = "deacon.ridley@gmail.com"

# Label IDs mapped from gog gmail labels list
LABELS = {
    "Events/Tickets/Receipts": "Label_6215911476932695930",
    "*AI": "Label_6195479638041814445",
    "*Spectrum": "Label_7026831307339453875",
    "*Politics": "Label_6843348990715824071",
    "*Taxes & Important Docs": "Label_8803829645104243768",
    "Financial": "Label_2256303730845995727",
    "Car": "Label_8386894919439776982",
    "Church": "Label_8002151879889028078",
    "Music": "Label_8272197634868836757",
    "Family": "Label_3273518040908559549",
    "Ellisyn <3": "Label_901535972652290226",
    "Career": "Label_5822780789661806535",
    "CFP": "Label_6761691424490922841",
    "Housing": "Label_3759805869569080938",
    "Networking": "Label_3889624343388305810",
    "Nonna": "Label_1550431354295241237",
    "Traveling": "Label_1980537551729784393",
    "Misc": "Label_2183405805860551293",
    "Notes/Reading": "Label_1",
    "Trading": "Label_2",
}

# Rule-based sorting: (from_pattern, subject_pattern) -> label_name
# First match wins. Patterns are case-insensitive regex.
RULES = [
    # Receipts & Orders
    (r"chick-fil-a|doordash|uber.*eats|grubhub|instacart|amazon\.com.*order|target\.com|walmart|order.*confirm|receipt|payment.*receipt|noreply@order", r"receipt|order|payment|confirm|delivery|shipped", "Events/Tickets/Receipts"),
    (r"stripe\.com|square|venmo|zelle|paypal|cashapp", r"receipt|payment|paid", "Events/Tickets/Receipts"),
    (r"ticketmaster|stubhub|seatgeek|eventbrite|axs\.com", r"ticket|order|confirm|event", "Events/Tickets/Receipts"),
    
    # AI & Tech
    (r"openai|anthropic|openclaw|ngrok|twilio|brave.*search|ollama|openrouter|notion|synth|cursor|github|vercel|netlify|heroku|digitalocean|inference\.net|x\.ai|xai", r"", "*AI"),
    (r"google.*cloud|firebase|gcloud|takeout", r"", "*AI"),
    
    # Spectrum / Work
    (r"spectrum.*advisor|redtail|emoney|orion|@spectrumadvisors", r"", "*Spectrum"),
    (r"", r"spectrum.*advisor|client.*meeting|compliance|finra|sec.*filing", "*Spectrum"),
    
    # CFP
    (r"cfp.*board|cfp\.net|kaplan|dalton|wiley.*cfp", r"", "CFP"),
    (r"", r"cfp.*exam|cfp.*study|certified financial", "CFP"),
    
    # Financial
    (r"citi.*card|chase|bank.*america|wells.*fargo|capital.*one|discover|amex|credit.*karma|mint\.com|ynab|betterment|fidelity|schwab|vanguard", r"", "Financial"),
    (r"", r"statement|balance|payment.*due|credit.*score|account.*summary", "Financial"),
    
    # Car
    (r"mcdavid|parkplace|honda|acura|toyota|autozone|oreill|carfax|geico|progressive|allstate|state.*farm", r"", "Car"),
    (r"", r"vehicle.*service|oil.*change|tire|car.*insurance|auto.*payment", "Car"),
    
    # Church
    (r"stonebriar|reformation.*church|thereformationchurch|planningcenter|subsplash|pushpay|tithe", r"", "Church"),
    (r"", r"sermon|worship|bible.*study|small.*group|ministry|tithe|offering", "Church"),
    
    # Ellisyn
    (r"ellisyn|strava.*ellisyn", r"", "Ellisyn <3"),
    
    # Family
    (r"", r"family.*reunion|thanksgiving|christmas.*dinner", "Family"),
    
    # Trading
    (r"polymarket|kalshi|predictit|robinhood|webull|coinbase|moonpay|binance", r"", "Trading"),
    
    # Politics
    (r"fuentes|america.*first|tpusa|turning.*point|prager", r"", "*Politics"),
    
    # Housing
    (r"zillow|realtor|redfin|apartments|rent|lease|hoa|homeowner", r"", "Housing"),
    (r"", r"rent|lease|mortgage|hoa|property.*tax|homeowner", "Housing"),
    
    # Taxes
    (r"irs\.gov|turbotax|hrblock|taxact|intuit.*tax", r"", "*Taxes & Important Docs"),
    (r"", r"w-2|1099|tax.*return|tax.*refund|estimated.*tax", "*Taxes & Important Docs"),
    
    # Music
    (r"spotify|apple.*music|bandcamp|soundcloud", r"", "Music"),
    
    # Strava / Ellisyn mentions
    (r"strava.*ellisyn|ellisyn.*ridley", r"", "Ellisyn <3"),
    (r"strava", r"ellisyn", "Ellisyn <3"),
    (r"", r"ellisyn", "Ellisyn <3"),
    
    # Health insurance (→ Financial or leave as action required)
    (r"marshmma|blue.*cross|aetna|cigna|united.*health|humana", r"", "Financial"),
    
    # Health / Appointments (→ Misc)
    (r"mytimemail|zocdoc|healthgrades|dentist|doctor|patient.*portal", r"", "Misc"),
    (r"", r"appointment.*reschedul|appointment.*confirm|your.*appointment", "Misc"),
    
    # AI tools (broader catch)
    (r"perplexity|cursor|moonpay|replit|supabase|railway|render\.com|fly\.io|cloudflare", r"", "*AI"),
    
    # X / Twitter security
    (r"verify@x\.com|noreply@x\.com", r"", "*AI"),
    
    # Kalshi / enoch bot
    (r"enoch\.os\.bot|kalshi", r"", "*AI"),
    
    # Traveling
    (r"airlines|expedia|booking\.com|airbnb|marriott|hilton|hyatt|southwest|united|delta|american.*air|tsa", r"", "Traveling"),
    (r"", r"flight|hotel|reservation|boarding.*pass|itinerary|travel", "Traveling"),
    
    # Networking
    (r"linkedin|meetup\.com", r"", "Networking"),
]

# Senders/subjects to auto-archive (remove from INBOX, keep labeled)
AUTO_ARCHIVE_PATTERNS = [
    r"promotions.*@|marketing@|newsletter@|noreply.*promo",
]

# Senders to auto-trash
AUTO_DELETE_PATTERNS = [
    r"strava",
]


def gog_cmd(args):
    """Run a gog command and return output."""
    cmd = ["gog"] + args + ["--account", ACCOUNT]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    return result.stdout.strip(), result.returncode


def get_unsorted_emails(max_results=20):
    """Get recent inbox emails that don't have user labels yet."""
    query = "in:inbox" if "--all" in sys.argv else "in:inbox newer_than:3d"
    out, rc = gog_cmd(["gmail", "search", query, "--max", str(max_results), "--json"])
    if rc != 0:
        # Fall back to plain
        out, rc = gog_cmd(["gmail", "search", "in:inbox newer_than:3d", "--max", str(max_results)])
        if rc != 0:
            print(f"Error searching: {out}")
            return []
        # Parse plain output
        emails = []
        lines = out.strip().split("\n")
        if len(lines) < 2:
            return []
        for line in lines[1:]:  # Skip header
            if line.startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) >= 6:
                emails.append({
                    "id": parts[0].strip(),
                    "date": parts[1].strip(),
                    "from": parts[2].strip(),
                    "subject": parts[3].strip(),
                    "labels": parts[4].strip(),
                })
        return emails
    
    try:
        data = json.loads(out)
        if isinstance(data, dict):
            data = data.get("threads", data.get("messages", []))
        return data
    except:
        return []


def match_rules(from_addr, subject):
    """Try to match email against rules. Returns label name or None."""
    from_lower = from_addr.lower()
    subj_lower = subject.lower()
    
    for from_pat, subj_pat, label in RULES:
        from_match = (not from_pat) or re.search(from_pat, from_lower)
        subj_match = (not subj_pat) or re.search(subj_pat, subj_lower)
        if from_match and subj_match:
            return label
    return None


def apply_label(email_id, label_name):
    """Apply a label to an email."""
    label_id = LABELS.get(label_name)
    if not label_id:
        print(f"  ⚠️  Unknown label: {label_name}")
        return False
    
    out, rc = gog_cmd(["gmail", "labels", "modify", email_id, "--add", label_id])
    if rc == 0:
        print(f"  ✅ Labeled '{label_name}'")
        return True
    else:
        print(f"  ❌ Failed to label: {out}")
        return False


def has_user_label(labels_str):
    """Check if email already has a user-applied label."""
    user_label_names = set(LABELS.keys())
    if not labels_str:
        return False
    if isinstance(labels_str, list):
        current = [l.strip() if isinstance(l, str) else str(l) for l in labels_str]
    else:
        current = [l.strip() for l in str(labels_str).split(",")]
    return any(l in user_label_names for l in current)


def main():
    dry_run = "--dry-run" in sys.argv
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    
    print(f"📧 Email Auto-Sorter {'(DRY RUN)' if dry_run else ''}")
    print(f"   Account: {ACCOUNT}")
    print()
    
    emails = get_unsorted_emails(30)
    if not emails:
        print("No emails to process.")
        return
    
    sorted_count = 0
    skipped = 0
    
    for email in emails:
        eid = email.get("id", "")
        from_addr = email.get("from", "")
        subject = email.get("subject", "")
        labels = email.get("labels", "")
        
        # Skip if already has a user label
        if has_user_label(labels):
            if verbose:
                print(f"  ⏭️  Already labeled: {subject[:50]}")
            skipped += 1
            continue
        
        print(f"📩 {subject[:60]}")
        print(f"   From: {from_addr[:50]}")
        
        # Check auto-delete first
        from_lower = from_addr.lower()
        should_delete = any(re.search(p, from_lower) for p in AUTO_DELETE_PATTERNS)
        if should_delete:
            if dry_run:
                print(f"  🗑️  Would delete (Strava etc)")
            else:
                out, rc = gog_cmd(["gmail", "labels", "modify", eid, "--add", "TRASH", "--remove", "INBOX"])
                print(f"  🗑️  Trashed")
            sorted_count += 1
            continue
        
        label = match_rules(from_addr, subject)
        
        if label:
            if dry_run:
                print(f"  🏷️  Would label: {label}")
            else:
                apply_label(eid, label)
                # Mark as read + archive (remove from inbox) unless it's action-required
                # Action required = keep unread in inbox
                action_labels = {"Financial", "*Taxes & Important Docs", "*Spectrum", "CFP"}
                action_subjects = re.compile(r"action.*need|action.*required|urgent|please.*respond|deadline|due.*date|overdue|past.*due|expiring|blue.*cross.*application", re.I)
                is_action = label in action_labels and action_subjects.search(subject)
                
                if not is_action:
                    # Mark read + remove from inbox
                    gog_cmd(["gmail", "labels", "modify", eid, "--remove", "INBOX,UNREAD"])
            sorted_count += 1
        else:
            print(f"  ❓ No rule matched — left in inbox")
    
    print(f"\n📊 Results: {sorted_count} sorted, {skipped} already labeled, {len(emails) - sorted_count - skipped} unmatched")


if __name__ == "__main__":
    main()
