import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { UpvoteButton } from "../UpvoteButton";
import { apiFetch } from "@/lib/api";

// Mock apiFetch
jest.mock("@/lib/api", () => ({
  apiFetch: jest.fn(),
}));

describe("UpvoteButton", () => {
  const defaultProps = {
    targetType: "persona" as const,
    uniqueId: "abc123",
    initialCount: 5,
    initialUpvoted: false,
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("renders the initial count", () => {
    render(<UpvoteButton {...defaultProps} />);
    expect(screen.getByText("5")).toBeInTheDocument();
  });

  it("toggles upvote on click and updates count", async () => {
    (apiFetch as jest.Mock).mockResolvedValueOnce({
      upvoted: true,
      upvote_count: 6,
    });

    render(<UpvoteButton {...defaultProps} />);
    const button = screen.getByRole("button");

    fireEvent.click(button);

    await waitFor(() => {
      expect(screen.getByText("6")).toBeInTheDocument();
    });

    expect(apiFetch).toHaveBeenCalledWith("/p/abc123/upvote", { method: "POST" });
  });

  it("toggles off upvote on second click", async () => {
    (apiFetch as jest.Mock).mockResolvedValueOnce({
      upvoted: false,
      upvote_count: 4,
    });

    render(<UpvoteButton {...defaultProps} initialUpvoted={true} initialCount={5} />);
    const button = screen.getByRole("button");

    fireEvent.click(button);

    await waitFor(() => {
      expect(screen.getByText("4")).toBeInTheDocument();
    });
  });

  it("disables button while loading", async () => {
    let resolveApi: (value: any) => void;
    const apiPromise = new Promise((resolve) => {
      resolveApi = resolve;
    });
    (apiFetch as jest.Mock).mockReturnValue(apiPromise);

    render(<UpvoteButton {...defaultProps} />);
    const button = screen.getByRole("button");

    fireEvent.click(button);

    expect(button).toBeDisabled();

    // @ts-ignore
    resolveApi({ upvoted: true, upvote_count: 6 });

    await waitFor(() => {
      expect(button).not.toBeDisabled();
    });
  });
});
