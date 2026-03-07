import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "richardnixon.dev",
      },
    ],
  },
};

export default nextConfig;
