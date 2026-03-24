import { getToken, setToken, clearToken } from "./auth";

describe("auth utilities", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it("getToken returns null when no token is stored", () => {
    expect(getToken()).toBeNull();
  });

  it("setToken stores token in localStorage", () => {
    setToken("test-jwt-token");
    expect(localStorage.getItem("ai_focus_groups_token")).toBe("test-jwt-token");
  });

  it("getToken retrieves a stored token", () => {
    setToken("my-token-123");
    expect(getToken()).toBe("my-token-123");
  });

  it("clearToken removes the stored token", () => {
    setToken("my-token-123");
    clearToken();
    expect(getToken()).toBeNull();
  });
});
