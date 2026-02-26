import { useState, useEffect } from 'react';
import { api } from '../api/client';
import type { Specialist } from '../types';

export default function ChatPage() {
  const [specialists, setSpecialists] = useState<Specialist[]>([]);
  const [selected, setSelected] = useState<Specialist | null>(null);

  useEffect(() => {
    api.request<{ specialists: Specialist[] }>('/specialists/')
      .then(data => {
        setSpecialists(data.specialists);
        if (data.specialists.length > 0) setSelected(data.specialists[0]);
      })
      .catch(console.error);
  }, []);

  return (
    <div className="flex h-screen">
      {/* Specialist selector */}
      <div className="w-64 p-4 border-r overflow-y-auto" style={{ borderColor: '#2A3A5C' }}>
        <h2 className="text-sm font-semibold text-white mb-3">Specialists</h2>
        {specialists.map(s => (
          <button
            key={s.id}
            onClick={() => setSelected(s)}
            className="w-full text-left px-3 py-2.5 rounded-lg text-sm mb-1 transition-all"
            style={{
              background: selected?.id === s.id ? 'var(--navy-light)' : 'transparent',
              color: selected?.id === s.id ? '#FFFFFF' : '#8899AA',
            }}
          >
            <div className="font-medium">{s.name}</div>
            <div className="text-xs mt-0.5 opacity-60">{s.provider} / {s.model}</div>
          </button>
        ))}
      </div>

      {/* Chat area — Phase 3B will implement full chat interface */}
      <div className="flex-1 flex flex-col items-center justify-center p-8">
        {selected ? (
          <div className="text-center">
            <h2 className="text-xl font-bold text-white mb-2">{selected.name}</h2>
            <p className="text-sm" style={{ color: '#8899AA' }}>{selected.description}</p>
            <p className="text-xs mt-4" style={{ color: '#556677' }}>
              Chat interface coming in Phase 3B
            </p>
          </div>
        ) : (
          <p style={{ color: '#667788' }}>Select a specialist to begin</p>
        )}
      </div>
    </div>
  );
}
