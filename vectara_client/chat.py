from vectara_client.util import ChatPromptFactory, render_markdown
from vectara_client.query import QueryService
import logging


class ChatHelper:

    def __init__(self, corpus_id: int, qs: QueryService, customer_name:str,
                 chat_persona="Customer Service", name="Fiona",
                 max_word_count:int=300, log_response: bool = True, resp_lang="en",
                 context_config=None, re_rank=False, summary_result_count=5,
                 page_size=10):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.corpus_id = corpus_id
        self.qs = qs
        self.prompt_factory = ChatPromptFactory(chat_persona, name, max_word_count=max_word_count)
        self.prompt_factory.add_assistant_message(f"Hi my name is {name}, who am I speaking with today?")
        self.prompt_factory.add_user_assistant_pair(f"My name is {customer_name}",
                                                    "Okay great to meet you. What can I help you with today?")
        self.resp_lang = resp_lang

        self.log_response = log_response
        self.context_config = context_config
        self.re_rank = re_rank
        self.summary_result_count = summary_result_count
        self.page_size = page_size

    def run_chat(self, query: str) -> str:
        prompt_text = self.prompt_factory.build()
        # self.logger.info(f"Prompt text is:\n {prompt_text}")

        #self.qs.query(query, self.corpus_id, prompt_text)

        response = self.qs.query(query, self.corpus_id, promptText=prompt_text, response_lang=self.resp_lang,
                                 context_config=self.context_config, re_rank=self.re_rank,
                                 summary_result_count=self.summary_result_count, page_size=self.page_size,
                                 summarizer="vectara-summary-ext-v1.3.0")

        if self.log_response:
            self.logger.info(render_markdown(query, response, show_search_results=False))

        summary_response = response.summary[0].text

        # Now we add the additional context to  the factory.
        self.prompt_factory.add_user_assistant_pair(query, summary_response)

        return response
