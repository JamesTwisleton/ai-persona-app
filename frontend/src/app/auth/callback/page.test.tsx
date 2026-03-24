import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import AuthCallbackPage from "./page";

// Mock next/navigation
const mockReplace = jest.fn();
let mockToken: string | null = "test-jwt-token";

jest.mock("next/navigation", () => ({
  useRouter: () => ({ replace: mockReplace }),
  useSearchParams: () => ({
    get: (key: string) => (key === "token" ? mockToken : null),
  }),
}));

// Mock AuthContext
const mockLogin = jest.fn();
jest.mock("@/context/AuthContext", () => ({
  useAuth: () => ({ login: mockLogin }),
}));

describe("AuthCallbackPage", () => {
  beforeEach(() => {
    mockToken = "test-jwt-token";
    mockLogin.mockReset();
    mockReplace.mockReset();
  });

  it("shows spinner while processing", () => {
    mockLogin.mockImplementation(() => new Promise(() => {})); // never resolves
    render(<AuthCallbackPage />);
    expect(screen.getByRole("status")).toBeInTheDocument();
  });

  it("calls login with token from query param and redirects to /personas", async () => {
    mockLogin.mockResolvedValueOnce(undefined);
    render(<AuthCallbackPage />);
    await waitFor(() => expect(mockLogin).toHaveBeenCalledWith("test-jwt-token"));
    await waitFor(() => expect(mockReplace).toHaveBeenCalledWith("/personas"));
  });

  it("shows error when no token in query params", async () => {
    mockToken = null;
    render(<AuthCallbackPage />);
    await waitFor(() =>
      expect(screen.getByRole("alert")).toBeInTheDocument()
    );
    expect(screen.getByText(/no token received/i)).toBeInTheDocument();
  });

  it("shows error when login fails", async () => {
    mockLogin.mockImplementation(() => Promise.reject(new Error("Auth failed")));
    render(<AuthCallbackPage />);
    await waitFor(() =>
      expect(screen.getByRole("alert")).toBeInTheDocument()
    );
    expect(screen.getByText(/failed to authenticate/i)).toBeInTheDocument();
  });

  it("shows back to login link on error", async () => {
    mockToken = null;
    render(<AuthCallbackPage />);
    await waitFor(() =>
      expect(screen.getByRole("link", { name: /back to login/i })).toBeInTheDocument()
    );
  });
});
