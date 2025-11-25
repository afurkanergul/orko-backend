import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  turbopack: {},       // ✔ enables Turbopack
  webpack: undefined,  // ✔ explicitly disables all webpack overrides
};

export default nextConfig;
