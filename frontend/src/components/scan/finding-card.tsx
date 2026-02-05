"use client"

import { useState } from "react"
import { ChevronDown, FileCode, AlertTriangle, Lightbulb, ExternalLink } from "lucide-react"
import { motion, AnimatePresence } from "framer-motion"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { cn, getSeverityIcon } from "@/lib/utils"
import type { Finding } from "@/store/scan-store"

interface FindingCardProps {
  finding: Finding
  index: number
}

export function FindingCard({ finding, index }: FindingCardProps) {
  const [isExpanded, setIsExpanded] = useState(false)

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05 }}
    >
      <Card className={cn("overflow-hidden transition-all", isExpanded && "ring-2 ring-foxy-orange/50")}>
        <button
          className="w-full p-4 flex items-start gap-4 text-left hover:bg-muted/50 transition-colors"
          onClick={() => setIsExpanded(!isExpanded)}
        >
          <div className="flex-shrink-0 text-2xl">{getSeverityIcon(finding.severity)}</div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 flex-wrap mb-1">
              <Badge variant={finding.severity as any}>{finding.severity.toUpperCase()}</Badge>
              {finding.cwe_ids?.map((cwe) => (
                <Badge key={cwe} variant="outline" className="text-xs">{cwe}</Badge>
              ))}
            </div>
            <h3 className="font-semibold truncate">{finding.rule_name}</h3>
            <div className="flex items-center gap-2 text-sm text-muted-foreground mt-1">
              <FileCode className="h-4 w-4" />
              <span className="truncate">{finding.file_path}</span>
              <span>:</span>
              <span>{finding.start_line}</span>
            </div>
          </div>
          <ChevronDown className={cn("h-5 w-5 transition-transform", isExpanded && "rotate-180")} />
        </button>

        <AnimatePresence>
          {isExpanded && (
            <motion.div
              initial={{ height: 0 }}
              animate={{ height: "auto" }}
              exit={{ height: 0 }}
              className="overflow-hidden"
            >
              <CardContent className="pt-0 pb-4 space-y-4">
                <div className="bg-muted rounded-lg p-4 overflow-x-auto">
                  <pre className="text-sm font-mono">
                    <code>{finding.code_snippet || "No code snippet available"}</code>
                  </pre>
                </div>

                <div className="space-y-3">
                  <div className="flex items-start gap-2">
                    <AlertTriangle className="h-5 w-5 text-foxy-orange flex-shrink-0 mt-0.5" />
                    <div>
                      <p className="font-medium">Issue</p>
                      <p className="text-sm text-muted-foreground">{finding.message}</p>
                    </div>
                  </div>

                  {finding.ai_explanation && (
                    <div className="flex items-start gap-2">
                      <span className="text-lg flex-shrink-0">🤖</span>
                      <div>
                        <p className="font-medium">AI Analysis</p>
                        <p className="text-sm text-muted-foreground whitespace-pre-wrap">{finding.ai_explanation}</p>
                      </div>
                    </div>
                  )}

                  {finding.ai_remediation && (
                    <div className="flex items-start gap-2">
                      <Lightbulb className="h-5 w-5 text-foxy-yellow flex-shrink-0 mt-0.5" />
                      <div>
                        <p className="font-medium">How to Fix</p>
                        <p className="text-sm text-muted-foreground whitespace-pre-wrap">{finding.ai_remediation}</p>
                      </div>
                    </div>
                  )}

                  {finding.owasp_ids?.length > 0 && (
                    <div className="flex flex-wrap gap-2">
                      {finding.owasp_ids.map((owasp) => (
                        <Badge key={owasp} variant="secondary">{owasp}</Badge>
                      ))}
                    </div>
                  )}
                </div>
              </CardContent>
            </motion.div>
          )}
        </AnimatePresence>
      </Card>
    </motion.div>
  )
}
