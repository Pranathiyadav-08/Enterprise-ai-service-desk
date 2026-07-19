# API Reference

Base URL for local development: `http://localhost:8000`

The interactive OpenAPI interface is available at `/docs` after starting the backend.

## GET `/`

Returns a basic API status message.

### Response: `200 OK`

```json
{
  "message": "Enterprise AI Service Desk API is running"
}
```

## GET `/health`

Returns the service health status. The browser interface uses this endpoint to detect backend availability.

### Response: `200 OK`

```json
{
  "status": "healthy"
}
```

## POST `/chat`

Classifies an employee query, retrieves knowledge-base context when appropriate, and generates a response.

### Request body

```json
{
  "message": "How do I reset my VPN password?"
}
```

### Response: `200 OK`

```json
{
  "status": "success",
  "intent": "IT_SUPPORT",
  "assigned_agent": "IT Agent",
  "response": "..."
}
```

### Errors

If routing, retrieval, or generation fails, the endpoint returns `500 Internal Server Error` with a `detail` field.

## POST `/upload`

Uploads a PDF to the knowledge base and indexes it.

### Request

Send `multipart/form-data` with a required `file` field containing a `.pdf` file.

### Response: `200 OK`

```json
{
  "status": "success",
  "message": "Document uploaded successfully",
  "filename": "employee-handbook.pdf"
}
```

### Errors

- `400 Bad Request` if the file is not a PDF.
- `500 Internal Server Error` if saving or indexing fails.

## GET `/documents`

Lists PDF files in the knowledge base.

### Response: `200 OK`

```json
{
  "documents": [
    "employee-handbook.pdf",
    "it-support-guide.pdf"
  ]
}
```

## DELETE `/documents/{filename}`

Deletes a PDF document and rebuilds the vector index from remaining PDFs.

### Example

```text
DELETE /documents/employee-handbook.pdf
```

### Response: `200 OK`

```json
{
  "status": "success",
  "message": "Document deleted"
}
```

### Errors

- `400 Bad Request` if `filename` does not end in `.pdf`.
- `404 Not Found` if the document does not exist.
- `500 Internal Server Error` if deletion or rebuilding the index fails.

## POST `/reindex`

Rebuilds the FAISS index from all PDF files currently in `docs/`.

### Response: `200 OK`

```json
{
  "status": "success",
  "documents_indexed": 2
}
```

### Errors

- `400 Bad Request` when no PDF documents are available.
- `500 Internal Server Error` when indexing fails.
