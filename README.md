# Acto-Sphere

**Acto-Sphere** is a high-performance, polyglot modular ecosystem designed to demonstrate modern event-driven architecture. It integrates low-level system monitoring with high-level analytics, visualization, and cross-platform communication.

![Architecture Status](https://img.shields.io/badge/Architecture-Event--Driven-blueviolet)
![License](https://img.shields.io/badge/License-MIT-green)
![Docker](https://img.shields.io/badge/Docker-Compose-blue)

## 🚀 Project Overview

Acto-Sphere evolves the concept of a "modular monolith" into a distributed system. It uses specialized languages for specific tasks to maximize performance and maintainability:

*   **C++17:** Real-time filesystem monitoring (Watcher).
*   **Go:** High-concurrency log ingestion and message publishing.
*   **Rust:** Asynchronous analytics engine and database management.
*   **Node.js:** Fast, non-blocking API and Web Dashboard.
*   **Redis:** In-memory message broker (Pub/Sub) and caching layer.
*   **PostgreSQL:** Persistent relational storage.
*   **C# / .NET 6:** Secure AES-256 file encryption vault.
*   **Python:** Data schema validation (Pydantic/Pandas) and XML/CSV conversion.
*   **Kotlin:** Android client for remote monitoring.
*   **Ruby:** Orchestration and launcher scripts.

## 🏗 Architecture

The system operates on a **Producer-Consumer** model via Redis:

1.  **Monitor (C++)** detects file changes -> writes to local logs.
2.  **Ingestor (Go)** tails logs -> publishes to Redis Channel `file_events`.
3.  **Engine (Rust)** subscribes to Redis -> processes data -> writes to Postgres -> updates Redis Cache.
4.  **Dashboard (Node.js)** reads Redis Cache -> visualizes data in real-time.

## 📦 Installation

### Prerequisites
*   **Docker** & **Docker Compose** (Recommended)
*   *Optional (for local dev):* Go 1.21+, Rust 1.75+, Node 18+, Python 3.11+, .NET 6.0, GCC/Clang.

### Quick Start (Docker)
The easiest way to run the entire stack is using Docker Compose.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Ccropiropi/Acto_sphere.git
    cd Acto_sphere
    ```

2.  **Start the Ecosystem:**
    ```bash
    docker-compose up --build
    ```
    *This will build the Go, Rust, and Node images and start the database containers.*

3.  **Access the Dashboard:**
    Open your browser to: [http://localhost:3000/dashboard.html](http://localhost:3000/dashboard.html)

## 🔧 Usage

### 1. File Monitoring
The system monitors the `Acto-Sphere/dat` directory (or configured target). Create, modify, or delete files in the target folders to see real-time updates on the dashboard.

### 2. Manual Tools
You can use the Ruby launcher to manage individual components if running locally without Docker:
```bash
cd Acto-Sphere/rb
ruby acto_launcher.rb
```

### 3. Encryption Vault (C#)
To securely encrypt files:
```bash
cd Acto-Sphere/cs/ActoVault
dotnet run -- /path/to/your/secret.file
```

## 🤝 Contribution Guidelines

We welcome contributions! Please follow these steps:

1.  **Fork** the repository.
2.  Create a **Feature Branch** (`git checkout -b feature/AmazingFeature`).
3.  Commit your changes with clear messages.
4.  **Test** your changes (ensure `docker-compose up` still works).
5.  Push to the branch (`git push origin feature/AmazingFeature`).
6.  Open a **Pull Request**.

### Standards
*   **Code Style:** Follow the standard idioms for each language (PEP8 for Python, standard Go formatting, etc.).
*   **Commits:** Use the script `Acto-Sphere/scripts/auto_commit.sh` or write descriptive messages.

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.
