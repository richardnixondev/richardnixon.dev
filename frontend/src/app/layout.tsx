import type { Metadata } from "next";
import { Inter } from "next/font/google";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import Script from "next/script";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: {
    default: "richardnixon.dev",
    template: "%s | richardnixon.dev",
  },
  description: "Personal platform - Blog, Portfolio, and Dashboards",
  openGraph: {
    type: "website",
    siteName: "richardnixon.dev",
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  const umamiId = process.env.NEXT_PUBLIC_UMAMI_WEBSITE_ID;

  return (
    <html lang="en" className="scroll-smooth">
      <body className={`${inter.className} bg-gray-900 text-gray-100 min-h-screen flex flex-col`}>
        <Navbar />
        <main className="flex-grow">{children}</main>
        <Footer />
        {umamiId && (
          <Script
            defer
            src="https://analytics.richardnixon.dev/script.js"
            data-website-id={umamiId}
          />
        )}
      </body>
    </html>
  );
}
