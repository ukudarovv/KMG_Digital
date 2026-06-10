import { CalendarDays, Clock, UserRound } from "lucide-react";
import type { OneToOneMeeting } from "../../data/adaptationData";
import "./MeetingCard.css";

type MeetingCardProps = {
  meeting: OneToOneMeeting;
};

export function MeetingCard({ meeting }: MeetingCardProps) {
  const statusLabel = {
    upcoming: "Ближайшая",
    completed: "Проведена",
    pending: "Запланирована",
  }[meeting.status];

  return (
    <article className={`meeting-card meeting-card--${meeting.status}`}>
      <div className="meeting-card__top">
        <span>{statusLabel}</span>
        <h3>{meeting.title}</h3>
      </div>

      <div className="meeting-card__meta">
        <div>
          <CalendarDays size={17} />
          {meeting.date}
        </div>

        <div>
          <Clock size={17} />
          {meeting.time}
        </div>

        <div>
          <UserRound size={17} />
          {meeting.manager}
        </div>
      </div>
    </article>
  );
}
