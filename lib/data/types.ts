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

export type ProductAnalytics = {
  productId: string;
  categoryId: string;
  returnRate: number;
  marginContribution: number;
  promotionScore: number;
  health: "healthy" | "warning" | "critical";
};

export type SellerAnalytics = {
  returnRate: number;
  effectiveCommissionRate: number;
  commissionTier: "standard" | "negotiated" | "uplifted";
  marginContribution: number;
  risk: "healthy" | "warning" | "risky";
};

export type CategoryAggregate = {
  categoryId: string;
  categoryName: string;
  gmvLast30d: number;
  returnRateLast30d: number;
  marginContribution: number;
  contributionPerOrder: number;
  toxicShare: number;
  health: "healthy" | "warning" | "critical";
};

export type InterventionDefinition = {
  code: "soft_penalty_high_returners" | "dynamic_commission_high_return_sellers" | "promote_low_return_products";
  label: string;
  targetType: "user" | "seller" | "product";
  defaults: Record<string, number>;
};

export type InterventionEligibility = {
  qualifies: boolean;
  reason: string;
};

export type ScenarioParameters = {
  softPenaltyEnabled: boolean;
  dynamicCommissionEnabled: boolean;
  promoteLowReturnProductsEnabled: boolean;
  currentBuyerProfile: "baseline" | "high_returner";
  quarterReturnsCount: number;
};

export type ScenarioResult = {
  deltaMargin: number;
  deltaGmv: number;
  affectedEntities: number;
  headline: string;
};

export type PipelineRunManifest = {
  snapshotDate: string;
  sourceDir: string;
  validationStatus: string;
  recordCounts: Record<string, number>;
  rejectedRecords: number;
};
