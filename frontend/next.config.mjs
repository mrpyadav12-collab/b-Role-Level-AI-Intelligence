/** @type {import('next').NextConfig} */
const nextConfig = {
  typescript: {
    ignoreBuildErrors: true,
  },
  images: {
    unoptimized: true,
  },
  async rewrites() {
    const configuredBackendUrl = process.env.NEXT_PUBLIC_BACKEND_URL
    const backendUrl = configuredBackendUrl
      ? /^https?:\/\//.test(configuredBackendUrl)
        ? configuredBackendUrl
        : `https://${configuredBackendUrl}`
      : "http://localhost:8000"
    return [
      {
        source: "/api/:path*",
        destination: `${backendUrl}/:path*`,
      },
    ]
  },
}

export default nextConfig
