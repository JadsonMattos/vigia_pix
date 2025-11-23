'use client'

import { useEffect, useState } from 'react'
import { useTriangulationData, TriangulationItem } from '../hooks/useTriangulationData'

interface DetailModalProps {
  itemId: string
  onClose: () => void
}

export function DetailModal({ itemId, onClose }: DetailModalProps) {
  const { data } = useTriangulationData()
  const [item, setItem] = useState<TriangulationItem | null>(null)

  useEffect(() => {
    const found = data.find(d => d.id === itemId)
    setItem(found || null)
  }, [itemId, data])

  if (!item) return null

  const temParla = item.parlaData !== null
  const temExec = item.executorData !== null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black bg-opacity-50 backdrop-blur-sm">
      <div className="bg-white rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto shadow-2xl">
        <div className="p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold text-gray-900">Dossiê Cruzado</h2>
            <button
              onClick={onClose}
              className="text-3xl text-gray-400 hover:text-gray-600 transition-colors"
            >
              &times;
            </button>
          </div>

          {/* Fonte 1: Portal */}
          <div className="bg-blue-50 p-4 rounded-lg mb-4 border-l-4 border-blue-500">
            <strong className="block text-blue-600 mb-3">1. DADOS DO PORTAL (Automático)</strong>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
              <div>
                <small className="text-gray-600">Valor:</small>
                <div className="font-bold text-gray-900">
                  {new Intl.NumberFormat('pt-BR', {
                    style: 'currency',
                    currency: 'BRL'
                  }).format(item.valor_empenhado)}
                </div>
              </div>
              <div>
                <small className="text-gray-600">Deputado:</small>
                <div className="font-bold text-gray-900">{item.deputado}</div>
              </div>
              <div>
                <small className="text-gray-600">Local:</small>
                <div className="font-bold text-gray-900">{item.local}</div>
              </div>
            </div>
          </div>

          {/* Fonte 2: Gabinete */}
          <div className={`p-4 rounded-lg mb-4 border-l-4 ${
            temParla ? 'bg-purple-50 border-purple-500' : 'bg-gray-50 border-gray-300'
          }`}>
            <strong className={`block mb-3 ${
              temParla ? 'text-purple-600' : 'text-gray-400'
            }`}>
              2. DADOS DO GABINETE (Enriquecimento)
            </strong>
            {temParla ? (
              <div className="space-y-3 text-sm">
                <div>
                  <small className="text-gray-600">Objeto Real:</small>
                  <p className="font-medium text-gray-900">{item.parlaData!.objeto}</p>
                </div>
                <div>
                  <small className="text-gray-600">Justificativa:</small>
                  <p className="font-medium text-gray-900">{item.parlaData!.justificativa}</p>
                </div>
              </div>
            ) : (
              <p className="text-gray-400 italic text-sm">Aguardando input do parlamentar...</p>
            )}
          </div>

          {/* Fonte 3: Executor */}
          <div className={`p-4 rounded-lg mb-4 border-l-4 ${
            temExec ? 'bg-orange-50 border-orange-500' : 'bg-gray-50 border-gray-300'
          }`}>
            <strong className={`block mb-3 ${
              temExec ? 'text-orange-600' : 'text-gray-400'
            }`}>
              3. DADOS DO EXECUTOR (Prova de Vida)
            </strong>
            {temExec ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                <div>
                  <small className="text-gray-600">Progresso:</small>
                  <div className="font-bold text-orange-600">{item.executorData!.progresso}%</div>
                </div>
                <div>
                  <small className="text-gray-600">Fotos:</small>
                  <div>
                    <a href={item.executorData!.fotos} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                      Link Verificado
                    </a>
                  </div>
                </div>
                <div className="md:col-span-2">
                  <small className="text-gray-600">Relatório:</small>
                  <p className="font-medium text-gray-900">{item.executorData!.relatorio}</p>
                </div>
              </div>
            ) : (
              <p className="text-gray-400 italic text-sm">Aguardando prestação de contas...</p>
            )}
          </div>

          {/* Parecer da IA */}
          {item.aiReason && (
            <div className="bg-green-50 p-4 rounded-lg border border-green-200">
              <strong className="block text-green-600 mb-2">
                🤖 PARECER DA IA (OpenAI):
              </strong>
              <p className="text-sm text-gray-700">{item.aiReason}</p>
              {item.aiScore !== null && (
                <div className="mt-3">
                  <span className="text-sm text-gray-600">Score: </span>
                  <strong className={`text-lg ${
                    item.aiScore > 80 ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {item.aiScore}/100
                  </strong>
                </div>
              )}
            </div>
          )}

          <button
            onClick={onClose}
            className="w-full mt-6 bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-lg transition-colors"
          >
            Fechar
          </button>
        </div>
      </div>
    </div>
  )
}


