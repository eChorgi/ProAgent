import logging
from typing import List, Dict
import json,os
from colorama import Fore, Style

from ProAgent.loggers.logs import logger
from ProAgent.agent.utils import _chat_completion_request
import openai

class OpenAIFunction():
    def __init__(self):
        os.environ["http_proxy"] = "http://localhost:7890"
        os.environ["https_proxy"] = "http://localhost:7890"
        self.client = openai.OpenAI()
        pass

    def parse(self, **args):
        """
        Parses the given arguments by making a chat completion request.

        Args:
            **args: The keyword arguments to be passed to the chat completion request.

        Returns:
            Tuple: A tuple containing the parsed content, function name, function arguments, and the original message.

        Raises:
            None.
        """

        #设定重试次数
        retry_time = 1
        max_time = 3
        for i in range(max_time):
            output = _chat_completion_request(client = self.client, **args)
            #if isinstance(output, openai.resources.Completions):
            usage = output.usage
            message = output.choices[0].message
            if message.function_call != None:
                break
            else:
                args['messages'].append({"role": "assistant", "content": message.content})
                args['messages'].append({"role": 'user', "content": "No Function call here! You should always use a function call as your response."})
            retry_time += 1
            
            logger._log(f"{Fore.RED} Retry for the {retry_time}'th time{Style.RESET_ALL}")

        if retry_time > max_time:
            error_str = "Failed to generate chat response."
            logger._log(error_str, Fore.LIGHTBLACK_EX, level=logging.ERROR)
            raise TimeoutError(error_str)

        function_name = message.function_call.name
        print("\n"*5)
        print(message.function_call.arguments)
        function_arguments = json.loads(message.function_call.arguments, strict=False)
        print("-"*40+"\nargs = "+str(function_arguments))
        content = ""
        if message.content != None:
            content = message.content
        return content, function_name, function_arguments, message