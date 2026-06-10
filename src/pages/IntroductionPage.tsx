import { useEffect, useMemo, useState } from "react";

import { ArrowLeft, CheckCircle2, PlayCircle, RotateCcw } from "lucide-react";

import { useNavigate } from "react-router-dom";

import {

  onboardingApi,

  type BackendDayOneTask,

  type LoginPopupResponse,

} from "../api/onboardingApi";

import { useDigitalBuddy } from "../components/DigitalBuddy/DigitalBuddyContext";

import { DigitalBuddyPopup } from "../components/DigitalBuddyPopup/DigitalBuddyPopup";

import { ProgressBar } from "../components/ProgressBar/ProgressBar";

import { TaskCard } from "../components/TaskCard/TaskCard";

import { dayOneTasks, mapBackendTask } from "../data/dayOneTasks";

import type { DayOneTask } from "../data/dayOneTasks";

import "./IntroductionPage.css";



const EMPLOYEE_ID = 1;

const INTRO_POPUP_SESSION_KEY = "kmg_intro_popup_shown";



export function IntroductionPage() {

  const navigate = useNavigate();

  const { openChat } = useDigitalBuddy();

  const [isBuddyPopupOpen, setIsBuddyPopupOpen] = useState(false);

  const [loginPopup, setLoginPopup] = useState<LoginPopupResponse["popup"] | null>(

    null

  );

  const [backendTasks, setBackendTasks] = useState<BackendDayOneTask[]>([]);

  const [isLoading, setIsLoading] = useState(true);

  const [isSimulatingLogin, setIsSimulatingLogin] = useState(false);



  const loadTasks = async () => {

    const tasks = await onboardingApi.getDayOneTasks(EMPLOYEE_ID);

    setBackendTasks(tasks);

    return tasks;

  };



  const simulatePortalLogin = async (forcePopup = false, resetDemo = false) => {
    setIsSimulatingLogin(true);

    try {
      if (resetDemo) {
        await onboardingApi.resetDayOneDemo(EMPLOYEE_ID);
        sessionStorage.removeItem(INTRO_POPUP_SESSION_KEY);
      }

      const loginResponse = await onboardingApi.triggerUserLogin(EMPLOYEE_ID);
      setLoginPopup(loginResponse.popup);
      await loadTasks();

      const shouldOpenPopup = forcePopup || resetDemo;

      if (shouldOpenPopup) {
        setIsBuddyPopupOpen(true);
        sessionStorage.setItem(INTRO_POPUP_SESSION_KEY, "1");
      }

    } finally {

      setIsSimulatingLogin(false);

    }

  };



  useEffect(() => {

    const init = async () => {

      try {

        setIsLoading(true);

        const alreadyShown = sessionStorage.getItem(INTRO_POPUP_SESSION_KEY);

        await simulatePortalLogin(!alreadyShown);

      } finally {

        setIsLoading(false);

      }

    };



    init();

  }, []);



  const visibleTasks: DayOneTask[] = useMemo(() => {

    if (backendTasks.length > 0) {

      return backendTasks.map(mapBackendTask);

    }



    return dayOneTasks;

  }, [backendTasks]);



  const completedTasks = visibleTasks.filter(

    (task) => task.status === "completed"

  ).length;



  const nextTask = visibleTasks.find((task) => task.status !== "completed");

  const videoTask = useMemo(() => {

    if (backendTasks.length > 0) {

      return (

        backendTasks.find((task) => task.external_link) ||

        backendTasks[0] ||

        null

      );

    }



    return null;

  }, [backendTasks]);



  const mappedVideoTask = videoTask ? mapBackendTask(videoTask) : null;

  const videoUrl =

    loginPopup?.video_url ||

    videoTask?.external_link ||

    "https://team.kmg.kz/onboarding/welcome-video";



  const employeeName = loginPopup?.employee_name || "Азамат";

  const allTasksCompleted =

    visibleTasks.length > 0 && completedTasks === visibleTasks.length;



  const handleCompleteTask = async (taskId: number) => {

    await onboardingApi.completeTask(taskId);

    await loadTasks();

  };



  const handleAskQuestion = () => {

    setIsBuddyPopupOpen(false);

    openChat();

  };



  const handleWatchVideo = () => {

    if (videoUrl) {

      window.open(videoUrl, "_blank", "noopener,noreferrer");

    }

  };



  const handleConfirmVideo = async () => {

    if (!videoTask || videoTask.status === "completed") {

      return;

    }



    await handleCompleteTask(videoTask.id);

  };



  const popupNextTask = loginPopup?.next_task

    ? {

        title: loginPopup.next_task.title,

        description: loginPopup.next_task.description,

        deadline_at: loginPopup.next_task.deadline_at,

      }

    : nextTask

      ? {

          title: nextTask.title,

          description: nextTask.description,

          deadline_at: null,

        }

      : undefined;



  return (

    <main className="introduction-page">

      <DigitalBuddyPopup

        employeeName={employeeName}

        adaptationDay={1}

        completedTasks={loginPopup?.completed_tasks ?? completedTasks}

        totalTasks={loginPopup?.total_tasks ?? visibleTasks.length}

        videoUrl={videoUrl}

        nextTask={popupNextTask}

        isOpen={isBuddyPopupOpen}

        onClose={() => setIsBuddyPopupOpen(false)}

        onAskQuestion={handleAskQuestion}

        onWatchVideo={handleWatchVideo}

      />



      <div className="introduction-page__container">

        <button

          type="button"

          className="introduction-page__back"

          onClick={() => navigate("/")}

        >

          <ArrowLeft size={18} />

          Назад к этапам

        </button>



        <header className="introduction-page__header">

          <div>

            <span>Этап 2</span>

            <h1>Знакомство</h1>

            <p>

              День 1: приветствие, обязательные инструктажи, видео и первый

              контакт с Digital Buddy.

            </p>

          </div>



          <div className="introduction-page__header-actions">

            <button

              type="button"

              className="introduction-page__demo-btn"

              onClick={() => simulatePortalLogin(true, true)}

              disabled={isSimulatingLogin}

            >

              <RotateCcw size={16} />

              {isSimulatingLogin ? "Вход..." : "Симулировать вход"}

            </button>

            <div className="introduction-page__badge">День 1</div>

          </div>

        </header>



        <section className="introduction-page__grid">

          <div className="introduction-page__main">

            <article

              className={`video-card ${

                mappedVideoTask?.status === "completed"

                  ? "video-card--completed"

                  : ""

              }`}

            >

              <div className="video-card__icon">

                {mappedVideoTask?.status === "completed" ? (

                  <CheckCircle2 size={42} />

                ) : (

                  <PlayCircle size={42} />

                )}

              </div>



              <div>

                <span>Обязательное видео</span>

                <h2>Видеообращение Председателя Правления КМГ</h2>

                <p>

                  Посмотрите приветственное видео, чтобы познакомиться с

                  миссией, ценностями и ожиданиями компании.

                </p>



                {mappedVideoTask && (

                  <div className="video-card__status">

                    {mappedVideoTask.status === "completed"

                      ? "Просмотр подтверждён"

                      : "Требуется просмотр и подтверждение"}

                  </div>

                )}



                <div className="video-card__actions">

                  <button type="button" onClick={handleWatchVideo}>

                    Смотреть видео

                  </button>



                  {mappedVideoTask &&

                    mappedVideoTask.status !== "completed" && (

                      <button

                        type="button"

                        className="video-card__confirm"

                        onClick={handleConfirmVideo}

                      >

                        Подтвердить просмотр

                      </button>

                    )}

                </div>

              </div>

            </article>



            <section className="tasks-section">

              <div className="tasks-section__header">

                <div>

                  <span>Маршрут Дня 1</span>

                  <h2>Обязательные задачи</h2>

                </div>

              </div>



              <div className="tasks-section__list">

                {isLoading ? (

                  <div className="info-card">

                    <h3>Загрузка задач...</h3>

                    <p>Запускаем маршрут Дня 1 через OnUserLogin.</p>

                  </div>

                ) : (

                  visibleTasks.map((task) => (

                    <TaskCard

                      key={task.id}

                      task={task}

                      onComplete={handleCompleteTask}

                    />

                  ))

                )}

              </div>

            </section>

          </div>



          <aside className="introduction-page__sidebar">

            <ProgressBar

              completed={completedTasks}

              total={visibleTasks.length}

            />



            <div className="introduction-page__buddy-block">

              <button

                type="button"

                className="introduction-page__open-popup"

                onClick={() => setIsBuddyPopupOpen(true)}

              >

                Открыть приветствие Digital Buddy

              </button>

            </div>



            {allTasksCompleted ? (

              <div className="info-card info-card--success">

                <h3>День 1 завершён</h3>

                <p>

                  Все обязательные инструктажи выполнены. Завтра начнётся этап

                  «Вовлечение» с Culture Fit Nudges.

                </p>

              </div>

            ) : (

              <div className="info-card">

                <h3>Что важно сегодня?</h3>

                <p>

                  Завершите все обязательные инструктажи до конца рабочего дня.

                  Если задача не будет выполнена вовремя, HR получит уведомление

                  за 2 часа до конца дня.

                </p>

              </div>

            )}



            <div className="info-card">

              <h3>Digital Buddy 24/7</h3>

              <p>

                Нажмите на анимированного помощника в правом нижнем углу — он

                доступен на всех страницах и ответит по ВНД.

              </p>

            </div>

          </aside>

        </section>

      </div>

    </main>

  );

}

