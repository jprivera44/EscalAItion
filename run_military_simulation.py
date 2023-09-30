"""
Main simulation loop to run the military simulation.
"""

from dataclasses import dataclass
import os
import sys
import time
import argparse
import yaml
import numpy as np
import random
import pandas as pd
from datetime import datetime
from collections import defaultdict

from agents import model_name_to_agent
from data_types import Action
from prompts import get_agent_system_prompt, get_agent_user_prompt, get_moderator_system_prompt, get_model_user_prompt 


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--num_turns', type=int, default=10,
                        help='Number of turns to simulate')
    parser.add_argument('--agent_model', type=str, default='gpt-3.5-turbo-0613',
                        help='Agent model to use')
    parser.add_argument('--moderator_model', type=str, default='gpt-3.5-turbo-0613',)
    parser.add_argument('--agent_spec_filepath', type=str, default='data/agent_specs/debug.yaml',)
    args = parser.parse_args()

    # Load agent specification
    with open(args.agent_spec_filepath, 'r') as file:
        all_agent_specs = yaml.safe_load(file)

    #commenting this out for now
    #actions_spec = pd.read_csv('data/actions_spec.csv')

    #hard code in a pandas datafrae for the actions spec


    # Define the lists
    event_names = ['nuclear_launch_detected', 'random_drone_strike', 'power_outage', 'cyber_attack', 'negotiation']
    actions = ['Action1', 'Action2', 'Action3', 'Action4', 'Action5']
    severities = ['Low', 'Medium', 'High']

    # Define some hardcoded economic impact values
    economic_impact_values = np.random.uniform(-1.0, 1.0, 15)  # Generating 15 random values as an example

    # Create a list of dictionaries where each dictionary represents a row in the DataFrame
    data = [
        {'event_name': 'nuclear_launch_detected', 'economic_impact': economic_impact_values[0], 'action': 'Action1', 'severity': 'High'},
        {'event_name': 'random_drone_strike', 'economic_impact': economic_impact_values[1], 'action': 'Action2', 'severity': 'Medium'},
        {'event_name': 'power_outage', 'economic_impact': economic_impact_values[2], 'action': 'Action3', 'severity': 'Low'},
        {'event_name': 'cyber_attack', 'economic_impact': economic_impact_values[3], 'action': 'Action4', 'severity': 'High'},
        {'event_name': 'negotiation', 'economic_impact': economic_impact_values[4], 'action': 'Action5', 'severity': 'Medium'}
    ]

    # Convert the list of dictionaries to a DataFrame
    actions_spec = pd.DataFrame(data)
        

    #store the prompts, and the specifications inthe current state 

    # Initialize things
    agents = [model_name_to_agent(agent_spec) for agent_spec in all_agent_specs]
    num_turns = args.num_turns
    
    moderator = 


    with open('prompts/events.yaml', 'r') as file:
        events_data = yaml.safe_load(file)

    # Main simulation loop
    for turn_index in range(num_turns):

        # 1. Roll some random events
        #select random events fromt the random events yaml file
        event_index = np.random.choice(len(events_data['events']))  # Assuming equal probabilities for simplicity
        random_event = events_data['events'][event_index]

        # #once the random event is selected, it is added to the message history, with moves from both sides
        # queued_actions.append(Action(
        #     sender='moderator',
        #     recipient='all',
        #     content=random_event['prompt'],
        #     turn_index=turn_index,
        # ))
 
        # 2. Query the models
        queued_actions: Action = []
        for model in models:
            response = model.query()

            queued_actions.append(Action(
                sender=model.name,
                recipient=model.recipient,
                content=response.message,
                timestamp=datetime.now(),
            ))

        # 3. Execute the queued actions by asking the moderator
        moderator_prompt = prompts.get_moderator_prompt(queued_actions, agents)
        moderator_response = moderator.query(moderator_prompt)

if __name__ == '__main__':
    main()