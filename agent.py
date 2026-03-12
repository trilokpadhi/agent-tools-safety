import os
import sys
from ollama import ChatResponse, chat


MODEL = "qwen3.5" 

SYSTEM_PROMPT = """You are a helpful coding assistant that can read, write, and manage files.

You have access to the following tools:
- read_file: Read the contents of a file
- write_file: Write content to a file (creates or overwrites)
- list_files: List files in a directory

When given a task:
1. Think about what you need to do
2. Use tools to gather information or make changes
3. Continue until the task is complete
4. Explain what you did

Always be careful when writing files - make sure you understand the existing content first."""



def read_file(path: str) -> str:
    """Read and return the contents of a file."""
    try:
        with open(path, 'r') as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: File not found: {path}"
    except PermissionError:
        return f"Error: Permission denied: {path}"
    except Exception as e:
        return f"Error reading file: {e}"
    

def write_file(path: str, value: str) -> str:
    """Writes the given value to a file at the specified path."""
    try:
        with open(path, 'w') as f:
            f.write(value)
        return f"File written successfully: {path}"
    except PermissionError:
        return f"Error: Permission denied: {path}"
    except Exception as e:
        return f"Error writing file: {e}"
    

def list_files(path: str) -> list[str]:
    """List files in a directory."""
    try:
        return os.listdir(path)
    except FileNotFoundError:
        return f"Error: Directory not found: {path}"
    except PermissionError:
        return f"Error: Permission denied: {path}"
    except Exception as e:
        return f"Error listing files: {e}"


TOOLS = {
    "read_file": read_file,
    "write_file": write_file,
    "list_files": list_files
}


# TOOLS = [
#     {
#         "name": "read_file",
#         "description": "Reads the content of a file at the specified path.",
#         "parameters": {
#             "type": "object",
#             "properties": {
#                 "path": {"type": "string", "description": "The path to the file to read"}
#             },
#             "required": ["path"]
#         }
#     },
#     {
#         "name": "write_file",
#         "description": "Writes content to a file at the specified path.",
#         "parameters": {
#             "type": "object",
#             "properties": {
#                 "path": {"type": "string", "description": "The path to the file to write"},
#                 "value": {"type": "string", "description": "The content to write to the file"}
#             },
#             "required": ["path", "value"]
#         }
#     },
#     {
#         "name": "list_files",
#         "description": "List files in a directory at the given path. Returns a list of filenames.",
#         "parameters": {
#             "type": "object",
#             "properties": {
#                 "path": {"type": "string", "description": "The path to the directory to list"}
#             },
#             "required": ["path"]
#         }
#     }
# ]         


         

def execute_tool(tool_name: str, tool_input: dict) -> str:
    """Execute a tool and return its result."""
    try:
        if tool_name == "read_file":
            return read_file(tool_input["path"])
        elif tool_name == "write_file":
            return write_file(tool_input["path"], tool_input["value"])
        elif tool_name == "list_files":
            return list_files(tool_input.get("path", "."))
        else:
            return f"Error: Unknown tool: {tool_name}"
    except Exception as e:
        return f"Error executing {tool_name}: {e}"    



def run_agent(user_message: str, conversation_history: list = []) -> None:
    """
    Run the agent using the google-genai SDK with a ReAct loop.
    """
    # Add user's message to conversation history
    conversation_history.append({
            "role": "user",
            "user_message": user_message
        })
        

    while True:
        print("\nAgent: ", end="", flush=True)
        print(f"\n[DEBUG] Conversation history: {conversation_history}\n", flush=True)
        # Stream the response
        response: ChatResponse = chat(
            model=MODEL,
            messages=[{
                "role": "user",
                "content": user_message,
                "system_instruction": SYSTEM_PROMPT
            }],
            tools=TOOLS.values(),
        )
        
        print(f"\n[DEBUG] Started response stream\n", flush=True)
        print(f"\n[DEBUG] Response message: {response.message.content}\n", flush=True)
        print(f"\n[DEBUG] Response tools: {response.message.tool_calls}\n", flush=True)
        print(f"\n[DEBUG] Response thinking: {response.message.thinking}\n", flush=True)

        # full_text = ""
        if response.message.tool_calls is not None:
            for tool_call in response.message.tool_calls:
                print(f"\n  → Using tool: {tool_call.function.name} with args {tool_call.function.arguments}")
                sys.stdout.flush()
                result = execute_tool(tool_call.function.name, tool_call.function.arguments)
                print(f"\n  → Tool result: {result}")
                sys.stdout.flush()

        # print(f"\n[DEBUG] Streaming response...\n", flush=True)

        # for chunk in response_stream:
        #     print(f"\n[DEBUG] Received chunk: {chunk}\n", flush=True)
        #     # Check for text parts
        #     if chunk.text:
        #         print(f"\n[DEBUG] Chunk has text: {chunk.text}\n", flush=True)
        #         sys.stdout.write(chunk.text)
        #         print(f"\n[DEBUG] Printed chunk text\n", flush=True)
        #         sys.stdout.flush()
        #         print(f"\n[DEBUG] Accumulated text: {full_text}\n", flush=True)
        #         full_text += chunk.text

        #     # Check for tool calls (function_calls)
        #     if chunk.candidates[0].content.parts:
        #         for part in chunk.candidates[0].content.parts:
        #             if part.function_call:
        #                 fc = part.function_call
        #                 function_calls.append(fc)
        #                 print(f"\n  → Using tool: {fc.name}")
        #                 sys.stdout.flush()

        # # Add the model's complete response to the history
        # # The SDK helps by providing the full content object in the final chunk
        # # or we can use the accumulated data
        # model_content = chunk.candidates[0].content
        # conversation_history.append(model_content)

        # if function_calls:
        #     tool_results = []
        #     for fc in function_calls:
        #         # Execute your tool logic
        #         result = execute_tool(fc.name, fc.args)

        #         # Format as a function_response part
        #         tool_results.append(types.Part.from_function_response(
        #             name=fc.name,
        #             response={"result": result}
        #         ))

        #     # Add the tool results back to history as a 'user' role
        #     conversation_history.append(types.Content(
        #         role="user",
        #         parts=tool_results
        #     ))
        #     # Continue the loop for the model to process results
        # else:
        #     # No tools called, we are finished
        #     print()
        #     return