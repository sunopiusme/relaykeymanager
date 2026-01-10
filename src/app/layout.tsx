import type { Metadata, Viewport } from "next";
import { Inter } from "next/font/google";
import { TelegramScript } from "@/components/TelegramScript";
import { TelegramProvider } from "@/components/TelegramProvider";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: "Relay Payment Mini App",
  description: "Telegram Mini App for payments",
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
  userScalable: false,
  viewportFit: "cover",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    // suppressHydrationWarning because Telegram SDK injects style attributes on <html>
    <html lang="en" className={inter.variable} suppressHydrationWarning>
      <head>
        {/* Preload critical images for instant loading */}
        <link rel="preload" href="/relaydefaultappcicon.png" as="image" />
        <link rel="preload" href="/telegram-stars.svg" as="image" type="image/svg+xml" />
        <TelegramScript />
      </head>
      <body
        style={{ background: '#f2f2f7', margin: 0, padding: 0 }}
        suppressHydrationWarning
      >
        <TelegramProvider>{children}</TelegramProvider>
      </body>
    </html>
  );
}
