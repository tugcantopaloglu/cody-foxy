import { create } from "zustand"

export interface Finding {
  id: number
  rule_id: string
  rule_name: string
  severity: string
  file_path: string
  start_line: number
  end_line: number
  code_snippet: string
  message: string
  ai_explanation?: string
  ai_remediation?: string
  cwe_ids: string[]
  owasp_ids: string[]
}

export interface Scan {
  id: number
  status: string
  source_type: string
  source_path?: string
  languages_detected: string[]
  total_files: number
  files_scanned: number
  total_findings: number
  critical_count: number
  high_count: number
  medium_count: number
  low_count: number
  created_at: string
  started_at?: string
  completed_at?: string
  findings: Finding[]
}

interface ScanState {
  currentScan: Scan | null
  scans: Scan[]
  isScanning: boolean
  progress: number
  currentFile: string
  setCurrentScan: (scan: Scan | null) => void
  setScans: (scans: Scan[]) => void
  setIsScanning: (isScanning: boolean) => void
  setProgress: (progress: number) => void
  setCurrentFile: (file: string) => void
  updateScanStatus: (scanId: number, status: Partial<Scan>) => void
}

export const useScanStore = create<ScanState>((set) => ({
  currentScan: null,
  scans: [],
  isScanning: false,
  progress: 0,
  currentFile: "",
  setCurrentScan: (scan) => set({ currentScan: scan }),
  setScans: (scans) => set({ scans }),
  setIsScanning: (isScanning) => set({ isScanning }),
  setProgress: (progress) => set({ progress }),
  setCurrentFile: (currentFile) => set({ currentFile }),
  updateScanStatus: (scanId, status) =>
    set((state) => ({
      scans: state.scans.map((s) => (s.id === scanId ? { ...s, ...status } : s)),
      currentScan: state.currentScan?.id === scanId ? { ...state.currentScan, ...status } : state.currentScan,
    })),
}))
