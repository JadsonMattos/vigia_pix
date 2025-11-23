'use client'

import { useState, useRef } from 'react'
import { Button } from '@/shared/components/ui/button'

interface PhotoUploadProps {
  emendaId: string
  onUploadSuccess?: (result: any) => void
  onUploadError?: (error: string) => void
}

export function PhotoUpload({ emendaId, onUploadSuccess, onUploadError }: PhotoUploadProps) {
  const [isUploading, setIsUploading] = useState(false)
  const [preview, setPreview] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const cameraInputRef = useRef<HTMLInputElement>(null)

  const handleFileSelect = async (file: File | null) => {
    if (!file) return

    // Preview
    const reader = new FileReader()
    reader.onloadend = () => {
      setPreview(reader.result as string)
    }
    reader.readAsDataURL(file)

    // Upload
    await uploadPhoto(file)
  }

  const uploadPhoto = async (file: File) => {
    setIsUploading(true)
    try {
      const formData = new FormData()
      formData.append('photo_file', file)
      formData.append('tipo', 'foto_obra')
      formData.append('validate_location', 'true')

      const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const response = await fetch(`${apiBaseUrl}/api/v1/emenda-pix/${emendaId}/upload-photo`, {
        method: 'POST',
        body: formData
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'Erro ao fazer upload')
      }

      const result = await response.json()
      onUploadSuccess?.(result)
      
      // Reset
      setPreview(null)
      if (fileInputRef.current) fileInputRef.current.value = ''
      if (cameraInputRef.current) cameraInputRef.current.value = ''
      
    } catch (error: any) {
      onUploadError?.(error.message || 'Erro ao fazer upload da foto')
    } finally {
      setIsUploading(false)
    }
  }

  const openCamera = () => {
    if (cameraInputRef.current) {
      cameraInputRef.current.click()
    }
  }

  const openFilePicker = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click()
    }
  }

  return (
    <div className="space-y-4">
      {/* Preview */}
      {preview && (
        <div className="relative">
          <img
            src={preview}
            alt="Preview"
            className="w-full max-w-md h-auto rounded-lg border border-gray-300"
          />
          <button
            onClick={() => setPreview(null)}
            className="absolute top-2 right-2 bg-red-500 text-white rounded-full w-8 h-8 flex items-center justify-center hover:bg-red-600"
          >
            ×
          </button>
        </div>
      )}

      {/* Upload Buttons */}
      <div className="flex flex-col sm:flex-row gap-3">
        {/* Camera Button (Mobile) */}
        <input
          ref={cameraInputRef}
          type="file"
          accept="image/*"
          capture="environment"
          className="hidden"
          onChange={(e) => handleFileSelect(e.target.files?.[0] || null)}
        />
        <Button
          onClick={openCamera}
          disabled={isUploading}
          className="flex-1 bg-blue-600 hover:bg-blue-700"
        >
          📷 {isUploading ? 'Enviando...' : 'Tirar Foto'}
        </Button>

        {/* File Picker Button */}
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          className="hidden"
          onChange={(e) => handleFileSelect(e.target.files?.[0] || null)}
        />
        <Button
          onClick={openFilePicker}
          disabled={isUploading}
          variant="outline"
          className="flex-1"
        >
          📁 {isUploading ? 'Enviando...' : 'Escolher Arquivo'}
        </Button>
      </div>

      {/* Info */}
      <p className="text-xs text-gray-500">
        📍 A foto será validada automaticamente com geofencing
      </p>
    </div>
  )
}

