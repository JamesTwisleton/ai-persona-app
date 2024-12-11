import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';

// Initialize the Inter font with Latin subset for optimized loading
const inter = Inter({ subsets: ['latin'] });

// Define metadata for the application
export const metadata: Metadata = {
  title: 'PersonaComposer',
  description: 'Create and manage social media personalities',
};

/**
 * RootLayout component
 * This component wraps all pages in the application, providing a consistent layout
 *
 * @param {Object} props - Component props
 * @param {React.ReactNode} props.children - Child components to be rendered within the layout
 */
export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      {/* Apply the Inter font class to the body for consistent typography */}
      <body className={inter.className}>
        {/* Render the child components (page content) */}
        {children}
      </body>
    </html>
  );
}
