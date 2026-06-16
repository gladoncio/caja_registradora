import { Inter } from 'next/font/google'
import ClientLayout from './ClientLayout'

const inter = Inter({
  subsets: ['latin'],
  weight: ['300', '400', '500', '600', '700', '800'],
  display: 'swap',
})

export const metadata = {
  title: 'Caja Registradora',
  description: 'Sistema POS Caja Registradora',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es" className={inter.className}>
      <body>
        <ClientLayout>{children}</ClientLayout>
      </body>
    </html>
  )
}
