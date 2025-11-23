'use client'

import { useState } from 'react'
import { useLegislations } from '@/features/legislation/hooks/useLegislations'
import { LegislationList } from '@/features/legislation/components/LegislationList'
import { Button } from '@/shared/components/ui/button'

export default function LegislationPage() {
  const [page, setPage] = useState(0)
  const limit = 12
  const offset = page * limit

  const { data, isLoading, error } = useLegislations({ limit, offset })

  const handleViewDetails = (id: string) => {
    window.location.href = `/legislation/${id}`
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
        <div className="container mx-auto px-4 py-8">
          <div className="text-center py-12">
            <div className="text-6xl mb-4">❌</div>
            <p className="text-red-500 text-lg">Erro ao carregar legislações</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-[#F3F4F6]">
      <div className="container mx-auto px-4 sm:px-5 md:px-6 lg:px-8 py-6 sm:py-8 md:py-10 lg:py-12 max-w-7xl">
        {/* Header Melhorado */}
        <div className="mb-6 sm:mb-8 md:mb-12">
          <h1 className="text-2xl sm:text-3xl md:text-4xl font-extrabold text-[#1F2937] mb-2">
            📜 Legislações
          </h1>
          <p className="text-sm sm:text-base md:text-lg text-[#6B7280] max-w-2xl">
            Explore as propostas legislativas em tramitação e simplifique textos complexos com IA
          </p>
        </div>

        <LegislationList
          legislations={data?.items || []}
          onViewDetails={handleViewDetails}
          isLoading={isLoading}
        />

        {/* Pagination Melhorado */}
        {data && data.items.length > 0 && (
          <div className="mt-8 flex justify-center gap-4">
            <Button
              variant="outline"
              onClick={() => setPage(p => Math.max(0, p - 1))}
              disabled={page === 0}
              className="px-6 py-2 border-2 hover:bg-gray-50"
            >
              ← Anterior
            </Button>
            <span className="flex items-center px-6 py-2 bg-white rounded-lg border-2 border-gray-200 font-semibold text-gray-700">
              Página {page + 1}
            </span>
            <Button
              variant="outline"
              onClick={() => setPage(p => p + 1)}
              disabled={data.items.length < limit}
              className="px-6 py-2 border-2 hover:bg-gray-50"
            >
              Próxima →
            </Button>
          </div>
        )}
      </div>
    </div>
  )
}
