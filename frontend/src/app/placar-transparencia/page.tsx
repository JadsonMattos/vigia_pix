'use client'

import { useState } from 'react'
import { useEmendasPix } from '@/features/emenda-pix/hooks/useEmendasPix'
import { PlacarCard } from '@/shared/components/PlacarCard'
import { Input } from '@/shared/components/ui/input'
import { Button } from '@/shared/components/ui/button'

export default function PlacarTransparenciaPage() {
  const [searchType, setSearchType] = useState<'municipio' | 'parlamentar'>('municipio')
  const [searchQuery, setSearchQuery] = useState<string>('')
  const [isSearching, setIsSearching] = useState(false)

  const { data, isLoading, error } = useEmendasPix({
    limit: 50,
    offset: 0,
    autor_nome: searchType === 'parlamentar' && searchQuery ? searchQuery : undefined,
    // Para município, usamos destinatario_uf como aproximação
    // (em produção, seria necessário adicionar filtro por destinatario_nome)
  })

  const handleSearch = () => {
    if (searchQuery.trim()) {
      setIsSearching(true)
      // A busca será feita automaticamente pelo useQuery quando os parâmetros mudarem
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      handleSearch()
    }
  }

  // Filtrar por município no frontend (temporário até backend ter filtro)
  const filteredData = searchType === 'municipio' && searchQuery
    ? data?.items.filter(emenda => 
        emenda.destinatario_nome.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : data?.items

  const totalEmendas = filteredData?.length || 0
  const totalValor = filteredData?.reduce((sum, e) => sum + e.valor_aprovado, 0) || 0
  const totalPago = filteredData?.reduce((sum, e) => sum + e.valor_pago, 0) || 0
  const totalAlertas = filteredData?.reduce((sum, e) => 
    sum + (e.alertas?.filter(a => a.severidade === 'alta' || a.severidade === 'media').length || 0), 0
  ) || 0

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
      minimumFractionDigits: 0
    }).format(value)
  }

  return (
    <div className="min-h-screen bg-[#F3F4F6]">
      <div className="container mx-auto px-4 sm:px-5 md:px-6 lg:px-8 py-6 sm:py-8 md:py-10 lg:py-12 max-w-7xl">
        {/* Header */}
        <div className="mb-6 sm:mb-8">
          <h1 className="text-2xl sm:text-3xl md:text-4xl font-extrabold text-[#1F2937] mb-2">
            Placar de Transparência
          </h1>
          <p className="text-sm sm:text-base md:text-lg text-[#6B7280]">
            Busque emendas por município ou parlamentar e acompanhe a execução dos recursos
          </p>
        </div>

        {/* Busca */}
        <div className="bg-white border border-[#E5E7EB] rounded-xl shadow-sm p-4 sm:p-6 mb-6 sm:mb-8">
          <div className="flex flex-col sm:flex-row gap-4">
            {/* Tipo de Busca */}
            <div className="flex gap-2">
              <button
                onClick={() => setSearchType('municipio')}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  searchType === 'municipio'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                Município
              </button>
              <button
                onClick={() => setSearchType('parlamentar')}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  searchType === 'parlamentar'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                Parlamentar
              </button>
            </div>

            {/* Campo de Busca */}
            <div className="flex-1 flex gap-2">
              <Input
                type="text"
                placeholder={
                  searchType === 'municipio'
                    ? 'Digite o nome do município...'
                    : 'Digite o nome do parlamentar...'
                }
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyPress={handleKeyPress}
                className="flex-1"
              />
              <Button onClick={handleSearch}>
                Buscar
              </Button>
            </div>
          </div>
        </div>

        {/* Estatísticas */}
        {isSearching && filteredData && filteredData.length > 0 && (
          <div className="grid grid-cols-1 sm:grid-cols-4 gap-4 mb-8">
            <div className="bg-white border border-[#E5E7EB] rounded-xl shadow-sm p-4">
              <p className="text-xs font-semibold text-[#6B7280] uppercase tracking-wide mb-1">Total de Emendas</p>
              <p className="text-2xl font-bold text-[#1F2937]">{totalEmendas}</p>
            </div>
            <div className="bg-white border border-[#E5E7EB] rounded-xl shadow-sm p-4">
              <p className="text-xs font-semibold text-[#6B7280] uppercase tracking-wide mb-1">Valor Aprovado</p>
              <p className="text-2xl font-bold text-[#1F2937]">
                {formatCurrency(totalValor)}
              </p>
            </div>
            <div className="bg-white border border-[#E5E7EB] rounded-xl shadow-sm p-4">
              <p className="text-xs font-semibold text-[#6B7280] uppercase tracking-wide mb-1">Valor Pago</p>
              <p className="text-2xl font-bold text-[#1F2937]">
                {formatCurrency(totalPago)}
              </p>
            </div>
            <div className="bg-white border border-[#E5E7EB] rounded-xl shadow-sm p-4">
              <p className="text-xs font-semibold text-[#6B7280] uppercase tracking-wide mb-1">Total de Alertas</p>
              <p className="text-2xl font-bold text-red-600">{totalAlertas}</p>
            </div>
          </div>
        )}

        {/* Resultados */}
        {isLoading && (
          <div className="text-center py-12">
            <p className="text-gray-600">Carregando...</p>
          </div>
        )}

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-8">
            <p className="text-red-800">
              Erro ao carregar dados: {error instanceof Error ? error.message : 'Erro desconhecido'}
            </p>
          </div>
        )}

        {!isLoading && !error && (
          <>
            {!isSearching && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 text-center">
                <p className="text-blue-800">
                  🔍 Digite um município ou parlamentar acima para começar a busca
                </p>
              </div>
            )}

            {isSearching && filteredData && filteredData.length === 0 && (
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 text-center">
                <p className="text-yellow-800">
                  Nenhuma emenda encontrada para "{searchQuery}"
                </p>
              </div>
            )}

            {isSearching && filteredData && filteredData.length > 0 && (
              <div>
                <div className="mb-4">
                  <h2 className="text-xl font-semibold text-gray-900">
                    Resultados ({filteredData.length})
                  </h2>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {filteredData.map((emenda) => (
                    <PlacarCard key={emenda.id} emenda={emenda} />
                  ))}
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}


