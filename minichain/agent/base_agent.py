from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, List, Optional, Sequence, Dict, Union

from pydantic import BaseModel, Extra

from minichain.agent.output_parser import AgentOutputParser
from minichain.agent.prompt import SHOULD_ANSWER_PROMPT, \
    STEP_BY_STEP_PROMPT
from minichain.agent.structs import AgentAction, AgentFinish
from minichain.models.base import BaseLanguageModel
from minichain.tools.base import Tool


class BaseAgent(BaseModel, ABC):
    output_parser: AgentOutputParser = None
    llm: BaseLanguageModel = None
    tools: Sequence[Tool] = []

    class Config:
        """Configuration for this pydantic object."""

    extra = Extra.forbid
    arbitrary_types_allowed = True

    @classmethod
    def from_llm_and_tools(
        cls,
        llm: BaseLanguageModel,
        tools: Sequence[Tool],
        output_parser: Optional[AgentOutputParser] = None,
        prompt: str = STEP_BY_STEP_PROMPT,
        input_variables: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> BaseAgent:
        """Construct an agent from an LLM and tools."""

    @abstractmethod
    def should_answer(self, inputs: Dict[str, Any],
                      should_answer_prompt_template: str = SHOULD_ANSWER_PROMPT
                      ) -> Optional[AgentFinish]:
        """Determine if agent should continue to answer user questions based on the latest user
        query"""

    @abstractmethod
    def plan(
        self, intermediate_steps: List[AgentAction], **kwargs: Any
    ) -> Union[AgentAction, AgentFinish]:
        """Plan for the next step"""

    @abstractmethod
    def clarify_args_for_agent_action(self, agent_action: AgentAction,
                                      intermediate_steps: List[AgentAction],
                                      **kwargs: Any) -> Union[AgentAction, AgentFinish]:
        """Ask clarifying question if needed"""

    def fix_action_input(self,
                         tool: Tool,
                         action: AgentAction,
                         error: str) -> Optional[AgentAction]:
        """If the tool failed due to error, what should be the fix for inputs"""
        pass