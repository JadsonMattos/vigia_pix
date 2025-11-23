// Shared types

export interface Legislation {
  id: string
  external_id: string
  title: string
  content: string
  author: string
  status: string
  created_at: string
  updated_at: string
  simplified_content?: string
  complexity_score?: number
  impact_analysis?: Record<string, any>
  original_length?: number
  simplified_length?: number
}

export interface Alert {
  id: string
  legislation_id: string
  user_id: string
  message: string
  created_at: string
}

export type ComplexityLevel = 'basic' | 'intermediate' | 'advanced'




