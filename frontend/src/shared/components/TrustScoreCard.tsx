'use client'

import { TrustScoreResponse } from '@/features/emenda-pix/hooks/useTrustScore'

interface TrustScoreCardProps {
  trustScore: TrustScoreResponse
}

export function TrustScoreCard({ trustScore }: TrustScoreCardProps) {
  const getScoreColor = (score: number) => {
    if (score >= 90) return 'text-green-600 bg-green-50 border-green-200'
    if (score >= 70) return 'text-blue-600 bg-blue-50 border-blue-200'
    if (score >= 50) return 'text-yellow-600 bg-yellow-50 border-yellow-200'
    return 'text-red-600 bg-red-50 border-red-200'
  }

  const getLevelLabel = (level: string) => {
    const labels: Record<string, string> = {
      excelente: 'Excelente',
      bom: 'Bom',
      regular: 'Regular',
      ruim: 'Ruim'
    }
    return labels[level] || level
  }

  const getLevelColor = (level: string) => {
    const colors: Record<string, string> = {
      excelente: 'bg-green-100 text-green-800',
      bom: 'bg-blue-100 text-blue-800',
      regular: 'bg-yellow-100 text-yellow-800',
      ruim: 'bg-red-100 text-red-800'
    }
    return colors[level] || 'bg-gray-100 text-gray-800'
  }

  const getFactorLabel = (key: string) => {
    const labels: Record<string, string> = {
      execucao: 'Execução',
      tempo: 'Tempo',
      documentacao: 'Documentação',
      risco: 'Risco',
      historico: 'Histórico'
    }
    return labels[key] || key
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6 border-2 border-gray-200">
      <div className="mb-6">
        <h2 className="text-xl font-bold text-gray-900 mb-2">
          Índice de Integridade (Trust Score)
        </h2>
        <p className="text-sm text-gray-600">
          Avaliação baseada em Triangulação de Dados: Financeira, Política e Física
        </p>
      </div>

      {/* Score Principal */}
      <div className={`rounded-lg p-6 mb-6 border-2 ${getScoreColor(trustScore.trust_score)}`}>
        <div className="flex items-center justify-between mb-4">
          <div>
            <p className="text-sm font-medium text-gray-600 mb-1">Score de Integridade</p>
            <p className="text-4xl font-bold">{trustScore.trust_score.toFixed(1)}</p>
            <p className="text-sm text-gray-600">de 100 pontos</p>
          </div>
          <div>
            <span className={`px-4 py-2 rounded-full text-sm font-semibold ${getLevelColor(trustScore.level)}`}>
              {getLevelLabel(trustScore.level)}
            </span>
          </div>
        </div>

        {/* Barra de Progresso */}
        <div className="w-full bg-gray-200 rounded-full h-3">
          <div
            className={`h-3 rounded-full transition-all ${
              trustScore.trust_score >= 90 ? 'bg-green-500' :
              trustScore.trust_score >= 70 ? 'bg-blue-500' :
              trustScore.trust_score >= 50 ? 'bg-yellow-500' :
              'bg-red-500'
            }`}
            style={{ width: `${trustScore.trust_score}%` }}
          />
        </div>
      </div>

      {/* Fatores */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Fatores de Avaliação</h3>
        <div className="space-y-3">
          {Object.entries(trustScore.factors).map(([key, factor]) => (
            <div key={key} className="bg-gray-50 rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <span className="font-medium text-gray-900">
                    {getFactorLabel(key)}
                  </span>
                  <span className="text-xs text-gray-500">
                    ({(factor.weight * 100).toFixed(0)}%)
                  </span>
                </div>
                <span className="text-lg font-bold text-gray-900">
                  {factor.score.toFixed(1)}
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
                <div
                  className={`h-2 rounded-full ${
                    factor.score >= 70 ? 'bg-green-500' :
                    factor.score >= 50 ? 'bg-yellow-500' :
                    'bg-red-500'
                  }`}
                  style={{ width: `${factor.score}%` }}
                />
              </div>
              <p className="text-xs text-gray-600">{factor.details}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Recomendações */}
      {trustScore.recommendations && trustScore.recommendations.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-3">Recomendações</h3>
          <ul className="space-y-2">
            {trustScore.recommendations.map((rec, index) => (
              <li key={index} className="flex items-start gap-2 text-sm text-gray-700">
                <span className="text-blue-500 mt-1">•</span>
                <span>{rec}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}

