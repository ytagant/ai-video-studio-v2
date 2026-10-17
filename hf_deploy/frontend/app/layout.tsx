import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI Video Studio — Autonomous Production Floor",
  description: "Multi-agent AI video production studio",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-studio-bg">{children}</body>
    </html>
  );
}
