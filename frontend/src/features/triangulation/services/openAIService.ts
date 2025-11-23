import { TriangulationItem } from '../hooks/useTriangulationData'

interface AuditResult {
  score: number
  reason: string
}

class OpenAIService {
  /**
   * Audita uma emenda usando OpenAI (simulado para apresentação)
   * Em produção, isso chamaria a API real da OpenAI
   */
  async auditAmendment(amendment: TriangulationItem): Promise<AuditResult> {
    // Simula delay de chamada à API
    await new Promise(resolve => setTimeout(resolve, 1500))

    let score = 0
    const reasons: string[] = []

    // BASE: Portal Transparência (Sempre tem 20pts se tiver dinheiro)
    if (amendment.valor_empenhado > 0) {
      score += 20
    }

    // FONTE 2: Parlamentar (Justificativa de Impacto)
    if (amendment.parlaData && amendment.parlaData.justificativa.length > 10) {
      score += 30
    } else {
      reasons.push('Falta a justificativa de impacto social do parlamentar.')
    }

    // FONTE 3: Executor (Progresso Físico)
    if (amendment.executorData) {
      score += 20 // Enviou dados
      if (parseInt(String(amendment.executorData.progresso)) > 0) {
        score += 10 // Obra andou
      }
      if (amendment.executorData.fotos.length > 5) {
        score += 20 // Tem fotos
      }
    } else {
      reasons.push('Município não informou progresso físico nem fotos.')
    }

    // Parecer Cruzado
    let finalReason = ''
    if (score >= 90) {
      finalReason = '✅ INTEGRIDADE TOTAL: Dados do Portal coincidem com o Processo SEI e as fotos da obra comprovam o progresso informado.'
    } else if (score >= 50) {
      finalReason = '⚠️ ALERTA DE GESTÃO: Recurso empenhado (Portal), mas execução física lenta ou pouco documentada pelo município.'
    } else {
      finalReason = '🚨 RISCO DE INEFICIÊNCIA: Dinheiro liberado sem justificativa clara de impacto e sem rastro de obra.'
    }

    return { score, reason: finalReason }
  }
}

export const openAIService = new OpenAIService()


