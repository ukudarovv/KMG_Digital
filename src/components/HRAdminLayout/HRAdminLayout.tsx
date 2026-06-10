import { Link, NavLink } from "react-router-dom";
import {
  ArrowLeftRight,
  BarChart3,
  BrainCircuit,
  FileText,
  Settings,
  ShieldCheck,
  UserRound,
  UsersRound,
} from "lucide-react";
import { HR_ROUTES } from "../../routes/hrRoutes";
import "./HRAdminLayout.css";

type HRAdminLayoutProps = {
  children: React.ReactNode;
};

const navigationItems = [
  {
    title: "Дашборд",
    path: HR_ROUTES.dashboard,
    icon: BarChart3,
    end: true,
  },
  {
    title: "Сотрудники",
    path: HR_ROUTES.employees,
    icon: UsersRound,
    end: false,
  },
  {
    title: "Документооборот",
    path: HR_ROUTES.documents,
    icon: FileText,
    end: false,
  },
  {
    title: "Рекрутинг AI",
    path: HR_ROUTES.recruiting,
    icon: BrainCircuit,
    end: false,
  },
  {
    title: "Настройки",
    path: HR_ROUTES.settings,
    icon: Settings,
    end: false,
  },
];

export function HRAdminLayout({ children }: HRAdminLayoutProps) {
  return (
    <div className="hr-admin-layout">
      <header className="hr-admin-header">
        <div className="hr-admin-header__brand">
          <div className="hr-admin-header__logo">
            <ShieldCheck size={24} />
          </div>

          <div>
            <strong>KMG HR Admin</strong>
            <span>Панель управления адаптацией</span>
          </div>
        </div>

        <nav className="hr-admin-header__nav">
          {navigationItems.map((item) => {
            const Icon = item.icon;

            return (
              <NavLink
                key={item.title}
                to={item.path}
                end={item.end}
                className={({ isActive }) =>
                  `hr-admin-header__nav-link ${
                    isActive ? "hr-admin-header__nav-link--active" : ""
                  }`
                }
              >
                <Icon size={16} />
                {item.title}
              </NavLink>
            );
          })}
        </nav>

        <div className="hr-admin-header__actions">
          <Link className="hr-admin-header__portal-link" to="/">
            <ArrowLeftRight size={15} />
            Портал сотрудника
          </Link>

          <div className="hr-admin-header__user">
            <UserRound size={17} />
            HR — Айгуль
          </div>
        </div>
      </header>

      <main className="hr-admin-layout__content">{children}</main>
    </div>
  );
}
