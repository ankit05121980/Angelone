import { Power, RadioTower } from "lucide-react";

import { useAppStore } from "../store";
import type { TradeMode } from "../types";

export function StrategyControls(): JSX.Element {
  const summary = useAppStore((state) => state.summary);
  const setStrategy = useAppStore((state) => state.setStrategy);
  const mode = summary?.mode ?? "paper";
  const enabled = summary?.strategy_enabled ?? false;

  const changeMode = (nextMode: TradeMode) => {
    void setStrategy(enabled, nextMode);
  };

  return (
    <section className="card p-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <RadioTower className="text-accent" />
          <div>
            <h3 className="font-semibold">Strategy status</h3>
            <p className="muted">Entries 09:30-12:30, force exit 15:15</p>
          </div>
        </div>
        <button
          className={`flex items-center gap-2 rounded-xl px-4 py-2 font-semibold ${enabled ? "bg-danger text-white" : "bg-success text-ink"}`}
          onClick={() => void setStrategy(!enabled, mode)}
        >
          <Power size={16} /> {enabled ? "Disable" : "Enable"}
        </button>
      </div>
      <div className="mt-4 grid grid-cols-2 rounded-xl border border-white/10 p-1">
        {(["paper", "live"] as TradeMode[]).map((item) => (
          <button
            className={`rounded-lg py-2 text-sm font-semibold ${mode === item ? "bg-accent text-ink" : "text-slate-300"}`}
            key={item}
            onClick={() => changeMode(item)}
          >
            {item.toUpperCase()}
          </button>
        ))}
      </div>
      {mode === "live" ? <p className="mt-3 text-sm text-amber-300">Live mode uses Angel One SmartAPI credentials from backend environment variables.</p> : null}
    </section>
  );
}
