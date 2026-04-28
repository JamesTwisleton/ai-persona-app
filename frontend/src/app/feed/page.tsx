"use client";

import { Navbar } from "@/components/layout/Navbar";
import { DiscoveryFeed } from "@/components/layout/DiscoveryFeed";

export default function FeedPage() {
  return (
    <div className="min-h-screen">
      <Navbar />
      <DiscoveryFeed />
    </div>
  );
}
