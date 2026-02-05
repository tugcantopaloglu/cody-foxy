"use client"

import Link from "next/link"
import { motion } from "framer-motion"
import { ArrowRight, Shield, Zap, Github, Code2, Brain, CheckCircle } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Header } from "@/components/layout/header"
import { Footer } from "@/components/layout/footer"

const features = [
  { icon: <Shield className="h-6 w-6" />, title: "Multi-Language Support", description: "Scan Python, JavaScript, Go, Java, and more with our advanced detection engine" },
  { icon: <Brain className="h-6 w-6" />, title: "AI-Powered Analysis", description: "Get intelligent explanations and remediation advice from GPT-4 or Claude" },
  { icon: <Github className="h-6 w-6" />, title: "GitHub Integration", description: "Connect your repos and scan directly from GitHub with one click" },
  { icon: <Zap className="h-6 w-6" />, title: "Real-time Scanning", description: "Watch vulnerabilities appear as they're found with WebSocket updates" },
  { icon: <Code2 className="h-6 w-6" />, title: "CI/CD Ready", description: "Integrate into GitHub Actions, GitLab CI, and any pipeline with SARIF output" },
  { icon: <CheckCircle className="h-6 w-6" />, title: "OWASP & CWE", description: "Full mapping to industry standards for compliance and prioritization" },
]

export default function HomePage() {
  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1">
        <section className="relative py-20 md:py-32 overflow-hidden">
          <div className="absolute inset-0 gradient-bg" />
          <div className="absolute inset-0">
            <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-foxy-orange/20 rounded-full blur-[100px] animate-pulse" />
            <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-foxy-purple/20 rounded-full blur-[100px] animate-pulse delay-1000" />
          </div>
          <div className="container relative">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              className="text-center max-w-4xl mx-auto"
            >
              <div className="inline-flex items-center gap-2 bg-foxy-orange/10 border border-foxy-orange/30 rounded-full px-4 py-2 mb-6">
                <span className="text-2xl animate-float">🦊</span>
                <span className="text-sm font-medium text-foxy-orange">AI-Powered Security Scanner</span>
              </div>
              <h1 className="text-4xl md:text-6xl lg:text-7xl font-bold mb-6">
                Find vulnerabilities
                <br />
                <span className="gradient-text">before they find you</span>
              </h1>
              <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
                Cody Foxy scans your code for security issues and uses AI to explain
                vulnerabilities and suggest fixes. It&apos;s like having a security expert on your team.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Link href="/scan">
                  <Button size="xl" variant="gradient" className="glow-orange">
                    Start Scanning <ArrowRight className="ml-2 h-5 w-5" />
                  </Button>
                </Link>
                <Link href="https://github.com/tugcantopaloglu/cody-foxy" target="_blank">
                  <Button size="xl" variant="outline">
                    <Github className="mr-2 h-5 w-5" /> View on GitHub
                  </Button>
                </Link>
              </div>
            </motion.div>
          </div>
        </section>

        <section className="py-20 container">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">Everything you need for secure code</h2>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              Powerful features to help you find, understand, and fix security vulnerabilities
            </p>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature, index) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                viewport={{ once: true }}
              >
                <Card className="h-full hover:shadow-lg hover:shadow-foxy-orange/10 transition-all hover:-translate-y-1">
                  <CardContent className="p-6">
                    <div className="w-12 h-12 bg-foxy-orange/10 rounded-xl flex items-center justify-center text-foxy-orange mb-4">
                      {feature.icon}
                    </div>
                    <h3 className="font-semibold text-lg mb-2">{feature.title}</h3>
                    <p className="text-muted-foreground">{feature.description}</p>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </section>

        <section className="py-20 bg-muted/50">
          <div className="container">
            <div className="text-center max-w-3xl mx-auto">
              <h2 className="text-3xl md:text-4xl font-bold mb-4">Ready to secure your code?</h2>
              <p className="text-muted-foreground mb-8">
                Start scanning in seconds. No signup required for public repositories.
              </p>
              <Link href="/scan">
                <Button size="xl" variant="gradient">
                  Scan Your Code Now <ArrowRight className="ml-2 h-5 w-5" />
                </Button>
              </Link>
            </div>
          </div>
        </section>
      </main>
      <Footer />
    </div>
  )
}
