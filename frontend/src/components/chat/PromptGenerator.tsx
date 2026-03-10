import { useState } from 'react';
import { Sparkles, ChevronRight, X } from 'lucide-react';

/** Prompt templates keyed by specialist ID (falls back to "default"). */
const PROMPT_LIBRARY: Record<string, { category: string; prompts: string[] }[]> = {
  'financial-analyst': [
    { category: 'Valuation', prompts: [
      'Build a DCF model for a $5M multifamily property with 12 units averaging $1,200/mo rent',
      'Compare cap rate compression across Sun Belt MSAs over the last 3 years',
      'Analyze the debt service coverage ratio for a 75% LTV bridge loan at 9.5% interest',
    ]},
    { category: 'Market Analysis', prompts: [
      'What are the key risk factors in the current CRE lending environment?',
      'Compare fixed vs floating rate structures for a 36-month bridge loan',
      'Evaluate refinance risk for a portfolio of DSCR loans originated in 2022',
    ]},
  ],
  'research-assistant': [
    { category: 'Due Diligence', prompts: [
      'Research the regulatory framework for private credit fund formation in Delaware',
      'Summarize recent CFPB enforcement actions related to commercial lending',
      'Analyze the competitive landscape for AI-powered underwriting platforms',
    ]},
    { category: 'Market Research', prompts: [
      'What is the current TAM for private credit in the US mid-market?',
      'Research recent trends in CDFI lending and federal funding programs',
      'Compare portfolio monitoring tools used by institutional credit funds',
    ]},
  ],
  'legal-quick': [
    { category: 'Lending Law', prompts: [
      'What are the key differences between judicial and non-judicial foreclosure states?',
      'Explain the Truth in Lending Act requirements for commercial loans',
      'What constitutes a valid demand letter under UCC Article 9?',
    ]},
    { category: 'Compliance', prompts: [
      'Outline BSA/AML requirements for a private credit fund',
      'What fair lending obligations apply to non-bank commercial lenders?',
      'Summarize ECOA requirements for adverse action notices',
    ]},
  ],
  'calculus-intelligence': [
    { category: 'Strategic Analysis', prompts: [
      'Analyze the risk-adjusted return profile of a $50M CRE bridge lending portfolio',
      'Compare the institutional viability of a direct lending fund vs. a CLO structure',
      'Evaluate the strategic implications of rising interest rates on private credit origination',
    ]},
    { category: 'Deep Reasoning', prompts: [
      'What second-order effects would a 200bp rate cut have on CRE bridge lending?',
      'Analyze the game theory dynamics between borrowers, lenders, and servicers in distressed CRE',
      'Build a framework for evaluating AI automation ROI in institutional credit operations',
    ]},
  ],
  'lex-intelligence': [
    { category: 'Legal Analysis', prompts: [
      'Analyze the enforceability of a personal guarantee on a non-recourse CRE loan',
      'What are the legal requirements for a valid UCC-1 filing in New York?',
      'Research recent case law on lender liability in construction loan disputes',
    ]},
    { category: 'Regulatory', prompts: [
      'Draft a regulatory risk assessment for an AI-powered underwriting platform',
      'Analyze OCC guidance on third-party risk management for bank-fintech partnerships',
      'What state licensing requirements apply to a private credit fund operating nationally?',
    ]},
  ],
  'code-reviewer': [
    { category: 'Architecture', prompts: [
      'Review this FastAPI endpoint for security vulnerabilities and suggest improvements',
      'Design a database schema for tracking loan covenant compliance over time',
      'How should I structure a multi-tenant SaaS backend for financial data isolation?',
    ]},
    { category: 'Code Quality', prompts: [
      'Optimize this SQL query for a 10M-row loan performance table',
      'Review this React component for performance issues and suggest memoization strategy',
      'Design an idempotent API endpoint for processing loan payments',
    ]},
  ],
  'compliance-scanner': [
    { category: 'Regulatory Check', prompts: [
      'Scan this loan agreement for TILA/RESPA compliance issues',
      'Check if our borrower onboarding process meets BSA/AML requirements',
      'Evaluate our data retention policy against CCPA and GLBA requirements',
    ]},
  ],
  'data-analyst': [
    { category: 'Financial Data', prompts: [
      'Calculate the weighted average DSCR for this portfolio of 50 loans',
      'Build a cohort analysis framework for tracking loan delinquency rates',
      'Design a SQL query to identify loans approaching covenant trigger thresholds',
    ]},
  ],
  default: [
    { category: 'General', prompts: [
      'Help me analyze this situation step by step',
      'What are the key risks and opportunities here?',
      'Summarize the most important considerations for this decision',
    ]},
  ],
};

