-- SEED DATA FOR TESTING

-- 1. Create Dummy Users
INSERT INTO users (username, email, password_hash, bio) VALUES
('ghost_in_shell', 'ghost@arena.io', 'hash_pw_1', 'Specialist in stealth and persistence.'),
('root_overflow', 'root@arena.io', 'hash_pw_2', 'I only play for the root access.'),
('cyber_monk', 'monk@arena.io', 'hash_pw_3', 'Defense is the best offense.');

-- 2. Create User Stats (Initialize Leaderboard)
INSERT INTO user_stats (user_id, wins, rank_points)
SELECT id, FLOOR(RANDOM() * 50), FLOOR(RANDOM() * 1000) FROM users;

-- 3. Add Base Models (Physical Ollama Tags)
INSERT INTO base_models (ollama_tag, description, size_bytes) VALUES
('dolphin-llama3:latest', 'Uncensored general-purpose hacking model.', 4900000000),
('mistral-nemo:12b', 'High reasoning model for complex network puzzles.', 7500000000),
('deepseek-coder:6.7b', 'Specialized in exploit code generation.', 4000000000);

-- 4. Create Agent Configs (User Persona + Model)
INSERT INTO agent_configs (user_id, base_model_id, name, system_prompt) VALUES
((SELECT id FROM users WHERE username='ghost_in_shell'), 
 (SELECT id FROM base_models WHERE ollama_tag='dolphin-llama3:latest'), 
 'ShadowAgent', 'You are a stealthy agent. Prioritize nmap -sS and avoid noisy scans.'),
((SELECT id FROM users WHERE username='root_overflow'), 
 (SELECT id FROM base_models WHERE ollama_tag='deepseek-coder:6.7b'), 
 'Overflower', 'You are aggressive. Use Metasploit modules as soon as a port is found.');

-- 5. Forum Posts
INSERT INTO forum_posts (author_id, title, content, category) VALUES
((SELECT id FROM users WHERE username='cyber_monk'), 
 'Why Dolphin-Llama3 is better for SQLi', 
 'In my testing, the logic for blind SQL injection is much more consistent...', 
 'Model Discussion'),
((SELECT id FROM users WHERE username='root_overflow'), 
 'How to survive more than 5 minutes', 
 'Protecting your own SSH port is key. Here is a script I use...', 
 'Tactics');

-- 6. Forum Comments
INSERT INTO forum_comments (post_id, author_id, content) VALUES
((SELECT id FROM forum_posts LIMIT 1), 
 (SELECT id FROM users WHERE username='ghost_in_shell'), 
 'I agree, but Mistral-Nemo handles the bypasses better.');