# src/evaluator.py
from src.state import AgentState

class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

def evaluate_and_eliminate(state: AgentState) -> dict:
    diamond_counts = {agent: state["inventories"].get(agent, []).count("diamond") for agent in state["positions"]}
    
    # Check if anyone has diamonds
    total_diamonds = sum(diamond_counts.values())
    
    if total_diamonds == 0:
        # NO WINNER — everyone failed
        drama = f"""
{Colors.BOLD}💀 STALEMATE! NO ONE COLLECTED ANY DIAMONDS! 💀{Colors.END}
{'='*50}
All agents failed to collect a single diamond.
No winner. No elimination.

📊 FINAL DIAMOND COUNT:
  📌 A: 0 diamond(s)
  📌 B: 0 diamond(s)
  📌 C: 0 diamond(s)

🔥 Everyone survives to fight another day!
"""
        print(drama)
        return {
            "winner": None,
            "eliminated": None,
            "game_over": True
        }
    
    # If someone has diamonds, rank them
    sorted_agents = sorted(diamond_counts.items(), key=lambda x: x[1], reverse=True)
    winner = sorted_agents[0][0]
    eliminated = sorted_agents[-1][0]
    
    drama = f"""
{Colors.BOLD}🏆 FINAL ELIMINATION CEREMONY 🏆{Colors.END}
{'='*50}
🥇 WINNER: Agent {winner} with {diamond_counts[winner]} diamond(s)!
💀 ELIMINATED: Agent {eliminated} with {diamond_counts[eliminated]} diamond(s)!

📊 FINAL DIAMOND COUNT:
"""
    for agent, count in sorted_agents:
        medal = "🥇" if agent == winner else "💀" if agent == eliminated else "📌"
        drama += f"  {medal} {agent}: {count} diamond(s)\n"
    print(drama)
    return {"winner": winner, "eliminated": eliminated, "game_over": True}