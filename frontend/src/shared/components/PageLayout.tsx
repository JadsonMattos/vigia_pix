'use client'

import { ReactNode } from 'react'

interface PageLayoutProps {
  children: ReactNode
  title?: string
  subtitle?: string
}

export function PageLayout({ children, title, subtitle }: PageLayoutProps) {
  return (
    <div className="min-h-screen bg-[#F3F4F6]">
      <div className="container mx-auto px-4 py-8 md:py-10 max-w-7xl">
        {(title || subtitle) && (
          <div className="mb-8">
            {title && (
              <h1 className="text-3xl md:text-4xl font-extrabold text-[#1F2937] mb-2">
                {title}
              </h1>
            )}
            {subtitle && (
              <p className="text-lg text-[#6B7280]">
                {subtitle}
              </p>
            )}
          </div>
        )}
        {children}
      </div>
    </div>
  )
}

