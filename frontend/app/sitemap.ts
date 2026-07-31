import type { MetadataRoute } from 'next'

const BASE = 'https://cardiorisk.roilabs.com.br'

export default function sitemap(): MetadataRoute.Sitemap {
  return [{ url: BASE, lastModified: new Date(), changeFrequency: 'monthly', priority: 1 }]
}
