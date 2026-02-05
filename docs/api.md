# 🦊 Cody Foxy API Documentation

## Base URL

```
http://localhost:8000/api
```

## Authentication

Cody Foxy uses JWT Bearer tokens for authentication.

### Get Token

```http
POST /api/auth/token
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=yourpassword
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Using the Token

Include the token in all authenticated requests:

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## Scans API

### Upload Scan

Upload a code archive for scanning.

```http
POST /api/scans/upload
Authorization: Bearer {token}
Content-Type: multipart/form-data

file: (binary) - zip or tar.gz archive
enable_ai: true (optional, default: true)
```

**Response:**
```json
{
  "id": 1,
  "status": "pending",
  "source_type": "upload",
  "source_path": "my-code.zip",
  "created_at": "2024-01-15T10:30:00Z"
}
```

### GitHub Scan

Scan a GitHub repository.

```http
POST /api/scans/github
Authorization: Bearer {token}
Content-Type: application/json

{
  "repo_url": "https://github.com/owner/repo",
  "branch": "main",
  "enable_ai": true
}
```

**Response:**
```json
{
  "id": 2,
  "status": "pending",
  "source_type": "github",
  "source_path": "https://github.com/owner/repo",
  "branch": "main",
  "created_at": "2024-01-15T10:30:00Z"
}
```

### Get Scan

Get scan details by ID.

```http
GET /api/scans/{scan_id}
Authorization: Bearer {token}
```

**Response:**
```json
{
  "id": 1,
  "status": "completed",
  "source_type": "upload",
  "source_path": "my-code.zip",
  "languages_detected": ["python", "javascript"],
  "total_files": 42,
  "files_scanned": 42,
  "total_findings": 15,
  "critical_count": 2,
  "high_count": 5,
  "medium_count": 6,
  "low_count": 2,
  "started_at": "2024-01-15T10:30:05Z",
  "completed_at": "2024-01-15T10:31:30Z",
  "created_at": "2024-01-15T10:30:00Z"
}
```

### Get Findings

Get all findings for a scan.

```http
GET /api/scans/{scan_id}/findings
Authorization: Bearer {token}
```

**Query Parameters:**
- `severity` (optional): Filter by severity (critical, high, medium, low)

**Response:**
```json
[
  {
    "id": 1,
    "scan_id": 1,
    "rule_id": "python.lang.security.audit.eval-injection",
    "rule_name": "Eval Injection",
    "severity": "critical",
    "file_path": "app/utils.py",
    "start_line": 42,
    "end_line": 42,
    "start_col": 4,
    "end_col": 25,
    "code_snippet": "result = eval(user_input)",
    "message": "Avoid using eval() with untrusted input",
    "ai_explanation": "This vulnerability allows...",
    "ai_remediation": "Replace eval() with ast.literal_eval()...",
    "cwe_ids": ["CWE-94"],
    "owasp_ids": ["A03:2021"],
    "references": ["https://cwe.mitre.org/data/definitions/94.html"],
    "is_false_positive": false,
    "created_at": "2024-01-15T10:31:00Z"
  }
]
```

### Get SARIF Report

Download SARIF format report.

```http
GET /api/scans/{scan_id}/sarif
Authorization: Bearer {token}
```

**Response:**
```json
{
  "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
  "version": "2.1.0",
  "runs": [...]
}
```

### List Scans

Get all scans for the authenticated user.

```http
GET /api/scans
Authorization: Bearer {token}
```

**Query Parameters:**
- `limit` (optional, default: 20): Number of results
- `offset` (optional, default: 0): Pagination offset

**Response:**
```json
[
  {
    "id": 1,
    "status": "completed",
    "source_type": "upload",
    "total_findings": 15,
    "created_at": "2024-01-15T10:30:00Z"
  }
]
```

---

## Projects API

### Create Project

```http
POST /api/projects/projects
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "My Project",
  "description": "Project description",
  "team_id": null,
  "repository_id": null,
  "default_branch": "main",
  "scan_on_push": true,
  "scan_on_pr": true,
  "fail_threshold": "high"
}
```

**Response:**
```json
{
  "id": 1,
  "name": "My Project",
  "slug": "my-project",
  "description": "Project description",
  "team_id": null,
  "owner_id": 1,
  "default_branch": "main",
  "scan_on_push": true,
  "scan_on_pr": true,
  "fail_threshold": "high",
  "created_at": "2024-01-15T10:30:00Z"
}
```

### List Projects

```http
GET /api/projects/projects
Authorization: Bearer {token}
```

**Query Parameters:**
- `team_id` (optional): Filter by team

### Get Project

```http
GET /api/projects/projects/{project_id}
Authorization: Bearer {token}
```

### Get Project Stats

```http
GET /api/projects/projects/{project_id}/stats
Authorization: Bearer {token}
```

**Response:**
```json
{
  "total_scans": 25,
  "total_findings": 150,
  "critical_count": 5,
  "high_count": 20,
  "trend": "improving"
}
```

### Update Project

```http
PUT /api/projects/projects/{project_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "Updated Name",
  "scan_on_push": false
}
```

### Delete Project

```http
DELETE /api/projects/projects/{project_id}
Authorization: Bearer {token}
```

---

## Teams API

### Create Team

```http
POST /api/projects/teams
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "Security Team",
  "description": "Our security scanning team"
}
```

### List Teams

```http
GET /api/projects/teams
Authorization: Bearer {token}
```

### Add Team Member

```http
POST /api/projects/teams/{team_id}/members
Authorization: Bearer {token}
Content-Type: application/json

