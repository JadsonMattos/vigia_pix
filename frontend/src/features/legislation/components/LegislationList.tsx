'use client'

import { Legislation } from '@/shared/types'
import { LegislationCard } from './LegislationCard'

interface LegislationListProps {
  legislations: Legislation[]
  onViewDetails?: (id: string) => void
  onSendMessage?: (id: string, title: string, deputyName?: string) => void
  isLoading?: boolean
}

export function LegislationList({ 
  legislations, 
  onViewDetails,
  onSendMessage,
  isLoading = false 
}: LegislationListProps) {
  if (isLoading) {
    return (
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {[1, 2, 3, 4, 5, 6].map((i) => (
          <div key={i} className="bg-gray-200 animate-pulse rounded-lg h-64" />
        ))}
      </div>
    )
  }

  if (legislations.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500 text-lg">Nenhuma legislação encontrada</p>
      </div>
    )
  }

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      {legislations.map((legislation) => (
        <LegislationCard
          key={legislation.id}
          legislation={legislation}
          onViewDetails={onViewDetails}
          onSendMessage={onSendMessage}
        />
      ))}
    </div>
  )
}



