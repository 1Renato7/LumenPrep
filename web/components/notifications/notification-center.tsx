"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

import { LumenApiError, type LumenApiClient } from "@/lib/api/client-interface";
import { resolveLumenClient } from "@/lib/api/client-runtime";
import type { NotificationFeed } from "@/lib/api/types";

import styles from "./notification-center.module.css";

export function NotificationCenter({ api: suppliedApi }: { api?: LumenApiClient }) {
  const client = useMemo(() => resolveLumenClient(suppliedApi), [suppliedApi]);
  const [feed, setFeed] = useState<NotificationFeed | null>(null);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    if (!client.api) return;
    const controller = new AbortController();
    void client.api.listNotifications({ signal: controller.signal }).then(setFeed).catch((error: unknown) => {
      if (!(error instanceof LumenApiError && error.code === "CANCELLED")) setFeed({ notifications: [], unread_count: 0 });
    });
    return () => controller.abort();
  }, [client]);

  const unread = feed?.unread_count ?? 0;
  async function markRead(notificationId: string) {
    if (!client.api) return;
    await client.api.markNotificationRead(notificationId);
    setFeed((current) => current ? {
      unread_count: Math.max(0, current.unread_count - (current.notifications.find((item) => item.notification_id === notificationId)?.read_at ? 0 : 1)),
      notifications: current.notifications.map((item) => item.notification_id === notificationId ? { ...item, read_at: new Date().toISOString() } : item),
    } : current);
  }

  return <section className={styles.wrap} aria-label="Incident notifications">
    <p className={styles.live} aria-live="polite">{unread ? `${unread} new incident${unread === 1 ? "" : "s"} require attention.` : "No unread incidents."}</p>
    <button className={styles.bell} type="button" aria-expanded={open} aria-controls="incident-notifications" onClick={() => setOpen((value) => !value)}>
      <BellIcon /><span className={styles.screenReaderOnly}>Notifications</span>{unread ? <span className={styles.badge} aria-label={`${unread} unread incidents`}>{unread}</span> : null}
    </button>
    {unread ? <div className={styles.card}><div><strong>New incidents</strong><p>{unread} incident{unread === 1 ? "" : "s"} need review.</p></div><Link href="/incidents">Review incidents</Link></div> : null}
    {open ? <div className={styles.popover} id="incident-notifications" role="region" aria-label="New incidents">
      {feed?.notifications.length ? feed.notifications.map((item) => <article key={item.notification_id} className={item.read_at ? styles.read : undefined}><Link href={`/incidents/${encodeURIComponent(item.incident_id)}`} onClick={() => void markRead(item.notification_id)}><strong>{item.incident.title}</strong><small>{item.read_at ? "Read" : "New"} · {item.incident.root_cause.status}</small></Link><button type="button" onClick={() => void markRead(item.notification_id)} disabled={Boolean(item.read_at)}>Mark read</button></article>) : <p>No notifications yet.</p>}
    </div> : null}
  </section>;
}

function BellIcon() { return <svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" strokeWidth="1.9"><path d="M18 9a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9M10 21h4" /></svg>; }
