import os
import gdb
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

def get_register_values():
    # List of register names you want to get the values for
    register_names = ["rax", "rbx", "rsp", "rip", "r8", "r9", "rcx", "rdx", "rsi", "rdi"]

    register_values = {}
    for reg_name in register_names:
        try:
            # Evaluate the expression to get the register value
            value = gdb.parse_and_eval(f"${reg_name}")
            # Convert the value to an appropriate Python representation (optional)
            value_str = str(value)
            register_values[reg_name] = value_str
        except gdb.error as e:
            print(f"Error while reading register {reg_name}: {e}")
            return None

    return register_values


def get_stack_trace():
    # Execute the "backtrace" command in GDB to get the stack trace
    try:
        result = gdb.execute("backtrace", to_string=True)
        stack_trace = result.strip()
        return stack_trace
    except gdb.error as e:
        print(f"Error while getting stack trace: {e}")
        return None


def get_completion(prompt=""):
    # Send the input text to OpenAI API
    # response = openai.Completion.create(
    #     engine="text-davinci-002",  # Choose an appropriate GPT-3.5 model
    #     prompt=input_text,
    #     max_tokens=100  # Adjust the response length as needed
    # )
    if prompt.strip() == "":
        return "empty chat"

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful gdb assistant."},
            {"role": "user", "content": prompt }
        ]
    )

    # Process the AI response and extract suggestions
    suggestions = response.choices[0].message.get('content','get ai suggestions failed') + '\n'
    return suggestions

def get_debug_seggestions(question=""):
    # Get the relevant debugging information from GDB
    # For example:
    current_function = ""
    register_values = ""
    stack_trace = ""
    input_text = ""
    try:
        current_function = gdb.selected_frame().name()
        register_values = get_register_values()  # Get register values using GDB API
        stack_trace = get_stack_trace()       # Get stack trace using GDB API
    except :    
        current_function = register_values = stack_trace = None
    finally:
        if current_function is not None:
            # Prepare the input text for the AI model
            input_text = f"Debugging function {current_function} with registers {register_values} and stack trace {stack_trace}." + question
        else:
            if len(question.strip()) == 0:
                return "cannot get current function info or your question\n"
            else:
                input_text = question
    

    return get_completion(input_text)


class AICommand(gdb.Command):
    def __init__(self):
        super(AICommand, self).__init__(
            "ai",  # The name of the command to be used in GDB
            gdb.COMMAND_USER  # The command type (in this case, a user-defined command)
        )
        gdb.write("AI assistant inited!\n")


    def invoke(self, argument: str, from_tty: bool) -> None:
        # 'arg' contains the arguments passed to the command
        # 'from_tty' is a boolean indicating if the command was invoked from a terminal

        # Your custom logic here
        suggestions = ""
        if argument.strip() == "":
            suggestions = get_debug_seggestions()
        else:
            suggestions = get_debug_seggestions(argument.strip())
        
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

        # Your custom logic here
        suggestions = ""
        if argument.strip() == "":
            suggestions = get_debug_seggestions()
        else:
            suggestions = get_debug_seggestions(argument.strip())
        
        gdb.write(suggestions)

AICommand()
ChatCommand()
# gdb.execute("ai", from_tty=True)

