#!/usr/bin/env python3
"""Generate charts for Jacob & Todd Allen's OpenClaw guide."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

OUT = "/Users/deaconsopenclaw/.openclaw/workspace/tmp/charts-jacob"

GOLD = '#D4A843'
DARK = '#1a1a2e'
RED = '#e94560'
GREEN = '#2ecc71'
BLUE = '#3498db'

plt.rcParams['font.family'] = 'Helvetica'
plt.rcParams['font.size'] = 12

# --- Chart 1: Weekly Time Savings ---
fig, ax = plt.subplots(figsize=(10, 6))
tasks = ['Email\nMgmt', 'Deal\nResearch', 'CRM\nEntry', 'Funding\nCoord', 'Tenant\nScreening', 'Content\nConsumption']
before = [4, 10, 2.5, 3.5, 1.5, 4.5]
after = [0.7, 0, 0, 1.25, 0.25, 0.5]

x = np.arange(len(tasks))
w = 0.35
bars1 = ax.bar(x - w/2, before, w, label='Before OpenClaw', color=RED, alpha=0.85)
bars2 = ax.bar(x + w/2, after, w, label='After OpenClaw', color=GOLD, alpha=0.85)

ax.set_ylabel('Hours per Week', fontweight='bold', fontsize=13)
ax.set_title('Weekly Time Savings — Jacob Allen', fontweight='bold', fontsize=15, color=DARK)
ax.set_xticks(x)
ax.set_xticklabels(tasks, fontsize=10)
ax.legend(fontsize=12)
ax.set_ylim(0, 13)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

for bar in bars1:
    ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.2, f'{bar.get_height():.1f}h', ha='center', fontsize=9, fontweight='bold', color=RED)
for bar in bars2:
    if bar.get_height() > 0:
        ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.2, f'{bar.get_height():.1f}h', ha='center', fontsize=9, fontweight='bold', color='#8B7225')

fig.tight_layout()
fig.savefig(f'{OUT}-time-savings.png', dpi=150, bbox_inches='tight')
plt.close()

# --- Chart 2: Deal Pipeline Funnel ---
fig, ax = plt.subplots(figsize=(10, 6))
stages = ['Leads\nScraped', 'Researched\n& Qualified', 'Contacted', 'Offers\nMade', 'Under\nContract', 'Closed']
counts = [200, 80, 50, 20, 8, 5]
colors_grad = ['#e94560', '#d45070', '#c45b80', '#b46690', '#9477a0', GOLD]

bars = ax.bar(stages, counts, color=colors_grad, width=0.7, edgecolor='white', linewidth=1.5)

ax.set_ylabel('Deals per Month', fontweight='bold', fontsize=13)
ax.set_title('Automated Deal Pipeline — Monthly Flow', fontweight='bold', fontsize=15, color=DARK)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

for bar, count in zip(bars, counts):
    ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 3, str(count), ha='center', fontweight='bold', fontsize=13, color=DARK)

# Add conversion rates
for i in range(len(counts)-1):
    rate = counts[i+1]/counts[i]*100
    mid_x = (i + i+1) / 2
    mid_y = (counts[i] + counts[i+1]) / 2
    ax.annotate(f'{rate:.0f}%', xy=(mid_x + 0.5, mid_y), fontsize=9, color=DARK, alpha=0.6, ha='center')

fig.tight_layout()
fig.savefig(f'{OUT}-deal-pipeline.png', dpi=150, bbox_inches='tight')
plt.close()

# --- Chart 3: Cost Comparison - CRM ---
fig, ax = plt.subplots(figsize=(10, 5))
solutions = ['OpenClaw\nCustom CRM', 'Salesforce', 'Podio', 'REI BlackBook', 'PropertyRadar']
annual = [360, 1800, 948, 1188, 1188]
colors = [GOLD, RED, RED, RED, RED]

bars = ax.barh(solutions, annual, color=colors, alpha=0.85, height=0.6)
bars[0].set_edgecolor(GOLD)
bars[0].set_linewidth(2)

ax.set_xlabel('Annual Cost ($)', fontweight='bold', fontsize=13)
ax.set_title('Annual CRM Cost Comparison — Real Estate', fontweight='bold', fontsize=15, color=DARK)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.invert_yaxis()

for bar, cost in zip(bars, annual):
    ax.text(bar.get_width() + 30, bar.get_y() + bar.get_height()/2., f'${cost:,}/yr', va='center', fontweight='bold', fontsize=12)

fig.tight_layout()
fig.savefig(f'{OUT}-crm-cost.png', dpi=150, bbox_inches='tight')
plt.close()

# --- Chart 4: Where Your Time Goes (Before vs After pie) ---
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Before
labels1 = ['Admin &\nData Entry', 'Deal\nResearch', 'Email &\nScheduling', 'Actual\nDeal Work', 'Family &\nFaith']
sizes1 = [20, 25, 15, 25, 15]
colors1 = [RED, '#d45070', '#c45b80', GOLD, GREEN]
explode1 = (0.05, 0.05, 0.05, 0, 0)

ax1.pie(sizes1, labels=labels1, autopct='%1.0f%%', colors=colors1, explode=explode1,
        textprops={'fontsize': 11}, pctdistance=0.75, startangle=90)
ax1.set_title('BEFORE OpenClaw', fontweight='bold', fontsize=14, color=RED)

# After
labels2 = ['Admin\n(Automated)', 'Deal Work\n& Calls', 'Strategy &\nGrowth', 'Family &\nFaith', 'Real Estate\nExpansion']
sizes2 = [5, 30, 20, 30, 15]
colors2 = ['#cccccc', GOLD, BLUE, GREEN, '#27ae60']
explode2 = (0, 0, 0, 0.05, 0)

ax2.pie(sizes2, labels=labels2, autopct='%1.0f%%', colors=colors2, explode=explode2,
        textprops={'fontsize': 11}, pctdistance=0.75, startangle=90)
ax2.set_title('AFTER OpenClaw', fontweight='bold', fontsize=14, color=GOLD)

fig.suptitle('Where Your Time Goes — Weekly Breakdown', fontweight='bold', fontsize=16, color=DARK, y=1.02)
fig.tight_layout()
fig.savefig(f'{OUT}-time-allocation.png', dpi=150, bbox_inches='tight')
plt.close()

# --- Chart 5: ROI Summary Table ---
fig, ax = plt.subplots(figsize=(8, 5))
ax.axis('off')

data = [
    ['Annual Cost', '$360'],
    ['Hours Saved/Week', '26+'],
    ['Annual Hours Saved', '1,352+'],
    ['Productivity Value', '$50,000+'],
    ['Deals Found (Automated)', '200+/month'],
    ['CRM Savings', '$600-1,400/yr'],
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

ax.set_title('ROI Summary — Jacob Allen / Blessed Abodes', fontweight='bold', fontsize=16, color=DARK, pad=20)
fig.tight_layout()
fig.savefig(f'{OUT}-roi-summary.png', dpi=150, bbox_inches='tight')
plt.close()

print("Jacob charts generated!")
