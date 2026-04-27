"use client";

import { useState } from "react";

import { ProductCard } from "@/components/store/product-card";
import { useStore } from "@/components/store/store-provider";
import { rankProductsForScenario } from "@/lib/data/selectors";
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
  const { scenario } = useStore();
  const products = rankProductsForScenario(tab === "new" ? newArrivals : bestSellers, scenario);

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
        {scenario.promoteLowReturnProductsEnabled ? (
          <p className="mb-4 text-center text-xs uppercase tracking-[0.5px] text-[#2f7d4a]">
            Preview: products with low return risk are pushed higher in this rail.
          </p>
        ) : null}
        <div className="scrollbar-hide flex gap-4 overflow-x-auto pb-2">
          {products.map((product) => (
            <ProductCard key={product.slug} product={product} />
          ))}
        </div>
      </div>
    </section>
  );
}
