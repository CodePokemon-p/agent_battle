# src/orchestrator.py
import random
import copy
import json
import sys
from langgraph.graph import StateGraph, END
from src.state import AgentState
from src.agents import agent_a_node, agent_b_node, agent_c_node

class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

def apply_actions(state: AgentState) -> dict:
    print(f"\n{Colors.BOLD}=== TURN {state['turn']+1} / {state['max_turns']} ==={Colors.END}")

    pending = state.get("pending_actions", {})
    positions = state["positions"].copy()
    inventories = {k: v.copy() for k, v in state["inventories"].items()}
    diamonds = state["diamonds"].copy()
    traps = state["traps"].copy()
    walls = state["walls"].copy()
    frozen = state["frozen"].copy()
    memory = {k: v.copy() for k, v in state["memory"].items()}
    messages = state["messages"].copy()
    bounties = state["bounties"].copy()

    deltas = {"up": (-1,0), "down": (1,0), "left": (0,-1), "right": (0,1), "stay": (0,0)}

    intended_moves = {}
    steal_attempts = []
    shouts = []
    private_msgs = []

    # Parse actions
    for agent, action in pending.items():
        if frozen.get(agent, 0) > 0:
            if action.get("action") == "shout":
                shouts.append((agent, action.get("message", "...")))
            elif action.get("action") == "sayTo":
                private_msgs.append((agent, action.get("target"), action.get("message")))
            else:
                intended_moves[agent] = positions[agent]
            continue

        act_type = action.get("action", "move")
        if act_type == "move":
            dx, dy = deltas.get(action.get("direction", "stay"), (0,0))
            x, y = positions[agent]
            target = (x+dx, y+dy)
            if 0 <= target[0] < 10 and 0 <= target[1] < 10 and target not in walls:
                intended_moves[agent] = target
            else:
                intended_moves[agent] = positions[agent]
        elif act_type == "steal":
            target = action.get("target")
            if target and target in positions and target != agent:
                if abs(positions[agent][0] - positions[target][0]) + abs(positions[agent][1] - positions[target][1]) == 1:
                    steal_attempts.append((agent, target))
                else:
                    intended_moves[agent] = positions[agent]
            else:
                intended_moves[agent] = positions[agent]
        elif act_type == "trap":
            if "trap_part" in inventories.get(agent, []):
                traps[positions[agent]] = agent
                inventories[agent].remove("trap_part")
            intended_moves[agent] = positions[agent]
        elif act_type == "block":
            if "wall_part" in inventories.get(agent, []):
                walls.add(positions[agent])
                inventories[agent].remove("wall_part")
            intended_moves[agent] = positions[agent]
        elif act_type == "shout":
            shouts.append((agent, action.get("message", "...")))
            intended_moves[agent] = positions[agent]
        elif act_type == "sayTo":
            private_msgs.append((agent, action.get("target"), action.get("message")))
            intended_moves[agent] = positions[agent]
        else:
            intended_moves[agent] = positions[agent]

    # Resolve collisions & traps
    final_positions = positions.copy()
    for agent, target in intended_moves.items():
        if target in traps and traps[target] != agent:
            frozen[agent] = frozen.get(agent, 0) + 2
            print(f"{Colors.CYAN}💥 [DRAMA] {agent} stepped on {traps[target]}'s TRAP at {target}! Frozen for 2 turns!{Colors.END}")
            memory[agent] = memory.get(agent, []) + [f"Stepped on a trap at {target} placed by {traps[target]}"]
            messages.append({"sender": "ORCHESTRATOR", "receiver": "all", "content": f"💥 {agent} stepped on a trap!", "turn": state["turn"]})
            del traps[target]
        blocked = False
        for other, other_target in intended_moves.items():
            if other != agent:
                if other_target == positions[other] and positions[other] == target:
                    blocked = True
                if intended_moves.get(other) == target and other != agent:
                    blocked = True
        if target in walls:
            blocked = True
        final_positions[agent] = positions[agent] if blocked else target

    # Resolve steals
    for thief, victim in steal_attempts:
        if final_positions[thief] == final_positions[victim]:
            if inventories.get(victim):
                stolen_item = random.choice(inventories[victim])
                inventories[victim].remove(stolen_item)
                inventories[thief] = inventories.get(thief, []) + [stolen_item]
                print(f"{Colors.RED}⚡ [DRAMA] {thief} STOLE {stolen_item} from {victim}!{Colors.END}")
                memory[victim] = memory.get(victim, []) + [f"{thief} stole {stolen_item} from me"]
                memory[thief] = memory.get(thief, []) + [f"I stole {stolen_item} from {victim}"]
                messages.append({"sender": "ORCHESTRATOR", "receiver": "all", "content": f"⚡ {thief} stole from {victim}!", "turn": state["turn"]})

    # Collect diamonds
    for agent, pos in final_positions.items():
        if pos in diamonds:
            diamonds.remove(pos)
            inventories[agent] = inventories.get(agent, []) + ["diamond"]
            print(f"{Colors.YELLOW}💎 [DRAMA] {agent} found a DIAMOND at {pos}!{Colors.END}")
            messages.append({"sender": "ORCHESTRATOR", "receiver": "all", "content": f"💎 {agent} found a diamond!", "turn": state["turn"]})
            memory[agent] = memory.get(agent, []) + [f"Found a diamond at {pos}"]

    # Process chat
    for sender, msg in shouts:
        print(f"{Colors.BLUE}📢 [CHAT] {sender} SHOUTS: '{msg}'{Colors.END}")
        messages.append({"sender": sender, "receiver": "all", "content": msg, "turn": state["turn"]})
    for sender, target, msg in private_msgs:
        print(f"{Colors.PURPLE}🤫 [PRIVATE] {sender} -> {target}: '{msg}'{Colors.END}")
        messages.append({"sender": sender, "receiver": target, "content": msg, "turn": state["turn"]})

    # Random bounties
    if random.random() < 0.15 and state["turn"] > 5:
        bounties.append("💰 BOUNTY: Steal from the current diamond holder for +5 points!")
    if len(bounties) > 5:
        bounties = bounties[-5:]

    # Decrement frozen
    for agent in list(frozen.keys()):
        frozen[agent] -= 1
        if frozen[agent] <= 0:
            del frozen[agent]

    # NO early winner – let game run full turns
    winner = None

    # Log history
    history = state.get("history", [])
    history.append({
        "turn": state["turn"],
        "positions": final_positions,
        "inventories": copy.deepcopy(inventories),
        "actions": pending,
        "diamonds_left": diamonds,
        "messages": messages[-5:]
    })

    # ======== 🔥 NEW: Print state for live viewer ========
    # ======== STATE: PRINT FOR LIVE VIEWER ========
    state_json = {
        "turn": state["turn"] + 1,
        "max_turns": state["max_turns"],
        "positions": final_positions,
        "diamonds_left": diamonds,
        "inventories": inventories,
        "messages": messages[-3:],
        "frozen": frozen,
        "winner": None
    }
    print(f"STATE:{json.dumps(state_json)}", flush=True)  # <--- flush=True

    return {
        "positions": final_positions,
        "inventories": inventories,
        "diamonds": diamonds,
        "traps": traps,
        "walls": walls,
        "frozen": frozen,
        "memory": memory,
        "messages": messages,
        "pending_actions": {},
        "turn": state["turn"] + 1,
        "history": history,
        "bounties": bounties,
        "winner": None,
        "game_over": False
    }

def should_continue(state: AgentState) -> str:
    if state["turn"] >= state["max_turns"]:
        return "evaluate"
    return "agents"

def build_graph():
    builder = StateGraph(AgentState)
    builder.add_node("agent_a", agent_a_node)
    builder.add_node("agent_b", agent_b_node)
    builder.add_node("agent_c", agent_c_node)
    builder.add_node("apply_actions", apply_actions)
    builder.set_entry_point("agent_a")
    builder.add_edge("agent_a", "agent_b")
    builder.add_edge("agent_b", "agent_c")
    builder.add_edge("agent_c", "apply_actions")
    builder.add_conditional_edges("apply_actions", should_continue, {"agents": "agent_a", "evaluate": END})
    return builder.compile()