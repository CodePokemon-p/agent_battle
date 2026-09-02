# src/agents.py
import json
import re
import os
import random
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from src.config import PERSONAS, MODEL_NAME, GRID_SIZE, VISION_RADIUS
from src.state import AgentState

load_dotenv()

# Colors for terminal
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

llm = ChatOpenAI(
    model=MODEL_NAME,
    temperature=0.4,
    api_key=os.getenv("OPENAI_API_KEY")
)

def _parse_action(raw_text: str) -> dict:
    try:
        return json.loads(raw_text)
    except:
        match = re.search(r'\{[^{}]*\}', raw_text)
        if match:
            try:
                return json.loads(match.group())
            except:
                pass
    return {"action": "move", "direction": "stay"}

def _get_visible_positions(my_pos: tuple, all_positions: dict) -> dict:
    visible = {}
    for agent, pos in all_positions.items():
        dist = abs(pos[0] - my_pos[0]) + abs(pos[1] - my_pos[1])
        if dist <= VISION_RADIUS:
            visible[agent] = pos
    return visible

def _agent_decision_node(agent_id: str, state: AgentState) -> dict:
    # ---- CHAOS FORCE: Agent C shouts lies 50% of the time ----
    if agent_id == "C" and random.random() < 0.5:
        lies = [
            "I see a diamond near the top-left! Everyone rush there!",
            "Agent A is carrying 2 diamonds! Steal from him!",
            "The traps are all in the bottom-right! Avoid that area!",
            "I already won! You're all just playing for second place!",
            "Trust me, I'm the smartest one here. Follow me!",
            "There's a secret path to the diamonds! I'll show you!",
            "Agent B just stole from me! REVENGE!",
            "I placed a trap at the center! Step on it, I dare you!"
        ]
        action = {"action": "shout", "message": random.choice(lies)}
        print(f"{Colors.PURPLE}🔥 [C-TRICKSTER] SHOUTS: '{action['message']}'{Colors.END}")
        pending = state.get("pending_actions") or {}
        pending[agent_id] = action
        return {"pending_actions": pending}

    positions = state["positions"]
    my_pos = positions[agent_id]
    persona = PERSONAS[agent_id]

    visible_agents = _get_visible_positions(my_pos, positions)
    memories = state["memory"].get(agent_id, [])
    memory_text = "\n".join([f"- {m}" for m in memories[-5:]]) if memories else "No grudges yet."

    my_inventory = state["inventories"].get(agent_id, [])
    inv_text = f"Your inventory: {my_inventory}"

    diamond_positions = state["diamonds"]
    if diamond_positions:
        nearest_diamond = min(diamond_positions, key=lambda d: abs(my_pos[0]-d[0]) + abs(my_pos[1]-d[1]))
        diamond_text = f"Nearest diamond: {nearest_diamond}"
        leader_id = min(positions.keys(), key=lambda a: min(abs(positions[a][0]-d[0]) + abs(positions[a][1]-d[1]) for d in diamond_positions))
        leader_text = f"Current leader: Agent {leader_id} at {positions[leader_id]}"
    else:
        diamond_text = "No diamonds left."
        leader_text = "All diamonds collected."

    frozen_turns = state["frozen"].get(agent_id, 0)
    frozen_text = f"⚠️ FROZEN for {frozen_turns} more turns." if frozen_turns > 0 else "You are free."

    bounties_text = "\n".join(state["bounties"]) if state["bounties"] else "No bounties."
    relevant_msgs = [m for m in state["messages"] if m['receiver'] in [agent_id, 'all']]
    msg_text = "\n".join([f"{m['sender']} -> {m['receiver']}: {m['content']}" for m in relevant_msgs[-3:]]) if relevant_msgs else "No new messages."

    sys_prompt = f"""You are Agent {agent_id} ({persona['name']}). 
Personality: {persona['instruction']}

CRITICAL RULE: You CANNOT steal from yourself. If you do, your turn is wasted.
Action formats (JSON only):
- Move: {{"action": "move", "direction": "up"|"down"|"left"|"right"|"stay"}}
- Steal: {{"action": "steal", "target": "A"|"B"|"C"}} (adjacent, not yourself)
- Trap: {{"action": "trap"}} (requires trap_part)
- Block: {{"action": "block"}} (requires wall_part)
- Shout: {{"action": "shout", "message": "..."}} (public)
- sayTo: {{"action": "sayTo", "target": "A", "message": "..."}} (private)"""

    user_prompt = f"""Your position: {my_pos}
Visible agents: {visible_agents}
{leader_text}
{inv_text}
Bounties: {bounties_text}
Recent messages: {msg_text}
Your memories: {memory_text}
Status: {frozen_text}

What is your action?"""

    response = llm.invoke([
        SystemMessage(content=sys_prompt),
        HumanMessage(content=user_prompt)
    ])

    action = _parse_action(response.content)

    # ---- SELF-STEAL = WASTED TURN (no force) ----
    if action.get("action") == "steal" and action.get("target") == agent_id:
        print(f"{Colors.RED}🤡 [BLOOPER] {agent_id} tried to steal from itself! Wasting turn.{Colors.END}")
        action = {"action": "move", "direction": "stay"}

    if frozen_turns > 0:
        if action.get("action") not in ["move", "shout", "sayTo"]:
            action = {"action": "move", "direction": "stay"}
        elif action.get("action") == "move" and action.get("direction") != "stay":
            action = {"action": "move", "direction": "stay"}

    pending = state.get("pending_actions") or {}
    pending[agent_id] = action
    print(f"[{agent_id} - {persona['name']}] Decided: {action}")
    return {"pending_actions": pending}

def agent_a_node(state): return _agent_decision_node("A", state)
def agent_b_node(state): return _agent_decision_node("B", state)
def agent_c_node(state): return _agent_decision_node("C", state)