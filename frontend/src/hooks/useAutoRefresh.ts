import { useState, useEffect, useRef, useCallback } from 'react';

/**
 * Hook that auto-fetches data on an interval and refetches when the
 * browser tab regains focus.  Pauses polling while the tab is hidden
 * to avoid wasted requests.
 *
 * @param fetcher  Async function that returns the data.
 * @param intervalMs  Polling interval in milliseconds (default 30 000).
 */
export function useAutoRefresh<T>(
  fetcher: () => Promise<T>,
  intervalMs = 30_000,
) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  // Keep latest fetcher in a ref so the interval always uses the
  // current closure without needing to restart the timer.
  const fetcherRef = useRef(fetcher);
  fetcherRef.current = fetcher;

  const isMountedRef = useRef(true);

  const doFetch = useCallback(async (showLoading = false) => {
    try {
      if (showLoading) setLoading(true);
      const result = await fetcherRef.current();
      if (isMountedRef.current) {
        setData(result);
        setError(null);
        setLastUpdated(new Date());
      }
    } catch (err) {
      if (isMountedRef.current) {
        setError(err instanceof Error ? err.message : 'Fetch failed');
      }
    } finally {
      if (isMountedRef.current) setLoading(false);
    }
  }, []);

  // Initial fetch
  useEffect(() => {
    isMountedRef.current = true;
    doFetch(true);
    return () => { isMountedRef.current = false; };
  }, [doFetch]);

  // Polling interval — pauses when tab is hidden
  useEffect(() => {
    let timer: ReturnType<typeof setInterval> | null = null;

    const start = () => {
      if (timer) return;
      timer = setInterval(() => doFetch(false), intervalMs);
    };

    const stop = () => {
      if (timer) { clearInterval(timer); timer = null; }
    };

    const onVisibility = () => {
      if (document.hidden) {
        stop();
      } else {
        doFetch(false);   // immediate refresh on tab focus
        start();
      }
    };

    start();
    document.addEventListener('visibilitychange', onVisibility);

    return () => {
      stop();
      document.removeEventListener('visibilitychange', onVisibility);
    };
  }, [doFetch, intervalMs]);

  return { data, loading, error, lastUpdated, refresh: () => doFetch(false) };
}
