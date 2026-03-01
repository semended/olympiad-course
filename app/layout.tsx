import type { Metadata } from "next";
import "@/app/globals.css";

import { SiteFooter } from "@/components/site-footer";
import { SiteHeader } from "@/components/site-header";

export const metadata: Metadata = {
  title: "Pandamath",
  description: "Публичный фронтенд проект для олимпиадных курсов"
};

export default function RootLayout({
  children
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ru">
      <body className="min-h-screen bg-slate-50 text-slate-900 antialiased">
        <SiteHeader />
        <main className="mx-auto w-full max-w-6xl px-4 pt-10 sm:px-6">{children}</main>
        <SiteFooter />
      </body>
    </html>
  );
}
