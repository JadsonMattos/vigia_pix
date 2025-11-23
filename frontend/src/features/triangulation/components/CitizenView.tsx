'use client'

import { useState, useEffect } from 'react'
import { useTriangulationData } from '../hooks/useTriangulationData'
import { DetailModal } from './DetailModal'

export function TriangulationCitizenView() {
  const { data, isLoading } = useTriangulationData()
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedItem, setSelectedItem] = useState<string | null>(null)

  const filteredData = data.filter(item => {
    if (!searchQuery) return true
    const query = searchQuery.toLowerCase()
    return (
      item.id.toLowerCase().includes(query) ||
      item.deputado.toLowerCase().includes(query) ||
      item.local.toLowerCase().includes(query)
    )
  })

  return (
    <>
      <div className="bg-white rounded-xl shadow-md border border-gray-200 p-6 mb-6">
        <div className="mb-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Monitoramento Unificado</h2>
          <p className="text-gray-600">Dados consolidados de 3 fontes oficiais.</p>
        </div>
        
        <div className="grid grid-cols-2 gap-4 mb-6">
          <div>
            <span className="text-gray-500 text-sm">Total Auditado</span>
            <div className="text-2xl font-bold text-gray-900">R$ 4.0 Mi</div>
          </div>
          <div>
            <span className="text-gray-500 text-sm">Integridade Média</span>
            <div className="text-2xl font-bold text-green-600">92/100</div>
          </div>
        </div>
        
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="🔍 Buscar Emenda, Deputado ou Local..."
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-[#1F2937] bg-white placeholder:text-gray-400"
        />
      </div>

      <div className="bg-white rounded-xl shadow-md border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase">Emenda (Portal)</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase">Parlamentar</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase">Status Gov</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase">Score Cruzado</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase">Ação</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {isLoading ? (
                <tr>
                  <td colSpan={5} className="px-4 py-8 text-center text-gray-500">
                    Carregando...
                  </td>
                </tr>
              ) : filteredData.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-4 py-8 text-center text-gray-500">
                    Nenhuma emenda encontrada
                  </td>
                </tr>
              ) : (
                filteredData.map((item) => (
                  <tr key={item.id} className="hover:bg-gray-50">
                    <td className="px-4 py-4">
                      <span className="inline-block px-2 py-1 text-xs font-bold bg-blue-100 text-blue-700 rounded mb-1">
                        Portal
                      </span>
                      <br />
                      <strong className="text-gray-900">{item.id}</strong>
                    </td>
                    <td className="px-4 py-4">
                      <div className="font-medium text-gray-900">{item.deputado}</div>
                      <div className="text-sm text-gray-500">{item.local}</div>
                    </td>
                    <td className="px-4 py-4">
                      <span className="inline-block px-3 py-1 text-xs font-semibold bg-blue-100 text-blue-800 rounded-full">
                        {item.status_gov}
                      </span>
                    </td>
                    <td className="px-4 py-4">
                      {item.aiScore !== null ? (
                        <strong className={`text-lg ${item.aiScore > 80 ? 'text-green-600' : 'text-red-600'}`}>
                          {item.aiScore}/100
                        </strong>
                      ) : (
                        <span className="text-gray-400 text-sm">Pendente</span>
                      )}
                    </td>
                    <td className="px-4 py-4">
                      <button
                        onClick={() => setSelectedItem(item.id)}
                        className="px-3 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                      >
                        <i className="fa-solid fa-eye"></i>
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {selectedItem && (
        <DetailModal
          itemId={selectedItem}
          onClose={() => setSelectedItem(null)}
        />
      )}
    </>
  )
}


