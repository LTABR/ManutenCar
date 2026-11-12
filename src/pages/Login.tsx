import { useState, type FormEvent } from "react";
import { ApiError } from "../api/client";
import { Icon } from "../components/Icon";
import { useAuth } from "../auth";

export function Login() {
  const { login, signUp } = useAuth();
  const [isSignUp, setIsSignUp] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    if (isSignUp && password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    setIsSubmitting(true);
    try {
      if (isSignUp) {
        await signUp(email.trim(), password);
      } else {
        await login(email.trim(), password);
      }
    } catch (caught) {
      setError(
        caught instanceof ApiError || caught instanceof Error
          ? caught.message
          : `Unable to ${isSignUp ? "create your account" : "sign in"}. Please try again.`,
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  function toggleMode() {
    setIsSignUp((current) => !current);
    setPassword("");
    setConfirmPassword("");
    setError("");
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
          <p>{isSignUp ? "GET STARTED" : "WELCOME BACK"}</p>
          <h1 id="login-title">{isSignUp ? "Create your account." : "Your garage is waiting."}</h1>
          <span>{isSignUp ? "Sign up to keep every service on track." : "Sign in to keep every service on track."}</span>
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
              autoComplete={isSignUp ? "new-password" : "current-password"}
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              placeholder={isSignUp ? "Create a password" : "Enter your password"}
              minLength={8}
              required
            />
          </label>
          {isSignUp && (
            <label>
              Confirm password
              <input
                type="password"
                autoComplete="new-password"
                value={confirmPassword}
                onChange={(event) => setConfirmPassword(event.target.value)}
                placeholder="Re-enter your password"
                minLength={8}
                required
              />
            </label>
          )}
          {error && <p className="login-error" role="alert">{error}</p>}
          <button className="login-submit" type="submit" disabled={isSubmitting}>
            {isSubmitting
              ? isSignUp ? "Creating account…" : "Signing in…"
              : isSignUp ? "Create account" : "Sign in"}
            <Icon name="arrow" size={16} />
          </button>
        </form>
        <p className="login-mode-switch">
          {isSignUp ? "Already have an account?" : "New to ManutenCar?"}{" "}
          <button type="button" onClick={toggleMode} disabled={isSubmitting}>
            {isSignUp ? "Sign in" : "Create an account"}
          </button>
        </p>
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