{
  "user_email": "member@example.com",
  "role": "member"
}
```

---

## GitHub Webhook

### Webhook Endpoint

```http
POST /api/github/webhook
X-GitHub-Event: {event_type}
X-Hub-Signature-256: sha256={signature}

{webhook_payload}
```

**Supported Events:**
- `ping` - Webhook verification
- `push` - Code push events
- `pull_request` - PR events (opened, synchronize, reopened)
- `check_suite` - Check suite requests

---

## WebSocket

### Connect

```javascript
const ws = new WebSocket('ws://localhost:8000/api/ws/scans')

ws.onmessage = (event) => {
  const data = JSON.parse(event.data)
  console.log(data)
}
```

### Event Types

**scan_started:**
```json
{
  "type": "scan_started",
  "scan_id": 1
}
```

**scan_progress:**
```json
{
  "type": "scan_progress",
  "scan_id": 1,
  "progress": 50,
  "current_file": "app/main.py"
}
```

**scan_completed:**
```json
{
  "type": "scan_completed",
  "scan_id": 1,
  "status": "completed",
  "total_findings": 15
}
```

---

## Rate Limits

| Endpoint | Limit | Window |
|----------|-------|--------|
| Upload Scan | 10 requests | 1 hour |
| GitHub Scan | 20 requests | 1 hour |
| AI Analysis | 50 requests | 1 hour |
| General API | 100 requests | 1 minute |

**Rate Limit Headers:**
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1705315860
Retry-After: 60
```

---

## Error Responses

**400 Bad Request:**
```json
{
  "detail": "Only zip/tar.gz files supported"
}
```

**401 Unauthorized:**
```json
{
  "detail": "Invalid token"
}
```

**404 Not Found:**
```json
{
  "detail": "Scan not found"
}
```

**429 Too Many Requests:**
```json
{
  "detail": "Rate limit exceeded. Retry after 60 seconds."
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Internal server error"
}
```

---

## SDKs

### Python

```python
import httpx

class CodyFoxyClient:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {token}"}
    
    async def scan_github(self, repo_url: str, branch: str = "main"):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/scans/github",
                headers=self.headers,
                json={"repo_url": repo_url, "branch": branch}
            )
            return response.json()
```

### TypeScript

```typescript
class CodyFoxyClient {
  constructor(private baseUrl: string, private token: string) {}

  async scanGitHub(repoUrl: string, branch = "main") {
    const response = await fetch(`${this.baseUrl}/api/scans/github`, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${this.token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ repo_url: repoUrl, branch }),
    });
    return response.json();
  }
}
```
