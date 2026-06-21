/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Static export: `next build` emits a static site to ./out, served by FastAPI
  // in the single-container deployment. Set NEXT_PUBLIC_API_URL to "" for
  // same-origin (container) or to a full URL for a separate backend.
  output: 'export',
  images: { unoptimized: true },
  trailingSlash: true,
  env: { NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL ?? '' },
};
module.exports = nextConfig;
