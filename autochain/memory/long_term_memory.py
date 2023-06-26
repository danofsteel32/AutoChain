"""
This is an example implementation of long term memory and retrieve using query
It contains three memory stores.
chat_history stores all the messages including FunctionMessage between assistant and agent,
long_term_memory stores a collection of ChromaDoc (or would be modified use other vectory db)
kv_memory: stores anything else as kv pairs
"""
from typing import Any, Optional

from autochain.agent.message import ChatMessageHistory, MessageType
from autochain.memory.base import BaseMemory
from autochain.tools.internal_search.chromadb_tool import ChromaDBSearch, ChromaDoc


class LongTermMemory(BaseMemory):
    """Buffer for storing conversation memory and an in-memory kv store."""

    chat_history = ChatMessageHistory()
    kv_memory = {}
    long_term_memory = ChromaDBSearch(docs=[], description="long term memory")

    class Config:
        keep_untouched = (ChromaDBSearch,)

    def load_memory(
        self,
        key: Optional[str] = None,
        default: Optional[Any] = None,
        n_results: int = 1,
        **kwargs
    ) -> Any:
        """Return history buffer by key or all memories."""
        if key in self.kv_memory:
            return self.kv_memory[key]

        # else try to retrieve from long term memory
        result = self.long_term_memory.run({"query": key, "n_results": n_results})
        return result or default

    def load_conversation(self, **kwargs) -> ChatMessageHistory:
        """Return history buffer and format it into a conversational string format."""
        return self.chat_history

    def save_memory(self, key: str, value: Any) -> None:
        if (
            isinstance(value, list)
            and len(value) > 0
            and isinstance(value[0], ChromaDoc)
        ):
            self.long_term_memory.add_docs(docs=value)
        elif key:
            self.kv_memory[key] = value

    def save_conversation(
        self, message: str, message_type: MessageType, **kwargs
    ) -> None:
        """Save context from this conversation to buffer."""
        self.chat_history.save_message(
            message=message, message_type=message_type, **kwargs
        )

    def clear(self) -> None:
        """Clear memory contents."""
        self.chat_history.clear()
        self.long_term_memory.clear_index()
        self.kv_memory = {}