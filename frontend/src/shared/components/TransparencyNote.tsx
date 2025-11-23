'use client'

export function TransparencyNote() {
  return (
    <div className="mt-8 p-6 bg-gradient-to-r from-blue-50 to-indigo-50 border-2 border-blue-200 rounded-xl">
      <div className="flex items-start gap-3">
        <div className="text-3xl">📋</div>
        <div className="flex-1">
          <h3 className="font-bold text-lg text-gray-900 mb-2">
            Nota de Transparência Pública
          </h3>
          <p className="text-sm text-gray-700 leading-relaxed mb-3">
            O VigiaPix é uma ferramenta de fiscalização cidadã que integra dados públicos de múltiplas fontes 
            para promover transparência e controle social sobre a execução de Emendas Pix. 
            Todas as informações apresentadas são baseadas em dados oficiais disponíveis publicamente.
          </p>
          <div className="text-xs text-gray-600 space-y-1">
            <p><strong>Fontes de Dados:</strong> Portal da Transparência, Transferegov.br, CEIS</p>
            <p><strong>IA Utilizada:</strong> OpenAI GPT (análise e classificação de dados)</p>
            <p><strong>Última Atualização:</strong> {new Date().toLocaleDateString('pt-BR')}</p>
          </div>
        </div>
      </div>
    </div>
  )
}


