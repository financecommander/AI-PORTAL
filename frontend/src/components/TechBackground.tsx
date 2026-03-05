import { useEffect, useRef } from 'react';

/**
 * Animated data-center / circuit-board background canvas.
 * Renders network nodes, circuit traces, and pulsing data flows
 * in the Calculus brand green palette.
 */
export default function TechBackground() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animationId: number;
    let nodes: { x: number; y: number; radius: number; pulse: number; speed: number }[] = [];
    let connections: { from: number; to: number; progress: number; speed: number; active: boolean }[] = [];

    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
      generateNetwork();
    };

    const generateNetwork = () => {
      const w = canvas.width;
      const h = canvas.height;

      // Create grid of nodes (server rack positions)
      nodes = [];
      const cols = Math.floor(w / 120);
      const rows = Math.floor(h / 100);
      for (let r = 0; r < rows; r++) {
        for (let c = 0; c < cols; c++) {
          // Offset every other row for hex-grid feel
          const offsetX = r % 2 === 0 ? 0 : 60;
          nodes.push({
            x: 60 + c * 120 + offsetX + (Math.random() - 0.5) * 30,
            y: 50 + r * 100 + (Math.random() - 0.5) * 20,
            radius: 2 + Math.random() * 2,
            pulse: Math.random() * Math.PI * 2,
            speed: 0.01 + Math.random() * 0.02,
          });
        }
      }

      // Create connections between nearby nodes
      connections = [];
      for (let i = 0; i < nodes.length; i++) {
        for (let j = i + 1; j < nodes.length; j++) {
          const dx = nodes[i].x - nodes[j].x;
          const dy = nodes[i].y - nodes[j].y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < 180 && Math.random() < 0.4) {
            connections.push({
              from: i,
              to: j,
              progress: Math.random(),
              speed: 0.002 + Math.random() * 0.004,
              active: Math.random() < 0.3,
            });
          }
        }
      }
    };

    const draw = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // Draw circuit traces (connections)
      for (const conn of connections) {
        const from = nodes[conn.from];
        const to = nodes[conn.to];

        // Static trace line
        ctx.beginPath();
        ctx.moveTo(from.x, from.y);

        // Right-angle routing like circuit traces
        const midX = (from.x + to.x) / 2;
        ctx.lineTo(midX, from.y);
        ctx.lineTo(midX, to.y);
        ctx.lineTo(to.x, to.y);

        ctx.strokeStyle = 'rgba(15, 77, 44, 0.06)';
        ctx.lineWidth = 1;
        ctx.stroke();

        // Animated data pulse along active connections
        if (conn.active) {
          conn.progress += conn.speed;
          if (conn.progress > 1) {
            conn.progress = 0;
            conn.active = Math.random() < 0.3;
          }

          const t = conn.progress;
          let px: number, py: number;

          if (t < 0.33) {
            const lt = t / 0.33;
            px = from.x + (midX - from.x) * lt;
            py = from.y;
          } else if (t < 0.66) {
            const lt = (t - 0.33) / 0.33;
            px = midX;
            py = from.y + (to.y - from.y) * lt;
          } else {
            const lt = (t - 0.66) / 0.34;
            px = midX + (to.x - midX) * lt;
            py = to.y;
          }

          // Glowing pulse dot
          const gradient = ctx.createRadialGradient(px, py, 0, px, py, 8);
          gradient.addColorStop(0, 'rgba(62, 155, 95, 0.25)');
          gradient.addColorStop(1, 'rgba(62, 155, 95, 0)');
          ctx.fillStyle = gradient;
          ctx.beginPath();
          ctx.arc(px, py, 8, 0, Math.PI * 2);
          ctx.fill();

          ctx.fillStyle = 'rgba(62, 155, 95, 0.4)';
          ctx.beginPath();
          ctx.arc(px, py, 2, 0, Math.PI * 2);
          ctx.fill();
        } else {
          // Randomly activate connections
          if (Math.random() < 0.001) conn.active = true;
        }
      }

      // Draw nodes (server positions)
      for (const node of nodes) {
        node.pulse += node.speed;

        const pulseAlpha = 0.04 + Math.sin(node.pulse) * 0.02;

        // Outer glow
        const gradient = ctx.createRadialGradient(
          node.x, node.y, 0,
          node.x, node.y, node.radius * 4
        );
        gradient.addColorStop(0, `rgba(15, 77, 44, ${pulseAlpha * 2})`);
        gradient.addColorStop(1, 'rgba(15, 77, 44, 0)');
        ctx.fillStyle = gradient;
        ctx.beginPath();
        ctx.arc(node.x, node.y, node.radius * 4, 0, Math.PI * 2);
        ctx.fill();

        // Core dot
        ctx.fillStyle = `rgba(15, 77, 44, ${0.12 + Math.sin(node.pulse) * 0.04})`;
        ctx.beginPath();
        ctx.arc(node.x, node.y, node.radius, 0, Math.PI * 2);
        ctx.fill();
      }

      // Draw subtle grid lines (server rack outlines)
      ctx.strokeStyle = 'rgba(15, 77, 44, 0.025)';
      ctx.lineWidth = 1;
      const gridSize = 60;
      for (let x = 0; x < canvas.width; x += gridSize) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, canvas.height);
        ctx.stroke();
      }
      for (let y = 0; y < canvas.height; y += gridSize) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(canvas.width, y);
        ctx.stroke();
      }

      animationId = requestAnimationFrame(draw);
    };

    window.addEventListener('resize', resize);
    resize();
    draw();

    return () => {
      window.removeEventListener('resize', resize);
      cancelAnimationFrame(animationId);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
        pointerEvents: 'none',
        zIndex: 0,
      }}
    />
  );
}
