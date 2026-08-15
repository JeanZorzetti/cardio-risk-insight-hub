/** @type {import('next').NextConfig} */
const nextConfig = {
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
  env: {
    // ponytail: production fallback exists because Vercel's NEXT_PUBLIC_API_URL was unset,
    // baking `localhost:8000` into every visitor's browser bundle. Set the real env var in
    // Vercel and this fallback stops mattering.
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL ||
      (process.env.NODE_ENV === 'production' ? 'https://cardioapi.roilabs.com.br' : 'http://localhost:8000'),
  }
}

module.exports = nextConfig