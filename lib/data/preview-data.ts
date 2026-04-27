import phase2Config from "@/shared/fashionhero_phase2_config.json";

import {
  CategoryAggregate,
  InterventionDefinition,
  InterventionEligibility,
  Product,
  ProductAnalytics,
  ScenarioParameters,
  Seller,
  SellerAnalytics,
} from "@/lib/data/types";

type InterventionConfigRecord = typeof phase2Config.interventions;

const sellerOverrides: Record<string, Partial<SellerAnalytics>> = {
  "urban-edge": { returnRate: 0.21, effectiveCommissionRate: 0.18, marginContribution: 210, risk: "healthy" },
  "bella-donna": { returnRate: 0.29, effectiveCommissionRate: 0.19, marginContribution: 182, risk: "warning" },
  "marta-handmade": { returnRate: 0.11, effectiveCommissionRate: 0.22, marginContribution: 95, risk: "healthy" },
  "eco-threads": { returnRate: 0.16, effectiveCommissionRate: 0.22, marginContribution: 141, risk: "healthy" },
  "drop-style": { returnRate: 0.47, effectiveCommissionRate: 0.22, marginContribution: -18, risk: "risky" },
};

const productReturnRateOverrides: Record<string, number> = {
  "cloud-runner": 0.18,
  "trail-pacer": 0.22,
  "dash-sport": 0.24,
  "breeze-slip-on": 0.17,
  "aero-knit": 0.33,
  "wrap-dress": 0.29,
  "oversized-blazer": 0.35,
  "reczne-baleriny": 0.12,
};

export const interventionDefinitions: InterventionDefinition[] = Object.entries(
  phase2Config.interventions as InterventionConfigRecord,
).map(([code, definition]) => ({
  code: code as InterventionDefinition["code"],
  label: definition.label,
  targetType: definition.target_type as InterventionDefinition["targetType"],
  defaults: Object.fromEntries(
    Object.entries(definition).filter(([, value]) => typeof value === "number"),
  ) as Record<string, number>,
}));

export const defaultScenarioParameters: ScenarioParameters = {
  softPenaltyEnabled: false,
  dynamicCommissionEnabled: false,
  promoteLowReturnProductsEnabled: false,
  currentBuyerProfile: "baseline",
  quarterReturnsCount: 1,
};

export function slugifyCategory(category: string) {
  return category.toLowerCase().replace(/[^a-z0-9]+/g, "_").replace(/^_|_$/g, "");
}

export function getSellerAnalytics(seller: Seller): SellerAnalytics {
  const override = sellerOverrides[seller.id] ?? {};
  const returnRate = override.returnRate ?? (seller.isPro ? 0.24 : 0.34);
  const marginContribution = override.marginContribution ?? (seller.isPro ? 130 : 55);
  const effectiveCommissionRate = override.effectiveCommissionRate ?? (seller.isPro ? 0.2 : 0.22);
  const risk =
    override.risk ??
    (returnRate >= phase2Config.seller_thresholds.risky_return_rate
      ? "risky"
      : returnRate >= phase2Config.seller_thresholds.warning_return_rate
        ? "warning"
        : "healthy");
  return {
    returnRate,
    effectiveCommissionRate,
    commissionTier: effectiveCommissionRate < 0.2 ? "negotiated" : "standard",
    marginContribution,
    risk,
  };
}

export function getProductAnalytics(product: Product, seller?: Seller): ProductAnalytics {
  const sellerAnalytics = seller
    ? getSellerAnalytics(seller)
    : {
        returnRate: 0.28,
        effectiveCommissionRate: 0.22,
        marginContribution: 90,
        commissionTier: "standard" as const,
        risk: "warning" as const,
      };
  const returnRate =
    productReturnRateOverrides[product.slug] ??
    Number(
      Math.max(
        0.08,
        Math.min(
          0.55,
          (product.badge === "BESTSELLER" ? 0.16 : 0.22) +
            (product.category.includes("Apparel") ? 0.09 : 0) +
            (sellerAnalytics.risk === "risky" ? 0.14 : sellerAnalytics.risk === "warning" ? 0.06 : 0),
        ),
      ).toFixed(2),
    );
  const baseMargin = Number((product.price * sellerAnalytics.effectiveCommissionRate).toFixed(1));
  const marginContribution = Number((baseMargin - product.price * returnRate * 0.45).toFixed(1));
  const promotionScore = Number(
    (
      (1 - returnRate) * 100 +
      product.rating.average * 8 +
      (product.badge === "BESTSELLER" ? 10 : 0) +
      marginContribution / 3
    ).toFixed(1),
  );
  const health =
    returnRate <= phase2Config.category_thresholds.healthy_return_rate_max && marginContribution >= 25
      ? "healthy"
      : returnRate <= phase2Config.category_thresholds.warning_return_rate_max && marginContribution >= 8
        ? "warning"
        : "critical";
  return {
    productId: product.slug,
    categoryId: slugifyCategory(product.category),
    returnRate,
    marginContribution,
    promotionScore,
    health,
  };
}

export function getCategoryAggregate(products: Product[], sellers: Seller[], categoryName: string): CategoryAggregate {
  const categoryProducts = products.filter((product) => product.category === categoryName);
  const productAnalytics = categoryProducts.map((product) =>
    getProductAnalytics(product, sellers.find((seller) => seller.id === product.sellerId)),
  );
  const estimatedOrders = categoryProducts.length * 18;
  const gmvLast30d = categoryProducts.reduce((sum, product) => sum + product.price * 18, 0);
  const marginContribution = productAnalytics.reduce((sum, entry) => sum + entry.marginContribution, 0);
  const returnRateLast30d =
    productAnalytics.reduce((sum, entry) => sum + entry.returnRate, 0) / Math.max(productAnalytics.length, 1);
  const contributionPerOrder = marginContribution / Math.max(estimatedOrders, 1);
  const toxicShare = Math.min(0.45, Math.max(0.08, returnRateLast30d - 0.08));
  const health =
    returnRateLast30d <= phase2Config.category_thresholds.healthy_return_rate_max && contributionPerOrder >= 20
      ? "healthy"
      : returnRateLast30d <= phase2Config.category_thresholds.warning_return_rate_max && contributionPerOrder >= 8
        ? "warning"
        : "critical";
  return {
    categoryId: slugifyCategory(categoryName),
    categoryName,
    gmvLast30d,
    returnRateLast30d,
    marginContribution,
    contributionPerOrder,
    toxicShare,
    health,
  };
}

export function getSoftPenaltyEligibility(parameters: ScenarioParameters): InterventionEligibility {
  if (!parameters.softPenaltyEnabled) {
    return { qualifies: false, reason: "Soft penalty preview is disabled." };
  }
  if (parameters.currentBuyerProfile !== "high_returner") {
    return { qualifies: false, reason: "Current preview shopper is not in the high-return cohort." };
  }
  if (parameters.quarterReturnsCount <= phase2Config.interventions.soft_penalty_high_returners.free_returns_per_quarter) {
    return { qualifies: false, reason: "Shopper is still within the free-return limit for the quarter." };
  }
  return { qualifies: true, reason: "Buyer exceeded the free-return limit and would pay return shipping." };
}
