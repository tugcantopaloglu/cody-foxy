"use client"

import { useState, useMemo } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Copy, Check, ChevronDown, ChevronUp, ExternalLink, AlertCircle } from "lucide-react"
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter"
import { vscDarkPlus, vs } from "react-syntax-highlighter/dist/esm/styles/prism"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { useTheme } from "next-themes"

interface Finding {
  id: number
  rule_id: string
  rule_name: string
  severity: string
  file_path: string
  start_line: number
  end_line: number
  start_col: number
  end_col: number
  code_snippet: string
  message: string
  ai_explanation?: string
  ai_remediation?: string
  cwe_ids: string[]
  owasp_ids: string[]
  references: string[]
}

interface CodeDiffViewerProps {
  finding: Finding
  expanded?: boolean
}

const languageMap: Record<string, string> = {
  ".py": "python",
  ".js": "javascript",
  ".jsx": "jsx",
  ".ts": "typescript",
  ".tsx": "tsx",
  ".go": "go",
  ".java": "java",
  ".rb": "ruby",
  ".php": "php",
  ".rs": "rust",
  ".c": "c",
  ".cpp": "cpp",
  ".cs": "csharp",
  ".swift": "swift",
  ".kt": "kotlin",
  ".scala": "scala",
  ".sh": "bash",
  ".yml": "yaml",
  ".yaml": "yaml",
  ".json": "json",
  ".xml": "xml",
  ".sql": "sql",
}

function getLanguage(filePath: string): string {
  const ext = filePath.slice(filePath.lastIndexOf("."))
  return languageMap[ext] || "text"
}

function parseCodeWithLineNumbers(code: string, startLine: number): { line: number; content: string }[] {
  const lines = code.split("\n")
  return lines.map((content, index) => ({
    line: startLine + index,
    content,
  }))
}

