"use client";

import { useState, useEffect } from "react";
import NavBar from "@/components/NavBar";
import { Card } from "@/components/ui";
import { getCommunityLeaderboard } from "@/lib/api";

interface LeaderboardEntry {
  rank?: number;
  username: string;
  wins?: number;
  losses?: number;
  rank_points?: number;
  post_count?: number;
  total_likes?: number;
}

export default function LeaderboardPage() {
  const [communityLeaderboard, setCommunityLeaderboard] = useState<
    LeaderboardEntry[]
  >([]);
  const [activeTab, setActiveTab] = useState<"battle" | "community">("battle");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadLeaderboards();
  }, []);

  const loadLeaderboards = async () => {
    try {
      const communityData = await getCommunityLeaderboard(100);
      setCommunityLeaderboard((communityData as LeaderboardEntry[]) || []);
    } catch (err) {
      console.error("failed to load leaderboards:", err);
    } finally {
      setLoading(false);
    }
  };

  const leaderboard = communityLeaderboard;

  return (
    <>
      <NavBar />
      <main className="min-h-screen py-12 px-4">
        <div className="max-w-4xl mx-auto space-y-8">
          {/* Header */}
          <div>
            <h1
              className="text-3xl font-bold mb-2"
              style={{ color: "var(--text-green-bright)" }}
            >
              $ leaderboard
            </h1>
            <p
              className="text-sm"
              style={{ color: "var(--text-gray)" }}
            >
              &gt;&gt; top hackers
            </p>
          </div>

          {/* Tab Buttons */}
          {/* <div className="flex gap-2">
            <button
              onClick={() => setActiveTab("battle")}
              className="px-4 py-2 border text-sm font-mono"
              style={{
                borderColor: "var(--border-green)",
                backgroundColor:
                  activeTab === "battle"
                    ? "var(--text-green)"
                    : "transparent",
                color:
                  activeTab === "battle"
                    ? "var(--bg-dark)"
                    : "var(--text-green)",
              }}
            >
              battles
            </button>
            <button
              onClick={() => setActiveTab("community")}
              className="px-4 py-2 border text-sm font-mono"
              style={{
                borderColor: "var(--border-green)",
                backgroundColor:
                  activeTab === "community"
                    ? "var(--text-green)"
                    : "transparent",
                color:
                  activeTab === "community"
                    ? "var(--bg-dark)"
                    : "var(--text-green)",
              }}
            >
              community
            </button>
          </div> */}

          {/* Leaderboard Table */}
          {loading ? (
            <p style={{ color: "var(--text-gray)" }}>loading leaderboard...</p>
          ) : leaderboard.length === 0 ? (
            <p style={{ color: "var(--text-gray)" }}>
              no leaderboard data yet
            </p>
          ) : (
            <div className="space-y-2">
              {/* Header */}
              <Card>
                <div className="grid grid-cols-4 gap-4 text-sm font-bold">
                  <div style={{ color: "var(--text-green-subtle)" }}>rank</div>
                  <div style={{ color: "var(--text-green-subtle)" }}>
                    username
                  </div>
                  
                  <div style={{ color: "var(--text-green-subtle)" }}>
                        wins
                      </div>
                      <div style={{ color: "var(--text-green-subtle)" }}>
                        points
                      </div>
                </div>
              </Card>

              {/* Entries */}
              {leaderboard.map((entry, index) => (
                <Card key={entry.username}>
                  <div className="grid grid-cols-4 gap-4 text-sm items-center">
                    <div
                      style={{ color: "var(--text-green)" }}
                      className="font-bold text-lg"
                    >
                      #{index + 1}
                    </div>
                    <div style={{ color: "var(--text-green)" }}>
                      {entry.username}
                    </div>
                    <div style={{ color: "var(--text-green-dim)" }}>
                          {entry.wins || 0} wins
                        </div>
                        <div style={{ color: "var(--text-green-dim)" }}>
                          {entry.rank_points || 0} pts
                        </div>
                  </div>
                </Card>
              ))}
            </div>
          )}
        </div>
      </main>
    </>
  );
}
