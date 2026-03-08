import React, { useRef, useCallback, useState } from 'react';
import { InputState } from '../../game/types';

interface TouchControlsProps {
  onInput: (input: Partial<InputState>) => void;
  onSpecial: () => void;
}

const JOYSTICK_SIZE = 120;
const KNOB_SIZE = 44;

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
      {/* Left joystick */}
      <div
        className="absolute bottom-8 left-8 z-30 touch-none"
        style={{ width: JOYSTICK_SIZE, height: JOYSTICK_SIZE }}
        onTouchStart={e => handleTouchStart(e, 'left')}
        onTouchMove={e => handleTouchMove(e, 'left')}
        onTouchEnd={e => handleTouchEnd(e, 'left')}
      >
        <div className="w-full h-full rounded-full border-2 border-[#5a3a28] bg-[#2a1810]/60 flex items-center justify-center">
          <div
            className="rounded-full bg-[#8a6a50]/80 border border-[#CD853F]"
            style={{
              width: KNOB_SIZE, height: KNOB_SIZE,
              transform: `translate(${leftPos.x}px, ${leftPos.y}px)`,
            }}
          />
        </div>
      </div>

      {/* Right joystick */}
      <div
        className="absolute bottom-8 right-8 z-30 touch-none"
        style={{ width: JOYSTICK_SIZE, height: JOYSTICK_SIZE }}
        onTouchStart={e => handleTouchStart(e, 'right')}
        onTouchMove={e => handleTouchMove(e, 'right')}
        onTouchEnd={e => handleTouchEnd(e, 'right')}
      >
        <div className="w-full h-full rounded-full border-2 border-[#5a3a28] bg-[#2a1810]/60 flex items-center justify-center">
          <div
            className="rounded-full bg-[#e74c3c]/60 border border-[#e74c3c]"
            style={{
              width: KNOB_SIZE, height: KNOB_SIZE,
              transform: `translate(${rightPos.x}px, ${rightPos.y}px)`,
            }}
          />
        </div>
      </div>

      {/* Special button */}
      <button
        className="absolute bottom-36 right-10 z-30 w-14 h-14 rounded-full bg-[#9b59b6]/50 border-2 border-[#9b59b6] flex items-center justify-center text-2xl active:scale-90 active:bg-[#9b59b6]/80 transition-transform touch-none"
        onTouchStart={e => { e.preventDefault(); onSpecial(); }}
      >
        ✨
      </button>
    </>
  );
};

export default TouchControls;
