from llama_index.core import Settings, get_response_synthesizer
from llama_index.core.response_synthesizers import ResponseMode

from src.promts.promt_qa import QA_PROMPT


class ResponseSynthesizerFactory:
    def __init__(self):
        self.llm = Settings.llm

    def build(self, streaming: bool = True):
        return get_response_synthesizer(
            llm=self.llm,
            response_mode=ResponseMode.COMPACT,
            text_qa_template=QA_PROMPT,
            streaming=streaming,
        )