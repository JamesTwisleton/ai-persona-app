import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import { PersonaCard } from "./PersonaCard";
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
  archetype_affinities: { ANALYST: 0.85, SOCIALITE: 0.15 },
  motto: "Question everything.",
  avatar_url: "https://api.dicebear.com/7.x/personas/svg?seed=alice",
  is_public: true,
  view_count: 0,
  upvote_count: 0,
  created_at: "2026-01-01T00:00:00",
};

describe("PersonaCard", () => {
  it("renders persona name", () => {
    render(<PersonaCard persona={mockPersona} />);
    expect(screen.getByText("Alice")).toBeInTheDocument();
  });

  it("renders motto when provided", () => {
    render(<PersonaCard persona={mockPersona} />);
    expect(screen.getByText(/Question everything/)).toBeInTheDocument();
  });

  it("renders avatar image with correct src", () => {
    render(<PersonaCard persona={mockPersona} />);
    const img = screen.getByRole("img", { name: /alice/i });
    expect(img).toHaveAttribute(
      "src",
      expect.stringContaining("api.dicebear.com")
    );
  });

  it("renders initials when avatar_url is null", () => {
    render(<PersonaCard persona={{ ...mockPersona, avatar_url: null }} />);
    expect(screen.getByText("A")).toBeInTheDocument();
  });

  it("renders the highest-affinity archetype badge", () => {
    render(<PersonaCard persona={mockPersona} />);
    expect(screen.getByText(/analyst/i)).toBeInTheDocument();
  });

  it("renders age when provided", () => {
    render(<PersonaCard persona={mockPersona} />);
    expect(screen.getByText(/30/)).toBeInTheDocument();
  });

  it("renders attitude badge", () => {
    render(<PersonaCard persona={mockPersona} />);
    expect(screen.getByText("Neutral")).toBeInTheDocument();
  });

  it("links to the persona profile page", () => {
    render(<PersonaCard persona={mockPersona} />);
    const link = screen.getByRole("link");
    expect(link).toHaveAttribute("href", "/p/abc123");
  });

  it("does not show delete button when onDelete is not provided", () => {
    render(<PersonaCard persona={mockPersona} />);
    expect(screen.queryByRole("button", { name: /delete/i })).not.toBeInTheDocument();
  });

  it("renders delete button when onDelete is provided", () => {
    render(<PersonaCard persona={mockPersona} onDelete={jest.fn()} />);
    expect(screen.getByRole("button", { name: /delete alice/i })).toBeInTheDocument();
  });

  it("calls onDelete with persona unique_id when delete is confirmed", () => {
    const onDelete = jest.fn();
    window.confirm = jest.fn(() => true);
    render(<PersonaCard persona={mockPersona} onDelete={onDelete} />);
    fireEvent.click(screen.getByRole("button", { name: /delete alice/i }));
    fireEvent.click(screen.getByRole("button", { name: "Delete" }));
    expect(onDelete).toHaveBeenCalledWith("abc123");
  });

  it("does not call onDelete when delete is cancelled", () => {
    const onDelete = jest.fn();
    window.confirm = jest.fn(() => false);
    render(<PersonaCard persona={mockPersona} onDelete={onDelete} />);
    fireEvent.click(screen.getByRole("button", { name: /delete alice/i }));
    fireEvent.click(screen.getByRole("button", { name: "Cancel" }));
    expect(onDelete).not.toHaveBeenCalled();
  });
});
