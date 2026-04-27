import { collections, products, sellers } from "@/lib/data/mock-data";
import { getProductAnalytics, getSellerAnalytics } from "@/lib/data/preview-data";
import { Collection, Product, ScenarioParameters, Seller } from "@/lib/data/types";

export type ProductFilters = {
  gender?: string;
  size?: string;
  price?: "under-199" | "199-399" | "over-399";
  productType?: string;
  material?: string;
  sellerId?: string;
};

export type SortOption = "featured" | "price-asc" | "price-desc" | "top-rated" | "newest";

export function getCollectionBySlug(slug: string): Collection | undefined {
  return collections.find((collection) => collection.slug === slug);
}

export function getProductBySlug(slug: string): Product | undefined {
  return products.find((product) => product.slug === slug);
}

export function getSellerById(id: string) {
  return sellers.find((seller) => seller.id === id);
}

export function getProductsForCollection(slug: string) {
  return products.filter((product) => product.collectionSlugs.includes(slug));
}

export function getRecommendedProducts(product: Product, limit = 4, scenario?: ScenarioParameters) {
  return rankProductsForScenario(
    products
      .filter((candidate) => candidate.slug !== product.slug)
      .filter(
        (candidate) =>
          candidate.sellerId === product.sellerId ||
          candidate.productType === product.productType ||
          candidate.collectionSlugs.some((slug) => product.collectionSlugs.includes(slug)),
      ),
    scenario,
  ).slice(0, limit);
}

export function filterProducts(items: Product[], filters: ProductFilters) {
  return items.filter((product) => {
    if (filters.gender && filters.gender !== "All" && product.gender !== filters.gender) {
      return false;
    }

    if (filters.size && !product.variants.some((variant) => variant.sizes.includes(filters.size!))) {
      return false;
    }

    if (filters.price === "under-199" && product.price >= 199) {
      return false;
    }

    if (filters.price === "199-399" && (product.price < 199 || product.price > 399)) {
      return false;
    }

    if (filters.price === "over-399" && product.price <= 399) {
      return false;
    }

    if (filters.productType && product.productType !== filters.productType) {
      return false;
    }

    if (filters.material && product.material !== filters.material) {
      return false;
    }

    if (filters.sellerId && product.sellerId !== filters.sellerId) {
      return false;
    }

    return true;
  });
}

export function sortProducts(items: Product[], sort: SortOption) {
  const cloned = [...items];

  switch (sort) {
    case "price-asc":
      return cloned.sort((left, right) => left.price - right.price);
    case "price-desc":
      return cloned.sort((left, right) => right.price - left.price);
    case "top-rated":
      return cloned.sort((left, right) => right.rating.average - left.rating.average);
    case "newest":
      return cloned.sort((left, right) => {
        const leftScore = left.badge === "NEW" ? 1 : 0;
        const rightScore = right.badge === "NEW" ? 1 : 0;
        return rightScore - leftScore || left.featuredOrder - right.featuredOrder;
      });
    case "featured":
    default:
      return cloned.sort((left, right) => left.featuredOrder - right.featuredOrder);
  }
}

export function rankProductsForScenario(items: Product[], scenario?: ScenarioParameters) {
  if (!scenario?.promoteLowReturnProductsEnabled) {
    return sortProducts(items, "featured");
  }

  return [...items].sort((left, right) => {
    const leftSeller = getSellerById(left.sellerId);
    const rightSeller = getSellerById(right.sellerId);
    const leftAnalytics = getProductAnalytics(left, leftSeller);
    const rightAnalytics = getProductAnalytics(right, rightSeller);
    return rightAnalytics.promotionScore - leftAnalytics.promotionScore || left.featuredOrder - right.featuredOrder;
  });
}

export function getFilterOptions(items: Product[]) {
  return {
    genders: ["All", ...new Set(items.map((item) => item.gender))],
    sizes: [...new Set(items.flatMap((item) => item.variants.flatMap((variant) => variant.sizes)))],
    productTypes: [...new Set(items.map((item) => item.productType))],
    materials: [...new Set(items.map((item) => item.material))],
    sellers: sellers.filter((seller) => items.some((item) => item.sellerId === seller.id)),
  };
}

export function getScenarioProductCallout(product: Product, scenario?: ScenarioParameters) {
  const seller = getSellerById(product.sellerId);
  const analytics = getProductAnalytics(product, seller);

  if (scenario?.promoteLowReturnProductsEnabled && analytics.health === "healthy") {
    return "Low-return product boosted in preview ranking";
  }
  if (analytics.health === "critical") {
    return "High return-risk item";
  }
  return null;
}

export function getScenarioSellerBadge(seller: Seller | undefined, scenario?: ScenarioParameters) {
  if (!seller) {
    return null;
  }
  const analytics = getSellerAnalytics(seller);
  if (scenario?.dynamicCommissionEnabled && analytics.risk === "risky") {
    return `Preview commission ${Math.round((analytics.effectiveCommissionRate + 0.03) * 100)}%`;
  }
  return `Base commission ${Math.round(analytics.effectiveCommissionRate * 100)}%`;
}
