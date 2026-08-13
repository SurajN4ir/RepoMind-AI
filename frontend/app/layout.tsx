import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";

import "@/app/globals.css";
import { AuthProvider, ThemeProvider, QueryProvider, ToastProvider } from "@/providers";

const fontUI = Geist({
  subsets: ["latin"],
  variable: "--font-ui",
  display: "swap",
  preload: true,
});

const fontCode = Geist_Mono({
  subsets: ["latin"],
  variable: "--font-code",
  display: "swap",
  preload: false,
});

export const metadata: Metadata = {
  title: {
    default: "RepoMind — Repository Intelligence Platform",
    template: "%s · RepoMind",
  },
  description:
    "RepoMind parses your source code at the AST level, builds a semantic index, and answers your questions with direct citations — no hallucinations, no guessing.",
  keywords: [
    "repository intelligence",
    "code search",
    "AI codebase",
    "semantic search",
    "code Q&A",
    "developer tools",
  ],
  authors: [{ name: "RepoMind Team" }],
  openGraph: {
    title: "RepoMind — Repository Intelligence Platform",
    description:
      "Understand any repository in minutes with AI-powered semantic search and grounded Q&A.",
    type: "website",
    locale: "en_US",
  },
  twitter: {
    card: "summary_large_image",
    title: "RepoMind — Repository Intelligence Platform",
    description: "AI-powered repository understanding. No hallucinations.",
  },
  robots: {
    index: true,
    follow: true,
  },
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html
      lang="en"
      suppressHydrationWarning
      className={`${fontUI.variable} ${fontCode.variable}`}
    >
      <body>
        <a
          href="#main-content"
          className="fixed -top-40 left-4 z-[100] rounded-xl bg-primary px-4 py-2 text-sm font-medium text-slate-950 shadow-glow transition-all focus:top-4 focus-visible:outline-2 focus-visible:outline-ring"
        >
          Skip to content
        </a>
        <ThemeProvider>
          <AuthProvider>
            <QueryProvider>
              <ToastProvider>
                {children}
              </ToastProvider>
            </QueryProvider>
          </AuthProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
