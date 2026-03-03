import { useState, useCallback, useEffect } from 'react';
import { api } from '../api/client';
import type { PermitRecord, PermitSearchParams, PermitStats } from '../types';

interface UsePermitsResult {
  permits: PermitRecord[];
  total: number;
  stats: PermitStats | null;
  loading: boolean;
  statsLoading: boolean;
  error: string | null;
  page: number;
  pageSize: number;
  search: (params: PermitSearchParams) => Promise<void>;
  setPage: (page: number) => void;
  refreshStats: () => Promise<void>;
}

export function usePermits(initialPageSize = 25): UsePermitsResult {
  const [permits, setPermits] = useState<PermitRecord[]>([]);
  const [total, setTotal] = useState(0);
  const [stats, setStats] = useState<PermitStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [statsLoading, setStatsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(initialPageSize);
  const [lastParams, setLastParams] = useState<PermitSearchParams>({});

  const search = useCallback(async (params: PermitSearchParams) => {
    setLoading(true);
    setError(null);
    try {
      const result = await api.searchPermits({ ...params, page: 1, page_size: pageSize });
      setPermits(result.results);
      setTotal(result.total);
      setPage(1);
      setLastParams(params);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Search failed');
    } finally {
      setLoading(false);
    }
  }, [pageSize]);

  const changePage = useCallback(async (newPage: number) => {
    setLoading(true);
    setError(null);
    try {
      const result = await api.searchPermits({ ...lastParams, page: newPage, page_size: pageSize });
      setPermits(result.results);
      setTotal(result.total);
      setPage(newPage);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Search failed');
    } finally {
      setLoading(false);
    }
  }, [lastParams, pageSize]);

  const refreshStats = useCallback(async () => {
    setStatsLoading(true);
    try {
      const s = await api.getPermitStats();
      setStats(s);
    } catch {
      // Stats are non-critical; silently ignore
    } finally {
      setStatsLoading(false);
    }
  }, []);

  useEffect(() => {
    void refreshStats();
  }, [refreshStats]);

  return {
    permits,
    total,
    stats,
    loading,
    statsLoading,
    error,
    page,
    pageSize,
    search,
    setPage: changePage,
    refreshStats,
  };
}
