# src/state.py
from typing import TypedDict, Dict, Tuple, List, Optional, Set

class AgentState(TypedDict):
    positions: Dict[str, Tuple[int, int]]
    inventories: Dict[str, List[str]]
    diamonds: List[Tuple[int, int]]
    traps: Dict[Tuple[int, int], str]
    walls: Set[Tuple[int, int]]
    turn: int
    max_turns: int
    history: List[Dict]
    pending_actions: Dict[str, Dict]
    messages: List[Dict]
    memory: Dict[str, List[str]]
    bounties: List[str]
    frozen: Dict[str, int]
    winner: Optional[str]
    game_over: bool