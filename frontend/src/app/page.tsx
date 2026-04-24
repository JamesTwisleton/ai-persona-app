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
import { LoginModal } from "@/components/auth/LoginModal";
import { apiFetch } from "@/lib/api";
import { Persona, Conversation, ApiError } from "@/types";

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
      <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 rounded-xl overflow-hidden hover:border-teal-300 transition-colors">
        <div className="p-5 pb-3">
          <div className="flex items-start gap-3">
            <div className="flex-shrink-0 w-12 h-12 relative">
              {persona.avatar_url ? (
                <Image
                  src={persona.avatar_url}
                  alt=""
                  fill
                  className="object-cover rounded-full"
                />
              ) : (
                <div className="w-full h-full rounded-full bg-gray-200 dark:bg-gray-700 flex items-center justify-center text-gray-400 font-bold text-lg">
                  {persona.name.charAt(0)}
                </div>
              )}
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between mb-1">
                <h3 className="font-bold text-gray-900 dark:text-white truncate">{persona.name}</h3>
                <span className="text-xs px-2 py-1 bg-teal-50 dark:bg-teal-900/50 text-teal-700 dark:text-teal-300 rounded-full border border-teal-100 dark:border-teal-800">
                  {persona.archetype}
                </span>
              </div>
              <p className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed line-clamp-3 mb-2">
                {persona.description}
              </p>
            </div>
          </div>
        </div>
        <div className="px-5 pb-3 flex items-center gap-4 text-xs text-gray-500">
          <span>{persona.view_count} views</span>
          <span>{persona.upvote_count} upvotes</span>
        </div>
        <div className="px-5 pb-3">
          <UpvoteButton
            type="persona"
            targetId={persona.unique_id}
            initialUpvoted={persona.user_has_upvoted || false}
            initialCount={persona.upvote_count}
            disabled={!loggedIn}
          />
        </div>
      </div>
    </Link>
  );
}

function ConversationFeedCard({ conversation, loggedIn }: { conversation: Conversation; loggedIn: boolean }) {
  return (
    <Link href={`/c/${conversation.unique_id}`} className="block group">
      <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 rounded-xl overflow-hidden hover:border-teal-300 transition-colors">
        <div className="p-5 pb-3">
          <div className="flex items-center gap-2 mb-2">
            <h3 className="font-bold text-gray-900 dark:text-white line-clamp-2 flex-1">{conversation.topic}</h3>
          </div>
          <p className="text-xs text-gray-500 mb-3">
            {conversation.message_count} messages
            {conversation.is_challenge && " • Challenge Mode"}
          </p>
          <AvatarGroup
            participants={conversation.participants}
            maxVisible={4}
          />
        </div>
        <div className="px-5 pb-3 flex items-center gap-4 text-xs text-gray-500">
          <span>{conversation.view_count} views</span>
          <span>{conversation.upvote_count} upvotes</span>
        </div>
        <div className="px-5 pb-3">
          <UpvoteButton
            type="conversation"
            targetId={conversation.unique_id}
            initialUpvoted={conversation.user_has_upvoted || false}
            initialCount={conversation.upvote_count}
            disabled={!loggedIn}
          />
        </div>
      </div>
    </Link>
  );
}

