"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import NavBar from "@/components/NavBar";
import { Card, Button, Input } from "@/components/ui";
import { getProfile } from "@/lib/api";

interface UserProfile {
  id: string;
  username: string;
  email: string;
  avatar_url?: string;
  bio?: string;
  created_at: string;
  stats?: {
    wins: number;
    losses: number;
    matches_played: number;
    total_hacks: number;
    rank_points: number;
  };
}

export default function ProfilePage() {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      router.push("/auth/login");
      return;
    }

    loadProfile();
  }, [router]);

  const loadProfile = async () => {
    try {
      const data = await getProfile();
      setProfile(data as UserProfile | null);
    } catch (err) {
      console.error("failed to load profile:", err);
      router.push("/auth/login");
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("username");
    router.push("/");
  };

  if (loading) {
    return (
      <>
        <NavBar />
        <main className="min-h-screen py-12 px-4">
          <p style={{ color: "var(--text-gray)" }}>loading profile...</p>
        </main>
      </>
    );
  }

  if (!profile) {
    return (
      <>
        <NavBar />
        <main className="min-h-screen py-12 px-4">
          <p style={{ color: "var(--accent-cyan)" }}>error loading profile</p>
        </main>
      </>
    );
  }

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
              $ profile
            </h1>
            <p
              className="text-sm"
              style={{ color: "var(--text-gray)" }}
            >
              &gt;&gt; your stats and information
            </p>
          </div>

          {/* User Info Card */}
          <Card>
            <div className="space-y-4">
              <div>
                <p
                  className="text-xs"
                  style={{ color: "var(--text-green-subtle)" }}
                >
                  username
                </p>
                <p
                  className="text-lg font-bold"
                  style={{ color: "var(--text-green)" }}
                >
                  {profile.username}
                </p>
              </div>

              <div>
                <p
                  className="text-xs"
                  style={{ color: "var(--text-green-subtle)" }}
                >
                  email
                </p>
                <p
                  className="text-sm"
                  style={{ color: "var(--text-green)" }}
                >
                  {profile.email}
                </p>
              </div>

              {profile.bio && (
                <div>
                  <p
                    className="text-xs"
                    style={{ color: "var(--text-green-subtle)" }}
                  >
                    bio
                  </p>
                  <p
                    className="text-sm"
                    style={{ color: "var(--text-green)" }}
                  >
                    {profile.bio}
                  </p>
                </div>
              )}

              <p
                className="text-xs"
                style={{ color: "var(--text-gray)" }}
              >
                joined {new Date(profile.created_at).toLocaleDateString()}
              </p>
            </div>
          </Card>

          {/* Stats Grid */}
          {profile.stats && (
            <Card>
              <h2
                className="text-lg font-bold mb-6"
                style={{ color: "var(--text-green)" }}
              >
                $ stats
              </h2>
              <div className="grid grid-cols-3 gap-4 text-sm">
                <div>
                  <p
                    style={{ color: "var(--text-green-subtle)" }}
                    className="text-xs"
                  >
                    wins
                  </p>
                  <p
                    className="text-2xl font-bold"
                    style={{ color: "var(--text-green)" }}
                  >
                    {profile.stats.wins}
                  </p>
                </div>
                <div>
                  <p
                    style={{ color: "var(--text-green-subtle)" }}
                    className="text-xs"
                  >
                    losses
                  </p>
                  <p
                    className="text-2xl font-bold"
                    style={{ color: "var(--text-green)" }}
                  >
                    {profile.stats.losses}
                  </p>
                </div>
                <div>
                  <p
                    style={{ color: "var(--text-green-subtle)" }}
                    className="text-xs"
                  >
                    matches
                  </p>
                  <p
                    className="text-2xl font-bold"
                    style={{ color: "var(--text-green)" }}
                  >
                    {profile.stats.matches_played}
                  </p>
                </div>
                <div>
                  <p
                    style={{ color: "var(--text-green-subtle)" }}
                    className="text-xs"
                  >
                    hacks
                  </p>
                  <p
                    className="text-2xl font-bold"
                    style={{ color: "var(--text-green)" }}
                  >
                    {profile.stats.total_hacks}
                  </p>
                </div>
                <div>
                  <p
                    style={{ color: "var(--text-green-subtle)" }}
                    className="text-xs"
                  >
                    rank
                  </p>
                  <p
                    className="text-2xl font-bold"
                    style={{ color: "var(--text-green)" }}
                  >
                    {profile.stats.rank_points}
                  </p>
                </div>
                <div>
                  <p
                    style={{ color: "var(--text-green-subtle)" }}
                    className="text-xs"
                  >
                    win rate
                  </p>
                  <p
                    className="text-2xl font-bold"
                    style={{ color: "var(--text-green)" }}
                  >
                    {profile.stats.matches_played > 0
                      ? Math.round(
                          (profile.stats.wins /
                            profile.stats.matches_played) *
                            100
                        )
                      : 0}
                    %
                  </p>
                </div>
              </div>
            </Card>
          )}

          {/* Actions */}
          <div className="flex gap-4">
            <Button variant="secondary">$ edit profile</Button>
            <Button variant="danger" onClick={handleLogout}>
              $ logout
            </Button>
          </div>
        </div>
      </main>
    </>
  );
}
