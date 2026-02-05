# 🦊 Cody Foxy

**AI-Powered Code Security Scanner**

Find vulnerabilities before they find you. Cody Foxy scans your code for security issues and uses AI to explain vulnerabilities and suggest fixes.

![Cody Foxy](https://img.shields.io/badge/Security-Scanner-orange?style=for-the-badge&logo=shield)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python)
![Next.js](https://img.shields.io/badge/Next.js-14-black?style=for-the-badge&logo=next.js)

## ✨ Features

- 🔍 **Multi-Language Support** - Python, JavaScript, TypeScript, Go, Java, Ruby, PHP, and more
- 🤖 **AI-Powered Analysis** - Get intelligent explanations and remediation from GPT-4 or Claude
- 🐙 **GitHub Integration** - Connect repos and scan directly from GitHub
- ⚡ **Real-time Scanning** - Watch vulnerabilities appear with WebSocket updates
- 📊 **SARIF Output** - Industry-standard format for CI/CD integration
- 🛡️ **OWASP & CWE Mapping** - Full compliance mapping for prioritization
- 🎨 **Beautiful UI** - Modern, responsive dark/light mode interface

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
docker-compose up -d

# Access the app
open http://localhost:3000
```

### Manual Installation

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install semgrep bandit

# Run
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## 🔧 Configuration

Create a `.env` file:

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/codyfoxy

# AI Providers (at least one required for AI analysis)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
AI_PROVIDER=openai  # or anthropic

# GitHub OAuth (optional, for GitHub integration)
GITHUB_CLIENT_ID=...
GITHUB_CLIENT_SECRET=...
GITHUB_REDIRECT_URI=http://localhost:3000/auth/github/callback

# Security
SECRET_KEY=your-secret-key-here
```

## 🔌 CI/CD Integration

### GitHub Actions

Add to your workflow:

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
          enable_ai: true
          fail_on: critical  # critical, high, medium, low
```

### GitLab CI

```yaml
security-scan:
  image: python:3.11
  script:
    - pip install semgrep bandit
    - semgrep scan --config p/security-audit --sarif -o results.sarif .
  artifacts:
    reports:
      sast: results.sarif
```

## 📖 API Reference

### Scan Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/scans/upload` | Upload code archive for scanning |
| POST | `/api/scans/github` | Scan a GitHub repository |
| GET | `/api/scans/{id}` | Get scan details |
| GET | `/api/scans/{id}/findings` | Get scan findings |
| GET | `/api/scans/{id}/sarif` | Download SARIF report |

### Example Request

```bash
curl -X POST http://localhost:8000/api/scans/github \
  -H "Content-Type: application/json" \
  -d '{"repo_url": "https://github.com/owner/repo", "branch": "main"}'
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (Next.js 14)                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Upload  │  │  GitHub  │  │ Results  │  │Dashboard │   │
│  │  Scanner │  │  Scanner │  │  Viewer  │  │  Charts  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────┬───────────────────────────────┘
                              │ WebSocket / REST API
┌─────────────────────────────▼───────────────────────────────┐
│                      Backend (FastAPI)                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Scanner  │  │    AI    │  │  GitHub  │  │  SARIF   │   │
│  │ Service  │  │ Analyzer │  │ Service  │  │Generator │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────┬───────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────┐
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                   │
│  │ Semgrep  │  │  Bandit  │  │ Custom   │  Scanning Tools   │
│  │          │  │          │  │  Rules   │                   │
│  └──────────┘  └──────────┘  └──────────┘                   │
└─────────────────────────────────────────────────────────────┘
```

## 🛠️ Tech Stack

- **Frontend**: Next.js 14, React 18, Tailwind CSS, shadcn/ui, Framer Motion
- **Backend**: FastAPI, SQLAlchemy, Pydantic
- **Scanning**: Semgrep, Bandit, custom rules
- **AI**: OpenAI GPT-4, Anthropic Claude
- **Database**: PostgreSQL
- **Caching**: Redis
- **Deployment**: Docker, Docker Compose

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Semgrep](https://semgrep.dev/) for the amazing scanning engine
- [OWASP](https://owasp.org/) for security standards and guidelines
- [shadcn/ui](https://ui.shadcn.com/) for beautiful UI components

---

Made with ❤️ by [Tuğcan Topaloğlu](https://github.com/tugcantopaloglu)
