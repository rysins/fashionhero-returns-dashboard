import { describe, expect, it } from "vitest";

import { products } from "@/lib/data/mock-data";
import { filterProducts, getCollectionBySlug, getProductBySlug, sortProducts } from "@/lib/data/selectors";

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
});
