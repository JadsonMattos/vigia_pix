import { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'VigiaPix - Fiscalização Inteligente de Emendas Pix',
  description: 'Sistema especializado em rastreamento e transparência de Emendas Pix com IA. Acompanhe execução, detecte anomalias e fiscalize recursos públicos.',
  manifest: '/manifest.json',
  themeColor: '#2563eb',
  viewport: {
    width: 'device-width',
    initialScale: 1,
    maximumScale: 5,
    userScalable: true,
  },
  appleWebApp: {
    capable: true,
    statusBarStyle: 'default',
    title: 'VigiaPix',
  },
  icons: {
    icon: [
      { url: '/icon-192x192.png', sizes: '192x192', type: 'image/png' },
      { url: '/icon-512x512.png', sizes: '512x512', type: 'image/png' },
    ],
    apple: [
      { url: '/icon-192x192.png', sizes: '192x192', type: 'image/png' },
    ],
  },
}



