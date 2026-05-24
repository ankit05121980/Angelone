import { ShieldCheck } from "lucide-react";

export function LoginScreen(): JSX.Element {
  return (
    <section className="card p-6">
      <div className="mb-4 flex items-center gap-3">
        <ShieldCheck className="text-accent" />
        <div>
          <h2 className="text-xl font-semibold">Secure trading console</h2>
          <p className="muted">Use `/api/v1/auth/register` or `/api/v1/auth/login` to issue JWTs for production deployments.</p>
        </div>
      </div>
      <div className="grid gap-3 md:grid-cols-2">
        <input className="rounded-xl border border-white/10 bg-ink p-3 outline-none" placeholder="Email" />
        <input className="rounded-xl border border-white/10 bg-ink p-3 outline-none" placeholder="Password" type="password" />
      </div>
      <button className="mt-4 rounded-xl bg-accent px-4 py-2 font-semibold text-ink">Login</button>
    </section>
  );
}
