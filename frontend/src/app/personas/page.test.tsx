import React from "react";
import { render, screen, waitFor, fireEvent } from "@testing-library/react";

// Mock auth guard — just render children
jest.mock("@/components/auth/AuthGuard", () => ({
  AuthGuard: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));

// Mock Navbar
jest.mock("@/components/layout/Navbar", () => ({
  Navbar: () => <nav data-testid="navbar" />,
}));

// Mock next/navigation
jest.mock("next/navigation", () => ({
  useRouter: () => ({ push: jest.fn(), back: jest.fn() }),
}));

// Mock apiFetch
const mockApiFetch = jest.fn();
jest.mock("@/lib/api", () => ({
  apiFetch: (...args: unknown[]) => mockApiFetch(...args),
}));

import PersonasPage from "./page";
import { Persona } from "@/types";

const mockPersona: Persona = {
  unique_id: "abc123",
  name: "Alice",
  age: 30,
  gender: "Female",
  description: "A thoughtful analyst",
  attitude: "Neutral",
  ocean_openness: 0.65,
  ocean_conscientiousness: 0.90,
  ocean_extraversion: 0.25,
  ocean_agreeableness: 0.35,
  ocean_neuroticism: 0.20,
  archetype_affinities: { ANALYST: 0.85 },
  motto: "Question everything.",
  avatar_url: null,
  created_at: "2026-01-01T00:00:00",
};

describe("PersonasPage", () => {
  beforeEach(() => {
    mockApiFetch.mockReset();
  });

  it("renders persona cards after loading", async () => {
    mockApiFetch.mockResolvedValueOnce([mockPersona]);
    render(<PersonasPage />);
    await waitFor(() => expect(screen.getByText("Alice")).toBeInTheDocument());
  });

  it("shows empty state when no personas", async () => {
    mockApiFetch.mockResolvedValueOnce([]);
    render(<PersonasPage />);
    await waitFor(() =>
      expect(screen.getByText(/no personas yet/i)).toBeInTheDocument()
    );
  });

  it("shows New Persona link", async () => {
    mockApiFetch.mockResolvedValueOnce([mockPersona]);
    render(<PersonasPage />);
    await waitFor(() => screen.getByText("Alice"));
    expect(screen.getByRole("link", { name: /new persona/i })).toBeInTheDocument();
  });

  it("shows error message on fetch failure", async () => {
    const { ApiError } = await import("@/types");
    mockApiFetch.mockRejectedValueOnce(new ApiError(500, "Server error"));
    render(<PersonasPage />);
    await waitFor(() =>
      expect(screen.getByRole("alert")).toBeInTheDocument()
    );
  });

  it("removes persona from list on successful delete", async () => {
    mockApiFetch
      .mockResolvedValueOnce([mockPersona]) // GET /personas
      .mockResolvedValueOnce(undefined);     // DELETE /personas/abc123
    window.confirm = jest.fn(() => true);

    render(<PersonasPage />);
    await waitFor(() => screen.getByText("Alice"));

    const deleteBtn = screen.getByRole("button", { name: /delete alice/i });
    fireEvent.click(deleteBtn);

    // Wait for the confirmation modal to appear, then click the confirm delete button
    await waitFor(() => screen.getByRole("button", { name: "Delete" }));
    const confirmDeleteBtn = screen.getByRole("button", { name: "Delete" });
    fireEvent.click(confirmDeleteBtn);

    await waitFor(() =>
      expect(screen.queryByText("Alice")).not.toBeInTheDocument()
    );
    expect(mockApiFetch).toHaveBeenCalledWith("/personas/abc123", { method: "DELETE" });
  });
});
