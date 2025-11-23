'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useEffect, useState } from 'react'
import Image from 'next/image'

export function Navigation() {
  const pathname = usePathname()
  const [mounted, setMounted] = useState(false)
  const [logoError, setLogoError] = useState(false)
  const isLandingPage = pathname === '/'

  useEffect(() => {
    setMounted(true)
  }, [])

  // Navegação para Landing Page (dark, fixa, com blur)
  if (isLandingPage) {
    return (
      <nav className="fixed top-0 w-full z-50 bg-[rgba(2,6,23,0.85)] backdrop-blur-[12px] border-b border-white/10 py-4">
        <div className="container mx-auto px-5 flex justify-between items-center">
          <Link href="/" className="flex items-center gap-2 hover:opacity-80 transition-opacity">
            {!logoError && mounted ? (
              <div className="relative w-32 h-8 md:w-40 md:h-10 rounded-xl overflow-hidden">
                <Image
                  src="/logo.jpeg"
                  alt="VigiaPix"
                  fill
                  className="object-contain rounded-xl"
                  onError={() => setLogoError(true)}
                />
              </div>
            ) : (
              <div className="text-xl md:text-2xl font-extrabold text-white flex items-center gap-2">
                <i className="fa-solid fa-link"></i>
                <span>VigiaPix</span>
              </div>
            )}
          </Link>
          <div className="hidden md:flex gap-8 items-center">
            <Link href="#problema" className="text-[#94a3b8] hover:text-white text-sm font-medium transition-colors">
              O Gap
            </Link>
            <Link href="#solucao" className="text-[#94a3b8] hover:text-white text-sm font-medium transition-colors">
              Triangulação
            </Link>
            <Link 
              href="/triangulacao" 
              className="inline-flex items-center gap-2 px-6 py-2 bg-[#3b82f6] hover:bg-[#2563EB] text-white font-semibold rounded-lg shadow-lg hover:shadow-xl transition-all text-sm"
            >
              Acessar Sistema
            </Link>
          </div>
        </div>
      </nav>
    )
  }

  // Navegação para outras páginas (clean, branca)
  if (!mounted) {
    return (
      <nav className="bg-white shadow-sm border-b">
        <div className="container mx-auto px-4 py-4">
          <div className="flex justify-between items-center">
            <div className="h-8 w-32 bg-gray-200 animate-pulse rounded" />
            <div className="flex gap-4">
              <div className="h-6 w-20 bg-gray-200 animate-pulse rounded" />
              <div className="h-6 w-24 bg-gray-200 animate-pulse rounded" />
            </div>
          </div>
        </div>
      </nav>
    )
  }

  return (
    <nav className="bg-white shadow-sm border-b sticky top-0 z-40">
      <div className="container mx-auto px-4 py-4">
        <div className="flex justify-between items-center">
          <Link href="/" className="flex items-center gap-2 hover:opacity-80 transition-opacity">
            {!logoError ? (
              <div className="relative w-56 h-14 md:w-64 md:h-16 lg:w-72 lg:h-18 rounded-xl overflow-hidden">
                <Image
                  src="/logo.jpeg"
                  alt="VigiaPix"
                  fill
                  className="object-contain rounded-xl"
                  onError={() => setLogoError(true)}
                />
              </div>
            ) : (
              <div className="flex items-center text-xl md:text-2xl font-bold">
                <span className="text-[#1E40AF]">VIGIA</span>
                <span className="text-[#10B981] flex items-center">
                  P
                  <span className="relative">
                    I
                    <span className="absolute -top-0.5 left-1/2 transform -translate-x-1/2 w-3 h-3 bg-[#10B981] rounded-full flex items-center justify-center">
                      <span className="text-white text-[8px] font-bold">$</span>
                    </span>
                  </span>
                  X
                </span>
              </div>
            )}
          </Link>
          <div className="hidden md:flex gap-6 items-center">
            <Link 
              href="/dashboard" 
              className={`text-sm font-medium transition-colors ${
                pathname === '/dashboard' ? 'text-[#3b82f6]' : 'text-gray-700 hover:text-[#3b82f6]'
              }`}
            >
              Dashboard
            </Link>
            <Link 
              href="/legislation" 
              className={`text-sm font-medium transition-colors ${
                pathname?.startsWith('/legislation') ? 'text-[#3b82f6]' : 'text-gray-700 hover:text-[#3b82f6]'
              }`}
            >
              Legislações
            </Link>
            <Link 
              href="/emenda-pix" 
              className={`text-sm font-medium transition-colors ${
                pathname?.startsWith('/emenda-pix') ? 'text-[#3b82f6]' : 'text-gray-700 hover:text-[#3b82f6]'
              }`}
            >
              Emenda Pix
            </Link>
            <Link 
              href="/placar-transparencia" 
              className={`text-sm font-medium transition-colors ${
                pathname === '/placar-transparencia' ? 'text-[#3b82f6]' : 'text-gray-700 hover:text-[#3b82f6]'
              }`}
            >
              Placar
            </Link>
            <Link 
              href="/triangulacao" 
              className={`text-sm font-medium transition-colors ${
                pathname === '/triangulacao' ? 'text-[#3b82f6]' : 'text-gray-700 hover:text-[#3b82f6]'
              }`}
            >
              Triangulação
            </Link>
            <Link 
              href="/whatsapp-simulator" 
              className={`text-sm font-medium transition-colors ${
                pathname === '/whatsapp-simulator' ? 'text-[#3b82f6]' : 'text-gray-700 hover:text-[#3b82f6]'
              }`}
            >
              WhatsApp
            </Link>
          </div>
          {/* Mobile menu button */}
          <button className="md:hidden text-gray-700" aria-label="Menu">
            <i className="fa-solid fa-bars text-xl"></i>
          </button>
        </div>
      </div>
    </nav>
  )
}
