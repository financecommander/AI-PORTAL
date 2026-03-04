import { useEffect, useRef } from 'react';

const CHARS = 'アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン0123456789ABCDEF{}[]<>/\\|=+-*&^%$#@!';
const FONT_SIZE = 14;
const DROP_SPEED = 0.4;

export default function MatrixRain({ opacity = 0.14 }: { opacity?: number }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const rafRef = useRef<number>(0);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let columns = 0;
    let drops: number[] = [];

    const resize = () => {
      const parent = canvas.parentElement;
      if (!parent) return;
      canvas.width = parent.clientWidth;
      canvas.height = parent.clientHeight;
      const newCols = Math.floor(canvas.width / FONT_SIZE);
      if (newCols !== columns) {
        const old = drops;
        drops = Array.from({ length: newCols }, (_, i) =>
          i < old.length ? old[i] : Math.random() * -50
        );
        columns = newCols;
      }
    };

    resize();
    const ro = new ResizeObserver(resize);
    ro.observe(canvas.parentElement!);

    const draw = () => {
      ctx.fillStyle = 'rgba(0, 0, 0, 0.06)';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      for (let i = 0; i < columns; i++) {
        const char = CHARS[Math.floor(Math.random() * CHARS.length)];
        const x = i * FONT_SIZE;
        const y = drops[i] * FONT_SIZE;

        // Bright head
        ctx.fillStyle = '#5FBD7A';
        ctx.font = `${FONT_SIZE}px monospace`;
        ctx.fillText(char, x, y);

        // Slightly dimmer trail character above
        if (drops[i] > 1) {
          const trailChar = CHARS[Math.floor(Math.random() * CHARS.length)];
          ctx.fillStyle = '#3E9B5F';
          ctx.fillText(trailChar, x, y - FONT_SIZE);
        }

        drops[i] += DROP_SPEED + Math.random() * 0.3;

        if (y > canvas.height && Math.random() > 0.98) {
          drops[i] = Math.random() * -20;
        }
      }

      rafRef.current = requestAnimationFrame(draw);
    };

    rafRef.current = requestAnimationFrame(draw);

    return () => {
      cancelAnimationFrame(rafRef.current);
      ro.disconnect();
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      style={{
        position: 'absolute',
        inset: 0,
        opacity,
        zIndex: 0,
        pointerEvents: 'none',
      }}
    />
  );
}
