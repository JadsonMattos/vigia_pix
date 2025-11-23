'use client'

import { useParams } from 'next/navigation'
import { useState } from 'react'
import { useEmendaPix } from '@/features/emenda-pix/hooks/useEmendasPix'
import { useTrustScore } from '@/features/emenda-pix/hooks/useTrustScore'
import { TrustScoreCard } from '@/shared/components/TrustScoreCard'
import { PhotoUpload } from '@/components/PhotoUpload'
import { MapView } from '@/shared/components/MapView'
import { ComparisonCard } from '@/shared/components/ComparisonCard'
import { Button } from '@/shared/components/ui/button'
import { api } from '@/core/api/client'
import Link from 'next/link'

export default function EmendaPixDetailPage() {
  const params = useParams()
  const id = params.id as string
  const [analyzing, setAnalyzing] = useState(false)

  const { data: emenda, isLoading, error, refetch } = useEmendaPix(id)
  const { data: trustScore, isLoading: isLoadingTrustScore } = useTrustScore(id)

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
      minimumFractionDigits: 0
    }).format(value)
  }

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'Não informado'
    return new Date(dateString).toLocaleDateString('pt-BR')
  }

  const handleAnalyze = async () => {
    setAnalyzing(true)
    try {
      await api.post(`/emenda-pix/${id}/analyze`)
      await refetch()
      alert('✅ Análise com IA concluída! Verifique os alertas e recomendações.')
    } catch (error) {
      console.error('Erro ao analisar:', error)
      alert('❌ Erro ao analisar emenda. Tente novamente.')
    } finally {
      setAnalyzing(false)
    }
  }

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="bg-gray-200 animate-pulse rounded-lg h-96" />
      </div>
    )
  }

  if (error || !emenda) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center">
          <p className="text-red-500">Emenda não encontrada</p>
          <Link href="/emenda-pix">
            <Button variant="outline" className="mt-4">Voltar para lista</Button>
          </Link>
        </div>
      </div>
    )
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

  const getSeverityColor = (severidade: string) => {
    const colors: Record<string, string> = {
      'alta': 'bg-red-100 text-red-800 border-red-300',
      'media': 'bg-yellow-100 text-yellow-800 border-yellow-300',
      'baixa': 'bg-blue-100 text-blue-800 border-blue-300'
    }
    return colors[severidade] || 'bg-gray-100 text-gray-800'
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-6xl">
      {/* Header */}
      <div className="mb-6">
        <Link href="/emenda-pix">
          <Button variant="outline" size="sm" className="mb-4">
            ← Voltar
          </Button>
        </Link>
        <div className="flex flex-col md:flex-row md:justify-between md:items-start gap-4">
          <div>
            <h1 className="text-2xl md:text-3xl font-bold text-gray-900 mb-2">{emenda.numero_emenda}</h1>
            <p className="text-sm md:text-base text-gray-600">Ano {emenda.ano} • {emenda.tipo === 'individual' ? 'Emenda Individual' : 'Emenda de Bancada'}</p>
          </div>
          <div className="flex flex-col sm:flex-row gap-2">
            <Button
              onClick={handleAnalyze}
              disabled={analyzing}
              variant="primary"
              className="w-full sm:w-auto"
            >
              {analyzing ? '⏳ Analisando...' : '🤖 Analisar com IA'}
            </Button>
            <span className={`px-4 py-2 text-sm font-medium rounded text-center ${getStatusColor(emenda.status_execucao)}`}>
              {emenda.status_execucao.replace('_', ' ').toUpperCase()}
            </span>
          </div>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-3">
        {/* Main Content */}
        <div className="md:col-span-2 space-y-6">
          {/* Valores e Execução */}
          <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Valores e Execução</h2>
            
            <div className="grid gap-4 md:grid-cols-2 mb-4">
              <div>
                <p className="text-sm text-gray-600 mb-1">Valor Aprovado</p>
                <p className="text-2xl font-bold text-gray-900">{formatCurrency(emenda.valor_aprovado)}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600 mb-1">Valor Pago</p>
                <p className="text-2xl font-bold text-green-600">{formatCurrency(emenda.valor_pago)}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600 mb-1">Valor Empenhado</p>
                <p className="text-lg font-semibold text-blue-600">{formatCurrency(emenda.valor_empenhado)}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600 mb-1">Valor Liquidado</p>
                <p className="text-lg font-semibold text-yellow-600">{formatCurrency(emenda.valor_liquidado)}</p>
              </div>
            </div>

            <div className="mt-4">
              <div className="flex justify-between text-sm mb-2">
                <span className="text-gray-600">Progresso de Execução</span>
                <span className="font-semibold">{emenda.percentual_executado.toFixed(1)}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-4">
                <div
                  className={`h-4 rounded-full ${
                    emenda.percentual_executado < 50 ? 'bg-red-500' :
                    emenda.percentual_executado < 80 ? 'bg-yellow-500' : 'bg-green-500'
                  }`}
                  style={{ width: `${emenda.percentual_executado}%` }}
                />
              </div>
            </div>
          </div>

          {/* Trust Score */}
          {trustScore && trustScore.success && (
            <TrustScoreCard trustScore={trustScore} />
          )}
          {isLoadingTrustScore && (
            <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6">
              <div className="bg-gray-200 animate-pulse rounded-lg h-64" />
            </div>
          )}

          {/* Informações da Emenda */}
          <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Informações</h2>
            
            <div className="space-y-3">
              <div>
                <p className="text-sm font-medium text-gray-600">Autor</p>
                <p className="text-base text-gray-900">{emenda.autor_nome} {emenda.autor_partido && `(${emenda.autor_partido}/${emenda.autor_uf})`}</p>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-600">Destinatário</p>
                <p className="text-base text-gray-900">{emenda.destinatario_nome} - {emenda.destinatario_uf}</p>
                <p className="text-xs text-gray-500">{emenda.destinatario_tipo}</p>
              </div>
              {emenda.objetivo && (
                <div>
                  <p className="text-sm font-medium text-gray-600">Objetivo</p>
                  <p className="text-base text-gray-900">{emenda.objetivo}</p>
                </div>
              )}
              {emenda.descricao_detalhada && (
                <div>
                  <p className="text-sm font-medium text-gray-600">Descrição Detalhada</p>
                  <p className="text-base text-gray-900 whitespace-pre-wrap">{emenda.descricao_detalhada}</p>
                </div>
              )}
              {emenda.area && (
                <div>
                  <p className="text-sm font-medium text-gray-600">Área</p>
                  <p className="text-base text-gray-900 capitalize">{emenda.area}</p>
                </div>
              )}
            </div>
          </div>

          {/* Plano de Trabalho */}
          {emenda.plano_trabalho && emenda.plano_trabalho.length > 0 && (
            <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">
                Plano de Trabalho ({emenda.metas_concluidas}/{emenda.numero_metas} concluídas)
              </h2>
              
              <div className="space-y-3">
                {emenda.plano_trabalho.map((meta, index) => (
                  <div key={index} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex justify-between items-start mb-2">
                      <div>
                        <p className="font-semibold text-gray-900">Meta {meta.meta}: {meta.descricao}</p>
                        <p className="text-sm text-gray-600">{formatCurrency(meta.valor)}</p>
                      </div>
                      <span className={`px-2 py-1 text-xs font-medium rounded ${
                        meta.status === 'concluida' ? 'bg-green-100 text-green-800' :
                        meta.status === 'atrasada' ? 'bg-red-100 text-red-800' :
                        'bg-yellow-100 text-yellow-800'
                      }`}>
                        {meta.status === 'concluida' ? 'Concluída' :
                         meta.status === 'atrasada' ? 'Atrasada' : 'Em Execução'}
                      </span>
                    </div>
                    <p className="text-xs text-gray-500">Prazo: {formatDate(meta.prazo)}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Alertas */}
          {emenda.alertas && emenda.alertas.length > 0 && (
            <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">⚠️ Alertas</h2>
              
              <div className="space-y-3">
                {emenda.alertas.map((alerta, index) => (
                  <div key={index} className={`border rounded-lg p-4 ${getSeverityColor(alerta.severidade)}`}>
                    <div className="flex justify-between items-start mb-1">
                      <p className="font-semibold">{alerta.tipo.replace('_', ' ').toUpperCase()}</p>
                      <span className="text-xs">{formatDate(alerta.data)}</span>
                    </div>
                    <p className="text-sm">{alerta.mensagem}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Comparação Portal vs Transferegov */}
          {emenda.analise_ia && (
            <ComparisonCard
              portalData={{
                valor_aprovado: emenda.valor_aprovado,
                valor_pago: emenda.valor_pago,
                valor_empenhado: emenda.valor_empenhado,
                valor_liquidado: emenda.valor_liquidado
              }}
              transferegovData={emenda.analise_ia.plano_acao}
              anomalias={emenda.analise_ia.anomalias_cruzamento}
            />
          )}

          {/* Localização Extraída e Mapa */}
          {emenda.analise_ia?.localizacao_extraida && (
            <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">
                📍 Localização da Emenda
              </h2>
              <div className="mb-4">
                <p className="text-sm text-gray-600 mb-2">Localização extraída:</p>
                <p className="text-base font-medium text-gray-900">
                  {emenda.analise_ia.localizacao_extraida}
                </p>
                {emenda.analise_ia.categoria_gasto && (
                  <p className="text-sm text-gray-600 mt-2">
                    Categoria: <span className="font-medium">{emenda.analise_ia.categoria_gasto}</span>
                  </p>
                )}
                {emenda.analise_ia.objeto_principal && (
                  <p className="text-sm text-gray-600 mt-1">
                    Objeto: <span className="font-medium">{emenda.analise_ia.objeto_principal}</span>
                  </p>
                )}
              </div>
              <MapView 
                address={emenda.analise_ia.localizacao_extraida}
                height="300px"
              />
            </div>
          )}

          {/* Triangulação de Dados - Fonte Física */}
          {((emenda.fotos_georreferenciadas && emenda.fotos_georreferenciadas.length > 0) || 
           (emenda.documentos_comprobatórios && emenda.documentos_comprobatórios.length > 0)) && (
            <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">
                📸 Triangulação de Dados - Fonte Física
              </h2>
              <p className="text-sm text-gray-600 mb-4">
                Fotos e documentos georreferenciados para validação física da execução
              </p>
              
              {/* Fotos Georreferenciadas */}
              {emenda.fotos_georreferenciadas && emenda.fotos_georreferenciadas.length > 0 && (
                <div className="mb-6">
                  <h3 className="text-lg font-medium text-gray-900 mb-3">Fotos Georreferenciadas</h3>
                  <div className="grid gap-4 md:grid-cols-2">
                    {emenda.fotos_georreferenciadas.map((foto, index) => (
                      <div key={index} className="border border-gray-200 rounded-lg p-4">
                        <div className="flex items-start justify-between mb-2">
                          <div>
                            <p className="font-medium text-gray-900 capitalize">{foto.tipo?.replace('_', ' ') || 'Foto'}</p>
                            <p className="text-xs text-gray-500">
                              📍 {foto.latitude?.toFixed(6)}, {foto.longitude?.toFixed(6)}
                            </p>
                          </div>
                          {foto.validacao_geofencing !== undefined && (
                            <span className={`px-2 py-1 text-xs font-medium rounded ${
                              foto.validacao_geofencing 
                                ? 'bg-green-100 text-green-800' 
                                : 'bg-red-100 text-red-800'
                            }`}>
                              {foto.validacao_geofencing ? '✓ Válido' : '✗ Inválido'}
                            </span>
                          )}
                        </div>
                        {foto.url && (
                          <a
                            href={foto.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-sm text-blue-600 hover:underline"
                          >
                            Ver foto →
                          </a>
                        )}
                        {foto.data_upload && (
                          <p className="text-xs text-gray-500 mt-1">
                            Upload: {formatDate(foto.data_upload)}
                          </p>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
              
              {/* Documentos Comprobatórios */}
              {emenda.documentos_comprobatórios && emenda.documentos_comprobatórios.length > 0 && (
                <div>
                  <h3 className="text-lg font-medium text-gray-900 mb-3">Documentos Comprobatórios</h3>
                  <div className="space-y-2">
                    {emenda.documentos_comprobatórios.map((doc, index) => (
                      <div key={index} className="flex items-center justify-between border border-gray-200 rounded-lg p-3">
                        <div>
                          <p className="font-medium text-gray-900 capitalize">{doc.tipo?.replace('_', ' ') || 'Documento'}</p>
                          {doc.descricao && (
                            <p className="text-sm text-gray-600">{doc.descricao}</p>
                          )}
                        </div>
                        {doc.url && (
                          <a
                            href={doc.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-sm text-blue-600 hover:underline"
                          >
                            Ver →
                          </a>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
              
              {/* Upload de Fotos (Mobile-First) */}
              <div className="mt-6 p-4 bg-gray-50 rounded-lg border border-gray-200">
                <h3 className="text-lg font-medium text-gray-900 mb-3">
                  📸 Adicionar Foto Comprobatória
                </h3>
                <PhotoUpload
                  emendaId={id}
                  onUploadSuccess={(result) => {
                    alert('Foto enviada com sucesso!')
                    refetch()
                  }}
                  onUploadError={(error) => {
                    alert(`Erro: ${error}`)
                  }}
                />
              </div>

              {/* Status de Validação Geral */}
              {emenda.validacao_geofencing !== undefined && (
                <div className={`mt-4 p-4 rounded-lg ${
                  emenda.validacao_geofencing 
                    ? 'bg-green-50 border border-green-200' 
                    : 'bg-red-50 border border-red-200'
                }`}>
                  <div className="flex items-center gap-2">
                    <span className="text-lg">
                      {emenda.validacao_geofencing ? '✅' : '⚠️'}
                    </span>
                    <div>
                      <p className="font-medium text-gray-900">
                        Validação Geofencing: {emenda.validacao_geofencing ? 'Aprovada' : 'Reprovada'}
                      </p>
                      <p className="text-sm text-gray-600">
                        {emenda.validacao_geofencing 
                          ? 'Todas as fotos estão dentro do geofence esperado'
                          : 'Algumas fotos estão fora do geofence esperado'}
                      </p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Notícias */}
          {emenda.noticias_relacionadas && emenda.noticias_relacionadas.length > 0 && (
            <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">📰 Notícias Relacionadas</h2>
              
              <div className="space-y-3">
                {emenda.noticias_relacionadas.map((noticia, index) => (
                  <div key={index} className="border border-gray-200 rounded-lg p-4">
                    <p className="font-semibold text-gray-900 mb-1">{noticia.titulo}</p>
                    <p className="text-sm text-gray-600">{noticia.fonte} • {formatDate(noticia.data)}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Análise IA */}
          {emenda.analise_ia && (
            <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">🤖 Análise com IA</h2>
              
              <div className="space-y-4">
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-600">Score de Transparência</span>
                    <span className="font-semibold">{(emenda.analise_ia.transparencia_score * 100).toFixed(0)}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-500 h-2 rounded-full"
                      style={{ width: `${emenda.analise_ia.transparencia_score * 100}%` }}
                    />
                  </div>
                </div>

                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-600">Risco de Desvio</span>
                    <span className="font-semibold">{(emenda.analise_ia.risco_desvio * 100).toFixed(0)}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full ${
                        emenda.analise_ia.risco_desvio > 0.7 ? 'bg-red-500' :
                        emenda.analise_ia.risco_desvio > 0.4 ? 'bg-yellow-500' : 'bg-green-500'
                      }`}
                      style={{ width: `${emenda.analise_ia.risco_desvio * 100}%` }}
                    />
                  </div>
                </div>

                {emenda.analise_ia.recomendacoes && emenda.analise_ia.recomendacoes.length > 0 && (
                  <div>
                    <p className="text-sm font-medium text-gray-600 mb-2">Recomendações:</p>
                    <ul className="space-y-1">
                      {emenda.analise_ia.recomendacoes.map((rec, index) => (
                        <li key={index} className="text-sm text-gray-700">• {rec}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Datas Importantes */}
          <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">📅 Datas Importantes</h2>
            
            <div className="space-y-3">
              <div>
                <p className="text-sm font-medium text-gray-600">Data de Início</p>
                <p className="text-base text-gray-900">{formatDate(emenda.data_inicio)}</p>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-600">Prazo Previsto</p>
                <p className="text-base text-gray-900">{formatDate(emenda.data_prevista_conclusao)}</p>
              </div>
              {emenda.data_real_conclusao && (
                <div>
                  <p className="text-sm font-medium text-gray-600">Data Real de Conclusão</p>
                  <p className="text-base text-gray-900">{formatDate(emenda.data_real_conclusao)}</p>
                </div>
              )}
            </div>
          </div>

          {/* Links */}
          <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">🔗 Links</h2>
            
            <div className="space-y-2">
              {emenda.processo_sei && (
                <a
                  href={`https://ceis.gov.br/${emenda.processo_sei}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="block text-sm text-blue-600 hover:underline"
                >
                  Processo CEIS: {emenda.processo_sei}
                </a>
              )}
              {emenda.link_portal_transparencia && (
                <a
                  href={emenda.link_portal_transparencia}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="block text-sm text-blue-600 hover:underline"
                >
                  Portal da Transparência
                </a>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

