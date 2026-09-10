import * as React from "react";

const MOBILE_BREAKPOINT = 768;

function computeIsMobile() {
  const hasTouch = 'ontouchstart' in window || navigator.maxTouchPoints > 0;
  // Use the smaller of the two dimensions so a phone rotated to
  // landscape (e.g. 812x375) is still correctly detected as mobile —
  // checking innerWidth alone misclassified it as desktop, hiding the
  // touch joysticks and leaving the player with no way to move.
  const smallestSide = Math.min(window.innerWidth, window.innerHeight);
  return hasTouch && smallestSide < MOBILE_BREAKPOINT;
}

export function useIsMobile() {
  const [isMobile, setIsMobile] = React.useState<boolean | undefined>(undefined);

  React.useEffect(() => {
    const onChange = () => setIsMobile(computeIsMobile());
    onChange();
    window.addEventListener("resize", onChange);
    window.addEventListener("orientationchange", onChange);
    return () => {
      window.removeEventListener("resize", onChange);
      window.removeEventListener("orientationchange", onChange);
    };
  }, []);

  return !!isMobile;
}
