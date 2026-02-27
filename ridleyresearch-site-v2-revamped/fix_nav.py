#!/usr/bin/env python3
"""
fix_nav.py — Remove orphaned duplicate nav links from all HTML files.

The prior nav update left a second set of links outside the .nav-dropdown-menu
div but still inside .nav-dropdown. The pattern to remove is everything
between the closing </div> of .nav-dropdown-menu and the extra spurious </div>
that follows it — leaving only the correct .nav-dropdown closing </div>.

Before (broken):
  <div class="nav-dropdown-menu">
    ... correct links ...
  </div>                          ← closes nav-dropdown-menu (keep)
    <a href="/testimonials/submit">... ← ORPHAN start (remove)
    ...
  </div>                          ← ORPHAN extra close (remove)
</div>                            ← closes nav-dropdown (keep)

After (fixed):
  <div class="nav-dropdown-menu">
    ... correct links ...
  </div>
</div>
"""

import re
import glob
import sys

SITE_DIR = "/Users/deaconsopenclaw/.openclaw/workspace/ridleyresearch-site-v2-revamped/ridleyresearch-site-v2"

# Match: the nav-dropdown-menu close div, then orphaned content (any links/divs
# starting with the orphan's first <a> tag), then the extra closing </div>.
# The orphan always starts with an <a href="/testimonials/submit"> tag after
# the nav-dropdown-menu closes.
ORPHAN_PATTERN = re.compile(
    r'([ \t]*</div>)\n'                            # closes nav-dropdown-menu
    r'[ \t]*\n?[ \t]*<a href="/testimonials/submit">.*?'  # orphan starts here
    r'[ \t]*</div>(\s*\n[ \t]*</div>)',            # orphan's extra </div> + real nav-dropdown close
    re.DOTALL
)

def fix_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        original = f.read()

    # Only touch files that have the nav-dropdown-menu AND an orphaned block
    if 'nav-dropdown-menu' not in original:
        return False, "no nav-dropdown-menu"
    if '<a href="/testimonials/submit">' not in original:
        return False, "no orphan anchor"

    fixed, count = ORPHAN_PATTERN.subn(r'\1\2', original)
    if count == 0:
        return False, "pattern not matched"

    if fixed == original:
        return False, "no change"

    with open(path, 'w', encoding='utf-8') as f:
        f.write(fixed)
    return True, f"{count} substitution(s)"

def main():
    files = sorted(
        glob.glob(f"{SITE_DIR}/**/*.html", recursive=True) +
        glob.glob(f"{SITE_DIR}/*.html")
    )
    # Deduplicate
    files = sorted(set(files))

    fixed_count = 0
    for path in files:
        changed, note = fix_file(path)
        rel = path.replace(SITE_DIR + "/", "")
        if changed:
            print(f"  ✓ FIXED   {rel} ({note})")
            fixed_count += 1
        else:
            print(f"  · skip    {rel} ({note})")

    print(f"\nDone: {fixed_count}/{len(files)} files fixed.")

if __name__ == "__main__":
    main()
