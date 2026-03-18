/** @type {import('next').NextConfig} */
const nextConfig = {
  env: {
    API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
    AUTOMATION_URL: process.env.NEXT_PUBLIC_AUTOMATION_URL || 'http://localhost:3001',
  },
}

module.exports = nextConfig
