import React from "react";
import { render, screen } from "@testing-library/react";
import { MessageBubble } from "./MessageBubble";
import { ConversationMessage } from "@/types";

const mockMessage: ConversationMessage = {
  id: 1,
  persona_name: "Alice",
  message_text: "I think we should definitely colonize Mars.",
  turn_number: 1,
  moderation_status: "approved",
  toxicity_score: 0.02,
  created_at: "2026-01-01T00:00:00",
};

describe("MessageBubble", () => {
  it("renders persona name", () => {
    render(<MessageBubble message={mockMessage} />);
    expect(screen.getByText("Alice")).toBeInTheDocument();
  });

  it("renders message text", () => {
    render(<MessageBubble message={mockMessage} />);
    expect(
      screen.getByText("I think we should definitely colonize Mars.")
    ).toBeInTheDocument();
  });

  it("renders turn number", () => {
    render(<MessageBubble message={mockMessage} />);
    expect(screen.getByText(/turn 1/i)).toBeInTheDocument();
  });

  it("does not show toxicity warning for safe content", () => {
    render(<MessageBubble message={mockMessage} />);
    expect(screen.queryByText(/flagged/i)).not.toBeInTheDocument();
  });

  it("shows flagged badge when moderation_status is flagged", () => {
    render(
      <MessageBubble
        message={{ ...mockMessage, moderation_status: "flagged", toxicity_score: 0.9 }}
      />
    );
    expect(screen.getByText(/flagged/i)).toBeInTheDocument();
  });

  it("renders persona initial as avatar fallback", () => {
    render(<MessageBubble message={mockMessage} />);
    expect(screen.getByText("A")).toBeInTheDocument();
  });
});
