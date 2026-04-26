"use client";

import Link from "next/link";
import { useState } from "react";

import { useStore } from "@/components/store/store-provider";
import { AccountIcon, BagIcon, HeartIcon, MenuIcon, SearchIcon } from "@/components/store/icons";

const navLinks = [
  { href: "/collections/mens", label: "MEN" },
  { href: "/collections/womens", label: "WOMEN" },
  { href: "/collections/sale", label: "SALE" },
  { href: "/collections/new-arrivals", label: "NEW" },
];

export function Header() {
  const [mobileOpen, setMobileOpen] = useState(false);
  const { cart, wishlist, openCart } = useStore();

  return (
    <>
      <div className="bg-charcoal text-center text-white">
        <p className="mx-auto h-9 max-w-layout px-4 text-[11px] font-medium leading-9 tracking-wide">
          Free Shipping on Orders over 299 zl - Easy Returns.
        </p>
      </div>
      <header className="sticky top-0 z-40 border-b border-black/5 bg-white/95 backdrop-blur">
        <nav className="mx-auto flex h-14 max-w-layout items-center px-4 lg:px-8">
          <button
            className="mr-3 p-1 lg:hidden"
            aria-label="Open menu"
            onClick={() => setMobileOpen((current) => !current)}
          >
            <MenuIcon />
          </button>
          <Link href="/" className="mr-8 text-xl font-semibold italic tracking-tight text-charcoal">
            FashionHero
          </Link>
          <div className="hidden flex-1 items-center gap-6 lg:flex">
            {navLinks.map((link) => (
              <Link key={link.href} href={link.href} className="text-nav text-charcoal transition-opacity hover:opacity-60">
                {link.label}
              </Link>
            ))}
          </div>
          <div className="ml-auto flex items-center gap-3">
            <Link href="/about" className="hidden text-[12px] text-charcoal transition-opacity hover:opacity-60 lg:block">
              About
            </Link>
            <button aria-label="Search" className="p-1 transition-opacity hover:opacity-60">
              <SearchIcon />
            </button>
            <Link aria-label="Wishlist" href="/wishlist" className="relative hidden p-1 transition-opacity hover:opacity-60 sm:block">
              <HeartIcon />
              {wishlist.length > 0 ? (
                <span className="absolute -right-1 -top-1 flex h-4 w-4 items-center justify-center rounded-full bg-charcoal text-[9px] text-white">
                  {wishlist.length}
                </span>
              ) : null}
            </Link>
            <Link
              aria-label="Account"
              href="/account/login"
              className="hidden items-center justify-center p-1 transition-opacity hover:opacity-60 sm:flex"
            >
              <AccountIcon />
            </Link>
            <button aria-label="View cart" className="relative p-1 transition-opacity hover:opacity-60" onClick={openCart}>
              <BagIcon />
              {cart.length > 0 ? (
                <span className="absolute -right-1 -top-1 flex h-4 w-4 items-center justify-center rounded-full bg-charcoal text-[9px] text-white">
                  {cart.reduce((sum, item) => sum + item.quantity, 0)}
                </span>
              ) : null}
            </button>
          </div>
        </nav>
        <div className={`overflow-hidden border-t border-black/5 transition-all duration-300 lg:hidden ${mobileOpen ? "max-h-80" : "max-h-0"}`}>
          <div className="space-y-1 px-4 py-4">
            {navLinks.map((link) => (
              <Link key={link.href} href={link.href} className="block py-2 text-nav" onClick={() => setMobileOpen(false)}>
                {link.label}
              </Link>
            ))}
            <Link href="/about" className="block py-2 text-sm" onClick={() => setMobileOpen(false)}>
              About
            </Link>
          </div>
        </div>
      </header>
    </>
  );
}
