import React, { useRef, useCallback, useState } from 'react';
import { InputState } from '../../game/types';

interface TouchControlsProps {
  onInput: (input: Partial<InputState>) => void;
  onSpecial: () => void;
}

const JOYSTICK_SIZE = 140;
const KNOB_SIZE = 52;

const TouchControls: React.FC<TouchControlsProps> = ({ onInput, onSpecial }) => {
  const leftRef = useRef<{ id: number | null; startX: number; startY: number }>({ id: null, startX: 0, startY: 0 });
  const rightRef = useRef<{ id: number | null; startX: number; startY: number }>({ id: null, startX: 0, startY: 0 });
  const [leftPos, setLeftPos] = useState({ x: 0, y: 0 });
  const [rightPos, setRightPos] = useState({ x: 0, y: 0 });

  const handleTouchStart = useCallback((e: React.TouchEvent, side: 'left' | 'right') => {
    e.preventDefault();
    const touch = e.changedTouches[0];
    const ref = side === 'left' ? leftRef : rightRef;
    ref.current = { id: touch.identifier, startX: touch.clientX, startY: touch.clientY };
  }, []);

  const handleTouchMove = useCallback((e: React.TouchEvent, side: 'left' | 'right') => {
    e.preventDefault();
    const ref = side === 'left' ? leftRef : rightRef;
    if (ref.current.id === null) return;

    for (let i = 0; i < e.changedTouches.length; i++) {
      const touch = e.changedTouches[i];
      if (touch.identifier !== ref.current.id) continue;

      const dx = touch.clientX - ref.current.startX;
      const dy = touch.clientY - ref.current.startY;
      const maxDist = JOYSTICK_SIZE / 2 - KNOB_SIZE / 2;
      const dist = Math.hypot(dx, dy);
      const clampedDist = Math.min(dist, maxDist);
      const angle = Math.atan2(dy, dx);
      const nx = (clampedDist / maxDist) * Math.cos(angle);
      const ny = (clampedDist / maxDist) * Math.sin(angle);

      if (side === 'left') {
        setLeftPos({ x: nx * maxDist, y: ny * maxDist });
        onInput({ moveX: nx, moveY: ny });
      } else {
        setRightPos({ x: nx * maxDist, y: ny * maxDist });
        if (dist > 10) {
          onInput({ aimX: Math.cos(angle), aimY: Math.sin(angle), shooting: true });
        }
      }
    }
  }, [onInput]);

  const handleTouchEnd = useCallback((e: React.TouchEvent, side: 'left' | 'right') => {
    e.preventDefault();
    const ref = side === 'left' ? leftRef : rightRef;
    ref.current.id = null;
    if (side === 'left') {
      setLeftPos({ x: 0, y: 0 });
      onInput({ moveX: 0, moveY: 0 });
    } else {
      setRightPos({ x: 0, y: 0 });
      onInput({ shooting: false });
    }
  }, [onInput]);

  return (
    <>
      {/* Left joystick - movement */}
      <div
        className="absolute z-30 touch-none"
        style={{ bottom: 24, left: 16, width: JOYSTICK_SIZE, height: JOYSTICK_SIZE }}
        onTouchStart={e => handleTouchStart(e, 'left')}
        onTouchMove={e => handleTouchMove(e, 'left')}
        onTouchEnd={e => handleTouchEnd(e, 'left')}
      >
        <div className="w-full h-full rounded-full flex items-center justify-center"
             style={{ border: '3px solid rgba(0,255,255,0.35)', background: 'rgba(0,0,20,0.55)' }}>
          <div
            className="rounded-full"
            style={{
              width: KNOB_SIZE, height: KNOB_SIZE,
              background: 'radial-gradient(circle, rgba(0,255,255,0.45) 0%, rgba(0,255,255,0.2) 100%)',
              border: '2px solid rgba(0,255,255,0.7)',
              boxShadow: '0 0 15px rgba(0,255,255,0.3)',
              transform: `translate(${leftPos.x}px, ${leftPos.y}px)`,
            }}
          />
        </div>
        <div style={{
          position: 'absolute', bottom: -18, left: '50%', transform: 'translateX(-50%)',
          fontSize: 10, fontWeight: 800, color: 'rgba(0,255,255,0.5)', letterSpacing: '0.1em',
        }}>MOVE</div>
      </div>

      {/* Right joystick - aim & shoot */}
      <div
        className="absolute z-30 touch-none"
        style={{ bottom: 24, right: 16, width: JOYSTICK_SIZE, height: JOYSTICK_SIZE }}
        onTouchStart={e => handleTouchStart(e, 'right')}
        onTouchMove={e => handleTouchMove(e, 'right')}
        onTouchEnd={e => handleTouchEnd(e, 'right')}
      >
        <div className="w-full h-full rounded-full flex items-center justify-center"
             style={{ border: '3px solid rgba(255,0,64,0.35)', background: 'rgba(0,0,20,0.55)' }}>
          <div
            className="rounded-full"
            style={{
              width: KNOB_SIZE, height: KNOB_SIZE,
              background: 'radial-gradient(circle, rgba(255,0,64,0.45) 0%, rgba(255,0,64,0.2) 100%)',
              border: '2px solid rgba(255,0,64,0.7)',
              boxShadow: '0 0 15px rgba(255,0,64,0.3)',
              transform: `translate(${rightPos.x}px, ${rightPos.y}px)`,
            }}
          />
        </div>
        <div style={{
          position: 'absolute', bottom: -18, left: '50%', transform: 'translateX(-50%)',
          fontSize: 10, fontWeight: 800, color: 'rgba(255,0,64,0.5)', letterSpacing: '0.1em',
        }}>AIM</div>
      </div>

      {/* Special button */}
      <button
        className="absolute z-30 flex items-center justify-center touch-none"
        style={{
          bottom: JOYSTICK_SIZE + 40, right: 24,
          width: 62, height: 62, borderRadius: 99,
          background: 'radial-gradient(circle, rgba(191,90,242,0.4) 0%, rgba(191,90,242,0.15) 100%)',
          border: '3px solid rgba(191,90,242,0.65)',
          boxShadow: '0 0 20px rgba(191,90,242,0.25)',
          fontSize: 26,
        }}
        onTouchStart={e => { e.preventDefault(); onSpecial(); }}
      >
        ✨
        <div style={{
          position: 'absolute', bottom: -16,
          fontSize: 9, fontWeight: 800, color: 'rgba(191,90,242,0.6)', letterSpacing: '0.1em', whiteSpace: 'nowrap',
        }}>SPECIAL</div>
      </button>
    </>
  );
};

export default TouchControls;
