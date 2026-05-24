import type { Position } from "../types";

interface PositionsTableProps {
  positions: Position[];
}

export function PositionsTable({ positions }: PositionsTableProps): JSX.Element {
  return (
    <section className="card overflow-hidden">
      <div className="border-b border-white/10 p-4">
        <h3 className="font-semibold">Active positions</h3>
      </div>
      <table className="w-full text-left text-sm">
        <thead className="text-slate-400">
          <tr>
            <th className="p-3">Symbol</th>
            <th>Option</th>
            <th>Qty</th>
            <th>Avg</th>
            <th>LTP</th>
            <th>PnL</th>
          </tr>
        </thead>
        <tbody>
          {positions.map((position) => (
            <tr className="border-t border-white/5" key={position.id}>
              <td className="p-3">{position.symbol}</td>
              <td>{position.option_symbol}</td>
              <td>{position.quantity}</td>
              <td>{position.average_price.toFixed(2)}</td>
              <td>{position.last_price.toFixed(2)}</td>
              <td className={position.unrealized_pnl >= 0 ? "text-success" : "text-danger"}>{position.unrealized_pnl.toFixed(2)}</td>
            </tr>
          ))}
          {positions.length === 0 ? (
            <tr>
              <td className="p-4 text-slate-400" colSpan={6}>
                No open positions.
              </td>
            </tr>
          ) : null}
        </tbody>
      </table>
    </section>
  );
}
