"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import NavBar from "@/components/NavBar";
import { login } from "@/lib/api";

export default function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const data = await login(username, password);
      localStorage.setItem("token", data.access_token);
      localStorage.setItem("username", data.user.username);
      router.push("/play");
    } catch (err: any) {
      setError(err.message || "login failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <NavBar />
      <main className="min-h-screen py-12 px-4">
        <div
          className="max-w-md mx-auto p-8 border rounded"
          style={{
            borderColor: "var(--border-green)",
            backgroundColor: "rgba(0, 255, 0, 0.02)",
          }}
        >
          <h1
            className="text-2xl font-bold mb-8"
            style={{ color: "var(--text-green-bright)" }}
          >
            $ login
          </h1>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label
                className="block text-sm mb-2"
                style={{ color: "var(--text-green)" }}
              >
                username:
              </label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full px-3 py-2 border rounded text-sm font-mono"
                style={{
                  borderColor: "var(--text-green-subtle)",
                  backgroundColor: "var(--bg-darker)",
                  color: "var(--text-green)",
                }}
                required
              />
            </div>

            <div>
              <label
                className="block text-sm mb-2"
                style={{ color: "var(--text-green)" }}
              >
                password:
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-3 py-2 border rounded text-sm font-mono"
                style={{
                  borderColor: "var(--text-green-subtle)",
                  backgroundColor: "var(--bg-darker)",
                  color: "var(--text-green)",
                }}
                required
              />
            </div>

            {error && (
              <p
                className="text-sm"
                style={{ color: "var(--accent-cyan)" }}
              >
                error: {error}
              </p>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full px-4 py-2 border rounded text-sm font-mono hover:opacity-80 disabled:opacity-50"
              style={{
                color: "var(--bg-dark)",
                backgroundColor: "var(--text-green)",
                borderColor: "var(--text-green)",
              }}
            >
              {loading ? "loading..." : "$ login"}
            </button>
          </form>

          <p
            className="mt-6 text-sm text-center"
            style={{ color: "var(--text-gray)" }}
          >
            no account?{" "}
            <Link
              href="/register"
              style={{ color: "var(--text-green)" }}
              className="hover:opacity-80"
            >
              register here
            </Link>
          </p>
        </div>
      </main>
    </>
  );
}
