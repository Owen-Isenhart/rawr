"""
Docker service for spawning and managing isolated agent containers.
"""
import docker
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class DockerService:
    """Manages Docker containers for agent execution."""

    def __init__(self):
        try:
            self.client = docker.from_env()
            # Test connection
            self.client.ping()
            logger.info("Docker client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to connect to Docker: {e}")
            raise RuntimeError(f"Docker connection failed: {str(e)}")

    def create_network(self, network_name: str, internal: bool = True):
        """
        Create an isolated Docker network for the battle.
        
        Args:
            network_name: Name of the network
            internal: If True, no external internet access
        
        Returns:
            Docker network object
        """
        try:
            network = self.client.networks.create(
                network_name,
                driver="bridge",
                opts={"internal": str(internal).lower()}
            )
            logger.info(f"Created Docker network: {network_name}")
            return network
        except docker.errors.APIError as e:
            if "already exists" in str(e):
                return self.client.networks.get(network_name)
            logger.error(f"Failed to create network {network_name}: {e}")
            raise

    def spawn_agent_container(self, agent_name: str, network_name: str, ip_address: Optional[str] = None):
        """
        Create an isolated Kali container for a hacking agent.
        
        Args:
            agent_name: Name for the container
            network_name: Docker network to connect to
            ip_address: Specific IP to assign (optional)
        
        Returns:
            Docker container object
        """
        try:
            # Network configuration with optional static IP
            net_config = {"Target": network_name}
            if ip_address:
                net_config["IPAddress"] = ip_address
            
            container = self.client.containers.run(
                image="kalilinux/kali-rolling",
                name=agent_name,
                network=network_name,
                detach=True,
                tty=True,
                cap_add=["NET_ADMIN", "SYS_ADMIN"],  # Required for hacking tools
                cap_drop=["ALL"],  # Drop all others for security
                read_only=True,  # Filesystem read-only by default
                tmpfs=["/tmp", "/run"],  # Temporary filesystems for runtime
                cpu_quota=100000,  # Limit CPU
                mem_limit="512m",  # Limit memory
                command="sleep infinity"
            )
            
            logger.info(f"Spawned container {agent_name}: {container.id[:12]}")
            return container
            
        except docker.errors.ImageNotFound:
            logger.error(f"Docker image not found: kalilinux/kali-rolling")
            raise RuntimeError("Required Docker image not available")
        except docker.errors.APIError as e:
            logger.error(f"Failed to spawn container {agent_name}: {e}")
            raise

    def execute_hacking_command(self, container_id: str, cmd: str) -> str:
        """
        Execute a command inside an agent container.
        
        Args:
            container_id: Container ID or name
            cmd: Command to execute
        
        Returns:
            Command output as string
        """
        try:
            container = self.client.containers.get(container_id)
            exit_code, output = container.exec_run(
                cmd,
                stdout=True,
                stderr=True,
                timeout=30
            )
            
            output_str = output.decode("utf-8", errors="ignore")
            
            if exit_code != 0:
                logger.debug(f"Command failed with exit code {exit_code}: {cmd}")
            
            return output_str
            
        except docker.errors.NotFound:
            logger.error(f"Container not found: {container_id}")
            raise RuntimeError(f"Container {container_id} not found")
        except docker.errors.APIError as e:
            logger.error(f"Failed to execute command in {container_id}: {e}")
            raise

    def cleanup_container(self, container_id: str, force: bool = True):
        """
        Stop and remove a container.
        
        Args:
            container_id: Container ID or name
            force: Force stop if running
        """
        try:
            container = self.client.containers.get(container_id)
            container.stop(timeout=5)
            container.remove(force=force)
            logger.info(f"Cleaned up container {container_id[:12]}")
        except docker.errors.NotFound:
            logger.warning(f"Container not found for cleanup: {container_id}")
        except docker.errors.APIError as e:
            logger.error(f"Failed to cleanup container {container_id}: {e}")
            # Don't raise - cleanup should be best-effort

    def cleanup_network(self, network_name: str):
        """
        Remove a Docker network.
        
        Args:
            network_name: Name of network to remove
        """
        try:
            network = self.client.networks.get(network_name)
            network.remove()
            logger.info(f"Removed network {network_name}")
        except docker.errors.NotFound:
            logger.warning(f"Network not found for cleanup: {network_name}")
        except docker.errors.APIError as e:
            logger.error(f"Failed to remove network {network_name}: {e}")
            # Don't raise - cleanup should be best-effort

    def get_container_info(self, container_id: str) -> dict:
        """Get information about a running container."""
        try:
            container = self.client.containers.get(container_id)
            return {
                "id": container.id,
                "name": container.name,
                "status": container.status,
                "ip_address": container.attrs.get("NetworkSettings", {}).get("IPAddress")
            }
        except docker.errors.NotFound:
            logger.error(f"Container not found: {container_id}")
            return {}
