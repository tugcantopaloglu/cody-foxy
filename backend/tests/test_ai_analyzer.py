import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.ai_analyzer import AIAnalyzer


@pytest.fixture
def analyzer():
    return AIAnalyzer()


@pytest.fixture
def sample_finding():
    return {
        "rule_id": "python.lang.security.audit.eval-injection",
        "rule_name": "Eval Injection",
        "severity": "critical",
        "file_path": "app.py",
        "start_line": 10,
        "end_line": 10,
        "code_snippet": "result = eval(user_input)",
        "message": "Avoid using eval() with user input",
        "cwe_ids": ["CWE-94"],
        "owasp_ids": ["A03:2021"],
    }


def test_build_prompt(analyzer, sample_finding):
    prompt = analyzer._build_prompt(sample_finding)
    
    assert "Eval Injection" in prompt
    assert "critical" in prompt.upper()
    assert "app.py" in prompt
    assert "eval(user_input)" in prompt
    assert "CWE-94" in prompt


def test_fallback_analysis_critical(analyzer):
    finding = {"severity": "critical", "rule_name": "Test Issue", "start_line": 10}
    
    result = analyzer._fallback_analysis(finding)
    
    assert "explanation" in result
    assert "remediation" in result
    assert "critical" in result["explanation"].lower()
    assert "immediate" in result["explanation"].lower()


def test_fallback_analysis_high(analyzer):
    finding = {"severity": "high", "rule_name": "Test Issue", "start_line": 10}
    
    result = analyzer._fallback_analysis(finding)
    
    assert "high" in result["explanation"].lower()
    assert "promptly" in result["explanation"].lower()


def test_fallback_analysis_medium(analyzer):
    finding = {"severity": "medium", "rule_name": "Test Issue", "start_line": 10}
    
    result = analyzer._fallback_analysis(finding)
    
    assert "medium" in result["explanation"].lower()


def test_fallback_analysis_low(analyzer):
    finding = {"severity": "low", "rule_name": "Test Issue", "start_line": 10}
    
    result = analyzer._fallback_analysis(finding)
    
    assert "low" in result["explanation"].lower()


def test_parse_response_basic(analyzer):
    response = """**Explanation**: This is a test vulnerability.

**Impact:** It could allow attackers to execute code.

**Remediation**: Fix by sanitizing input.

**Risk Level**: High"""
    
    result = analyzer._parse_response(response)
    
    assert "explanation" in result
    assert "remediation" in result
    assert len(result["explanation"]) > 0


def test_parse_response_truncation(analyzer):
    long_text = "A" * 3000
    response = f"**Explanation**: {long_text}\n**Remediation**: {long_text}\n**Risk Level**: High"
    
    result = analyzer._parse_response(response)
    
    assert len(result["explanation"]) <= 2000
    assert len(result["remediation"]) <= 2000


@pytest.mark.asyncio
async def test_analyze_finding_fallback(analyzer):
    finding = {"severity": "high", "rule_name": "Test", "start_line": 1}
    
    analyzer.openai_key = ""
    analyzer.anthropic_key = ""
    
    result = await analyzer.analyze_finding(finding)
    
    assert "explanation" in result
    assert "remediation" in result


@pytest.mark.asyncio
async def test_analyze_findings_batch(analyzer):
    findings = [
        {"severity": "high", "rule_name": f"Test {i}", "start_line": i}
        for i in range(3)
    ]
    
    analyzer.openai_key = ""
    analyzer.anthropic_key = ""
    
    results = await analyzer.analyze_findings_batch(findings)
    
    assert len(results) == 3
    for f in results:
        assert "ai_explanation" in f
        assert "ai_remediation" in f


@pytest.mark.asyncio
@patch("httpx.AsyncClient.post")
async def test_call_openai(mock_post, analyzer):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "Test response"}}]
    }
    mock_post.return_value = mock_response
    
    analyzer.openai_key = "test-key"
    result = await analyzer._call_openai("Test prompt")
    
    assert result == "Test response"


@pytest.mark.asyncio
@patch("httpx.AsyncClient.post")
async def test_call_anthropic(mock_post, analyzer):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "content": [{"text": "Test response"}]
    }
    mock_post.return_value = mock_response
    
    analyzer.anthropic_key = "test-key"
    result = await analyzer._call_anthropic("Test prompt")
    
    assert result == "Test response"
