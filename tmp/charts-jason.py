#!/usr/bin/env python3
"""Generate charts for Jason Brownstein's OpenClaw guide."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

OUT = "/Users/deaconsopenclaw/.openclaw/workspace/tmp/charts-jason"

# Color palette
GOLD = '#D4A843'
DARK = '#1a1a2e'
RED = '#e94560'
GRAY = '#4a4a6a'
LIGHT = '#f0f0f0'

plt.rcParams['font.family'] = 'Helvetica'
plt.rcParams['font.size'] = 12

# --- Chart 1: Weekly Time Savings ---
fig, ax = plt.subplots(figsize=(10, 6))
tasks = ['Prospect\nResearch', 'Email\nManagement', 'CRM Data\nEntry', 'Follow-up\nEmails', 'Meeting\nScheduling']
before = [6, 4, 3.5, 2, 1.5]
after = [0, 0.7, 0, 0.4, 0.15]

x = np.arange(len(tasks))
w = 0.35
bars1 = ax.bar(x - w/2, before, w, label='Before OpenClaw', color=RED, alpha=0.85)
bars2 = ax.bar(x + w/2, after, w, label='After OpenClaw', color=GOLD, alpha=0.85)

ax.set_ylabel('Hours per Week', fontweight='bold', fontsize=13)
ax.set_title('Weekly Time Savings — Jason Brownstein', fontweight='bold', fontsize=15, color=DARK)
ax.set_xticks(x)
ax.set_xticklabels(tasks, fontsize=11)
ax.legend(fontsize=12)
ax.set_ylim(0, 8)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Add value labels
for bar in bars1:
    ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.15, f'{bar.get_height():.1f}h', ha='center', fontsize=10, fontweight='bold', color=RED)
for bar in bars2:
    if bar.get_height() > 0:
        ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.15, f'{bar.get_height():.1f}h', ha='center', fontsize=10, fontweight='bold', color='#8B7225')

fig.tight_layout()
fig.savefig(f'{OUT}-time-savings.png', dpi=150, bbox_inches='tight')
plt.close()

# --- Chart 2: Cost Comparison ---
fig, ax = plt.subplots(figsize=(10, 5))
solutions = ['OpenClaw', 'Salesforce', 'Redtail CRM', 'Wealthbox', 'ChatGPT Team']
monthly = [30, 150, 99, 59, 25]
colors = [GOLD, RED, RED, RED, RED]
alphas = [1.0, 0.7, 0.7, 0.7, 0.7]

bars = ax.barh(solutions, monthly, color=colors, alpha=0.85, height=0.6)
bars[0].set_edgecolor(GOLD)
bars[0].set_linewidth(2)

ax.set_xlabel('Monthly Cost ($)', fontweight='bold', fontsize=13)
ax.set_title('Monthly Cost Comparison', fontweight='bold', fontsize=15, color=DARK)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.invert_yaxis()

for bar, cost in zip(bars, monthly):
    ax.text(bar.get_width() + 3, bar.get_y() + bar.get_height()/2., f'${cost}/mo', va='center', fontweight='bold', fontsize=12)

fig.tight_layout()
fig.savefig(f'{OUT}-cost-comparison.png', dpi=150, bbox_inches='tight')
plt.close()

# --- Chart 3: Revenue Impact Projection ---
fig, ax = plt.subplots(figsize=(10, 6))
months = ['Month 1', 'Month 2', 'Month 3', 'Month 6', 'Month 12']
without = [12000, 24000, 36000, 72000, 144000]
with_ai = [13200, 28800, 46800, 108000, 234000]

ax.plot(months, without, 'o-', color=RED, linewidth=2.5, markersize=8, label='Without OpenClaw (5% close rate)')
ax.plot(months, with_ai, 'o-', color=GOLD, linewidth=2.5, markersize=8, label='With OpenClaw (7% close rate)')
ax.fill_between(range(len(months)), without, with_ai, alpha=0.15, color=GOLD)

ax.set_ylabel('Cumulative New Revenue ($)', fontweight='bold', fontsize=13)
ax.set_title('Projected Revenue Impact — 200 Calls/Week', fontweight='bold', fontsize=15, color=DARK)
ax.legend(fontsize=11)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f'${x:,.0f}'))

# Annotate the gap at month 12
ax.annotate(f'+${with_ai[-1]-without[-1]:,.0f}/yr', xy=(4, (with_ai[-1]+without[-1])/2),
            fontsize=14, fontweight='bold', color=GOLD, ha='center',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor=GOLD))

fig.tight_layout()
fig.savefig(f'{OUT}-revenue-impact.png', dpi=150, bbox_inches='tight')
plt.close()

# --- Chart 4: ROI Summary ---
fig, ax = plt.subplots(figsize=(8, 5))
ax.axis('off')

data = [
    ['Annual Cost', '$360'],
    ['Hours Saved/Week', '17+'],
    ['Annual Hours Saved', '884+'],
    ['Productivity Value', '$39,000-52,000'],
    ['Revenue Uplift (est.)', '$90,000+'],
    ['ROI', '100-140x'],
]

table = ax.table(cellText=data, colLabels=['Metric', 'Value'], loc='center', cellLoc='center')
table.auto_set_font_size(False)
table.set_fontsize(14)
table.scale(1.2, 2.0)

for (row, col), cell in table.get_celld().items():
    if row == 0:
        cell.set_facecolor(DARK)
        cell.set_text_props(color='white', fontweight='bold')
    elif row % 2 == 0:
        cell.set_facecolor('#f8f8f8')
    if col == 1 and row > 0:
        cell.set_text_props(fontweight='bold', color=DARK)
    cell.set_edgecolor('#dddddd')

ax.set_title('ROI Summary — Jason Brownstein', fontweight='bold', fontsize=16, color=DARK, pad=20)
fig.tight_layout()
fig.savefig(f'{OUT}-roi-summary.png', dpi=150, bbox_inches='tight')
plt.close()

print("Jason charts generated!")
