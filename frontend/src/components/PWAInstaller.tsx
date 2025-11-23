'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/shared/components/ui/button'

export function PWAInstaller() {
  const [deferredPrompt, setDeferredPrompt] = useState<any>(null)
  const [showInstallButton, setShowInstallButton] = useState(false)

  useEffect(() => {
    const handler = (e: Event) => {
      e.preventDefault()
      setDeferredPrompt(e)
      setShowInstallButton(true)
    }

    window.addEventListener('beforeinstallprompt', handler)

    return () => {
      window.removeEventListener('beforeinstallprompt', handler)
    }
  }, [])

  const handleInstallClick = async () => {
    if (!deferredPrompt) return

    deferredPrompt.prompt()
    const { outcome } = await deferredPrompt.userChoice
    
    if (outcome === 'accepted') {
      console.log('PWA instalado com sucesso')
    }
    
    setDeferredPrompt(null)
    setShowInstallButton(false)
  }

  if (!showInstallButton) return null

  return (
    <div className="fixed bottom-4 right-4 z-50">
      <div className="bg-white rounded-lg shadow-lg p-4 border border-gray-200 max-w-sm">
        <p className="text-sm text-gray-700 mb-3">
          📱 Instale o VigiaPix no seu celular para acesso rápido!
        </p>
        <div className="flex gap-2">
          <Button
            onClick={handleInstallClick}
            size="sm"
            className="flex-1"
          >
            Instalar App
          </Button>
          <Button
            onClick={() => setShowInstallButton(false)}
            variant="outline"
            size="sm"
          >
            Depois
          </Button>
        </div>
      </div>
    </div>
  )
}



