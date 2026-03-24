"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import Image from "next/image";
import { AuthGuard } from "@/components/auth/AuthGuard";
import { Navbar } from "@/components/layout/Navbar";
import { Spinner } from "@/components/ui/Spinner";
import { ErrorMessage } from "@/components/ui/ErrorMessage";
import { ConfirmModal } from "@/components/ui/ConfirmModal";
import { apiFetch } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";
import { Persona, Conversation, ApiError } from "@/types";

interface AdminUser {
  id: number;
  name: string | null;
  email: string;
  avatar_url?: string | null;
  created_at: string;
  is_admin: boolean;
  is_superuser: boolean;
  persona_count: number;
}

interface PagedResponse<T> {
  total: number;
  page: number;
  page_size: number;
  items: T[];
}

type Tab = "users" | "personas" | "conversations";

// ============================================================================
// Users Tab
// ============================================================================

function UsersTab({ currentUserId }: { currentUserId: number }) {
  const [data, setData] = useState<AdminUser[]>([]);
  const [total, setTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setIsLoading(true);
    try {
      const res = await apiFetch<PagedResponse<AdminUser>>("/admin/users");
      setData(res.items);
      setTotal(res.total);
    } catch (err) {
      if (err instanceof ApiError) setError(err.message);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  const toggleSuperuser = async (userId: number, current: boolean) => {
    try {
      await apiFetch(`/admin/users/${userId}/superuser`, {
        method: "PATCH",
        body: JSON.stringify({ is_superuser: !current }),
      });
      await load();
    } catch (err) {
      if (err instanceof ApiError) setError(err.message);
    }
  };

  if (isLoading) return <div className="flex justify-center py-12"><Spinner size="lg" /></div>;
  if (error) return <ErrorMessage message={error} />;

  return (
    <div>
      <p className="text-sm text-gray-500 mb-4">{total} users</p>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left border-b border-gray-200">
              <th className="pb-2 pr-4 font-medium text-gray-600">User</th>
              <th className="pb-2 pr-4 font-medium text-gray-600">Email</th>
              <th className="pb-2 pr-4 font-medium text-gray-600">Personas</th>
              <th className="pb-2 pr-4 font-medium text-gray-600">Joined</th>
              <th className="pb-2 font-medium text-gray-600">Roles</th>
            </tr>
          </thead>
          <tbody>
            {data.map((u) => (
              <tr key={u.id} className="border-b border-gray-100 last:border-0">
                <td className="py-3 pr-4">
                  <div className="flex items-center gap-2">
                    <div className="w-8 h-8 rounded-full bg-indigo-100 overflow-hidden flex items-center justify-center flex-shrink-0">
                      {u.avatar_url ? (
                        <Image src={u.avatar_url} alt={u.name ?? u.email} width={32} height={32} className="object-cover" unoptimized />
                      ) : (
                        <span className="text-indigo-700 font-semibold text-xs">{(u.name ?? u.email).charAt(0).toUpperCase()}</span>
                      )}
                    </div>
                    <span className="font-medium text-gray-900">{u.name ?? "—"}</span>
                  </div>
                </td>
                <td className="py-3 pr-4 text-gray-600">{u.email}</td>
                <td className="py-3 pr-4 text-gray-600">{u.persona_count}</td>
                <td className="py-3 pr-4 text-gray-500">
                  {new Date(u.created_at).toLocaleDateString()}
                </td>
                <td className="py-3">
                  <div className="flex items-center gap-2 flex-wrap">
                    {u.is_admin && (
                      <span className="text-xs px-2 py-0.5 rounded-full bg-blue-100 text-blue-700 font-medium">admin</span>
                    )}
                    {u.is_superuser && (
                      <span className="text-xs px-2 py-0.5 rounded-full bg-purple-100 text-purple-700 font-medium">superuser</span>
                    )}
                    <button
                      onClick={() => toggleSuperuser(u.id, u.is_superuser)}
                      disabled={u.id === currentUserId && u.is_superuser}
                      className="text-xs px-2 py-0.5 rounded border border-gray-300 text-gray-600 hover:bg-gray-50 disabled:opacity-40 transition-colors"
                    >
                      {u.is_superuser ? "Remove superuser" : "Make superuser"}
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

// ============================================================================
// Personas Tab
// ============================================================================

interface AdminPersona extends Persona {
  owner_email?: string;
  owner_name?: string;
}

function PersonasTab() {
  const [data, setData] = useState<AdminPersona[]>([]);
  const [total, setTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [showConfirm, setShowConfirm] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [deleteProgress, setDeleteProgress] = useState("");
  const [repairStatus, setRepairStatus] = useState<string | null>(null);
  const [isRepairing, setIsRepairing] = useState(false);

  const load = useCallback(async () => {
    setIsLoading(true);
    try {
      const res = await apiFetch<PagedResponse<AdminPersona>>("/admin/personas");
      setData(res.items);
      setTotal(res.total);
    } catch (err) {
      if (err instanceof ApiError) setError(err.message);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  const toggleSelect = (id: string) => {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const handleBulkDelete = async () => {
    setIsDeleting(true);
    const ids = Array.from(selected);
    let deleted = 0;
    for (const id of ids) {
      try {
        await apiFetch(`/personas/${id}/force`, { method: "DELETE" });
        deleted++;
        setDeleteProgress(`${deleted} / ${ids.length} deleted`);
        setData((prev) => prev.filter((p) => p.unique_id !== id));
        setSelected((prev) => { const next = new Set(prev); next.delete(id); return next; });
      } catch {
        // continue
      }
    }
    setIsDeleting(false);
    setShowConfirm(false);
    setDeleteProgress("");
    setTotal((t) => t - deleted);
  };

  if (isLoading) return <div className="flex justify-center py-12"><Spinner size="lg" /></div>;
  if (error) return <ErrorMessage message={error} />;

  return (
    <div>
      <div className="flex items-center justify-between mb-4 flex-wrap gap-2">
        <p className="text-sm text-gray-500">{total} personas</p>
        <div className="flex items-center gap-2 flex-wrap">
          {/* Repair avatars */}
          <button
            onClick={async () => {
              setIsRepairing(true);
              setRepairStatus(null);
              try {
                const res = await apiFetch<{ repaired: number; failed: number; remaining: number; message: string }>(
                  "/admin/repair-avatars?limit=10",
                  { method: "POST" }
                );
                setRepairStatus(res.message);
                if (res.repaired > 0) load();
              } catch (e) {
                setRepairStatus("Repair failed — check logs.");
              } finally {
                setIsRepairing(false);
              }
            }}
            disabled={isRepairing}
            className="px-3 py-1.5 text-sm font-medium text-indigo-700 bg-indigo-50 border border-indigo-200 rounded-lg hover:bg-indigo-100 disabled:opacity-40 transition-colors"
          >
            {isRepairing ? "Repairing…" : "Repair avatars"}
          </button>

          <button
            onClick={() => setSelected(selected.size === data.length ? new Set() : new Set(data.map((p) => p.unique_id)))}
            className="text-sm text-gray-500 hover:text-gray-700"
          >
            {selected.size === data.length ? "Deselect all" : "Select all"}
          </button>
          {selected.size > 0 && (
            <button
              onClick={() => setShowConfirm(true)}
              className="px-3 py-1.5 text-sm font-medium text-white bg-red-600 rounded-lg hover:bg-red-700"
            >
              Delete ({selected.size})
            </button>
          )}
        </div>
      </div>

      {repairStatus && (
        <p className={`text-sm mb-3 px-3 py-2 rounded-lg ${
          repairStatus.includes("failed") || repairStatus.includes("Failed")
            ? "bg-red-50 text-red-700"
            : "bg-green-50 text-green-700"
        }`}>
          {repairStatus}
          {repairStatus.includes("pending") && (
            <button
              onClick={() => setRepairStatus(null)}
              className="ml-2 underline"
            >
              Run again
            </button>
          )}
        </p>
      )}

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left border-b border-gray-200">
              <th className="pb-2 w-8" />
              <th className="pb-2 pr-4 font-medium text-gray-600">Persona</th>
              <th className="pb-2 pr-4 font-medium text-gray-600">Owner</th>
              <th className="pb-2 pr-4 font-medium text-gray-600">Views</th>
              <th className="pb-2 pr-4 font-medium text-gray-600">Upvotes</th>
              <th className="pb-2 font-medium text-gray-600">Created</th>
            </tr>
          </thead>
          <tbody>
            {data.map((p) => (
              <tr key={p.unique_id} className="border-b border-gray-100 last:border-0">
                <td className="py-2 pr-2">
                  <input
                    type="checkbox"
                    checked={selected.has(p.unique_id)}
                    onChange={() => toggleSelect(p.unique_id)}
                    className="rounded text-indigo-600"
                  />
                </td>
                <td className="py-2 pr-4">
                  <div className="flex items-center gap-2">
                    <div className="w-7 h-7 rounded-full bg-indigo-100 overflow-hidden flex items-center justify-center flex-shrink-0">
                      {p.avatar_url ? (
                        <Image src={p.avatar_url} alt={p.name} width={28} height={28} className="object-cover" unoptimized />
                      ) : (
                        <span className="text-indigo-700 font-semibold text-xs">{p.name.charAt(0)}</span>
                      )}
                    </div>
                    <span className="font-medium text-gray-900">{p.name}</span>
                    {!p.is_public && <span className="text-xs text-gray-400">(private)</span>}
                  </div>
                </td>
                <td className="py-2 pr-4 text-gray-500">{p.owner_email ?? "—"}</td>
                <td className="py-2 pr-4 text-gray-600">{p.view_count}</td>
                <td className="py-2 pr-4 text-gray-600">{p.upvote_count}</td>
                <td className="py-2 text-gray-500">{new Date(p.created_at!).toLocaleDateString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {showConfirm && (
        <ConfirmModal
          title={`Force-delete ${selected.size} persona${selected.size !== 1 ? "s" : ""}?`}
          message={deleteProgress || "This will permanently delete the selected personas regardless of owner. This cannot be undone."}
          confirmLabel={`Delete ${selected.size}`}
          onConfirm={handleBulkDelete}
          onCancel={() => setShowConfirm(false)}
          isLoading={isDeleting}
        />
      )}
    </div>
  );
}

// ============================================================================
// Conversations Tab
// ============================================================================

interface AdminConversation extends Conversation {
  owner_email?: string;
  owner_name?: string;
}

function ConversationsTab() {
  const [data, setData] = useState<AdminConversation[]>([]);
  const [total, setTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [showConfirm, setShowConfirm] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [deleteProgress, setDeleteProgress] = useState("");

  const load = useCallback(async () => {
    setIsLoading(true);
    try {
      const res = await apiFetch<PagedResponse<AdminConversation>>("/admin/conversations");
      setData(res.items);
      setTotal(res.total);
    } catch (err) {
      if (err instanceof ApiError) setError(err.message);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  const toggleSelect = (id: string) => {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const handleBulkDelete = async () => {
    setIsDeleting(true);
    const ids = Array.from(selected);
    let deleted = 0;
    for (const id of ids) {
      try {
        await apiFetch(`/conversations/${id}/force`, { method: "DELETE" });
        deleted++;
        setDeleteProgress(`${deleted} / ${ids.length} deleted`);
        setData((prev) => prev.filter((c) => c.unique_id !== id));
        setSelected((prev) => { const next = new Set(prev); next.delete(id); return next; });
      } catch {
        // continue
      }
    }
    setIsDeleting(false);
    setShowConfirm(false);
    setDeleteProgress("");
    setTotal((t) => t - deleted);
  };

  if (isLoading) return <div className="flex justify-center py-12"><Spinner size="lg" /></div>;
  if (error) return <ErrorMessage message={error} />;

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <p className="text-sm text-gray-500">{total} conversations</p>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setSelected(selected.size === data.length ? new Set() : new Set(data.map((c) => c.unique_id)))}
            className="text-sm text-gray-500 hover:text-gray-700"
          >
            {selected.size === data.length ? "Deselect all" : "Select all"}
          </button>
          {selected.size > 0 && (
            <button
              onClick={() => setShowConfirm(true)}
              className="px-3 py-1.5 text-sm font-medium text-white bg-red-600 rounded-lg hover:bg-red-700"
            >
              Delete ({selected.size})
            </button>
          )}
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left border-b border-gray-200">
              <th className="pb-2 w-8" />
              <th className="pb-2 pr-4 font-medium text-gray-600">Topic</th>
              <th className="pb-2 pr-4 font-medium text-gray-600">Owner</th>
              <th className="pb-2 pr-4 font-medium text-gray-600">Turns</th>
              <th className="pb-2 pr-4 font-medium text-gray-600">Status</th>
              <th className="pb-2 font-medium text-gray-600">Created</th>
            </tr>
          </thead>
          <tbody>
            {data.map((c) => (
              <tr key={c.unique_id} className="border-b border-gray-100 last:border-0">
                <td className="py-2 pr-2">
                  <input
                    type="checkbox"
                    checked={selected.has(c.unique_id)}
                    onChange={() => toggleSelect(c.unique_id)}
                    className="rounded text-indigo-600"
                  />
                </td>
                <td className="py-2 pr-4">
                  <span className="font-medium text-gray-900 line-clamp-1">{c.topic}</span>
                  {!c.is_public && <span className="ml-1 text-xs text-gray-400">(private)</span>}
                </td>
                <td className="py-2 pr-4 text-gray-500">{c.owner_email ?? "—"}</td>
                <td className="py-2 pr-4 text-gray-600">{c.turn_count} / {c.max_turns}</td>
                <td className="py-2 pr-4">
                  {c.is_complete ? (
                    <span className="text-xs px-1.5 py-0.5 rounded-full bg-green-100 text-green-700">Complete</span>
                  ) : (
                    <span className="text-xs px-1.5 py-0.5 rounded-full bg-indigo-50 text-indigo-700">Active</span>
                  )}
                </td>
                <td className="py-2 text-gray-500">{new Date(c.created_at!).toLocaleDateString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {showConfirm && (
        <ConfirmModal
          title={`Force-delete ${selected.size} conversation${selected.size !== 1 ? "s" : ""}?`}
          message={deleteProgress || "This will permanently delete the selected conversations regardless of owner. This cannot be undone."}
          confirmLabel={`Delete ${selected.size}`}
          onConfirm={handleBulkDelete}
          onCancel={() => setShowConfirm(false)}
          isLoading={isDeleting}
        />
      )}
    </div>
  );
}

// ============================================================================
// Admin Page
// ============================================================================

function AdminContent() {
  const { user } = useAuth();
  const router = useRouter();
  const [tab, setTab] = useState<Tab>("users");

  useEffect(() => {
    if (user && !user.is_superuser) {
      router.replace("/");
    }
  }, [user, router]);

  if (!user?.is_superuser) {
    return (
      <div className="flex justify-center py-16">
        <Spinner size="lg" />
      </div>
    );
  }

  const tabs: { id: Tab; label: string }[] = [
    { id: "users", label: "Users" },
    { id: "personas", label: "Personas" },
    { id: "conversations", label: "Conversations" },
  ];

  return (
    <>
      <Navbar />
      <main className="max-w-5xl mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold text-gray-900 mb-6">Admin Panel</h1>

        {/* Tab bar */}
        <div className="flex border-b border-gray-200 mb-6">
          {tabs.map(({ id, label }) => (
            <button
              key={id}
              onClick={() => setTab(id)}
              className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors -mb-px ${
                tab === id
                  ? "border-indigo-600 text-indigo-600"
                  : "border-transparent text-gray-500 hover:text-gray-700"
              }`}
            >
              {label}
            </button>
          ))}
        </div>

        <div className="bg-white rounded-xl border border-gray-200 p-6">
          {tab === "users" && <UsersTab currentUserId={user.id} />}
          {tab === "personas" && <PersonasTab />}
          {tab === "conversations" && <ConversationsTab />}
        </div>
      </main>
    </>
  );
}

export default function AdminPage() {
  return (
    <AuthGuard>
      <AdminContent />
    </AuthGuard>
  );
}
