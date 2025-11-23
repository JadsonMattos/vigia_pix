'use client'

import { useState } from 'react'
import { useLegislations } from '@/features/legislation/hooks/useLegislations'
import { LegislationList } from '@/features/legislation/components/LegislationList'
import { Button } from '@/shared/components/ui/button'
import { Modal } from '@/shared/components/ui/modal'
import { Input } from '@/shared/components/ui/input'
import { Select } from '@/shared/components/ui/select'
import { api } from '@/core/api/client'

export default function DashboardPage() {
  const [page, setPage] = useState(0)
  const limit = 12
  const offset = page * limit
  const [manifestationCount, setManifestationCount] = useState(0)
  
  // Filters
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [dateFilter, setDateFilter] = useState<string>('all')
  const [searchQuery, setSearchQuery] = useState<string>('')
  
  // Modal
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [selectedLegislation, setSelectedLegislation] = useState<{id: string, title: string, deputyName?: string} | null>(null)
  const [formData, setFormData] = useState({ name: '', email: '', message: '' })

  const { data, isLoading, error, refetch } = useLegislations({ limit, offset })

  const handleViewDetails = (id: string) => {
    window.location.href = `/legislation/${id}`
  }

  const handleSendMessage = async (legislationId: string, title: string, deputyName?: string) => {
    setSelectedLegislation({ id: legislationId, title, deputyName: deputyName || 'Desconhecido' })
    setIsModalOpen(true)
  }
  
  const handleSubmitMessage = async () => {
    if (!formData.name || !formData.message) {
      alert('Por favor, preencha pelo menos o nome e a mensagem.')
      return
    }
    
    setManifestationCount(prev => prev + 1)
    
    console.log('Mensagem enviada:', {
      legislationId: selectedLegislation?.id,
      deputyName: selectedLegislation?.deputyName,
      ...formData
    })
    
    setIsModalOpen(false)
    setFormData({ name: '', email: '', message: '' })
    setSelectedLegislation(null)
    
    alert(`✅ Mensagem enviada com sucesso!\n\nTotal de manifestações: ${manifestationCount + 1}`)
  }
  
  const handleCloseModal = () => {
    setIsModalOpen(false)
    setFormData({ name: '', email: '', message: '' })
    setSelectedLegislation(null)
  }

  const [isSyncing, setIsSyncing] = useState(false)
  
  const handleSync = async () => {
    setIsSyncing(true)
    try {
      const response = await api.post<{ message: string; count: number }>('/legislation/sync?days=30')
      const count = response.count || 0
      if (count > 0) {
        alert(`✅ ${count} nova(s) legislação(ões) sincronizada(s) com sucesso!`)
      } else {
        alert('ℹ️ Nenhuma nova legislação encontrada. Todas já estão sincronizadas.')
      }
      setStatusFilter('all')
      setDateFilter('all')
      setSearchQuery('')
      setPage(0)
      await refetch()
    } catch (error) {
      console.error('Erro ao sincronizar:', error)
      alert('❌ Erro ao sincronizar legislações. Tente novamente.')
    } finally {
      setIsSyncing(false)
    }
  }

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center py-12">
          <div className="text-6xl mb-4">❌</div>
          <p className="text-red-500 text-lg">Erro ao carregar dashboard</p>
        </div>
      </div>
    )
  }

  const filteredLegislations = data?.items.filter(legislation => {
    if (statusFilter !== 'all') {
      const statusLower = legislation.status.toLowerCase()
      if (statusFilter === 'tramitacao' && !statusLower.includes('tramitacao')) return false
      if (statusFilter === 'aprovado' && !statusLower.includes('aprovado')) return false
      if (statusFilter === 'arquivado' && !statusLower.includes('arquivado')) return false
    }
    
    if (dateFilter !== 'all') {
      const date = new Date(legislation.created_at)
      const now = new Date()
      const daysDiff = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24))
      
      if (dateFilter === '30' && daysDiff > 30) return false
      if (dateFilter === '90' && daysDiff > 90) return false
    }
    
    if (searchQuery) {
      const query = searchQuery.toLowerCase()
      const matchesTitle = legislation.title.toLowerCase().includes(query)
      const matchesAuthor = legislation.author.toLowerCase().includes(query)
      const matchesContent = legislation.content.toLowerCase().includes(query)
      if (!matchesTitle && !matchesAuthor && !matchesContent) return false
    }
    
    return true
  }) || []

  const totalLegislations = data?.total || 0
  const activeLegislations = data?.items.filter(l => 
    l.status.toLowerCase().includes('tramitacao') || l.status.toLowerCase().includes('aprovado')
  ).length || 0

  return (
    <div className="min-h-screen bg-[#F3F4F6]">
      <div className="container mx-auto px-4 sm:px-5 md:px-6 lg:px-8 py-6 sm:py-8 md:py-10 lg:py-12 max-w-7xl">
        {/* Header Melhorado */}
        <div className="mb-6 sm:mb-8 md:mb-12">
          <div className="flex flex-col md:flex-row md:justify-between md:items-center mb-6 gap-4">
            <div>
              <h1 className="text-2xl sm:text-3xl md:text-4xl font-extrabold text-[#1F2937] mb-2 sm:mb-3">
                📊 Dashboard - VigiaPix
              </h1>
              <p className="text-sm sm:text-base md:text-lg text-[#6B7280]">
                Acompanhe e participe das discussões legislativas
              </p>
            </div>
            <Button 
              onClick={handleSync} 
              variant="outline"
              disabled={isSyncing}
              className="w-full md:w-auto px-6 py-3 border-2 border-blue-600 text-blue-600 hover:bg-blue-50 font-semibold rounded-lg shadow-md hover:shadow-lg transition-all duration-300"
            >
              {isSyncing ? '⏳ Sincronizando...' : '🔄 Sincronizar Legislações'}
            </Button>
          </div>

          {/* Stats Cards Melhorados */}
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4 mb-6 sm:mb-8">
            <div className="bg-white border border-[#E5E7EB] rounded-xl shadow-sm p-4 sm:p-6 hover:shadow-md transition-shadow">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-sm font-semibold text-[#6B7280] uppercase tracking-wide">Total de Legislações</h3>
                <div className="text-2xl">📜</div>
              </div>
              <div className="text-3xl md:text-4xl font-bold text-[#1F2937]">{totalLegislations}</div>
            </div>

            <div className="bg-white border border-[#E5E7EB] rounded-xl shadow-sm p-6 hover:shadow-md transition-shadow">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-sm font-semibold text-[#6B7280] uppercase tracking-wide">Em Tramitação</h3>
                <div className="text-2xl">⚡</div>
              </div>
              <div className="text-3xl md:text-4xl font-bold text-[#1F2937]">{activeLegislations}</div>
            </div>

            <div className="bg-white border border-[#E5E7EB] rounded-xl shadow-sm p-6 hover:shadow-md transition-shadow">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-sm font-semibold text-[#6B7280] uppercase tracking-wide">Manifestações</h3>
                <div className="text-2xl">💬</div>
              </div>
              <div className="text-3xl md:text-4xl font-bold text-[#1F2937]">{manifestationCount}</div>
              <p className="text-xs text-[#6B7280] mt-1">Cidadãos que se manifestaram</p>
            </div>

            <div className="bg-white border border-[#E5E7EB] rounded-xl shadow-sm p-6 hover:shadow-md transition-shadow">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-sm font-semibold text-[#6B7280] uppercase tracking-wide">Taxa de Engajamento</h3>
                <div className="text-2xl">📈</div>
              </div>
              <div className="text-3xl md:text-4xl font-bold text-[#1F2937]">
                {totalLegislations > 0 
                  ? Math.round((manifestationCount / totalLegislations) * 100) 
                  : 0}%
              </div>
            </div>
          </div>
        </div>

        {/* Filters Melhorados */}
        <div className="mb-6 sm:mb-8">
          <div className="bg-white border border-[#E5E7EB] rounded-xl shadow-sm p-4 sm:p-6">
            <h2 className="text-base sm:text-lg font-semibold text-[#1F2937] mb-4">🔍 Filtros de Busca</h2>
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              <div>
                <Input
                  label="Buscar"
                  placeholder="Título, autor ou conteúdo..."
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
                    { value: 'tramitacao', label: 'Em Tramitação' },
                    { value: 'aprovado', label: 'Aprovado' },
                    { value: 'arquivado', label: 'Arquivado' }
                  ]}
                />
              </div>
              <div>
                <Select
                  label="Data"
                  value={dateFilter}
                  onChange={(e) => setDateFilter(e.target.value)}
                  options={[
                    { value: 'all', label: 'Todas' },
                    { value: '30', label: 'Últimos 30 dias' },
                    { value: '90', label: 'Últimos 90 dias' }
                  ]}
                />
              </div>
              <div className="flex items-end">
                <Button
                  variant="outline"
                  onClick={() => {
                    setStatusFilter('all')
                    setDateFilter('all')
                    setSearchQuery('')
                  }}
                  className="w-full border-2 hover:bg-gray-50"
                >
                  🔄 Limpar Filtros
                </Button>
              </div>
            </div>
          </div>
        </div>

        {/* Legislation List */}
        <div>
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl md:text-3xl font-bold text-gray-900">
              Legislações {filteredLegislations.length !== data?.items.length 
                ? `(${filteredLegislations.length} de ${data?.items.length})` 
                : ''}
            </h2>
          </div>
          <LegislationList
            legislations={filteredLegislations}
            onViewDetails={handleViewDetails}
            isLoading={isLoading}
            onSendMessage={(id, deputyName) => {
              const legislation = data?.items.find(l => l.id === id)
              if (legislation) {
                handleSendMessage(id, legislation.title, deputyName)
              }
            }}
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
              <span className="flex items-center px-6 py-2 bg-white rounded-lg border border-[#E5E7EB] font-semibold text-[#1F2937]">
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

        {/* Modal de Envio de Mensagem */}
        <Modal
          isOpen={isModalOpen}
          onClose={handleCloseModal}
          title="Enviar Mensagem ao Deputado"
        >
          <div className="space-y-4">
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <p className="text-sm text-gray-700 mb-1">
                <strong>Legislação:</strong> {selectedLegislation?.title}
              </p>
              {selectedLegislation?.deputyName && (
                <p className="text-sm text-gray-700">
                  <strong>Deputado:</strong> {selectedLegislation.deputyName}
                </p>
              )}
            </div>
            
            <Input
              label="Seu Nome *"
              placeholder="Digite seu nome"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            />
            
            <Input
              label="Seu Email (opcional)"
              type="email"
              placeholder="seu@email.com"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
            />
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Sua Mensagem *
              </label>
              <textarea
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                rows={4}
                placeholder="Digite sua mensagem sobre esta legislação..."
                value={formData.message}
                onChange={(e) => setFormData({ ...formData, message: e.target.value })}
              />
            </div>
            
            <div className="flex gap-2 pt-4">
              <Button
                variant="outline"
                onClick={handleCloseModal}
                className="flex-1 border-2"
              >
                Cancelar
              </Button>
              <Button
                onClick={handleSubmitMessage}
                className="flex-1 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800"
              >
                📢 Enviar Mensagem
              </Button>
            </div>
          </div>
        </Modal>
      </div>
    </div>
  )
}
