"use client";

import Image from "next/image";
import Link from "next/link";

import { HeartIcon } from "@/components/store/icons";
import { useStore } from "@/components/store/store-provider";
import { getSellerById } from "@/lib/data/selectors";
import { Product } from "@/lib/data/types";

export function ProductCard({ product }: { product: Product }) {
  const { isWishlisted, toggleWishlist } = useStore();
  const seller = getSellerById(product.sellerId);
  const variant = product.variants[0];
  const wishlisted = isWishlisted(product.slug);

  return (
    <div className="group min-w-[220px] max-w-[280px] flex-1">
      <div className="relative">
        <Link href={`/products/${product.slug}`} className="block">
          <div className="relative mb-3 aspect-square overflow-hidden bg-cream">
            {product.badge ? (
              <span className="absolute left-3 top-3 z-10 bg-white/90 px-2 py-1 text-[10px] font-medium uppercase tracking-wider">
                {product.badge}
              </span>
            ) : null}
            <Image
              src={variant.image}
              alt={`${product.name} - ${variant.color}`}
              fill
              className="object-cover transition-transform duration-500 group-hover:scale-105"
              sizes="(max-width: 768px) 50vw, 280px"
            />
            <span className="absolute bottom-3 left-1/2 hidden -translate-x-1/2 bg-white/90 px-4 py-2 text-[10px] font-medium uppercase tracking-wider md:block">
              QUICK VIEW
            </span>
          </div>
        </Link>
        <div className="absolute right-3 top-3 z-10">
          <button
            aria-label="Toggle wishlist"
            className="rounded-full bg-white/90 p-1.5 transition hover:bg-white"
            onClick={() => toggleWishlist(product.slug)}
          >
            <HeartIcon filled={wishlisted} />
          </button>
        </div>
      </div>

      <Link href={`/products/${product.slug}`} className="block">
        <h3 className="mb-0.5 text-[12px] font-medium uppercase tracking-[0.5px]">{product.name}</h3>
        <p className="mb-0.5 text-[12px] text-warm-gray">{variant.color}</p>
        <p className="mb-1 text-[11px] text-warm-gray/70">
          Sold by <span className="text-charcoal/60">{seller?.name ?? "Seller"}</span>
          {seller?.isPro ? (
            <span className="ml-1 inline-block rounded bg-charcoal/10 px-1 py-0.5 text-[9px] uppercase tracking-wide text-charcoal/70">
              Pro
            </span>
          ) : null}
        </p>
      </Link>

      <div className="mb-1.5 flex gap-1.5">
        {product.variants.map((entry) => (
          <span
            key={entry.color}
            className="h-3 w-3 rounded-full border border-black/10"
            style={{ backgroundColor: entry.hex }}
            aria-label={entry.color}
          />
        ))}
      </div>
      <div className="flex items-center gap-2">
        <span className="text-[14px] font-medium">{product.price} zl</span>
      </div>
    </div>
  );
}
