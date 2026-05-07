/** @type {import('next').NextConfig} */
module.exports = {
  reactStrictMode: true,
  experimental: {
    serverComponentsExternalPackages: ['postgres'],
  },
  transpilePackages: [
    '@agentboard/agents',
    '@agentboard/config',
    '@agentboard/database',
    '@agentboard/memory',
    '@agentboard/shared',
  ],
};
