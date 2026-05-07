import Link from 'next/link';

const links = [
  { href: '/', label: 'Overview' },
  { href: '/agents', label: 'Agents' },
  { href: '/tasks', label: 'Tasks' },
  { href: '/conversations', label: 'Conversations' },
  { href: '/memory', label: 'Memory' },
  { href: '/logs', label: 'Logs' },
  { href: '/settings', label: 'Settings' },
];

export function Sidebar() {
  return (
    <aside className="w-56 border-r border-panelborder bg-panel/40 px-4 py-6 sticky top-0 h-screen">
      <div className="font-mono text-sm text-accent mb-8 px-2">AgentBoard OS</div>
      <nav className="flex flex-col gap-1">
        {links.map((l) => (
          <Link
            key={l.href}
            href={l.href}
            className="px-3 py-2 rounded text-sm text-ink hover:bg-panelborder/60 transition"
          >
            {l.label}
          </Link>
        ))}
      </nav>
    </aside>
  );
}

export function StatCard({
  label,
  value,
  hint,
}: {
  label: string;
  value: string | number;
  hint?: string;
}) {
  return (
    <div className="rounded-lg border border-panelborder bg-panel p-5">
      <div className="text-xs uppercase tracking-wide text-muted">{label}</div>
      <div className="mt-2 text-2xl font-mono">{value}</div>
      {hint ? <div className="text-xs text-muted mt-1">{hint}</div> : null}
    </div>
  );
}

export function Panel({
  title,
  children,
  right,
}: {
  title: string;
  children: React.ReactNode;
  right?: React.ReactNode;
}) {
  return (
    <section className="rounded-lg border border-panelborder bg-panel p-5">
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-sm font-semibold text-ink">{title}</h2>
        {right}
      </div>
      {children}
    </section>
  );
}
