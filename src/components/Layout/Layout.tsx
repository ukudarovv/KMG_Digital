import { NavLink } from "react-router-dom";
import {
  BarChart3,
  ClipboardList,
  Hand,
  Home,
  Settings,
  Target,
  UserRound,
} from "lucide-react";
import { DigitalBuddyProvider } from "../DigitalBuddy/DigitalBuddyContext";
import { DigitalBuddyWidget } from "../DigitalBuddy/DigitalBuddyWidget";
import "./Layout.css";

type LayoutProps = {
  children: React.ReactNode;
};

const navigationItems = [
  {
    title: "Главная",
    path: "/",
    icon: Home,
  },
  {
    title: "Знакомство",
    path: "/introduction",
    icon: Hand,
  },
  {
    title: "Вовлечение",
    path: "/engagement",
    icon: BarChart3,
  },
  {
    title: "Адаптация",
    path: "/adaptation",
    icon: Settings,
  },
  {
    title: "Закрепление",
    path: "/retention",
    icon: Target,
  },
];

export function Layout({ children }: LayoutProps) {
  return (
    <DigitalBuddyProvider>
      <div className="app-layout">
        <header className="app-header">
          <div className="app-header__brand">
            <div className="app-header__logo">
              <ClipboardList size={24} />
            </div>

            <div>
              <strong>KMG Onboarding</strong>
              <span>Digital Buddy Platform</span>
            </div>
          </div>

          <nav className="app-header__nav">
            {navigationItems.map((item) => {
              const Icon = item.icon;

              return (
                <NavLink
                  key={item.path}
                  to={item.path}
                  className={({ isActive }) =>
                    `app-header__nav-link ${
                      isActive ? "app-header__nav-link--active" : ""
                    }`
                  }
                >
                  <Icon size={16} />
                  {item.title}
                </NavLink>
              );
            })}
          </nav>

          <div className="app-header__profile">
            <div className="app-header__user">
              <UserRound size={17} />
              Азамат
            </div>
          </div>
        </header>

        <main className="app-layout__content">{children}</main>
        <DigitalBuddyWidget />
      </div>
    </DigitalBuddyProvider>
  );
}
