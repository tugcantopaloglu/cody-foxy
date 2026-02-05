"use client"

import { useCallback, useState } from "react"
import { useDropzone } from "react-dropzone"
import { Upload, FileArchive, Loader2 } from "lucide-react"
import { motion, AnimatePresence } from "framer-motion"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { uploadFile } from "@/lib/api"
import { useScanStore } from "@/store/scan-store"
import { useRouter } from "next/navigation"
import { useToast } from "@/hooks/use-toast"

export function FileUploader() {
  const [isUploading, setIsUploading] = useState(false)
  const { setCurrentScan, setIsScanning } = useScanStore()
  const router = useRouter()
  const { toast } = useToast()

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0]
    if (!file) return

    setIsUploading(true)
    setIsScanning(true)

    try {
      const scan = await uploadFile(file, true)
      setCurrentScan(scan)
      toast({ title: "Scan started", description: "Your code is being analyzed..." })
      router.push(`/scan/${scan.id}`)
    } catch (error: any) {
      toast({ title: "Upload failed", description: error.message, variant: "destructive" })
      setIsScanning(false)
    } finally {
      setIsUploading(false)
    }
  }, [setCurrentScan, setIsScanning, router, toast])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "application/zip": [".zip"],
      "application/gzip": [".tar.gz", ".tgz"],
    },
    maxFiles: 1,
    disabled: isUploading,
  })

  return (
    <div
      {...getRootProps()}
      className={cn(
        "relative border-2 border-dashed rounded-2xl p-12 transition-all duration-300 cursor-pointer",
        isDragActive
          ? "border-foxy-orange bg-foxy-orange/5 scale-[1.02]"
          : "border-muted-foreground/25 hover:border-foxy-orange/50 hover:bg-muted/50",
        isUploading && "pointer-events-none opacity-60"
      )}
    >
      <input {...getInputProps()} />
      <AnimatePresence mode="wait">
        {isUploading ? (
          <motion.div
            key="uploading"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="flex flex-col items-center gap-4"
          >
            <Loader2 className="h-16 w-16 text-foxy-orange animate-spin" />
            <div className="text-center">
              <p className="text-xl font-semibold">Analyzing your code...</p>
              <p className="text-muted-foreground">This may take a few moments</p>
            </div>
          </motion.div>
        ) : (
          <motion.div
            key="idle"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="flex flex-col items-center gap-4"
          >
            <div className="relative">
              <div className="absolute inset-0 bg-foxy-orange/20 blur-2xl rounded-full" />
              <div className="relative bg-gradient-to-br from-foxy-orange to-foxy-red p-6 rounded-2xl">
                {isDragActive ? (
                  <FileArchive className="h-12 w-12 text-white" />
                ) : (
                  <Upload className="h-12 w-12 text-white" />
                )}
              </div>
            </div>
            <div className="text-center">
              <p className="text-xl font-semibold">
                {isDragActive ? "Drop your code here" : "Drag & drop your code"}
              </p>
              <p className="text-muted-foreground mt-1">
                or click to browse • Supports .zip, .tar.gz
              </p>
            </div>
            <Button variant="outline" className="mt-2">
              Browse Files
            </Button>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
