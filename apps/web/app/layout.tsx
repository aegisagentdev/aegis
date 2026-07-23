import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Aegis — the security shield for agentic trading on Robinhood Chain",
  description:
    "Aegis is a two-way shield for MCP agents: a prompt-injection firewall on the way in, a deterministic pre-trade safety scanner on the way out. GO / CAUTION / NO in milliseconds, with on-chain receipts.",
  metadataBase: new URL("https://aegismcp.io"),
  openGraph: {
    title: "Aegis — security shield for agentic trading",
    description:
      "Prompt-injection firewall + pre-trade safety scanner for MCP agents on Robinhood Chain.",
    type: "website",
  },
  twitter: { card: "summary_large_image", title: "Aegis", description: "Two-way shield for agentic trading on Robinhood Chain." },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="" />
        <link
          href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700;800&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>{children}</body>
    </html>
  );
}
