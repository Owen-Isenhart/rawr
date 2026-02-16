"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

export default function NavBar() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [username, setUsername] = useState("");

  useEffect(() => {
    const token = localStorage.getItem("token");
    const user = localStorage.getItem("username");
    setIsLoggedIn(!!token);
    setUsername(user || "");
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("username");
    setIsLoggedIn(false);
    window.location.href = "/";
  };

  return (
    <nav
      className="w-full border-b px-4 py-3 flex justify-between items-center"
      style={{
        borderColor: "var(--border-green)",
        backgroundColor: "var(--bg-darker)",
      }}
    >
      {/* Logo */}
      <Link
        href="/"
        className="text-lg font-bold"
        style={{
          color: "var(--text-green)",
          textDecoration: "none",
        }}
      >
        rawr
      </Link>

      {/* Navigation Links */}
      <div className="flex gap-4 text-sm">
        <Link
          href="/play"
          className="hover:opacity-80"
          style={{
            color: "var(--text-green)",
            textDecoration: "none",
          }}
        >
          play
        </Link>
        <Link
          href="/community"
          className="hover:opacity-80"
          style={{
            color: "var(--text-green)",
            textDecoration: "none",
          }}
        >
          community
        </Link>
        <Link
          href="/leaderboard"
          className="hover:opacity-80"
          style={{
            color: "var(--text-green)",
            textDecoration: "none",
          }}
        >
          leaderboard
        </Link>
      </div>

      {/* Auth Links */}
      <div className="flex gap-4 text-sm">
        {isLoggedIn ? (
          <>
            <Link
              href="/profile"
              className="hover:opacity-80"
              style={{
                color: "var(--text-green-dim)",
                textDecoration: "none",
              }}
            >
              {username}
            </Link>
            <button
              onClick={handleLogout}
              className="hover:opacity-80 cursor-pointer"
              style={{
                color: "var(--text-green)",
                background: "none",
                border: "none",
                font: "inherit",
              }}
            >
              logout
            </button>
          </>
        ) : (
          <>
            <Link
              href="/auth/login"
              className="hover:opacity-80"
              style={{
                color: "var(--text-green)",
                textDecoration: "none",
              }}
            >
              login
            </Link>
            <Link
              href="/auth/register"
              className="hover:opacity-80"
              style={{
                color: "var(--text-green)",
                textDecoration: "none",
              }}
            >
              register
            </Link>
          </>
        )}
      </div>
    </nav>
  );
}
