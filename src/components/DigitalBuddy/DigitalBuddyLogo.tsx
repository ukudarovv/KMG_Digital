import { DigitalBuddyCharacter } from "./DigitalBuddyCharacter";
import "./DigitalBuddyLogo.css";

type DigitalBuddyLogoProps = {
  mood?: "idle" | "thinking" | "happy" | "talking";
  className?: string;
};

/** Логотип Digital Buddy для контекстных окон (ТЗ 4.2: мин. 60×80 px). */
export function DigitalBuddyLogo({
  mood = "idle",
  className = "",
}: DigitalBuddyLogoProps) {
  return (
    <div className={`buddy-logo ${className}`.trim()} aria-label="Digital Buddy">
      <DigitalBuddyCharacter mood={mood} size={72} variant="standing" />
    </div>
  );
}
