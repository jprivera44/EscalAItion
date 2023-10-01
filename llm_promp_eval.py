# code to prompt a LLM with evaluation data, passing in
# the evaluation data as a context

import openai
import requests
import json


# Other imports as necessary
def query_gpt4(prompt):
    # Replace with your actual API endpoint and authorization
    url = "https://api.openai.com/v1/engines/davinci/completions"
    headers = {
        "Authorization": "Bearer your-api-key",
    }
    data = {
        "prompt": prompt,
        "max_tokens": 150,
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()["choices"][0]["text"].strip()


def combine_prompt_info(world: World, nation_name: str):
    """User prompt for nation models. Mostly describes the state of the world history."""
    nation_descriptions_static = format_nation_descriptions_static(world)

    past_action_history = ""

    for day, actions in world.action_history.items():
        past_action_history += f"Day {day}:\n"
        for action in actions:
            # Look up if the action is private or public
            action_privacy_level = world.action_config.loc[
                world.action_config["name"] == action.name
            ]["privacy level"].values[0]

            action_is_public = False  # For this particular action instance
            if action_privacy_level == "Public":
                action_is_public = True
            elif action_privacy_level == "Private":
                action_is_public = False
            else:
                assert action_privacy_level == "Public or Private"
                assert action.name == "Message"  # Only allowed for messages for now
                action_is_public = True if action.other == "World" else False

            # If private and nation_name is not involved, don't show it to nation_name
            if not action_is_public and nation_name not in [
                action.self,
                action.other,
            ]:
                continue

            past_action_history += f"{action.self} -> {action.other} : {action.name}"
            if action.content:
                past_action_history += f" {action.content}"
            past_action_history += "\n"
        past_action_history += "\n"

    nation_states_dynamic = format_nation_states_dynamic(world)

    return f"""## Static descriptions of each nation (constant) ##
{nation_descriptions_static}

## History of past actions. Format: performer -> recipient : Action ##
{past_action_history if past_action_history else "No actions have been taken yet."}

## Current state of each nation ##
{nation_states_dynamic}

## Current state of the world (will be affected by actions) ##
It is currently day {world.current_day} out of {world.max_days} total days. 

As the commander of {nation_name}, please reply with a valid JSON object containing your reasoning and actions.
"""


def main():
    # Generate prompt for GPT-4 based on game output
    prompt = f"Analyze the following game output: {game_output}"

    # Query GPT-4
    gpt4_response = query_gpt4(prompt)

    # save the results to a json file
    with open("evaluation_results.json", "w") as outfile:
        json.dump(evaluation_results, outfile)


if __name__ == "__main__":
    main()
