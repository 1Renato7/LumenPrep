export interface PollingTimer {
  cancel(): void;
}

export interface PollingOptions {
  hasProcessing: boolean;
  onPoll: () => void;
  intervalMs?: number;
  setIntervalFn?: (callback: () => void, delay: number) => ReturnType<typeof setInterval>;
  clearIntervalFn?: (id: ReturnType<typeof setInterval>) => void;
}

/** Starts no timer unless the latest backend-authored response still has processing work. */
export function startProcessingPolling(options: PollingOptions): PollingTimer | undefined {
  if (!options.hasProcessing) return undefined;

  const setIntervalFn = options.setIntervalFn ?? setInterval;
  const clearIntervalFn = options.clearIntervalFn ?? clearInterval;
  const timer = setIntervalFn(options.onPoll, options.intervalMs ?? 1_000);

  return { cancel: () => clearIntervalFn(timer) };
}
