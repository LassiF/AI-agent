import os
from google.genai import types

schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="writes to file in a specified directory relative to the working directory",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Directory path to write to, relative to the working directory (default is the working directory itself)",
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="content to be written into file_path"
            )
        },
    ),
)

def write_file(working_directory: str, file_path: str, content: str) -> str:
    try:
        abs_working_dir = os.path.abspath(working_directory)
        abs_file_path = os.path.normpath(os.path.join(abs_working_dir, file_path))
        if os.path.commonpath([abs_working_dir, abs_file_path]) != abs_working_dir:
            return f'Error: Cannot write "{file_path}" as it is outside the permitted working directory'
        if os.path.isdir(abs_file_path):
            return f'Error: Cannot write to "{file_path}" as it is a directory'
        
        parent_dir = os.path.dirname(abs_file_path)

        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)

        file = open(abs_file_path, "w") #there was bug here, use abs path not relative path
        file.write(content)
        file.close()

        return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'
    except Exception as e:
        return f"Error {e}"