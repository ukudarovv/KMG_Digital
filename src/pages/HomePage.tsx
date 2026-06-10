import { onboardingStages } from "../data/stages";
import { StageCard } from "../components/StageCard/StageCard";

export function HomePage() {
  return (
    <main className="home-page">
      <div className="home-page__frame">
        <header className="home-page__header">
          <div className="home-page__brand">
            <span className="home-page__logo">KMG</span>
            <span className="home-page__portal">team.kmg.kz</span>
          </div>
          <span className="home-page__badge">Программа адаптации</span>
        </header>

        <section className="home-page__hero">
          <h1>Добро пожаловать в нашу команду</h1>
          <p className="home-page__subtitle">
            Пройдите пять этапов, чтобы уверенно начать работу и почувствовать себя частью KMG
          </p>
        </section>

        <section className="home-page__journey" aria-label="Этапы адаптации">
          <div className="home-page__stages">
            {onboardingStages.map((stage, index) => (
              <div className="home-page__stage-item" key={stage.id}>
                <StageCard
                  step={index + 1}
                  title={stage.title}
                  description={stage.description}
                  status={stage.status}
                  period={stage.period}
                  path={stage.path}
                  icon={stage.icon}
                  disabled={stage.disabled}
                />
                {index < onboardingStages.length - 1 && (
                  <div className="home-page__connector" aria-hidden="true">
                    <span />
                  </div>
                )}
              </div>
            ))}
          </div>
        </section>

        <footer className="home-page__footer">
          <p>Наведите на этап, чтобы узнать подробности. Нажмите, чтобы перейти.</p>
        </footer>
      </div>
    </main>
  );
}
