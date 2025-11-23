'use client'

import { useState } from 'react'
import { useEmendasPix } from '@/features/emenda-pix/hooks/useEmendasPix'
import { Button } from '@/shared/components/ui/button'
import { Select } from '@/shared/components/ui/select'
import { Input } from '@/shared/components/ui/input'
import Link from 'next/link'

export default function EmendaPixPage() {
  const [page, setPage] = useState(0)
  const limit = 12
  const offset = page * limit
  
  // Filters
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [areaFilter, setAreaFilter] = useState<string>('all')
  const [ufFilter, setUfFilter] = useState<string>('all')
  const [searchQuery, setSearchQuery] = useState<string>('')

  const { data, isLoading, error } = useEmendasPix({
    limit,
    offset,
    status_execucao: statusFilter !== 'all' ? statusFilter : undefined,
    area: areaFilter !== 'all' ? areaFilter : undefined,
    destinatario_uf: ufFilter !== 'all' ? ufFilter : undefined
  })

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

  const filteredEmendas = data?.items.filter(emenda => {
    if (!searchQuery) return true
    const query = searchQuery.toLowerCase()
    return (
      emenda.numero_emenda.toLowerCase().includes(query) ||
      emenda.autor_nome.toLowerCase().includes(query) ||
      emenda.destinatario_nome.toLowerCase().includes(query) ||
      emenda.objetivo?.toLowerCase().includes(query)
    )
  }) || []

  if (error) {
    return (
      <div className="min-h-screen bg-[#F3F4F6]">
        <div className="container mx-auto px-4 py-8">
          <div className="text-center py-12">
            <div className="text-6xl mb-4">❌</div>
            <p className="text-red-500 text-lg">Erro ao carregar emendas</p>
          </div>
        </div>
      </div>
    )
  }

  const totalEmendas = data?.total || 0
  const totalValor = data?.items?.reduce((sum, e) => sum + e.valor_aprovado, 0) || 0
  const emendasAtrasadas = data?.items?.filter(e => e.status_execucao === 'atrasada').length || 0
  const taxaExecucaoMedia = data?.items && data.items.length > 0
    ? Math.round(data.items.reduce((sum, e) => sum + e.percentual_executado, 0) / data.items.length)
    : 0

  return (
    <div className="min-h-screen bg-[#F3F4F6]">
      <div className="container mx-auto px-4 sm:px-5 md:px-6 lg:px-8 py-6 sm:py-8 md:py-10 lg:py-12 max-w-7xl">
        {/* Header Melhorado */}
        <div className="mb-6 sm:mb-8 md:mb-12">
          <div className="mb-6">
            <h1 className="text-2xl sm:text-3xl md:text-4xl font-extrabold text-[#1F2937] mb-2">
              🔍 Rastreamento de Emenda Pix
            </h1>
            <p className="text-sm sm:text-base md:text-lg text-[#6B7280] max-w-2xl">
              Transparência e controle social sobre a execução de emendas parlamentares
            </p>
          </div>

          {/* Stats Cards Melhorados */}
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4 mb-6">
            <div className="bg-white border border-[#E5E7EB] rounded-xl shadow-sm p-4 sm:p-6 hover:shadow-md transition-shadow">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-sm font-semibold text-[#6B7280] uppercase tracking-wide">Total de Emendas</h3>
                <div className="text-2xl">📊</div>
              </div>
              <div className="text-3xl md:text-4xl font-bold text-[#1F2937]">{totalEmendas}</div>
            </div>
            
            <div className="bg-white border border-[#E5E7EB] rounded-xl shadow-sm p-6 hover:shadow-md transition-shadow">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-sm font-semibold text-[#6B7280] uppercase tracking-wide">Valor Total</h3>
                <div className="text-2xl">💰</div>
              </div>
              <div className="text-2xl md:text-3xl font-bold text-[#1F2937]">{formatCurrency(totalValor)}</div>
            </div>
            
            <div className="bg-white border border-[#E5E7EB] rounded-xl shadow-sm p-6 hover:shadow-md transition-shadow">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-sm font-semibold text-[#6B7280] uppercase tracking-wide">Emendas Atrasadas</h3>
                <div className="text-2xl">⚠️</div>
              </div>
              <div className="text-3xl md:text-4xl font-bold text-[#1F2937]">{emendasAtrasadas}</div>
            </div>
            
            <div className="bg-white border border-[#E5E7EB] rounded-xl shadow-sm p-6 hover:shadow-md transition-shadow">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-sm font-semibold text-[#6B7280] uppercase tracking-wide">Taxa Execução Média</h3>
                <div className="text-2xl">📈</div>
              </div>
              <div className="text-3xl md:text-4xl font-bold text-[#1F2937]">{taxaExecucaoMedia}%</div>
            </div>
          </div>
        </div>

        {/* Filters Melhorados */}
        <div className="mb-6 sm:mb-8">
          <div className="bg-white border border-[#E5E7EB] rounded-xl shadow-sm p-4 sm:p-6">
            <h2 className="text-base sm:text-lg font-semibold text-[#1F2937] mb-4">🔍 Filtros de Busca</h2>
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
              <div>
                <Input
                  label="Buscar"
                  placeholder="Número, autor, destinatário..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>
              <div>
                <Select
                  label="Status"
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  options={[
                    { value: 'all', label: 'Todos' },
                    { value: 'pendente', label: 'Pendente' },
                    { value: 'em_execucao', label: 'Em Execução' },
                    { value: 'concluida', label: 'Concluída' },
                    { value: 'atrasada', label: 'Atrasada' }
                  ]}
                />
              </div>
              <div>
                <Select
                  label="Área"
                  value={areaFilter}
                  onChange={(e) => setAreaFilter(e.target.value)}
                  options={[
                    { value: 'all', label: 'Todas' },
                    { value: 'saude', label: 'Saúde' },
                    { value: 'educacao', label: 'Educação' },
                    { value: 'infraestrutura', label: 'Infraestrutura' },
                    { value: 'seguranca', label: 'Segurança' },
                    { value: 'saneamento', label: 'Saneamento' }
                  ]}
                />
              </div>
              <div>
                <Select
                  label="UF"
                  value={ufFilter}
                  onChange={(e) => setUfFilter(e.target.value)}
                  options={[
                    { value: 'all', label: 'Todas' },
                    { value: 'SP', label: 'SP' },
                    { value: 'RJ', label: 'RJ' },
                    { value: 'MG', label: 'MG' },
                    { value: 'RS', label: 'RS' },
                    { value: 'BA', label: 'BA' },
                    { value: 'CE', label: 'CE' },
                    { value: 'MT', label: 'MT' }
                  ]}
                />
              </div>
              <div className="flex items-end">
                <Button
                  variant="outline"
                  onClick={() => {
                    setStatusFilter('all')
                    setAreaFilter('all')
                    setUfFilter('all')
                    setSearchQuery('')
                  }}
                  className="w-full border-2 hover:bg-gray-50"
                >
                  🔄 Limpar
                </Button>
              </div>
            </div>
          </div>
        </div>

        {/* Emendas List Melhorado */}
        <div>
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl md:text-3xl font-bold text-gray-900">
              Emendas {filteredEmendas.length !== (data?.items?.length || 0)
                ? `(${filteredEmendas.length} de ${data?.items?.length || 0})` 
                : ''}
            </h2>
          </div>

          {isLoading ? (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {[...Array(6)].map((_, i) => (
                <div key={i} className="bg-white rounded-xl shadow-md border border-gray-200 p-6 animate-pulse">
                  <div className="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
                  <div className="h-4 bg-gray-200 rounded w-1/2 mb-4"></div>
                  <div className="h-20 bg-gray-200 rounded"></div>
                </div>
              ))}
            </div>
          ) : filteredEmendas.length === 0 ? (
            <div className="text-center py-12 bg-white border border-[#E5E7EB] rounded-xl shadow-sm">
              <div className="text-6xl mb-4">📭</div>
              <p className="text-gray-500 text-lg">Nenhuma emenda encontrada</p>
            </div>
          ) : (
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
              {filteredEmendas.map((emenda) => (
                <Link key={emenda.id} href={`/emenda-pix/${emenda.id}`}>
                  <div className="bg-white border border-[#E5E7EB] rounded-xl shadow-sm p-4 sm:p-6 hover:shadow-md hover:border-[#3b82f6] transition-all duration-300 transform hover:-translate-y-1 cursor-pointer h-full">
                    <div className="flex justify-between items-start mb-4">
                      <div>
                        <h3 className="font-bold text-xl text-gray-900 mb-1">{emenda.numero_emenda}</h3>
                        <p className="text-sm text-gray-500">Ano {emenda.ano}</p>
                      </div>
                      <span className={`px-3 py-1 text-xs font-semibold rounded-full ${getStatusColor(emenda.status_execucao)}`}>
                        {getStatusLabel(emenda.status_execucao)}
                      </span>
                    </div>
                    
                    <div className="mb-4 space-y-2">
                      <p className="text-sm text-gray-600">
                        <strong className="text-gray-900">Autor:</strong> {emenda.autor_nome}
                      </p>
                      <p className="text-sm text-gray-600">
                        <strong className="text-gray-900">Destinatário:</strong> {emenda.destinatario_nome} - {emenda.destinatario_uf}
                      </p>
                    </div>

                    <div className="mb-4">
                      <p className="text-lg font-bold text-gray-900 mb-2">
                        {formatCurrency(emenda.valor_aprovado)}
                      </p>
                      <div className="w-full bg-gray-200 rounded-full h-3 mb-1">
                        <div
                          className={`h-3 rounded-full transition-all ${
                            emenda.percentual_executado < 50 ? 'bg-red-500' :
                            emenda.percentual_executado < 80 ? 'bg-yellow-500' : 'bg-green-500'
                          }`}
                          style={{ width: `${emenda.percentual_executado}%` }}
                        />
                      </div>
                      <p className="text-xs text-gray-500 mt-1">
                        {emenda.percentual_executado.toFixed(1)}% executado
                      </p>
                    </div>

                    {emenda.objetivo && (
                      <p className="text-sm text-gray-600 line-clamp-2 mb-3">{emenda.objetivo}</p>
                    )}

                    {emenda.alertas && emenda.alertas.length > 0 && (
                      <div className="mt-4 pt-4 border-t border-gray-200">
                        <p className="text-xs text-red-600 font-semibold flex items-center gap-1">
                          <span>⚠️</span>
                          {emenda.alertas.length} alerta(s)
                        </p>
                      </div>
                    )}
                  </div>
                </Link>
              ))}
            </div>
          )}

          {/* Pagination Melhorado */}
          {data && data.items && data.items.length > 0 && (
            <div className="mt-8 flex justify-center gap-4">
              <Button
                variant="outline"
                onClick={() => setPage(p => Math.max(0, p - 1))}
                disabled={page === 0}
                className="px-6 py-2 border-2 hover:bg-gray-50"
              >
                ← Anterior
              </Button>
              <span className="flex items-center px-6 py-2 bg-white rounded-lg border border-[#E5E7EB] font-semibold text-[#1F2937]">
                Página {page + 1}
              </span>
              <Button
                variant="outline"
                onClick={() => setPage(p => p + 1)}
                disabled={(data?.items?.length || 0) < limit}
                className="px-6 py-2 border-2 hover:bg-gray-50"
              >
                Próxima →
              </Button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
