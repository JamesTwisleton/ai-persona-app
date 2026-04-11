"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import Image from "next/image";
import { useRouter } from "next/navigation";
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
              ? "bg-teal-600 text-white"
              : "bg-white dark:bg-gray-800 text-gray-500 dark:text-gray-400 border border-gray-200 dark:border-gray-600 hover:border-teal-300"
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
      <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden hover:border-teal-300 hover:shadow-md transition-all">
        <div className="relative w-full aspect-square bg-teal-50 dark:bg-teal-950">
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
              <span className="text-teal-300 font-bold text-5xl">{persona.name.charAt(0)}</span>
            </div>
          )}
          <div className="absolute inset-0 rounded-t-xl ring-inset ring-1 ring-black/5" />
        </div>

        <div className="p-3">
          <h3 className="font-semibold text-gray-900 dark:text-white group-hover:text-teal-600 dark:group-hover:text-teal-400 transition-colors truncate text-sm">
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
      <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-4 hover:border-teal-300 hover:shadow-md transition-all">
        <h3 className="font-semibold text-gray-900 dark:text-white group-hover:text-teal-600 dark:group-hover:text-teal-400 transition-colors line-clamp-2 text-sm">
          {conv.topic}
        </h3>
        {conv.participants && conv.participants.length > 0 && (
          <div className="mt-2">
            <AvatarGroup participants={conv.participants} size={40} />
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
  const router = useRouter();
  const [personaSort, setPersonaSort] = useState<Sort>("hot");
  const [convSort, setConvSort] = useState<Sort>("hot");
  const [feed, setFeed] = useState<FeedData | null>(null);
  const [convFeed, setConvFeed] = useState<Conversation[]>([]);
  const [loading, setLoading] = useState(true);
  const [convLoading, setConvLoading] = useState(false);
  const [challengeSubmitting, setChallengeSubmitting] = useState(false);

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
  }, [personaSort]);

  useEffect(() => {
    if (loading) return;
    setConvLoading(true);
    fetch(`${process.env.NEXT_PUBLIC_API_URL}/discover?sort=${convSort}`)
      .then((r) => r.json())
      .then((data: FeedData) => setConvFeed(data.conversations))
      .catch(() => setConvFeed([]))
      .finally(() => setConvLoading(false));
  }, [convSort, loading]);

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <Navbar />

      <div className="bg-gradient-to-br from-teal-600 to-rose-700 text-white py-12 px-4 text-center">
        <div className="flex justify-center mb-4">
          <div className="bg-white/90 rounded-xl p-2 inline-block">
            <img src="/logo.jpeg" alt="PersonaComposer" className="w-16 h-16 block" />
          </div>
        </div>
        <h1 className="text-4xl font-bold mb-3">PersonaComposer</h1>
        <p className="text-teal-100 max-w-xl mx-auto mb-6">
          Build AI personas and run focus group simulations. Discover what others have created.
        </p>
        {!authLoading && !user && (
          <div className="flex gap-3 justify-center">
            <Link href="/login">
              <button className="px-6 py-2.5 bg-white text-teal-700 font-semibold rounded-full hover:bg-teal-50 transition-colors">
                Sign in with Google
              </button>
            </Link>
          </div>
        )}
        {!authLoading && user && (
          <div className="flex flex-col items-center gap-6 max-w-2xl mx-auto">
            <div className="flex gap-3 justify-center">
              <Link href="/personas/new">
                <button className="px-5 py-2.5 bg-white text-teal-700 font-semibold rounded-full hover:bg-teal-50 transition-colors">
                  + New Persona
                </button>
              </Link>
              <Link href="/conversations/new">
                <button className="px-5 py-2.5 bg-teal-500 text-white font-semibold rounded-full hover:bg-teal-400 transition-colors border border-white/30">
                  + New Conversation
                </button>
              </Link>
            </div>

            <div className="w-full bg-white/10 backdrop-blur-md rounded-2xl p-6 border border-white/20">
              <h2 className="text-xl font-bold mb-4">Launch Challenge Mode</h2>
              <form
                onSubmit={async (e) => {
                  e.preventDefault();
                  const form = e.target as HTMLFormElement;
                  const proposal = (form.elements.namedItem("proposal") as HTMLInputElement).value;
                  const challengeType = (form.elements.namedItem("type") as HTMLSelectElement).value;
                  const nPersonas = parseInt((form.elements.namedItem("n_personas") as HTMLInputElement).value) || 3;

                  setChallengeSubmitting(true);
                  try {
                    const res = await apiFetch<Conversation>("/conversations/challenge", {
                      method: "POST",
                      body: JSON.stringify({ proposal, challenge_type: challengeType, n_personas: nPersonas }),
                    });
                    router.push(`/conversations/${res.unique_id}`);
                  } catch (err) {
                    setChallengeSubmitting(false);
                    alert("Failed to start challenge. Please try again.");
                  }
                }}
                className="flex flex-col gap-3"
              >
                <input
                  name="proposal"
                  placeholder="Enter a proposal to be challenged (e.g. 'Cycle lanes should be everywhere')"
                  required
                  disabled={challengeSubmitting}
                  className="px-4 py-3 rounded-xl bg-white text-gray-900 focus:outline-none focus:ring-2 focus:ring-teal-300 disabled:opacity-60"
                />
                <div className="flex gap-3 items-center">
                  <select
                    name="type"
                    disabled={challengeSubmitting}
                    className="flex-1 px-4 py-3 rounded-xl bg-white text-gray-900 focus:outline-none focus:ring-2 focus:ring-teal-300 disabled:opacity-60"
                  >
                    <option>Public Debate</option>
                    <option>Interview</option>
                    <option>Court of Law</option>
                    <option>Presentation</option>
                  </select>
                  <div className="flex items-center gap-2 bg-white px-3 py-2 rounded-xl text-gray-900">
                    <label className="text-xs font-bold text-gray-500 uppercase">Personas:</label>
                    <input
                      name="n_personas"
                      type="number"
                      min="1"
                      max="8"
                      defaultValue="3"
                      disabled={challengeSubmitting}
                      className="w-12 focus:outline-none font-bold disabled:opacity-60"
                    />
                  </div>
                  <button
                    type="submit"
                    disabled={challengeSubmitting}
                    className="flex items-center gap-2 px-6 py-3 bg-teal-600 hover:bg-teal-500 disabled:opacity-70 text-white font-bold rounded-xl transition-colors shadow-lg"
                  >
                    {challengeSubmitting && <Spinner size="sm" />}
                    {challengeSubmitting ? "Starting..." : "Start Challenge"}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>

      <div className="max-w-6xl mx-auto px-4 py-8">
        {loading ? (
          <div className="flex justify-center py-16"><Spinner size="lg" /></div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
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
