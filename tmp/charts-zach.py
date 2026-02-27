#!/usr/bin/env python3
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

OUT = "/Users/deaconsopenclaw/.openclaw/workspace/tmp/charts-zach"
GOLD = '#D4A843'
DARK = '#1a1a2e'
RED = '#e94560'
GREEN = '#2ecc71'
BLUE = '#3498db'
ORANGE = '#e67e22'
PURPLE = '#9b59b6'
plt.rcParams['font.family'] = 'Helvetica'
plt.rcParams['font.size'] = 12

# --- Chart 1: Drill Business Scaling ---
fig, ax = plt.subplots(figsize=(10, 6))
scenarios = ['Now\n(3-5 schools)', 'Year 1 w/ AI\n(10-15 schools)', 'Year 2 Pipeline\n(20-30 schools)']
low = [6000, 20000, 60000]
high = [25000, 75000, 150000]
x = np.arange(len(scenarios))
w = 0.35
bars1 = ax.bar(x - w/2, low, w, label='Conservative', color=GOLD, alpha=0.7)
bars2 = ax.bar(x + w/2, high, w, label='Optimistic', color=GOLD, alpha=1.0)
ax.set_ylabel('Annual Revenue ($)', fontweight='bold', fontsize=13)
ax.set_title('Drill Business Revenue — Scaling with AI', fontweight='bold', fontsize=15, color=DARK)
ax.set_xticks(x)
ax.set_xticklabels(scenarios, fontsize=11)
ax.legend(fontsize=12)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f'${x:,.0f}'))
for bar in bars1:
    ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 2000, f'${bar.get_height():,.0f}', ha='center', fontsize=9, fontweight='bold', color='#8B7225')
for bar in bars2:
    ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 2000, f'${bar.get_height():,.0f}', ha='center', fontsize=9, fontweight='bold', color=DARK)
fig.tight_layout()
fig.savefig(f'{OUT}-drill-scaling.png', dpi=150, bbox_inches='tight')
plt.close()

# --- Chart 2: Income Streams Combined ---
fig, ax = plt.subplots(figsize=(10, 6))
streams = ['Drill\nWriting', 'Content\nMonetization', 'Personal\nTraining', 'COMBINED']
low_range = [20000, 5000, 15000, 40000]
high_range = [50000, 20000, 30000, 100000]
x = np.arange(len(streams))
w = 0.35
bars1 = ax.bar(x - w/2, low_range, w, label='Conservative', color=BLUE, alpha=0.7)
bars2 = ax.bar(x + w/2, high_range, w, label='Full Potential', color=GOLD, alpha=0.9)
# Highlight combined
bars1[-1].set_color(GREEN)
bars1[-1].set_alpha(0.7)
bars2[-1].set_color(GOLD)
bars2[-1].set_edgecolor(DARK)
bars2[-1].set_linewidth(2)
ax.set_ylabel('Annual Income ($)', fontweight='bold', fontsize=13)
ax.set_title('Multiple Income Streams — The Freedom Stack', fontweight='bold', fontsize=15, color=DARK)
ax.set_xticks(x)
ax.set_xticklabels(streams, fontsize=11)
ax.legend(fontsize=12)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f'${x:,.0f}'))
for bar in bars2:
    ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 1500, f'${bar.get_height():,.0f}', ha='center', fontsize=10, fontweight='bold', color=DARK)
fig.tight_layout()
fig.savefig(f'{OUT}-income-streams.png', dpi=150, bbox_inches='tight')
plt.close()

# --- Chart 3: Before vs After Time Allocation ---
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
labels1 = ['Day Job', 'Drill\nAdmin', 'Drill\nCreative', 'Content', 'Dancing\n& Life']
sizes1 = [45, 20, 15, 5, 15]
colors1 = [RED, '#d45070', GOLD, BLUE, GREEN]
ax1.pie(sizes1, labels=labels1, autopct='%1.0f%%', colors=colors1, textprops={'fontsize': 11}, pctdistance=0.75, startangle=90)
ax1.set_title('NOW', fontweight='bold', fontsize=14, color=RED)

labels2 = ['Day Job\n(temporary)', 'Drill\nCreative', 'Content\nCreation', 'Fitness /\nTraining', 'Dancing\n& Life']
sizes2 = [30, 20, 15, 15, 20]
colors2 = ['#cccccc', GOLD, BLUE, ORANGE, GREEN]
ax2.pie(sizes2, labels=labels2, autopct='%1.0f%%', colors=colors2, textprops={'fontsize': 11}, pctdistance=0.75, startangle=90)
ax2.set_title('WITH AI', fontweight='bold', fontsize=14, color=GOLD)

fig.suptitle('Where Your Time Goes — Before & After', fontweight='bold', fontsize=16, color=DARK, y=1.02)
fig.tight_layout()
fig.savefig(f'{OUT}-time-allocation.png', dpi=150, bbox_inches='tight')
plt.close()

# --- Chart 4: Content Growth Projection ---
fig, ax = plt.subplots(figsize=(10, 6))
months = list(range(1, 13))
followers = [100, 350, 800, 1500, 3000, 5500, 9000, 14000, 21000, 30000, 42000, 58000]
ax.plot(months, followers, 'o-', color=GOLD, linewidth=2.5, markersize=7)
ax.fill_between(months, followers, alpha=0.15, color=GOLD)
ax.set_xlabel('Month', fontweight='bold', fontsize=13)
ax.set_ylabel('Total Followers (All Platforms)', fontweight='bold', fontsize=13)
ax.set_title('Content Growth — Consistent AI-Powered Posting', fontweight='bold', fontsize=15, color=DARK)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f'{x:,.0f}'))
ax.annotate('Monetization\nthreshold', xy=(6, 5500), xytext=(3, 20000),
            arrowprops=dict(arrowstyle='->', color=DARK), fontsize=12, fontweight='bold', color=DARK)
ax.axhline(y=10000, color=GREEN, linestyle='--', alpha=0.5)
ax.text(1, 11000, '10K = Brand deals unlock', fontsize=10, color=GREEN, alpha=0.7)
fig.tight_layout()
fig.savefig(f'{OUT}-content-growth.png', dpi=150, bbox_inches='tight')
plt.close()

print("Zach charts generated!")
