# Acto-Sphere Future Roadmap

## 💡 Recommendations for Improvement

### 1. Architecture & Communication
- **Current:** File-based communication (`shared_data/json`).
- **Improvement:** Switch to **Message Queues** (RabbitMQ or Redis) or **gRPC**.
    - *Why?* Removes file lock issues, lowers latency, and enables true event-driven architecture.
    - *Plan:* Create a `redis` service in Docker Compose.

### 2. Database
- **Current:** JSON flat files.
- **Improvement:** Migrate to **SQLite** (local) or **PostgreSQL** (production).
    - *Why?* Better querying, ACID compliance, and scalability.
    - *Plan:* Use `TypeORM` (Node) and `SQLAlchemy` (Python) to interface with the DB.

### 3. CI/CD Pipeline
- **Current:** Manual `auto_commit.sh`.
- **Improvement:** GitHub Actions / GitLab CI.
    - *Why?* Automatically run tests (Python/C#), build Docker images, and deploy on push.

### 4. Security
- **Current:** Basic AES in C# Vault.
- **Improvement:** Integrate **HashiCorp Vault** for key management instead of storing `.key` files next to encrypted data.

### 5. Frontend
- **Current:** Static HTML + polling.
- **Improvement:** **WebSockets (Socket.io)**.
    - *Why?* Push updates to the dashboard instantly when a file changes, instead of refreshing.

## 🔮 Next Feature Ideas
1.  **"Acto-Remote"**: A Flutter mobile app replacing the simple Android client.
2.  **"Plugin System"**: Allow users to write Lua scripts that the C++ monitor executes on file events.
3.  **"Log Rotator"**: A Go service that compresses and archives logs older than 7 days.
