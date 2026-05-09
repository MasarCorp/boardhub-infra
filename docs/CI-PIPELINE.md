# CI pipeline blueprint

A reusable GitHub Actions workflow that builds a Docker image and publishes it to **GitHub Container Registry (`ghcr.io`)**. Designed to be wired into any repo with a `Dockerfile` — current ones (`Magales`, `Magales-ui`) and any future ones — by adding ~15 lines of caller YAML.

The reusable workflow lives at:

```
MasarCorp/magales-infra/.github/workflows/docker-publish.yml
```

It is **not** executed against `magales-infra` itself (no `on: push` etc.) — only invoked by callers via `workflow_call`.

---

## What it does

1. Checks out the caller repo and `magales-infra` (for shared helper scripts in `.ci-infra/`).
2. Logs into `ghcr.io` using the workflow's `GITHUB_TOKEN` (skipped on `pull_request` since we don't push).
3. Computes a lowercased image reference (`ghcr.io/<owner>/<image-name>`).
4. Generates tags via [`docker/metadata-action`](https://github.com/docker/metadata-action) — see [Tag strategy](#tag-strategy).
5. Builds with Buildx and pushes (push is conditional on event type).
6. Writes a markdown summary to the job: image, digest, tags.

---

## Tag strategy

| Trigger | Push? | Tags applied |
|---|---|---|
| `pull_request` | **no** (build only) | `pr-<N>` (artifact only, not pushed) |
| `push` to default branch (`main`) | yes | `latest`, `sha-<short>`, `main` |
| `push` to other branch | yes | `<branch>`, `sha-<short>` |
| `release` with tag `v1.2.3` | yes | `1.2.3`, `1.2`, `1`, `latest`, `sha-<short>` |

Implementation: `type=ref,event=branch`, `type=ref,event=pr`, `type=sha,format=short,prefix=sha-`, `type=semver,pattern={{version}}|{{major}}.{{minor}}|{{major}}`, `type=raw,value=latest,enable={{is_default_branch}}`.

---

## How to wire it into a new repo

### 1. Create the caller workflow

`.github/workflows/build-and-publish.yml`:

```yaml
name: build-and-publish

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]
  release:
    types: [published]

permissions:
  contents: read
  packages: write

jobs:
  publish:
    uses: MasarCorp/magales-infra/.github/workflows/docker-publish.yml@main
    with:
      image-name: <your-image-name>     # e.g., magales-api
      # dockerfile: Dockerfile          # optional, default "Dockerfile"
      # context: .                      # optional, default "."
      # platforms: linux/amd64          # optional, default "linux/amd64"
    secrets: inherit
```

### 2. (Optional) Add a smoke-test job that consumes the published image

```yaml
  smoke-test:
    needs: publish
    if: github.event_name != 'pull_request'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: chmod +x scripts/ci/*.sh
      - name: Verify image
        env:
          IMAGE: ${{ needs.publish.outputs.image }}
          DIGEST: ${{ needs.publish.outputs.digest }}
        run: scripts/ci/verify-image.sh
```

`scripts/ci/verify-image.sh` lives in the caller repo and is repo-specific (e.g., the API smoke-tests `/api/actuator/health`, the UI smoke-tests `/`).

---

## Inputs reference

| Input | Required | Default | Purpose |
|---|---|---|---|
| `image-name` | yes | — | Short name appended to `ghcr.io/<owner>/`. Must be lowercase. |
| `dockerfile` | no | `Dockerfile` | Path to Dockerfile. |
| `context` | no | `.` | Build context. |
| `platforms` | no | `linux/amd64` | buildx `--platform`. Add `,linux/arm64` for multi-arch. |
| `runs-on` | no | `ubuntu-latest` | Runner label override. |

## Outputs

| Output | Meaning |
|---|---|
| `image` | `ghcr.io/<owner>/<image-name>` (no tag) |
| `digest` | `sha256:...` of the built image |
| `tags` | Newline-separated list of tags applied |

---

## Permissions and visibility

The reusable workflow declares `packages: write` and uses `GITHUB_TOKEN`. **The caller workflow must also set `permissions:` block** (shown above), otherwise `GITHUB_TOKEN` is read-only.

By default, packages published to GHCR inherit the visibility of the source repo. To make a package public after the first push:

1. Go to `https://github.com/orgs/MasarCorp/packages/container/<image-name>`
2. Package settings → Change visibility → Public

For private packages, downstream consumers need a PAT with `read:packages` scope.

---

## Why scripts, not inline `run:` blocks?

The reusable workflow delegates anything more than one-liner glue to scripts in `magales-infra/scripts/ci/`:

| Script | Purpose |
|---|---|
| `compute-image-ref.sh` | Lowercases `github.repository_owner` and emits `image=...` to `GITHUB_OUTPUT`. |
| `print-published.sh` | Renders the job-summary markdown. |

This keeps the YAML small and lets us shellcheck the logic. The workflow runs `chmod +x .ci-infra/scripts/ci/*.sh` before invoking them so the executable bit doesn't have to round-trip through git on every clone.

---

## Local-dev impact

None. This pipeline is GitHub-side only. Local dev still uses `docker compose -f docker-compose.dev.yml up -d --build` per [WORKFLOWS.md](../WORKFLOWS.md). Once a tagged image is in GHCR, `WORKFLOWS.md`'s **Registry flow** section describes how to consume it from `docker-compose.dev.yml`.
