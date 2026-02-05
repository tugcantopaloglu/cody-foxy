"use client"

import { useState } from "react"
import { Download, Filter, Shield, AlertCircle, AlertTriangle, Info } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Badge } from "@/components/ui/badge"
import { FindingCard } from "./finding-card"
import type { Scan } from "@/store/scan-store"

interface ScanResultsProps {
  scan: Scan
}

export function ScanResults({ scan }: ScanResultsProps) {
  const [severityFilter, setSeverityFilter] = useState<string>("all")

  const filteredFindings = scan.findings?.filter((f) =>
    severityFilter === "all" ? true : f.severity === severityFilter
  ) || []

  const downloadSarif = async () => {
    try {
      const response = await fetch(`/api/scans/${scan.id}/sarif`)
      const sarif = await response.json()
      const blob = new Blob([JSON.stringify(sarif, null, 2)], { type: "application/json" })
      const url = URL.createObjectURL(blob)
      const a = document.createElement("a")
      a.href = url
      a.download = `cody-foxy-scan-${scan.id}.sarif`
      a.click()
      URL.revokeObjectURL(url)
    } catch (error) {
      console.error("Failed to download SARIF:", error)
    }
  }

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <StatCard
          title="Total Issues"
          value={scan.total_findings}
          icon={<Shield className="h-5 w-5" />}
          color="text-foxy-orange"
        />
        <StatCard
          title="Critical"
          value={scan.critical_count}
          icon={<AlertCircle className="h-5 w-5" />}
          color="text-severity-critical"
        />
        <StatCard
          title="High"
          value={scan.high_count}
          icon={<AlertCircle className="h-5 w-5" />}
          color="text-severity-high"
        />
        <StatCard
          title="Medium"
          value={scan.medium_count}
          icon={<AlertTriangle className="h-5 w-5" />}
          color="text-severity-medium"
        />
        <StatCard
          title="Low"
          value={scan.low_count}
          icon={<Info className="h-5 w-5" />}
          color="text-severity-low"
        />
      </div>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Filter className="h-5 w-5" />
            Findings
          </CardTitle>
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={downloadSarif}>
              <Download className="h-4 w-4 mr-2" />
              SARIF
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <Tabs value={severityFilter} onValueChange={setSeverityFilter}>
            <TabsList className="mb-4">
              <TabsTrigger value="all">All ({scan.total_findings})</TabsTrigger>
              <TabsTrigger value="critical">Critical ({scan.critical_count})</TabsTrigger>
              <TabsTrigger value="high">High ({scan.high_count})</TabsTrigger>
              <TabsTrigger value="medium">Medium ({scan.medium_count})</TabsTrigger>
              <TabsTrigger value="low">Low ({scan.low_count})</TabsTrigger>
            </TabsList>
            <TabsContent value={severityFilter}>
              <ScrollArea className="h-[600px] pr-4">
                <div className="space-y-3">
                  {filteredFindings.length > 0 ? (
                    filteredFindings.map((finding, index) => (
                      <FindingCard key={finding.id} finding={finding} index={index} />
                    ))
                  ) : (
                    <div className="text-center py-12 text-muted-foreground">
                      <Shield className="h-12 w-12 mx-auto mb-4 opacity-50" />
                      <p>No findings in this category</p>
                    </div>
                  )}
                </div>
              </ScrollArea>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  )
}

function StatCard({ title, value, icon, color }: { title: string; value: number; icon: React.ReactNode; color: string }) {
  return (
    <Card>
      <CardContent className="p-4">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-muted-foreground">{title}</p>
            <p className={`text-2xl font-bold ${color}`}>{value}</p>
          </div>
          <div className={color}>{icon}</div>
        </div>
      </CardContent>
    </Card>
  )
}
