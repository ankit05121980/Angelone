import type { LogEvent } from "../types";

interface LogsViewerProps {
  logs: LogEvent[];
}

export function LogsViewer({ logs }: LogsViewerProps) {
  return (
    <section className="card p-4">
      <div className="mb-3 flex items-center justify-between">
        <h3 className="font-semibold">Realtime logs</h3>
        <button className="rounded-lg border border-white/10 px-3 py-1 text-sm" onClick={() => new Audio("/notify.mp3").play().catch(() => undefined)}>
          Test sound
        </button>
      </div>
      <div className="max-h-72 space-y-2 overflow-auto font-mono text-xs">
        {logs.map((log, index) => (
          <div className="rounded-lg bg-ink/70 p-2" key={`${log.time}-${index}`}>
            <span className="text-accent">{log.time}</span> <span className="text-amber-300">{log.event}</span>
            <pre className="mt-1 whitespace-pre-wrap text-slate-300">{JSON.stringify(log.payload, null, 2)}</pre>
          </div>
        ))}
        {logs.length === 0 ? <p className="muted">Waiting for websocket events.</p> : null}
      </div>
    </section>
  );
}
