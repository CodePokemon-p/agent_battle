# src/visualize.py
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.patches as patches
import json
import os
from matplotlib.patches import Circle, Rectangle, Polygon

def create_animation(log_file="run_log.json", output_file="race_replay.gif"):
    if not os.path.exists(log_file):
        print("❌ Log file not found.")
        return
    
    with open(log_file, 'r') as f:
        data = json.load(f)
    
    history = data["history"]
    config = data["config"]
    grid_size = config["grid_size"]
    diamonds = config["diamonds"]

    # --- BIGGER FIGURE SIZE for better readability ---
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(14, 14))  # Increased from 10 to 14
    ax.set_facecolor('#1a1a2e')

    agent_colors = {"A": "#ff6b6b", "B": "#4ecdc4", "C": "#ffe66d"}
    agent_names = {"A": "Blaze", "B": "Sage", "C": "Trickster"}

    def update(frame):
        ax.clear()
        ax.set_xlim(-1.5, grid_size + 0.5)
        ax.set_ylim(-1.5, grid_size + 0.5)
        ax.set_facecolor('#1a1a2e')
        
        # Grid lines (subtle)
        for i in range(grid_size + 1):
            ax.axhline(i - 0.5, color='#444477', linewidth=0.5, alpha=0.3)
            ax.axvline(i - 0.5, color='#444477', linewidth=0.5, alpha=0.3)

        turn_data = history[frame]
        turn_num = turn_data["turn"]
        max_turns = len(history) - 1
        
        # --- BIGGER TITLE ---
        ax.set_title(f"🏁 TURN {turn_num} / {max_turns}", 
                     fontsize=24, color='white', fontweight='bold', pad=25)

        # --- DRAW DIAMONDS (BIGGER) ---
        remaining = turn_data.get("diamonds_left", diamonds)
        for dx, dy in remaining:
            star = patches.RegularPolygon((dy, dx), 5, radius=0.5, 
                                          facecolor='gold', edgecolor='white', 
                                          linewidth=2, alpha=0.9)
            ax.add_patch(star)
            glow = Circle((dy, dx), 0.8, color='gold', alpha=0.15)
            ax.add_patch(glow)

        # --- DRAW AGENTS (BIGGER) ---
        positions = turn_data["positions"]
        for agent, pos in positions.items():
            x, y = pos
            color = agent_colors[agent]
            
            # Bigger body
            body = Circle((y, x), 0.5, color=color, edgecolor='white', linewidth=3)
            ax.add_patch(body)
            
            # BIGGER agent letter
            ax.text(y, x, agent, fontsize=20, ha='center', va='center', 
                    color='black', fontweight='bold')
            
            # BIGGER agent name below
            ax.text(y, x - 1.0, agent_names[agent], fontsize=14, ha='center', va='center', 
                    color='white', alpha=0.8, fontstyle='italic')

        # --- CHAT BUBBLE (BIGGER FONT) ---
        messages = turn_data.get("messages", [])
        if messages:
            latest = messages[-1]
            if latest.get("sender") not in ["ORCHESTRATOR"]:
                sender = latest["sender"]
                if sender in positions:
                    sx, sy = positions[sender]
                    msg_text = f"{sender}: {latest['content']}"
                    # BIGGER bubble with bigger font
                    ax.text(sy, sx + 1.0, msg_text, fontsize=14, ha='center', va='center',
                            color='white', 
                            bbox=dict(boxstyle="round,pad=0.5", 
                                      facecolor='#222266', 
                                      edgecolor='#6666cc', 
                                      alpha=0.9, 
                                      linewidth=2))

        # --- SCOREBOARD (BIGGER, TOP RIGHT) ---
        score_text = ""
        for agent in ["A", "B", "C"]:
            count = turn_data.get("inventories", {}).get(agent, []).count("diamond")
            score_text += f"{agent}: {count}💎  "
        
        ax.text(grid_size - 0.5, grid_size + 0.5, score_text, 
                fontsize=18, ha='right', va='center',
                color='white', fontweight='bold',
                bbox=dict(boxstyle="round,pad=0.3", 
                          facecolor='#111133', 
                          alpha=0.8))

    # --- SLOWER ANIMATION (so humans can read) ---
    ani = animation.FuncAnimation(fig, update, frames=len(history), repeat=True, interval=800)
    ani.save(output_file, writer='pillow', fps=1.5)  # Slower = readable
    plt.close()
    print(f"🎥 Animation saved to {output_file}")