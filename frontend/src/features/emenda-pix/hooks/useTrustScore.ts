import { useQuery } from '@tanstack/react-query'
import { api } from '@/core/api/client'

export interface TrustScoreResponse {
  success: boolean
  trust_score: number
  level: 'excelente' | 'bom' | 'regular' | 'ruim'
  factors: {
    execucao: {
      score: number
      weight: number
      contribution: number
      details: string
    }
    tempo: {
      score: number
      weight: number
      contribution: number
      details: string
    }
    documentacao: {
      score: number
      weight: number
      contribution: number
      details: string
    }
    risco: {
      score: number
      weight: number
      contribution: number
      details: string
    }
    historico: {
      score: number
      weight: number
      contribution: number
      details: string
    }
  }
  recommendations: string[]
}

export function useTrustScore(emendaId: string | undefined) {
  return useQuery<TrustScoreResponse>({
    queryKey: ['trust-score', emendaId],
    queryFn: async () => {
      if (!emendaId) throw new Error('Emenda ID is required')
      return api.get<TrustScoreResponse>(`/emenda-pix/${emendaId}/trust-score`)
    },
    enabled: !!emendaId,
    staleTime: 30000, // 30 segundos
  })
}

