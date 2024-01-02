import unittest
import logging
from vectara.core import Factory
import json
import os
from test.base import BaseClientTest
from vectara.util import render_markdown, SimplePromptFactory, StandardPromptFactory

import os

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
