# Storage + Document Vectorization

Document files are stored in MinIO (S3-compatible) and their content is indexed into RAG so
the AI Assistant can answer from the actual file, not just metadata.

- Backend: `MinIO StorageService`, `POST /api/documents/upload`, `GET /api/documents/{id}/content`.
- ai-services: the Magales pull downloads each document's content and `extract_text` (PDF/text) → index.

## 1. Upload a document file

```bash
# any local PDF or text file
echo "Board Risk Policy 2026: single-counterparty exposure capped at 8% of capital." > /tmp/policy.txt

curl -sS -X POST http://localhost:8080/api/documents/upload \
  -H 'X-Tenant-Slug: acme' \
  -F "file=@/tmp/policy.txt" \
  -F "title=Risk Policy 2026" -F "sourceType=BOARD"
```

**Expected:** HTTP 201 with a JSON `DocumentResponse` containing an `id`, `fileName`,
`filePath` like `00000001-…/documents/<uuid>/policy.txt`, and `fileSizeBytes`.

Confirm the object exists in MinIO console (http://localhost:9001) under bucket `magales-docs`.

## 2. Download it back

```bash
DOC_ID=<id from step 1>
curl -sS -D - -o /tmp/out.txt "http://localhost:8080/api/documents/$DOC_ID/content" -H 'X-Tenant-Slug: acme'
cat /tmp/out.txt
```

**Expected:** HTTP 200, `Content-Disposition: attachment; filename="policy.txt"`, body identical
to the uploaded file.

## 3. Vectorize document content into RAG

```bash
curl -sS -X POST http://localhost:8081/v1/rag/ingest/magales -H 'X-Tenant-Slug: acme'
```

**Expected:** JSON with `documents` and `chunks_indexed` > 0, `errors: {}`. Documents with a stored
file are indexed by **content**; metadata-only docs fall back to title/description/tags.

## 4. Ask the assistant about the file content

```bash
curl -sS -X POST http://localhost:8080/api/ai/assist/agent -H 'X-Tenant-Slug: acme' \
  -H 'Content-Type: application/json' \
  -d '{"query":"What single-counterparty exposure cap does the risk policy set?"}'
```

**Expected:** the answer cites the uploaded document and states **8% of capital**.

## Notes
- Bucket name comes from `S3_BUCKET` (default `magales-docs`); MinIO creds from `S3_ACCESS_KEY`/`S3_SECRET_KEY`.
- `GET /documents/{id}/content` returns 404 for legacy `pending-upload/...` rows (no stored bytes).
