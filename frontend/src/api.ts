import axios from "axios";

import type { Candle, DashboardSummary, Position, Trade, TradeMode } from "./types";

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? "/api/v1",
  timeout: 15000
});

export async function fetchDashboard(): Promise<DashboardSummary> {
  const { data } = await api.get<DashboardSummary>("/dashboard");
  return data;
}

export async function fetchPositions(): Promise<Position[]> {
  const { data } = await api.get<Position[]>("/positions");
  return data;
}

export async function fetchTrades(): Promise<Trade[]> {
  const { data } = await api.get<Trade[]>("/trades");
  return data;
}

export async function fetchCandles(symbol: string): Promise<Candle[]> {
  const { data } = await api.get<Candle[]>(`/market-data/${symbol}/3m`);
  return data;
}

export async function updateStrategy(enabled: boolean, mode: TradeMode): Promise<void> {
  await api.put("/strategy/settings", {
    enabled,
    mode,
    max_loss_per_trade: 1000,
    target_profit_per_trade: 2000,
    max_daily_loss: 3000,
    max_trades_per_index: 3,
    max_concurrent_trades: 2
  });
}
