import { notFound } from "next/navigation";

import { CollectionPage } from "@/components/store/collection-page";
import { collections } from "@/lib/data/mock-data";
import { getCollectionBySlug, getProductsForCollection } from "@/lib/data/selectors";

export function generateStaticParams() {
  return collections.map((collection) => ({ slug: collection.slug }));
}

export default async function CollectionRoute({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const collection = getCollectionBySlug(slug);

  if (!collection) {
    notFound();
  }

  const products = getProductsForCollection(slug);
  return <CollectionPage collection={collection} products={products} />;
}
