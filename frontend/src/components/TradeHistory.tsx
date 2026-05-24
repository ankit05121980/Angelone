import type { Trade } from "../types";

interface TradeHistoryProps {
  trades: Trade[];
}

export function TradeHistory({ trades }: TradeHistoryProps): JSX.Element {
  return (
    <section className="card overflow-hidden">
      <div className="border-b border-white/10 p-4">
        <h3 className="font-semibold">Trade history</h3>
      </div>
      <div className="max-h-80 overflow-auto">
        <table className="w-full text-left text-sm">
          <thead className="sticky top-0 bg-panel text-slate-400">
            <tr>
              <th className="p-3">Time</th>
              <th>Mode</th>
              <th>Option</th>
              <th>Qty</th>
              <th>PnL</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {trades.map((trade) => (
              <tr className="border-t border-white/5" key={trade.id}>
                <td className="p-3">{new Date(trade.created_at).toLocaleString()}</td>
                <td>{trade.mode.toUpperCase()}</td>
                <td>{trade.option_symbol}</td>
                <td>{trade.quantity}</td>
                <td className={trade.pnl >= 0 ? "text-success" : "text-danger"}>{trade.pnl.toFixed(2)}</td>
                <td>{trade.status}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
