import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { Toaster } from 'react-hot-toast'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  metadataBase: new URL('https://cardiorisk.roilabs.com.br'),
  title: 'CardioCare AI — Análise de Risco Cardiovascular',
  description: 'Análise de Risco Cardiovascular com Inteligência Artificial',
  alternates: { canonical: '/' },
  openGraph: {
    type: 'website',
    locale: 'pt_BR',
    url: 'https://cardiorisk.roilabs.com.br',
    title: 'CardioCare AI — Análise de Risco Cardiovascular',
    description: 'Análise de Risco Cardiovascular com Inteligência Artificial',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="pt-BR">
      <body className={inter.className}>
        {children}
        <Toaster position="top-right" />
      </body>
    </html>
  )
}