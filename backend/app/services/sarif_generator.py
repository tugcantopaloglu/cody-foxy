from typing import List, Dict, Any
from datetime import datetime


class SarifGenerator:
    VERSION = "2.1.0"
    SCHEMA = "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json"

    def generate(self, findings: List[Dict], tool_name: str = "Cody Foxy", scan_id: int = 0) -> Dict[str, Any]:
        rules = self._generate_rules(findings)
        results = self._generate_results(findings)
        
        return {
            "$schema": self.SCHEMA,
            "version": self.VERSION,
            "runs": [{
                "tool": {
                    "driver": {
                        "name": tool_name,
                        "version": "1.0.0",
                        "informationUri": "https://github.com/tugcantopaloglu/cody-foxy",
                        "rules": rules,
                    }
                },
                "results": results,
                "invocations": [{
                    "executionSuccessful": True,
                    "endTimeUtc": datetime.utcnow().isoformat() + "Z",
                }],
                "properties": {
                    "scanId": scan_id,
                    "totalFindings": len(findings),
                }
            }]
        }

    def _generate_rules(self, findings: List[Dict]) -> List[Dict]:
        seen_rules = {}
        rules = []
        
        for f in findings:
            rule_id = f.get("rule_id", "unknown")
            if rule_id not in seen_rules:
                seen_rules[rule_id] = True
                rules.append({
                    "id": rule_id,
                    "name": f.get("rule_name", rule_id),
                    "shortDescription": {"text": f.get("rule_name", "")},
                    "fullDescription": {"text": f.get("message", "")},
                    "defaultConfiguration": {
                        "level": self._severity_to_level(f.get("severity", "medium"))
                    },
                    "properties": {
                        "tags": self._get_tags(f),
                        "security-severity": self._severity_to_score(f.get("severity", "medium")),
                    },
                    "helpUri": f.get("references", [""])[0] if f.get("references") else "",
                })
        
        return rules

    def _generate_results(self, findings: List[Dict]) -> List[Dict]:
        results = []
        
        for i, f in enumerate(findings):
            result = {
                "ruleId": f.get("rule_id", "unknown"),
                "ruleIndex": self._get_rule_index(findings, f.get("rule_id")),
                "level": self._severity_to_level(f.get("severity", "medium")),
                "message": {
                    "text": f.get("message", "Security issue detected"),
                    "markdown": self._format_markdown_message(f),
                },
                "locations": [{
                    "physicalLocation": {
                        "artifactLocation": {
                            "uri": f.get("file_path", ""),
                            "uriBaseId": "%SRCROOT%",
                        },
                        "region": {
                            "startLine": f.get("start_line", 1),
                            "endLine": f.get("end_line", 1),
                            "startColumn": f.get("start_col", 1),
                            "endColumn": f.get("end_col", 1),
                            "snippet": {"text": f.get("code_snippet", "")},
                        }
                    }
                }],
                "fingerprints": {
                    "primary": f"{f.get('rule_id')}:{f.get('file_path')}:{f.get('start_line')}"
                },
                "properties": {
                    "severity": f.get("severity", "medium"),
                    "ai_explanation": f.get("ai_explanation", ""),
                    "ai_remediation": f.get("ai_remediation", ""),
                }
            }
            
            if f.get("cwe_ids"):
                result["taxa"] = [{"toolComponent": {"name": "CWE"}, "id": cwe} for cwe in f["cwe_ids"]]
            
            results.append(result)
        
        return results

    def _severity_to_level(self, severity: str) -> str:
        mapping = {
            "critical": "error",
            "high": "error",
            "medium": "warning",
            "low": "note",
            "info": "none",
        }
        return mapping.get(severity.lower(), "warning")

    def _severity_to_score(self, severity: str) -> str:
        mapping = {
            "critical": "9.5",
            "high": "7.5",
            "medium": "5.0",
            "low": "2.5",
            "info": "1.0",
        }
        return mapping.get(severity.lower(), "5.0")

    def _get_tags(self, finding: Dict) -> List[str]:
        tags = ["security"]
        tags.extend(finding.get("cwe_ids", []))
        tags.extend(finding.get("owasp_ids", []))
        return tags

    def _get_rule_index(self, findings: List[Dict], rule_id: str) -> int:
        seen = []
        for f in findings:
            rid = f.get("rule_id")
            if rid not in seen:
                seen.append(rid)
            if rid == rule_id:
                return seen.index(rid)
        return 0

    def _format_markdown_message(self, finding: Dict) -> str:
        parts = [f"**{finding.get('rule_name', 'Security Issue')}**\n"]
        parts.append(f"{finding.get('message', '')}\n")
        
        if finding.get("ai_explanation"):
            parts.append(f"\n**Analysis:**\n{finding['ai_explanation']}\n")
        
        if finding.get("ai_remediation"):
            parts.append(f"\n**Remediation:**\n{finding['ai_remediation']}\n")
        
        return "\n".join(parts)
