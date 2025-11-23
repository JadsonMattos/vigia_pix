import { useState, useEffect } from 'react'
import { triangulationService } from '../services/triangulationService'

export interface TriangulationItem {
  id: string
  deputado: string
  local: string
  valor_empenhado: number
  funcao: string
  status_gov: string
  aiScore: number | null
  aiReason: string | null
  executorData: ExecutorData | null
  parlaData: ParliamentaryData | null
}

export interface ParliamentaryData {
  objeto: string
  justificativa: string
}

export interface ExecutorData {
  progresso: number
  fotos: string
  relatorio: string
}

export function useTriangulationData() {
  const [data, setData] = useState<TriangulationItem[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const loadData = async () => {
      setIsLoading(true)
      const result = await triangulationService.getData()
      setData(result)
      setIsLoading(false)
    }
    loadData()
  }, [])

  const updateItem = (id: string, updates: Partial<TriangulationItem>) => {
    setData(prev => prev.map(item => 
      item.id === id ? { ...item, ...updates } : item
    ))
  }

  return { data, isLoading, updateItem }
}


