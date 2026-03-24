"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import Image from "next/image";
import { useAuth } from "@/context/AuthContext";
import { Navbar } from "@/components/layout/Navbar";
import { Spinner } from "@/components/ui/Spinner";
import { UpvoteButton } from "@/components/social/UpvoteButton";
import { apiFetch } from "@/lib/api";
import { Persona, Conversation } from "@/types";

type Sort = "hot" | "top" | "new";

interface FeedData {
  personas: Persona[];
  conversations: Conversation[];
}

function PersonaFeedCard({ persona, loggedIn }: { persona: Persona; loggedIn: boolean }) {
  return (
    <Link href={`/p/${persona.unique_id}`} className="block group">
      <div className="bg-white rounded-xl border border-gray-200 p-4 hover:border-indigo-300 hover:shadow-md transition-all">
        <div className="flex items-start gap-3">
          <div className="flex-shrink-0 w-10 h-10 rounded-full overflow-hidden bg-indigo-100 flex items-center justify-center">
            {persona.avatar_url ? (
              <Image src={persona.avatar_url} alt={persona.name} width={40} height={40} className="object-cover" unoptimized />
            ) : (
              <span className="text-indigo-600 font-bold">{persona.name.charAt(0)}</span>
            )}
          </div>
          <div className="flex-1 min-w-0">
            <h3 className="font-semibold text-gray-900 group-hover:text-indigo-600 transition-colors truncate">{persona.name}</h3>
            {persona.motto && (
              <p className="text-xs text-gray-500 italic truncate mt-0.5">&ldquo;{persona.motto}&rdquo;</p>
            )}
          </div>
        </div>
        <div className="flex items-center justify-between mt-3">
          <span className="text-xs text-gray-400">{persona.view_count} views</span>
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
    </Link>
  );
}

function ConversationFeedCard({ conv, loggedIn }: { conv: Conversation; loggedIn: boolean }) {
  return (
    <Link href={`/c/${conv.unique_id}`} className="block group">
      <div className="bg-white rounded-xl border border-gray-200 p-4 hover:border-indigo-300 hover:shadow-md transition-all">
        <h3 className="font-semibold text-gray-900 group-hover:text-indigo-600 transition-colors line-clamp-2 text-sm">
          {conv.topic}
        </h3>
        <p className="text-xs text-gray-400 mt-1">{conv.turn_count} turns</p>
        <div className="flex items-center justify-between mt-3">
          <span className="text-xs text-gray-400">{conv.view_count} views</span>
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
  const [sort, setSort] = useState<Sort>("hot");
  const [feed, setFeed] = useState<FeedData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    fetch(`${process.env.NEXT_PUBLIC_API_URL}/discover?sort=${sort}`)
      .then((r) => r.json())
      .then((data) => setFeed(data))
      .catch(() => setFeed({ personas: [], conversations: [] }))
      .finally(() => setLoading(false));
  }, [sort]);

  const sortTabs: { key: Sort; label: string }[] = [
    { key: "hot", label: "Hot" },
    { key: "top", label: "Top" },
    { key: "new", label: "New" },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />

      {/* Hero */}
      <div className="bg-gradient-to-br from-indigo-600 to-purple-700 text-white py-12 px-4 text-center">
        <h1 className="text-4xl font-bold mb-3">Persona Composer</h1>
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

      {/* Sort tabs */}
      <div className="max-w-6xl mx-auto px-4 py-6">
        <div className="flex gap-2 mb-6">
          {sortTabs.map((tab) => (
            <button
              key={tab.key}
              onClick={() => setSort(tab.key)}
              className={`px-4 py-1.5 rounded-full text-sm font-medium transition-colors ${
                sort === tab.key
                  ? "bg-indigo-600 text-white"
                  : "bg-white text-gray-600 border border-gray-200 hover:border-indigo-300"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {loading ? (
          <div className="flex justify-center py-16"><Spinner size="lg" /></div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Personas column */}
            <div>
              <div className="flex items-center justify-between mb-3">
                <h2 className="font-bold text-gray-700 text-sm uppercase tracking-wide">Personas</h2>
                {!authLoading && !user && (
                  <Link href="/login" className="text-xs text-indigo-600 hover:underline">Log in to create</Link>
                )}
              </div>
              {feed?.personas.length === 0 ? (
                <p className="text-gray-400 text-sm py-8 text-center">No public personas yet.</p>
              ) : (
                <div className="space-y-3">
                  {feed?.personas.map((p) => (
                    <PersonaFeedCard key={p.unique_id} persona={p} loggedIn={!!user} />
                  ))}
                </div>
              )}
            </div>

            {/* Conversations column */}
            <div>
              <div className="flex items-center justify-between mb-3">
                <h2 className="font-bold text-gray-700 text-sm uppercase tracking-wide">Conversations</h2>
                {!authLoading && !user && (
                  <Link href="/login" className="text-xs text-indigo-600 hover:underline">Log in to create</Link>
                )}
              </div>
              {feed?.conversations.length === 0 ? (
                <p className="text-gray-400 text-sm py-8 text-center">No public conversations yet.</p>
              ) : (
                <div className="space-y-3">
                  {feed?.conversations.map((c) => (
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
