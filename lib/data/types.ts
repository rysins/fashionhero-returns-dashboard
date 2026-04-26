export type Seller = {
  id: string;
  name: string;
  isPro: boolean;
  location?: string;
  description?: string;
};

export type ProductVariant = {
  color: string;
  hex: string;
  image: string;
  sizes: string[];
};

export type ReviewSummary = {
  average: number;
  count: number;
};

export type Product = {
  slug: string;
  name: string;
  category: string;
  gender: "Men" | "Women" | "Unisex";
  sellerId: string;
  price: number;
  badge?: "NEW" | "BESTSELLER";
  material: string;
  productType: string;
  shortDescription: string;
  description: string;
  features: string[];
  materials: string;
  care: string;
  stockStatus: string;
  rating: ReviewSummary;
  variants: ProductVariant[];
  collectionSlugs: string[];
  featuredOrder: number;
};

export type Collection = {
  slug: string;
  name: string;
  description: string;
  heroImage: string;
  gradient: string;
  ctaLabel: string;
  productSlugs: string[];
};

export type CartItem = {
  productSlug: string;
  color: string;
  size: string;
  quantity: number;
};

export type WishlistItem = {
  productSlug: string;
};