export default function HomePage() {
  const { user, loading: authLoading } = useAuth();
  const router = useRouter();
  const [feedData, setFeedData] = useState<FeedData | null>(null);
  const [feedLoading, setFeedLoading] = useState(true);
  const [feedError, setFeedError] = useState<string | null>(null);
  const [sort, setSort] = useState<Sort>("hot");
  const [challengeSubmitting, setChallengeSubmitting] = useState(false);
  const [loginModalOpen, setLoginModalOpen] = useState(false);

  const fetchFeed = async (sortBy: Sort) => {
    try {
      setFeedLoading(true);
      setFeedError(null);
      const data = await apiFetch<FeedData>(`/discover?sort=${sortBy}`);
      setFeedData(data);
    } catch (error) {
      setFeedError(error instanceof Error ? error.message : "Failed to load feed");
    } finally {
      setFeedLoading(false);
    }
  };

  useEffect(() => {
    fetchFeed(sort);
  }, [sort]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-teal-600 via-teal-700 to-rose-600">
      <Navbar />
      <main className="px-4 py-8">
        <div className="text-center mb-8 text-white">
          <div className="flex justify-center mb-4">
            <div className="w-20 h-20 relative">
              <Image
                src="/logo.svg"
                alt="PersonaComposer"
                fill
                className="object-contain filter brightness-0 invert"
              />
            </div>
          </div>
          <h1 className="text-4xl md:text-5xl font-bold mb-3">
            PersonaComposer
          </h1>
          <p className="text-teal-100 max-w-xl mx-auto mb-6">
            Build AI personas and run focus group simulations. Discover what others have created.
          </p>
          
          {!authLoading && (
            <div className="flex flex-col items-center gap-6 max-w-2xl mx-auto">
              <div className="flex gap-3 justify-center">
                {user ? (
                  <>
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
                  </>
                ) : (
                  <button
                    onClick={() => setLoginModalOpen(true)}
                    className="px-6 py-2.5 bg-white text-teal-700 font-semibold rounded-full hover:bg-teal-50 transition-colors shadow-lg"
                  >
                    Sign in with Google
                  </button>
                )}
              </div>

              <div className="w-full bg-white/10 backdrop-blur-md rounded-2xl p-6 border border-white/20">
                <h2 className="text-xl font-bold mb-4">Launch Challenge Mode</h2>
                <form
                  onSubmit={async (e) => {
                    e.preventDefault();
                    if (!user) {
                      setLoginModalOpen(true);
                      return;
                    }
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
                  <div className="flex flex-wrap gap-3 items-center">
                    <select
                      name="type"
                      disabled={challengeSubmitting}
                      className="flex-1 min-w-[140px] px-4 py-3 rounded-xl bg-white text-gray-900 focus:outline-none focus:ring-2 focus:ring-teal-300 disabled:opacity-60"
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
                        min="2"
                        max="8"
                        defaultValue="3"
                        disabled={challengeSubmitting}
                        className="w-12 text-center bg-transparent focus:outline-none"
                      />
                    </div>
                    <button
                      type="submit"
                      disabled={challengeSubmitting}
                      className="px-6 py-3 bg-rose-500 text-white font-bold rounded-xl hover:bg-rose-400 disabled:opacity-60 transition-colors flex items-center gap-2"
                    >
                      {challengeSubmitting && <Spinner size="sm" />}
                      {challengeSubmitting ? "Creating..." : "Challenge"}
                    </button>
                  </div>
                </form>
              </div>
            </div>
          )}
        </div>

        <div className="max-w-6xl mx-auto">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold text-white">Discover</h2>
            <SortTabBar value={sort} onChange={setSort} />
          </div>

          {feedLoading && (
            <div className="flex justify-center items-center py-12">
              <Spinner />
            </div>
          )}

          {feedError && (
            <div className="text-center py-12">
              <p className="text-red-300 mb-4">{feedError}</p>
              <button
                onClick={() => fetchFeed(sort)}
                className="px-4 py-2 bg-white text-teal-700 font-semibold rounded-lg hover:bg-teal-50 transition-colors"
              >
                Try again
              </button>
            </div>
          )}

          {feedData && !feedLoading && (
            <div className="space-y-8">
              {feedData.personas.length > 0 && (
                <div>
                  <h3 className="text-lg font-bold text-white mb-4">Personas</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {feedData.personas.map((persona) => (
                      <PersonaFeedCard
                        key={persona.unique_id}
                        persona={persona}
                        loggedIn={!!user}
                      />
                    ))}
                  </div>
                </div>
              )}

              {feedData.conversations.length > 0 && (
                <div>
                  <h3 className="text-lg font-bold text-white mb-4">Conversations</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {feedData.conversations.map((conversation) => (
                      <ConversationFeedCard
                        key={conversation.unique_id}
                        conversation={conversation}
                        loggedIn={!!user}
                      />
                    ))}
                  </div>
                </div>
              )}

              {feedData.personas.length === 0 && feedData.conversations.length === 0 && (
                <div className="text-center py-12">
                  <p className="text-teal-100 mb-4">No content found.</p>
                  {user && (
                    <div className="flex gap-3 justify-center">
                      <Link href="/personas/new">
                        <button className="px-5 py-2.5 bg-white text-teal-700 font-semibold rounded-full hover:bg-teal-50 transition-colors">
                          Create a Persona
                        </button>
                      </Link>
                      <Link href="/conversations/new">
                        <button className="px-5 py-2.5 bg-teal-500 text-white font-semibold rounded-full hover:bg-teal-400 transition-colors border border-white/30">
                          Start a Conversation
                        </button>
                      </Link>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      </main>

      <LoginModal
        isOpen={loginModalOpen}
        onClose={() => setLoginModalOpen(false)}
      />
    </div>
  );
}