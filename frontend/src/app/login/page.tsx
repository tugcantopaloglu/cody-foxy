"use client"

import { useState, type FormEvent } from "react"
import { useRouter } from "next/navigation"
import { login, register } from "@/lib/api"
import { Header } from "@/components/layout/header"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export default function LoginPage() {
  const router = useRouter()
  const [creatingAccount, setCreatingAccount] = useState(false)
  const [email, setEmail] = useState("")
  const [username, setUsername] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState("")
  const [submitting, setSubmitting] = useState(false)

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError("")
    setSubmitting(true)
    try {
      const response = creatingAccount
        ? await register(email, username, password)
        : await login(email, password)
      localStorage.setItem("token", response.access_token)
      router.push("/scan")
    } catch (failure) {
      setError(failure instanceof Error ? failure.message : "Sign in failed")
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <>
      <Header />
      <main className="container max-w-md py-12">
        <Card>
          <CardHeader><CardTitle>{creatingAccount ? "Create account" : "Sign in"}</CardTitle></CardHeader>
          <CardContent>
            <form onSubmit={submit} className="space-y-4">
              <label className="block space-y-2">
                <span>Email</span>
                <Input type="email" autoComplete="email" value={email} onChange={(event) => setEmail(event.target.value)} required />
              </label>
              {creatingAccount && (
                <label className="block space-y-2">
                  <span>Username</span>
                  <Input autoComplete="username" value={username} onChange={(event) => setUsername(event.target.value)} required />
                </label>
              )}
              <label className="block space-y-2">
                <span>Password</span>
                <Input type="password" autoComplete={creatingAccount ? "new-password" : "current-password"} value={password} onChange={(event) => setPassword(event.target.value)} required />
              </label>
              {error && <p role="alert" className="text-destructive">{error}</p>}
              <Button type="submit" disabled={submitting} className="w-full">
                {submitting ? "Please wait" : creatingAccount ? "Create account" : "Sign in"}
              </Button>
            </form>
            <Button variant="link" className="mt-4" onClick={() => { setCreatingAccount(!creatingAccount); setError("") }}>
              {creatingAccount ? "Use an existing account" : "Create an account"}
            </Button>
          </CardContent>
        </Card>
      </main>
    </>
  )
}
