#!/usr/bin/env python3
"""Generate charts for Jake Harker's OpenClaw guide."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

OUT = "/Users/deaconsopenclaw/.openclaw/workspace/tmp/charts-jake"

GOLD = '#D4A843'
DARK = '#1a1a2e'
RED = '#e94560'
GREEN = '#2ecc71'
BLUE = '#3498db'
ORANGE = '#e67e22'

plt.rcParams['font.family'] = 'Helvetica'
plt.rcParams['font.size'] = 12

# --- Chart 1: Compound Growth - Starting Now vs Later ---
fig, ax = plt.subplots(figsize=(10, 6))
weeks = list(range(0, 13))
labels = [f'Week {w}' for w in weeks]

# Automations built, skills configured, income streams
now = [0, 3, 7, 12, 18, 25, 33, 42, 52, 63, 75, 88, 102]
month_later = [0, 0, 0, 0, 3, 7, 12, 18, 25, 33, 42, 52, 63]
two_months = [0, 0, 0, 0, 0, 0, 0, 0, 3, 7, 12, 18, 25]

ax.plot(weeks, now, 'o-', color=GOLD, linewidth=2.5, markersize=7, label='Start Today')
ax.plot(weeks, month_later, 's--', color=ORANGE, linewidth=2, markersize=6, label='Start in 1 Month', alpha=0.7)
ax.plot(weeks, two_months, '^:', color=RED, linewidth=2, markersize=6, label='Start in 2 Months', alpha=0.5)

ax.fill_between(weeks, now, month_later, alpha=0.1, color=GOLD)

ax.set_xlabel('Timeline', fontweight='bold', fontsize=13)
ax.set_ylabel('Cumulative Automations & Assets Built', fontweight='bold', fontsize=13)
ax.set_title('The Compound Effect — Why Starting Now Matters', fontweight='bold', fontsize=15, color=DARK)
ax.legend(fontsize=11)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.set_xticks([0, 4, 8, 12])
ax.set_xticklabels(['Now', '1 Month', '2 Months', '3 Months'])

ax.annotate('Gap keeps\nwidening', xy=(10, 60), fontsize=12, fontweight='bold', color=GOLD,
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor=GOLD))

fig.tight_layout()
fig.savefig(f'{OUT}-compound.png', dpi=150, bbox_inches='tight')
plt.close()

# --- Chart 2: Side Income Scenarios ---
fig, ax = plt.subplots(figsize=(10, 6))
months = ['Month 1', 'Month 3', 'Month 6', 'Month 12']

cpa_solo = [500, 1500, 3000, 5000]
content = [0, 500, 1500, 3000]
combined = [500, 2000, 4500, 8000]

x = np.arange(len(months))
w = 0.25

bars1 = ax.bar(x - w, cpa_solo, w, label='Solo CPA Clients', color=BLUE, alpha=0.85)
bars2 = ax.bar(x, content, w, label='Car Content', color=ORANGE, alpha=0.85)
bars3 = ax.bar(x + w, combined, w, label='Combined', color=GOLD, alpha=0.85)

ax.set_ylabel('Monthly Side Income ($)', fontweight='bold', fontsize=13)
ax.set_title('Potential Side Income Ramp — Conservative Estimates', fontweight='bold', fontsize=15, color=DARK)
ax.set_xticks(x)
ax.set_xticklabels(months)
ax.legend(fontsize=11)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f'${x:,.0f}'))

for bar in bars3:
    ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 150, f'${bar.get_height():,}', ha='center', fontsize=10, fontweight='bold', color='#8B7225')

fig.tight_layout()
fig.savefig(f'{OUT}-income.png', dpi=150, bbox_inches='tight')
plt.close()

# --- Chart 3: What Others Built (Real Results) ---
fig, ax = plt.subplots(figsize=(10, 6))
ax.axis('off')

data = [
    ['Oliver Henry', 'Content Agent', 'Millions of TikTok views', '1 week'],
    ['@sentientt_media', 'One-Person Biz', '$100K/year revenue', 'Solo'],
    ['Vadim Strizheus', '9 AI Employees', 'Full business automation', '7 days'],
    ['@0x_Discover', 'Trading Bot', '$50 → $2,980', '48 hours'],
    ['@witcheer', 'Overnight Coder', 'Auto-builds projects at 2 AM', 'Ongoing'],
    ['Deacon Ridley', 'Full System', 'Email, CRM, presentations, content', '12 hours'],
]

table = ax.table(cellText=data, colLabels=['Who', 'What They Built', 'Result', 'Timeline'], loc='center', cellLoc='center')
table.auto_set_font_size(False)
table.set_fontsize(12)
table.scale(1.1, 2.0)

for (row, col), cell in table.get_celld().items():
    if row == 0:
        cell.set_facecolor(DARK)
        cell.set_text_props(color='white', fontweight='bold')
    elif row % 2 == 0:
        cell.set_facecolor('#f8f8f8')
    if col == 2 and row > 0:
        cell.set_text_props(fontweight='bold', color=DARK)
    cell.set_edgecolor('#dddddd')

ax.set_title('Real People. Real Results. This Month.', fontweight='bold', fontsize=16, color=DARK, pad=20)
fig.tight_layout()
fig.savefig(f'{OUT}-results.png', dpi=150, bbox_inches='tight')
plt.close()

# --- Chart 4: Cost of Freedom ---
fig, ax = plt.subplots(figsize=(10, 5))

categories = ['OpenClaw\n(Your Agent)', 'Netflix +\nSpotify', 'Single Night\nOut', 'One Tank\nof Gas', 'Flight School\nApplication']
costs = [30, 33, 60, 55, 150]
colors = [GOLD, '#cccccc', '#cccccc', '#cccccc', '#cccccc']

bars = ax.bar(categories, costs, color=colors, width=0.6, edgecolor='white', linewidth=1.5)
bars[0].set_edgecolor(GOLD)
bars[0].set_linewidth(3)

ax.set_ylabel('Monthly Cost ($)', fontweight='bold', fontsize=13)
ax.set_title('$30/Month in Perspective', fontweight='bold', fontsize=15, color=DARK)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

for bar, cost in zip(bars, costs):
    ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 2, f'${cost}', ha='center', fontweight='bold', fontsize=13, color=DARK)

fig.tight_layout()
fig.savefig(f'{OUT}-cost-perspective.png', dpi=150, bbox_inches='tight')
plt.close()

print("Jake charts generated!")
