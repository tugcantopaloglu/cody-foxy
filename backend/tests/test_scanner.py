import pytest
import tempfile
import os
from pathlib import Path

from app.services.scanner import ScannerService


@pytest.fixture
def scanner():
    return ScannerService()


@pytest.fixture
def temp_code_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        py_file = Path(tmpdir) / "vulnerable.py"
        py_file.write_text('''
import os
import subprocess

def unsafe_eval(user_input):
    return eval(user_input)

def command_injection(cmd):
    os.system(cmd)

def sql_injection(user_id):
    query = "SELECT * FROM users WHERE id = " + user_id
    return query

password = "hardcoded_secret_123"
''')
        
        js_file = Path(tmpdir) / "app.js"
        js_file.write_text('''
const express = require('express');
const app = express();

app.get('/search', (req, res) => {
    const query = req.query.q;
    res.send(`<h1>Results for: ${query}</h1>`);
});

const apiKey = "sk-1234567890abcdef";
''')
        
        yield tmpdir


def test_detect_languages(scanner, temp_code_dir):
    languages = scanner._detect_languages(Path(temp_code_dir))
    assert "python" in languages
    assert "javascript" in languages


def test_get_scannable_files(scanner, temp_code_dir):
    files = scanner._get_scannable_files(Path(temp_code_dir))
    assert len(files) == 2
    extensions = {f.suffix for f in files}
    assert ".py" in extensions
    assert ".js" in extensions


def test_calculate_stats(scanner):
    findings = [
        {"severity": "critical"},
        {"severity": "high"},
        {"severity": "high"},
        {"severity": "medium"},
        {"severity": "low"},
        {"severity": "low"},
        {"severity": "low"},
    ]
    stats = scanner._calculate_stats(findings)
    assert stats["critical"] == 1
    assert stats["high"] == 2
    assert stats["medium"] == 1
    assert stats["low"] == 3


def test_deduplicate_findings(scanner):
    findings = [
        {"file_path": "test.py", "start_line": 10, "rule_id": "rule1"},
        {"file_path": "test.py", "start_line": 10, "rule_id": "rule1"},
        {"file_path": "test.py", "start_line": 20, "rule_id": "rule1"},
    ]
    unique = scanner._deduplicate_findings(findings)
    assert len(unique) == 2


@pytest.mark.asyncio
async def test_scan_directory(scanner, temp_code_dir):
    results = await scanner.scan_directory(temp_code_dir)
    
    assert "languages" in results
    assert "total_files" in results
    assert "findings" in results
    assert "stats" in results
    
    assert results["total_files"] == 2
    assert len(results["languages"]) >= 1
