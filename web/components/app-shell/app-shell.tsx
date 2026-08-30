"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import type { ReactNode } from "react";

import styles from "./app-shell.module.css";
import { NotificationCenter } from "@/components/notifications/notification-center";

const destinations = [
  { href: "/transactions/new", label: "Input", description: "Create transactions", matches: (pathname: string) => pathname.startsWith("/transactions/new"), icon: InputIcon },
  { href: "/transactions", label: "Logs", description: "Follow processing", matches: (pathname: string) => (pathname === "/transactions" || pathname.startsWith("/transactions/")) && !pathname.startsWith("/transactions/new"), icon: LogsIcon },
  { href: "/incidents", label: "Incidents", description: "Investigate failures", matches: (pathname: string) => pathname.startsWith("/incidents"), icon: IncidentIcon },
] as const;

export function AppShell({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  return <div className={styles.shell}>
    <a className={styles.skipLink} href="#main-content">Skip to content</a>
    <aside className={styles.sidebar} aria-label="Lumen workspace navigation">
      <Link className={styles.brand} href="/transactions/new" aria-label="Lumen Input">
        <span className={styles.brandMark} aria-hidden="true"><span /></span>
        <span className={styles.brandCopy}><strong>LUMEN</strong><small>PAYMENT OBSERVABILITY</small></span>
      </Link>
      <nav className={styles.navigation} aria-label="Primary navigation">
        {destinations.map((destination) => {
          const active = destination.matches(pathname);
          const Icon = destination.icon;
          return <Link className={styles.navItem} data-active={active || undefined} aria-current={active ? "page" : undefined} aria-label={`${destination.label}: ${destination.description}`} href={destination.href} key={destination.href} onClick={(event) => { if (event.detail > 0) event.currentTarget.blur(); }}>
            <span className={styles.iconBox} aria-hidden="true"><Icon /></span>
            <span className={styles.navCopy}><strong>{destination.label}</strong><small>{destination.description}</small></span>
          </Link>;
        })}
      </nav>
      <div className={styles.workspaceStatus}>
        <span className={styles.statusDot} aria-hidden="true" />
        <span className={styles.statusCopy}><strong>Synthetic workspace</strong><small>Safe demo environment</small></span>
      </div>
    </aside>
    <div className={styles.mainColumn}><NotificationCenter /><div className={styles.content} id="main-content">{children}</div></div>
  </div>;
}

function InputIcon() { return <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"><path d="M4 5.5A1.5 1.5 0 0 1 5.5 4h13A1.5 1.5 0 0 1 20 5.5v13a1.5 1.5 0 0 1-1.5 1.5h-13A1.5 1.5 0 0 1 4 18.5z" /><path d="M8 12h8M12 8v8" /></svg>; }
function LogsIcon() { return <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"><path d="M5 5h14M5 12h14M5 19h14" /><path d="M8 3v4M15 10v4M11 17v4" /></svg>; }
function IncidentIcon() { return <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"><path d="M10.5 3.9 2.8 17.2A1.9 1.9 0 0 0 4.5 20h15a1.9 1.9 0 0 0 1.7-2.8L13.5 3.9a1.7 1.7 0 0 0-3 0Z" /><path d="M12 9v4M12 16.8v.2" /></svg>; }
