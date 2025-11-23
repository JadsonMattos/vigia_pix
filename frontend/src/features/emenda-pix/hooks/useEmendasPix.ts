import { useQuery } from '@tanstack/react-query'
import { api } from '@/core/api/client'

export interface EmendaPix {
  id: string
  numero_emenda: string
  ano: number
  tipo: string
  autor_nome: string
  autor_partido?: string
  autor_uf?: string
  destinatario_tipo: string
  destinatario_nome: string
  destinatario_uf?: string
  valor_aprovado: number
  valor_empenhado: number
  valor_liquidado: number
  valor_pago: number
  objetivo?: string
  area?: string
  status_execucao: string
  percentual_executado: number
  data_inicio?: string
  data_prevista_conclusao?: string
  plano_trabalho?: Array<{
    meta: number
    descricao: string
    valor: number
    prazo: string
    status: string
  }>
  numero_metas: number
  metas_concluidas: number
  alertas?: Array<{
    tipo: string
    severidade: string
    mensagem: string
    data: string
  }>
  descricao_detalhada?: string
  analise_ia?: {
    transparencia_score: number
    execucao_score: number
    risco_desvio: number
    recomendacoes: string[]
    plano_acao?: {
      situacao_plano_acao: string
      nome_beneficiario: string
      descricao_programacao_orcamentaria: string
      codigo_emenda_formatado: string
    }
    categoria_gasto?: string
    objeto_principal?: string
    localizacao_extraida?: string
    anomalias_cruzamento?: Array<{
      tipo: string
      severidade: string
      mensagem: string
      detalhes: {
        valor_pago: number
        percentual_pago: number
        situacao_plano: string
      }
    }>
  }
  risco_desvio?: number
  tem_noticias: boolean
  noticias_relacionadas?: Array<{
    titulo: string
    fonte: string
    data: string
  }>
  processo_sei?: string
  link_portal_transparencia?: string
  data_real_conclusao?: string
  documentos_comprobatórios?: Array<{
    tipo: string
    url: string
    descricao?: string
  }>
  fotos_georreferenciadas?: Array<{
    id: string
    url: string
    latitude: number
    longitude: number
    tipo: string
    data_upload: string
    validacao_geofencing?: boolean
  }>
  validacao_geofencing?: boolean
  created_at: string
  updated_at: string
}

export interface EmendaPixListResponse {
  items: EmendaPix[]
  total: number
  limit: number
  offset: number
}

interface UseEmendasPixParams {
  limit?: number
  offset?: number
  autor_nome?: string
  destinatario_uf?: string
  area?: string
  status_execucao?: string
}

export function useEmendasPix(params: UseEmendasPixParams = {}) {
  return useQuery<EmendaPixListResponse>({
    queryKey: ['emendas-pix', params],
    queryFn: async () => {
      const searchParams = new URLSearchParams()
      if (params.limit) searchParams.append('limit', params.limit.toString())
      if (params.offset) searchParams.append('offset', params.offset.toString())
      if (params.autor_nome) searchParams.append('autor_nome', params.autor_nome)
      if (params.destinatario_uf) searchParams.append('destinatario_uf', params.destinatario_uf)
      if (params.area) searchParams.append('area', params.area)
      if (params.status_execucao) searchParams.append('status_execucao', params.status_execucao)
      
      return api.get<EmendaPixListResponse>(`/emenda-pix?${searchParams.toString()}`)
    }
  })
}

export function useEmendaPix(id: string) {
  return useQuery<EmendaPix>({
    queryKey: ['emenda-pix', id],
    queryFn: async () => {
      return api.get<EmendaPix>(`/emenda-pix/${id}`)
    },
    enabled: !!id
  })
}

