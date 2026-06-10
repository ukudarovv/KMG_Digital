import type { SentimentWeek } from "../../data/retentionData";
import "./SentimentChart.css";

type SentimentChartProps = {
  data: SentimentWeek[];
};

export function SentimentChart({ data }: SentimentChartProps) {
  return (
    <div className="sentiment-chart">
      {data.map((item) => (
        <div key={item.week} className="sentiment-chart__row">
          <div className="sentiment-chart__label">{item.week}</div>

          <div className="sentiment-chart__bar">
            <div
              className="sentiment-chart__part sentiment-chart__part--positive"
              style={{ width: `${item.positive}%` }}
            >
              {item.positive}%
            </div>

            <div
              className="sentiment-chart__part sentiment-chart__part--neutral"
              style={{ width: `${item.neutral}%` }}
            >
              {item.neutral}%
            </div>

            <div
              className="sentiment-chart__part sentiment-chart__part--negative"
              style={{ width: `${item.negative}%` }}
            >
              {item.negative}%
            </div>
          </div>
        </div>
      ))}

      <div className="sentiment-chart__legend">
        <span>
          <i className="sentiment-chart__dot sentiment-chart__dot--positive" />
          Позитив
        </span>

        <span>
          <i className="sentiment-chart__dot sentiment-chart__dot--neutral" />
          Нейтрально
        </span>

        <span>
          <i className="sentiment-chart__dot sentiment-chart__dot--negative" />
          Негатив
        </span>
      </div>
    </div>
  );
}
