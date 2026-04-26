import type { Metadata } from "next";

import { CartDrawer } from "@/components/store/cart-drawer";
import { Footer } from "@/components/store/footer";
import { Header } from "@/components/store/header";
import { StoreProvider } from "@/components/store/store-provider";

import "./globals.css";

export const metadata: Metadata = {
  title: "FashionHero - Marketplace Storefront",
  description: "FashionHero storefront preview for development, demos and Vercel sharing.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <StoreProvider>
          <div className="flex min-h-screen flex-col">
            <Header />
            {children}
            <Footer />
            <CartDrawer />
          </div>
        </StoreProvider>
      </body>
    </html>
  );
}
