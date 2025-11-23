import { useQuery } from '@tanstack/react-query'
import { api } from '@/core/api/client'
import { Legislation } from '@/shared/types'

interface UseLegislationsOptions {
  limit?: number
  offset?: number
  enabled?: boolean
}

interface LegislationListResponse {
  items: Legislation[]
  total: number
  limit: number
  offset: number
}

export function useLegislations({ 
  limit = 100, 
  offset = 0,
  enabled = true 
}: UseLegislationsOptions = {}) {
  return useQuery({
    queryKey: ['legislations', limit, offset],
    queryFn: async () => {
      const response = await api.get<LegislationListResponse>(
        `/legislation?limit=${limit}&offset=${offset}`
      )
      return response
    },
    enabled
  })
}

export function useLegislation(id: string, enabled: boolean = true) {
  return useQuery({
    queryKey: ['legislation', id],
    queryFn: async () => {
      const response = await api.get<Legislation>(`/legislation/${id}`)
      return response
    },
    enabled: enabled && !!id
  })
}



