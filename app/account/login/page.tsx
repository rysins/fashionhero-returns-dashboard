export default function LoginPage() {
  return (
    <main className="flex flex-1 items-center justify-center px-4 py-16">
      <section className="w-full max-w-md rounded-[36px] border border-black/5 bg-white p-8 shadow-panel">
        <p className="mb-2 text-center text-[11px] font-medium uppercase tracking-[0.8px] text-warm-gray">Account</p>
        <h1 className="mb-8 text-center text-2xl font-light text-charcoal">Sign In</h1>

        <form className="space-y-4">
          <label className="block text-sm text-warm-gray">
            Email
            <input
              type="email"
              className="mt-2 w-full rounded-2xl border border-black/10 px-4 py-3 text-charcoal outline-none transition focus:border-charcoal"
              placeholder="you@example.com"
            />
          </label>

          <label className="block text-sm text-warm-gray">
            Password
            <input
              type="password"
              className="mt-2 w-full rounded-2xl border border-black/10 px-4 py-3 text-charcoal outline-none transition focus:border-charcoal"
              placeholder="••••••••"
            />
          </label>

          <button type="submit" className="btn-cta w-full">
            SIGN IN
          </button>
        </form>

        <div className="mt-6 rounded-[28px] bg-cream-light px-5 py-4 text-sm text-warm-gray">
          Login remains a UI shell in v1. Authentication and account flows are intentionally out of scope for this storefront preview.
        </div>
      </section>
    </main>
  );
}
