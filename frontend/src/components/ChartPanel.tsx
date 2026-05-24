import { CandlestickSeries, createChart, type IChartApi } from "lightweight-charts";
import { useEffect, useRef } from "react";

import type { Candle, IndexSymbol } from "../types";

interface ChartPanelProps {
  symbol: IndexSymbol;
  candles: Candle[];
}

export function ChartPanel({ symbol, candles }: ChartPanelProps) {
  const container = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!container.current) {
      return;
    }
    const chart: IChartApi = createChart(container.current, {
      height: 260,
      layout: { background: { color: "#0f1b2d" }, textColor: "#cbd5e1" },
      grid: { vertLines: { color: "#1e293b" }, horzLines: { color: "#1e293b" } }
    });
    const series = chart.addSeries(CandlestickSeries, {
      upColor: "#22c55e",
      downColor: "#ef4444",
      borderVisible: false,
      wickUpColor: "#22c55e",
      wickDownColor: "#ef4444"
    });
    series.setData(
      candles.map((item) => ({
        time: Math.floor(new Date(item.candle_time).getTime() / 1000) as never,
        open: item.open,
        high: item.high,
        low: item.low,
        close: item.close
      }))
    );
    chart.timeScale().fitContent();
    return () => chart.remove();
  }, [candles]);

  return (
    <section className="card p-4">
      <div className="mb-3 flex items-center justify-between">
        <h3 className="font-semibold">{symbol} 3m chart</h3>
        <span className="muted">TradingView Lightweight Charts</span>
      </div>
      <div ref={container} />
    </section>
  );
}
