'use client'

import { useState } from 'react'
import { TriangulationCitizenView } from '@/features/triangulation/components/CitizenView'
import { TriangulationParliamentaryView } from '@/features/triangulation/components/ParliamentaryView'
import { TriangulationExecutorView } from '@/features/triangulation/components/ExecutorView'
import { TransparencyNote } from '@/shared/components/TransparencyNote'

type ViewType = 'citizen' | 'parliamentary' | 'executor'

export default function TriangulationPage() {
  const [currentView, setCurrentView] = useState<ViewType>('citizen')

  return (
    <div className="min-h-screen bg-[#F3F4F6]">
      <div className="flex flex-col lg:flex-row h-screen">
        {/* Sidebar */}
        <aside className="bg-white border-b lg:border-b-0 lg:border-r border-gray-200 lg:w-64 lg:h-screen fixed lg:static bottom-0 left-0 right-0 z-50 lg:z-auto">
          <div className="lg:px-6 lg:py-6 px-4 py-3 border-b border-gray-200 hidden lg:block">
            <div className="flex items-center gap-2 text-xl font-bold text-gray-900">
              <span>🔗</span>
              <span>VigiaPix</span>
            </div>
          </div>
          
          <nav className="flex lg:flex-col justify-around lg:justify-start lg:gap-2 lg:px-4 lg:py-4">
            <button
              onClick={() => setCurrentView('citizen')}
              className={`flex flex-col lg:flex-row items-center gap-2 px-4 py-3 lg:px-4 lg:py-3 rounded-lg transition-all ${
                currentView === 'citizen'
                  ? 'bg-blue-50 text-blue-600'
                  : 'text-gray-600 hover:bg-gray-50'
              }`}
            >
              <i className="fa-solid fa-chart-pie text-xl lg:text-base"></i>
              <span className="text-xs lg:text-sm font-semibold">Painel Integrado</span>
            </button>
            
            <button
              onClick={() => setCurrentView('parliamentary')}
              className={`flex flex-col lg:flex-row items-center gap-2 px-4 py-3 lg:px-4 lg:py-3 rounded-lg transition-all ${
                currentView === 'parliamentary'
                  ? 'bg-purple-50 text-purple-600'
                  : 'text-gray-600 hover:bg-gray-50'
              }`}
            >
              <i className="fa-solid fa-landmark text-xl lg:text-base"></i>
              <span className="text-xs lg:text-sm font-semibold">Área Gabinete</span>
            </button>
            
            <button
              onClick={() => setCurrentView('executor')}
              className={`flex flex-col lg:flex-row items-center gap-2 px-4 py-3 lg:px-4 lg:py-3 rounded-lg transition-all ${
                currentView === 'executor'
                  ? 'bg-orange-50 text-orange-600'
                  : 'text-gray-600 hover:bg-gray-50'
              }`}
            >
              <i className="fa-solid fa-helmet-safety text-xl lg:text-base"></i>
              <span className="text-xs lg:text-sm font-semibold">Área Executor</span>
            </button>
          </nav>
        </aside>

        {/* Main Content */}
        <main className="flex-1 overflow-y-auto pb-20 lg:pb-0 pt-4 sm:pt-6 lg:pt-8 px-4 sm:px-5 md:px-6 lg:px-8 xl:px-10">
          <div className="max-w-6xl mx-auto">
            {currentView === 'citizen' && <TriangulationCitizenView />}
            {currentView === 'parliamentary' && <TriangulationParliamentaryView />}
            {currentView === 'executor' && <TriangulationExecutorView />}
            
            {/* Nota de Transparência */}
            <TransparencyNote />
          </div>
        </main>
      </div>
    </div>
  )
}


