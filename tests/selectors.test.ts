import { describe, expect, it } from "vitest";

import { products } from "@/lib/data/mock-data";
import { defaultScenarioParameters } from "@/lib/data/preview-data";
import {
  filterProducts,
  getCollectionBySlug,
  getProductBySlug,
  getRecommendedProducts,
  getScenarioProductCallout,
  getScenarioSellerBadge,
  rankProductsForScenario,
  sortProducts,
} from "@/lib/data/selectors";

describe("selectors", () => {
  it("returns collection by slug", () => {
    expect(getCollectionBySlug("womens")?.name).toBe("Women's Fashion");
  });

  it("returns product by slug", () => {
    expect(getProductBySlug("cloud-runner")?.name).toBe("Cloud Runner");
  });

  it("filters products by seller and price range", () => {
    const result = filterProducts(products, { sellerId: "bella-donna", price: "over-399" });
    expect(result.length).toBeGreaterThan(0);
    expect(result.every((item) => item.sellerId === "bella-donna" && item.price > 399)).toBe(true);
  });

  it("sorts products by ascending price", () => {
    const sorted = sortProducts(products.slice(0, 4), "price-asc");
    expect(sorted[0].price).toBeLessThanOrEqual(sorted[1].price);
  });

  it("reorders products when low-return promotion preview is enabled", () => {
    const sample = products.slice(0, 6);
    const ranked = rankProductsForScenario(sample, {
      ...defaultScenarioParameters,
      promoteLowReturnProductsEnabled: true,
    });
    expect(ranked.map((product) => product.slug)).not.toEqual(sample.map((product) => product.slug));
  });

  it("creates preview recommendations for a product", () => {
    const recommended = getRecommendedProducts(products[0], 4, {
      ...defaultScenarioParameters,
      promoteLowReturnProductsEnabled: true,
    });
    expect(recommended).toHaveLength(4);
    expect(recommended.every((product) => product.slug !== products[0].slug)).toBe(true);
  });

  it("returns preview seller badge and product callout", () => {
    const badge = getScenarioSellerBadge(undefined, defaultScenarioParameters);
    const callout = getScenarioProductCallout(products[0], {
      ...defaultScenarioParameters,
      promoteLowReturnProductsEnabled: true,
    });
    expect(badge).toBeNull();
    expect(callout).toBeTruthy();
  });
});
