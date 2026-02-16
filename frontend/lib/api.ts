const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

// --- Types & Interfaces ---

interface RequestOptions extends RequestInit {
  throwOnError?: boolean;
}

export interface AgentConfig {
  name: string;
  system_prompt: string;
  base_model_id: string;
  temperature: number;
}

export interface BattleRequest {
  player_agents: Array<{ agent_id: string }>;
  opponent_agents: Array<{ agent_id: string }>;
}

// --- Base API Helper ---

export async function apiCall<T>(
  endpoint: string,
  options: RequestOptions = {}
): Promise<T> {
  const { throwOnError = true, ...fetchOptions } = options;
  
  const url = `${API_BASE_URL}${endpoint}`;
  
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  
  if (fetchOptions.headers) {
    const existingHeaders = fetchOptions.headers as Record<string, string>;
    Object.assign(headers, existingHeaders);
  }
  
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("token");
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
  }
  
  try {
    const response = await fetch(url, {
      ...fetchOptions,
      headers,
    });
    
    if (response.status === 401) {
      if (typeof window !== "undefined") {
        localStorage.removeItem("token");
        window.location.href = "/auth/login";
      }
    }
    
    if (!response.ok && throwOnError) {
      const error = await response.json().catch(() => ({ 
        detail: "Unknown error" 
      }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }
    
    if (response.status === 204) {
      return null as T;
    }
    
    return response.json() as Promise<T>;
  } catch (error) {
    if (throwOnError) {
      throw error;
    }
    return null as T;
  }
}

// --- Authentication ---

export async function login(username: string, password: string) {
  // Updated to JSON instead of FormData
  return apiCall<{
    access_token: string;
    token_type: string;
    user: {
      id: string;
      username: string;
      email: string;
    };
  }>("/auth/login", {
    method: "POST",
    body: JSON.stringify({ username, password }),
  });
}

export async function register(
  username: string,
  email: string,
  password: string
) {
  return apiCall<{
    id: string;
    username: string;
    email: string;
  }>("/auth/register", {
    method: "POST",
    body: JSON.stringify({ username, email, password }),
  });
}

/**
 * Get the current authenticated user's profile.
 */
export async function getProfile() {
  return apiCall<{
    id: string;
    username: string;
    email: string;
    bio?: string;
    avatar_url?: string;
  }>("/auth/me");
}

// --- Agent Management ---

export async function getAgents() {
  return apiCall("/agents/agents");
}

export async function getAgent(id: string) {
  return apiCall(`/agents/agents/${id}`);
}

export async function createAgent(data: AgentConfig) {
  return apiCall("/agents/agents", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function updateAgent(id: string, data: Partial<AgentConfig>) {
  return apiCall(`/agents/agents/${id}`, {
    method: "PATCH",
    body: JSON.stringify(data),
  });
}

export async function deleteAgent(id: string) {
  return apiCall(`/agents/agents/${id}`, {
    method: "DELETE",
  });
}

export async function getModels() {
  return apiCall("/agents/models");
}

// --- Battle Arena ---

export async function startBattle(data: BattleRequest) {
  // Corrected path: /battles/start
  return apiCall("/battles/start", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function getBattleStatus(matchId: string) {
  // Corrected path: /battles/matches/{match_id}
  return apiCall(`/battles/matches/${matchId}`);
}

export async function getBattleLogs(matchId: string, skip = 0, limit = 100) {
  // Corrected path: /battles/matches/{match_id}/logs
  return apiCall(
    `/battles/matches/${matchId}/logs?skip=${skip}&limit=${limit}`
  );
}

export async function getBattleLeaderboard(limit = 10) {
  // Corrected path: /battles/leaderboard
  return apiCall(`/battles/leaderboard?limit=${limit}`);
}

// --- Community Forum ---

export async function getPosts(category?: string, skip = 0, limit = 20) {
  let url = `/community/posts?skip=${skip}&limit=${limit}`;
  if (category) url += `&category=${category}`;
  return apiCall(url);
}

export async function getPost(id: string) {
  return apiCall(`/community/posts/${id}`);
}

export async function createPost(data: {
  title: string;
  content: string;
  category: string;
}) {
  return apiCall("/community/posts", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function updatePost(id: string, data: Partial<any>) {
  return apiCall(`/community/posts/${id}`, {
    method: "PATCH",
    body: JSON.stringify(data),
  });
}

export async function deletePost(id: string) {
  return apiCall(`/community/posts/${id}`, {
    method: "DELETE",
  });
}

export async function likePost(id: string) {
  return apiCall(`/community/posts/${id}/like`, {
    method: "POST",
  });
}

export async function createComment(postId: string, content: string) {
  return apiCall(`/community/posts/${postId}/comments`, {
    method: "POST",
    body: JSON.stringify({ content }),
  });
}

export async function getCommunityLeaderboard(limit = 10) {
  return apiCall(`/community/leaderboard?limit=${limit}`);
}