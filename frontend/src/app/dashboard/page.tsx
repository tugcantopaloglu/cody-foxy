"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { motion } from "framer-motion"
import { Plus, Clock, Shield, TrendingDown, FileCode } from "lucide-react"
import { Header } from "@/components/layout/header"
import { Footer } from "@/components/layout/footer"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { StatsChart } from "@/components/dashboard/stats-chart"
import { getScans } from "@/lib/api"
import { formatDate } from "@/lib/utils"
import type { Scan } from "@/store/scan-store"

export default function DashboardPage() {
  const [scans, setScans] = useState<Scan[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchScans = async () => {
      try {
        const data = await getScans(10) as Scan[]
        setScans(data)
      } catch (err) {
        console.error("Failed to fetch scans:", err)
      } finally {
        setLoading(false)
      }
    }
    fetchScans()
  }, [])

  const totalVulnerabilities = scans.reduce((acc, s) => acc + s.total_findings, 0)
  const criticalCount = scans.reduce((acc, s) => acc + s.critical_count, 0)
  const recentScans = scans.length

  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1 py-12">
        <div className="container">
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
            <div className="flex items-center justify-between mb-8">
              <div>
                <h1 className="text-3xl font-bold">Dashboard</h1>
                <p className="text-muted-foreground">Monitor your code security status</p>
              </div>
              <Link href="/scan">
                <Button variant="gradient">
                  <Plus className="h-4 w-4 mr-2" />
                  New Scan
                </Button>
              </Link>
            </div>

            <div className="grid md:grid-cols-4 gap-6 mb-8">
              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-muted-foreground">Total Scans</p>
                      <p className="text-3xl font-bold">{recentScans}</p>
                    </div>
                    <FileCode className="h-8 w-8 text-foxy-orange" />
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-muted-foreground">Vulnerabilities</p>
                      <p className="text-3xl font-bold">{totalVulnerabilities}</p>
                    </div>
                    <Shield className="h-8 w-8 text-foxy-orange" />
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-muted-foreground">Critical Issues</p>
                      <p className="text-3xl font-bold text-severity-critical">{criticalCount}</p>
                    </div>
                    <TrendingDown className="h-8 w-8 text-severity-critical" />
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-muted-foreground">Last Scan</p>
                      <p className="text-lg font-medium">
                        {scans[0] ? formatDate(scans[0].created_at).split(",")[0] : "Never"}
                      </p>
                    </div>
                    <Clock className="h-8 w-8 text-muted-foreground" />
                  </div>
                </CardContent>
              </Card>
            </div>

            <StatsChart />

            <Card className="mt-8">
              <CardHeader>
                <CardTitle>Recent Scans</CardTitle>
              </CardHeader>
              <CardContent>
                {loading ? (
                  <p className="text-muted-foreground text-center py-8">Loading...</p>
                ) : scans.length === 0 ? (
                  <div className="text-center py-8">
                    <Shield className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                    <p className="text-muted-foreground">No scans yet</p>
                    <Link href="/scan">
                      <Button variant="outline" className="mt-4">Start your first scan</Button>
                    </Link>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {scans.map((scan, index) => (
                      <motion.div
                        key={scan.id}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: index * 0.05 }}
                      >
                        <Link href={`/scan/${scan.id}`}>
                          <div className="flex items-center justify-between p-4 rounded-lg border hover:bg-muted/50 transition-colors">
                            <div className="flex items-center gap-4">
                              <span className="text-2xl">🦊</span>
                              <div>
                                <p className="font-medium">{scan.source_path || `Scan #${scan.id}`}</p>
                                <p className="text-sm text-muted-foreground">{formatDate(scan.created_at)}</p>
                              </div>
                            </div>
                            <div className="flex items-center gap-4">
                              <div className="text-right">
                                <p className="font-medium">{scan.total_findings} issues</p>
                                <div className="flex gap-1">
                                  {scan.critical_count > 0 && <Badge variant="critical">{scan.critical_count} C</Badge>}
                                  {scan.high_count > 0 && <Badge variant="high">{scan.high_count} H</Badge>}
                                </div>
                              </div>
                              <Badge variant={scan.status === "completed" ? "default" : scan.status === "failed" ? "destructive" : "secondary"}>
                                {scan.status}
                              </Badge>
                            </div>
                          </div>
                        </Link>
                      </motion.div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </motion.div>
        </div>
      </main>
      <Footer />
    </div>
  )
}
