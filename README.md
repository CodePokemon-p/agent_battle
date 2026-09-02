# 🤖 AI Battle Royale — "Race to the Diamond"

**3 AI agents fight for diamonds. Stealing, traps, lying, and chaos allowed.**

## 🎬 What is this?

I built a game where 3 AI agents (Blaze, Sage, Trickster) compete to collect diamonds on a 10x10 grid. Each agent has a unique personality and makes decisions using GPT-4o-mini.

- **Blaze (A)** — Aggressive. Hunts diamonds. Steals from anyone near.
- **Sage (B)** — Cautious. Avoids fights. Uses traps to protect.
- **Trickster (C)** — Chaotic. Lies in chat. Steals from leaders.

## 🎮 Features

- 🔥 Live terminal chaos with colored output
- 💎 Diamond collection with scarcity (2 diamonds, 3 agents)
- 💬 Agents can shout lies and private messages
- ⚡ Steal, trap, and block mechanics
- 🏆 Elimination ceremony at the end
- 🎥 GIF replay of the entire match

## 📁 Project Structure
agent_battle/
├── src/
│ ├── config.py # Game settings
│ ├── state.py # Game state
│ ├── agents.py # AI decision logic
│ ├── orchestrator.py # LangGraph engine
│ ├── evaluator.py # Winner/elimination
│ ├── visualize.py # GIF generator
│ └── main.py # Entry point
├── runs/ # Each match = timestamped folder
│ └── 2026-09-02_15-26-34/
│ ├── run_log.json
│ └── race_replay.gif
├── content/ # OBS recordings & edits
├── content_log.md # Daily filming diary
├── requirements.txt
└── README.md


Watch the Chaos
https://github.com/CodePokemon-p/agent_battle/blob/main/episode-1-stalemate.gif

## 🚀 How to Run

```bash
# Install dependencies
pip install -r requirements.txt

# Set your OpenAI API key
export OPENAI_API_KEY="sk-..."

# Run a match
python -m src.main
eason 1 Episodes
Episode	Match	Result
1	49 turns	Stalemate — 0 diamonds collected
2	TBD	TBD
3	TBD	TBD
4	TBD	TBD
5	TBD	TBD
6	TBD	TBD
7	TBD	TBD
🛠️ Tech Stack
Python 3.10+

LangGraph (agent orchestration)

LangChain + OpenAI API (LLM decisions)

Matplotlib (GIF generation)




