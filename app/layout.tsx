import type { Metadata } from "next";
import "@/app/globals.css";
import { AuthProvider } from "@/components/auth-provider";


export const metadata: Metadata = {
  title: "Olympiad Course SaaS",
  description: "Production-ready Next.js 14 starter for course platform"
};

export default function RootLayout({
  children
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ru">
      <body className="antialiased">
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}
