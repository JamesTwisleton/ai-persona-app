"use client";

import { Suspense, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import { Spinner } from "@/components/ui/Spinner";
import { ErrorMessage } from "@/components/ui/ErrorMessage";

function AuthCallbackContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { login } = useAuth();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const token = searchParams.get("token");
    if (!token) {
      setError("No token received. Please try signing in again.");
      return;
    }

    login(token)
      .then(() => router.replace("/personas"))
      .catch(() => {
        setError("Failed to authenticate. Please try again.");
      });
  }, [searchParams, login, router]);

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="max-w-sm w-full px-4">
          <ErrorMessage message={error} />
          <div className="text-center mt-4">
            <a href="/login" className="text-teal-600 hover:underline text-sm">
              Back to login
            </a>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col items-center justify-center gap-4">
      <Spinner size="lg" />
      <p className="text-gray-500 text-sm">Signing you in…</p>
    </div>
  );
}

export default function AuthCallbackPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen flex flex-col items-center justify-center gap-4">
          <Spinner size="lg" />
          <p className="text-gray-500 text-sm">Loading…</p>
        </div>
      }
    >
      <AuthCallbackContent />
    </Suspense>
  );
}
