"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/context/AuthContext";

export function Navbar() {
  const { user, logout } = useAuth();
  const pathname = usePathname();

  const navLinks = [
    { href: "/personas", label: "Personas" },
    { href: "/conversations", label: "Conversations" },
  ];

  return (
    <nav className="bg-white border-b border-gray-200">
      <div className="max-w-5xl mx-auto px-4 flex items-center justify-between h-14">
        <Link href="/" className="font-bold text-indigo-600 text-lg">
          AI Focus Groups
        </Link>

        <div className="flex items-center gap-6">
          {navLinks.map(({ href, label }) => (
            <Link
              key={href}
              href={href}
              className={`text-sm font-medium transition-colors ${
                pathname?.startsWith(href)
                  ? "text-indigo-600"
                  : "text-gray-600 hover:text-gray-900"
              }`}
            >
              {label}
            </Link>
          ))}

          {user && (
            <div className="flex items-center gap-3">
              <span className="text-sm text-gray-500 hidden sm:block">
                {user.name ?? user.email}
              </span>
              <button
                onClick={logout}
                className="text-sm text-gray-500 hover:text-red-600 transition-colors"
              >
                Sign out
              </button>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
}
