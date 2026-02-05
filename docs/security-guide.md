# 🦊 Cody Foxy Security Scanning Guide

## Table of Contents

1. [Getting Started](#getting-started)
2. [Scanning Methods](#scanning-methods)
3. [Understanding Results](#understanding-results)
4. [Vulnerability Categories](#vulnerability-categories)
5. [Best Practices](#best-practices)
6. [CI/CD Integration](#cicd-integration)
7. [Custom Rules](#custom-rules)

---

## Getting Started

### First Scan

1. **Navigate to the Scan page** (`/scan`)
2. **Choose your method:**
   - Upload a ZIP/TAR.GZ archive
   - Connect a GitHub repository
3. **Wait for results** - Scans typically complete in 1-5 minutes
4. **Review findings** - Prioritize by severity

### Understanding Severity Levels

| Level | Color | Action Required |
|-------|-------|-----------------|
| **Critical** | 🔴 Red | Immediate fix needed |
| **High** | 🟠 Orange | Fix within days |
| **Medium** | 🟡 Yellow | Fix within sprint |
| **Low** | 🔵 Blue | Technical debt |

---

## Scanning Methods

### File Upload

Best for:
- Local projects
- One-time scans
- Projects not on GitHub

**Supported formats:**
- `.zip`
- `.tar.gz`
- `.tgz`

**Size limit:** 50MB

### GitHub Integration

Best for:
- Continuous scanning
- PR checks
- Team collaboration

**Features:**
- OAuth authentication
- Branch selection
- Automatic PR scanning
- Status checks

---

## Understanding Results

### Finding Card

Each finding includes:

```
┌─────────────────────────────────────────────────┐
│ [CRITICAL] Eval Injection                       │
│                                                 │
│ python.lang.security.audit.eval-injection       │
│                                                 │
│ Avoid using eval() with untrusted input         │
│                                                 │
│ 📁 app/utils.py                                 │
│ 📍 Lines 42-42                                  │
│                                                 │
│ [CWE-94] [A03:2021]                            │
└─────────────────────────────────────────────────┘
```

### Code Diff Viewer

The code diff viewer shows:
- **Highlighted lines** - The vulnerable code
- **Line numbers** - Exact location
- **Syntax highlighting** - Language-aware

### AI Analysis

When AI is enabled:

**Explanation:**
> This vulnerability allows attackers to execute arbitrary Python code. 
> The `eval()` function interprets the input as Python code, which means
> malicious users could run commands like `os.system('rm -rf /')`.

**Remediation:**
> Replace `eval()` with `ast.literal_eval()` for parsing literals:
> ```python
> import ast
> result = ast.literal_eval(user_input)
> ```

---

## Vulnerability Categories

### Injection Vulnerabilities

**CWE-78: OS Command Injection**
```python
# Vulnerable
os.system(f"ls {user_input}")

# Fixed
subprocess.run(["ls", user_input], shell=False)
```

**CWE-89: SQL Injection**
```python
# Vulnerable
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")

# Fixed
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
```

**CWE-94: Code Injection**
```python
# Vulnerable
eval(user_input)

# Fixed
import ast
ast.literal_eval(user_input)
```

### Authentication Issues

**CWE-798: Hardcoded Credentials**
```python
# Vulnerable
password = "admin123"

# Fixed
password = os.environ.get("DB_PASSWORD")
```

**CWE-306: Missing Authentication**
```python
# Vulnerable
@app.route("/admin")
def admin_panel():
    return render_template("admin.html")

# Fixed
@app.route("/admin")
@login_required
def admin_panel():
    return render_template("admin.html")
```

### Cryptographic Issues

**CWE-327: Weak Cryptography**
```python
# Vulnerable
hashlib.md5(password.encode())

# Fixed
import bcrypt
bcrypt.hashpw(password.encode(), bcrypt.gensalt())
```

**CWE-330: Insufficient Randomness**
```python
# Vulnerable
import random
token = random.randint(0, 999999)

# Fixed
import secrets
token = secrets.token_urlsafe(32)
```

### Data Exposure

**CWE-200: Information Exposure**
```python
# Vulnerable
except Exception as e:
    return str(e)  # Exposes internal details

# Fixed
except Exception as e:
    logger.error(e)
    return "An error occurred"
```

---

## Best Practices

### 1. Scan Early, Scan Often

- **Development:** Scan before commits
- **PR:** Automatic scans on pull requests
- **Main branch:** Scan after merges
- **Scheduled:** Weekly full scans

### 2. Prioritize by Risk

```
Critical → Block deployment
High     → Fix before release
Medium   → Fix in sprint
Low      → Backlog
```

### 3. Don't Ignore Findings

- **Review each finding** - Understand the risk
- **Mark false positives** - Don't ignore legitimate ones
- **Track progress** - Use the trend indicator

### 4. Enable AI Analysis

AI helps by:
- Explaining complex vulnerabilities
- Providing specific fix suggestions
- Assessing context-aware risk

### 5. Use Project Thresholds

Configure your project to:
- Fail on critical issues
- Block merges on high severity
- Alert on new vulnerabilities

---

## CI/CD Integration

### GitHub Actions

```yaml
name: Security Scan

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Run Cody Foxy
        uses: tugcantopaloglu/cody-foxy-action@v1
        with:
          api_url: ${{ secrets.CODY_FOXY_URL }}
          api_token: ${{ secrets.CODY_FOXY_TOKEN }}
          fail_on: high  # critical, high, medium, low
      
      - name: Upload SARIF
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: cody-foxy-results.sarif
```

### GitLab CI

```yaml
stages:
  - security

security_scan:
  stage: security
  image: python:3.11
  script:
    - pip install semgrep
    - semgrep scan --config p/security-audit --sarif -o results.sarif .
  artifacts:
    reports:
      sast: results.sarif
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
```

### Jenkins

```groovy
pipeline {
    agent any
    
    stages {
        stage('Security Scan') {
            steps {
                script {
                    def response = httpRequest(
                        httpMode: 'POST',
                        url: "${CODY_FOXY_URL}/api/scans/github",
                        customHeaders: [[name: 'Authorization', value: "Bearer ${CODY_FOXY_TOKEN}"]],
                        contentType: 'APPLICATION_JSON',
                        requestBody: """{"repo_url": "${GIT_URL}", "branch": "${GIT_BRANCH}"}"""
                    )
                    def scan = readJSON text: response.content
                    
                    // Poll for completion
                    def status = 'pending'
                    while (status == 'pending' || status == 'running') {
                        sleep(10)
                        def check = httpRequest(
                            url: "${CODY_FOXY_URL}/api/scans/${scan.id}",
                            customHeaders: [[name: 'Authorization', value: "Bearer ${CODY_FOXY_TOKEN}"]]
                        )
                        def result = readJSON text: check.content
                        status = result.status
                    }
                    
                    if (result.critical_count > 0) {
                        error "Critical vulnerabilities found!"
                    }
                }
            }
        }
    }
}
```

---

## Custom Rules

### Creating Custom Rules

Cody Foxy supports custom Semgrep rules. Create YAML files in `backend/app/rules/`:

```yaml
rules:
  - id: my-company-secret-detection
    patterns:
      - pattern: |
          $KEY = "..."
      - metavariable-regex:
          metavariable: $KEY
          regex: (api_key|secret|password)
    message: "Potential hardcoded secret: $KEY"
    languages: [python, javascript]
    severity: ERROR
    metadata:
      cwe: CWE-798
      owasp: A02:2021
      category: security
```

### Rule Structure

| Field | Description |
|-------|-------------|
| `id` | Unique rule identifier |
| `patterns` | Matching patterns |
| `message` | Description shown to users |
| `languages` | Target languages |
| `severity` | ERROR, WARNING, INFO |
| `metadata` | CWE, OWASP, etc. |

### Testing Rules

```bash
semgrep scan --config my-rule.yaml test-code/
```

---

## Frequently Asked Questions

### Why am I getting false positives?

Some common causes:
- Test code detected as vulnerabilities
- Sanitized inputs not recognized
- Third-party library code

**Solution:** Mark as false positive and add context.

### How do I exclude files/directories?

Create `.semgrepignore`:
```
tests/
*_test.py
vendor/
node_modules/
```

### Can I scan private repositories?

Yes! Connect your GitHub account via OAuth to access private repos.

### How accurate is the AI analysis?

AI analysis is approximately 85-90% accurate. Always verify critical findings manually.

### What languages are supported?

- Python (Semgrep + Bandit)
- JavaScript/TypeScript
- Go
- Java
- Ruby
- PHP
- C/C++
- And more via Semgrep

---

## Support

- **Documentation:** [docs/](/)
- **Issues:** [GitHub Issues](https://github.com/tugcantopaloglu/cody-foxy/issues)
- **Email:** support@codyfoxy.dev
