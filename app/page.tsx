import { CollectionShowcase } from "@/components/store/collection-showcase";
import { EditorialGrid } from "@/components/store/editorial-grid";
import { FavoritesSection } from "@/components/store/favorites-section";
import { FeatureStrip } from "@/components/store/feature-strip";
import { HeroCarousel } from "@/components/store/hero-carousel";
import { ShopGrid } from "@/components/store/shop-grid";
import { collections, heroSlides, homeFeatureCards, products } from "@/lib/data/mock-data";

export default function HomePage() {
  const featuredCollections = collections.filter((collection) =>
    ["new-arrivals", "mens", "womens", "best-sellers"].includes(collection.slug),
  );
  const newArrivals = products.filter((product) => product.collectionSlugs.includes("new-arrivals")).slice(0, 8);
  const bestSellers = products.filter((product) => product.collectionSlugs.includes("best-sellers")).slice(0, 8);

  return (
    <main>
      <HeroCarousel slides={heroSlides} />
      <CollectionShowcase collections={featuredCollections} />
      <FavoritesSection newArrivals={newArrivals} bestSellers={bestSellers} />
      <EditorialGrid
        items={[
          {
            title: "Cloud Runner",
            eyebrow: "NATURALLY EASY",
            body: "Our lightest seller-backed runner. Strong reviews, fast repeat purchase behavior and low return anxiety.",
            image: "/images/products/product-9.jpg",
            gradient: "linear-gradient(160deg, #8a7d6b 0%, #c4b59a 40%, #e8dfd0 100%)",
            href: "/products/cloud-runner",
          },
          {
            title: "Breeze Slip-On",
            eyebrow: "LIGHT ON YOUR FEET",
            body: "An easy-to-style best seller with polished shape, simple fit story and solid seller trust signals.",
            image: "/images/products/product-15.jpg",
            gradient: "linear-gradient(160deg, #5c6b4f 0%, #8a9a7a 40%, #c5cfbb 100%)",
            href: "/products/breeze-slip-on",
          },
        ]}
      />
      <ShopGrid
        items={[
          {
            title: "Trail Collection",
            image: "/images/products/product-3.jpg",
            gradient: "linear-gradient(170deg, #3d5a3d 0%, #5c7a5c 40%, #8a9a7a 100%)",
            links: [
              { href: "/collections/mens", label: "SHOP MEN" },
              { href: "/collections/womens", label: "SHOP WOMEN" },
            ],
          },
          {
            title: "Everyday Essentials",
            image: "/images/products/product-4.jpg",
            gradient: "linear-gradient(170deg, #6b5b4a 0%, #a89279 40%, #c4b59a 100%)",
            links: [
              { href: "/collections/new-arrivals", label: "NEW" },
              { href: "/collections/best-sellers", label: "BEST" },
            ],
          },
          {
            title: "Sale",
            image: "/images/products/product-7.jpg",
            gradient: "linear-gradient(170deg, #9e4040 0%, #c06060 40%, #d48a8a 100%)",
            links: [
              { href: "/collections/sale", label: "SHOP SALE" },
            ],
          },
        ]}
      />
      <FeatureStrip items={homeFeatureCards} />
    </main>
  );
}
