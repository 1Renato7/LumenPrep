import { createLumenApiClient, type LumenApiClient } from "./client-interface";

export type LumenApiSource = "LIVE_API" | "MOCK_FIXTURE";

export interface LumenClientState {
  api: LumenApiClient | null;
  error: string | null;
  source: LumenApiSource;
}

let liveClient: LumenApiClient | null = null;

/** Resolve the only browser client entry point. Tests may inject an explicit mock. */
export function resolveLumenClient(supplied?: LumenApiClient): LumenClientState {
  if (supplied) {
    return {
      api: supplied,
      error: null,
      source: isMockClient(supplied) ? "MOCK_FIXTURE" : "LIVE_API",
    };
  }
  try {
    liveClient ??= createLumenApiClient();
    return { api: liveClient, error: null, source: "LIVE_API" };
  } catch (error) {
    return {
      api: null,
      error: errorMessage(error, "The Lumen API is unavailable."),
      source: "LIVE_API",
    };
  }
}

export function apiErrorMessage(error: unknown, fallback: string): string {
  return errorMessage(error, fallback);
}

function isMockClient(client: LumenApiClient): boolean {
  return "source" in client && client.source === "MOCK_FIXTURE";
}

function errorMessage(error: unknown, fallback: string): string {
  return error instanceof Error && error.message ? error.message : fallback;
}
