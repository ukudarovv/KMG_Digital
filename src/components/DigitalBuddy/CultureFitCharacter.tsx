import { DigitalBuddyCharacter } from "./DigitalBuddyCharacter";

type CultureFitCharacterProps = {
  size?: number;
  animate?: "nudge" | "wave" | "idle" | "appear";
};

/** Персонаж Culture Fit — тот же Digital Buddy с лёгкой анимацией. */
export function CultureFitCharacter({
  size = 72,
  animate = "nudge",
}: CultureFitCharacterProps) {
  return (
    <DigitalBuddyCharacter
      mood="happy"
      size={size}
      variant="standing"
      animate={animate}
    />
  );
}
