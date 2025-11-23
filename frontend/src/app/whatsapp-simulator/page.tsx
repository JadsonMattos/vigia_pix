'use client'

import { useState } from 'react'
import { Button } from '@/shared/components/ui/button'

export default function WhatsAppSimulatorPage() {
  const [message, setMessage] = useState('')
  const [response, setResponse] = useState('')
  const [loading, setLoading] = useState(false)
  const [history, setHistory] = useState<Array<{message: string, response: string}>>([])

  const sendMessage = async () => {
    if (!message.trim()) return

    setLoading(true)
    try {
      const res = await fetch('http://localhost:8000/api/v1/whatsapp/simulate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          From: 'whatsapp:+5511999999999',
          Body: message
        })
      })

      const data = await res.json()
      
      if (data.status === 'success') {
        setResponse(data.response)
        setHistory(prev => [...prev, { message, response: data.response }])
        setMessage('')
      } else {
        setResponse('❌ Erro ao processar mensagem')
      }
    } catch (error) {
      setResponse('❌ Erro de conexão. Verifique se o backend está rodando.')
    } finally {
      setLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  return (
    <div className="min-h-screen bg-[#F3F4F6]">
      <div className="container mx-auto px-4 sm:px-5 md:px-6 lg:px-8 py-6 sm:py-8 md:py-10 lg:py-12 max-w-6xl">
        {/* Header Melhorado */}
        <div className="mb-6 sm:mb-8 md:mb-12 text-center">
          <h1 className="text-2xl sm:text-3xl md:text-4xl font-extrabold text-[#1F2937] mb-2">
            💬 Simulador WhatsApp - VigiaPix
          </h1>
          <p className="text-sm sm:text-base md:text-lg text-[#6B7280] max-w-2xl mx-auto">
            Teste o bot do WhatsApp sem precisar configurar Twilio. Interaja com legislações de forma simples e direta.
          </p>
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          {/* Chat Interface Melhorado */}
          <div className="bg-white rounded-2xl shadow-xl border-2 border-gray-200 h-[600px] flex flex-col overflow-hidden">
            <div className="bg-gradient-to-r from-green-500 to-green-600 p-6 border-b border-gray-200">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 bg-white rounded-full flex items-center justify-center text-2xl">
                  💬
                </div>
                <div>
                  <h2 className="text-xl font-bold text-white">Conversa</h2>
                  <p className="text-sm text-green-100">VigiaPix Bot</p>
                </div>
              </div>
            </div>
            
            <div className="p-6 flex-1 overflow-y-auto space-y-4 bg-gray-50">
              {history.length === 0 && (
                <div className="text-center text-gray-500 py-12">
                  <div className="text-6xl mb-4">💬</div>
                  <p className="text-lg font-medium mb-2">Envie uma mensagem para começar</p>
                  <p className="text-sm">Exemplo: "PL 1234" ou "ajuda"</p>
                </div>
              )}
              
              {history.map((item, idx) => (
                <div key={idx} className="space-y-3">
                  <div className="flex justify-end">
                    <div className="bg-gradient-to-r from-green-500 to-green-600 text-white rounded-2xl rounded-tr-none px-4 py-3 max-w-[80%] shadow-md">
                      <p className="text-sm whitespace-pre-wrap">{item.message}</p>
                    </div>
                  </div>
                  <div className="flex justify-start">
                    <div className="bg-white text-gray-900 rounded-2xl rounded-tl-none px-4 py-3 max-w-[80%] shadow-md border border-gray-200">
                      <p className="text-sm whitespace-pre-wrap">{item.response}</p>
                    </div>
                  </div>
                </div>
              ))}
              
              {loading && (
                <div className="flex justify-start">
                  <div className="bg-white text-gray-900 rounded-2xl rounded-tl-none px-4 py-3 shadow-md border border-gray-200">
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                      <span className="text-sm ml-2">Processando...</span>
                    </div>
                  </div>
                </div>
              )}
            </div>
            
            <div className="p-6 border-t border-gray-200 bg-white">
              <div className="flex gap-3">
                <input
                  type="text"
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Digite uma mensagem (ex: PL 1234)"
                  className="flex-1 px-4 py-3 border-2 border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  disabled={loading}
                />
                <Button 
                  onClick={sendMessage}
                  disabled={loading || !message.trim()}
                  className="px-6 py-3 bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 text-white font-semibold rounded-xl shadow-md hover:shadow-lg transition-all"
                >
                  Enviar
                </Button>
              </div>
            </div>
          </div>

          {/* Instructions Melhorado */}
          <div className="bg-white rounded-2xl shadow-xl border-2 border-gray-200">
            <div className="bg-gradient-to-r from-blue-500 to-blue-600 p-6 border-b border-gray-200">
              <h2 className="text-xl font-bold text-white">📖 Como usar</h2>
            </div>
            <div className="p-6 space-y-6">
              <div>
                <h3 className="font-bold text-lg text-gray-900 mb-3 flex items-center gap-2">
                  <span>⚡</span>
                  Comandos disponíveis:
                </h3>
                <ul className="space-y-2">
                  <li className="flex items-start gap-2">
                    <span className="text-green-500 mt-1">✓</span>
                    <div>
                      <code className="bg-gray-100 px-2 py-1 rounded text-sm font-mono">ajuda</code>
                      <span className="text-sm text-gray-600 ml-2">- Ver ajuda</span>
                    </div>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-green-500 mt-1">✓</span>
                    <div>
                      <code className="bg-gray-100 px-2 py-1 rounded text-sm font-mono">PL 1234</code>
                      <span className="text-sm text-gray-600 ml-2">- Buscar PL específico</span>
                    </div>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-green-500 mt-1">✓</span>
                    <div>
                      <code className="bg-gray-100 px-2 py-1 rounded text-sm font-mono">1234/2024</code>
                      <span className="text-sm text-gray-600 ml-2">- Formato alternativo</span>
                    </div>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-green-500 mt-1">✓</span>
                    <div>
                      <code className="bg-gray-100 px-2 py-1 rounded text-sm font-mono">1234</code>
                      <span className="text-sm text-gray-600 ml-2">- Apenas número</span>
                    </div>
                  </li>
                </ul>
              </div>

              <div>
                <h3 className="font-bold text-lg text-gray-900 mb-3 flex items-center gap-2">
                  <span>🎯</span>
                  Exemplos:
                </h3>
                <div className="space-y-2">
                  <Button
                    variant="outline"
                    size="sm"
                    className="w-full text-left border-2 hover:bg-gray-50"
                    onClick={() => setMessage('ajuda')}
                  >
                    💬 "ajuda"
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    className="w-full text-left border-2 hover:bg-gray-50"
                    onClick={() => setMessage('PL 1234')}
                  >
                    📜 "PL 1234"
                  </Button>
                </div>
              </div>

              <div className="bg-blue-50 border-2 border-blue-200 rounded-xl p-4">
                <p className="text-sm text-blue-900">
                  <strong className="flex items-center gap-2 mb-2">
                    <span>💡</span>
                    Dica:
                  </strong>
                  Antes de testar, certifique-se de que há legislações sincronizadas no banco. 
                  Use o endpoint <code className="bg-blue-100 px-2 py-1 rounded font-mono text-xs">/api/v1/legislation/sync</code> para sincronizar.
                </p>
              </div>

              <div className="bg-green-50 border-2 border-green-200 rounded-xl p-4">
                <h3 className="font-bold text-gray-900 mb-2 flex items-center gap-2">
                  <span>✅</span>
                  Status da API:
                </h3>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                  <span className="text-sm text-gray-700 font-medium">Backend conectado</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
