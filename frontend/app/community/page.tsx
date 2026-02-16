"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import NavBar from "@/components/NavBar";
import { Card, Button, Input } from "@/components/ui";
import { getPosts, createPost, getProfile } from "@/lib/api";

interface Post {
  id: string;
  title: string;
  content: string;
  category: string;
  likes_count: number;
  author_id: string;
  created_at: string;
  author?: {
    username: string;
  };
}

const CATEGORIES = ["general", "strategies", "tools", "showcase"];

export default function CommunityPage() {
  const [posts, setPosts] = useState<Post[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState("general");
  const [profile, setProfile] = useState<any>(null);
  const router = useRouter();

  const [formData, setFormData] = useState({
    title: "",
    content: "",
    category: "general",
  });

  const [error, setError] = useState("");

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      router.push("/auth/login");
      return;
    }

    loadData();
  }, [router, selectedCategory]);

  const loadData = async () => {
    try {
      const [postsData, profileData] = await Promise.all([
        getPosts(selectedCategory !== "all" ? selectedCategory : undefined),
        getProfile(),
      ]);
      setPosts((postsData as Post[]) || []);
      setProfile(profileData);
    } catch (err) {
      console.error("failed to load posts:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreatePost = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (!formData.title || !formData.content) {
      setError("title and content required");
      return;
    }

    try {
      await createPost(formData);
      setFormData({ title: "", content: "", category: "general" });
      setShowCreateForm(false);
      loadData();
    } catch (err: any) {
      setError(err.message || "failed to create post");
    }
  };

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
              $ community
            </h1>
            <p
              className="text-sm"
              style={{ color: "var(--text-gray)" }}
            >
              &gt;&gt; share strategies and discuss hacking techniques
            </p>
          </div>

          {/* Category Filter */}
          <div className="flex gap-2 flex-wrap">
            <Button
              variant={selectedCategory === "all" ? "primary" : "secondary"}
              onClick={() => setSelectedCategory("all")}
              className="text-xs"
            >
              all
            </Button>
            {CATEGORIES.map((cat) => (
              <Button
                key={cat}
                variant={
                  selectedCategory === cat ? "primary" : "secondary"
                }
                onClick={() => setSelectedCategory(cat)}
                className="text-xs"
              >
                {cat}
              </Button>
            ))}
          </div>

          {/* Create Post Form */}
          {showCreateForm && (
            <Card>
              <h2
                className="text-xl font-bold mb-6"
                style={{ color: "var(--text-green)" }}
              >
                $ new post
              </h2>
              <form onSubmit={handleCreatePost} className="space-y-4">
                <Input
                  label="title"
                  value={formData.title}
                  onChange={(e) =>
                    setFormData({ ...formData, title: e.target.value })
                  }
                  placeholder="share your knowledge..."
                />

                <div>
                  <label
                    className="block text-sm mb-2"
                    style={{ color: "var(--text-green)" }}
                  >
                    category:
                  </label>
                  <select
                    value={formData.category}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        category: e.target.value,
                      })
                    }
                    className="w-full px-3 py-2 border rounded text-sm font-mono"
                    style={{
                      borderColor: "var(--text-green-subtle)",
                      backgroundColor: "var(--bg-darker)",
                      color: "var(--text-green)",
                    }}
                  >
                    {CATEGORIES.map((cat) => (
                      <option key={cat} value={cat}>
                        {cat}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label
                    className="block text-sm mb-2"
                    style={{ color: "var(--text-green)" }}
                  >
                    content:
                  </label>
                  <textarea
                    value={formData.content}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        content: e.target.value,
                      })
                    }
                    rows={6}
                    className="w-full px-3 py-2 border rounded text-sm font-mono"
                    style={{
                      borderColor: "var(--text-green-subtle)",
                      backgroundColor: "var(--bg-darker)",
                      color: "var(--text-green)",
                    }}
                    placeholder="write your post here..."
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

                <div className="flex gap-4">
                  <Button variant="primary" type="submit">
                    $ post
                  </Button>
                  <Button
                    variant="secondary"
                    onClick={() => setShowCreateForm(false)}
                  >
                    $ cancel
                  </Button>
                </div>
              </form>
            </Card>
          )}

          {/* Create Button */}
          {!showCreateForm && (
            <Button
              variant="primary"
              onClick={() => setShowCreateForm(true)}
              className="w-full"
            >
              $ create new post
            </Button>
          )}

          {/* Posts List */}
          {loading ? (
            <p style={{ color: "var(--text-gray)" }}>loading posts...</p>
          ) : posts.length === 0 ? (
            <p style={{ color: "var(--text-gray)" }}>no posts yet</p>
          ) : (
            <div className="space-y-4">
              {posts.map((post) => (
                <Card key={post.id}>
                  <div>
                    <div className="flex justify-between items-start mb-3">
                      <div>
                        <h3
                          className="text-lg font-bold"
                          style={{ color: "var(--text-green)" }}
                        >
                          {post.title}
                        </h3>
                        <p
                          className="text-xs mt-1"
                          style={{ color: "var(--text-green-subtle)" }}
                        >
                          by {post.author?.username || "anonymous"} in{" "}
                          {post.category} •{" "}
                          {new Date(post.created_at).toLocaleDateString()}
                        </p>
                      </div>
                      <p
                        className="text-sm"
                        style={{ color: "var(--text-green-dim)" }}
                      >
                        ♥ {post.likes_count}
                      </p>
                    </div>
                    <p
                      className="text-sm"
                      style={{ color: "var(--text-gray)" }}
                    >
                      {post.content.substring(0, 200)}...
                    </p>
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
