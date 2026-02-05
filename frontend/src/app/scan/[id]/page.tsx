"use client"

import { useEffect, useState } from "react"
import { useParams } from "next/navigation"
import { motion } from "framer-motion"
import { Loader2, CheckCircle, XCircle, Clock, FileCode, Languages } from "lucide-react"
import { Header } from "@/components/layout/header"
import { Footer } from "@/components/layout/footer"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { ScanResults } from "@/components/scan/scan-results"
import { getScan, getScanFindings } from "@/lib/api"
import { formatDate } from "@/lib/utils"
import type { Scan, Finding } from "@/store/scan-store"

export default function ScanDetailPage() {
  const params = useParams()
  const scanId = params.id as string
  const [scan, setScan] = useState<Scan | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let interval: NodeJS.Timeout

    const fetchScan = async () => {
      try {
        const scanData = await getScan(Number(scanId)) as Scan
        
        if (scanData.status === "completed" || scanData.status === "failed") {
          const findings = await getScanFindings(Number(scanId)) as Finding[]
          scanData.findings = findings
          clearInterval(interval)
        }
        
        setScan(scanData)
        setLoading(false)
      } catch (err: any) {
        setError(err.message)
        setLoading(false)
        clearInterval(interval)
      }
    }

    fetchScan()
    interval = setInterval(fetchScan, 2000)

    return () => clearInterval(interval)
  }, [scanId])

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "completed":
        return <CheckCircle className="h-5 w-5 text-green-500" />
      case "failed":
        return <XCircle className="h-5 w-5 text-red-500" />
      case "running":
        return <Loader2 className="h-5 w-5 text-foxy-orange animate-spin" />
      default:
        return <Clock className="h-5 w-5 text-muted-foreground" />
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex flex-col">
        <Header />
        <main className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <Loader2 className="h-12 w-12 text-foxy-orange animate-spin mx-auto mb-4" />
            <p className="text-muted-foreground">Loading scan...</p>
          </div>
        </main>
        <Footer />
      </div>
    )
  }

  if (error || !scan) {
    return (
      <div className="min-h-screen flex flex-col">
        <Header />
        <main className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <XCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
            <p className="text-red-500">{error || "Scan not found"}</p>
          </div>
        </main>
        <Footer />
      </div>
    )
  }

  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1 py-12">
        <div className="container">
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
            <Card className="mb-6">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <span className="text-3xl">🦊</span>
                    <div>
                      <CardTitle className="flex items-center gap-2">
                        Scan #{scan.id}
                        {getStatusIcon(scan.status)}
                      </CardTitle>
                      <p className="text-sm text-muted-foreground mt-1">
                        {scan.source_path || "Uploaded code"} • {formatDate(scan.created_at)}
                      </p>
                    </div>
                  </div>
                  <Badge variant={scan.status === "completed" ? "default" : scan.status === "failed" ? "destructive" : "secondary"}>
                    {scan.status.toUpperCase()}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                {scan.status === "running" && (
                  <div className="space-y-3">
                    <div className="flex justify-between text-sm">
                      <span>Scanning files...</span>
                      <span>{scan.files_scanned} / {scan.total_files || "?"}</span>
                    </div>
                    <Progress value={scan.total_files ? (scan.files_scanned / scan.total_files) * 100 : 0} />
                  </div>
                )}
                {scan.status === "completed" && (
                  <div className="flex flex-wrap gap-4">
                    <div className="flex items-center gap-2">
                      <FileCode className="h-4 w-4 text-muted-foreground" />
                      <span className="text-sm">{scan.files_scanned} files scanned</span>
                    </div>
                    {scan.languages_detected?.length > 0 && (
                      <div className="flex items-center gap-2">
                        <Languages className="h-4 w-4 text-muted-foreground" />
                        <span className="text-sm">{scan.languages_detected.join(", ")}</span>
                      </div>
                    )}
                  </div>
                )}
                {scan.status === "failed" && scan.error_message && (
                  <div className="p-4 bg-red-500/10 border border-red-500/30 rounded-lg">
                    <p className="text-red-500">{scan.error_message}</p>
                  </div>
                )}
              </CardContent>
            </Card>

            {scan.status === "completed" && <ScanResults scan={scan} />}
          </motion.div>
        </div>
      </main>
      <Footer />
    </div>
  )
}
