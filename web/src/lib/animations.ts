import { Variants } from "framer-motion";

/**
 * Standard cubic-bezier and timing tokens from docs/WEB_MOTION_AND_INTERACTION_SPEC.md
 */
export const MOTION_TOKENS = {
  durationFast: 0.15,
  durationNormal: 0.25,
  durationPage: 0.35,
  durationPodium: 0.55,
  easeOutExpo: [0.16, 1, 0.3, 1] as const,
  easeInOutQuart: [0.77, 0, 0.175, 1] as const,
  springSnappy: { type: "spring", stiffness: 400, damping: 30 } as const,
  springGentle: { type: "spring", stiffness: 200, damping: 25 } as const,
};

/**
 * Page entrance and route transition variants
 */
export const pageTransitionVariants: Variants = {
  initial: { opacity: 0, y: 8 },
  animate: {
    opacity: 1,
    y: 0,
    transition: { duration: MOTION_TOKENS.durationPage, ease: MOTION_TOKENS.easeOutExpo },
  },
  exit: {
    opacity: 0,
    y: -4,
    transition: { duration: MOTION_TOKENS.durationFast },
  },
};

/**
 * Staggered container for card grids, tabular rows, and metrics
 */
export const staggerContainer: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.08,
      delayChildren: 0.05,
    },
  },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.08,
      delayChildren: 0.05,
    },
  },
};

/**
 * Staggered item inside container
 */
export const staggerItem: Variants = {
  hidden: { opacity: 0, y: 12 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: MOTION_TOKENS.durationNormal, ease: MOTION_TOKENS.easeOutExpo },
  },
  show: {
    opacity: 1,
    y: 0,
    transition: { duration: MOTION_TOKENS.durationNormal, ease: MOTION_TOKENS.easeOutExpo },
  },
};

export const fadeInUp: Variants = {
  hidden: { opacity: 0, y: 16 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: MOTION_TOKENS.durationNormal, ease: MOTION_TOKENS.easeOutExpo },
  },
  show: {
    opacity: 1,
    y: 0,
    transition: { duration: MOTION_TOKENS.durationNormal, ease: MOTION_TOKENS.easeOutExpo },
  },
};

export const scaleUp: Variants = {
  hidden: { opacity: 0, scale: 0.95 },
  visible: {
    opacity: 1,
    scale: 1,
    transition: { duration: MOTION_TOKENS.durationNormal, ease: MOTION_TOKENS.easeOutExpo },
  },
  show: {
    opacity: 1,
    scale: 1,
    transition: { duration: MOTION_TOKENS.durationNormal, ease: MOTION_TOKENS.easeOutExpo },
  },
};

export const transitionMedium = {
  duration: MOTION_TOKENS.durationNormal,
  ease: MOTION_TOKENS.easeOutExpo,
};

/**
 * Modal backdrop and card spring entrance
 */
export const modalBackdropVariants: Variants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { duration: 0.2 } },
  exit: { opacity: 0, transition: { duration: 0.15 } },
};

export const modalContentVariants: Variants = {
  hidden: { opacity: 0, scale: 0.95, y: 10 },
  visible: {
    opacity: 1,
    scale: 1,
    y: 0,
    transition: MOTION_TOKENS.springSnappy,
  },
  exit: {
    opacity: 0,
    scale: 0.95,
    y: 10,
    transition: { duration: 0.15 },
  },
};

/**
 * Leaderboard Top 3 Podium elevation variants
 */
export const podiumVariants: Variants = {
  hidden: { opacity: 0, scaleY: 0.3, originY: 1 },
  visible: (delay: number) => ({
    opacity: 1,
    scaleY: 1,
    originY: 1,
    transition: {
      delay,
      duration: MOTION_TOKENS.durationPodium,
      ease: MOTION_TOKENS.easeOutExpo,
    },
  }),
};

export const crownBounceVariants: Variants = {
  hidden: { opacity: 0, y: -16, scale: 0.8 },
  visible: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: {
      delay: 0.35,
      type: "spring",
      stiffness: 300,
      damping: 15,
    },
  },
};

