#!/bin/bash
# Image gen via xAI Grok — $0.02/image
# Usage: gen-image-grok.sh --prompt "your prompt" [--model grok-imagine-image-pro]

OUT_DIR="$HOME/.openclaw/workspace/creative-output"
mkdir -p "$OUT_DIR"

PROMPT=""
MODEL="grok-imagine-image"

while [[ $# -gt 0 ]]; do
  case $1 in
    --prompt) PROMPT="$2"; shift 2 ;;
    --model) MODEL="$2"; shift 2 ;;
    --pro) MODEL="grok-imagine-image-pro"; shift ;;
    *) shift ;;
  esac
done

if [ -z "$PROMPT" ]; then
  echo "Usage: gen-image-grok.sh --prompt \"your prompt\" [--pro]"
  exit 1
fi

TIMESTAMP=$(date +%Y%m%d-%H%M%S)
SLUG=$(echo "$PROMPT" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | cut -c1-40)
OUTFILE="$OUT_DIR/${TIMESTAMP}-${SLUG}.png"

RESPONSE=$(curl -s https://api.x.ai/v1/images/generations \
  -H "Authorization: Bearer $XAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"model\":\"$MODEL\",\"prompt\":\"$PROMPT\",\"n\":1,\"response_format\":\"b64_json\"}")

# Extract base64 and decode
echo "$RESPONSE" | python3 -c "
import sys, json, base64
data = json.load(sys.stdin)
if 'data' in data and len(data['data']) > 0:
    b64 = data['data'][0].get('b64_json','')
    if b64:
        sys.stdout.buffer.write(base64.b64decode(b64))
    else:
        # Maybe it returned a URL instead
        url = data['data'][0].get('url','')
        if url:
            print(f'URL: {url}', file=sys.stderr)
            import urllib.request
            urllib.request.urlretrieve(url, '$OUTFILE')
            sys.exit(0)
        print('No image data in response', file=sys.stderr)
        print(json.dumps(data, indent=2), file=sys.stderr)
        sys.exit(1)
else:
    print('Error:', json.dumps(data, indent=2), file=sys.stderr)
    sys.exit(1)
" > "$OUTFILE" 2>/tmp/gen-image-grok-err.log

if [ $? -eq 0 ] && [ -s "$OUTFILE" ]; then
  echo "$OUTFILE"
else
  cat /tmp/gen-image-grok-err.log
  exit 1
fi
