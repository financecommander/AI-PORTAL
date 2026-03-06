import { useState, useEffect, useRef, useCallback } from 'react';
import { ArrowLeft, Plus, Send, Pause, Play, CheckCircle, Wifi, WifiOff, RefreshCw, Lock, Layers } from 'lucide-react';
import { useSwarm } from '../hooks/useSwarm';
import type { CollaborationMode, CreateSessionRequest, SwarmSession } from '../types/swarm';
import BlueprintEditor from '../components/blueprint/BlueprintEditor';

// ── Helpers ─────────────────────────────────────────────────────────

const STATUS_COLORS: Record<string, string> = {
  active: '#1A6B3C',
  paused: '#D4A017',
  completed: '#2E75B6',
  failed: '#D64545',
};

const MODE_LABELS: Record<string, string> = {
  round_table: 'Round Table',
  review_chain: 'Review Chain',
  specialist: 'Specialist',
  debate: 'Debate',
};

function formatCost(cost: number): string {
  return cost === 0 ? '$0.00 (local)' : `$${cost.toFixed(4)}`;
}

function timeAgo(dateStr: string): string {
  const diff = Date.now() - new Date(dateStr).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return 'just now';
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  return `${Math.floor(hrs / 24)}d ago`;
}

// ── Caste Badge ─────────────────────────────────────────────────────

const CASTE_COLORS: Record<string, string> = {
  guardian_claude: '#7C3AED',
  guardian_opus: '#8B5CF6',
  hydra_code: '#059669',
  hydra_financial: '#D97706',
  hydra_compliance: '#9333EA',
  hydra_marketing: '#F59E0B',
  ultra_reasoning: '#2563EB',
  ultra_research: '#0891B2',
  mutalisk_legal: '#DC2626',
  mutalisk_conversational: '#EC4899',
  mutalisk_quick: '#F472B6',
  drone_ultra_cheap: '#14B8A6',
  drone_cheap: '#10B981',
  drone_fast: '#34D399',
  overseer: '#F97316',
  changeling: '#A855F7',
  nydus: '#6366F1',
};
