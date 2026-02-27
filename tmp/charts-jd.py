import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# Color palette - warm, professional
GOLD = '#D4A843'
STONE = '#8B8680'
CRIMSON = '#8B2500'
DARK = '#2C2C2C'
WARM_BG = '#1A1A1A'
CREAM = '#F5F0E8'
SAGE = '#6B8E6B'

plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['text.color'] = CREAM
plt.rcParams['axes.labelcolor'] = CREAM
plt.rcParams['xtick.color'] = CREAM
plt.rcParams['ytick.color'] = CREAM

# Chart 1: Day Shift - Before vs After
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
fig.patch.set_facecolor(WARM_BG)
for ax in [ax1, ax2]:
    ax.set_facecolor(WARM_BG)

# Before
categories = ['News &\nMarkets', 'Email', 'Spreadsheets', 'Calendar\nCoord', 'Meeting\nPrep', 'Free Time']
before_hrs = [1.5, 0.75, 0.5, 0.33, 0.5, 4.42]
colors_before = [CRIMSON]*5 + [STONE]
ax1.barh(categories, before_hrs, color=colors_before, height=0.6)
ax1.set_title('Before: Your Day (hours)', fontsize=14, fontweight='bold', color=GOLD)
ax1.set_xlim(0, 5)
ax1.invert_yaxis()
for i, v in enumerate(before_hrs):
    ax1.text(v + 0.1, i, f'{v:.1f}h', va='center', fontsize=11, color=CREAM)

# After
after_hrs = [0.17, 0.17, 0, 0, 0.08, 7.58]
colors_after = [SAGE]*5 + [GOLD]
ax2.barh(categories, after_hrs, color=colors_after, height=0.6)
ax2.set_title('After: Your Day (hours)', fontsize=14, fontweight='bold', color=GOLD)
ax2.set_xlim(0, 8.5)
ax2.invert_yaxis()
for i, v in enumerate(after_hrs):
    label = f'{v:.1f}h' if v > 0 else 'Auto'
    ax2.text(max(v, 0.1) + 0.1, i, label, va='center', fontsize=11, color=CREAM)

plt.tight_layout()
plt.savefig('tmp/charts-jd-day-shift.png', dpi=150, bbox_inches='tight', facecolor=WARM_BG)
plt.close()

# Chart 2: Time Reclaimed Over Years
fig, ax = plt.subplots(figsize=(10, 5))
fig.patch.set_facecolor(WARM_BG)
ax.set_facecolor(WARM_BG)

years = [1, 2, 3, 4, 5]
hours = [18*52, 18*52*2, 18*52*3, 18*52*4, 18*52*5]
days = [h/8 for h in hours]

bars = ax.bar(years, hours, color=GOLD, width=0.6, alpha=0.9)
ax.set_xlabel('Years', fontsize=12)
ax.set_ylabel('Hours Reclaimed', fontsize=12)
ax.set_title('Time Back — The Compound Effect', fontsize=16, fontweight='bold', color=GOLD)

for bar, d in zip(bars, days):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 50,
            f'{int(d)} days', ha='center', fontsize=11, color=CREAM, fontweight='bold')

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_color(STONE)
ax.spines['bottom'].set_color(STONE)

plt.tight_layout()
plt.savefig('tmp/charts-jd-time-reclaimed.png', dpi=150, bbox_inches='tight', facecolor=WARM_BG)
plt.close()

# Chart 3: Cost comparison
fig, ax = plt.subplots(figsize=(8, 4))
fig.patch.set_facecolor(WARM_BG)
ax.set_facecolor(WARM_BG)

items = ['Netflix', 'Spotify', 'AI Agent\n(Full-time assistant)', 'Human\nAssistant']
costs = [15, 11, 30, 4000]
colors = [STONE, STONE, GOLD, CRIMSON]

bars = ax.barh(items, costs, color=colors, height=0.5)
ax.set_title('Monthly Cost Comparison', fontsize=14, fontweight='bold', color=GOLD)
ax.set_xlabel('$/month', fontsize=11)
ax.invert_yaxis()

for i, (bar, v) in enumerate(zip(bars, costs)):
    ax.text(v + 50, i, f'${v}/mo', va='center', fontsize=11, color=CREAM)

ax.set_xlim(0, 5000)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_color(STONE)
ax.spines['bottom'].set_color(STONE)

plt.tight_layout()
plt.savefig('tmp/charts-jd-overview.png', dpi=150, bbox_inches='tight', facecolor=WARM_BG)
plt.close()

print("All charts generated.")
