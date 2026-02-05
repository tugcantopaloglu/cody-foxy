import asyncio
from typing import Dict, List, Optional
import httpx
from ..core.config import settings

SYSTEM_PROMPT = """You are Cody Foxy, an expert security analyst specializing in code vulnerability analysis.
When analyzing a security finding, provide:
1. A clear, concise explanation of the vulnerability
2. The potential impact and attack scenarios
3. Specific remediation steps with code examples
4. Risk assessment

Be direct, technical, and actionable. Format using markdown."""


class AIAnalyzer:
    def __init__(self):
        self.provider = settings.AI_PROVIDER
        self.openai_key = settings.OPENAI_API_KEY
        self.anthropic_key = settings.ANTHROPIC_API_KEY

    async def analyze_finding(self, finding: Dict) -> Dict[str, str]:
        prompt = self._build_prompt(finding)
        
        if self.provider == "anthropic" and self.anthropic_key:
            response = await self._call_anthropic(prompt)
        elif self.openai_key:
            response = await self._call_openai(prompt)
        else:
            return self._fallback_analysis(finding)
        
        return self._parse_response(response)

    async def analyze_findings_batch(self, findings: List[Dict], max_concurrent: int = 5) -> List[Dict]:
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def analyze_with_limit(finding):
            async with semaphore:
                analysis = await self.analyze_finding(finding)
                finding["ai_explanation"] = analysis.get("explanation", "")
                finding["ai_remediation"] = analysis.get("remediation", "")
                return finding
        
        tasks = [analyze_with_limit(f) for f in findings]
        return await asyncio.gather(*tasks)

    def _build_prompt(self, finding: Dict) -> str:
        return f"""Analyze this security vulnerability:

**Rule:** {finding.get('rule_name', 'Unknown')} ({finding.get('rule_id', '')})
**Severity:** {finding.get('severity', 'unknown').upper()}
**File:** {finding.get('file_path', '')}
**Line:** {finding.get('start_line', 0)}-{finding.get('end_line', 0)}

**Code:**
```
{finding.get('code_snippet', 'No code available')}
```

**Scanner Message:** {finding.get('message', '')}

**CWE:** {', '.join(finding.get('cwe_ids', []))}
**OWASP:** {', '.join(finding.get('owasp_ids', []))}

Provide:
1. **Explanation**: What is this vulnerability and why is it dangerous?
2. **Impact**: What could an attacker do?
3. **Remediation**: How to fix it with specific code changes?
4. **Risk Level**: Assessment considering context."""

    async def _call_openai(self, prompt: str) -> str:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.openai_key}"},
                json={
                    "model": "gpt-4-turbo-preview",
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.3,
                    "max_tokens": 1000
                },
                timeout=60
            )
            data = response.json()
            return data["choices"][0]["message"]["content"]

    async def _call_anthropic(self, prompt: str) -> str:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": self.anthropic_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                },
                json={
                    "model": "claude-3-sonnet-20240229",
                    "max_tokens": 1000,
                    "system": SYSTEM_PROMPT,
                    "messages": [{"role": "user", "content": prompt}]
                },
                timeout=60
            )
            data = response.json()
            return data["content"][0]["text"]

    def _fallback_analysis(self, finding: Dict) -> Dict[str, str]:
        severity = finding.get("severity", "medium")
        rule_name = finding.get("rule_name", "Unknown vulnerability")
        
        explanations = {
            "critical": f"This is a critical security issue: {rule_name}. Immediate attention required.",
            "high": f"High severity vulnerability detected: {rule_name}. Should be addressed promptly.",
            "medium": f"Medium severity issue: {rule_name}. Review and fix when possible.",
            "low": f"Low severity finding: {rule_name}. Consider addressing in future updates.",
        }
        
        return {
            "explanation": explanations.get(severity, f"Security issue detected: {rule_name}"),
            "remediation": f"Review the code at line {finding.get('start_line', 0)} and apply security best practices. Consult OWASP guidelines for detailed remediation steps."
        }

    def _parse_response(self, response: str) -> Dict[str, str]:
        parts = response.split("**Remediation**")
        explanation = parts[0].replace("**Explanation**:", "").replace("**Impact**:", "\n\n**Impact:**").strip()
        remediation = parts[1].strip() if len(parts) > 1 else ""
        
        if "**Risk Level**" in remediation:
            rem_parts = remediation.split("**Risk Level**")
            remediation = rem_parts[0].strip()
        
        return {
            "explanation": explanation[:2000],
            "remediation": remediation[:2000]
        }
