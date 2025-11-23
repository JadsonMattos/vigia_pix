'use client'

import { useEffect, useRef, useState } from 'react'

interface MapViewProps {
  address?: string
  latitude?: number
  longitude?: number
  height?: string
  zoom?: number
}

export function MapView({ 
  address, 
  latitude, 
  longitude, 
  height = '400px',
  zoom = 15 
}: MapViewProps) {
  const mapRef = useRef<HTMLDivElement>(null)
  const [mapLoaded, setMapLoaded] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!mapRef.current) return

    // Se temos coordenadas, usar diretamente
    if (latitude && longitude) {
      const iframe = document.createElement('iframe')
      iframe.width = '100%'
      iframe.height = height
      iframe.frameBorder = '0'
      iframe.style.border = '0'
      iframe.allowFullScreen = true
      iframe.loading = 'lazy'
      iframe.referrerPolicy = 'no-referrer-when-downgrade'
      
      // Usar OpenStreetMap (gratuito, sem chave)
      iframe.src = `https://www.openstreetmap.org/export/embed.html?bbox=${longitude - 0.01},${latitude - 0.01},${longitude + 0.01},${latitude + 0.01}&layer=mapnik&marker=${latitude},${longitude}`
      
      iframe.onload = () => setMapLoaded(true)
      iframe.onerror = () => setError('Erro ao carregar mapa')
      
      mapRef.current.innerHTML = ''
      mapRef.current.appendChild(iframe)
      
      return () => {
        if (mapRef.current) {
          mapRef.current.innerHTML = ''
        }
      }
    }
    
    // Se temos apenas endereço, usar geocoding via OpenStreetMap Nominatim
    if (address && !latitude && !longitude) {
      // Usar OpenStreetMap Nominatim para geocoding (gratuito, sem chave)
      fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(address)}&limit=1`, {
        headers: {
          'User-Agent': 'VigiaPix/1.0'
        }
      })
        .then(res => res.json())
        .then(data => {
          if (data && data.length > 0 && mapRef.current) {
            const lat = parseFloat(data[0].lat)
            const lon = parseFloat(data[0].lon)
            
            const iframe = document.createElement('iframe')
            iframe.width = '100%'
            iframe.height = height
            iframe.frameBorder = '0'
            iframe.style.border = '0'
            iframe.allowFullScreen = true
            iframe.loading = 'lazy'
            iframe.referrerPolicy = 'no-referrer-when-downgrade'
            iframe.src = `https://www.openstreetmap.org/export/embed.html?bbox=${lon - 0.01},${lat - 0.01},${lon + 0.01},${lat + 0.01}&layer=mapnik&marker=${lat},${lon}`
            iframe.onload = () => setMapLoaded(true)
            
            mapRef.current.innerHTML = ''
            mapRef.current.appendChild(iframe)
          } else {
            setError('Localização não encontrada')
          }
        })
        .catch(() => {
          // Fallback: usar link direto para Google Maps (sem chave)
          if (mapRef.current) {
            const iframe = document.createElement('iframe')
            iframe.width = '100%'
            iframe.height = height
            iframe.frameBorder = '0'
            iframe.style.border = '0'
            iframe.allowFullScreen = true
            iframe.loading = 'lazy'
            iframe.referrerPolicy = 'no-referrer-when-downgrade'
            iframe.src = `https://www.google.com/maps?q=${encodeURIComponent(address)}&output=embed`
            iframe.onload = () => setMapLoaded(true)
            
            mapRef.current.innerHTML = ''
            mapRef.current.appendChild(iframe)
          }
        })
      
      return
    }
  }, [address, latitude, longitude, height, zoom])

  if (error) {
    return (
      <div className="bg-gray-100 rounded-lg p-8 text-center" style={{ height }}>
        <p className="text-gray-600">⚠️ {error}</p>
        <p className="text-sm text-gray-500 mt-2">
          {address && `Endereço: ${address}`}
          {latitude && longitude && `Coordenadas: ${latitude}, ${longitude}`}
        </p>
      </div>
    )
  }

  if (!address && !latitude && !longitude) {
    return (
      <div className="bg-gray-100 rounded-lg p-8 text-center" style={{ height }}>
        <p className="text-gray-600">📍 Nenhuma localização disponível</p>
      </div>
    )
  }

  return (
    <div className="w-full rounded-lg overflow-hidden border border-gray-200 shadow-sm relative">
      <div ref={mapRef} style={{ width: '100%', height, minHeight: '200px' }} />
      {!mapLoaded && (
        <div className="absolute inset-0 bg-gray-100 flex items-center justify-center">
          <p className="text-gray-600">Carregando mapa...</p>
        </div>
      )}
    </div>
  )
}
