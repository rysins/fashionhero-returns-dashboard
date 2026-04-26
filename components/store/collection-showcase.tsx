import Image from "next/image";
import Link from "next/link";

import { Collection } from "@/lib/data/types";

export function CollectionShowcase({ collections }: { collections: Collection[] }) {
  return (
    <section className="px-4 py-10 md:px-8 lg:px-12">
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {collections.map((collection) => (
          <div
            key={collection.slug}
            className="group relative flex aspect-[3/4] flex-col items-center justify-end overflow-hidden"
            style={{ background: collection.gradient }}
          >
            <Image
              src={collection.heroImage}
              alt={collection.name}
              fill
              className="object-cover transition-transform duration-500 group-hover:scale-105"
              sizes="(max-width: 1024px) 50vw, 25vw"
            />
            <div className="absolute inset-0 bg-black/30 transition-colors duration-300 group-hover:bg-black/40" />
            <div className="relative z-10 px-4 pb-8 text-center">
              <h3 className="mb-4 text-xl font-normal tracking-wide text-white">{collection.name}</h3>
              <Link
                href={`/collections/${collection.slug}`}
                className="inline-flex items-center justify-center rounded-full border border-white px-5 py-2 text-[11px] font-medium uppercase tracking-[0.6px] text-white transition-all duration-200 hover:bg-white hover:text-charcoal"
              >
                {collection.ctaLabel}
              </Link>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
