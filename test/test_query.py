from test.base import BaseClientTest
from vectara_client.util import render_markdown, SimplePromptFactory, StandardPromptFactory
from vectara_client.chat import ChatHelper
from test.util import create_test_corpus
from pathlib import Path


class QueryIntegrationTest(BaseClientTest):


    def test_query_corpora(self):
        """
        Run a test over corpora - using Photon paper.

        TODO Make the corpora id dynamic and refreshed by a "start" test.
        :return:
        """
        qs = self.client.query_service
        query = "At Vectara, Can I bring any birds to the Vectara Office?"
        #query = "هل يمكنني إحضار أي طيور إلى مكتب Vectara؟"
        response = qs.query(query, 126)
        self.logger.info(render_markdown(query, response))

    def test_query_with_prompt_text(self):
        """
        Test out the promptText value

        :return:
        """
        qs = self.client.query_service
        query = "At Vectara, Can I bring any birds to the Vectara Office?"


        # prompt_text = ('[ {"role": "system", "content": "You are a human resources manager who takes the search results and summarizes them as a coherent response. Respond in the language denoted by ISO 639 code \\"$vectaraLangCode\\"."}, \n' #,\n'
        #                #'#foreach ($qResult in $vectaraQueryResults) \n'
        #                # '   #if ($foreach.first) \n'
        #                # '   {"role": "user", "content": "Search for \\"$esc.java(${vectaraQuery})\\",'
        #                # ' and give me the first search result."}, \n'
        #                # '   {"role": "assistant", "content": "$esc.java(${qResult.getText()})" }, \n'
        #                # '   #else \n'
        #                #'   {"role": "user", "content": "Give me the \\"$vectaraIdxWord[$foreach.index]\\" search result."}, \n'
        #                #'   {"role": "assistant", "content": "$esc.java(${qResult.getText()})" }, \n'
        #                # '   #end \n'
        #                #' #end \n'
        #                '{"role": "user", "content": "Generate a detailed answer (that is no more than 300 words) '
        #                'for the query \\"$esc.java(${vectaraQuery})\\" solely based on the search results in '
        #                'this chat. You must only use information from the provided results. Cite search results using '
        #                '[number] notation. Only cite the most relevant results that answer the question accurately. '
        #                'If the search results are not valid, respond with \\"The returned results didnt have '
        #                'sufficient information to be summarized into an answer for your query, please restate your '
        #                'query.\\"} '
        #                ']')

        #" Working!! "
        # prompt_text = ('[ {"role": "system", "content": "You are a human resources manager who takes the search results and summarizes them as a coherent response. Respond in the language denoted by ISO 639 code \\"$vectaraLangCode\\"."}, \n' #,\n'
        #                '#foreach ($qResult in $vectaraQueryResults) \n'
        #                # '   #if ($foreach.first) \n'
        #                # '   {"role": "user", "content": "Search for \\"$esc.java(${vectaraQuery})\\",'
        #                # ' and give me the first search result."}, \n'
        #                # '   {"role": "assistant", "content": "$esc.java(${qResult.getText()})" }, \n'
        #                # '   #else \n'
        #                '   {"role": "user", "content": "Give me the \\"$vectaraIdxWord[$foreach.index]\\" search result."}, \n'
        #                '   {"role": "assistant", "content": "$esc.java(${qResult.getText()})" }, \n'
        #                # '   #end \n'
        #                ' #end \n'
        #                '{"role": "user", "content": "Generate a detailed answer (that is no more than 300 words) for the query \\"$esc.java(${vectaraQuery})\\"." } ]')

        prompt_text = ('[ {"role": "system", "content": "You are a human resources manager who takes the search results and summarizes them as a coherent response. Only use information provided in this chat. Respond in the language denoted by ISO 639 code \\"$vectaraLangCode\\"."}, \n' #,\n'
                       '#foreach ($qResult in $vectaraQueryResults) \n'
                       '   #if ($foreach.first) \n'
                       '   {"role": "user", "content": "Search for \\"$esc.java(${vectaraQuery})\\", and give me the first search result."}, \n'
                       '   {"role": "assistant", "content": "$esc.java(${qResult.getText()})" }, \n'
                       '   #else \n'
                       '   {"role": "user", "content": "Give me the \\"$vectaraIdxWord[$foreach.index]\\" search result."}, \n'
                       '   {"role": "assistant", "content": "$esc.java(${qResult.getText()})" }, \n'
                       '   #end \n'
                       ' #end \n'
                       '{"role": "user", "content": "Generate a detailed answer (that is no more than 300 words) for the query \\"$esc.java(${vectaraQuery})\\" solely based on the search results in this chat. You must only use information from the provided results. Cite search results using \\"[number]\\" notation. Only cite the most relevant results that answer the question accurately." } ]')



        response = qs.query(query, 126, promptText=prompt_text)

        self.logger.info(render_markdown(query, response))


    def test_query_with_prompt_generator_standard(self):
        """
        Test out the promptText value

        :return:
        """
        qs = self.client.query_service
        query = "At Vectara, Can I bring any birds to the Vectara Office?"
        system_prompt = 'You are a human resources manager who takes the search results and summarizes them as a coherent response. Only use information provided in this chat. Respond in the language denoted by ISO 639 code \\"$vectaraLangCode\\".'
        user_prompt = 'Generate a detailed answer (that is no more than 300 words) for the query \\"$esc.java(${vectaraQuery})\\" solely based on the search results in this chat. You must only use information from the provided results. Cite search results using \\"[number]\\" notation. Only cite the most relevant results that answer the question accurately.'

        prompt_factory = StandardPromptFactory(system_prompt=system_prompt, user_prompt=user_prompt)
        prompt_text = prompt_factory.build()

        response = qs.query(query, 126, promptText=prompt_text)

        self.logger.info(render_markdown(query, response))

    def test_query_with_prompt_generator_simple(self):

        """
        Test out the promptText value

        :return:
        """
        qs = self.client.query_service
        query = "At Vectara, Can I bring any birds to the Vectara Office?"

        prompt_factory = SimplePromptFactory(persona="Legal Officer in Australia", cite=False, max_word_count=100)
        prompt_text = prompt_factory.build()

        self.logger.info(f"Prompt text is:\n {prompt_text}")

        response = qs.query(query, 126, promptText=prompt_text)

        self.logger.info(render_markdown(query, response, show_search_results=False))

    def test_query_chat(self):
        corpus_id, existing = create_test_corpus(test_name="test_query_chat")

        qs = self.client.query_service

        indexer_service = self.client.indexer_service

        resources_dir = Path("./resources/fair_work_australia")

        # Do not upload if we found existing corpus
        if not existing:
            result = None
            for p in resources_dir.glob("*.pdf"):
                result = indexer_service.upload(corpus_id, p, return_extracted=False)

        #prompt_factory = ChatPromptFactory(chat_persona="Friendly Human Resources employee", name="Fiona", max_word_count=150)

        chat_helper = ChatHelper(corpus_id, qs, customer_name="David", name="Rachel", max_word_count=150,
                                 chat_persona="A Pleasant Legal Officer at Fair Work Australia")

        chat_helper.run_chat("How are you today?")
        chat_helper.run_chat("Am I entitled to paid leave in Australia?")
        chat_helper.run_chat("My employer has said that Christmas Day and "
                             "Boxing Day counts as paid leave, is this correct?")
        chat_helper.run_chat("I'm a permanent employee who works regular hours: 9-5, 5 days a week without special "
                             "which only says is complies with Australia law.")
        chat_helper.run_chat("I work as a white collar employee and am interested in Annual Leave.")
        chat_helper.run_chat("It says I get four weeks paid annual leave in my employment contract plus public holidays")





