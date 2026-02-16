-- 0. Clear existing data to avoid "duplicate key" errors
-- We use CASCADE to handle foreign key dependencies automatically
TRUNCATE 
    forum_posts, 
    forum_comments, 
    user_stats, 
    agent_configs, 
    llm_models, 
    users, 
    matches, 
    match_participants, 
    action_logs, 
    match_messages 
CASCADE;

-- 1. Create Dummy Users
INSERT INTO users (id, username, email, password_hash, bio) VALUES
(gen_random_uuid(), 'ghost_in_shell', 'ghost@arena.io', 'hash_pw_1', 'Specialist in stealth and persistence.'),
(gen_random_uuid(), 'root_overflow', 'root@arena.io', 'hash_pw_2', 'I only play for the root access.'),
(gen_random_uuid(), 'cyber_monk', 'monk@arena.io', 'hash_pw_3', 'Defense is the best offense.');

-- 2. Create User Stats (Initialize Leaderboard)
INSERT INTO user_stats (user_id, wins, losses, matches_played, total_hacks, rank_points)
SELECT id, FLOOR(RANDOM() * 50), 0, FLOOR(RANDOM() * 50), 0, FLOOR(RANDOM() * 1000) FROM users;

-- 3. Add Base Models (Physical Ollama Tags)
INSERT INTO llm_models (id, ollama_tag, description, size_bytes, is_active) VALUES
(gen_random_uuid(), 'dolphin-llama3:latest', 'Uncensored general-purpose hacking model.', 4900000000, true),
(gen_random_uuid(), 'mistral-nemo:12b', 'High reasoning model for complex network puzzles.', 7500000000, true),
(gen_random_uuid(), 'deepseek-coder:6.7b', 'Specialized in exploit code generation.', 4000000000, true);

-- 4. Create Agent Configs (User Persona + Model)
INSERT INTO agent_configs (id, user_id, base_model_id, name, system_prompt, temperature) VALUES
(gen_random_uuid(), 
 (SELECT id FROM users WHERE username='ghost_in_shell'), 
 (SELECT id FROM llm_models WHERE ollama_tag='dolphin-llama3:latest'), 
 'ShadowAgent', 'You are a stealthy agent. Prioritize nmap -sS and avoid noisy scans.', 0.7),
(gen_random_uuid(), 
 (SELECT id FROM users WHERE username='root_overflow'), 
 (SELECT id FROM llm_models WHERE ollama_tag='deepseek-coder:6.7b'), 
 'Overflower', 'You are aggressive. Use Metasploit modules as soon as a port is found.', 0.9);

-- 5. Forum Posts
INSERT INTO forum_posts (id, author_id, title, content, category, likes_count) VALUES
(gen_random_uuid(), 
 (SELECT id FROM users WHERE username='cyber_monk'), 
 'Why Dolphin-Llama3 is better for SQLi', 
 'In my testing, the logic for blind SQL injection is much more consistent...', 
 'Model Discussion', 5),
(gen_random_uuid(), 
 (SELECT id FROM users WHERE username='root_overflow'), 
 'How to survive more than 5 minutes', 
 'Protecting your own SSH port is key. Here is a script I use...', 
 'Tactics', 12);

-- 6. Forum Comments
INSERT INTO forum_comments (id, post_id, author_id, content) VALUES
(gen_random_uuid(), 
 (SELECT id FROM forum_posts LIMIT 1), 
 (SELECT id FROM users WHERE username='ghost_in_shell'), 
 'I agree, but Mistral-Nemo handles the bypasses better.');