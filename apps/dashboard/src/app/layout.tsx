import './globals.css';
import type { ReactNode } from 'react';
import { Sidebar } from '@/components/sidebar';

export const metadata = {
  title: 'AgentBoard OS',
  description: 'Private command center for the boardroom of agents.',
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen">
        <div className="flex min-h-screen">
          <Sidebar />
          <main className="flex-1 p-8 max-w-6xl">{children}</main>
        </div>
      </body>
    </html>
  );
}
