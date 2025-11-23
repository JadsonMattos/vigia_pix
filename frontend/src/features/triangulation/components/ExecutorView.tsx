'use client'

import { useState } from 'react'
import { useTriangulationData } from '../hooks/useTriangulationData'
import { triangulationService } from '../services/triangulationService'
import { ExecutorData } from '../hooks/useTriangulationData'

export function TriangulationExecutorView() {
  const { data, updateItem } = useTriangulationData()
  const [selectedEmenda, setSelectedEmenda] = useState('')
  const [progresso, setProgresso] = useState(0)
  const [fotos, setFotos] = useState('')
  const [relatorio, setRelatorio] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleSubmit = async () => {
    if (!selectedEmenda) {
      alert('Por favor, selecione uma emenda.')
      return
    }

    setIsSubmitting(true)
    try {
      const executorData: ExecutorData = {
        progresso,
        fotos,
        relatorio
      }
      const updated = await triangulationService.submitExecutorData(selectedEmenda, executorData)
      updateItem(selectedEmenda, updated)
      
      alert('Prestação de Contas enviada com sucesso!')
      setProgresso(0)
      setFotos('')
      setRelatorio('')
    } catch (error) {
      alert('Erro ao enviar prestação. Tente novamente.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="bg-white rounded-xl shadow-md border-l-4 border-orange-500 p-6">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-orange-600 mb-2">🚜 Input Executor</h2>
        <p className="text-gray-600">Prestação de contas física para liberar recursos.</p>
      </div>

      <div className="mb-6">
        <label className="block text-sm font-semibold text-gray-700 mb-2">
          <span className="inline-block px-2 py-1 text-xs font-bold bg-blue-100 text-blue-700 rounded mb-1">
            Portal
          </span>
          <br />
          Selecione Emenda Empenhada
        </label>
        <select
          value={selectedEmenda}
          onChange={(e) => setSelectedEmenda(e.target.value)}
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 text-[#1F2937] bg-white"
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
        <strong className="block text-orange-600 mb-3">Evidências Físicas:</strong>

        <div className="mb-4">
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            Progresso Físico:
          </label>
          <div className="flex items-center gap-4">
            <input
              type="range"
              min="0"
              max="100"
              value={progresso}
              onChange={(e) => setProgresso(parseInt(e.target.value))}
              className="flex-1"
            />
            <span className="font-bold text-orange-600 w-16 text-right">{progresso}%</span>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Link Fotos:
            </label>
            <input
              type="text"
              value={fotos}
              onChange={(e) => setFotos(e.target.value)}
              placeholder="URL Drive..."
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 text-[#1F2937] bg-white placeholder:text-gray-400"
            />
          </div>
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Relatório:
            </label>
            <input
              type="text"
              value={relatorio}
              onChange={(e) => setRelatorio(e.target.value)}
              placeholder="Resumo..."
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 text-[#1F2937] bg-white placeholder:text-gray-400"
            />
          </div>
        </div>
      </div>

      <button
        onClick={handleSubmit}
        disabled={isSubmitting}
        className="w-full bg-orange-600 hover:bg-orange-700 text-white font-semibold py-3 px-6 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {isSubmitting ? '⏳ Processando...' : 'Enviar Prestação'}
      </button>
    </div>
  )
}


