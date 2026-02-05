import pytest
from app.services.sarif_generator import SarifGenerator


@pytest.fixture
def sarif_gen():
    return SarifGenerator()


@pytest.fixture
def sample_findings():
    return [
        {
            "rule_id": "python/sql-injection",
            "rule_name": "SQL Injection",
            "severity": "critical",
            "file_path": "app/db.py",
            "start_line": 42,
            "end_line": 42,
            "start_col": 5,
            "end_col": 50,
            "code_snippet": 'query = "SELECT * FROM users WHERE id = " + user_id',
            "message": "Possible SQL injection vulnerability",
            "ai_explanation": "This code concatenates user input directly into a SQL query.",
            "ai_remediation": "Use parameterized queries instead.",
            "cwe_ids": ["CWE-89"],
            "owasp_ids": ["A03:2021"],
            "references": ["https://owasp.org/Top10/A03_2021-Injection/"],
        },
        {
            "rule_id": "python/hardcoded-secret",
            "rule_name": "Hardcoded Secret",
            "severity": "high",
            "file_path": "config.py",
            "start_line": 10,
            "end_line": 10,
            "start_col": 0,
            "end_col": 30,
            "code_snippet": 'API_KEY = "sk-1234567890"',
            "message": "Hardcoded secret detected",
            "cwe_ids": ["CWE-798"],
            "owasp_ids": [],
            "references": [],
        },
    ]


def test_generate_sarif_structure(sarif_gen, sample_findings):
    sarif = sarif_gen.generate(sample_findings, scan_id=123)
    
    assert sarif["$schema"] == SarifGenerator.SCHEMA
    assert sarif["version"] == "2.1.0"
    assert len(sarif["runs"]) == 1
    
    run = sarif["runs"][0]
    assert run["tool"]["driver"]["name"] == "Cody Foxy"
    assert len(run["results"]) == 2


def test_sarif_rules(sarif_gen, sample_findings):
    sarif = sarif_gen.generate(sample_findings)
    rules = sarif["runs"][0]["tool"]["driver"]["rules"]
    
    assert len(rules) == 2
    rule_ids = [r["id"] for r in rules]
    assert "python/sql-injection" in rule_ids
    assert "python/hardcoded-secret" in rule_ids


def test_sarif_results(sarif_gen, sample_findings):
    sarif = sarif_gen.generate(sample_findings)
    results = sarif["runs"][0]["results"]
    
    sql_injection = next(r for r in results if r["ruleId"] == "python/sql-injection")
    
    assert sql_injection["level"] == "error"
    assert sql_injection["locations"][0]["physicalLocation"]["artifactLocation"]["uri"] == "app/db.py"
    assert sql_injection["locations"][0]["physicalLocation"]["region"]["startLine"] == 42


def test_severity_mapping(sarif_gen):
    assert sarif_gen._severity_to_level("critical") == "error"
    assert sarif_gen._severity_to_level("high") == "error"
    assert sarif_gen._severity_to_level("medium") == "warning"
    assert sarif_gen._severity_to_level("low") == "note"
    assert sarif_gen._severity_to_level("info") == "none"


def test_severity_score(sarif_gen):
    assert sarif_gen._severity_to_score("critical") == "9.5"
    assert sarif_gen._severity_to_score("high") == "7.5"
    assert sarif_gen._severity_to_score("medium") == "5.0"
    assert sarif_gen._severity_to_score("low") == "2.5"
