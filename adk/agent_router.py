from typing import Any, Dict
from adk.agent_registry import AgentRegistry


class AgentRouter:
    @classmethod
    def route_task(cls, target_agent_name: str, context: Dict[str, Any]) -> Any:
        agent = AgentRegistry.get_agent(target_agent_name)
        input_prompt = context.get("task_input", "")
        response = agent.run(input_prompt)
        return response
