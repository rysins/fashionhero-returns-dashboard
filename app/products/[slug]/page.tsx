import { notFound } from "next/navigation";

import { ProductDetail } from "@/components/store/product-detail";
import { products } from "@/lib/data/mock-data";
import { getProductBySlug } from "@/lib/data/selectors";

export function generateStaticParams() {
  return products.map((product) => ({ slug: product.slug }));
}

export default async function ProductRoute({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const product = getProductBySlug(slug);

  if (!product) {
    notFound();
  }

  return <ProductDetail product={product} />;
}
