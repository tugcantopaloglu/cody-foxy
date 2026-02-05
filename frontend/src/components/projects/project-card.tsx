"use client"

import Link from "next/link"
import { motion } from "framer-motion"
import { GitBranch, Clock, Shield, TrendingUp, TrendingDown, Minus, Settings } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { formatDate } from "@/lib/utils"

interface Project {
  id: number
  name: string
  slug: string
  description?: string
  team_id?: number
  owner_id: number
  repository_id?: number
  default_branch: string
  scan_on_push: boolean
  scan_on_pr: boolean
  fail_threshold: string
  last_scan_at?: string
  created_at: string
  stats?: {
    total_scans: number
    total_findings: number
    critical_count: number
    high_count: number
    trend: string
  }
}

interface ProjectCardProps {
  project: Project
  index?: number
}

const trendIcons = {
  improving: <TrendingDown className="h-4 w-4 text-green-500" />,
  worsening: <TrendingUp className="h-4 w-4 text-red-500" />,
  stable: <Minus className="h-4 w-4 text-muted-foreground" />,
}

export function ProjectCard({ project, index = 0 }: ProjectCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05 }}
    >
      <Link href={`/projects/${project.id}`}>
        <Card className="hover:border-foxy-orange/50 transition-all hover:shadow-lg">
          <CardHeader className="pb-2">
            <div className="flex items-start justify-between">
              <div className="flex items-center gap-2">
                <span className="text-2xl">🦊</span>
                <div>
                  <CardTitle className="text-lg">{project.name}</CardTitle>
                  <p className="text-sm text-muted-foreground">{project.description || "No description"}</p>
                </div>
              </div>
              <Button variant="ghost" size="icon" asChild onClick={(e) => e.stopPropagation()}>
                <Link href={`/projects/${project.id}/settings`}>
                  <Settings className="h-4 w-4" />
                </Link>
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-4 text-sm text-muted-foreground mb-4">
              <div className="flex items-center gap-1">
                <GitBranch className="h-4 w-4" />
                <span>{project.default_branch}</span>
              </div>
              <div className="flex items-center gap-1">
                <Clock className="h-4 w-4" />
                <span>{project.last_scan_at ? formatDate(project.last_scan_at) : "Never scanned"}</span>
              </div>
            </div>

            {project.stats && (
              <div className="grid grid-cols-4 gap-2">
                <div className="text-center p-2 rounded bg-muted/50">
                  <p className="text-xs text-muted-foreground">Scans</p>
                  <p className="text-lg font-bold">{project.stats.total_scans}</p>
                </div>
                <div className="text-center p-2 rounded bg-muted/50">
                  <p className="text-xs text-muted-foreground">Issues</p>
                  <p className="text-lg font-bold">{project.stats.total_findings}</p>
                </div>
                <div className="text-center p-2 rounded bg-severity-critical/10">
                  <p className="text-xs text-muted-foreground">Critical</p>
                  <p className="text-lg font-bold text-severity-critical">{project.stats.critical_count}</p>
                </div>
                <div className="text-center p-2 rounded bg-muted/50">
                  <p className="text-xs text-muted-foreground">Trend</p>
                  <div className="flex justify-center mt-1">
                    {trendIcons[project.stats.trend as keyof typeof trendIcons] || trendIcons.stable}
                  </div>
                </div>
              </div>
            )}

            <div className="flex items-center gap-2 mt-4">
              {project.scan_on_push && (
                <Badge variant="outline" className="text-xs">
                  Push Scan
                </Badge>
              )}
              {project.scan_on_pr && (
                <Badge variant="outline" className="text-xs">
                  PR Scan
                </Badge>
              )}
              <Badge variant={project.fail_threshold === "critical" ? "critical" : "default"} className="text-xs">
                Fail: {project.fail_threshold}
              </Badge>
            </div>
          </CardContent>
        </Card>
      </Link>
    </motion.div>
  )
}
