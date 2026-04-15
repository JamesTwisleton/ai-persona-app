"use client";

import { useAuth } from "@/context/AuthContext";
import { Navbar } from "@/components/layout/Navbar";
import { Onboarding } from "@/components/layout/Onboarding";
import { DiscoveryFeed } from "@/components/layout/DiscoveryFeed";

export default function Home() {
  const { user, isLoading: authLoading } = useAuth();

  if (!authLoading && !user) {
    return (
      <div className="min-h-screen">
        <Navbar />
        <Onboarding />
      </div>
    );
  }

  return (
    <div className="min-h-screen">
      <Navbar />
      <DiscoveryFeed />
    </div>
  );
}
