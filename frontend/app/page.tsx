import Link from "next/link";
import NavBar from "@/components/NavBar";

export default function Home() {
  const dinosaur = [
    "               __ ",
    "              / _)",
    "     _/\\/\\/\\_/ /  ",
    "   _|         /   ",
    " _|  (  | (  |    ",
    "/__.-'|_|--|_|    ",
  ];

  return (
    <>
      <NavBar />
      <main className="min-h-screen py-12 px-4">
        <div className="max-w-4xl mx-auto flex flex-col items-center justify-center gap-12">
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
            <p
              style={{ color: "var(--text-green)" }}
            >
              &gt;&gt; create customizable ai agents
            </p>
            <p
              style={{ color: "var(--text-green)" }}
            >
              &gt;&gt; design system prompts and parameters
            </p>
            <p
              style={{ color: "var(--text-green)" }}
            >
              &gt;&gt; battle agents in isolated docker arenas
            </p>
            <p
              style={{ color: "var(--text-green)" }}
            >
              &gt;&gt; share strategies in community forum
            </p>
            <p
              style={{ color: "var(--text-green)" }}
            >
              &gt;&gt; climb the global leaderboard
            </p>
          </div>
        </div>
      </main>
    </>
  );
}
