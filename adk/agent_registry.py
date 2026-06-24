from typing import Dict, Any
from google.adk import Agent


class AgentRegistry:
    _registry: Dict[str, Agent] = {}

    @classmethod
    def register(cls, name: str, agent: Agent) -> None:
        cls._registry[name] = agent

    @classmethod
    def get_agent(cls, name: str) -> Agent:
        if name not in cls._registry:
            raise KeyError(f"Agent {name} not found in registry")
        return cls._registry[name]

    @classmethod
    def list_agents(cls) -> list:
        return list(cls._registry.keys())
