"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { motion } from "framer-motion"
import { ArrowLeft, GitBranch, Shield, Bell, Zap } from "lucide-react"
import Link from "next/link"
import { Header } from "@/components/layout/header"
import { Footer } from "@/components/layout/footer"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Switch } from "@/components/ui/switch"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { TeamSelector } from "@/components/projects/team-selector"
import { useToast } from "@/hooks/use-toast"

export default function NewProjectPage() {
  const router = useRouter()
  const { toast } = useToast()
  const [loading, setLoading] = useState(false)

  const [formData, setFormData] = useState({
    name: "",
    description: "",
    team_id: undefined as number | undefined,
    default_branch: "main",
    scan_on_push: true,
    scan_on_pr: true,
    fail_threshold: "high",
    repository_url: "",
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      const res = await fetch("/api/projects/projects", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      })

      if (res.ok) {
        const project = await res.json()
        toast({
          title: "Project created",
          description: `${formData.name} has been created successfully.`,
        })
        router.push(`/projects/${project.id}`)
      } else {
        const error = await res.json()
        toast({
          title: "Error",
          description: error.detail || "Failed to create project",
          variant: "destructive",
        })
      }
    } catch (err) {
      toast({
        title: "Error",
        description: "Something went wrong",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1 py-12">
        <div className="container max-w-2xl">
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
            <Link href="/projects" className="inline-flex items-center text-muted-foreground hover:text-foreground mb-6">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Projects
            </Link>

            <div className="mb-8">
              <h1 className="text-3xl font-bold">Create Project</h1>
              <p className="text-muted-foreground">Set up a new security scanning project</p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Project Details</CardTitle>
                  <CardDescription>Basic information about your project</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="name">Project Name *</Label>
                    <Input
                      id="name"
                      value={formData.name}
                      onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                      placeholder="My Awesome Project"
                      required
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="description">Description</Label>
                    <Textarea
                      id="description"
                      value={formData.description}
                      onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                      placeholder="What does this project do?"
                      rows={3}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label>Team</Label>
                    <TeamSelector
                      value={formData.team_id}
                      onChange={(teamId) => setFormData({ ...formData, team_id: teamId })}
                    />
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <GitBranch className="h-5 w-5" />
                    Repository Settings
                  </CardTitle>
                  <CardDescription>Configure your repository connection</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="repository_url">Repository URL (optional)</Label>
                    <Input
                      id="repository_url"
                      value={formData.repository_url}
                      onChange={(e) => setFormData({ ...formData, repository_url: e.target.value })}
                      placeholder="https://github.com/owner/repo"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="default_branch">Default Branch</Label>
                    <Input
                      id="default_branch"
                      value={formData.default_branch}
                      onChange={(e) => setFormData({ ...formData, default_branch: e.target.value })}
                      placeholder="main"
                    />
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Zap className="h-5 w-5" />
                    Automation
                  </CardTitle>
                  <CardDescription>Configure automatic scanning triggers</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>Scan on Push</Label>
                      <p className="text-sm text-muted-foreground">
                        Automatically scan when code is pushed to the default branch
                      </p>
                    </div>
                    <Switch
                      checked={formData.scan_on_push}
                      onCheckedChange={(checked) => setFormData({ ...formData, scan_on_push: checked })}
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>Scan on Pull Request</Label>
                      <p className="text-sm text-muted-foreground">
                        Automatically scan when a PR is opened or updated
                      </p>
                    </div>
                    <Switch
                      checked={formData.scan_on_pr}
                      onCheckedChange={(checked) => setFormData({ ...formData, scan_on_pr: checked })}
                    />
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Shield className="h-5 w-5" />
                    Security Policy
                  </CardTitle>
                  <CardDescription>Configure security thresholds and notifications</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="fail_threshold">Fail Threshold</Label>
                    <p className="text-sm text-muted-foreground mb-2">
                      PR checks will fail if issues at or above this severity are found
                    </p>
                    <Select
                      value={formData.fail_threshold}
                      onValueChange={(value) => setFormData({ ...formData, fail_threshold: value })}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="critical">Critical only</SelectItem>
                        <SelectItem value="high">High and above</SelectItem>
                        <SelectItem value="medium">Medium and above</SelectItem>
                        <SelectItem value="low">All issues</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </CardContent>
              </Card>

              <div className="flex justify-end gap-4">
                <Link href="/projects">
                  <Button type="button" variant="outline">
                    Cancel
                  </Button>
                </Link>
                <Button type="submit" variant="gradient" disabled={loading || !formData.name.trim()}>
                  {loading ? "Creating..." : "Create Project"}
                </Button>
              </div>
            </form>
          </motion.div>
        </div>
      </main>
      <Footer />
    </div>
  )
}
