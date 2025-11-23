'use client'

import { useParams } from 'next/navigation'
import { useState } from 'react'
import { useLegislation } from '@/features/legislation/hooks/useLegislations'
import { LegislationDetailCard } from '@/features/legislation/components/LegislationDetailCard'
import { Button } from '@/shared/components/ui/button'
import { ComplexityLevel } from '@/shared/types'

export default function LegislationDetailPage() {
  const params = useParams()
  const id = params.id as string
  const [simplifying, setSimplifying] = useState(false)
  const [simplifyLevel, setSimplifyLevel] = useState<ComplexityLevel>('intermediate')

  const { data: legislation, isLoading, error, refetch } = useLegislation(id)

  const handleSimplify = async (level: ComplexityLevel) => {
    setSimplifying(true)
    try {
      const response = await fetch(
        `http://localhost:8000/api/v1/legislation/${id}/simplify?level=${level}`,
        { method: 'POST' }
      )
      if (response.ok) {
        await refetch()
        alert('Texto simplificado com sucesso!')
      } else {
        alert('Erro ao simplificar texto')
      }
    } catch (error) {
      alert('Erro ao simplificar texto')
    } finally {
      setSimplifying(false)
    }
  }

  const handleSendMessage = async (legislationId: string, title: string, deputyName?: string) => {
    // Para a página de detalhes, redirecionar para o dashboard com a legislação selecionada
    const confirmed = confirm(
      `Deseja enviar uma mensagem para ${deputyName || 'o deputado'} sobre esta legislação?\n\n` +
      `Legislação: ${title}\n\n` +
      `Clique em OK para ir ao Dashboard e enviar a mensagem.`
    )
    
    if (confirmed) {
      // Redirecionar para dashboard com parâmetro
      window.location.href = `/dashboard?legislation=${legislationId}`
    }
  }

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="bg-gray-200 animate-pulse rounded-lg h-96" />
      </div>
    )
  }

  if (error || !legislation) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center">
          <p className="text-red-500">Legislação não encontrada</p>
        </div>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      {/* Simplification Controls */}
      {!legislation.simplified_content && (
        <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6 mb-6">
          <div className="mb-4">
            <h3 className="text-xl font-semibold text-gray-900 text-lg">Simplificar Texto</h3>
          </div>
          <div className="text-gray-700">
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">
                  Nível de Complexidade:
                </label>
                <div className="flex gap-2">
                  <Button
                    variant={simplifyLevel === 'basic' ? 'primary' : 'outline'}
                    size="sm"
                    onClick={() => setSimplifyLevel('basic')}
                  >
                    Básico
                  </Button>
                  <Button
                    variant={simplifyLevel === 'intermediate' ? 'primary' : 'outline'}
                    size="sm"
                    onClick={() => setSimplifyLevel('intermediate')}
                  >
                    Intermediário
                  </Button>
                  <Button
                    variant={simplifyLevel === 'advanced' ? 'primary' : 'outline'}
                    size="sm"
                    onClick={() => setSimplifyLevel('advanced')}
                  >
                    Avançado
                  </Button>
                </div>
              </div>
              <Button
                onClick={() => handleSimplify(simplifyLevel)}
                disabled={simplifying}
                className="w-full"
              >
                {simplifying ? 'Simplificando...' : '🤖 Simplificar com IA'}
              </Button>
            </div>
          </div>
        </div>
      )}

      <LegislationDetailCard
        legislation={legislation}
        onSendMessage={handleSendMessage}
      />
    </div>
  )
}



