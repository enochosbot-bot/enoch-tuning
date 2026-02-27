// functions/chat.js — Ridley Research AI Chat Backend (Cloudflare Pages Function)
// Set OPENAI_API_KEY in Cloudflare Pages → Settings → Environment Variables

const SYSTEM = `You are Riley, a friendly and sharp AI assistant for Ridley Research & Consulting — a firm that builds practical AI systems and workflow automation for businesses.

Your job: have a genuine, helpful conversation, understand the visitor's situation, and naturally guide them toward booking a discovery call with the team.

How to approach it:
1. Be genuinely helpful first. Answer their questions, show you get their situation.
2. As you learn about their needs, connect the dots to how Ridley Research could help.
3. After 2-3 good exchanges, offer to connect them: "Sounds like a solid fit — want me to pass your info to the team? Drop your name and email and they'll reach out within a business day."
4. Once you have name + email, confirm warmly: "Done — the team will reach out to [email] within 1 business day. Keep asking if you have more questions."

Keep responses short: 2-4 sentences. Be real, not salesy. Never be pushy or repetitive.

What Ridley Research does:
- Workflow automation (mapping and automating the repetitive 80%)
- AI agent design (task routing, guardrails, verification)
- Implementation sprints (pilot-to-production, clear outcomes)
- Operational readiness (SOPs, handoff playbooks, scalable deployment)

Target clients: small-to-medium businesses, professional services, teams drowning in manual work.`;

export async function onRequestPost(context) {
  const { request, env } = context;

  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Content-Type': 'application/json',
  };

  try {
    const { messages } = await request.json();

    if (!Array.isArray(messages)) {
      return new Response(JSON.stringify({ error: 'Invalid request.' }), { status: 400, headers });
    }

    const apiKey = env.OPENAI_API_KEY;

    if (!apiKey) {
      console.error('Missing OPENAI_API_KEY in environment variables.');
      return new Response(
        JSON.stringify({
          reply:
            "Thanks for the message — our AI assistant is temporarily offline. If you drop your name and email, the team can follow up within 1 business day.",
        }),
        { headers }
      );
    }

    const res = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: 'gpt-4o-mini',
        messages: [{ role: 'system', content: SYSTEM }, ...messages.slice(-14)],
        max_tokens: 450,
        temperature: 0.72,
      }),
    });

    if (!res.ok) {
      const errorText = await res.text();
      console.error('OpenAI error:', errorText);
      return new Response(
        JSON.stringify({
          reply:
            "Sorry — I’m having trouble reaching the AI service right now. Leave your name and email and our team will reach out within 1 business day.",
        }),
        { headers }
      );
    }

    const data = await res.json();
    const reply = data.choices?.[0]?.message?.content ?? "I'm not sure about that one — try rephrasing?";

    return new Response(JSON.stringify({ reply }), { headers });
  } catch (err) {
    console.error('Worker error:', err);
    return new Response(JSON.stringify({ error: 'Something went wrong.' }), { status: 500, headers });
  }
}

export async function onRequestOptions() {
  return new Response(null, {
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    },
  });
}
