import { useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { ArrowLeft, BrainCircuit, FileUp } from "lucide-react";
import { recruitingApi } from "../../api/recruitingApi";
import { HR_ROUTES } from "../../routes/hrRoutes";
import "./HRAdminShared.css";

export function RecruitingAnalyzePage() {
  const navigate = useNavigate();
  const inputRef = useRef<HTMLInputElement>(null);
  const [file, setFile] = useState<File | null>(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const acceptFile = (candidate: File | undefined) => {
    if (!candidate) {
      return;
    }
    const name = candidate.name.toLowerCase();
    if (!name.endsWith(".pdf") && !name.endsWith(".docx")) {
      setError("Поддерживаются только файлы PDF и DOCX.");
      return;
    }
    setError(null);
    setFile(candidate);
  };

  const handleAnalyze = async () => {
    if (!file) {
      return;
    }
    setIsAnalyzing(true);
    setError(null);
    try {
      const result = await recruitingApi.analyzeResume(file);
      navigate(HR_ROUTES.candidate(result.candidate.id));
    } catch {
      setError(
        "Не удалось проанализировать резюме. Проверьте файл и доступность backend."
      );
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <main className="hra-page">
      <div className="hra-container">
        <header className="hra-header">
          <div>
            <span>Рекрутинг AI</span>
            <h1>Анализ резюме</h1>
            <p>
              ИИ извлечёт навыки, опыт и образование кандидата, затем сопоставит
              профиль с компетенциями отделов компании.
            </p>
          </div>

          <div className="hra-header__actions">
            <button
              type="button"
              className="hra-btn hra-btn--secondary"
              onClick={() => navigate(HR_ROUTES.recruiting)}
            >
              <ArrowLeft size={15} />
              Назад
            </button>
          </div>
        </header>

        {error && <div className="hra-alert hra-alert--error">{error}</div>}

        <section className="hra-card">
          <div
            className={`hra-upload ${isDragOver ? "is-dragover" : ""}`}
            onClick={() => inputRef.current?.click()}
            onDragOver={(event) => {
              event.preventDefault();
              setIsDragOver(true);
            }}
            onDragLeave={() => setIsDragOver(false)}
            onDrop={(event) => {
              event.preventDefault();
              setIsDragOver(false);
              acceptFile(event.dataTransfer.files?.[0]);
            }}
          >
            <FileUp size={36} color="#0b7a3b" />
            <strong>
              {file ? file.name : "Перетащите резюме сюда или нажмите для выбора"}
            </strong>
            <small>PDF или DOCX, до 10 МБ</small>
            <input
              ref={inputRef}
              type="file"
              accept=".pdf,.docx"
              style={{ display: "none" }}
              onChange={(event) => acceptFile(event.target.files?.[0])}
            />
          </div>

          <div style={{ marginTop: 18 }}>
            <button
              type="button"
              className="hra-btn"
              disabled={!file || isAnalyzing}
              onClick={handleAnalyze}
            >
              <BrainCircuit size={16} />
              {isAnalyzing
                ? "Анализ резюме... (может занять до минуты)"
                : "Анализировать"}
            </button>
          </div>
        </section>
      </div>
    </main>
  );
}
