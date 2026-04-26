"use client";

import Image from "next/image";
import { useMemo, useState } from "react";

import { ProductCard } from "@/components/store/product-card";
import { ProductFilters, SortOption, filterProducts, getFilterOptions, sortProducts } from "@/lib/data/selectors";
import { Collection, Product } from "@/lib/data/types";

export function CollectionPage({ collection, products }: { collection: Collection; products: Product[] }) {
  const [filters, setFilters] = useState<ProductFilters>({ gender: "All" });
  const [sort, setSort] = useState<SortOption>("featured");

  const filterOptions = useMemo(() => getFilterOptions(products), [products]);
  const filteredProducts = useMemo(() => sortProducts(filterProducts(products, filters), sort), [filters, products, sort]);

  return (
    <main>
      <section className="relative overflow-hidden">
        <div className="relative flex min-h-[320px] items-end px-6 pb-10 md:px-12" style={{ background: collection.gradient }}>
          <Image src={collection.heroImage} alt={collection.name} fill className="object-cover" sizes="100vw" />
          <div className="absolute inset-0 bg-black/35" />
          <div className="relative z-10 max-w-2xl text-white">
            <p className="mb-2 text-sm">Home / {collection.name}</p>
            <h1 className="mb-2 text-3xl font-normal tracking-tight md:text-4xl">{collection.name}</h1>
            <p className="max-w-xl text-sm text-white/80 md:text-base">{collection.description}</p>
          </div>
        </div>
      </section>

      <section className="px-4 py-10 md:px-8 lg:px-12">
        <div className="grid gap-8 lg:grid-cols-[280px_minmax(0,1fr)]">
          <aside className="rounded-[28px] border border-black/5 bg-cream-light p-5">
            <div className="mb-4 flex items-center justify-between">
              <h2 className="text-nav">Filters</h2>
              <button className="text-xs uppercase tracking-[0.4px] text-warm-gray" onClick={() => setFilters({ gender: "All" })}>
                Reset
              </button>
            </div>
            <div className="space-y-5 text-sm">
              <FilterGroup title="Gender">
                <select
                  className="w-full rounded-full border border-black/10 bg-white px-4 py-2"
                  value={filters.gender ?? "All"}
                  onChange={(event) => setFilters((current) => ({ ...current, gender: event.target.value }))}
                >
                  {filterOptions.genders.map((option) => (
                    <option key={option} value={option}>
                      {option}
                    </option>
                  ))}
                </select>
              </FilterGroup>

              <FilterGroup title="Size">
                <div className="flex flex-wrap gap-2">
                  {filterOptions.sizes.map((size) => (
                    <FilterChip
                      key={size}
                      active={filters.size === size}
                      onClick={() => setFilters((current) => ({ ...current, size: current.size === size ? undefined : size }))}
                    >
                      {size}
                    </FilterChip>
                  ))}
                </div>
              </FilterGroup>

              <FilterGroup title="Price">
                <div className="flex flex-wrap gap-2">
                  {[
                    { value: "under-199", label: "Under 199 zl" },
                    { value: "199-399", label: "199 - 399 zl" },
                    { value: "over-399", label: "Over 399 zl" },
                  ].map((option) => (
                    <FilterChip
                      key={option.value}
                      active={filters.price === option.value}
                      onClick={() =>
                        setFilters((current) => ({
                          ...current,
                          price: current.price === option.value ? undefined : (option.value as ProductFilters["price"]),
                        }))
                      }
                    >
                      {option.label}
                    </FilterChip>
                  ))}
                </div>
              </FilterGroup>

              <FilterGroup title="Product Type">
                <div className="flex flex-wrap gap-2">
                  {filterOptions.productTypes.map((item) => (
                    <FilterChip
                      key={item}
                      active={filters.productType === item}
                      onClick={() =>
                        setFilters((current) => ({
                          ...current,
                          productType: current.productType === item ? undefined : item,
                        }))
                      }
                    >
                      {item}
                    </FilterChip>
                  ))}
                </div>
              </FilterGroup>

              <FilterGroup title="Material">
                <div className="flex flex-wrap gap-2">
                  {filterOptions.materials.map((item) => (
                    <FilterChip
                      key={item}
                      active={filters.material === item}
                      onClick={() =>
                        setFilters((current) => ({
                          ...current,
                          material: current.material === item ? undefined : item,
                        }))
                      }
                    >
                      {item}
                    </FilterChip>
                  ))}
                </div>
              </FilterGroup>

              <FilterGroup title="Seller">
                <div className="space-y-2">
                  {filterOptions.sellers.map((seller) => (
                    <label key={seller.id} className="flex items-center gap-2">
                      <input
                        type="radio"
                        name="seller"
                        checked={filters.sellerId === seller.id}
                        onChange={() => setFilters((current) => ({ ...current, sellerId: seller.id }))}
                      />
                      <span>{seller.name}</span>
                    </label>
                  ))}
                  <button
                    className="text-xs uppercase tracking-[0.4px] text-warm-gray"
                    onClick={() => setFilters((current) => ({ ...current, sellerId: undefined }))}
                  >
                    Clear seller
                  </button>
                </div>
              </FilterGroup>
            </div>
          </aside>

          <div>
            <div className="mb-6 flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
              <div>
                <h2 className="text-2xl font-light text-charcoal">{collection.name}</h2>
                <p className="text-sm text-warm-gray">{filteredProducts.length} products</p>
              </div>
              <label className="text-sm text-warm-gray">
                Sort
                <select
                  className="ml-3 rounded-full border border-black/10 bg-white px-4 py-2 text-charcoal"
                  value={sort}
                  onChange={(event) => setSort(event.target.value as SortOption)}
                >
                  <option value="featured">Featured</option>
                  <option value="newest">Newest</option>
                  <option value="top-rated">Top Rated</option>
                  <option value="price-asc">Price: Low to High</option>
                  <option value="price-desc">Price: High to Low</option>
                </select>
              </label>
            </div>

            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 xl:grid-cols-3">
              {filteredProducts.map((product) => (
                <ProductCard key={product.slug} product={product} />
              ))}
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}

function FilterGroup({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div>
      <h3 className="mb-3 text-xs font-medium uppercase tracking-[0.6px] text-charcoal">{title}</h3>
      {children}
    </div>
  );
}

function FilterChip({
  active,
  children,
  onClick,
}: {
  active: boolean;
  children: React.ReactNode;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      className={`rounded-full border px-3 py-1.5 text-xs transition ${
        active ? "border-charcoal bg-charcoal text-white" : "border-black/10 bg-white text-charcoal"
      }`}
      onClick={onClick}
    >
      {children}
    </button>
  );
}
