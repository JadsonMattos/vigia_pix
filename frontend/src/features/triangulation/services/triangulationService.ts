import { TriangulationItem, ParliamentaryData, ExecutorData } from '../hooks/useTriangulationData'
import { openAIService } from './openAIService'

// Dados simulados para apresentação
const mockData: TriangulationItem[] = [
  {
    id: 'EM-2025-4290-0008',
    deputado: 'Abilio Brunini',
    local: 'Várzea Grande - MT',
    valor_empenhado: 500000,
    funcao: 'Saúde',
    status_gov: 'Empenhado',
    aiScore: null,
    aiReason: null,
    executorData: null,
    parlaData: null
  },
  {
    id: 'EM-2025-1055-0012',
    deputado: 'Tabata Amaral',
    local: 'São Paulo - SP',
    valor_empenhado: 1500000,
    funcao: 'Educação',
    status_gov: 'Pago',
    aiScore: null,
    aiReason: null,
    executorData: null,
    parlaData: null
  },
  {
    id: 'EM-2025-1234-0056',
    deputado: 'Erika Kokay',
    local: 'Brasília - DF',
    valor_empenhado: 800000,
    funcao: 'Infraestrutura',
    status_gov: 'Liquidado',
    aiScore: 85,
    aiReason: '✅ INTEGRIDADE TOTAL: Dados do Portal coincidem com o Processo SEI e as fotos da obra comprovam o progresso informado.',
    executorData: {
      progresso: 75,
      fotos: 'https://drive.google.com/fotos-obra',
      relatorio: 'Obra em andamento, 75% concluída conforme planejado.'
    },
    parlaData: {
      objeto: 'Reforma e modernização de escola pública',
      justificativa: 'Melhoria da infraestrutura educacional para atender 500 alunos'
    }
  }
]

class TriangulationService {
  private data: TriangulationItem[] = [...mockData]

  async getData(): Promise<TriangulationItem[]> {
    // Simula delay de API
    await new Promise(resolve => setTimeout(resolve, 500))
    return [...this.data]
  }

  async submitParliamentaryData(
    id: string,
    parlaData: ParliamentaryData
  ): Promise<TriangulationItem> {
    const item = this.data.find(d => d.id === id)
    if (!item) throw new Error('Item não encontrado')

    item.parlaData = parlaData

    // Chama IA para auditar
    const audit = await openAIService.auditAmendment(item)
    item.aiScore = audit.score
    item.aiReason = audit.reason

    return item
  }

  async submitExecutorData(
    id: string,
    executorData: ExecutorData
  ): Promise<TriangulationItem> {
    const item = this.data.find(d => d.id === id)
    if (!item) throw new Error('Item não encontrado')

    item.executorData = executorData

    // Chama IA para auditar
    const audit = await openAIService.auditAmendment(item)
    item.aiScore = audit.score
    item.aiReason = audit.reason

    return item
  }
}

export const triangulationService = new TriangulationService()


