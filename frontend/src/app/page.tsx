"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import Image from "next/image";
import { useAuth } from "@/context/AuthContext";
import { Navbar } from "@/components/layout/Navbar";
import { Spinner } from "@/components/ui/Spinner";
import { UpvoteButton } from "@/components/social/UpvoteButton";
import { AvatarGroup } from "@/components/social/AvatarGroup";
import { apiFetch } from "@/lib/api";
import { Persona, Conversation } from "@/types";

type Sort = "hot" | "top" | "new";

interface FeedData {
  personas: Persona[];
  conversations: Conversation[];
}

const SORT_TABS: { key: Sort; label: string }[] = [
  { key: "hot", label: "Hot" },
  { key: "top", label: "Top" },
  { key: "new", label: "New" },
];

function SortTabBar({ value, onChange }: { value: Sort; onChange: (s: Sort) => void }) {
  return (
    <div className="flex gap-1.5">
      {SORT_TABS.map((tab) => (
        <button
          key={tab.key}
          onClick={() => onChange(tab.key)}
          className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
            value === tab.key
              ? "bg-indigo-600 text-white"
              : "bg-white dark:bg-gray-800 text-gray-500 dark:text-gray-400 border border-gray-200 dark:border-gray-600 hover:border-indigo-300"
          }`}
        >
          {tab.label}
        </button>
      ))}
    </div>
  );
}

function PersonaFeedCard({ persona, loggedIn }: { persona: Persona; loggedIn: boolean }) {
  return (
    <Link href={`/p/${persona.unique_id}`} className="block group">
      <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden hover:border-indigo-300 hover:shadow-md transition-all">
        {/* Photo-first: square avatar at top */}
        <div className="relative w-full aspect-square bg-indigo-50 dark:bg-indigo-950">
          {persona.avatar_url ? (
            <Image
              src={persona.avatar_url}
              alt={persona.name}
              fill
              className="object-cover"
              unoptimized
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center">
              <span className="text-indigo-300 font-bold text-5xl">{persona.name.charAt(0)}</span>
            </div>
          )}
          {/* Gradient ring effect */}
          <div className="absolute inset-0 rounded-t-xl ring-inset ring-1 ring-black/5" />
        </div>

        {/* Info */}
        <div className="p-3">
          <h3 className="font-semibold text-gray-900 dark:text-white group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors truncate text-sm">
            {persona.name}
          </h3>
          {persona.motto && (
            <p className="text-xs text-gray-500 dark:text-gray-400 italic truncate mt-0.5">&ldquo;{persona.motto}&rdquo;</p>
          )}
          <div className="flex items-center justify-between mt-2">
            <span className="text-xs text-gray-400 dark:text-gray-500">{persona.view_count} views</span>
            <div onClick={(e) => e.preventDefault()}>
              <UpvoteButton
                targetType="persona"
                uniqueId={persona.unique_id}
                initialCount={persona.upvote_count}
                requiresAuth={!loggedIn}
              />
            </div>
          </div>
        </div>
      </div>
    </Link>
  );
}

function ConversationFeedCard({ conv, loggedIn }: { conv: Conversation; loggedIn: boolean }) {
  return (
    <Link href={`/c/${conv.unique_id}`} className="block group">
      <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-4 hover:border-indigo-300 hover:shadow-md transition-all">
        <h3 className="font-semibold text-gray-900 dark:text-white group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors line-clamp-2 text-sm">
          {conv.topic}
        </h3>
        {conv.participants && conv.participants.length > 0 && (
          <div className="mt-2">
            <AvatarGroup participants={conv.participants} size={24} />
          </div>
        )}
        <p className="text-xs text-gray-400 dark:text-gray-500 mt-2">{conv.turn_count} turns</p>
        <div className="flex items-center justify-between mt-2">
          <span className="text-xs text-gray-400 dark:text-gray-500">{conv.view_count} views</span>
          <div onClick={(e) => e.preventDefault()}>
            <UpvoteButton
              targetType="conversation"
              uniqueId={conv.unique_id}
              initialCount={conv.upvote_count}
              requiresAuth={!loggedIn}
            />
          </div>
        </div>
      </div>
    </Link>
  );
}

export default function Home() {
  const { user, isLoading: authLoading } = useAuth();
  const [personaSort, setPersonaSort] = useState<Sort>("hot");
  const [convSort, setConvSort] = useState<Sort>("hot");
  const [feed, setFeed] = useState<FeedData | null>(null);
  const [convFeed, setConvFeed] = useState<Conversation[]>([]);
  const [loading, setLoading] = useState(true);
  const [convLoading, setConvLoading] = useState(false);

  // Initial full feed load (hot sort)
  useEffect(() => {
    setLoading(true);
    fetch(`${process.env.NEXT_PUBLIC_API_URL}/discover?sort=${personaSort}`)
      .then((r) => r.json())
      .then((data: FeedData) => {
        setFeed(data);
        setConvFeed(data.conversations);
      })
      .catch(() => {
        setFeed({ personas: [], conversations: [] });
        setConvFeed([]);
      })
      .finally(() => setLoading(false));
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [personaSort]);

  // Separate reload when conversation sort changes (after initial load)
  useEffect(() => {
    if (loading) return;
    setConvLoading(true);
    fetch(`${process.env.NEXT_PUBLIC_API_URL}/discover?sort=${convSort}`)
      .then((r) => r.json())
      .then((data: FeedData) => setConvFeed(data.conversations))
      .catch(() => setConvFeed([]))
      .finally(() => setConvLoading(false));
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [convSort]);

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <Navbar />

      {/* Hero */}
      <div className="bg-gradient-to-br from-indigo-600 to-purple-700 text-white py-12 px-4 text-center">
        <div className="flex justify-center mb-4">
          <img src="/logo.svg" alt="PersonaComposer" className="w-16 h-16" />
        </div>
        <h1 className="text-4xl font-bold mb-3">PersonaComposer</h1>
        <p className="text-indigo-100 max-w-xl mx-auto mb-6">
          Build AI personas and run focus group simulations. Discover what others have created.
        </p>
        {!authLoading && !user && (
          <div className="flex gap-3 justify-center">
            <Link href="/login">
              <button className="px-6 py-2.5 bg-white text-indigo-700 font-semibold rounded-full hover:bg-indigo-50 transition-colors">
                Sign in with Google
              </button>
            </Link>
          </div>
        )}
        {!authLoading && user && (
          <div className="flex gap-3 justify-center">
            <Link href="/personas/new">
              <button className="px-5 py-2.5 bg-white text-indigo-700 font-semibold rounded-full hover:bg-indigo-50 transition-colors">
                + New Persona
              </button>
            </Link>
            <Link href="/conversations/new">
              <button className="px-5 py-2.5 bg-indigo-500 text-white font-semibold rounded-full hover:bg-indigo-400 transition-colors border border-white/30">
                + New Conversation
              </button>
            </Link>
          </div>
        )}
      </div>

      {/* Feed */}
      <div className="max-w-6xl mx-auto px-4 py-8">
        {loading ? (
          <div className="flex justify-center py-16"><Spinner size="lg" /></div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Personas column */}
            <div>
              <div className="flex items-center justify-between mb-4">
                <h2 className="font-bold text-gray-700 dark:text-gray-300 text-sm uppercase tracking-wide">Personas</h2>
                <SortTabBar value={personaSort} onChange={setPersonaSort} />
              </div>
              {feed?.personas.length === 0 ? (
                <p className="text-gray-400 text-sm py-8 text-center">No public personas yet.</p>
              ) : (
                <div className="grid grid-cols-2 gap-3">
                  {feed?.personas.map((p) => (
                    <PersonaFeedCard key={p.unique_id} persona={p} loggedIn={!!user} />
                  ))}
                </div>
              )}
            </div>

            {/* Conversations column */}
            <div>
              <div className="flex items-center justify-between mb-4">
                <h2 className="font-bold text-gray-700 dark:text-gray-300 text-sm uppercase tracking-wide">Conversations</h2>
                <SortTabBar value={convSort} onChange={setConvSort} />
              </div>
              {convLoading ? (
                <div className="flex justify-center py-8"><Spinner /></div>
              ) : convFeed.length === 0 ? (
                <p className="text-gray-400 text-sm py-8 text-center">No public conversations yet.</p>
              ) : (
                <div className="space-y-3">
                  {convFeed.map((c) => (
                    <ConversationFeedCard key={c.unique_id} conv={c} loggedIn={!!user} />
                  ))}
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
