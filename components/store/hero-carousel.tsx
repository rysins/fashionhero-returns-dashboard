"use client";

import Image from "next/image";
import Link from "next/link";
import { useEffect, useState } from "react";

type Slide = {
  id: string;
  eyebrow: string;
  title: string;
  image: string;
  gradient: string;
  primaryHref: string;
  primaryLabel: string;
  secondaryHref: string;
  secondaryLabel: string;
};

export function HeroCarousel({ slides }: { slides: Slide[] }) {
  const [activeIndex, setActiveIndex] = useState(0);
  const [isPaused, setIsPaused] = useState(false);

  useEffect(() => {
    if (isPaused) {
      return undefined;
    }

    const timer = window.setInterval(() => {
      setActiveIndex((current) => (current + 1) % slides.length);
    }, 5000);

    return () => window.clearInterval(timer);
  }, [isPaused, slides.length]);

  const activeSlide = slides[activeIndex];

  return (
    <section className="relative w-full overflow-hidden">
      <div
        className="relative flex min-h-[70vh] items-end px-6 pb-16 transition-all duration-700 md:px-16 md:pb-24"
        style={{ background: activeSlide.gradient }}
      >
        <Image
          src={activeSlide.image}
          alt={activeSlide.title}
          fill
          priority
          className="object-cover"
          sizes="100vw"
        />
        <div className="absolute inset-0 bg-black/30" />
        <div className="relative z-10 max-w-xl">
          <p className="mb-3 text-[11px] font-medium uppercase tracking-[0.6px] text-white/70">{activeSlide.eyebrow}</p>
          <h1 className="mb-8 text-3xl font-normal leading-tight tracking-[0.6px] text-white md:text-5xl lg:text-6xl">
            {activeSlide.title}
          </h1>
          <div className="flex flex-wrap gap-3">
            <Link href={activeSlide.primaryHref} className="rounded-full border border-white px-6 py-2.5 text-[12px] font-medium uppercase tracking-[0.6px] text-white transition hover:bg-white hover:text-charcoal">
              {activeSlide.primaryLabel}
            </Link>
            <Link href={activeSlide.secondaryHref} className="rounded-full border border-white px-6 py-2.5 text-[12px] font-medium uppercase tracking-[0.6px] text-white transition hover:bg-white hover:text-charcoal">
              {activeSlide.secondaryLabel}
            </Link>
          </div>
        </div>
      </div>
      <div className="absolute bottom-4 left-1/2 flex -translate-x-1/2 items-center gap-3">
        {slides.map((slide, index) => (
          <button
            key={slide.id}
            aria-label={`Go to slide ${index + 1}`}
            className={`h-2 w-2 rounded-full transition-colors ${index === activeIndex ? "bg-white" : "bg-white/40"}`}
            onClick={() => setActiveIndex(index)}
          />
        ))}
        <button
          aria-label={isPaused ? "Play carousel" : "Pause carousel"}
          className="ml-2 p-1 text-white/60 transition-colors hover:text-white"
          onClick={() => setIsPaused((current) => !current)}
        >
          {isPaused ? "Play" : "Pause"}
        </button>
      </div>
    </section>
  );
}
