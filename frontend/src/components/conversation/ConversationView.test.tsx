import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { ConversationView } from "./ConversationView";
import { Conversation, ConversationMessage } from "@/types";

const mockMessages: ConversationMessage[] = [
  {
    id: 1,
    persona_name: "Alice",
    message_text: "I think Mars colonization is a great idea.",
    turn_number: 1,
    moderation_status: "approved",
    toxicity_score: 0.01,
    created_at: "2026-01-01T00:00:00",
  },
  {
    id: 2,
    persona_name: "Bob",
    message_text: "I have some concerns about the cost.",
    turn_number: 1,
    moderation_status: "approved",
    toxicity_score: 0.02,
    created_at: "2026-01-01T00:00:01",
  },
];

const mockConversation: Conversation = {
  unique_id: "conv01",
  topic: "Should we colonize Mars?",
  turn_count: 1,
  max_turns: 20,
  is_complete: false,
  created_at: "2026-01-01T00:00:00",
  messages: mockMessages,
};

describe("ConversationView", () => {
  const mockOnContinue = jest.fn();

  beforeEach(() => {
    mockOnContinue.mockReset();
  });

  it("renders the conversation topic", () => {
    render(
      <ConversationView conversation={mockConversation} onContinue={mockOnContinue} />
    );
    expect(screen.getByText("Should we colonize Mars?")).toBeInTheDocument();
  });

  it("renders all messages", () => {
    render(
      <ConversationView conversation={mockConversation} onContinue={mockOnContinue} />
    );
    expect(
      screen.getByText("I think Mars colonization is a great idea.")
    ).toBeInTheDocument();
    expect(screen.getByText("I have some concerns about the cost.")).toBeInTheDocument();
  });

  it("shows turn counter", () => {
    render(
      <ConversationView conversation={mockConversation} onContinue={mockOnContinue} />
    );
    expect(screen.getByText(/1\s*\/\s*20/)).toBeInTheDocument();
  });

  it("Next Turn button is enabled when not complete", () => {
    render(
      <ConversationView conversation={mockConversation} onContinue={mockOnContinue} />
    );
    expect(
      screen.getByRole("button", { name: /next turn/i })
    ).not.toBeDisabled();
  });

  it("Next Turn button is disabled when conversation is complete", () => {
    render(
      <ConversationView
        conversation={{ ...mockConversation, is_complete: true }}
        onContinue={mockOnContinue}
      />
    );
    expect(screen.getByRole("button", { name: /next turn/i })).toBeDisabled();
  });

  it("calls onContinue when Next Turn is clicked", () => {
    render(
      <ConversationView conversation={mockConversation} onContinue={mockOnContinue} />
    );
    fireEvent.click(screen.getByRole("button", { name: /next turn/i }));
    expect(mockOnContinue).toHaveBeenCalledTimes(1);
  });

  it("shows empty state when no messages", () => {
    render(
      <ConversationView
        conversation={{ ...mockConversation, messages: [] }}
        onContinue={mockOnContinue}
      />
    );
    expect(screen.getByText(/no messages yet/i)).toBeInTheDocument();
  });

  it("shows completed badge when is_complete is true", () => {
    render(
      <ConversationView
        conversation={{ ...mockConversation, is_complete: true }}
        onContinue={mockOnContinue}
      />
    );
    expect(screen.getByText(/complete/i)).toBeInTheDocument();
  });

  it("shows make public button and opens modal when clicked", async () => {
    const mockOnUpdateVisibility = jest.fn();
    render(
      <ConversationView
        conversation={{ ...mockConversation, is_public: false }}
        onContinue={mockOnContinue}
        onSendMessage={jest.fn()}
        onUpdateVisibility={mockOnUpdateVisibility}
      />
    );

    // Check that button exists
    const makePublicBtn = screen.getByRole("button", { name: "Make Public" });
    expect(makePublicBtn).toBeInTheDocument();

    // Click button to open modal
    fireEvent.click(makePublicBtn);

    // Check modal contents
    expect(screen.getByText("Make Conversation Public?")).toBeInTheDocument();
    expect(screen.getByText(/Anyone will be able to view and fork it/i)).toBeInTheDocument();

    // Click confirm
    // Note: We might have two buttons with "Make Public" now (one on page, one in modal),
    // let's grab the one inside the modal by finding the one that is inside the dialog/modal div.
    // Or just use getAllByRole and click the second one.
    const buttons = screen.getAllByRole("button", { name: "Make Public" });
    fireEvent.click(buttons[1]);

    expect(mockOnUpdateVisibility).toHaveBeenCalledWith(true);
  });

  it("shows make private button and opens modal when clicked", async () => {
    const mockOnUpdateVisibility = jest.fn();
    render(
      <ConversationView
        conversation={{ ...mockConversation, is_public: true }}
        onContinue={mockOnContinue}
        onSendMessage={jest.fn()}
        onUpdateVisibility={mockOnUpdateVisibility}
      />
    );

    // Check that button exists
    const makePrivateBtn = screen.getByRole("button", { name: "Make Private" });
    expect(makePrivateBtn).toBeInTheDocument();

    // Click button to open modal
    fireEvent.click(makePrivateBtn);

    // Check modal contents
    expect(screen.getByText("Make Conversation Private?")).toBeInTheDocument();
    expect(screen.getByText(/Only you will be able to see it/i)).toBeInTheDocument();

    // Click confirm
    const buttons = screen.getAllByRole("button", { name: "Make Private" });
    fireEvent.click(buttons[1]);

    expect(mockOnUpdateVisibility).toHaveBeenCalledWith(false);
  });
});
