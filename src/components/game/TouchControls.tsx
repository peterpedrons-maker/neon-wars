import React, { useRef, useEffect, useCallback } from 'react';
import { InputState } from '../../game/types';

interface TouchControlsProps {
  onInput: (input: Partial<InputState>) => void;
  onSpecial: () => void;
}

const JOYSTICK_SIZE = 132;
const KNOB_SIZE = 56;
const MAX_DIST = JOYSTICK_SIZE / 2 - KNOB_SIZE / 2;
const DEAD_ZONE = 0.08;

interface StickState {
  id: number | null;
  cx: number;
  cy: number;
}

/**
 * Native (non-passive) touch handling anchored to the joystick's true
 * geometric center, computed fresh on every touchstart via
 * getBoundingClientRect. React's synthetic touch handlers are attached
 * passively by default, which silently defeats preventDefault() and lets
 * the page pan/zoom underneath the thumb while dragging — that mismatch
 * between visual center and touch-start origin was the source of the
 * "imprecise" joystick feel. Using imperative refs (not React state) for
 * the knob transform also avoids a re-render on every touchmove.
 */
function useStick(
  baseRef: React.RefObject<HTMLDivElement>,
  knobRef: React.RefObject<HTMLDivElement>,
  onMove: (nx: number, ny: number) => void,
  onEnd: () => void,
) {
  const stick = useRef<StickState>({ id: null, cx: 0, cy: 0 });

  useEffect(() => {
    const base = baseRef.current;
    const knob = knobRef.current;
    if (!base || !knob) return;

    const setKnob = (x: number, y: number) => {
      knob.style.transform = `translate(${x}px, ${y}px)`;
    };

    const start = (e: TouchEvent) => {
      e.preventDefault();
      if (stick.current.id !== null) return;
      const touch = e.changedTouches[0];
      const rect = base.getBoundingClientRect();
      stick.current = { id: touch.identifier, cx: rect.left + rect.width / 2, cy: rect.top + rect.height / 2 };
    };

    const move = (e: TouchEvent) => {
      if (stick.current.id === null) return;
      for (let i = 0; i < e.changedTouches.length; i++) {
        const touch = e.changedTouches[i];
        if (touch.identifier !== stick.current.id) continue;
        e.preventDefault();

        const dx = touch.clientX - stick.current.cx;
        const dy = touch.clientY - stick.current.cy;
        const dist = Math.hypot(dx, dy);
        const clamped = Math.min(dist, MAX_DIST);
        const angle = Math.atan2(dy, dx);
        const nx = dist > 0 ? (clamped / MAX_DIST) * Math.cos(angle) : 0;
        const ny = dist > 0 ? (clamped / MAX_DIST) * Math.sin(angle) : 0;

        setKnob(nx * MAX_DIST, ny * MAX_DIST);
        onMove(dist < DEAD_ZONE * MAX_DIST ? 0 : nx, dist < DEAD_ZONE * MAX_DIST ? 0 : ny);
      }
    };

    const end = (e: TouchEvent) => {
      for (let i = 0; i < e.changedTouches.length; i++) {
        if (e.changedTouches[i].identifier !== stick.current.id) continue;
        e.preventDefault();
        stick.current.id = null;
        setKnob(0, 0);
        onEnd();
      }
    };

    // Non-passive listeners are required so preventDefault() actually
    // stops the page from scrolling/zooming while dragging the stick.
    base.addEventListener('touchstart', start, { passive: false });
    window.addEventListener('touchmove', move, { passive: false });
    window.addEventListener('touchend', end, { passive: false });
    window.addEventListener('touchcancel', end, { passive: false });
    return () => {
      base.removeEventListener('touchstart', start);
      window.removeEventListener('touchmove', move);
      window.removeEventListener('touchend', end);
      window.removeEventListener('touchcancel', end);
    };
  }, [baseRef, knobRef, onMove, onEnd]);
}

const TouchControls: React.FC<TouchControlsProps> = ({ onInput, onSpecial }) => {
  const leftBaseRef = useRef<HTMLDivElement>(null);
  const leftKnobRef = useRef<HTMLDivElement>(null);
  const rightBaseRef = useRef<HTMLDivElement>(null);
  const rightKnobRef = useRef<HTMLDivElement>(null);

  const handleLeftMove = useCallback((nx: number, ny: number) => {
    onInput({ moveX: nx, moveY: ny });
  }, [onInput]);
  const handleLeftEnd = useCallback(() => {
    onInput({ moveX: 0, moveY: 0 });
  }, [onInput]);

  const handleRightMove = useCallback((nx: number, ny: number) => {
    if (nx === 0 && ny === 0) {
      onInput({ shooting: false });
      return;
    }
    onInput({ aimX: nx, aimY: ny, shooting: true });
  }, [onInput]);
  const handleRightEnd = useCallback(() => {
    onInput({ shooting: false });
  }, [onInput]);

  useStick(leftBaseRef, leftKnobRef, handleLeftMove, handleLeftEnd);
  useStick(rightBaseRef, rightKnobRef, handleRightMove, handleRightEnd);

  return (
    <>
      {/* Left joystick - movement */}
      <div
        ref={leftBaseRef}
        className="absolute z-30 touch-none"
        style={{
          bottom: 'calc(env(safe-area-inset-bottom, 0px) + 20px)',
          left: 'calc(env(safe-area-inset-left, 0px) + 16px)',
          width: JOYSTICK_SIZE, height: JOYSTICK_SIZE,
        }}
      >
        <div className="w-full h-full rounded-full flex items-center justify-center"
             style={{ border: '3px solid rgba(0,255,255,0.35)', background: 'rgba(0,0,20,0.55)' }}>
          <div
            ref={leftKnobRef}
            className="rounded-full"
            style={{
              width: KNOB_SIZE, height: KNOB_SIZE,
              background: 'radial-gradient(circle, rgba(0,255,255,0.45) 0%, rgba(0,255,255,0.2) 100%)',
              border: '2px solid rgba(0,255,255,0.7)',
              boxShadow: '0 0 15px rgba(0,255,255,0.3)',
              willChange: 'transform',
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
        ref={rightBaseRef}
        className="absolute z-30 touch-none"
        style={{
          bottom: 'calc(env(safe-area-inset-bottom, 0px) + 20px)',
          right: 'calc(env(safe-area-inset-right, 0px) + 16px)',
          width: JOYSTICK_SIZE, height: JOYSTICK_SIZE,
        }}
      >
        <div className="w-full h-full rounded-full flex items-center justify-center"
             style={{ border: '3px solid rgba(255,0,64,0.35)', background: 'rgba(0,0,20,0.55)' }}>
          <div
            ref={rightKnobRef}
            className="rounded-full"
            style={{
              width: KNOB_SIZE, height: KNOB_SIZE,
              background: 'radial-gradient(circle, rgba(255,0,64,0.45) 0%, rgba(255,0,64,0.2) 100%)',
              border: '2px solid rgba(255,0,64,0.7)',
              boxShadow: '0 0 15px rgba(255,0,64,0.3)',
              willChange: 'transform',
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
          bottom: 'calc(env(safe-area-inset-bottom, 0px) + ' + (JOYSTICK_SIZE + 36) + 'px)',
          right: 'calc(env(safe-area-inset-right, 0px) + 24px)',
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
