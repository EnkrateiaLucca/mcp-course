import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Data Analysis Chat Agent",
  description: "Claude Agent SDK + MCP + Vercel Sandbox demo",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-bg text-gray-200 antialiased">{children}</body>
    </html>
  );
}
