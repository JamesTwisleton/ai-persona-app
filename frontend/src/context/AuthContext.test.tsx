import React from "react";
import { render, screen, waitFor, act } from "@testing-library/react";
import { AuthProvider, useAuth } from "./AuthContext";
import { setToken, clearToken } from "@/lib/auth";

// Minimal test component to expose context values
function TestConsumer() {
  const { user, isLoading, token } = useAuth();
  if (isLoading) return <div data-testid="loading">loading</div>;
  if (user) return <div data-testid="user">{user.email}</div>;
  return <div data-testid="no-user">no user</div>;
}

function mockFetchUser(email = "test@example.com") {
  global.fetch = jest.fn().mockResolvedValueOnce({
    ok: true,
    status: 200,
    json: () =>
      Promise.resolve({
        id: 1,
        email,
        name: "Test User",
        picture_url: null,
        is_admin: false,
        created_at: "2026-01-01T00:00:00",
      }),
  } as Response);
}

function mockFetch401() {
  global.fetch = jest.fn().mockResolvedValueOnce({
    ok: false,
    status: 401,
    json: () => Promise.resolve({ detail: "Not authenticated" }),
  } as Response);
}

describe("AuthProvider", () => {
  beforeEach(() => {
    clearToken();
    jest.restoreAllMocks();
  });

  it("shows no-user when no token stored", async () => {
    render(
      <AuthProvider>
        <TestConsumer />
      </AuthProvider>
    );
    await waitFor(() =>
      expect(screen.getByTestId("no-user")).toBeInTheDocument()
    );
  });

  it("validates stored token on mount and shows user", async () => {
    setToken("valid-jwt");
    mockFetchUser("me@example.com");

    render(
      <AuthProvider>
        <TestConsumer />
      </AuthProvider>
    );

    await waitFor(() =>
      expect(screen.getByTestId("user")).toHaveTextContent("me@example.com")
    );
  });

  it("clears token on 401 response", async () => {
    setToken("expired-jwt");
    mockFetch401();

    render(
      <AuthProvider>
        <TestConsumer />
      </AuthProvider>
    );

    await waitFor(() =>
      expect(screen.getByTestId("no-user")).toBeInTheDocument()
    );
    expect(localStorage.getItem("ai_focus_groups_token")).toBeNull();
  });
});

describe("useAuth login/logout", () => {
  beforeEach(() => {
    clearToken();
    jest.restoreAllMocks();
  });

  function LoginButton() {
    const { login, logout, user } = useAuth();
    return (
      <>
        {user ? (
          <button onClick={logout}>logout</button>
        ) : (
          <button
            onClick={() => login("new-token")}
          >
            login
          </button>
        )}
        <div data-testid="email">{user?.email ?? "none"}</div>
      </>
    );
  }

  it("login stores token and fetches user", async () => {
    // First mount: no token → no /users/me call
    global.fetch = jest.fn().mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: () => Promise.resolve({ id: 1, email: "new@example.com", name: "New", picture_url: null, is_admin: false, created_at: "" }),
    } as Response);

    const { getByRole, getByTestId } = render(
      <AuthProvider>
        <LoginButton />
      </AuthProvider>
    );

    // Wait for initial load
    await waitFor(() => getByRole("button", { name: "login" }));

    await act(async () => {
      getByRole("button", { name: "login" }).click();
    });

    await waitFor(() =>
      expect(getByTestId("email")).toHaveTextContent("new@example.com")
    );
  });

  it("logout clears user and token", async () => {
    setToken("valid-jwt");
    global.fetch = jest.fn().mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: () => Promise.resolve({ id: 1, email: "user@example.com", name: "U", picture_url: null, is_admin: false, created_at: "" }),
    } as Response);

    const { getByRole, getByTestId } = render(
      <AuthProvider>
        <LoginButton />
      </AuthProvider>
    );

    await waitFor(() => getByRole("button", { name: "logout" }));
    getByRole("button", { name: "logout" }).click();

    await waitFor(() =>
      expect(getByTestId("email")).toHaveTextContent("none")
    );
    expect(localStorage.getItem("ai_focus_groups_token")).toBeNull();
  });
});
