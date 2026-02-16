"use client";

import { useState, useRef, useEffect, KeyboardEvent } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import NavBar from "@/components/NavBar";

type HistoryItem = {
  command: string;
  output: React.ReactNode;
};

export default function Home() {
  const router = useRouter();
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [input, setInput] = useState("");
  
  const inputRef = useRef<HTMLInputElement>(null);
  const terminalEndRef = useRef<HTMLDivElement>(null);

  // Available "directories" based on your project structure
  const availablePages = ["play", "community", "leaderboard", "profile", "login", "register"];

  const dinosaur = [
    "               __ ",
    "              / _)",
    "     _/\\/\\/\\_/ /  ",
    "   _|         /   ",
    " _|  (  | (  |    ",
    "/__.-'|_|--|_|    ",
  ];

  // Auto-scroll the terminal to the bottom whenever history changes
  useEffect(() => {
    if (terminalEndRef.current) {
      terminalEndRef.current.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }
  }, [history]);

  // Keep focus on the hidden input when clicking anywhere inside the terminal box
  const focusInput = () => {
    inputRef.current?.focus();
  };

  const processCommand = (cmdStr: string): React.ReactNode => {
    const trimmed = cmdStr.trim();
    if (!trimmed) return null;

    const args = trimmed.split(" ").filter(Boolean);
    const command = args[0].toLowerCase();

    switch (command) {
      case "help":
        return (
          <div className="flex flex-col space-y-1">
            <span>Available commands:</span>
            <span className="ml-4">ls      - list available pages</span>
            <span className="ml-4">cd      - navigate to a page (e.g., 'cd play')</span>
            <span className="ml-4">clear   - clear terminal history</span>
            <span className="ml-4">whoami  - display current user info</span>
            <span className="ml-4">rawr    - summon the dinosaur</span>
            <span className="ml-4">help    - show this help message</span>
          </div>
        );
      
      case "ls":
        return (
          <div className="flex gap-4 flex-wrap">
            {availablePages.map((page) => (
              <span key={page} style={{ color: "var(--text-green-bright, #00ff00)" }}>
                {page}/
              </span>
            ))}
          </div>
        );

      case "cd":
        const target = args[1];
        if (!target || target === "~") {
          return <span>already at home directory</span>;
        }

        const cleanTarget = target.replace(/\/$/, "");

        if (availablePages.includes(cleanTarget)) {
          router.push(`/${cleanTarget}`);
          return <span className="animate-pulse">navigating to /{cleanTarget}...</span>;
        } else if (cleanTarget === "..") {
          return <span>permission denied</span>;
        } else {
          return <span>cd: {target}: No such file or directory</span>;
        }

      case "whoami":
        return <span>guest_user</span>;

      case "rawr":
        return (
          <pre className="font-mono whitespace-pre-wrap text-xs">
            {dinosaur.join("\n")}
          </pre>
        );

      default:
        return <span>{command}: command not found. Type 'help' to see available commands.</span>;
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      const trimmedInput = input.trim();
      
      if (trimmedInput.toLowerCase() === "clear") {
        setHistory([]);
      } else if (trimmedInput) {
        const output = processCommand(trimmedInput);
        setHistory((prev) => [...prev, { command: input, output }]);
      }
      
      setInput("");
    }
  };

  return (
    <>
      <NavBar />
      <main className="min-h-screen py-12 px-4">
        <div className="max-w-4xl mx-auto flex flex-col items-center justify-center gap-12">
          
          {/* --- ORIGINAL UI CONTENT --- */}
          
          {/* ASCII Art */}
          <pre
            className="text-sm font-mono whitespace-pre-wrap text-center"
            style={{ color: "var(--text-green)" }}
          >
            {dinosaur.join("\n")}
          </pre>

          {/* Title */}
          <div className="text-center space-y-4">
            <h1
              className="text-3xl font-bold"
              style={{ color: "var(--text-green-bright)" }}
            >
              root access: wipe royale
            </h1>
            <p
              className="text-sm"
              style={{ color: "var(--text-gray)" }}
            >
              compete with ai agents in hacking battles
            </p>
          </div>

          {/* CTA Buttons */}
          <div className="flex gap-4 flex-wrap justify-center">
            <Link
              href="/play"
              className="px-6 py-3 text-sm font-mono border"
              style={{
                color: "var(--bg-dark)",
                backgroundColor: "var(--text-green)",
                borderColor: "var(--text-green)",
              }}
            >
              $ play
            </Link>
            <Link
              href="/community"
              className="px-6 py-3 text-sm font-mono border hover:opacity-80"
              style={{
                color: "var(--text-green)",
                borderColor: "var(--text-green)",
                backgroundColor: "transparent",
              }}
            >
              $ community
            </Link>
            <Link
              href="/leaderboard"
              className="px-6 py-3 text-sm font-mono border hover:opacity-80"
              style={{
                color: "var(--text-green)",
                borderColor: "var(--text-green)",
                backgroundColor: "transparent",
              }}
            >
              $ leaderboard
            </Link>
          </div>

          {/* Info Section */}
          <div
            className="w-full max-w-2xl px-6 py-4 border rounded text-sm space-y-3"
            style={{
              borderColor: "var(--text-green-subtle)",
              backgroundColor: "rgba(0, 255, 0, 0.02)",
            }}
          >
            <p style={{ color: "var(--text-green)" }}>
              &gt;&gt; create customizable ai agents
            </p>
            <p style={{ color: "var(--text-green)" }}>
              &gt;&gt; design system prompts and parameters
            </p>
            <p style={{ color: "var(--text-green)" }}>
              &gt;&gt; battle agents in isolated docker arenas
            </p>
            <p style={{ color: "var(--text-green)" }}>
              &gt;&gt; share strategies in community forum
            </p>
            <p style={{ color: "var(--text-green)" }}>
              &gt;&gt; climb the global leaderboard
            </p>
          </div>

          {/* --- NEW TERMINAL COMPONENT --- */}
          <div 
            className="w-full max-w-2xl border rounded font-mono text-sm cursor-text flex flex-col"
            style={{
              borderColor: "var(--text-green-subtle)",
              backgroundColor: "rgba(0, 0, 0, 0.4)",
              color: "var(--text-green)",
              height: "300px" // Fixed height so the terminal scrolls internally
            }}
            onClick={focusInput}
          >
            {/* Terminal Header Bar (Optional, for aesthetics) */}
            <div 
              className="w-full px-4 py-1 border-b flex items-center"
              style={{ borderColor: "var(--text-green-subtle)", backgroundColor: "rgba(0, 255, 0, 0.05)" }}
            >
              <span className="text-xs" style={{ color: "var(--text-gray)" }}>terminal - rawr@rawr:~</span>
            </div>

            {/* Terminal Body */}
            <div className="p-4 flex-grow overflow-y-auto custom-scrollbar">
              <div className="mb-4">
                <p style={{ color: "var(--text-gray)" }}>
                  Interactive terminal ready. Type 'help' for commands.
                </p>
              </div>

              {/* Terminal History */}
              <div className="space-y-2 mb-2">
                {history.map((item, index) => (
                  <div key={index} className="space-y-1">
                    <div className="flex gap-2">
                      <span style={{ color: "var(--text-green-bright)" }}>rawr@rawr:~$</span>
                      <span>{item.command}</span>
                    </div>
                    {item.output && (
                      <div className="text-gray-300 ml-4">
                        {item.output}
                      </div>
                    )}
                  </div>
                ))}
              </div>

              {/* Active Input Line */}
              <div className="flex gap-2 items-center">
                <span style={{ color: "var(--text-green-bright)" }}>rawr@rawr:~$</span>
                <input
                  ref={inputRef}
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={handleKeyDown}
                  className="flex-grow bg-transparent border-none outline-none focus:ring-0 p-0"
                  style={{ color: "inherit" }}
                  autoComplete="off"
                  spellCheck="false"
                />
              </div>
              
              {/* Invisible div to track the bottom of the terminal */}
              <div ref={terminalEndRef} />
            </div>
          </div>

        </div>
      </main>
    </>
  );
}