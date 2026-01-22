# --- Stage 1: Build C# Vault ---
FROM mcr.microsoft.com/dotnet/sdk:6.0 AS cs-builder
WORKDIR /app
COPY Acto-Sphere/cs/ActoVault/ ./ 
RUN dotnet publish -c Release -o /out

# --- Stage 2: Build Go TUI ---
FROM golang:1.21 AS go-builder
WORKDIR /app
COPY Acto-Sphere/go/ ./ 
# Build a static binary
RUN CGO_ENABLED=0 go build -o acto-monitor main.go

# --- Stage 3: Final Polyglot Runtime ---
FROM ubuntu:22.04

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# 1. Install System Dependencies & Runtimes
# We install: Python3, Node.js (via curl), Ruby, Java (OpenJDK), and .NET Runtime dependencies
RUN apt-get update && apt-get install -u -y \
    curl \
    build-essential \
    python3 \
    python3-pip \
    ruby-full \
    openjdk-17-jdk \
    wget \
    git \
    && rm -rf /var/lib/apt/lists/*

# 2. Install Node.js 18
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs

# 3. Install .NET 6 Runtime (Microsoft Repo)
RUN wget https://packages.microsoft.com/config/ubuntu/22.04/packages-microsoft-prod.deb -O packages-microsoft-prod.deb \
    && dpkg -i packages-microsoft-prod.deb \
    && rm packages-microsoft-prod.deb \
    && apt-get update \
    && apt-get install -y dotnet-runtime-6.0

# 4. Setup Working Directory
WORKDIR /app/Acto-Sphere

# 5. Copy Source Code
# We copy the specific language folders
COPY Acto-Sphere/cpp ./cpp
COPY Acto-Sphere/py ./py
COPY Acto-Sphere/js ./js
COPY Acto-Sphere/rb ./rb
COPY Acto-Sphere/sh ./sh
COPY Acto-Sphere/jav ./jav

# Create data directories
RUN mkdir -p dat/json dat/logs vault_storage cpp/target_folder py/target_folder

# 6. Install Language Dependencies

# Python
RUN pip3 install -r py/requirements.txt

# Node.js
WORKDIR /app/Acto-Sphere/js
RUN npm install --production

# Ruby (Launchy is optional in headless server, but we install it)
WORKDIR /app/Acto-Sphere/rb
RUN bundle install || echo "Bundle install skipped, using system ruby"

# 7. Compile C++ (Directly in final stage as it is small and needs local libs)
WORKDIR /app/Acto-Sphere/cpp
RUN g++ -std=c++17 monitor.cpp -o monitor

# 8. Copy Artifacts from Builders
COPY --from=cs-builder /out /app/Acto-Sphere/cs/bin/Release/net6.0/publish
COPY --from=go-builder /app/acto-monitor /app/Acto-Sphere/go/acto-monitor

# 9. Environment Setup
ENV NODE_ENV=production
ENV PORT=3000
EXPOSE 3000
EXPOSE 8080

# Return to root of the Acto-Sphere folder for the launcher
WORKDIR /app/Acto-Sphere/rb

# 10. Default Command
# We default to the Launcher, but in a non-interactive mode usually.
# However, since Acto_Launcher is a menu, we might prefer running the Node server directly for 'production'.
# For now, let's run the launcher, but user should use "docker run -it"
CMD ["ruby", "acto_launcher.rb"]
