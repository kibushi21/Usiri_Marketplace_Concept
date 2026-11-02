import type { Metadata } from "next";

import { AuthProvider } from "@/lib/auth";

import "./globals.css";

export const metadata: Metadata = {
  title: {
    default: "Usiri — a managed marketplace for Tanzanian homes",
    template: "%s · Usiri",
  },
  description:
    "Shop six home departments from verified Tanzanian suppliers. One checkout, per-supplier delivery and payments through an authorised provider.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}
