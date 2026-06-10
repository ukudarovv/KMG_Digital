import "./DigitalBuddyCharacter.css";

type BuddyMood = "idle" | "thinking" | "happy" | "talking";
type BuddyVariant = "avatar" | "standing";
type BuddyAnimate = "none" | "idle" | "appear" | "wave" | "nudge";

type DigitalBuddyCharacterProps = {
  mood?: BuddyMood;
  size?: number;
  variant?: BuddyVariant;
  animate?: BuddyAnimate;
  className?: string;
};

const BUDDY_IMAGE = "/buddy/digital-buddy.png";

export function DigitalBuddyCharacter({
  mood = "idle",
  size = 72,
  variant = "avatar",
  animate,
  className = "",
}: DigitalBuddyCharacterProps) {
  const isStanding = variant === "standing";
  const resolvedAnimate = animate ?? (isStanding ? "idle" : "none");

  return (
    <div
      className={[
        "buddy-character",
        `buddy-character--${variant}`,
        `buddy-character--${mood}`,
        `buddy-character--animate-${resolvedAnimate}`,
        className,
      ]
        .filter(Boolean)
        .join(" ")}
      style={{
        width: size,
        height: isStanding ? undefined : size,
      }}
      aria-hidden="true"
    >
      <div className="buddy-character__motion">
        <img
          className="buddy-character__image"
          src={BUDDY_IMAGE}
          alt=""
          draggable={false}
        />
        {isStanding && resolvedAnimate !== "none" && (
          <>
            <span className="buddy-character__blink" />
            <span className="buddy-character__shine" />
          </>
        )}
      </div>
    </div>
  );
}
