import json
import os
import time
import gdb
import openai
import requests

# openai.api_key = os.getenv("OPENAI_API_KEY")
# openai.api_base = os.environ.get("OPENAI_API_BASE", "https://api.openai.com/v1")
CHATGLM_API = os.environ.get("CHATGLM_API", "http://localhost:8000")
g_llm = "gpt"
LLMODEL = os.environ.get("GDBAI_MODEL", "gpt-3.5-turbo")
AnwserLang = os.environ.get("GDBAI_LANG", None)

def get_register_values() -> str:
    try:
        # result = gdb.execute("info all-registers", to_string=True)
        result = gdb.execute("i r", to_string=True)
        register_values = result.strip()
        return register_values
    except gdb.error as e:
        print(f"Error while getting register vlaues: {e}")
        return None


def get_breakpoints() -> str:
    try:
        result = gdb.execute("i b", to_string=True)
        breakpoints = result.strip()
        return breakpoints
    except gdb.error as e:
        print(f"Error while getting breakpoints: {e}")
        return None


def get_execution_status() -> str:
    try:
        result = gdb.execute("i program", to_string=True)
        execution_status = result.strip()
        return execution_status
    except:
        print("Error while getting execution status")
        return None


def get_stack_trace() -> str:
    # Execute the "backtrace" command in GDB to get the stack trace
    try:
        result = gdb.execute("backtrace", to_string=True)
        stack_trace = result.strip()
        return stack_trace
    except gdb.error as e:
        print(f"Error while getting stack trace: {e}")
        return None


def get_completion(prompt="") -> str:
    # Send the input text to OpenAI API
    # response = openai.Completion.create(
    #     engine="text-davinci-002",  # Choose an appropriate GPT-3.5 model
    #     prompt=input_text,
    #     max_tokens=100  # Adjust the response length as needed
    # )
    start_time = time.time()
    if prompt.strip() == "":
        return "empty chat"

    suggestions = ""
    if  g_llm == "glm":
        # print("use chatglm api")

        # example: curl -X POST ${CHATGLM_API}  -H 'Content-Type: application/json'  -d '{"prompt": "你好", "history": []}'
        data = {
            "prompt": "I want you to play the role of a senior software engineer,\
                  debugging information through the following GDB\n" + prompt,
            "history": []
        }

        headers = {'Content-Type': 'application/json'}
        response = requests.post(CHATGLM_API, headers=headers, data=json.dumps(data))
        if response.status_code == 200:
            result = response.json()
            suggestions = result.get('response', "get ai suggestions failed") + '\n'
        else:
            suggestions = "get ai suggestions failed\n"

    elif g_llm == "gpt":
        # print("use gpt3 api")
        response = openai.ChatCompletion.create(
            model=LLMODEL,
            messages=[
                {"role": "system", "content": "You are a helpful gdb assistant."},
                {"role": "user", "content": prompt }
            ]
        )

        # Process the AI response and extract suggestions
        suggestions = response.choices[0].message.get('content','get ai suggestions failed') + '\n'
    else:
        suggestions =  "get ai suggestions failed\n"

    # print(f"{g_llm} response time: {time.time() - start_time} seconds")
    return suggestions

def get_debug_info() -> dict:
    # Get the relevant debugging information from GDB
    # For example:
    current_function = ""
    register_values = ""
    stack_trace = ""
    breakpoints = ""
    frame = gdb.selected_frame()
    try:
        current_function = frame.name()
    except:
        current_function = None

    try:
        register_values = get_register_values()
    except:
        register_values = None

    try:
        stack_trace = get_stack_trace()
    except:
        stack_trace = None

    try:
        breakpoints = get_breakpoints()
    except:
        breakpoints = None


    res = {
        'current_function': current_function,
        'register_values': register_values,
        'stack_trace': stack_trace,
        'breakpoints': breakpoints
    }
    return res


