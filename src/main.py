# src/main.py
import os
import json
from datetime import datetime
from src.state import AgentState
from src.config import GRID_SIZE, MAX_TURNS, START_POSITIONS, DIAMOND_POSITIONS
from src.orchestrator import build_graph
from src.evaluator import evaluate_and_eliminate
from src.visualize import create_animation

def run_simulation():
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    run_dir = f"runs/{timestamp}"
    os.makedirs(run_dir, exist_ok=True)
    log_path = f"{run_dir}/run_log.json"
    gif_path = f"{run_dir}/race_replay.gif"

    print(f"🎬 Recording match to: {run_dir}")

    state = AgentState(
        positions=START_POSITIONS.copy(),
        inventories={"A": ["trap_part", "wall_part"], "B": ["trap_part", "wall_part"], "C": ["trap_part", "wall_part"]},
        diamonds=DIAMOND_POSITIONS.copy(),
        traps={},
        walls=set(),
        turn=0,
        max_turns=MAX_TURNS,
        history=[],
        pending_actions={},
        messages=[],
        memory={"A": [], "B": [], "C": []},
        bounties=[],
        frozen={},
        winner=None,
        game_over=False
    )

    graph = build_graph()
    print("🚦 Starting the Dirty Race...")
    final_state = graph.invoke(state)

    eval_result = evaluate_and_eliminate(final_state)
    final_state.update(eval_result)

    log_data = {
        "config": {"grid_size": GRID_SIZE, "max_turns": MAX_TURNS, "diamonds": DIAMOND_POSITIONS, "start_positions": START_POSITIONS},
        "history": final_state["history"],
        "winner": final_state["winner"],
        "eliminated": final_state["eliminated"],
        "final_positions": final_state["positions"],
        "final_inventories": final_state["inventories"]
    }
    with open(log_path, "w") as f:
        json.dump(log_data, f, indent=2)
    print(f"✅ Log saved to {log_path}")

    create_animation(log_path, gif_path)

    print(f"\n🏁 MATCH COMPLETE!")
    print(f"   Winner: {final_state['winner']}")
    print(f"   Eliminated: {final_state['eliminated']}")
    print(f"   File: {run_dir}")

if __name__ == "__main__":
    run_simulation()