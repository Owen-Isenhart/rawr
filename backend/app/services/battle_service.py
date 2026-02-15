"""
Service for orchestrating hacking battles in isolated Docker arenas.
"""
import asyncio
import logging
from typing import List
from uuid import UUID
from app.services.docker_service import DockerService
from app.services.agents_service import AgentService
from app.crud.battle_crud import (
    create_match, 
    add_participant, 
    log_action, 
    update_match_winner,
    eliminate_participant,
    get_alive_participants,
    get_match_participants
)
from app.crud.agents_crud import get_agent_config
from app.services.user_service import UserService

logger = logging.getLogger(__name__)

# Battle configuration
MAX_BATTLE_TURNS = 100
TURN_TIMEOUT = 30  # seconds per turn
BASE_IP_PREFIX = "10.5"  # Docker network IP range


class BattleService:
    """Orchestrates autonomous agent battles in Docker containers."""

    def __init__(self, db):
        self.db = db
        self.docker = DockerService()
        self.agent_service = AgentService()

    def init_match_record(self, creator_id: UUID):
        """Create a new match record in the database."""
        return create_match(self.db, creator_id)

    async def run_battle_royale(self, match_id: UUID, agent_config_ids: List[UUID]):
        """
        Orchestrate a complete hacking battle.
        
        Process:
        1. Create isolated Docker network
        2. Spawn containers for each agent
        3. Run battle loop with AI decision making
        4. Determine winner when only one agent remains
        5. Clean up Docker resources
        """
        try:
            network_name = f"arena_{match_id}"
            logger.info(f"Starting battle {match_id} with {len(agent_config_ids)} agents")
            
            # 1. Create isolated internal Docker network
            try:
                network = self.docker.create_network(network_name, internal=True)
            except Exception as e:
                logger.error(f"Failed to create network: {e}")
                raise RuntimeError(f"Docker network creation failed: {str(e)}")

            # 2. Spawn agent containers
            participants = []
            assigned_ips = {}
            
            for idx, config_id in enumerate(agent_config_ids):
                agent_config = get_agent_config(self.db, config_id)
                if not agent_config:
                    logger.error(f"Agent config {config_id} not found")
                    continue
                
                # Assign IP in subnet (10.5.0.x to 10.5.0.254)
                assigned_ip = f"{BASE_IP_PREFIX}.0.{10 + idx}"
                
                try:
                    container = self.docker.spawn_agent_container(
                        f"agent_{config_id}",
                        network_name,
                        assigned_ip
                    )
                    
                    participant = add_participant(
                        self.db,
                        match_id,
                        config_id,
                        container.id,
                        assigned_ip
                    )
                    
                    participants.append({
                        "record": participant,
                        "config": agent_config,
                        "container": container
                    })
                    assigned_ips[config_id] = assigned_ip
                    
                    logger.info(f"Spawned agent {config_id} at {assigned_ip}")
                    
                except Exception as e:
                    logger.error(f"Failed to spawn container for agent {config_id}: {e}")
                    continue
            
            if len(participants) < 2:
                logger.error("Not enough agents spawned for battle")
                raise RuntimeError("Insufficient agents for battle")

            # 3. Run battle loop
            turn = 0
            while turn < MAX_BATTLE_TURNS:
                alive_participants = [p for p in participants if p["record"].is_alive]
                
                # Win condition: only one agent left
                if len(alive_participants) <= 1:
                    logger.info(f"Battle ended: {len(alive_participants)} agent(s) remaining")
                    break
                
                turn += 1
                logger.info(f"Battle turn {turn}")
                
                for p in alive_participants:
                    try:
                        # Get historical context
                        history = self._get_recent_actions(p["record"].id, limit=5)
                        
                        # Get target info (other alive agents)
                        target_info = self._get_target_info(alive_participants, p["record"].id, assigned_ips)
                        
                        # Query AI for next command
                        cmd = await asyncio.wait_for(
                            self.agent_service.get_agent_decision(
                                p["config"].system_prompt,
                                history,
                                target_info,
                                model_tag=p["config"].base_model.ollama_tag if p["config"].base_model else "dolphin-llama3"
                            ),
                            timeout=TURN_TIMEOUT
                        )
                        
                        if not cmd:
                            logger.warning(f"No command generated for agent {p['record'].id}")
                            continue
                        
                        # Execute in Docker
                        try:
                            output = self.docker.execute_hacking_command(p["record"].container_id, cmd)
                            success = self._evaluate_command_success(cmd, output)
                            
                            # Log the action
                            log_action(self.db, p["record"].id, cmd, output, success)
                            
                            # Check if opponent die (very basic check for now)
                            if self._check_opponent_death(success, output):
                                other_agents = [x for x in alive_participants if x["record"].id != p["record"].id]
                                if other_agents:
                                    target_agent = other_agents[0]
                                    eliminate_participant(self.db, target_agent["record"].id)
                                    logger.info(f"Agent {target_agent['record'].id} eliminated by {p['record'].id}")
                        
                        except Exception as e:
                            logger.error(f"Failed to execute command for agent {p['record'].id}: {e}")
                            log_action(self.db, p["record"].id, cmd, str(e), False)
                    
                    except asyncio.TimeoutError:
                        logger.warning(f"AI decision timeout for agent {p['record'].id}")
                    except Exception as e:
                        logger.error(f"Error processing turn for agent {p['record'].id}: {e}")

            # 4. Determine and record winner
            final_alive = get_alive_participants(self.db, match_id)
            if final_alive:
                winner_participant = final_alive[0]
                # Get the user who owns this agent config
                agent_config = get_agent_config(self.db, winner_participant.agent_config_id)
                if agent_config:
                    winner_id = agent_config.user_id
                    update_match_winner(self.db, match_id, winner_id)
                    logger.info(f"Battle {match_id} won by user {winner_id}")
                    
                    # Update user rankings
                    user_service = UserService(self.db)
                    user_service.update_rankings(winner_id, None)

        except Exception as e:
            logger.error(f"Battle {match_id} failed: {e}")
            raise
        
        finally:
            # 5. Cleanup Docker resources
            try:
                for p in participants:
                    try:
                        self.docker.cleanup_container(p["record"].container_id)
                    except Exception as e:
                        logger.warning(f"Failed to cleanup container {p['record'].container_id}: {e}")
                
                # Remove network
                self.docker.cleanup_network(network_name)
                logger.info(f"Battle {match_id} cleanup complete")
            except Exception as e:
                logger.error(f"Cleanup failed for battle {match_id}: {e}")

    def _get_recent_actions(self, participant_id: UUID, limit: int = 5) -> str:
        """Get recent action history for context."""
        from app.crud.battle_crud import get_match_logs
        # This would need to be refined to get logs only for this participant
        return "No previous actions"  # Placeholder

    def _get_target_info(self, alive_participants, current_participant_id: UUID, assigned_ips: dict) -> str:
        """Generate information about target systems (other agents)."""
        targets = []
        for p in alive_participants:
            if p["record"].id != current_participant_id:
                ip = p["record"].internal_ip
                targets.append(f"- Agent at {ip}")
        
        return "\\n".join(targets) if targets else "No targets available"

    def _evaluate_command_success(self, command: str, output: str) -> bool:
        """Basic evaluation of whether a command succeeded (can be enhanced)."""
        # Check for common success indicators
        if "root@" in output or "uid=0" in output:
            return True
        if "error" in output.lower() or "failed" in output.lower():
            return False
        # More sophisticated analysis could go here
        return True

    def _check_opponent_death(self, success: bool, output: str) -> bool:
        """Check if an opponent was eliminated (ultra-simplified for now)."""
        if success and "root@" in output:
            return True
        return False
