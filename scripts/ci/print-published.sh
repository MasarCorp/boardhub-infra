#!/usr/bin/env bash
# Print a human-readable summary of what the docker-publish workflow
# just did. On a pull_request event the image is built but not pushed;
# we still print the planned tags for visibility.
#
# Inputs (env):
#   EVENT   github.event_name
#   IMAGE   ghcr.io/<owner>/<name>
#   DIGEST  sha256:... (from build-push-action; empty if not built)
#   TAGS    newline-separated list of image refs (from metadata-action)
set -euo pipefail

: "${EVENT:?EVENT is required}"
: "${IMAGE:?IMAGE is required}"

action_word="published"
if [[ "${EVENT}" == "pull_request" ]]; then
  action_word="built (NOT pushed; pull_request event)"
fi

{
  echo "## Docker image ${action_word}"
  echo ""
  echo "**Image:** \`${IMAGE}\`"
  if [[ -n "${DIGEST:-}" ]]; then
    echo "**Digest:** \`${DIGEST}\`"
  fi
  echo ""
  echo "**Tags:**"
  echo ""
  echo '```'
  echo "${TAGS:-<none>}"
  echo '```'
} | tee -a "${GITHUB_STEP_SUMMARY:-/dev/stdout}"
