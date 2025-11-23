'use client'

import { useState, useEffect } from 'react'
import { useTriangulationData } from '../hooks/useTriangulationData'
import { triangulationService } from '../services/triangulationService'
import { ParliamentaryData } from '../hooks/useTriangulationData'

export function TriangulationParliamentaryView() {
  const { data, updateItem } = useTriangulationData()
  const [selectedEmenda, setSelectedEmenda] = useState('')
  const [objeto, setObjeto] = useState('')
  const [justificativa, setJustificativa] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleSubmit = async () => {
    if (!selectedEmenda || !objeto || !justificativa) {
      alert('Por favor, preencha todos os campos.')
      return
    }

    setIsSubmitting(true)
    try {
      const parlaData: ParliamentaryData = { objeto, justificativa }
      const updated = await triangulationService.submitParliamentaryData(selectedEmenda, parlaData)
      updateItem(selectedEmenda, updated)
      
      alert('Dados do Gabinete registrados com sucesso!')
      setObjeto('')
      setJustificativa('')
    } catch (error) {
      alert('Erro ao registrar dados. Tente novamente.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="bg-white rounded-xl shadow-md border-l-4 border-purple-500 p-6">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-purple-600 mb-2">🏛️ Input Parlamentar</h2>
        <p className="text-gray-600">Enriqueça os dados financeiros do Portal com o impacto social.</p>
      </div>

      <div className="mb-6">
        <label className="block text-sm font-semibold text-gray-700 mb-2">
          <span className="inline-block px-2 py-1 text-xs font-bold bg-blue-100 text-blue-700 rounded mb-1">
            Portal
          </span>
          <br />
          Selecione Dado Existente
        </label>
        <select
          value={selectedEmenda}
          onChange={(e) => setSelectedEmenda(e.target.value)}
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 text-[#1F2937] bg-white"
        >
          <option value="">Selecione uma emenda...</option>
          {data.map(item => (
            <option key={item.id} value={item.id}>
              {item.deputado} - {new Intl.NumberFormat('pt-BR', {
                style: 'currency',
                currency: 'BRL',
                notation: 'compact'
              }).format(item.valor_empenhado)}
            </option>
          ))}
        </select>
      </div>

      <div className="bg-gray-50 p-4 rounded-lg border border-dashed border-gray-300 mb-6">
        <strong className="block text-purple-600 mb-3">Novos Dados (VigiaPix):</strong>
        
        <div className="mb-4">
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            Objeto Detalhado:
          </label>
          <input
            type="text"
            value={objeto}
            onChange={(e) => setObjeto(e.target.value)}
            placeholder="Ex: Aquisição de Tomógrafo..."
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 text-[#1F2937] bg-white placeholder:text-gray-400"
          />
        </div>

        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            Justificativa:
          </label>
          <textarea
            value={justificativa}
            onChange={(e) => setJustificativa(e.target.value)}
            rows={3}
            placeholder="Por que este recurso é necessário?"
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 text-[#1F2937] bg-white placeholder:text-gray-400"
          />
        </div>
      </div>

      <button
        onClick={handleSubmit}
        disabled={isSubmitting}
        className="w-full bg-purple-600 hover:bg-purple-700 text-white font-semibold py-3 px-6 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {isSubmitting ? '⏳ Processando...' : 'Registrar Dados'}
      </button>
    </div>
  )
}


