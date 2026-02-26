import { useState, useEffect } from 'react';
import { api } from '../api/client';
import { Brain } from 'lucide-react';

interface Pipeline {
  name: string;
  description: string;
  agents: string[];
}

export default function PipelinesPage() {
  const [pipelines, setPipelines] = useState<Pipeline[]>([]);

  useEffect(() => {
    api.request<{ pipelines: Pipeline[] }>('/api/v2/pipelines/list')
      .then(data => setPipelines(data.pipelines))
      .catch(console.error);
  }, []);

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold text-white mb-6">Intelligence Pipelines</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {pipelines.map(p => (
          <div key={p.name} className="p-5 rounded-xl" style={{ background: 'var(--navy)' }}>
            <div className="flex items-center gap-3 mb-3">
              <Brain className="w-5 h-5" style={{ color: 'var(--blue)' }} />
              <h3 className="font-semibold text-white">{p.name}</h3>
            </div>
            <p className="text-sm mb-3" style={{ color: '#8899AA' }}>{p.description}</p>
            <div className="flex flex-wrap gap-1">
              {p.agents.map(a => (
                <span key={a} className="px-2 py-0.5 rounded text-xs"
                      style={{ background: 'var(--navy-dark)', color: '#8899AA' }}>
                  {a}
                </span>
              ))}
            </div>
            <p className="text-xs mt-3" style={{ color: '#556677' }}>
              Pipeline execution coming in Phase 3C
            </p>
          </div>
        ))}
        {pipelines.length === 0 && (
          <p style={{ color: '#667788' }}>Loading pipelines...</p>
        )}
      </div>
    </div>
  );
}
