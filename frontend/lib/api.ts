const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

interface RequestOptions extends RequestInit {
  throwOnError?: boolean;
}

export async function apiCall<T>(
  endpoint: string,
  options: RequestOptions = {}
): Promise<T> {
  const { throwOnError = true, ...fetchOptions } = options;
  
  const url = `${API_BASE_URL}${endpoint}`;
  
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  
  // Add existing headers
  if (fetchOptions.headers) {
    const existingHeaders = fetchOptions.headers as Record<string, string>;
    Object.assign(headers, existingHeaders);
  }
  
  // Add auth token if available
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
    
    // Handle authentication errors
    if (response.status === 401) {
      if (typeof window !== "undefined") {
        localStorage.removeItem("token");
        window.location.href = "/login";
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

export async function login(username: string, password: string) {
  const formData = new FormData();
  formData.append("username", username);
  formData.append("password", password);
  
  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: "POST",
    body: formData,
  });
  
  if (!response.ok) {
    throw new Error("login failed");
  }
  
  return response.json();
}

export async function register(
  username: string,
  email: string,
  password: string
) {
  return apiCall("/auth/register", {
    method: "POST",
    body: JSON.stringify({ username, email, password }),
  });
}

export async function getProfile() {
  return apiCall("/auth/me");
}

// Agent endpoints
export async function getAgents() {
  return apiCall("/agents/agents");
}

export async function getAgent(id: string) {
  return apiCall(`/agents/agents/${id}`);
}

export async function createAgent(data: {
  name: string;
  system_prompt: string;
  base_model_id: string;
  temperature: number;
}) {
  return apiCall("/agents/agents", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function updateAgent(id: string, data: Partial<any>) {
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

// Battle endpoints
export async function startBattle(data: {
  player_agents: Array<{ agent_id: string }>;
  opponent_agents: Array<{ agent_id: string }>;
}) {
  return apiCall("/battle/start", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function getBattleStatus(id: string) {
  return apiCall(`/battle/battles/${id}`);
}

export async function getBattleLogs(id: string, skip = 0, limit = 100) {
  return apiCall(
    `/battle/battles/${id}/logs?skip=${skip}&limit=${limit}`
  );
}

export async function getBattleLeaderboard(limit = 10) {
  return apiCall(`/battle/leaderboard?limit=${limit}`);
}

// Community endpoints
export async function getPosts(category?: string, skip = 0, limit = 20) {
  let url = "/community/posts?skip=" + skip + "&limit=" + limit;
  if (category) url += "&category=" + category;
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
    throwOnError: true,
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

export async function createComment(id: string, content: string) {
  return apiCall(`/community/posts/${id}/comments`, {
    method: "POST",
    body: JSON.stringify({ content }),
  });
}

export async function getCommunityLeaderboard(limit = 10) {
  return apiCall(`/community/leaderboard?limit=${limit}`);
}
