import { useState, useEffect, useCallback } from 'react';
import { api } from '../api/client';
import type { PermitRecord, PermitSearchParams, PermitStats } from '../types';

export function usePermits() {
  const [permits, setPermits] = useState<PermitRecord[]>([]);
  const [total, setTotal] = useState(0);
  const [stats, setStats] = useState<PermitStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [statsLoading, setStatsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [params, setParams] = useState<PermitSearchParams>({
    limit: 50,
    offset: 0,
    sort: 'created_at',
    order: 'desc',
  });

  const search = useCallback(async (newParams?: Partial<PermitSearchParams>) => {
    const merged = { ...params, ...newParams };
    setParams(merged);
    setLoading(true);
    setError(null);
    try {
      const result = await api.searchPermits(merged);
      setPermits(result.results);
      setTotal(result.total);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Search failed');
    } finally {
      setLoading(false);
    }
  }, [params]);

  const loadStats = useCallback(async () => {
    setStatsLoading(true);
    try {
      const result = await api.getPermitStats();
      setStats(result);
    } catch {
      // Stats are non-critical
    } finally {
      setStatsLoading(false);
    }
  }, []);

  const nextPage = useCallback(() => {
    const newOffset = (params.offset ?? 0) + (params.limit ?? 50);
    if (newOffset < total) {
      search({ offset: newOffset });
    }
  }, [params, total, search]);

  const prevPage = useCallback(() => {
    const newOffset = Math.max(0, (params.offset ?? 0) - (params.limit ?? 50));
    search({ offset: newOffset });
  }, [params, search]);

  useEffect(() => {
    search();
    loadStats();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  return {
    permits,
    total,
    stats,
    loading,
    statsLoading,
    error,
    params,
    search,
    loadStats,
    nextPage,
    prevPage,
    currentPage: Math.floor((params.offset ?? 0) / (params.limit ?? 50)) + 1,
    totalPages: Math.ceil(total / (params.limit ?? 50)),
  };
}
