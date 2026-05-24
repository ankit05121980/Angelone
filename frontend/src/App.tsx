import { useEffect } from "react";

import { ChartPanel } from "./components/ChartPanel";
import { LoginScreen } from "./components/LoginScreen";
import { LogsViewer } from "./components/LogsViewer";
import { MetricCard } from "./components/MetricCard";
import { PositionsTable } from "./components/PositionsTable";
import { RiskSettings } from "./components/RiskSettings";
import { StrategyControls } from "./components/StrategyControls";
import { TradeHistory } from "./components/TradeHistory";
import { useRealtime } from "./hooks/useRealtime";
import { useAppStore } from "./store";

export function App() {
  const { summary, positions, trades, candles, logs, load } = useAppStore();
  useRealtime();

  useEffect(() => {
    void load();
  }, [load]);

  return (
    <main className="min-h-screen p-4 lg:p-8">
      <header className="mb-6 flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <p className="text-sm uppercase tracking-[0.3em] text-accent">Angel One SmartAPI</p>
          <h1 className="text-3xl font-bold">NIFTY / BANKNIFTY Algo Trading</h1>
          <p className="muted">Intraday momentum breakout with strict paper/live mode separation.</p>
        </div>
        <a className="rounded-xl border border-white/10 px-4 py-2 text-sm" href="/api/v1/openapi.json">
          API docs
        </a>
      </header>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <MetricCard label="Live PnL" value={`INR ${(summary?.live_pnl ?? 0).toFixed(2)}`} tone={(summary?.live_pnl ?? 0) >= 0 ? "success" : "danger"} />
        <MetricCard label="Day PnL" value={`INR ${(summary?.day_pnl ?? 0).toFixed(2)}`} tone={(summary?.day_pnl ?? 0) >= 0 ? "success" : "danger"} />
        <MetricCard label="Win rate" value={`${(summary?.win_rate ?? 0).toFixed(1)}%`} />
        <MetricCard label="Open positions" value={`${summary?.active_positions ?? 0}`} />
      </div>

      <div className="mt-4 grid gap-4 xl:grid-cols-[1fr_360px]">
        <div className="grid gap-4">
          <div className="grid gap-4 xl:grid-cols-2">
            <ChartPanel symbol="NIFTY" candles={candles.NIFTY} />
            <ChartPanel symbol="BANKNIFTY" candles={candles.BANKNIFTY} />
          </div>
          <PositionsTable positions={positions.filter((item) => item.status === "open")} />
          <TradeHistory trades={trades} />
        </div>
        <aside className="grid content-start gap-4">
          <StrategyControls />
          <RiskSettings />
          <LoginScreen />
          <LogsViewer logs={logs} />
        </aside>
      </div>
    </main>
  );
}
