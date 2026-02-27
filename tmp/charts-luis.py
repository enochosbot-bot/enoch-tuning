import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# Style
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['figure.facecolor'] = '#1a1a2e'
plt.rcParams['axes.facecolor'] = '#1a1a2e'
plt.rcParams['text.color'] = '#e0e0e0'
plt.rcParams['axes.labelcolor'] = '#e0e0e0'
plt.rcParams['xtick.color'] = '#e0e0e0'
plt.rcParams['ytick.color'] = '#e0e0e0'

# Chart 1: Weekly Time Savings
fig, ax = plt.subplots(figsize=(10, 5))
tasks = ['Contact\nMgmt', 'Follow-ups', 'Research', 'Event Prep', 'Social\nMedia', 'Email']
before = [5, 7, 5, 3, 5, 5]
after = [0, 0.5, 0, 0.25, 0.5, 1.75]
x = np.arange(len(tasks))
w = 0.35
ax.bar(x - w/2, before, w, label='Before OpenClaw', color='#e94560')
ax.bar(x + w/2, after, w, label='With OpenClaw', color='#0f3460')
ax.set_ylabel('Hours / Week')
ax.set_title('Weekly Time Savings — Luis Canosa', fontsize=14, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(tasks)
ax.legend()
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_color('#333')
ax.spines['bottom'].set_color('#333')
plt.tight_layout()
plt.savefig('tmp/charts-luis-time-savings.png', dpi=150, bbox_inches='tight')
plt.close()

# Chart 2: Cost Comparison
fig, ax = plt.subplots(figsize=(8, 5))
items = ['OpenClaw\n(monthly)', 'Political\nStaffer', 'CRM\nSubscription', 'Oppo Research\nFirm (per project)']
costs = [30, 4000, 350, 5000]
colors = ['#0f3460', '#e94560', '#e94560', '#e94560']
bars = ax.bar(items, costs, color=colors)
ax.set_ylabel('Cost ($)')
ax.set_title('Cost Comparison', fontsize=14, fontweight='bold')
for bar, cost in zip(bars, costs):
    ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 100,
            f'${cost:,}', ha='center', va='bottom', fontweight='bold', color='#e0e0e0')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_color('#333')
ax.spines['bottom'].set_color('#333')
plt.tight_layout()
plt.savefig('tmp/charts-luis-cost.png', dpi=150, bbox_inches='tight')
plt.close()

# Chart 3: Force Multiplier
fig, ax = plt.subplots(figsize=(8, 5))
team_size = [1, 3, 5, 10]
without_ai = [1, 3, 5, 10]
with_ai = [8, 24, 40, 80]
ax.plot(team_size, without_ai, 'o-', color='#e94560', linewidth=2, markersize=8, label='Without AI')
ax.plot(team_size, with_ai, 's-', color='#0f3460', linewidth=2, markersize=8, label='With OpenClaw')
ax.fill_between(team_size, without_ai, with_ai, alpha=0.15, color='#0f3460')
ax.set_xlabel('Actual Team Size')
ax.set_ylabel('Effective Operating Capacity')
ax.set_title('Force Multiplier Effect', fontsize=14, fontweight='bold')
ax.legend()
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_color('#333')
ax.spines['bottom'].set_color('#333')
plt.tight_layout()
plt.savefig('tmp/charts-luis-force.png', dpi=150, bbox_inches='tight')
plt.close()

print("All charts generated.")
