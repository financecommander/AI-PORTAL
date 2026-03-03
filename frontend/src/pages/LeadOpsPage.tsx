import { useState } from 'react';
import { FileSearch, TrendingUp, Download } from 'lucide-react';
import LeadOpsStats from '../components/leadops/LeadOpsStats';
import PermitFilters from '../components/leadops/PermitFilters';
import PermitTable from '../components/leadops/PermitTable';
import QueryInput from '../components/pipeline/QueryInput';
import { usePermits } from '../hooks/usePermits';
import type { PermitSearchParams } from '../types';

type Tab = 'search' | 'analytics' | 'export';

export default function LeadOpsPage() {
  const [activeTab, setActiveTab] = useState<Tab>('search');
  const {
    permits,
    total,
    stats,
    loading,
    statsLoading,
    error,
    page,
    pageSize,
    search,
    setPage,
  } = usePermits();

  const handleNaturalLanguageSearch = (query: string) => {
    search({ query });
  };

  const handleFilterSearch = (params: PermitSearchParams) => {
    search(params);
  };

  const tabs: Array<{ id: Tab; label: string; icon: React.ReactNode }> = [
    { id: 'search', label: 'Permit Search', icon: <FileSearch style={{ width: 16, height: 16 }} /> },
    { id: 'analytics', label: 'Analytics', icon: <TrendingUp style={{ width: 16, height: 16 }} /> },
    { id: 'export', label: 'Export', icon: <Download style={{ width: 16, height: 16 }} /> },
  ];

  return (
    <div
      className="tech-grid-bg"
      style={{
        flex: 1,
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
        overflow: 'hidden',
      }}
    >
      {/* Header */}
      <div
        style={{
          padding: '20px 24px 0',
          borderBottom: '1px solid var(--cr-border)',
          background: 'var(--cr-charcoal)',
        }}
      >
        <h1
          style={{
            fontSize: 22,
            fontWeight: 600,
            color: 'var(--cr-text)',
            margin: '0 0 4px',
            fontFamily: "'Space Grotesk', sans-serif",
          }}
        >
          LeadOps
        </h1>
        <p style={{ fontSize: 13, color: 'var(--cr-text-muted)', margin: '0 0 16px' }}>
          Search building permits and generate contractor leads across jurisdictions.
        </p>

        {/* Tabs */}
        <div style={{ display: 'flex', gap: 0 }}>
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 6,
                padding: '10px 16px',
                border: 'none',
                borderBottom: activeTab === tab.id ? '2px solid var(--cr-green-500)' : '2px solid transparent',
                background: 'transparent',
                color: activeTab === tab.id ? 'var(--cr-text)' : 'var(--cr-text-muted)',
                fontWeight: activeTab === tab.id ? 600 : 400,
                fontSize: 13,
                cursor: 'pointer',
                transition: 'all 150ms',
              }}
            >
              {tab.icon}
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Body */}
      <div style={{ flex: 1, overflow: 'auto', padding: 24, display: 'flex', flexDirection: 'column', gap: 20 }}>
        {/* Stats summary */}
        <LeadOpsStats stats={stats} loading={statsLoading} />

        {error && (
          <div
            style={{
              background: 'rgba(239,68,68,0.1)',
              border: '1px solid rgba(239,68,68,0.3)',
              borderRadius: 'var(--cr-radius)',
              padding: '10px 14px',
              color: '#ef4444',
              fontSize: 13,
            }}
          >
            {error}
          </div>
        )}

        {activeTab === 'search' && (
          <>
            {/* Natural language query */}
            <div>
              <h3 style={{ fontSize: 14, fontWeight: 600, color: 'var(--cr-text)', margin: '0 0 8px' }}>
                AI-Powered Search
              </h3>
              <QueryInput
                onSubmit={handleNaturalLanguageSearch}
                isRunning={loading}
                placeholder="Search permits by description, e.g. 'new construction in Atlanta over $500k'..."
              />
            </div>

            {/* Structured filters */}
            <div>
              <h3 style={{ fontSize: 14, fontWeight: 600, color: 'var(--cr-text)', margin: '0 0 8px' }}>
                Filter by Fields
              </h3>
              <PermitFilters onSearch={handleFilterSearch} loading={loading} />
            </div>

            {/* Results table */}
            <div
              style={{
                background: 'var(--cr-charcoal-deep)',
                borderRadius: 'var(--cr-radius)',
                padding: 16,
              }}
            >
              <PermitTable
                permits={permits}
                loading={loading}
                total={total}
                page={page}
                pageSize={pageSize}
                onPageChange={setPage}
              />
            </div>
          </>
        )}

        {activeTab === 'analytics' && (
          <div>
            <h3 style={{ fontSize: 14, fontWeight: 600, color: 'var(--cr-text)', margin: '0 0 8px' }}>
              Permit Analytics
            </h3>
            <QueryInput
              onSubmit={handleNaturalLanguageSearch}
              isRunning={loading}
              placeholder="Ask analytics questions, e.g. 'top 10 cities by permit volume this quarter'..."
            />
            <div
              style={{
                marginTop: 16,
                padding: 40,
                textAlign: 'center',
                color: 'var(--cr-text-dim)',
                fontSize: 13,
                background: 'var(--cr-charcoal-deep)',
                borderRadius: 'var(--cr-radius)',
              }}
            >
              Analytics dashboard coming soon. Use the search tab to explore permits.
            </div>
          </div>
        )}

        {activeTab === 'export' && (
          <div>
            <h3 style={{ fontSize: 14, fontWeight: 600, color: 'var(--cr-text)', margin: '0 0 8px' }}>
              Export Leads
            </h3>
            <QueryInput
              onSubmit={handleNaturalLanguageSearch}
              isRunning={loading}
              placeholder="Describe the leads to export, e.g. 'all active residential permits in Georgia'..."
            />
            <div
              style={{
                marginTop: 16,
                padding: 40,
                textAlign: 'center',
                color: 'var(--cr-text-dim)',
                fontSize: 13,
                background: 'var(--cr-charcoal-deep)',
                borderRadius: 'var(--cr-radius)',
              }}
            >
              Export functionality coming soon. Search results can be exported as CSV.
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
