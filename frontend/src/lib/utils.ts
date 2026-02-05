import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatDate(date: string | Date) {
  return new Intl.DateTimeFormat("en-US", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(date))
}

export function getSeverityColor(severity: string) {
  const colors: Record<string, string> = {
    critical: "text-severity-critical bg-severity-critical/10 border-severity-critical/30",
    high: "text-severity-high bg-severity-high/10 border-severity-high/30",
    medium: "text-severity-medium bg-severity-medium/10 border-severity-medium/30",
    low: "text-severity-low bg-severity-low/10 border-severity-low/30",
    info: "text-severity-info bg-severity-info/10 border-severity-info/30",
  }
  return colors[severity.toLowerCase()] || colors.info
}

export function getSeverityIcon(severity: string) {
  const icons: Record<string, string> = {
    critical: "🔴",
    high: "🟠",
    medium: "🟡",
    low: "🟢",
    info: "⚪",
  }
  return icons[severity.toLowerCase()] || "⚪"
}
