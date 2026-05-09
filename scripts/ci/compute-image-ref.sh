#!/usr/bin/env bash
# Print the canonical lowercase GHCR image reference (without tag).
#
# Inputs (env):
#   OWNER  GitHub repo owner / org (e.g., MasarCorp)
#   NAME   Short image name (e.g., magales-api)
#
# Output (GITHUB_OUTPUT):
#   image=ghcr.io/<owner-lowercased>/<name>
#
# Why this exists:
#   GHCR rejects mixed-case org names. github.repository_owner can be
#   mixed-case (e.g., "MasarCorp"), so we lowercase it before composing
#   the image reference.
set -euo pipefail

: "${OWNER:?OWNER is required}"
: "${NAME:?NAME is required}"

owner_lc="$(printf '%s' "$OWNER" | tr '[:upper:]' '[:lower:]')"
image="ghcr.io/${owner_lc}/${NAME}"

echo "image=${image}" >> "${GITHUB_OUTPUT:-/dev/stdout}"
echo "Resolved image reference: ${image}"
