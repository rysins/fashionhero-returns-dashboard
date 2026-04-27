"use client";

import Image from "next/image";
import Link from "next/link";

import { useStore } from "@/components/store/store-provider";
import { getSoftPenaltyEligibility } from "@/lib/data/preview-data";
import { getProductBySlug } from "@/lib/data/selectors";

export function CartDrawer() {
  const { cart, isCartOpen, closeCart, removeFromCart, scenario } = useStore();
  const softPenalty = getSoftPenaltyEligibility(scenario);

  return (
    <>
      <button
        type="button"
        aria-label="Close cart"
        className={`fixed inset-0 z-40 bg-black/40 transition ${isCartOpen ? "opacity-100" : "pointer-events-none opacity-0"}`}
        onClick={closeCart}
      />
      <aside
        className={`fixed right-0 top-0 z-50 flex h-full w-full max-w-md flex-col bg-white shadow-panel transition-transform duration-300 ${
          isCartOpen ? "translate-x-0" : "translate-x-full"
        }`}
      >
        <div className="flex items-center justify-between border-b px-4 py-4">
          <h2 className="text-nav">CART ({cart.reduce((sum, item) => sum + item.quantity, 0)})</h2>
          <button aria-label="Close cart" onClick={closeCart} className="text-2xl leading-none">
            ×
          </button>
        </div>
        <div className="bg-cream-light px-4 py-3 text-center">
          <p className="text-xs text-warm-gray">
            {softPenalty.qualifies
              ? "Preview: this shopper would pay the return shipment cost on future returns."
              : "Spend 299 zl more to earn free shipping!"}
          </p>
        </div>
        <div className="flex-1 overflow-y-auto px-4 py-4">
          {cart.length === 0 ? (
            <div className="py-12 text-center">
              <p className="mb-4 text-sm text-warm-gray">Your cart is empty. Start shopping!</p>
              <div className="space-y-2">
                <Link href="/collections/womens" className="btn-cta block" onClick={closeCart}>
                  SHOP WOMENS
                </Link>
                <Link href="/collections/mens" className="btn-cta-outline block" onClick={closeCart}>
                  SHOP MENS
                </Link>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              {cart.map((item) => {
                const product = getProductBySlug(item.productSlug);
                const variant = product?.variants.find((entry) => entry.color === item.color) ?? product?.variants[0];

                if (!product || !variant) {
                  return null;
                }

                return (
                  <div key={`${item.productSlug}-${item.color}-${item.size}`} className="flex gap-3 border-b pb-4">
                    <div className="relative h-24 w-24 overflow-hidden rounded bg-cream">
                      <Image src={variant.image} alt={product.name} fill className="object-cover" sizes="96px" />
                    </div>
                    <div className="flex flex-1 flex-col">
                      <p className="text-sm font-medium uppercase tracking-[0.4px]">{product.name}</p>
                      <p className="text-xs text-warm-gray">{item.color}</p>
                      <p className="text-xs text-warm-gray">Size {item.size}</p>
                      <p className="mt-1 text-sm font-medium">{product.price} zl</p>
                      <div className="mt-auto flex items-center justify-between pt-2">
                        <span className="text-xs text-warm-gray">Qty {item.quantity}</span>
                        <button
                          type="button"
                          className="text-xs uppercase tracking-[0.4px] text-warm-gray transition hover:text-charcoal"
                          onClick={() => removeFromCart(item)}
                        >
                          Remove
                        </button>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </aside>
    </>
  );
}
