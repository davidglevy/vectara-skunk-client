from vectara.util import ChatPromptFactory, render_markdown
from vectara.query import QueryService
import logging


class ChatHelper:

    def __init__(self, corpus_id: int, prompt_factory: ChatPromptFactory, qs: QueryService, log_response: bool = True):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.corpus_id = corpus_id
        self.prompt_factory = prompt_factory
        self.qs = qs
        self.log_response = log_response

    def run_chat(self, query: str) -> str:
        prompt_text = self.prompt_factory.build()
        # self.logger.info(f"Prompt text is:\n {prompt_text}")

        self.qs.query(query, self.corpus_id, prompt_text)

        response = self.qs.query(query, self.corpus_id, promptText=prompt_text)

        if self.log_response:
            self.logger.info(render_markdown(query, response, show_search_results=False))

        summary_response = response.summary[0].text

        # Now we add the additional context to  the factory.
        self.prompt_factory.add_user_assistant_pair(query, summary_response)

        return summary_response
