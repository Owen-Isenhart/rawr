-- ENABLE UUID EXTENSION (Recommended for security/scalability)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. USERS & IDENTITY
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    avatar_url TEXT,
    bio TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. LEADERBOARD / STATS
-- This tracks cumulative performance for the leaderboard
CREATE TABLE user_stats (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    wins INTEGER DEFAULT 0,
    matches_played INTEGER DEFAULT 0,
    total_hacks INTEGER DEFAULT 0, -- Successful root access gained
    rank_points INTEGER DEFAULT 0, -- For ELO or similar ranking
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. THE "BRAINS" (OLLAMA MODELS)
CREATE TABLE base_models (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ollama_tag VARCHAR(100) UNIQUE NOT NULL, -- e.g. "dolphin-llama3:latest"
    description TEXT,
    size_bytes BIGINT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. THE "AGENTS" (USER CONFIGURATIONS)
CREATE TABLE agent_configs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    base_model_id UUID REFERENCES base_models(id) ON DELETE SET NULL,
    name VARCHAR(100) NOT NULL,
    system_prompt TEXT NOT NULL,
    temperature DECIMAL(3,2) DEFAULT 0.7,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 5. MATCHES (THE ARENA)
CREATE TABLE matches (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    creator_id UUID REFERENCES users(id),
    status VARCHAR(20) DEFAULT 'lobby', -- lobby, ongoing, completed
    winner_id UUID REFERENCES users(id),
    start_time TIMESTAMP WITH TIME ZONE,
    end_time TIMESTAMP WITH TIME ZONE
);

-- 6. MATCH PARTICIPANTS
CREATE TABLE match_participants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    match_id UUID REFERENCES matches(id) ON DELETE CASCADE,
    agent_config_id UUID REFERENCES agent_configs(id),
    container_id VARCHAR(100), -- The ephemeral Docker ID
    internal_ip VARCHAR(45),
    is_alive BOOLEAN DEFAULT TRUE,
    eliminated_at TIMESTAMP WITH TIME ZONE
);

-- 7. IN-BATTLE CHAT
CREATE TABLE match_messages (
    id BIGSERIAL PRIMARY KEY,
    match_id UUID REFERENCES matches(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id),
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 8. FORUM: POSTS
CREATE TABLE forum_posts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    author_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    category VARCHAR(50), -- e.g. "Model Discussion", "Tactics", "General"
    likes_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 9. FORUM: COMMENTS
CREATE TABLE forum_comments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    post_id UUID REFERENCES forum_posts(id) ON DELETE CASCADE,
    author_id UUID REFERENCES users(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    parent_id UUID REFERENCES forum_comments(id), -- For nested replies
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 10. ACTION LOGS (For AI behavior tracking)
CREATE TABLE action_logs (
    id BIGSERIAL PRIMARY KEY,
    participant_id UUID REFERENCES match_participants(id) ON DELETE CASCADE,
    command TEXT NOT NULL,
    output TEXT,
    was_successful BOOLEAN,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- INDEXES FOR PERFORMANCE
CREATE INDEX idx_user_stats_points ON user_stats(rank_points DESC);
CREATE INDEX idx_forum_posts_category ON forum_posts(category);
CREATE INDEX idx_match_messages_match_id ON match_messages(match_id);