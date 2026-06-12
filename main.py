import os
import argparse
from dotenv import load_dotenv
from google import genai
from google.genai import types

from prompts import system_prompt
from call_function import available_functions, call_function


def main():
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("API key was not found")

    client = genai.Client(api_key=api_key)

    parser = argparse.ArgumentParser(description="Chatbot")
    parser.add_argument("user_prompt", type=str)
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    messages = [
        types.Content(role="user", parts=[types.Part(text=args.user_prompt)])
    ]

    for i in range(20):

        response = generate_content(client, messages, args.verbose)

        # 1. Add model candidates to history
        if response.candidates:
            for candidate in response.candidates:
                messages.append(candidate.content)

        # 2. If no function calls → we are DONE
        if not response.function_calls:
            print("Final response:")
            print(response.text)
            return

        # 3. Handle function calls
        function_results = []

        for function_call in response.function_calls:
            result = call_function(function_call)

            if result.parts[0].function_response is None:
                raise Exception("function_response is None")

            function_results.append(result.parts[0])

            if args.verbose:
                print(f"-> {result.parts[0].function_response.response}")

        # 4. Add tool results back into conversation
        messages.append(
            types.Content(role="user", parts=function_results)
        )

    print("Max iterations reached without final response.")
    exit(1)


def generate_content(client, messages, verbose):
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=messages,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            tools=[available_functions],
        ),
    )

    if not response:
        raise RuntimeError("No response")

    if verbose:
        print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
        print(f"Response tokens: {response.usage_metadata.candidates_token_count}")

    print("Response:")
    print(response.text)

    return response


if __name__ == "__main__":
    main()