interface PromptGeneratorProps {
  specialistId: string | null;
  onSelectPrompt: (prompt: string) => void;
}

export default function PromptGenerator({ specialistId, onSelectPrompt }: PromptGeneratorProps) {
  const [isOpen, setIsOpen] = useState(false);

  const categories = PROMPT_LIBRARY[specialistId ?? ''] ?? PROMPT_LIBRARY.default;

  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: 6,
          background: 'none',
          border: '1px solid var(--cr-border)',
          borderRadius: 20,
          padding: '6px 14px',
          color: 'var(--cr-text-muted)',
          fontSize: 12,
          cursor: 'pointer',
          transition: 'all 150ms',
        }}
        onMouseEnter={(e) => { e.currentTarget.style.borderColor = 'var(--cr-green-600)'; e.currentTarget.style.color = 'var(--cr-green-900)'; }}
        onMouseLeave={(e) => { e.currentTarget.style.borderColor = 'var(--cr-border)'; e.currentTarget.style.color = 'var(--cr-text-muted)'; }}
      >
        <Sparkles style={{ width: 13, height: 13 }} />
        Prompt Library
      </button>
    );
  }

  return (
    <div style={{
      border: '1px solid var(--cr-border)',
      borderRadius: 'var(--cr-radius-sm)',
      background: 'var(--cr-white)',
      padding: 16,
      marginBottom: 12,
    }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 13, fontWeight: 600, color: 'var(--cr-text)' }}>
          <Sparkles style={{ width: 14, height: 14, color: 'var(--cr-green-600)' }} />
          Prompt Library
        </div>
        <button
          onClick={() => setIsOpen(false)}
          style={{ background: 'none', border: 'none', cursor: 'pointer', padding: 4, color: 'var(--cr-text-dim)' }}
        >
          <X style={{ width: 14, height: 14 }} />
        </button>
      </div>

      {categories.map((cat) => (
        <div key={cat.category} style={{ marginBottom: 12 }}>
          <div style={{
            fontSize: 10,
            fontWeight: 600,
            color: 'var(--cr-text-muted)',
            textTransform: 'uppercase',
            letterSpacing: '0.06em',
            marginBottom: 6,
          }}>
            {cat.category}
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
            {cat.prompts.map((prompt) => (
              <button
                key={prompt}
                onClick={() => { onSelectPrompt(prompt); setIsOpen(false); }}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  gap: 8,
                  width: '100%',
                  textAlign: 'left',
                  padding: '8px 10px',
                  borderRadius: 6,
                  border: '1px solid transparent',
                  background: 'var(--cr-surface)',
                  cursor: 'pointer',
                  fontSize: 12,
                  color: 'var(--cr-text-secondary)',
                  lineHeight: 1.4,
                  transition: 'all 120ms',
                }}
                onMouseEnter={(e) => { e.currentTarget.style.borderColor = 'var(--cr-green-600)'; e.currentTarget.style.color = 'var(--cr-text)'; }}
                onMouseLeave={(e) => { e.currentTarget.style.borderColor = 'transparent'; e.currentTarget.style.color = 'var(--cr-text-secondary)'; }}
              >
                <span>{prompt}</span>
                <ChevronRight style={{ width: 12, height: 12, flexShrink: 0, opacity: 0.4 }} />
              </button>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
