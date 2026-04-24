import { apiFetch } from "./api";
import { ApiError } from "@/types";
import { setToken, clearToken } from "./auth";

// Minimal fetch mock — we don't use MSW here to keep this unit test pure
function mockFetch(status: number, body: unknown, ok = status >= 200 && status < 300) {
  global.fetch = jest.fn().mockResolvedValueOnce({
    ok,
    status,
    json: () => Promise.resolve(body),
  } as Response);
}

describe("apiFetch", () => {
  beforeEach(() => {
    clearToken();
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  it("makes a GET request to the correct URL", async () => {
    mockFetch(200, { status: "healthy" });
    await apiFetch("/health");
    expect(fetch).toHaveBeenCalledWith(
      expect.stringContaining("/health"),
      expect.objectContaining({ headers: expect.objectContaining({}) })
    );
  });

  it("attaches Bearer token header when token is stored", async () => {
    setToken("my-jwt-token");
    mockFetch(200, []);
    await apiFetch("/personas");
    const headers = (fetch as jest.Mock).mock.calls[0][1].headers;
    expect(headers["Authorization"]).toBe("Bearer my-jwt-token");
  });

  it("does not attach Authorization header when no token", async () => {
    mockFetch(200, []);
    await apiFetch("/personas");
    const headers = (fetch as jest.Mock).mock.calls[0][1].headers;
    expect(headers["Authorization"]).toBeUndefined();
  });

  it("returns parsed JSON on 200", async () => {
    mockFetch(200, { name: "Alice" });
    const result = await apiFetch("/personas/abc");
    expect(result).toEqual({ name: "Alice" });
  });

  it("throws ApiError with status 401 on unauthorized", async () => {
    mockFetch(401, { detail: "Not authenticated" }, false);
    const error = await apiFetch("/personas").catch((e) => e);
    expect(error).toBeInstanceOf(ApiError);
    if (error instanceof ApiError) {
      expect(error.status).toBe(401);
    }
  });

  it("throws ApiError with status 404 on not found", async () => {
    mockFetch(404, { detail: "Not found" }, false);
    await expect(apiFetch("/personas/bad-id")).rejects.toMatchObject({ status: 404 });
  });

  it("includes the detail message in the ApiError", async () => {
    mockFetch(400, { detail: "Content failed moderation" }, false);
    await expect(apiFetch("/personas")).rejects.toMatchObject({
      message: "Content failed moderation",
    });
  });

  it("returns undefined for 204 No Content", async () => {
    global.fetch = jest.fn().mockResolvedValueOnce({
      ok: true,
      status: 204,
      json: () => Promise.reject(new Error("No body")),
    } as unknown as Response);
    const result = await apiFetch("/personas/abc");
    expect(result).toBeUndefined();
  });
});
