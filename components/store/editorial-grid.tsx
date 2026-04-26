import Image from "next/image";
import Link from "next/link";

type EditorialCard = {
  title: string;
  eyebrow: string;
  body: string;
  image: string;
  gradient: string;
  href: string;
};

export function EditorialGrid({ items }: { items: EditorialCard[] }) {
  return (
    <section className="px-4 py-10 md:px-8 lg:px-12">
      <h2 className="mb-10 text-center text-[40px] font-normal text-charcoal">Your Easy, Breezy MVP</h2>
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        {items.map((item) => (
          <div key={item.title} className="group relative min-h-[520px] overflow-hidden" style={{ background: item.gradient }}>
            <Image src={item.image} alt={item.title} fill className="object-cover transition-transform duration-500 group-hover:scale-105" sizes="(max-width: 768px) 100vw, 50vw" />
            <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-black/20 to-transparent" />
            <div className="absolute bottom-0 left-0 right-0 z-10 p-8">
              <p className="mb-2 text-[11px] font-medium uppercase tracking-[0.8px] text-white/70">{item.eyebrow}</p>
              <h3 className="mb-2 text-2xl font-normal text-white">{item.title}</h3>
              <p className="mb-6 max-w-xs text-sm leading-relaxed text-white/80">{item.body}</p>
              <Link
                href={item.href}
                className="inline-flex items-center justify-center rounded-full border border-white px-5 py-2 text-[11px] font-medium uppercase tracking-[0.6px] text-white transition hover:bg-white hover:text-charcoal"
              >
                EXPLORE MORE
              </Link>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
