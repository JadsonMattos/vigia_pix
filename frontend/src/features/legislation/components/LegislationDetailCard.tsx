'use client'

import { Legislation } from '@/shared/types'
import { Button } from '@/shared/components/ui/button'
import { formatDate } from '@/shared/utils'

interface LegislationDetailCardProps {
  legislation: Legislation
  onSendMessage?: (id: string, title: string, deputyName?: string) => void
}

export function LegislationDetailCard({ legislation, onSendMessage }: LegislationDetailCardProps) {
  return (
    <div className="bg-white rounded-lg shadow-md border border-gray-200">
      <div className="p-6 border-b border-gray-200">
        <h2 className="text-2xl font-semibold text-gray-900">{legislation.title}</h2>
        <div className="flex flex-wrap gap-4 text-sm text-gray-500 mt-2">
          <span>Autor: {legislation.author}</span>
          <span>•</span>
          <span>{formatDate(legislation.created_at)}</span>
          <span>•</span>
          <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded">
            {legislation.status}
          </span>
        </div>
      </div>
      <div className="p-6">
        <div className="space-y-4">
          <div>
            <h3 className="font-semibold mb-2">Conteúdo Original</h3>
            <div className="bg-gray-50 p-4 rounded-lg text-sm text-gray-700 whitespace-pre-wrap max-h-64 overflow-y-auto">
              {legislation.content}
            </div>
          </div>
          
          {legislation.simplified_content && (
            <div>
              <h3 className="font-semibold mb-2">Versão Simplificada</h3>
              <div className="bg-green-50 p-4 rounded-lg text-sm text-gray-700 whitespace-pre-wrap">
                {legislation.simplified_content}
              </div>
              <p className="text-xs text-gray-500 mt-2">
                Redução de {legislation.original_length && legislation.simplified_length
                  ? Math.round((1 - legislation.simplified_length / legislation.original_length) * 100)
                  : 0}% no tamanho do texto
              </p>
            </div>
          )}
        </div>
      </div>
      <div className="p-6 border-t border-gray-200 flex gap-2">
        <Button
          variant="primary"
          onClick={() => onSendMessage?.(legislation.id, legislation.title, legislation.author)}
          className="flex-1"
        >
          📢 Enviar Mensagem ao Deputado
        </Button>
      </div>
    </div>
  )
}

