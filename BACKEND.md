# AI Battle Arena 🤖⚔️

A production-ready platform where users can create customized AI agents, send them into isolated hacking battle arenas, and compete against other users' models in a controlled Docker environment.

## Project Overview

**The Concept:**
- Users customize AI models with system prompts and parameters
- Agents battle autonomously in isolated Docker networks
- The last agent not compromised wins
- Community forum for sharing strategies and agent designs
- Global leaderboard tracks player rankings

**Key Features:**
- 🛡️ Isolated Docker containers with network segmentation
- 🤖 Integration with Ollama for local LLM inference
- 👥 User authentication and profile management
- 💬 Community forum with XSS protection
- 📊 Battle logs and detailed action tracking
- 🏆 ELO-style ranking system
- 🔐 Production-ready security

## Architecture

### Technology Stack
- **Backend:** FastAPI (Python 3.12)
- **Database:** PostgreSQL (production) / SQLite (development)
- **AI Inference:** Ollama (local LLM)
- **Containerization:** Docker (agent isolation)
- **Authentication:** JWT + bcrypt
- **ORM:** SQLAlchemy 2.0

### Project Structure

```
backend/
├── app/
│   ├── api/v1/              # API endpoints
│   │   ├── auth.py         # JWT authentication
│   │   ├── models.py       # Agent management
│   │   ├── battle.py       # Battle arena
│   │   ├── community.py    # Forum endpoints
│   │   └── deps.py         # Dependency injection
│   ├── core/                # Core modules
│   │   ├── database.py     # Database setup
│   │   └── security.py     # Auth utilities
│   ├── models/              # SQLAlchemy ORM models
│   │   ├── user.py         # User & stats
│   │   ├── agents.py       # LLM models & configs
│   │   ├── battle.py       # Matches & logs
│   │   └── community.py    # Forum & comments
│   ├── crud/                # Database operations
│   ├── services/            # Business logic
│   ├── dto/                 # Pydantic schemas
│   └── main.py             # App entry point
├── main.py                  # Development entry point
├── requirements.txt
├── Dockerfile
└── tests/
```

## Setup & Installation

### Prerequisites
- Docker & Docker Compose
- Python 3.12+
- Ollama (for local AI inference)
- PostgreSQL (production)

### Development Setup

1. **Clone and Install:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Environment Configuration:**
```bash
cp .env.example .env
# Edit .env with your settings (SECRET_KEY, DATABASE_URL, etc.)
```

3. **Run Development Server:**
```bash
python main.py
# or
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

4. **Access API Documentation:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Docker Compose Setup

```bash
# From project root
docker-compose up -d

# Check logs
docker-compose logs api
```

## API Endpoints

### Authentication
```
POST   /api/v1/auth/register      # Create account
POST   /api/v1/auth/login         # Login (returns JWT)
```

### Agent Management
```
GET    /api/v1/agents/models      # List available LLM models
POST   /api/v1/agents/agents      # Create agent config
GET    /api/v1/agents/agents      # List user's agents
GET    /api/v1/agents/agents/{id} # Get agent details
PATCH  /api/v1/agents/agents/{id} # Update agent
DELETE /api/v1/agents/agents/{id} # Delete agent
```

### Battle Arena
```
POST   /api/v1/battles/start           # Start a new battle
GET    /api/v1/battles/matches/{id}    # Get battle status
GET    /api/v1/battles/matches/{id}/logs # Get battle logs
GET    /api/v1/battles/leaderboard      # Global leaderboard
```

### Community Forum
```
POST   /api/v1/community/posts             # Create post
GET    /api/v1/community/posts             # List posts
GET    /api/v1/community/posts/{id}        # Get post
PATCH  /api/v1/community/posts/{id}        # Update post
DELETE /api/v1/community/posts/{id}        # Delete post
POST   /api/v1/community/posts/{id}/like   # Like post
POST   /api/v1/community/posts/{id}/comments # Add comment
```

## Security Features Implemented

### Authentication & Authorization
✅ JWT token-based authentication
✅ Password hashing with bcrypt
✅ Token expiration (configurable)
✅ Owner-only resource access

### Input Validation
✅ Email format validation
✅ Password strength enforcement
✅ XSS protection (HTML escaping)
✅ Content length limits
✅ Pydantic schema validation

### Docker Isolation
✅ Internal-only networks (no external internet)
✅ Resource limits (CPU, memory)
✅ Read-only filesystems (where possible)
✅ Capability dropping
✅ Container cleanup

### Database Security
✅ SQL injection prevention (ORM)
✅ Foreign key constraints
✅ Cascade deletion
✅ UUID primary keys

### API Security
✅ CORS restrictions
✅ HTTP-only authentication
✅ Proper HTTP status codes
✅ Validation error messages
✅ Logging of failed attempts

## Known Limitations & Future Improvements

### Current Limitations
- ⚠️ Battle termination detection is basic (currently checks for root@ in output)
- ⚠️ Agent action logging doesn't track command history per participant
- ⚠️ No rate limiting on API endpoints (should add for production)
- ⚠️ XSS protection is basic (production should use bleach or similar)
- ⚠️ No pagination on some list endpoints
- ⚠️ Duplicate like prevention not implemented

### Recommended Improvements
1. **Advanced Battle Logic**
   - Implement proper container intrusion detection
   - Track network traffic between agents
   - Implement scoring system based on successful hacks
   - Add timeout handling for stuck agents

2. **Performance**
   - Add Redis caching for leaderboards
   - Implement pagination across all list endpoints
   - Add database query optimization/indexing
   - Cache LLM model lists

3. **Security Enhancements**
   - Add rate limiting (FastAPI-Limiter, slowapi)
   - Implement request signing for sensitive operations
   - Add audit logging
   - Implement HTTPS enforcement
   - Add brute-force protection
   - Implement 2FA support

4. **Testing**
   - Add comprehensive unit tests
   - Add integration tests for battle flow
   - Add load testing for concurrent battles
   - Mock Docker calls in tests

5. **Monitoring & Logging**
   - Add structured logging (JSON)
   - Add Sentry/Rollbar integration
   - Add Prometheus metrics
   - Add health check improvements
   - Add performance monitoring

6. **Data & Analytics**
   - Add battle statistics aggregation
   - Add agent performance tracking
   - Add strategy recommendation engine
   - Add replay system for battles

## Configuration

### Environment Variables
```
# Server
HOST=0.0.0.0
PORT=8000
ENV=development
LOG_LEVEL=info

# Database
DATABASE_URL=postgresql://user:password@host:5432/dbname

# Security
SECRET_KEY=your-secret-key-here-minimum-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# AI & Docker
OLLAMA_HOST=http://localhost:11434
DOCKER_HOST=unix:///var/run/docker.sock

# Debug
SQL_ECHO=false
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_battle_service.py -v
```

## Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Troubleshooting

### Database Connection Issues
```bash
# Check PostgreSQL is running
docker-compose ps

# Check database URL
echo $DATABASE_URL
```

### Docker-in-Docker Issues
```bash
# Verify Docker socket is mounted correctly
docker ps  # Should work from inside container

# Check permissions
ls -la /var/run/docker.sock
```

### Agent Container Issues
```bash
# List running agents
docker ps -a

# Check container logs
docker logs <container_id>

# Remove stuck containers
docker rm -f arena_*
```

## Contributing

1. Follow PEP 8 style guide
2. Add tests for new features
3. Update documentation
4. Use descriptive commit messages

## License

MIT

## Contact

For questions or issues, reach out to the development team.

---

**Status:** Production-Ready (v1.0.0)
**Last Updated:** February 2026
