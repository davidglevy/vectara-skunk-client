import unittest
from test.base import BaseClientTest
from pathlib import Path
from vectara.client.util import StandardPromptFactory


class BasicQuery(BaseClientTest):

    def setUp(self):
        super().setUp()
        self.upload_test_doc("./resources/ksa/MCIT_Annual Report_2022_En-Web_0.pdf")

    def test_write_speech_generic(self):
        """
        Write a speech on a topic in a generic style
        """

        system_prompt = ("""You are a speech writer who needs to write a speech for a technical presentation that celebrates the success and bright future of the Kingdom of Saudi Arabia. Use only the information below to create a speech of the requested length in english.""")

        topic = "Green Energy in the Kingdom of Saudi Arabia"
        user_prompt = (f"Create a speech on topic [{topic}] that is 200 words long, including a reference to an initiative"
                       f"listed in our prior responses")

        prompt_factory = StandardPromptFactory(system_prompt, user_prompt)
        prompt = prompt_factory.build()

        qs = self.query_service
        result = qs.query("Green Energy achievements in 2022 or new developments in the future",
                          self.corpus_id, promptText=prompt)

        self.logger.info(result.summary[0].text)

    def test_write_speech_styled(self):
        """
        Write a speech on a topic in a generic style
        """

        speech_path = Path("./resources/speech_transcript/prosperous_future.txt")

        with open(speech_path, 'r') as f:
            example_speech = f.read().replace("\n", "\\n ")

        system_prompt = ("""You are a speech writer who needs to write a speech for a technical presentation that celebrates the success and bright future of the Kingdom of Saudi Arabia. Use only the information below to create a speech of the requested length in english.""")

        system_prompt += "\\nWrite the speech in the following style:\\n{example_speech}"

        topic = "Green Energy in the Kingdom of Saudi Arabia"
        user_prompt = (f"Create a speech on topic [{topic}] that is 200 words long, including a reference to an initiative"
                       f"listed in our prior responses")

        prompt_factory = StandardPromptFactory(system_prompt, user_prompt)
        prompt = prompt_factory.build()

        qs = self.query_service
        result = qs.query("Green Energy achievements in 2022 or new developments in the future",
                          self.corpus_id, promptText=prompt, re_rank=True)

        self.logger.info(result.summary[0].text)


if __name__ == '__main__':
    unittest.main()
