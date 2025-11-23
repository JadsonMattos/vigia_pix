'use client'

interface ComparisonCardProps {
  portalData: {
    valor_aprovado: number
    valor_pago: number
    valor_empenhado: number
    valor_liquidado: number
  }
  transferegovData?: {
    situacao_plano_acao?: string
    nome_beneficiario?: string
    descricao_programacao_orcamentaria?: string
  }
  anomalias?: Array<{
    tipo: string
    severidade: string
    mensagem: string
    detalhes?: {
      valor_pago?: number
      percentual_pago?: number
      situacao_plano?: string
    }
  }>
}

export function ComparisonCard({ portalData, transferegovData, anomalias = [] }: ComparisonCardProps) {
  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
      minimumFractionDigits: 0
    }).format(value)
  }

  const percentualPago = portalData.valor_aprovado > 0 
    ? (portalData.valor_pago / portalData.valor_aprovado * 100) 
    : 0

  const getStatusColor = (situacao?: string) => {
    if (!situacao) return 'bg-gray-100 text-gray-800'
    const situacaoLower = situacao.toLowerCase()
    if (situacaoLower.includes('aprovado')) return 'bg-green-100 text-green-800'
    if (situacaoLower.includes('análise') || situacaoLower.includes('analise')) return 'bg-yellow-100 text-yellow-800'
    if (situacaoLower.includes('cancelado')) return 'bg-red-100 text-red-800'
    return 'bg-gray-100 text-gray-800'
  }

  const getSeverityColor = (severidade: string) => {
    const colors: Record<string, string> = {
      'alta': 'bg-red-100 text-red-800 border-red-300',
      'media': 'bg-yellow-100 text-yellow-800 border-yellow-300',
      'baixa': 'bg-blue-100 text-blue-800 border-blue-300'
    }
    return colors[severidade] || 'bg-gray-100 text-gray-800'
  }

  return (
    <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6">
      <h2 className="text-xl font-semibold text-gray-900 mb-6">
        🔍 Comparação: Portal da Transparência vs Transferegov.br
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        {/* Portal da Transparência */}
        <div className="border border-blue-200 rounded-lg p-4 bg-blue-50">
          <h3 className="text-lg font-semibold text-blue-900 mb-4">
            💰 Portal da Transparência
          </h3>
          <div className="space-y-3">
            <div>
              <p className="text-sm text-blue-700 mb-1">Valor Aprovado</p>
              <p className="text-lg font-bold text-blue-900">
                {formatCurrency(portalData.valor_aprovado)}
              </p>
            </div>
            <div>
              <p className="text-sm text-blue-700 mb-1">Valor Empenhado</p>
              <p className="text-base font-semibold text-blue-900">
                {formatCurrency(portalData.valor_empenhado)}
              </p>
            </div>
            <div>
              <p className="text-sm text-blue-700 mb-1">Valor Liquidado</p>
              <p className="text-base font-semibold text-blue-900">
                {formatCurrency(portalData.valor_liquidado)}
              </p>
            </div>
            <div>
              <p className="text-sm text-blue-700 mb-1">Valor Pago</p>
              <p className="text-xl font-bold text-blue-900">
                {formatCurrency(portalData.valor_pago)}
              </p>
            </div>
            <div>
              <p className="text-sm text-blue-700 mb-1">Percentual Pago</p>
              <div className="flex items-center gap-2">
                <div className="flex-1 bg-blue-200 rounded-full h-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full transition-all"
                    style={{ width: `${Math.min(percentualPago, 100)}%` }}
                  />
                </div>
                <span className="text-sm font-semibold text-blue-900">
                  {percentualPago.toFixed(1)}%
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Transferegov.br */}
        <div className="border border-green-200 rounded-lg p-4 bg-green-50">
          <h3 className="text-lg font-semibold text-green-900 mb-4">
            📋 Transferegov.br (Execução)
          </h3>
          {transferegovData ? (
            <div className="space-y-3">
              <div>
                <p className="text-sm text-green-700 mb-1">Situação do Plano</p>
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(transferegovData.situacao_plano_acao)}`}>
                  {transferegovData.situacao_plano_acao || 'Não informado'}
                </span>
              </div>
              <div>
                <p className="text-sm text-green-700 mb-1">Beneficiário</p>
                <p className="text-base font-semibold text-green-900">
                  {transferegovData.nome_beneficiario || 'Não informado'}
                </p>
              </div>
              <div>
                <p className="text-sm text-green-700 mb-1">Descrição</p>
                <p className="text-sm text-green-900 line-clamp-3">
                  {transferegovData.descricao_programacao_orcamentaria || 'Não informado'}
                </p>
              </div>
            </div>
          ) : (
            <div className="text-center py-4">
              <p className="text-sm text-gray-600">
                ⚠️ Dados do Transferegov.br não disponíveis
              </p>
              <p className="text-xs text-gray-500 mt-2">
                Execute a análise com IA para sincronizar
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Anomalias Detectadas */}
      {anomalias.length > 0 && (
        <div className="mt-6 border-t border-gray-200 pt-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            ⚠️ Anomalias Detectadas ({anomalias.length})
          </h3>
          <div className="space-y-3">
            {anomalias.map((anomalia, index) => (
              <div
                key={index}
                className={`p-4 rounded-lg border ${getSeverityColor(anomalia.severidade)}`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <p className="font-medium mb-1">{anomalia.mensagem}</p>
                    {anomalia.detalhes && (
                      <div className="text-xs mt-2 space-y-1">
                        {anomalia.detalhes.percentual_pago !== undefined && (
                          <p>Percentual pago: {anomalia.detalhes.percentual_pago.toFixed(1)}%</p>
                        )}
                        {anomalia.detalhes.situacao_plano && (
                          <p>Situação do plano: {anomalia.detalhes.situacao_plano}</p>
                        )}
                      </div>
                    )}
                  </div>
                  <span className={`px-2 py-1 rounded text-xs font-medium ${
                    anomalia.severidade === 'alta' ? 'bg-red-200 text-red-900' :
                    anomalia.severidade === 'media' ? 'bg-yellow-200 text-yellow-900' :
                    'bg-blue-200 text-blue-900'
                  }`}>
                    {anomalia.severidade.toUpperCase()}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Indicador de Consistência */}
      {anomalias.length === 0 && transferegovData && (
        <div className="mt-6 border-t border-gray-200 pt-6">
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <p className="text-green-800 font-medium">
              ✅ Nenhuma inconsistência detectada entre os dados
            </p>
          </div>
        </div>
      )}
    </div>
  )
}


