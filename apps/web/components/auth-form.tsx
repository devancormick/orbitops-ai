"use client";

import { useState } from "react";

import { clearToken, login, storeToken } from "../lib/api";

export function AuthForm() {
  const [message, setMessage] = useState("Use `admin@orbitops.local` / `orbitops123` for the seeded admin account.");
  const [pending, setPending] = useState(false);

  return (
    <form
      className="card form-card"
      onSubmit={async (event) => {
        event.preventDefault();
        setPending(true);
        const formData = new FormData(event.currentTarget);
        const result = await login({
          email: String(formData.get("email")),
          password: String(formData.get("password"))
        });
        setPending(false);
        if (!result.ok) {
          clearToken();
          setMessage("Login failed. Check credentials and API URL.");
          return;
        }
        storeToken(result.token);
        setMessage(`Logged in as ${result.user.full_name}. Auth token stored in this browser.`);
      }}
    >
      <label className="field">
        <span>Email</span>
        <input name="email" defaultValue="admin@orbitops.local" />
      </label>
      <label className="field">
        <span>Password</span>
        <input name="password" type="password" defaultValue="orbitops123" />
      </label>
      <div className="action-row">
        <button className="button button-primary" type="submit" disabled={pending}>
          {pending ? "Signing in..." : "Sign in"}
        </button>
      </div>
      <p className="status-note">{message}</p>
    </form>
  );
}
