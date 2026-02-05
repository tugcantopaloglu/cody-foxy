"use client"

import { motion } from "framer-motion"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Header } from "@/components/layout/header"
import { Footer } from "@/components/layout/footer"
import { FileUploader } from "@/components/scan/file-uploader"
import { GitHubScanner } from "@/components/scan/github-scanner"
import { Upload, Github } from "lucide-react"

export default function ScanPage() {
  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1 py-12">
        <div className="container max-w-4xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center mb-8"
          >
            <h1 className="text-3xl md:text-4xl font-bold mb-4">
              <span className="gradient-text">Scan Your Code</span>
            </h1>
            <p className="text-muted-foreground max-w-xl mx-auto">
              Upload a zip file or connect to GitHub to scan your code for security vulnerabilities
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <span className="text-2xl">🦊</span>
                  Choose Scan Method
                </CardTitle>
                <CardDescription>
                  Select how you want to provide your code for analysis
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Tabs defaultValue="upload" className="w-full">
                  <TabsList className="grid w-full grid-cols-2 mb-6">
                    <TabsTrigger value="upload" className="flex items-center gap-2">
                      <Upload className="h-4 w-4" />
                      Upload Files
                    </TabsTrigger>
                    <TabsTrigger value="github" className="flex items-center gap-2">
                      <Github className="h-4 w-4" />
                      GitHub Repo
                    </TabsTrigger>
                  </TabsList>
                  <TabsContent value="upload">
                    <FileUploader />
                  </TabsContent>
                  <TabsContent value="github">
                    <GitHubScanner />
                  </TabsContent>
                </Tabs>
              </CardContent>
            </Card>
          </motion.div>

          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
            className="mt-8 grid md:grid-cols-3 gap-4 text-center text-sm text-muted-foreground"
          >
            <div className="p-4 rounded-xl bg-muted/50">
              <p className="font-medium text-foreground mb-1">🔒 Private & Secure</p>
              <p>Your code is never stored after scanning</p>
            </div>
            <div className="p-4 rounded-xl bg-muted/50">
              <p className="font-medium text-foreground mb-1">⚡ Fast Analysis</p>
              <p>Results in under a minute for most repos</p>
            </div>
            <div className="p-4 rounded-xl bg-muted/50">
              <p className="font-medium text-foreground mb-1">🤖 AI Insights</p>
              <p>Get explanations and fixes from AI</p>
            </div>
          </motion.div>
        </div>
      </main>
      <Footer />
    </div>
  )
}
