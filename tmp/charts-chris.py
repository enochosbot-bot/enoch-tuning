#!/usr/bin/env python3
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

OUT = "/Users/deaconsopenclaw/.openclaw/workspace/tmp/charts-chris"
GOLD = '#D4A843'
DARK = '#1a1a2e'
RED = '#e94560'
GREEN = '#2ecc71'
BLUE = '#3498db'
plt.rcParams['font.family'] = 'Helvetica'
plt.rcParams['font.size'] = 12

# --- Chart 1: Time Savings ---
fig, ax = plt.subplots(figsize=(10, 6))
tasks = ['Contact\nEntry', 'Follow-up\nEmails', 'Event/Area\nResearch', 'Email\nMgmt', 'CRM\nEntry', 'Market\nResearch']
before = [6.5, 8.5, 5, 4, 3.5, 2.5]
after = [0, 1.3, 0, 0.7, 0, 0]
x = np.arange(len(tasks))
w = 0.35
bars1 = ax.bar(x - w/2, before, w, label='Before OpenClaw', color=RED, alpha=0.85)
bars2 = ax.bar(x + w/2, after, w, label='After OpenClaw', color=GOLD, alpha=0.85)
ax.set_ylabel('Hours per Week', fontweight='bold', fontsize=13)
ax.set_title('Weekly Time Savings — Chris Rivera', fontweight='bold', fontsize=15, color=DARK)
ax.set_xticks(x)
ax.set_xticklabels(tasks, fontsize=10)
ax.legend(fontsize=12)
ax.set_ylim(0, 11)
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

# --- Chart 2: Follow-up Conversion Funnel ---
fig, ax = plt.subplots(figsize=(10, 6))
stages = ['People Met\nat Events', 'Contacts\nLogged', 'Follow-ups\nSent', 'Meetings\nBooked', 'Proposals\nDelivered', 'Clients\nWon']
without_ai = [50, 30, 15, 5, 3, 1]
with_ai = [50, 50, 50, 18, 10, 4]
x = np.arange(len(stages))
w = 0.35
bars1 = ax.bar(x - w/2, without_ai, w, label='Manual Follow-up', color=RED, alpha=0.7)
bars2 = ax.bar(x + w/2, with_ai, w, label='AI-Powered Follow-up', color=GOLD, alpha=0.85)
ax.set_ylabel('Count per Month', fontweight='bold', fontsize=13)
ax.set_title('The Follow-Up Gap — Where Clients Are Lost vs Won', fontweight='bold', fontsize=15, color=DARK)
ax.set_xticks(x)
ax.set_xticklabels(stages, fontsize=10)
ax.legend(fontsize=11)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
for bar in bars1:
    ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.8, str(int(bar.get_height())), ha='center', fontsize=10, fontweight='bold', color=RED)
for bar in bars2:
    ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.8, str(int(bar.get_height())), ha='center', fontsize=10, fontweight='bold', color='#8B7225')
fig.tight_layout()
fig.savefig(f'{OUT}-funnel.png', dpi=150, bbox_inches='tight')
plt.close()

# --- Chart 3: Revenue Impact ---
fig, ax = plt.subplots(figsize=(10, 6))
months = ['Month 1', 'Month 3', 'Month 6', 'Month 12']
without = [5000, 15000, 30000, 60000]
with_ai = [20000, 60000, 140000, 300000]
ax.plot(months, without, 'o-', color=RED, linewidth=2.5, markersize=8, label='Manual Prospecting (1 client/mo)')
ax.plot(months, with_ai, 'o-', color=GOLD, linewidth=2.5, markersize=8, label='AI-Powered (4 clients/mo)')
ax.fill_between(range(len(months)), without, with_ai, alpha=0.12, color=GOLD)
ax.set_ylabel('Cumulative New Recurring Revenue ($/yr)', fontweight='bold', fontsize=13)
ax.set_title('Revenue Impact — Affluent Client Acquisition', fontweight='bold', fontsize=15, color=DARK)
ax.legend(fontsize=11)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f'${x:,.0f}'))
ax.annotate(f'+$240K/yr', xy=(3, 180000), fontsize=16, fontweight='bold', color=GOLD, ha='center',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='white', edgecolor=GOLD, linewidth=2))
fig.tight_layout()
fig.savefig(f'{OUT}-revenue.png', dpi=150, bbox_inches='tight')
plt.close()

# --- Chart 4: Cost vs CRM alternatives ---
fig, ax = plt.subplots(figsize=(10, 5))
solutions = ['OpenClaw\n+ Custom CRM', 'Salesforce\nFinancial', 'Wealthbox', 'Redtail CRM', 'HubSpot\nPro']
annual = [360, 3600, 708, 1188, 10800]
colors = [GOLD, RED, RED, RED, RED]
bars = ax.barh(solutions, annual, color=colors, alpha=0.85, height=0.6)
bars[0].set_edgecolor(GOLD)
bars[0].set_linewidth(2)
ax.set_xlabel('Annual Cost ($)', fontweight='bold', fontsize=13)
ax.set_title('Annual Cost — CRM + Prospecting Tools', fontweight='bold', fontsize=15, color=DARK)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.invert_yaxis()
for bar, cost in zip(bars, annual):
    ax.text(bar.get_width() + 150, bar.get_y() + bar.get_height()/2., f'${cost:,}/yr', va='center', fontweight='bold', fontsize=12)
fig.tight_layout()
fig.savefig(f'{OUT}-cost.png', dpi=150, bbox_inches='tight')
plt.close()

print("Chris charts generated!")