export function CodeDiffViewer({ finding, expanded: initialExpanded = false }: CodeDiffViewerProps) {
  const [expanded, setExpanded] = useState(initialExpanded)
  const [copied, setCopied] = useState(false)
  const [showRemediation, setShowRemediation] = useState(false)
  const { theme } = useTheme()

  const language = useMemo(() => getLanguage(finding.file_path), [finding.file_path])
  const codeLines = useMemo(
    () => parseCodeWithLineNumbers(finding.code_snippet || "", finding.start_line),
    [finding.code_snippet, finding.start_line]
  )

  const copyCode = async () => {
    await navigator.clipboard.writeText(finding.code_snippet || "")
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const severityColors: Record<string, string> = {
    critical: "bg-red-500/10 border-red-500/50 text-red-500",
    high: "bg-orange-500/10 border-orange-500/50 text-orange-500",
    medium: "bg-yellow-500/10 border-yellow-500/50 text-yellow-500",
    low: "bg-blue-500/10 border-blue-500/50 text-blue-500",
  }

  return (
    <Card className={`border-l-4 ${severityColors[finding.severity] || ""}`}>
      <CardHeader className="pb-2">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-2 flex-wrap">
              <Badge variant={finding.severity as any}>{finding.severity.toUpperCase()}</Badge>
              <span className="font-mono text-sm text-muted-foreground">{finding.rule_id}</span>
            </div>
            <CardTitle className="text-lg mt-2">{finding.rule_name}</CardTitle>
            <p className="text-sm text-muted-foreground mt-1">{finding.message}</p>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setExpanded(!expanded)}
            className="shrink-0"
          >
            {expanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
          </Button>
        </div>

        <div className="flex items-center gap-4 mt-3 text-sm">
          <span className="font-mono text-foxy-orange">{finding.file_path}</span>
          <span className="text-muted-foreground">
            Lines {finding.start_line}-{finding.end_line}
          </span>
        </div>

        <div className="flex flex-wrap gap-2 mt-2">
          {finding.cwe_ids.map((cwe) => (
            <Badge key={cwe} variant="outline" className="text-xs">
              {cwe}
            </Badge>
          ))}
          {finding.owasp_ids.map((owasp) => (
            <Badge key={owasp} variant="outline" className="text-xs bg-purple-500/10">
              {owasp}
            </Badge>
          ))}
        </div>
      </CardHeader>

      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
          >
            <CardContent className="pt-0">
              <div className="relative mt-4 rounded-lg overflow-hidden border">
                <div className="flex items-center justify-between px-4 py-2 bg-muted/50 border-b">
                  <span className="text-xs font-mono text-muted-foreground">{language}</span>
                  <Button variant="ghost" size="sm" onClick={copyCode}>
                    {copied ? (
                      <Check className="h-4 w-4 text-green-500" />
                    ) : (
                      <Copy className="h-4 w-4" />
                    )}
                  </Button>
                </div>
                <div className="relative">
                  <div className="absolute left-0 top-0 bottom-0 w-12 bg-muted/30 flex flex-col items-end pr-2 pt-4 text-xs text-muted-foreground font-mono">
                    {codeLines.map(({ line }) => (
                      <div
                        key={line}
                        className={`h-6 leading-6 ${
                          line >= finding.start_line && line <= finding.end_line
                            ? "text-red-500 font-bold"
                            : ""
                        }`}
                      >
                        {line}
                      </div>
                    ))}
                  </div>
                  <div className="pl-14 overflow-x-auto">
                    <SyntaxHighlighter
                      language={language}
                      style={theme === "dark" ? vscDarkPlus : vs}
                      customStyle={{
                        margin: 0,
                        padding: "1rem",
                        background: "transparent",
                        fontSize: "0.875rem",
                      }}
                      showLineNumbers={false}
                      wrapLines={true}
                      lineProps={(lineNumber) => {
                        const actualLine = finding.start_line + lineNumber - 1
                        const isVulnerable =
                          actualLine >= finding.start_line && actualLine <= finding.end_line
                        return {
                          style: {
                            display: "block",
                            backgroundColor: isVulnerable
                              ? theme === "dark"
                                ? "rgba(239, 68, 68, 0.15)"
                                : "rgba(239, 68, 68, 0.1)"
                              : "transparent",
                            borderLeft: isVulnerable ? "3px solid rgb(239, 68, 68)" : "3px solid transparent",
                            paddingLeft: "0.5rem",
                          },
                        }
                      }}
                    >
                      {finding.code_snippet || "// No code snippet available"}
                    </SyntaxHighlighter>
                  </div>
                </div>
              </div>

              {(finding.ai_explanation || finding.ai_remediation) && (
                <div className="mt-4 space-y-4">
                  {finding.ai_explanation && (
                    <div className="p-4 rounded-lg bg-muted/50">
                      <div className="flex items-center gap-2 mb-2">
                        <AlertCircle className="h-4 w-4 text-foxy-orange" />
                        <span className="font-semibold">AI Analysis</span>
                      </div>
                      <div className="prose prose-sm dark:prose-invert max-w-none">
                        {finding.ai_explanation}
                      </div>
                    </div>
                  )}

                  {finding.ai_remediation && (
                    <div className="p-4 rounded-lg bg-green-500/10 border border-green-500/20">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => setShowRemediation(!showRemediation)}
                        className="w-full justify-between"
                      >
                        <span className="font-semibold text-green-600 dark:text-green-400">
                          🔧 Suggested Fix
                        </span>
                        {showRemediation ? (
                          <ChevronUp className="h-4 w-4" />
                        ) : (
                          <ChevronDown className="h-4 w-4" />
                        )}
                      </Button>
                      <AnimatePresence>
                        {showRemediation && (
                          <motion.div
                            initial={{ height: 0, opacity: 0 }}
                            animate={{ height: "auto", opacity: 1 }}
                            exit={{ height: 0, opacity: 0 }}
                            className="mt-2 prose prose-sm dark:prose-invert max-w-none"
                          >
                            {finding.ai_remediation}
                          </motion.div>
                        )}
                      </AnimatePresence>
                    </div>
                  )}
                </div>
              )}

              {finding.references.length > 0 && (
                <div className="mt-4">
                  <h4 className="text-sm font-semibold mb-2">References</h4>
                  <ul className="space-y-1">
                    {finding.references.map((ref, i) => (
                      <li key={i}>
                        <a
                          href={ref}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-sm text-blue-500 hover:underline flex items-center gap-1"
                        >
                          <ExternalLink className="h-3 w-3" />
                          {ref}
                        </a>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </CardContent>
          </motion.div>
        )}
      </AnimatePresence>
    </Card>
  )
}
