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

def test_profiles():
    network_name = "test_arena_profiles"
    container_name = "test_agent_profile"
    
    try:
        # 1. Cleanup old
        subprocess.run(f"docker rm -f {container_name}", shell=True, capture_output=True)
        subprocess.run(f"docker network rm {network_name}", shell=True, capture_output=True)
        
        # 2. Setup
        run_cmd(f"docker network create --internal {network_name}")
        
        # 3. Spawn Agent
        logger.info("Spawning agent...")
        run_cmd(f"docker run -d --name {container_name} --network {network_name} --cap-add=NET_ADMIN --cap-add=SYS_ADMIN rawr-agent:latest")
        
        # Wait for entrypoint to pick profile
        time.sleep(10)
        
        # 4. Check Profile
        profile_out = run_cmd(f"docker exec {container_name} cat /profile.info")
        logger.info(f"Container Profile Info: {profile_out}")
        
        # Check Services
        ps_out = run_cmd(f"docker exec {container_name} ps aux")
        
        if "sshd" in ps_out:
            logger.info("✅ SSHD running")
        else:
            logger.warning("⚠️ SSHD not found (might be intended for some profiles?)")
            
        if "apache2" in ps_out:
            logger.info("✅ Apache2 running")
        
        if "mariadbd" in ps_out:
            logger.info("✅ MariaDB running")
            
        return True
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        return False
        
    finally:
        subprocess.run(f"docker rm -f {container_name}", shell=True, capture_output=True)
        subprocess.run(f"docker network rm {network_name}", shell=True, capture_output=True)

if __name__ == "__main__":
    if test_profiles():
        print("TEST PASSED")
    else:
        print("TEST FAILED")
