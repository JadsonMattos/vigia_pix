import Link from 'next/link'
import Image from 'next/image'

export default function Home() {
  return (
    <main className="min-h-screen bg-[#020617] text-white overflow-x-hidden">
      {/* Hero Section - Exatamente como o original */}
      <header className="pt-[140px] pb-20 min-h-screen flex items-center bg-[radial-gradient(circle_at_50%_0%,#1e1b4b_0%,#020617_60%)]">
        <div className="container mx-auto px-6 sm:px-8 md:px-12 lg:px-16 xl:px-20">
          <div className="grid gap-12 lg:grid-cols-[1.1fr_0.9fr] lg:gap-20 lg:items-center">
            <div>
              <span className="inline-block bg-[rgba(59,130,246,0.1)] text-[#60A5FA] px-3 py-1.5 rounded-full text-xs font-bold uppercase border border-[rgba(59,130,246,0.3)] mb-5">
                Hackathon Devs de Impacto
              </span>
              <div className="mb-5">
                <div className="flex items-start gap-6 sm:gap-8 md:gap-10 lg:gap-12">
                  <div className="flex-1">
                    <h1 className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-black mb-5 leading-[1.1] tracking-[-1px]">
                      O Portal da Transparência diz o valor.{' '}
                      <span className="bg-gradient-to-r from-[#3b82f6] to-[#8b5cf6] bg-clip-text text-transparent">
                        Nós mostramos a obra.
                      </span>
                    </h1>
                    <p className="text-base sm:text-lg md:text-xl text-[#94a3b8] leading-relaxed">
                      Integramos dados financeiros, políticos e físicos em um único "Trust Score" auditado por Inteligência Artificial.
                    </p>
                  </div>
                  <div className="flex-shrink-0 ml-auto">
                    <div className="relative w-32 h-32 sm:w-40 sm:h-40 md:w-56 md:h-56 lg:w-64 lg:h-64 xl:w-72 xl:h-72 rounded-2xl overflow-hidden shadow-2xl border-2 border-white/20">
                      <Image
                        src="/logo_clean.png"
                        alt="VigiaPix Logo"
                        fill
                        className="object-contain rounded-2xl"
                        priority
                      />
                    </div>
                  </div>
                </div>
              </div>
              <div className="flex gap-4 flex-wrap mb-10">
                <Link href="/triangulacao" className="inline-flex items-center gap-2 px-6 py-3 bg-[#3b82f6] hover:bg-[#2563EB] text-white font-semibold rounded-lg shadow-lg hover:shadow-xl transition-all">
                  <i className="fa-solid fa-rocket"></i>
                  Testar Demo Agora
                </Link>
                <Link href="#solucao" className="inline-flex items-center px-6 py-3 border border-white/20 text-white hover:bg-white/10 rounded-lg font-semibold transition-all">
                  Entender a Lógica
                </Link>
              </div>
              <div className="flex flex-wrap gap-6 sm:gap-10 border-t border-white/10 pt-8 mt-10">
                <div className="stat">
                  <strong className="text-2xl sm:text-3xl font-bold text-white block mb-1">100%</strong>
                  <span className="text-xs text-[#64748b] uppercase tracking-wider font-semibold">Auditável</span>
                </div>
                <div className="stat">
                  <strong className="text-2xl sm:text-3xl font-bold text-white block mb-1">3</strong>
                  <span className="text-xs text-[#64748b] uppercase tracking-wider font-semibold">Fontes de Dados</span>
                </div>
                <div className="stat">
                  <strong className="text-2xl sm:text-3xl font-bold text-white block mb-1">IA</strong>
                  <span className="text-xs text-[#64748b] uppercase tracking-wider font-semibold">OpenAI Engine</span>
                </div>
              </div>
            </div>
            <div className="text-center opacity-80 hidden lg:block">
              <i className="fa-solid fa-diagram-project text-[15rem] text-[rgba(59,130,246,0.1)] drop-shadow-[0_0_30px_rgba(59,130,246,0.3)]"></i>
            </div>
          </div>
        </div>
      </header>

      {/* Problema Section */}
      <section id="problema" className="py-16 sm:py-20 md:py-24 bg-[#0B1120]">
        <div className="container mx-auto px-6 sm:px-8 md:px-12 lg:px-16 xl:px-20">
          <h2 className="text-center text-2xl sm:text-3xl md:text-4xl font-extrabold mb-12 sm:mb-16">
            Por que o sistema atual falha?
          </h2>
          <div className="grid gap-6 sm:gap-8 md:grid-cols-2 lg:grid-cols-3">
            <div className="bg-[rgba(255,255,255,0.02)] border border-white/5 p-6 sm:p-8 rounded-2xl transition-all hover:border-[#3b82f6] hover:-translate-y-1">
              <div className="w-14 h-14 sm:w-16 sm:h-16 rounded-xl bg-[rgba(239,68,68,0.1)] text-[#EF4444] flex items-center justify-center text-2xl sm:text-3xl mb-6">
                <i className="fa-solid fa-eye-slash"></i>
              </div>
              <h3 className="text-lg sm:text-xl font-bold mb-4">Dados Isolados</h3>
              <p className="text-sm sm:text-base text-[#94a3b8]">
                O Portal da Transparência mostra o PIX saindo, mas não conecta com a Nota Fiscal do município.
              </p>
            </div>
            
            <div className="bg-[rgba(255,255,255,0.02)] border border-white/5 p-6 sm:p-8 rounded-2xl transition-all hover:border-[#F59E0B] hover:-translate-y-1">
              <div className="w-14 h-14 sm:w-16 sm:h-16 rounded-xl bg-[rgba(245,158,11,0.1)] text-[#F59E0B] flex items-center justify-center text-2xl sm:text-3xl mb-6">
                <i className="fa-solid fa-file-signature"></i>
              </div>
              <h3 className="text-lg sm:text-xl font-bold mb-4">Objetos Genéricos</h3>
              <p className="text-sm sm:text-base text-[#94a3b8]">
                "Custeio de Saúde" pode ser qualquer coisa. Sem detalhamento, não há fiscalização real.
              </p>
            </div>
            
            <div className="bg-[rgba(255,255,255,0.02)] border border-white/5 p-6 sm:p-8 rounded-2xl transition-all hover:border-[#3B82F6] hover:-translate-y-1 md:col-span-2 lg:col-span-1">
              <div className="w-14 h-14 sm:w-16 sm:h-16 rounded-xl bg-[rgba(59,130,246,0.1)] text-[#3B82F6] flex items-center justify-center text-2xl sm:text-3xl mb-6">
                <i className="fa-solid fa-robot"></i>
              </div>
              <h3 className="text-lg sm:text-xl font-bold mb-4">Volume Impossível</h3>
              <p className="text-sm sm:text-base text-[#94a3b8]">
                Humanos não conseguem auditar milhares de notas fiscais manualmente. A IA consegue.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Solução Section */}
      <section id="solucao" className="py-16 sm:py-20 md:py-24 bg-[#020617]">
        <div className="container mx-auto px-6 sm:px-8 md:px-12 lg:px-16 xl:px-20">
          <div className="text-center max-w-2xl mx-auto mb-12 sm:mb-16">
            <h2 className="text-3xl sm:text-4xl md:text-5xl font-extrabold mb-5">A Solução: Triangulação</h2>
            <p className="text-base sm:text-lg text-[#94a3b8]">
              O VigiaPix não substitui o Portal da Transparência. Ele o enriquece conectando duas novas pontas.
            </p>
          </div>
          
          <div className="flex flex-col gap-4 sm:gap-5 max-w-3xl mx-auto">
            <div className="flex gap-4 sm:gap-5 items-center bg-[rgba(255,255,255,0.05)] p-4 sm:p-5 rounded-xl">
              <div className="min-w-[45px] h-[45px] sm:min-w-[50px] sm:h-[50px] bg-[#2563EB] rounded-full flex items-center justify-center font-bold text-lg sm:text-xl flex-shrink-0">
                1
              </div>
              <div>
                <h3 className="text-lg sm:text-xl font-bold mb-1">Fonte Portal (Financeiro)</h3>
                <p className="text-sm text-[#94a3b8]">
                  Puxamos automaticamente: Valor, Data, Deputado e Status do SIAFI.
                </p>
              </div>
            </div>
            
            <div className="flex gap-4 sm:gap-5 items-center bg-[rgba(255,255,255,0.05)] p-4 sm:p-5 rounded-xl">
              <div className="min-w-[45px] h-[45px] sm:min-w-[50px] sm:h-[50px] bg-[#7C3AED] rounded-full flex items-center justify-center font-bold text-lg sm:text-xl flex-shrink-0">
                2
              </div>
              <div>
                <h3 className="text-lg sm:text-xl font-bold mb-1">Fonte Gabinete (Político)</h3>
                <p className="text-sm text-[#94a3b8]">
                  O Deputado insere: Objeto detalhado, Justificativa e Público-alvo.
                </p>
              </div>
            </div>
            
            <div className="flex gap-4 sm:gap-5 items-center bg-[rgba(255,255,255,0.05)] p-4 sm:p-5 rounded-xl">
              <div className="min-w-[45px] h-[45px] sm:min-w-[50px] sm:h-[50px] bg-[#D97706] rounded-full flex items-center justify-center font-bold text-lg sm:text-xl flex-shrink-0">
                3
              </div>
              <div>
                <h3 className="text-lg sm:text-xl font-bold mb-1">Fonte Executor (Físico)</h3>
                <p className="text-sm text-[#94a3b8]">
                  O Município envia: Foto georreferenciada e Nota Fiscal da obra.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Funcionalidades Section */}
      <section className="py-16 sm:py-20 md:py-24 bg-[#0B1120]">
        <div className="container mx-auto px-6 sm:px-8 md:px-12 lg:px-16 xl:px-20">
          <div className="text-center max-w-2xl mx-auto mb-12 sm:mb-16">
            <h2 className="text-3xl sm:text-4xl md:text-5xl font-extrabold mb-4 sm:mb-5">
              ✨ Funcionalidades Implementadas
            </h2>
            <p className="text-base sm:text-lg text-[#94a3b8]">
              Todas as funcionalidades estão 100% operacionais e prontas para uso
            </p>
          </div>
          
          <div className="grid gap-6 sm:gap-8 md:grid-cols-2 lg:grid-cols-3">
            <Link href="/emenda-pix" className="bg-[rgba(255,255,255,0.02)] border border-white/5 p-6 sm:p-8 rounded-2xl transition-all hover:border-[#3b82f6] hover:-translate-y-1 group">
              <div className="text-4xl sm:text-5xl mb-4">📊</div>
              <h3 className="text-lg sm:text-xl font-bold mb-3 group-hover:text-[#60A5FA] transition-colors">Rastreamento Completo</h3>
              <p className="text-sm sm:text-base text-[#94a3b8] mb-4">
                Acompanhamento de execução em tempo real com valores, metas, progresso e riscos.
              </p>
              <span className="text-xs text-[#60A5FA] font-semibold inline-flex items-center gap-1">
                Explorar <i className="fa-solid fa-arrow-right"></i>
              </span>
            </Link>
            
            <Link href="/triangulacao" className="bg-[rgba(255,255,255,0.02)] border border-white/5 p-6 sm:p-8 rounded-2xl transition-all hover:border-[#7C3AED] hover:-translate-y-1 group">
              <div className="text-4xl sm:text-5xl mb-4">🔗</div>
              <h3 className="text-lg sm:text-xl font-bold mb-3 group-hover:text-[#A78BFA] transition-colors">Triangulação de Dados</h3>
              <p className="text-sm sm:text-base text-[#94a3b8] mb-4">
                Integra Portal, Gabinete e Executor em um único Trust Score auditado por IA.
              </p>
              <span className="text-xs text-[#A78BFA] font-semibold inline-flex items-center gap-1">
                Explorar <i className="fa-solid fa-arrow-right"></i>
              </span>
            </Link>
            
            <Link href="/placar-transparencia" className="bg-[rgba(255,255,255,0.02)] border border-white/5 p-6 sm:p-8 rounded-2xl transition-all hover:border-[#10B981] hover:-translate-y-1 group">
              <div className="text-4xl sm:text-5xl mb-4">🏆</div>
              <h3 className="text-lg sm:text-xl font-bold mb-3 group-hover:text-[#34D399] transition-colors">Placar de Transparência</h3>
              <p className="text-sm sm:text-base text-[#94a3b8] mb-4">
                Ranking e métricas de transparência por município e parlamentar.
              </p>
              <span className="text-xs text-[#34D399] font-semibold inline-flex items-center gap-1">
                Explorar <i className="fa-solid fa-arrow-right"></i>
              </span>
            </Link>
            
            <Link href="/dashboard" className="bg-[rgba(255,255,255,0.02)] border border-white/5 p-6 sm:p-8 rounded-2xl transition-all hover:border-[#3b82f6] hover:-translate-y-1 group">
              <div className="text-4xl sm:text-5xl mb-4">📜</div>
              <h3 className="text-lg sm:text-xl font-bold mb-3 group-hover:text-[#60A5FA] transition-colors">Legislações Simplificadas</h3>
              <p className="text-sm sm:text-base text-[#94a3b8] mb-4">
                Simplifique textos legislativos com IA e participe das discussões.
              </p>
              <span className="text-xs text-[#60A5FA] font-semibold inline-flex items-center gap-1">
                Explorar <i className="fa-solid fa-arrow-right"></i>
              </span>
            </Link>
            
            <Link href="/emenda-pix" className="bg-[rgba(255,255,255,0.02)] border border-white/5 p-6 sm:p-8 rounded-2xl transition-all hover:border-[#F59E0B] hover:-translate-y-1 group">
              <div className="text-4xl sm:text-5xl mb-4">🤖</div>
              <h3 className="text-lg sm:text-xl font-bold mb-3 group-hover:text-[#FBBF24] transition-colors">IA Proativa</h3>
              <p className="text-sm sm:text-base text-[#94a3b8] mb-4">
                Análise automática, detecção de riscos e alertas inteligentes com OpenAI.
              </p>
              <span className="text-xs text-[#FBBF24] font-semibold inline-flex items-center gap-1">
                Explorar <i className="fa-solid fa-arrow-right"></i>
              </span>
            </Link>
            
            <Link href="/whatsapp-simulator" className="bg-[rgba(255,255,255,0.02)] border border-white/5 p-6 sm:p-8 rounded-2xl transition-all hover:border-[#10B981] hover:-translate-y-1 group">
              <div className="text-4xl sm:text-5xl mb-4">💬</div>
              <h3 className="text-lg sm:text-xl font-bold mb-3 group-hover:text-[#34D399] transition-colors">Bot WhatsApp</h3>
              <p className="text-sm sm:text-base text-[#94a3b8] mb-4">
                Interaja com legislações via WhatsApp de forma simples e direta.
              </p>
              <span className="text-xs text-[#34D399] font-semibold inline-flex items-center gap-1">
                Explorar <i className="fa-solid fa-arrow-right"></i>
              </span>
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="text-center py-8 sm:py-10 bg-[#020617] border-t border-white/10 text-[#64748b]">
        <div className="container mx-auto px-6 sm:px-8 md:px-12 lg:px-16 xl:px-20">
          <p>&copy; 2025 VigiaPix Team. Hackathon Devs de Impacto.</p>
        </div>
      </footer>
    </main>
  )
}
