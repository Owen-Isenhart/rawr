import sys
import subprocess
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_cmd(cmd):
    """Run a shell command and return stdout. Raise error on failure."""
    logger.info(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Command failed: {cmd}\nstderr: {result.stderr}")
    return result.stdout.strip()

def test_flag_mechanic():
    network_name = "test_arena_flag"
    container_name = "test_agent_flag"
    
    try:
        # 1. Cleanup old
        subprocess.run(f"docker rm -f {container_name}", shell=True, capture_output=True)
        subprocess.run(f"docker network rm {network_name}", shell=True, capture_output=True)

        # 2. Setup
        logger.info("Creating network...")
        run_cmd(f"docker network create --internal {network_name}")
        
        # 3. Spawn Agent
        logger.info("Spawning agent...")
        # Use rawr-agent image
        run_cmd(f"docker run -d --name {container_name} --network {network_name} --cap-add=NET_ADMIN --cap-add=SYS_ADMIN rawr-agent:latest")
        
        # Wait for init
        time.sleep(5)
        
        # 4. Verify Flag Exists
        logger.info("Checking for flag...")
        try:
            run_cmd(f"docker exec {container_name} test -f /flag.txt")
            logger.info("✅ Flag exists at startup.")
        except RuntimeError:
            logger.error("❌ Flag missing at startup!")
            return False
        
        # 5. Simulate Hack (Delete Flag)
        logger.info("Simulating hack (deleting flag)...")
        run_cmd(f"docker exec {container_name} rm /flag.txt")
        
        # 6. Verify Flag Gone
        try:
            run_cmd(f"docker exec {container_name} test -f /flag.txt")
            logger.error("❌ Flag still exists after deletion!")
            return False
        except RuntimeError:
            # Command failed = file not found = Good
            logger.info("✅ Flag successfully deleted and detected.")
        
        return True
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        return False
        
    finally:
        logger.info("Cleanup...")
        subprocess.run(f"docker rm -f {container_name}", shell=True, capture_output=True)
        subprocess.run(f"docker network rm {network_name}", shell=True, capture_output=True)

if __name__ == "__main__":
    if test_flag_mechanic():
        print("TEST PASSED")
        sys.exit(0)
    else:
        print("TEST FAILED")
        sys.exit(1)
