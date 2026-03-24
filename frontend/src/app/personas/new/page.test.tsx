import React from "react";
import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

jest.mock("@/components/auth/AuthGuard", () => ({
  AuthGuard: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));
jest.mock("@/components/layout/Navbar", () => ({
  Navbar: () => <nav data-testid="navbar" />,
}));

const mockPush = jest.fn();
const mockBack = jest.fn();
jest.mock("next/navigation", () => ({
  useRouter: () => ({ push: mockPush, back: mockBack }),
}));

const mockApiFetch = jest.fn();
jest.mock("@/lib/api", () => ({
  apiFetch: (...args: unknown[]) => mockApiFetch(...args),
}));

import NewPersonaPage from "./page";
import { Persona } from "@/types";

const mockCreatedPersona: Persona = {
  unique_id: "new123",
  name: "Bob",
  age: null,
  gender: null,
  description: null,
  attitude: "Neutral",
  ocean_openness: 0.5,
  ocean_conscientiousness: 0.5,
  ocean_extraversion: 0.5,
  ocean_agreeableness: 0.5,
  ocean_neuroticism: 0.5,
  archetype_affinities: {},
  motto: null,
  avatar_url: null,
  created_at: "2026-01-01T00:00:00",
};

describe("NewPersonaPage", () => {
  beforeEach(() => {
    mockApiFetch.mockReset();
    mockPush.mockReset();
  });

  it("renders the creation form with required fields", () => {
    render(<NewPersonaPage />);
    expect(screen.getByLabelText(/name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/description/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/attitude/i)).toBeInTheDocument();
  });

  it("submits form and redirects to /personas on success", async () => {
    mockApiFetch.mockResolvedValueOnce(mockCreatedPersona);
    const user = userEvent.setup();
    render(<NewPersonaPage />);

    await user.type(screen.getByLabelText(/name \*/i), "Bob");
    await user.click(screen.getByRole("button", { name: /create persona/i }));

    await waitFor(() => expect(mockPush).toHaveBeenCalledWith("/personas"));
  });

  it("shows error message on moderation failure (400)", async () => {
    const { ApiError } = await import("@/types");
    mockApiFetch.mockRejectedValueOnce(
      new ApiError(400, "Content failed moderation", "Content failed moderation")
    );
    const user = userEvent.setup();
    render(<NewPersonaPage />);

    await user.type(screen.getByLabelText(/name \*/i), "BadActor");
    await user.click(screen.getByRole("button", { name: /create persona/i }));

    await waitFor(() =>
      expect(screen.getByRole("alert")).toBeInTheDocument()
    );
    expect(screen.getByText(/content failed moderation/i)).toBeInTheDocument();
  });

  it("Cancel button calls router.back()", () => {
    render(<NewPersonaPage />);
    fireEvent.click(screen.getByRole("button", { name: /cancel/i }));
    expect(mockBack).toHaveBeenCalled();
  });
});
