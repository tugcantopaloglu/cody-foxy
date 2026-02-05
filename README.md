# 🦊 Cody Foxy

**Enterprise-Grade AI-Powered Code Security Scanner**

Find vulnerabilities before they find you. Cody Foxy scans your code for security issues and uses AI to explain vulnerabilities and suggest fixes.

![Cody Foxy](https://img.shields.io/badge/Security-Scanner-orange?style=for-the-badge&logo=shield)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python)
![Next.js](https://img.shields.io/badge/Next.js-14-black?style=for-the-badge&logo=next.js)
![TypeScript](https://img.shields.io/badge/TypeScript-5.3-blue?style=for-the-badge&logo=typescript)

## ✨ Features

### 🔍 Multi-Language Support
- **Python** - Semgrep + Bandit
- **JavaScript/TypeScript** - Semgrep with JS/TS rulesets
- **Go** - Semgrep Go security rules
- **Java** - Semgrep Java security rules
- **Ruby** - Semgrep Ruby security rules
- **PHP** - Semgrep PHP security rules
- **C/C++** - Semgrep C/C++ rules
- **Custom Rules** - Support for custom YAML rule definitions

### 🤖 AI-Powered Analysis
- **GPT-4 & Claude Integration** - Choose your preferred AI provider
- **Intelligent Explanations** - Understand vulnerabilities in plain English
- **Remediation Suggestions** - Get specific code fixes
- **Risk Prioritization** - AI-assisted severity assessment

### 🐙 GitHub Integration
- **OAuth Authentication** - Secure repo access
- **PR Scanning** - Automatic scans on pull requests
- **Status Checks** - Block merges on security issues
- **GitHub App** - Full GitHub App support
- **Webhooks** - Real-time push and PR events

### ⚡ Performance
- **Parallel Scanning** - Multi-threaded file analysis
- **Incremental Scans** - Only scan changed files
- **Result Caching** - Redis-backed caching
- **Scan Queue** - Managed concurrent scans

### 🛡️ Security & Compliance
- **SARIF Output** - Industry-standard format
- **OWASP Mapping** - OWASP Top 10 compliance
- **CWE IDs** - Common Weakness Enumeration
- **Rate Limiting** - API and scan rate limits

### 👥 Enterprise Features
- **Projects** - Organize scans by project
- **Teams** - Collaborate with team members
- **Scheduled Scans** - Cron-based automation
- **Audit Logs** - Track all activities

## 📸 Screenshots

<details>
<summary>Dashboard</summary>

The dashboard provides an overview of your security posture:
- Total scans and vulnerabilities
- Severity breakdown charts
- Recent scan history
- Quick actions

</details>

<details>
<summary>Scan Results</summary>

Detailed scan results with:
- Code diff viewer with syntax highlighting
- Vulnerability explanations
- AI-powered fix suggestions
- OWASP/CWE mapping

</details>

<details>
<summary>Projects</summary>

Project management features:
- GitHub repository integration
- Automated scan triggers
- Team collaboration
- Scan history

</details>

## 🚀 Quick Start

### Using Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/tugcantopaloglu/cody-foxy.git
cd cody-foxy

# Set environment variables
cp .env.example .env
# Edit .env with your API keys

# Start with Docker Compose
docker compose up -d

# Access the app
open http://localhost:3000
```

### Manual Installation

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install semgrep bandit

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/codyfoxy

# Redis (for caching and rate limiting)
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY=your-super-secret-key-change-in-production

# AI Providers (at least one required for AI analysis)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
AI_PROVIDER=openai  # or anthropic
AI_MODEL=gpt-4-turbo-preview  # or claude-3-sonnet-20240229

# GitHub OAuth (optional, for GitHub integration)
GITHUB_CLIENT_ID=...
GITHUB_CLIENT_SECRET=...
GITHUB_REDIRECT_URI=http://localhost:3000/auth/github/callback

# GitHub App (optional, for PR scanning)
GITHUB_APP_ID=...
GITHUB_APP_PRIVATE_KEY=...
GITHUB_WEBHOOK_SECRET=...

# Performance
MAX_CONCURRENT_SCANS=5
SCAN_TIMEOUT=300
MAX_FILE_SIZE=52428800  # 50MB
```

## 📖 API Reference

See [API Documentation](docs/api.md) for complete API reference.

### Quick Examples

**Upload Scan:**
```bash
curl -X POST http://localhost:8000/api/scans/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@code.zip" \
  -F "enable_ai=true"
```

**GitHub Scan:**
```bash
curl -X POST http://localhost:8000/api/scans/github \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"repo_url": "https://github.com/owner/repo", "branch": "main"}'
```

**Get Findings:**
```bash
curl http://localhost:8000/api/scans/1/findings \
  -H "Authorization: Bearer $TOKEN"
```

## 🔌 CI/CD Integration

### GitHub Actions

```yaml
name: Security Scan

on: [push, pull_request]

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Run Cody Foxy Scan
        uses: tugcantopaloglu/cody-foxy-action@v1
        with:
          api_url: ${{ secrets.CODY_FOXY_URL }}
          api_token: ${{ secrets.CODY_FOXY_TOKEN }}
          enable_ai: true
          fail_on: high  # critical, high, medium, low
```

### GitLab CI

```yaml
security-scan:
  stage: test
  image: python:3.11
  script:
    - pip install semgrep bandit
    - semgrep scan --config p/security-audit --config p/secrets --sarif -o results.sarif .
  artifacts:
    reports:
      sast: results.sarif
```

### Jenkins

```groovy
pipeline {
    agent any
    stages {
        stage('Security Scan') {
            steps {
                sh 'curl -X POST $CODY_FOXY_URL/api/scans/github -H "Authorization: Bearer $TOKEN" -d "{\"repo_url\": \"${GIT_URL}\"}"'
            }
        }
    }
}
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      Frontend (Next.js 14)                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │Dashboard │  │ Projects │  │  Scans   │  │  Teams   │        │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘        │
└─────────────────────────────┬───────────────────────────────────┘
                              │ WebSocket / REST API
┌─────────────────────────────▼───────────────────────────────────┐
│                      Backend (FastAPI)                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Rate Limiter │  │  Scan Queue  │  │    Cache     │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Scanner    │  │  AI Analyzer │  │ GitHub App   │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────┬───────────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────────┐
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │ Semgrep  │  │  Bandit  │  │  Custom  │  │  Redis   │        │
│  │          │  │          │  │  Rules   │  │  Cache   │        │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘        │
└─────────────────────────────────────────────────────────────────┘
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest --cov=app --cov-report=html
```

### Frontend Tests
```bash
cd frontend
npm run test           # Unit tests
npm run test:coverage  # With coverage
npm run test:e2e       # Playwright E2E tests
```

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | Next.js 14, React 18, TypeScript, Tailwind CSS, shadcn/ui |
| **Backend** | FastAPI, SQLAlchemy 2.0, Pydantic 2.0 |
| **Scanning** | Semgrep, Bandit, Custom Rules |
| **AI** | OpenAI GPT-4, Anthropic Claude |
| **Database** | PostgreSQL 16 |
| **Caching** | Redis 7 |
| **Deployment** | Docker, Docker Compose |

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Run tests (`pytest` and `npm test`)
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Semgrep](https://semgrep.dev/) - Amazing open-source SAST
- [OWASP](https://owasp.org/) - Security standards and guidelines
- [shadcn/ui](https://ui.shadcn.com/) - Beautiful UI components
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework

---

Made with ❤️ by [Tuğcan Topaloğlu](https://github.com/tugcantopaloglu)
