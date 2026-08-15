import type { MetadataRoute } from 'next'

const BASE = 'https://cardiorisk.roilabs.com.br'

export default function sitemap(): MetadataRoute.Sitemap {
  const lastModified = new Date()
  return [
    { url: `${BASE}/calculadora`, lastModified, changeFrequency: 'monthly', priority: 1 },
    { url: `${BASE}/calculadora/prevent`, lastModified, changeFrequency: 'monthly', priority: 1 },
    { url: `${BASE}/metodologia`, lastModified, changeFrequency: 'monthly', priority: 0.8 },
  ]
}
