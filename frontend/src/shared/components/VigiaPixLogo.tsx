'use client'

import React, { useState } from 'react'
import Image from 'next/image'

interface VigiaPixLogoProps {
  className?: string
  showTagline?: boolean
  size?: 'sm' | 'md' | 'lg'
  showText?: boolean // Se deve mostrar o texto "VIGIA PIX" abaixo da logo
}

export function VigiaPixLogo({ 
  className = '', 
  showTagline = false, 
  size = 'md',
  showText = true
}: VigiaPixLogoProps) {
  const [imageError, setImageError] = useState(false)
  
  const sizeClasses = {
    sm: 'w-24 h-24',
    md: 'w-32 h-32',
    lg: 'w-48 h-48'
  }

  const textSizes = {
    sm: 'text-xl',
    md: 'text-2xl',
    lg: 'text-4xl'
  }

  const logoImagePath = '/logo.jpeg'
  
  return (
    <div className={`flex flex-col items-center ${className}`}>
      {/* Logo Icon - Usa imagem se disponível, senão usa SVG */}
      <div className={`${sizeClasses[size]} relative mb-4`}>
        {!imageError ? (
          <div className="w-full h-full rounded-2xl overflow-hidden shadow-lg">
            <Image
              src={logoImagePath}
              alt="VigiaPix Logo"
              width={200}
              height={200}
              className="w-full h-full object-contain rounded-2xl"
              onError={() => setImageError(true)}
              priority
            />
          </div>
        ) : (
          <SVGLogo />
        )}
      </div>

      {/* Texto VIGIA PIX - apenas se showText for true */}
      {showText && (
        <div className={`flex items-center ${textSizes[size]} font-bold mb-2`}>
          <span className="text-[#1E40AF]">VIGIA</span>
          <span className="text-[#10B981] flex items-center">
            P
            <span className="relative">
              I
              {/* Círculo verde com cifrão substituindo o ponto do I */}
              <span className="absolute -top-1 left-1/2 transform -translate-x-1/2 w-4 h-4 bg-[#10B981] rounded-full flex items-center justify-center">
                <span className="text-white text-xs font-bold">$</span>
              </span>
            </span>
            X
          </span>
        </div>
      )}

      {/* Tagline */}
      {showTagline && (
        <p className="text-gray-500 text-sm font-normal">
          FISCALIZANDO EMENDAS PIX
        </p>
      )}
    </div>
  )
}

// Componente SVG como fallback
function SVGLogo() {
  return (
    <svg
      viewBox="0 0 200 200"
      className="w-full h-full"
      xmlns="http://www.w3.org/2000/svg"
    >
      {/* Contorno azul claro */}
      <circle
        cx="100"
        cy="100"
        r="95"
        fill="none"
        stroke="#60A5FA"
        strokeWidth="2"
        opacity="0.3"
      />
      
      {/* QR Code verde (fundo) */}
      <g opacity="0.8">
        {/* Padrão de QR code simplificado */}
        <rect x="50" y="50" width="100" height="100" fill="#10B981" opacity="0.2" />
        {/* Quadrados do QR code */}
        <rect x="60" y="60" width="20" height="20" fill="#10B981" />
        <rect x="90" y="60" width="20" height="20" fill="#10B981" />
        <rect x="120" y="60" width="20" height="20" fill="#10B981" />
        <rect x="60" y="90" width="20" height="20" fill="#10B981" />
        <rect x="120" y="90" width="20" height="20" fill="#10B981" />
        <rect x="60" y="120" width="20" height="20" fill="#10B981" />
        <rect x="90" y="120" width="20" height="20" fill="#10B981" />
        <rect x="120" y="120" width="20" height="20" fill="#10B981" />
        {/* Pequenos quadrados */}
        <rect x="75" y="75" width="10" height="10" fill="#10B981" />
        <rect x="105" y="75" width="10" height="10" fill="#10B981" />
        <rect x="75" y="105" width="10" height="10" fill="#10B981" />
        <rect x="105" y="105" width="10" height="10" fill="#10B981" />
      </g>
      
      {/* Círculo verde com cifrão no QR code (canto inferior direito) */}
      <circle
        cx="160"
        cy="160"
        r="15"
        fill="#10B981"
      />
      <text
        x="160"
        y="167"
        textAnchor="middle"
        fill="white"
        fontSize="18"
        fontWeight="bold"
        fontFamily="Arial, sans-serif"
      >
        $
      </text>
      
      {/* Lupa azul escuro */}
      <g>
        {/* Cabo da lupa */}
        <rect
          x="140"
          y="140"
          width="8"
          height="25"
          fill="#1E40AF"
          transform="rotate(45 144 152.5)"
        />
        {/* Aro da lupa */}
        <circle
          cx="100"
          cy="100"
          r="45"
          fill="none"
          stroke="#1E40AF"
          strokeWidth="6"
        />
        {/* Lente azul claro transparente */}
        <circle
          cx="100"
          cy="100"
          r="40"
          fill="#60A5FA"
          opacity="0.3"
        />
      </g>
    </svg>
  )
}
