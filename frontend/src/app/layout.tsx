import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "HARVEY OS | Command Center",
  description: "Hybrid Strategic AI Command Center",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.className} antialiased selection:bg-cyan-900 selection:text-cyan-100`}>
        <div className="scanlines"></div>
        {children}
      </body>
    </html>
  );
}
