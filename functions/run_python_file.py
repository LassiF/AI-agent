import os
import subprocess
from google.genai import types

schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Run a python file in a specified directory relative to the working directory",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Directory path to the python file which will be run, relative to the working directory (default is the working directory itself)",
            ),
            "args": types.Schema(
                type=types.Type.ARRAY,
                items=types.Schema(
                    type=types.Type.STRING,
                ),
                description="Optional list of arguments to pass to the Python script"
            )
        },
        required=["file_path"]
    ),
)

def run_python_file(
        working_directory: str, file_path: str, args: list[str] | None = None
) -> str:
    
    try:
        abs_working_dir = os.path.abspath(working_directory)
        abs_file_path = os.path.normpath(os.path.join(abs_working_dir, file_path))
        if os.path.commonpath([abs_working_dir, abs_file_path]) != abs_working_dir:
            return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
        if os.path.isfile(abs_file_path) == False:
            return f'Error: "{file_path}" does not exist or is not a regular file'
        if file_path[-3:] != ".py":
            return f'Error: "{file_path}" is not a Python file'
        #Checks have passed now execute as a child process
        command = ["uv", "run", "python3", abs_file_path]
        if args:
            command.extend(args)
        completed_process = subprocess.run(command, text=True, timeout=30, capture_output=True) # this is an object
        output_string = ""
        if completed_process.returncode != 0:
            output_string += f"Process exited with code {completed_process.returncode}"
        if not completed_process.stderr and not completed_process.stdout:
            output_string += f" No output produced"
            return output_string
        output_string += f" STDOUT: {completed_process.stdout}"
        output_string += f" STDERR: {completed_process.stderr}"
        return output_string

    except Exception as e:
        return f"Error: executing Python file {file_path}\nEncountered: {e}"