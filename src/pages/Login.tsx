import { useState, type FormEvent } from "react";
import { ApiError } from "../api/client";
import { Icon } from "../components/Icon";
import { useAuth } from "../auth";

export function Login() {
  const { login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setIsSubmitting(true);
    try {
      await login(email.trim(), password);
    } catch (caught) {
      setError(
        caught instanceof ApiError || caught instanceof Error
          ? caught.message
          : "Unable to sign in. Please try again.",
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="login-page">
      <section className="login-panel" aria-labelledby="login-title">
        <a className="brand login-brand" href="#" aria-label="ManutenCar home">
          <span className="brand-mark"><Icon name="wrench" size={19} /></span>
          <span>ManutenCar<span className="brand-period">.</span></span>
        </a>
        <div className="login-heading">
          <span className="login-security-icon"><Icon name="lock" size={20} /></span>
          <p>WELCOME BACK</p>
          <h1 id="login-title">Your garage is waiting.</h1>
          <span>Sign in to keep every service on track.</span>
        </div>
        <form className="login-form" onSubmit={submit}>
          <label>
            Email address
            <input
              type="email"
              autoComplete="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              placeholder="you@example.com"
              required
            />
          </label>
          <label>
            Password
            <input
              type="password"
              autoComplete="current-password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              placeholder="Enter your password"
              minLength={8}
              required
            />
          </label>
          {error && <p className="login-error" role="alert">{error}</p>}
          <button className="login-submit" type="submit" disabled={isSubmitting}>
            {isSubmitting ? "Signing in…" : "Sign in"} <Icon name="arrow" size={16} />
          </button>
        </form>
        <p className="login-security-note"><Icon name="lock" size={13} /> Credentials are encrypted before they leave this browser.</p>
      </section>
      <aside className="login-aside" aria-hidden="true">
        <div className="login-orb login-orb-one" />
        <div className="login-orb login-orb-two" />
        <div className="login-car"><Icon name="car" size={170} /></div>
        <div className="login-aside-copy"><span>MAINTENANCE, MADE CALM</span><strong>Drive with<br />confidence.</strong></div>
      </aside>
    </main>
  );
}
