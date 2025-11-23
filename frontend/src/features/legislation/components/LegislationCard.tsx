'use client'

import { Legislation } from '@/shared/types'
import { Button } from '@/shared/components/ui/button'
import { formatDate } from '@/shared/utils'

interface LegislationCardProps {
  legislation: Legislation
  onViewDetails?: (id: string) => void
  onSendMessage?: (id: string, title: string, deputyName?: string) => void
}

export function LegislationCard({ 
  legislation, 
  onViewDetails,
  onSendMessage 
}: LegislationCardProps) {
  return (
    <div className="bg-white rounded-lg shadow-md border border-gray-200">
      <div className="p-6 border-b border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900">{legislation.title}</h3>
        <p className="text-sm text-gray-500">
          {legislation.author} • {formatDate(legislation.created_at)}
        </p>
      </div>
      <div className="p-6">
        <p className="text-sm text-gray-600 line-clamp-3">
          {legislation.simplified_content || legislation.content.substring(0, 200)}...
        </p>
        <div className="mt-2 flex gap-2 flex-wrap">
          <span className="inline-block px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded">
            {legislation.status}
          </span>
          {legislation.simplified_content && (
            <span className="inline-block px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded">
              ✓ Simplificado
            </span>
          )}
        </div>
      </div>
      <div className="p-6 border-t border-gray-200 flex gap-2">
        <Button
          variant="outline"
          size="sm"
          onClick={() => onViewDetails?.(legislation.id)}
        >
          Ver Detalhes
        </Button>
        <Button
          variant="primary"
          size="sm"
          onClick={() => {
            if (onSendMessage) {
              onSendMessage(legislation.id, legislation.title, legislation.author)
            } else {
              alert('Funcionalidade de envio de mensagem não disponível nesta página. Use o Dashboard.')
            }
          }}
          className="flex-1"
        >
          📢 Enviar Mensagem
        </Button>
      </div>
    </div>
  )
}



