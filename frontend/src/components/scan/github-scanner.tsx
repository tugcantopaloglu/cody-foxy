"use client"

import { useState } from "react"
import { Github, Loader2, ArrowRight } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { scanGitHubRepo } from "@/lib/api"
import { useScanStore } from "@/store/scan-store"
import { useRouter } from "next/navigation"
import { useToast } from "@/hooks/use-toast"

export function GitHubScanner() {
  const [repoUrl, setRepoUrl] = useState("")
  const [branch, setBranch] = useState("main")
  const [isScanning, setIsScanning] = useState(false)
  const { setCurrentScan } = useScanStore()
  const router = useRouter()
  const { toast } = useToast()

  const handleScan = async () => {
    if (!repoUrl) {
      toast({ title: "Enter repository URL", variant: "destructive" })
      return
    }

    setIsScanning(true)
    try {
      const scan = await scanGitHubRepo(repoUrl, branch, true)
      setCurrentScan(scan as any)
      toast({ title: "Scan started", description: "Analyzing repository..." })
      router.push(`/scan/${scan.id}`)
    } catch (error: any) {
      toast({ title: "Scan failed", description: error.message, variant: "destructive" })
    } finally {
      setIsScanning(false)
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3 p-4 bg-muted rounded-xl">
        <Github className="h-8 w-8 text-foxy-orange" />
        <div>
          <p className="font-medium">Scan GitHub Repository</p>
          <p className="text-sm text-muted-foreground">Enter a public repo URL or connect your account</p>
        </div>
      </div>
      <div className="space-y-3">
        <Input
          placeholder="https://github.com/owner/repo"
          value={repoUrl}
          onChange={(e) => setRepoUrl(e.target.value)}
          className="h-12"
        />
        <div className="flex gap-3">
          <Input
            placeholder="Branch (default: main)"
            value={branch}
            onChange={(e) => setBranch(e.target.value)}
            className="h-12 flex-1"
          />
          <Button
            onClick={handleScan}
            disabled={isScanning || !repoUrl}
            className="h-12 px-8"
            variant="gradient"
          >
            {isScanning ? (
              <Loader2 className="h-5 w-5 animate-spin" />
            ) : (
              <>
                Scan <ArrowRight className="ml-2 h-5 w-5" />
              </>
            )}
          </Button>
        </div>
      </div>
    </div>
  )
}
