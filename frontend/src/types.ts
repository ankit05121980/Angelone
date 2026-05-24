export type TradeMode = "paper" | "live";
export type IndexSymbol = "NIFTY" | "BANKNIFTY";

export interface DashboardSummary {
  mode: TradeMode;
  strategy_enabled: boolean;
  live_pnl: number;
  day_pnl: number;
  win_rate: number;
  active_positions: number;
  trades_taken: Record<IndexSymbol, number>;
}

export interface Position {
  id: string;
  symbol: IndexSymbol;
  option_symbol: string;
  quantity: number;
  average_price: number;
  last_price: number;
  unrealized_pnl: number;
  status: "open" | "closed";
}

export interface Trade {
  id: string;
  mode: TradeMode;
  symbol: IndexSymbol;
  option_symbol: string;
  quantity: number;
  entry_price: number;
  exit_price: number | null;
  pnl: number;
  status: "open" | "closed";
  exit_reason: string | null;
  created_at: string;
}

export interface Candle {
  symbol: IndexSymbol;
  timeframe: string;
  candle_time: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface LogEvent {
  time: string;
  event: string;
  payload: unknown;
}
