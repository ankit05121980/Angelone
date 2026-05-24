import { create } from "zustand";

import { fetchCandles, fetchDashboard, fetchPositions, fetchTrades, updateStrategy } from "./api";
import type { Candle, DashboardSummary, IndexSymbol, LogEvent, Position, Trade, TradeMode } from "./types";

interface AppState {
  summary: DashboardSummary | null;
  positions: Position[];
  trades: Trade[];
  candles: Record<IndexSymbol, Candle[]>;
  logs: LogEvent[];
  load: () => Promise<void>;
  setStrategy: (enabled: boolean, mode: TradeMode) => Promise<void>;
  pushEvent: (event: string, payload: unknown) => void;
}

export const useAppStore = create<AppState>((set, get) => ({
  summary: null,
  positions: [],
  trades: [],
  candles: { NIFTY: [], BANKNIFTY: [] },
  logs: [],
  load: async () => {
    const [summary, positions, trades, nifty, banknifty] = await Promise.all([
      fetchDashboard(),
      fetchPositions(),
      fetchTrades(),
      fetchCandles("NIFTY"),
      fetchCandles("BANKNIFTY")
    ]);
    set({ summary, positions, trades, candles: { NIFTY: nifty, BANKNIFTY: banknifty } });
  },
  setStrategy: async (enabled, mode) => {
    await updateStrategy(enabled, mode);
    set({ summary: get().summary ? { ...get().summary, strategy_enabled: enabled, mode } : get().summary });
  },
  pushEvent: (event, payload) => {
    set({ logs: [{ time: new Date().toLocaleTimeString(), event, payload }, ...get().logs].slice(0, 100) });
  }
}));
