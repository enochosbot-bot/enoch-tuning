// Cloudflare Pages Function — Stripe Checkout
// POST /checkout → creates a Stripe Checkout session, returns redirect URL
// GET  /checkout?session_id=xxx → verify payment (used by success page)

function getSiteOrigin(env) {
  const configured = env.PUBLIC_SITE_ORIGIN || 'https://ridleyresearch.com';
  try {
    return new URL(configured).origin;
  } catch {
    return 'https://ridleyresearch.com';
  }
}

export async function onRequestPost(context) {
  const { env } = context;
  const secretKey = env.STRIPE_SECRET_KEY;

  if (!secretKey) {
    return new Response(JSON.stringify({ error: 'Stripe not configured' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }

  // SECURITY: never trust request headers for redirect URLs.
  const origin = getSiteOrigin(env);

  // Create Stripe Checkout Session
  const params = new URLSearchParams({
    'payment_method_types[]': 'card',
    'line_items[0][price_data][currency]': 'usd',
    'line_items[0][price_data][product_data][name]': 'Build Your Autonomous AI',
    'line_items[0][price_data][product_data][description]': 'Everything I know about building a personal AI operating system — agent setup, memory architecture, cron automation, Telegram integration, and more.',
    'line_items[0][price_data][unit_amount]': '7900',
    'line_items[0][quantity]': '1',
    'mode': 'payment',
    'success_url': `${origin}/success?session_id={CHECKOUT_SESSION_ID}`,
    'cancel_url': `${origin}/#guide`,
    'allow_promotion_codes': 'true',
  });

  const response = await fetch('https://api.stripe.com/v1/checkout/sessions', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${secretKey}`,
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: params.toString(),
  });

  const session = await response.json();

  if (!response.ok) {
    return new Response(JSON.stringify({ error: session.error?.message || 'Stripe error' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }

  return new Response(JSON.stringify({ url: session.url }), {
    status: 200,
    headers: { 'Content-Type': 'application/json' }
  });
}

export async function onRequestGet(context) {
  const { env } = context;
  const url = new URL(context.request.url);
  const sessionId = url.searchParams.get('session_id');

  if (!sessionId) {
    return new Response(JSON.stringify({ error: 'No session ID' }), {
      status: 400,
      headers: { 'Content-Type': 'application/json' }
    });
  }

  const response = await fetch(`https://api.stripe.com/v1/checkout/sessions/${sessionId}`, {
    headers: {
      'Authorization': `Bearer ${env.STRIPE_SECRET_KEY}`,
    }
  });

  const session = await response.json();
  const paid = session.payment_status === 'paid';

  // Only reveal the download URL after confirmed payment
  const downloadUrl = paid
    ? (env.GUIDE_DOWNLOAD_URL || null)
    : null;

  return new Response(JSON.stringify({
    status: session.payment_status,
    email: session.customer_details?.email,
    downloadUrl,
  }), {
    status: 200,
    headers: { 'Content-Type': 'application/json' }
  });
}