class AICommand(gdb.Command):
    def __init__(self):
        super(AICommand, self).__init__(
            "ai",  # The name of the command to be used in GDB
            gdb.COMMAND_USER  # The command type (in this case, a user-defined command)
        )


    def invoke(self, argument: str, from_tty: bool) -> None:
        # 'arg' contains the arguments passed to the command
        # 'from_tty' is a boolean indicating if the command was invoked from a terminal


        suggestions = ""
        question = argument.strip()
        info = get_debug_info()
        lang = " 用中文回答." if AnwserLang is not None else ""
        prompt = "Here aie some GDB debug info:\n"
        if info["current_function"] is not None:
            prompt += f"Current function: {info['current_function']}\n"
        if info['register_values'] is not None:
            prompt += f"Register values:\n{info['register_values']}\n"
        if info['stack_trace'] is not None:
            prompt += f"Stack trace:\n{info['stack_trace']}\n"
        if info['breakpoints'] is not None:
            prompt += f"Breakpoints:\n{info['breakpoints']}\n"
        if question == "":
            prompt += "\nExplain what the root cause of this error is.Give me Suggestions." + lang
        else:
            prompt += '\n' + question + lang

        # print(prompt)
        suggestions = get_completion(prompt)
        gdb.write(suggestions)


class ChatCommand(gdb.Command):
    def __init__(self):
        super(ChatCommand, self).__init__(
            "chat",  # The name of the command to be used in GDB
            gdb.COMMAND_USER  # The command type (in this case, a user-defined command)
        )


    def invoke(self, argument: str, from_tty: bool) -> None:
        # 'arg' contains the arguments passed to the command
        # 'from_tty' is a boolean indicating if the command was invoked from a terminal


        suggestions = ""
        if argument.strip() == "":
            suggestions = "usage: chat how to use gdb\n"
        else:
            suggestions = get_completion(argument.strip())

        gdb.write(suggestions)


class TransCommand(gdb.Command):
    def __init__(self):
        super(TransCommand, self).__init__(
            "trans",  # The name of the command to be used in GDB
            gdb.COMMAND_USER  # The command type (in this case, a user-defined command)
        )


    def invoke(self, argument: str, from_tty: bool) -> None:
        # 'arg' contains the arguments passed to the command
        # 'from_tty' is a boolean indicating if the command was invoked from a terminal


        question = argument.strip()
        if question == "":
            suggestions = "usage: trans show the instructions at the current location\n"
            gdb.write(suggestions)
        else:
            prompt = f"Give me a single GDB command with no explanation.Do not write any text above or below the command. Only give me the command as text.Here is my question:{question}"
            suggestions = get_completion(prompt)
            print(suggestions)
            gdb.execute(suggestions, from_tty=True)


class ExplainCommand(gdb.Command):
    def __init__(self):
        super(ExplainCommand, self).__init__(
            "explain",  # The name of the command to be used in GDB
            gdb.COMMAND_USER  # The command type (in this case, a user-defined command)
        )


    def invoke(self, argument: str, from_tty: bool) -> None:
        # 'arg' contains the arguments passed to the command
        # 'from_tty' is a boolean indicating if the command was invoked from a terminal


        suggestions = ""
        if argument.strip() == "":
            suggestions = "usage: explain handle SIGINT stop\n"
        else:
            lang = " in Chinese" if AnwserLang is not None else ""
            prompt = f"Explain for this GDB command{lang}: {argument.strip()}"
            suggestions = get_completion(prompt)

        gdb.write(suggestions)

class SelectLLMCommand(gdb.Command):
    def __init__(self):
        super(SelectLLMCommand, self).__init__(
            "llm",  # The name of the command to be used in GDB
            gdb.COMMAND_USER  # The command type (in this case, a user-defined command)
        )

    def invoke(self, argument: str, from_tty: bool) -> None:
        # 'arg' contains the arguments passed to the command
        # 'from_tty' is a boolean indicating if the command was invoked from a terminal
        global g_llm

        suggestions = ""
        if argument.strip() == "":
            suggestions = "usage: llm [gpt|glm]\n"
        else:
            llm = argument.strip().lower()
            if llm not in ["gpt", "glm"]:
                suggestions = "usage: llm [gpt|glm]\n"
            else:
                g_llm = llm
                suggestions = f"select {llm} model\n"

        gdb.write(suggestions)


AICommand()
ChatCommand()
TransCommand()
ExplainCommand()
SelectLLMCommand()

gdb.write("usage:\n"
          "\tai\n"
          "\tai Explain what the root cause of this error is.Give me Suggestions\n"
          "\tai 用中文回答无效指针是哪个\n"
          "\tchat how to use gdb\n"
          "\ttrans show the instructions at the current location\n"
          "\texplain handle SIGINT stop\n"
          "\tllm [gpt|glm] select llm\n"
          )
# gdb.execute("ai", from_tty=True)

