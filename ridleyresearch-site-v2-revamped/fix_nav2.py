#!/usr/bin/env python3
"""
fix_nav2.py — Restore the canonical nav in all broken HTML files.

The previous fix_nav.py was too greedy and removed the correct inner links
along with the orphan block. This script replaces the entire nav-dropdown block
(from <div class="nav-dropdown" to the matching </div> chain) with the
canonical clean version.

Canonical nav (same for all pages):
  <div class="nav-dropdown" id="ocDropdown">
    <button ...>Menu ▾</button>
    <div class="nav-dropdown-menu">
      Explore section + Work With Us section
    </div>
  </div>
"""

import re
import glob

SITE_DIR = "/Users/deaconsopenclaw/.openclaw/workspace/ridleyresearch-site-v2-revamped/ridleyresearch-site-v2"

CANONICAL_NAV_DROPDOWN = """        <div class="nav-dropdown" id="ocDropdown">
          <button class="nav-dropdown-btn" onclick="toggleDropdown('ocDropdown')">
            Menu <span class="chevron">▾</span>
          </button>
          <div class="nav-dropdown-menu">
            <div class="dropdown-section-label">Explore</div>
            <a href="/testimonials/submit">&#11088; Leave a Review</a>
            <a href="/about">About</a>
            <a href="/blog/">Blog</a>
            <a href="/openclaw/what-is-openclaw">OpenClaw &#8594;</a>
            <div class="dropdown-section-label">Work With Us</div>
            <a href="/small-business/">Small Business &#8594;</a>
            <a href="/products/">Products &amp; Pricing</a>
            <a href="mailto:hello@ridleyresearch.com?subject=Discovery%20Call">Book a Discovery Call</a>
          </div>
        </div>"""

# Pattern matches the nav-dropdown div from opening to its closing </div>
# regardless of what's inside (handles both broken and already-partially-fixed states)
# We match from `<div class="nav-dropdown"` to the closing sequence
# </div>\n      </div>\n    </div> which closes nav-dropdown, nav-links, nav-inner
NAV_DROPDOWN_PATTERN = re.compile(
    r'        <div class="nav-dropdown" id="ocDropdown">.*?'
    r'        </div>(?=\n      </div>\n    </div>)',
    re.DOTALL
)

def fix_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        original = f.read()

    if 'nav-dropdown' not in original:
        return False, "no nav-dropdown"

    fixed, count = NAV_DROPDOWN_PATTERN.subn(CANONICAL_NAV_DROPDOWN, original)

    if count == 0:
        return False, "pattern not matched"

    if fixed == original:
        return False, "no change"

    with open(path, 'w', encoding='utf-8') as f:
        f.write(fixed)
    return True, f"{count} substitution(s)"

def main():
    files = sorted(set(
        glob.glob(f"{SITE_DIR}/**/*.html", recursive=True) +
        glob.glob(f"{SITE_DIR}/*.html")
    ))

    fixed = 0
    for path in files:
        changed, note = fix_file(path)
        rel = path.replace(SITE_DIR + "/", "")
        if changed:
            print(f"  ✓ FIXED  {rel} ({note})")
            fixed += 1
        else:
            print(f"  · skip   {rel} ({note})")

    print(f"\nDone: {fixed}/{len(files)} files fixed.")

if __name__ == "__main__":
    main()
