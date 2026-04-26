import Link from "next/link";

import { aboutMilestones } from "@/lib/data/mock-data";

export default function AboutPage() {
  return (
    <main className="px-4 py-10 md:px-8 lg:px-12">
      <section className="mx-auto max-w-5xl py-10">
        <p className="mb-4 text-[11px] font-medium uppercase tracking-[0.8px] text-warm-gray">OUR STORY</p>
        <h1 className="max-w-2xl text-4xl font-light leading-tight text-charcoal md:text-5xl">
          Where sellers grow and buyers discover.
        </h1>
      </section>

      <section className="mx-auto grid max-w-5xl gap-10 py-6 md:grid-cols-3">
        <div>
          <p className="mb-2 text-[11px] font-medium uppercase tracking-[0.8px] text-warm-gray">OUR MISSION</p>
          <p className="text-sm leading-relaxed text-warm-gray">
            FashionHero started with a simple idea: fashion should not be controlled by a few big players. We are building a marketplace where independent sellers compete alongside global brands and where buyers can discover styles they would never find on their own.
          </p>
        </div>
        <div>
          <p className="mb-2 text-[11px] font-medium uppercase tracking-[0.8px] text-warm-gray">WHAT WE STAND FOR</p>
          <div className="space-y-4 text-sm leading-relaxed text-warm-gray">
            <p>
              <span className="font-medium text-charcoal">Empowering Sellers.</span> Independent sellers and established brands get access to a premium storefront and shared buyer demand.
            </p>
            <p>
              <span className="font-medium text-charcoal">Curated Discovery.</span> Marketplace variety only matters if the buyer can navigate it with confidence.
            </p>
            <p>
              <span className="font-medium text-charcoal">Fair For Everyone.</span> Visibility, proof signals and seller trust need to scale beyond the biggest accounts.
            </p>
          </div>
        </div>
        <div>
          <p className="mb-2 text-[11px] font-medium uppercase tracking-[0.8px] text-warm-gray">WHY THIS COPY EXISTS</p>
          <p className="text-sm leading-relaxed text-warm-gray">
            This preview environment is a working copy of the storefront used to test future discovery, seller visibility and conversion ideas before deeper platform work starts.
          </p>
        </div>
      </section>

      <section className="mx-auto max-w-5xl py-12">
        <p className="mb-4 text-[11px] font-medium uppercase tracking-[0.8px] text-warm-gray">OUR JOURNEY</p>
        <div className="space-y-4">
          {aboutMilestones.map((item) => (
            <div key={item.year} className="grid gap-2 rounded-[28px] border border-black/5 bg-cream-light px-6 py-5 md:grid-cols-[120px_1fr]">
              <p className="text-lg font-medium text-charcoal">{item.year}</p>
              <p className="text-sm leading-relaxed text-warm-gray">{item.label}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="mx-auto max-w-5xl rounded-[36px] bg-charcoal px-8 py-12 text-white">
        <p className="mb-3 text-[11px] font-medium uppercase tracking-[0.8px] text-white/60">READY TO STEP FORWARD?</p>
        <h2 className="mb-6 text-3xl font-light">Start exploring.</h2>
        <div className="flex flex-wrap gap-3">
          <Link href="/collections/mens" className="rounded-full border border-white px-5 py-2 text-[11px] font-medium uppercase tracking-[0.6px] text-white transition hover:bg-white hover:text-charcoal">
            SHOP MEN
          </Link>
          <Link href="/collections/womens" className="rounded-full border border-white px-5 py-2 text-[11px] font-medium uppercase tracking-[0.6px] text-white transition hover:bg-white hover:text-charcoal">
            SHOP WOMEN
          </Link>
        </div>
      </section>
    </main>
  );
}
