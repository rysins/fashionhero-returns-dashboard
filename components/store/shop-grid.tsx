import Image from "next/image";
import Link from "next/link";

type ShopGridItem = {
  title: string;
  image: string;
  gradient: string;
  links: { href: string; label: string }[];
};

export function ShopGrid({ items }: { items: ShopGridItem[] }) {
  return (
    <section className="px-4 py-10 md:px-8 lg:px-12">
      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        {items.map((item) => (
          <div key={item.title} className="group relative aspect-[3/4] overflow-hidden" style={{ background: item.gradient }}>
            <Image src={item.image} alt={item.title} fill className="object-cover transition-transform duration-500 group-hover:scale-105" sizes="(max-width: 768px) 100vw, 33vw" />
            <div className="absolute inset-0 bg-black/30 transition-colors duration-300 group-hover:bg-black/40" />
            <div className="absolute bottom-0 left-0 right-0 z-10 p-6 text-center">
              <h3 className="mb-4 text-xl font-normal tracking-wide text-white">{item.title}</h3>
              <div className="flex justify-center gap-3">
                {item.links.map((link) => (
                  <Link
                    key={link.href + link.label}
                    href={link.href}
                    className="inline-flex items-center justify-center rounded-full border border-white px-5 py-2 text-[11px] font-medium uppercase tracking-[0.6px] text-white transition hover:bg-white hover:text-charcoal"
                  >
                    {link.label}
                  </Link>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
