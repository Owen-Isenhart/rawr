FROM kalilinux/kali-rolling

# Prevent interactive prompts during install
ENV DEBIAN_FRONTEND=noninteractive

# Install essential hacking tools
RUN apt-get update && apt-get install -y \
    nmap \
    netcat-traditional \
    metasploit-framework \
    sqlmap \
    iputils-ping \
    curl \
    iproute2 \
    openssh-server \
    && apt-get clean

# Set a default workspace
WORKDIR /home/agent

# This container stays alive so the backend can 'exec' into it
CMD ["sleep", "infinity"]