interface MetricCardProps {
  label: string;
  value: string;
  tone?: "neutral" | "success" | "danger";
}

export function MetricCard({ label, value, tone = "neutral" }: MetricCardProps): JSX.Element {
  const color = tone === "success" ? "text-success" : tone === "danger" ? "text-danger" : "text-white";
  return (
    <div className="card p-4">
      <p className="muted">{label}</p>
      <p className={`mt-2 text-2xl font-bold ${color}`}>{value}</p>
    </div>
  );
}
