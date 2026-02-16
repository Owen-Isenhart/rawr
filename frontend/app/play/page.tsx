"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import NavBar from "@/components/NavBar";
import { Card, Button, Input } from "@/components/ui";
import { getAgents, getModels, createAgent, getProfile } from "@/lib/api";

interface Agent {
  id: string;
  name: string;
  system_prompt: string;
  temperature: number;
  base_model_id: string;
  created_at: string;
}

interface Model {
  id: string;
  ollama_tag: string;
  description: string;
}

export default function PlayPage() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [models, setModels] = useState<Model[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [profile, setProfile] = useState<any>(null);
  const router = useRouter();

  const [formData, setFormData] = useState({
    name: "",
    system_prompt: "",
    base_model_id: "",
    temperature: 0.7,
  });

  const [error, setError] = useState("");

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      router.push("/login");
      return;
    }

    loadData();
  }, [router]);

  const loadData = async () => {
    try {
      const [agentsData, modelsData, profileData] = await Promise.all([
        getAgents(),
        getModels(),
        getProfile(),
      ]);
      setAgents((agentsData as Agent[]) || []);
      setModels((modelsData as Model[]) || []);
      setProfile(profileData);
    } catch (err) {
      console.error("failed to load data:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateAgent = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (!formData.name || !formData.system_prompt || !formData.base_model_id) {
      setError("all fields required");
      return;
    }

    try {
      await createAgent(formData);
      setFormData({ name: "", system_prompt: "", base_model_id: "", temperature: 0.7 });
      setShowCreateForm(false);
      loadData();
    } catch (err: any) {
      setError(err.message || "failed to create agent");
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
              $ agents
            </h1>
            {profile && (
              <p
                className="text-sm"
                style={{ color: "var(--text-gray)" }}
              >
                &gt;&gt; welcome back, {profile.username}
              </p>
            )}
          </div>

          {/* Stats */}
          {profile && (
            <Card>
              <div className="grid grid-cols-4 gap-4 text-sm">
                <div>
                  <p
                    style={{ color: "var(--text-green-subtle)" }}
                  >
                    agents
                  </p>
                  <p
                    className="text-xl font-bold"
                    style={{ color: "var(--text-green)" }}
                  >
                    {agents.length}
                  </p>
                </div>
                <div>
                  <p
                    style={{ color: "var(--text-green-subtle)" }}
                  >
                    wins
                  </p>
                  <p
                    className="text-xl font-bold"
                    style={{ color: "var(--text-green)" }}
                  >
                    {profile.stats?.wins || 0}
                  </p>
                </div>
                <div>
                  <p
                    style={{ color: "var(--text-green-subtle)" }}
                  >
                    losses
                  </p>
                  <p
                    className="text-xl font-bold"
                    style={{ color: "var(--text-green)" }}
                  >
                    {profile.stats?.losses || 0}
                  </p>
                </div>
                <div>
                  <p
                    style={{ color: "var(--text-green-subtle)" }}
                  >
                    rank
                  </p>
                  <p
                    className="text-xl font-bold"
                    style={{ color: "var(--text-green)" }}
                  >
                    {profile.stats?.rank_points || 0}
                  </p>
                </div>
              </div>
            </Card>
          )}

          {/* Create Agent Form */}
          {showCreateForm && (
            <Card>
              <h2
                className="text-xl font-bold mb-6"
                style={{ color: "var(--text-green)" }}
              >
                $ create agent
              </h2>
              <form onSubmit={handleCreateAgent} className="space-y-4">
                <Input
                  label="agent name"
                  value={formData.name}
                  onChange={(e) =>
                    setFormData({ ...formData, name: e.target.value })
                  }
                  placeholder="my awesome agent"
                />

                <div>
                  <label
                    className="block text-sm mb-2"
                    style={{ color: "var(--text-green)" }}
                  >
                    model:
                  </label>
                  <select
                    value={formData.base_model_id}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        base_model_id: e.target.value,
                      })
                    }
                    className="w-full px-3 py-2 border rounded text-sm font-mono"
                    style={{
                      borderColor: "var(--text-green-subtle)",
                      backgroundColor: "var(--bg-darker)",
                      color: "var(--text-green)",
                    }}
                  >
                    <option value="">select model...</option>
                    {models.map((model) => (
                      <option key={model.id} value={model.id}>
                        {model.ollama_tag}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label
                    className="block text-sm mb-2"
                    style={{ color: "var(--text-green)" }}
                  >
                    system prompt:
                  </label>
                  <textarea
                    value={formData.system_prompt}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        system_prompt: e.target.value,
                      })
                    }
                    rows={4}
                    className="w-full px-3 py-2 border rounded text-sm font-mono"
                    style={{
                      borderColor: "var(--text-green-subtle)",
                      backgroundColor: "var(--bg-darker)",
                      color: "var(--text-green)",
                    }}
                    placeholder="you are a hacker who..."
                  />
                </div>

                <div>
                  <label
                    className="block text-sm mb-2"
                    style={{ color: "var(--text-green)" }}
                  >
                    temperature: {formData.temperature.toFixed(1)}
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="2"
                    step="0.1"
                    value={formData.temperature}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        temperature: parseFloat(e.target.value),
                      })
                    }
                    className="w-full"
                    style={{ accentColor: "var(--text-green)" }}
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
                    $ create
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
              $ create new agent
            </Button>
          )}

          {/* Agents List */}
          {loading ? (
            <p style={{ color: "var(--text-gray)" }}>loading agents...</p>
          ) : agents.length === 0 ? (
            <p style={{ color: "var(--text-gray)" }}>no agents yet</p>
          ) : (
            <div className="space-y-4">
              {agents.map((agent) => (
                <Card key={agent.id}>
                  <div className="flex justify-between items-start">
                    <div className="space-y-2">
                      <h3
                        className="text-lg font-bold"
                        style={{ color: "var(--text-green)" }}
                      >
                        {agent.name}
                      </h3>
                      <p
                        className="text-sm"
                        style={{ color: "var(--text-gray)" }}
                      >
                        {agent.system_prompt.substring(0, 100)}...
                      </p>
                      <p
                        className="text-xs"
                        style={{ color: "var(--text-green-subtle)" }}
                      >
                        temperature: {agent.temperature.toFixed(1)} | created:{" "}
                        {new Date(agent.created_at).toLocaleDateString()}
                      </p>
                    </div>
                    <div className="flex gap-2">
                      <Button variant="secondary" size="sm">
                        $ view
                      </Button>
                      <Button variant="danger" size="sm">
                        $ delete
                      </Button>
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
