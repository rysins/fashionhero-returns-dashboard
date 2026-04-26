"use client";

import { useState } from "react";

import { ProductCard } from "@/components/store/product-card";
import { Product } from "@/lib/data/types";

type Tab = "new" | "best";

export function FavoritesSection({
  newArrivals,
  bestSellers,
}: {
  newArrivals: Product[];
  bestSellers: Product[];
}) {
  const [tab, setTab] = useState<Tab>("new");
  const products = tab === "new" ? newArrivals : bestSellers;

  return (
    <section className="py-12">
      <h2 className="mb-2 text-center text-[40px] font-normal text-charcoal">Our Favorites</h2>
      <div className="mb-8 flex justify-center gap-6">
        <button
          className={`border-b-2 pb-1 text-[12px] font-medium uppercase tracking-[0.5px] transition-colors ${
            tab === "new" ? "border-charcoal text-charcoal" : "border-transparent text-warm-gray hover:text-charcoal"
          }`}
          onClick={() => setTab("new")}
        >
          NEW ARRIVALS
        </button>
        <button
          className={`border-b-2 pb-1 text-[12px] font-medium uppercase tracking-[0.5px] transition-colors ${
            tab === "best" ? "border-charcoal text-charcoal" : "border-transparent text-warm-gray hover:text-charcoal"
          }`}
          onClick={() => setTab("best")}
        >
          BEST SELLERS
        </button>
      </div>
      <div className="relative px-4 md:px-8 lg:px-12">
        <div className="scrollbar-hide flex gap-4 overflow-x-auto pb-2">
          {products.map((product) => (
            <ProductCard key={product.slug} product={product} />
          ))}
        </div>
      </div>
    </section>
  );
}
