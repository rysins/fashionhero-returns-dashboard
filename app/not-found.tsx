import Link from "next/link";

export default function NotFound() {
  return (
    <main className="flex flex-1 items-center justify-center px-4 py-20">
      <div className="max-w-md text-center">
        <p className="mb-2 text-sm uppercase tracking-[0.6px] text-warm-gray">404</p>
        <h1 className="mb-4 text-4xl font-light text-charcoal">This page could not be found.</h1>
        <p className="mb-6 text-sm leading-relaxed text-warm-gray">
          The route does not exist in this storefront preview yet.
        </p>
        <Link href="/" className="btn-cta">
          BACK TO HOME
        </Link>
      </div>
    </main>
  );
}
