// chat-widget.js — Ridley Research AI Chat Widget
(function () {
  'use strict';

  // ── CSS ──────────────────────────────────────────────────────────────────
  var css = `
    #rr-cw-btn {
      position: fixed; bottom: 24px; right: 24px; z-index: 9999;
      width: 56px; height: 56px; border-radius: 50%;
      background: #7aa2ff; border: none; cursor: pointer;
      display: flex; align-items: center; justify-content: center;
      box-shadow: 0 4px 22px rgba(122,162,255,.5);
      transition: transform .15s, box-shadow .15s;
    }
    #rr-cw-btn:hover { transform: scale(1.07); box-shadow: 0 6px 28px rgba(122,162,255,.65); }
    #rr-cw-panel {
      position: fixed; bottom: 90px; right: 24px; z-index: 9998;
      width: 340px; height: 500px;
      background: #0f1628; border: 1px solid #25315f;
      border-radius: 20px; box-shadow: 0 14px 52px rgba(0,0,0,.75);
      display: none; flex-direction: column; overflow: hidden;
      font-family: Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    #rr-cw-panel.rr-open { display: flex; }
    #rr-cw-head {
      padding: 14px 16px; background: #141d3b;
      border-bottom: 1px solid #25315f;
      display: flex; align-items: center; justify-content: space-between;
      flex-shrink: 0;
    }
    .rr-head-left { display: flex; align-items: center; gap: 10px; }
    .rr-avatar {
      width: 34px; height: 34px; border-radius: 50%;
      background: #7aa2ff; display: flex; align-items: center;
      justify-content: center; font-size: 15px; font-weight: 700; color: #0d1530;
      flex-shrink: 0;
    }
    .rr-name { font-size: 14px; font-weight: 600; color: #e8ecff; line-height: 1.2; }
    .rr-status { font-size: 11px; color: #4ade80; }
    #rr-cw-close {
      background: none; border: none; color: #a9b4da;
      cursor: pointer; font-size: 24px; line-height: 1; padding: 0; margin: 0;
    }
    #rr-cw-msgs {
      flex: 1; overflow-y: auto; padding: 14px 14px 8px;
      display: flex; flex-direction: column; gap: 10px;
      scroll-behavior: smooth;
    }
    #rr-cw-msgs::-webkit-scrollbar { width: 4px; }
    #rr-cw-msgs::-webkit-scrollbar-thumb { background: #25315f; border-radius: 2px; }
    .rr-msg { max-width: 84%; display: flex; flex-direction: column; }
    .rr-msg.rr-user { align-self: flex-end; align-items: flex-end; }
    .rr-msg.rr-bot  { align-self: flex-start; align-items: flex-start; }
    .rr-bubble {
      padding: 10px 13px; font-size: 13.5px; line-height: 1.5; color: #e8ecff;
    }
    .rr-msg.rr-user .rr-bubble {
      background: #7aa2ff; color: #0d1530;
      border-radius: 16px 16px 4px 16px; font-weight: 500;
    }
    .rr-msg.rr-bot .rr-bubble {
      background: #1a2540;
      border-radius: 16px 16px 16px 4px;
    }
    #rr-typing {
      align-self: flex-start;
    }
    .rr-dots {
      background: #1a2540; border-radius: 16px 16px 16px 4px;
      padding: 12px 14px; display: flex; gap: 4px; align-items: center;
    }
    .rr-dot {
      width: 6px; height: 6px; border-radius: 50%;
      background: #a9b4da; animation: rr-pulse 1.2s infinite;
    }
    .rr-dot:nth-child(2) { animation-delay: .2s; }
    .rr-dot:nth-child(3) { animation-delay: .4s; }
    @keyframes rr-pulse { 0%,80%,100%{opacity:.2} 40%{opacity:1} }
    #rr-cw-footer {
      padding: 10px 12px; border-top: 1px solid #25315f;
      display: flex; gap: 8px; align-items: flex-end;
      flex-shrink: 0; background: #0f1628;
    }
    #rr-cw-input {
      flex: 1; background: #1a2540; border: 1px solid #25315f;
      border-radius: 14px; padding: 9px 13px;
      font-size: 13.5px; color: #e8ecff; outline: none;
      resize: none; font-family: inherit; line-height: 1.4;
      max-height: 90px; min-height: 38px;
    }
    #rr-cw-input::placeholder { color: #4a5878; }
    #rr-cw-input:focus { border-color: #7aa2ff; }
    #rr-cw-send {
      width: 38px; height: 38px; border-radius: 50%;
      background: #7aa2ff; border: none; cursor: pointer;
      display: flex; align-items: center; justify-content: center;
      flex-shrink: 0; transition: opacity .15s;
    }
    #rr-cw-send:hover { opacity: .85; }
    #rr-cw-send:disabled { opacity: .35; cursor: default; }
  `;

  var styleEl = document.createElement('style');
  styleEl.textContent = css;
  document.head.appendChild(styleEl);

  // ── HTML ─────────────────────────────────────────────────────────────────
  var wrap = document.createElement('div');
  wrap.innerHTML = `
    <button id="rr-cw-btn" aria-label="Chat with RR.AI">
      <svg width="26" height="26" viewBox="0 0 24 24" fill="#0d1530" xmlns="http://www.w3.org/2000/svg">
        <path d="M20 2H4C2.9 2 2 2.9 2 4v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z"/>
      </svg>
    </button>
    <div id="rr-cw-panel" role="dialog" aria-label="Chat with RR.AI">
      <div id="rr-cw-head">
        <div class="rr-head-left">
          <div class="rr-avatar">R</div>
          <div>
            <div class="rr-name">RR.AI</div>
            <div class="rr-status">● Online</div>
          </div>
        </div>
        <button id="rr-cw-close" aria-label="Close">×</button>
      </div>
      <div id="rr-cw-msgs"></div>
      <div id="rr-cw-footer">
        <textarea id="rr-cw-input" rows="1" placeholder="Ask me anything…"></textarea>
        <button id="rr-cw-send" aria-label="Send">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="#0d1530" xmlns="http://www.w3.org/2000/svg">
            <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
          </svg>
        </button>
      </div>
    </div>
  `;
  document.body.appendChild(wrap);

  // ── Refs ─────────────────────────────────────────────────────────────────
  var btn     = document.getElementById('rr-cw-btn');
  var panel   = document.getElementById('rr-cw-panel');
  var closeEl = document.getElementById('rr-cw-close');
  var msgsEl  = document.getElementById('rr-cw-msgs');
  var input   = document.getElementById('rr-cw-input');
  var sendBtn = document.getElementById('rr-cw-send');

  var history = [];
  var isOpen  = false;
  var greeted = false;

  // ── Open / close ─────────────────────────────────────────────────────────
  function openChat() {
    isOpen = true;
    panel.classList.add('rr-open');
    if (!greeted) {
      greeted = true;
      setTimeout(function () {
        addBot("Hey! I'm RR.AI — the AI assistant for Ridley Research. What's going on in your business? Whether you have a specific problem or just want to understand what AI can actually do for you, I'm happy to dig in.");
      }, 350);
    }
    setTimeout(function () { input.focus(); }, 120);
  }

  function closeChat() {
    isOpen = false;
    panel.classList.remove('rr-open');
  }

  btn.addEventListener('click', function (e) {
    e.stopPropagation();
    isOpen ? closeChat() : openChat();
  });

  closeEl.addEventListener('click', function (e) {
    e.stopPropagation();
    closeChat();
  });

  document.addEventListener('click', function (e) {
    if (isOpen && !panel.contains(e.target) && e.target !== btn) closeChat();
  });

  // ── Message helpers ───────────────────────────────────────────────────────
  function addMsg(role, text) {
    var div    = document.createElement('div');
    div.className = 'rr-msg ' + role;
    var bubble = document.createElement('div');
    bubble.className = 'rr-bubble';
    bubble.textContent = text;
    div.appendChild(bubble);
    msgsEl.appendChild(div);
    msgsEl.scrollTop = msgsEl.scrollHeight;
  }

  function addBot(text) {
    history.push({ role: 'assistant', content: text });
    addMsg('rr-bot', text);
  }

  function showTyping() {
    var div = document.createElement('div');
    div.id = 'rr-typing';
    div.className = 'rr-msg rr-bot';
    div.innerHTML = '<div class="rr-dots"><span class="rr-dot"></span><span class="rr-dot"></span><span class="rr-dot"></span></div>';
    msgsEl.appendChild(div);
    msgsEl.scrollTop = msgsEl.scrollHeight;
  }

  function hideTyping() {
    var el = document.getElementById('rr-typing');
    if (el) el.remove();
  }

  // ── Send ─────────────────────────────────────────────────────────────────
  function send() {
    var text = input.value.trim();
    if (!text || sendBtn.disabled) return;

    addMsg('rr-user', text);
    history.push({ role: 'user', content: text });
    input.value = '';
    input.style.height = 'auto';
    sendBtn.disabled = true;
    showTyping();

    fetch('/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ messages: history }),
    })
      .then(function (r) { return r.json(); })
      .then(function (d) {
        hideTyping();
        addBot(d.reply || "Hmm, something went quiet on my end — try again?");
        sendBtn.disabled = false;
        input.focus();
      })
      .catch(function () {
        hideTyping();
        addBot("Having trouble connecting right now. You can reach the team directly at hello@ridleyresearch.com.");
        sendBtn.disabled = false;
      });
  }

  sendBtn.addEventListener('click', send);

  input.addEventListener('keydown', function (e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  });

  input.addEventListener('input', function () {
    this.style.height = 'auto';
    this.style.height = Math.min(this.scrollHeight, 90) + 'px';
  });

})();
