'use client'

import Link from 'next/link'
import { EmendaPix } from '@/features/emenda-pix/hooks/useEmendasPix'

interface PlacarCardProps {
  emenda: EmendaPix
}

export function PlacarCard({ emenda }: PlacarCardProps) {
  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
      minimumFractionDigits: 0
    }).format(value)
  }

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      'pendente': 'bg-gray-100 text-gray-800',
      'em_execucao': 'bg-blue-100 text-blue-800',
      'concluida': 'bg-green-100 text-green-800',
      'atrasada': 'bg-red-100 text-red-800',
      'cancelada': 'bg-gray-100 text-gray-800'
    }
    return colors[status] || 'bg-gray-100 text-gray-800'
  }

  const getStatusLabel = (status: string) => {
    const labels: Record<string, string> = {
      'pendente': 'Pendente',
      'em_execucao': 'Em Execução',
      'concluida': 'Concluída',
      'atrasada': 'Atrasada',
      'cancelada': 'Cancelada'
    }
    return labels[status] || status
  }

  const getSeverityColor = (severidade: string) => {
    const colors: Record<string, string> = {
      'alta': 'bg-red-100 text-red-800 border-red-300',
      'media': 'bg-yellow-100 text-yellow-800 border-yellow-300',
      'baixa': 'bg-blue-100 text-blue-800 border-blue-300'
    }
    return colors[severidade] || 'bg-gray-100 text-gray-800 border-gray-300'
  }

  const alertasAlta = emenda.alertas?.filter(a => a.severidade === 'alta') || []
  const alertasMedia = emenda.alertas?.filter(a => a.severidade === 'media') || []
  const totalAlertas = alertasAlta.length + alertasMedia.length

  return (
    <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow border border-gray-200">
      {/* Header */}
      <div className="flex justify-between items-start mb-4">
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-gray-900 mb-1">
            {emenda.autor_nome}
            {emenda.autor_partido && (
              <span className="text-sm text-gray-500 ml-2">
                ({emenda.autor_partido})
              </span>
            )}
          </h3>
          <p className="text-sm text-gray-600">
            {emenda.destinatario_nome}
            {emenda.destinatario_uf && (
              <span className="ml-1">- {emenda.destinatario_uf}</span>
            )}
          </p>
        </div>
        <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(emenda.status_execucao)}`}>
          {getStatusLabel(emenda.status_execucao)}
        </span>
      </div>

      {/* Valores */}
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div>
          <p className="text-xs text-gray-500 mb-1">Valor Aprovado</p>
          <p className="text-lg font-semibold text-gray-900">
            {formatCurrency(emenda.valor_aprovado)}
          </p>
        </div>
        <div>
          <p className="text-xs text-gray-500 mb-1">Valor Pago</p>
          <p className="text-lg font-semibold text-gray-900">
            {formatCurrency(emenda.valor_pago)}
          </p>
        </div>
      </div>

      {/* Progresso */}
      <div className="mb-4">
        <div className="flex justify-between text-xs text-gray-600 mb-1">
          <span>Execução</span>
          <span>{emenda.percentual_executado.toFixed(1)}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className="bg-blue-600 h-2 rounded-full transition-all"
            style={{ width: `${Math.min(emenda.percentual_executado, 100)}%` }}
          />
        </div>
      </div>

      {/* Alertas */}
      {totalAlertas > 0 && (
        <div className="mb-4 space-y-2">
          <p className="text-xs font-semibold text-gray-700 mb-2">
            ⚠️ Alertas ({totalAlertas})
          </p>
          {alertasAlta.slice(0, 2).map((alerta, idx) => (
            <div
              key={idx}
              className={`p-2 rounded border ${getSeverityColor(alerta.severidade)}`}
            >
              <p className="text-xs font-medium">{alerta.mensagem}</p>
            </div>
          ))}
          {alertasAlta.length > 2 && (
            <p className="text-xs text-gray-500">
              +{alertasAlta.length - 2} alerta(s) de alta severidade
            </p>
          )}
        </div>
      )}

      {/* Objeto */}
      {emenda.objetivo && (
        <div className="mb-4">
          <p className="text-xs text-gray-500 mb-1">Objeto</p>
          <p className="text-sm text-gray-700 line-clamp-2">
            {emenda.objetivo}
          </p>
        </div>
      )}

      {/* Footer */}
      <div className="flex justify-between items-center pt-4 border-t border-gray-200">
        <div className="text-xs text-gray-500">
          {emenda.numero_emenda} • {emenda.ano}
        </div>
        <Link
          href={`/emenda-pix/${emenda.id}`}
          className="text-sm font-medium text-blue-600 hover:text-blue-800"
        >
          Ver Detalhes →
        </Link>
      </div>
    </div>
  )
}


