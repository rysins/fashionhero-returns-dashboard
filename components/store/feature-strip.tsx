type Feature = {
  title: string;
  heading: string;
  body: string;
};

export function FeatureStrip({ items }: { items: Feature[] }) {
  return (
    <section className="bg-cream-light px-4 py-16 md:px-8 lg:px-12">
      <div className="mx-auto grid max-w-5xl grid-cols-1 gap-10 text-center md:grid-cols-3">
        {items.map((item) => (
          <div key={item.title}>
            <p className="mb-2 text-[11px] font-medium uppercase tracking-[0.8px] text-warm-gray">{item.title}</p>
            <h3 className="mb-3 text-lg font-normal text-charcoal">{item.heading}</h3>
            <p className="text-sm leading-relaxed text-warm-gray">{item.body}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
