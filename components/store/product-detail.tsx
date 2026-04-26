"use client";

import Image from "next/image";
import Link from "next/link";
import { useState } from "react";

import { ProductCard } from "@/components/store/product-card";
import { useStore } from "@/components/store/store-provider";
import { getSellerById } from "@/lib/data/selectors";
import { Product } from "@/lib/data/types";

export function ProductDetail({
  product,
  recommendations,
}: {
  product: Product;
  recommendations: Product[];
}) {
  const seller = getSellerById(product.sellerId);
  const [selectedVariantIndex, setSelectedVariantIndex] = useState(0);
  const [selectedSize, setSelectedSize] = useState(product.variants[0]?.sizes[0] ?? "");
  const { addToCart, isWishlisted, toggleWishlist } = useStore();

  const selectedVariant = product.variants[selectedVariantIndex];

  return (
    <main className="px-4 py-8 md:px-8 lg:px-12">
      <div className="mb-8 text-sm text-warm-gray">Home / {product.category} / {product.name}</div>

      <section className="grid gap-10 lg:grid-cols-[minmax(0,1fr)_440px]">
        <div className="space-y-4">
          <div className="relative aspect-square overflow-hidden rounded-[32px] bg-cream">
            <Image src={selectedVariant.image} alt={`${product.name} - ${selectedVariant.color}`} fill className="object-cover" sizes="(max-width: 1024px) 100vw, 50vw" />
          </div>
          <div className="grid grid-cols-3 gap-3">
            {product.variants.map((variant, index) => (
              <button
                key={variant.color}
                className={`relative aspect-square overflow-hidden rounded-3xl border ${
                  index === selectedVariantIndex ? "border-charcoal" : "border-black/10"
                }`}
                onClick={() => {
                  setSelectedVariantIndex(index);
                  setSelectedSize(variant.sizes[0] ?? "");
                }}
              >
                <Image src={variant.image} alt={variant.color} fill className="object-cover" sizes="160px" />
              </button>
            ))}
          </div>
        </div>

        <div>
          <div className="mb-6">
            <div className="mb-2 flex items-start justify-between gap-4">
              <div>
                <h1 className="mb-2 text-2xl font-normal text-charcoal md:text-3xl">{product.name}</h1>
                <p className="text-sm text-warm-gray">
                  ({product.rating.count}) reviews
                </p>
              </div>
              <button
                aria-label="Toggle wishlist"
                className={`rounded-full border p-3 transition ${isWishlisted(product.slug) ? "border-charcoal bg-charcoal text-white" : "border-black/10"}`}
                onClick={() => toggleWishlist(product.slug)}
              >
                Save
              </button>
            </div>
            <p className="mb-1 text-sm text-warm-gray">
              Sold by <span className="text-charcoal">{seller?.name ?? "Seller"}</span>
              {seller?.isPro ? <span className="ml-1 rounded bg-charcoal/10 px-1 py-0.5 text-[9px] uppercase tracking-wide text-charcoal/70">Pro</span> : null}
            </p>
            <p className="text-2xl font-medium">{product.price} zl</p>
          </div>

          <div className="mb-6 rounded-[28px] border border-black/5 bg-cream-light p-5">
            <p className="mb-3 text-sm text-charcoal">{product.stockStatus}</p>
            <p className="text-sm text-warm-gray">Free Shipping on Orders over 299 zl</p>
            <p className="mt-1 text-sm text-warm-gray">Estimated delivery: Apr 28 - Apr 30</p>
            <p className="mt-1 text-sm text-warm-gray">Easy Returns</p>
          </div>

          <div className="mb-6">
            <p className="mb-3 text-xs font-medium uppercase tracking-[0.6px]">Color</p>
            <div className="flex gap-2">
              {product.variants.map((variant, index) => (
                <button
                  key={variant.color}
                  className={`flex items-center gap-2 rounded-full border px-3 py-2 text-sm ${
                    index === selectedVariantIndex ? "border-charcoal bg-charcoal text-white" : "border-black/10"
                  }`}
                  onClick={() => {
                    setSelectedVariantIndex(index);
                    setSelectedSize(variant.sizes[0] ?? "");
                  }}
                >
                  <span className="h-3 w-3 rounded-full border border-black/10" style={{ backgroundColor: variant.hex }} />
                  {variant.color}
                </button>
              ))}
            </div>
          </div>

          <div className="mb-8">
            <p className="mb-3 text-xs font-medium uppercase tracking-[0.6px]">Size</p>
            <div className="flex flex-wrap gap-2">
              {selectedVariant.sizes.map((size) => (
                <button
                  key={size}
                  className={`rounded-full border px-4 py-2 text-sm ${
                    selectedSize === size ? "border-charcoal bg-charcoal text-white" : "border-black/10"
                  }`}
                  onClick={() => setSelectedSize(size)}
                >
                  {size}
                </button>
              ))}
            </div>
          </div>

          <div className="mb-10 flex flex-wrap gap-3">
            <button
              className="btn-cta"
              onClick={() =>
                addToCart({
                  productSlug: product.slug,
                  color: selectedVariant.color,
                  size: selectedSize,
                  quantity: 1,
                })
              }
            >
              ADD TO CART
            </button>
            <Link href="/wishlist" className="btn-cta-outline">
              VIEW WISHLIST
            </Link>
          </div>

          <div className="space-y-6 text-sm leading-relaxed text-warm-gray">
            <section>
              <h2 className="mb-2 text-lg font-medium text-charcoal">Description</h2>
              <p>{product.description}</p>
            </section>
            <section>
              <h2 className="mb-2 text-lg font-medium text-charcoal">Features</h2>
              <ul className="list-disc space-y-1 pl-5">
                {product.features.map((feature) => (
                  <li key={feature}>{feature}</li>
                ))}
              </ul>
            </section>
            <section>
              <h2 className="mb-2 text-lg font-medium text-charcoal">Materials</h2>
              <p>{product.materials}</p>
            </section>
            <section>
              <h2 className="mb-2 text-lg font-medium text-charcoal">Care</h2>
              <p>{product.care}</p>
            </section>
          </div>
        </div>
      </section>

      <section className="py-16">
        <h2 className="mb-8 text-lg font-medium text-charcoal">You May Also Like</h2>
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 xl:grid-cols-4">
          {recommendations.map((item) => (
            <ProductCard key={item.slug} product={item} />
          ))}
        </div>
      </section>
    </main>
  );
}
