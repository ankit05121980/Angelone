export function RiskSettings() {
  const settings = [
    ["NIFTY capital", "INR 50,000"],
    ["BANKNIFTY capital", "INR 50,000"],
    ["Max loss / trade", "INR 1,000"],
    ["Target / trade", "INR 2,000"],
    ["Daily loss lock", "INR 3,000"],
    ["Trades / index", "3"]
  ];

  return (
    <section className="card p-4">
      <h3 className="mb-3 font-semibold">Risk management</h3>
      <div className="grid gap-3 sm:grid-cols-2">
        {settings.map(([label, value]) => (
          <div className="rounded-xl border border-white/10 bg-ink/60 p-3" key={label}>
            <p className="muted">{label}</p>
            <p className="font-semibold">{value}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
