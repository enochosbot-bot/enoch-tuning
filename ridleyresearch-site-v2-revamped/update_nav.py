#!/usr/bin/env python3
"""
update_nav.py — Replace nav dropdown menu content across all HTML files.
Uses regex to find and replace the entire nav-dropdown-menu div content.
"""

import os
import re
import sys

SITE_DIR = "/Users/deaconsopenclaw/.openclaw/workspace/ridleyresearch-site-v2-revamped/ridleyresearch-site-v2"

# The canonical new nav dropdown menu content
NEW_NAV = """<div class="nav-dropdown-menu">
            <div class="dropdown-section-label">Explore</div>
            <a href="/testimonials/submit">⭐ Leave a Review</a>
            <a href="/about">About</a>
            <a href="/blog/">Blog</a>
            <a href="/openclaw/what-is-openclaw">OpenClaw →</a>
            <div class="dropdown-section-label">Work With Us</div>
            <a href="/small-business/">Small Business →</a>
            <a href="/products/">Products &amp; Pricing</a>
            <a href="mailto:hello@ridleyresearch.com?subject=Discovery%20Call">Book a Discovery Call</a>
          </div>"""

# Pattern: match the entire nav-dropdown-menu div
# We use DOTALL to match across newlines
PATTERN = re.compile(
    r'<div class="nav-dropdown-menu">.*?</div>',
    re.DOTALL
)

def get_all_html_files(root):
    html_files = []
    for dirpath, dirnames, filenames in os.walk(root):
        # Skip hidden dirs and functions dir
        dirnames[:] = [d for d in dirnames if not d.startswith('.')]
        for fname in filenames:
            if fname.endswith('.html'):
                html_files.append(os.path.join(dirpath, fname))
    return html_files

def update_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if this file has a nav-dropdown-menu
    if 'class="nav-dropdown-menu"' not in content:
        return False, "no nav-dropdown-menu found"

    new_content, count = PATTERN.subn(NEW_NAV, content, count=1)

    if count == 0:
        return False, "regex did not match"

    if new_content == content:
        return False, "no change (already up to date)"

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)

    return True, f"updated ({count} replacement)"

def main():
    html_files = get_all_html_files(SITE_DIR)
    print(f"Found {len(html_files)} HTML files.\n")

    updated = 0
    skipped = 0
    errors = []

    for fpath in sorted(html_files):
        rel = os.path.relpath(fpath, SITE_DIR)
        try:
            ok, msg = update_file(fpath)
            if ok:
                print(f"  ✅  {rel} — {msg}")
                updated += 1
            else:
                print(f"  ⚠️   {rel} — {msg}")
                skipped += 1
        except Exception as e:
            print(f"  ❌  {rel} — ERROR: {e}")
            errors.append((rel, str(e)))

    print(f"\n{'='*60}")
    print(f"Done. Updated: {updated}  |  Skipped: {skipped}  |  Errors: {len(errors)}")
    if errors:
        print("\nErrors:")
        for rel, err in errors:
            print(f"  {rel}: {err}")
        sys.exit(1)

if __name__ == '__main__':
    main()
