"use client";

import { ProductCard } from "@/components/store/product-card";
import { useStore } from "@/components/store/store-provider";
import { products } from "@/lib/data/mock-data";

export function WishlistPage() {
  const { wishlist } = useStore();
  const items = products.filter((product) => wishlist.some((entry) => entry.productSlug === product.slug));

  return (
    <main className="px-4 py-10 md:px-8 lg:px-12">
      <div className="mb-10">
        <p className="mb-2 text-sm text-warm-gray">Saved for later</p>
        <h1 className="text-4xl font-light text-charcoal">Wishlist</h1>
      </div>

      {items.length === 0 ? (
        <div className="rounded-[32px] bg-cream-light px-8 py-16 text-center">
          <p className="mb-4 text-sm text-warm-gray">Your wishlist is empty.</p>
          <p className="text-sm text-warm-gray">Browse collections and save the items you want to review with the team later.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 xl:grid-cols-4">
          {items.map((product) => (
            <ProductCard key={product.slug} product={product} />
          ))}
        </div>
      )}
    </main>
  );
}
