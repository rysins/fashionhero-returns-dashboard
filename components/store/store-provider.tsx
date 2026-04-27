"use client";

import {
  createContext,
  ReactNode,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";

import { defaultScenarioParameters } from "@/lib/data/preview-data";
import { CartItem, ScenarioParameters, WishlistItem } from "@/lib/data/types";

type StoreContextValue = {
  cart: CartItem[];
  wishlist: WishlistItem[];
  isCartOpen: boolean;
  scenario: ScenarioParameters;
  openCart: () => void;
  closeCart: () => void;
  addToCart: (item: CartItem) => void;
  removeFromCart: (item: CartItem) => void;
  toggleWishlist: (productSlug: string) => void;
  isWishlisted: (productSlug: string) => boolean;
  updateScenario: (patch: Partial<ScenarioParameters>) => void;
};

const StoreContext = createContext<StoreContextValue | null>(null);

const CART_KEY = "fashionhero-cart";
const WISHLIST_KEY = "fashionhero-wishlist";
const SCENARIO_KEY = "fashionhero-scenarios";

export function StoreProvider({ children }: { children: ReactNode }) {
  const [cart, setCart] = useState<CartItem[]>([]);
  const [wishlist, setWishlist] = useState<WishlistItem[]>([]);
  const [scenario, setScenario] = useState<ScenarioParameters>(defaultScenarioParameters);
  const [isCartOpen, setIsCartOpen] = useState(false);

  useEffect(() => {
    const cartPayload = window.localStorage.getItem(CART_KEY);
    const wishlistPayload = window.localStorage.getItem(WISHLIST_KEY);
    const scenarioPayload = window.localStorage.getItem(SCENARIO_KEY);

    if (cartPayload) {
      setCart(JSON.parse(cartPayload));
    }

    if (wishlistPayload) {
      setWishlist(JSON.parse(wishlistPayload));
    }

    if (scenarioPayload) {
      setScenario({ ...defaultScenarioParameters, ...JSON.parse(scenarioPayload) });
    }
  }, []);

  useEffect(() => {
    window.localStorage.setItem(CART_KEY, JSON.stringify(cart));
  }, [cart]);

  useEffect(() => {
    window.localStorage.setItem(WISHLIST_KEY, JSON.stringify(wishlist));
  }, [wishlist]);

  useEffect(() => {
    window.localStorage.setItem(SCENARIO_KEY, JSON.stringify(scenario));
  }, [scenario]);

  const value = useMemo<StoreContextValue>(
    () => ({
      cart,
      wishlist,
      isCartOpen,
      scenario,
      openCart: () => setIsCartOpen(true),
      closeCart: () => setIsCartOpen(false),
      addToCart: (item) => {
        setCart((current) => {
          const existing = current.find(
            (entry) =>
              entry.productSlug === item.productSlug &&
              entry.color === item.color &&
              entry.size === item.size,
          );

          if (existing) {
            return current.map((entry) =>
              entry === existing ? { ...entry, quantity: entry.quantity + item.quantity } : entry,
            );
          }

          return [...current, item];
        });
        setIsCartOpen(true);
      },
      removeFromCart: (item) => {
        setCart((current) =>
          current.filter(
            (entry) =>
              !(
                entry.productSlug === item.productSlug &&
                entry.color === item.color &&
                entry.size === item.size
              ),
          ),
        );
      },
      toggleWishlist: (productSlug) => {
        setWishlist((current) =>
          current.some((entry) => entry.productSlug === productSlug)
            ? current.filter((entry) => entry.productSlug !== productSlug)
            : [...current, { productSlug }],
        );
      },
      isWishlisted: (productSlug) => wishlist.some((entry) => entry.productSlug === productSlug),
      updateScenario: (patch) => {
        setScenario((current) => ({ ...current, ...patch }));
      },
    }),
    [cart, isCartOpen, scenario, wishlist],
  );

  return <StoreContext.Provider value={value}>{children}</StoreContext.Provider>;
}

export function useStore() {
  const context = useContext(StoreContext);

  if (!context) {
    throw new Error("useStore must be used inside StoreProvider");
  }

  return context;
}
