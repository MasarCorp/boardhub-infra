#!/usr/bin/env bash
# curl for ai-services, which refuses unsigned requests. Reads AI_SERVICE_HMAC_SECRET from the
# environment or .env, and takes the tenant from AI_TENANT (default acme).
# Usage: scripts/ai-curl.sh METHOD /v1/path [extra curl args]
set -euo pipefail

method="$1"; path="$2"; shift 2
secret="${AI_SERVICE_HMAC_SECRET:-}"
if [ -z "$secret" ] && [ -f "$(dirname "$0")/../.env" ]; then
  secret="$(sed -n 's/^AI_SERVICE_HMAC_SECRET=//p' "$(dirname "$0")/../.env" | tail -1)"
fi
secret="${secret:-dev-ai-hmac-secret-change-me-32-chars-min}"
tenant="${AI_TENANT:-acme}"
ts="$(date +%s)"
sig="$(printf '%s' "$ts.$method.$path.$tenant" | openssl dgst -sha256 -hmac "$secret" -r | cut -d' ' -f1)"

exec curl -sS -X "$method" "${AI_BASE_URL:-http://localhost:8081}$path" \
  -H "X-Tenant-Slug: $tenant" -H "X-AI-Timestamp: $ts" -H "X-AI-Signature: $sig" "$@"
