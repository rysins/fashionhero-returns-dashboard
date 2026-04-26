import Link from "next/link";

import { footerGroups } from "@/lib/data/mock-data";

export function Footer() {
  return (
    <footer className="mt-auto bg-footer-bg text-white">
      <div className="mx-auto max-w-layout px-4 py-16 lg:px-8">
        <div className="mb-12 border-b border-white/10 pb-10">
          <h3 className="mb-4 text-[12px] font-medium uppercase tracking-[0.8px] text-white/50">FOLLOW THE FLOCK</h3>
          <div className="flex gap-5 text-sm text-white/70">
            <a href="#" className="transition-colors hover:text-white">Instagram</a>
            <a href="#" className="transition-colors hover:text-white">TikTok</a>
            <a href="#" className="transition-colors hover:text-white">Facebook</a>
            <a href="#" className="transition-colors hover:text-white">X/Twitter</a>
          </div>
        </div>

        <div className="grid grid-cols-1 gap-10 sm:grid-cols-2 lg:grid-cols-4">
          <div>
            <h3 className="mb-4 text-[12px] font-medium uppercase tracking-[0.8px] text-white/50">JOIN THE FLOCK</h3>
            <p className="mb-4 text-sm leading-relaxed text-white/60">
              Get the latest on new products, exclusive deals and marketplace drops.
            </p>
            <form className="flex flex-col gap-3">
              <input
                type="email"
                placeholder="Email Address"
                className="w-full border-b border-white/30 bg-transparent px-0 py-2 text-sm placeholder:text-white/30 focus:border-white focus:outline-none"
              />
              <button type="submit" className="self-start rounded-full bg-white px-6 py-2 text-[11px] font-medium uppercase tracking-wider text-charcoal transition hover:bg-white/90">
                Sign Up
              </button>
            </form>
          </div>

          {footerGroups.map((group) => (
            <div key={group.title}>
              <h3 className="mb-4 text-[12px] font-medium uppercase tracking-[0.8px] text-white/50">{group.title}</h3>
              <ul className="space-y-2.5">
                {group.links.map((link) => (
                  <li key={link}>
                    <Link href={resolveFooterLink(link)} className="text-sm text-white/70 transition-colors hover:text-white">
                      {link}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div className="mt-14 flex flex-col items-start justify-between gap-4 border-t border-white/10 pt-8 sm:flex-row sm:items-center">
          <div className="flex items-center gap-6">
            <span className="text-lg font-semibold italic tracking-tight">FashionHero</span>
            <span className="rounded border border-white/20 px-3 py-1 text-xs text-white/40">PL (zl)</span>
          </div>
          <p className="text-xs text-white/30">© 2026 FashionHero. Preview storefront for collaborative development.</p>
        </div>
      </div>
    </footer>
  );
}

function resolveFooterLink(label: string) {
  switch (label) {
    case "Men's Shoes":
      return "/collections/mens";
    case "Women's Shoes":
      return "/collections/womens";
    case "New Arrivals":
      return "/collections/new-arrivals";
    case "Best Sellers":
      return "/collections/best-sellers";
    case "Sale":
      return "/collections/sale";
    case "Our Story":
      return "/about";
    default:
      return "/";
  }
}
