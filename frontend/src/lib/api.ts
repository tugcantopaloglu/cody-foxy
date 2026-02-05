const API_BASE = process.env.NEXT_PUBLIC_API_URL || "/api"

export async function fetchApi<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const token = typeof window !== "undefined" ? localStorage.getItem("token") : null
  
  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
  })
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Request failed" }))
    throw new Error(error.detail || "Request failed")
  }
  
  return response.json()
}

export async function uploadFile(file: File, enableAi: boolean = true) {
  const token = typeof window !== "undefined" ? localStorage.getItem("token") : null
  const formData = new FormData()
  formData.append("file", file)
  
  const response = await fetch(`${API_BASE}/scans/upload?enable_ai=${enableAi}`, {
    method: "POST",
    headers: token ? { Authorization: `Bearer ${token}` } : {},
    body: formData,
  })
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Upload failed" }))
    throw new Error(error.detail || "Upload failed")
  }
  
  return response.json()
}

export async function scanGitHubRepo(repoUrl: string, branch: string = "main", enableAi: boolean = true) {
  return fetchApi("/scans/github", {
    method: "POST",
    body: JSON.stringify({ repo_url: repoUrl, branch, enable_ai: enableAi }),
  })
}

export async function getScan(scanId: number) {
  return fetchApi(`/scans/${scanId}`)
}

export async function getScanFindings(scanId: number, severity?: string) {
  const query = severity ? `?severity=${severity}` : ""
  return fetchApi(`/scans/${scanId}/findings${query}`)
}

export async function getScanSarif(scanId: number) {
  return fetchApi(`/scans/${scanId}/sarif`)
}

export async function getScans(limit: number = 20, offset: number = 0) {
  return fetchApi(`/scans/?limit=${limit}&offset=${offset}`)
}

export async function login(email: string, password: string) {
  return fetchApi("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  })
}

export async function register(email: string, username: string, password: string) {
  return fetchApi("/auth/register", {
    method: "POST",
    body: JSON.stringify({ email, username, password }),
  })
}

export async function githubAuth(code: string) {
  return fetchApi("/auth/github/callback", {
    method: "POST",
    body: JSON.stringify({ code }),
  })
}
