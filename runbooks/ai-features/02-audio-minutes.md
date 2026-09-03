# Audio → Minutes (Whisper, Phase 4)

Transcribe a meeting recording with Whisper (faster-whisper, CPU/int8), then draft and save
minutes from it.

- ai-services: `POST /v1/transcribe` (lazy-loads the model `WHISPER_MODEL`, default `base`; cached in the `aimodelcache` volume under `HF_HOME=/models/hf`).
- The transcript feeds the existing AI Minutes flow (agent drafts → `save_minutes` → `POST /api/minutes`).

## 1. Prepare a test audio

On macOS you can synthesize one (Arabic voice if installed, else any voice):

```bash
say -o /tmp/test.aiff "This is a test of the board meeting minutes transcription."
# or Arabic: say -v Maged -o /tmp/test.aiff "هذا اختبار لتفريغ محضر اجتماع المجلس"
```

Any `.wav`/`.mp3`/`.m4a`/`.aiff` works.

## 2. Transcribe

```bash
curl -sS -X POST http://localhost:8081/v1/transcribe -H 'X-Tenant-Slug: acme' -F "file=@/tmp/test.aiff"
```

**Expected:** JSON `{ "language": "...", "duration": <sec>, "text": "<transcript>", "filename": "test.aiff" }`.
First call downloads the model (~140 MB for `base`) into the cache volume — subsequent calls are fast.

## 3. Draft + save minutes from the transcript (UI)

- Open a meeting (DRAFT status to allow agenda edits), click **✦ Draft minutes**, or paste the transcript
  into the AI Assist panel and ask: "draft the minutes from this transcript".
- Review, then say "save it" → a Minutes draft is created (`POST /api/minutes`), visible under المحاضر.

## Notes
- Model size via `WHISPER_MODEL` (`tiny`/`base`/`small`/`medium`/`large-v3`). `base` is the dev default.
- The model loads lazily, so ai-services starts fine even before the first transcription.
