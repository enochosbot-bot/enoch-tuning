(function render() {
  const data = window.DASHBOARD_DATA;
  const grid = document.getElementById('grid');
  const meta = document.getElementById('meta');

  if (!data?.agents?.length) {
    meta.textContent = 'No data found. Run: node scripts/dashboard/refresh-data.mjs';
    return;
  }

  const fmt = (iso) => iso ? new Date(iso).toLocaleString() : 'No signal';
  meta.textContent = `Read at startup from backlog.md, in-flight.md, and session logs • Updated ${fmt(data.generatedAt)}`;

  grid.innerHTML = data.agents.map((a) => `
    <article class="card" style="border-color:${a.color}66">
      <span class="badge" style="background:${a.color}22;color:${a.color}">${a.emoji} ${a.name}</span>
      <h2 class="name">${a.name}</h2>
      <p class="cls">${a.className}</p>
      <div class="stat"><span>Tasks Completed</span><b>${a.tasksCompleted}</b></div>
      <div class="stat"><span>Messages (24h)</span><b>${a.messages24h}</b></div>
      <div class="stat"><span>Last Active</span><b>${fmt(a.lastActive)}</b></div>
      <p class="footer">RPG class card • BL-014</p>
    </article>
  `).join('');
})();
