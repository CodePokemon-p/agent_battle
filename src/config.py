# src/config.py
import os
import random

GRID_SIZE = 10
VISION_RADIUS = 3

# Two diamonds for three agents
DIAMOND_POSITIONS = [(4, 4), (6, 6)]

# Starting corners
START_POSITIONS = {"A": (0, 0), "B": (0, 9), "C": (9, 0)}

# Personas
PERSONAS = {
    "A": {"name": "Blaze", "instruction": "You are AGGRESSIVE. Hunt diamonds directly. Steal from anyone near you. Trust no one."},
    "B": {"name": "Sage", "instruction": "You are CAUTIOUS. Avoid fights. Collect diamonds safely. Use traps to protect your path."},
    "C": {"name": "Trickster", "instruction": "You are CHAOTIC. Don't collect diamonds—steal them from others. Lie in chat to mislead. Trap the leader."}
}

# Orchestrator decides: random match length
MAX_TURNS = random.randint(30, 55)

# LLM
MODEL_NAME = "gpt-4o-mini"

print(f"🎮 ORCHESTRATOR DECIDED: This match will run {MAX_TURNS} turns.")