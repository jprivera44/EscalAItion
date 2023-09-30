# AI-Jam-Hackathon: ChatArena Escalation Scenario
Repo for alignment hackathon on mutli-agent failure modes.

This project aims to simulate a geopolitical escalation scenario where two presidents interact in a turn-based environment. Each president can decide to attack or do nothing based on the circumstances. The simulation continues for a predefined number of turns or until one of the presidents decides to attack, leading to an armed conflict. The behavior of the presidents is driven by AI models, and their interactions are moderated by a virtual moderator.

Files
chatarenatutorial_ai_jams.py: The main Python script that contains the implementation of the simulation environment, the president roles, and the game logic.
Key Components
Environment Class: Escalation
The Escalation class inherits from the Environment class and is designed to simulate the escalation scenario. The key methods include:

__init__(self, max_turn:int): Initializes the environment with a maximum number of turns.
reset(self): Resets the environment to its initial state.
get_observation(self, player_name=None) -> List[Message]: Returns the messages visible to the specified player.
get_next_player(self) -> str: Determines which president's turn is next.
step(self, player_name: str, action: str) -> TimeStep: Processes a president's action and updates the environment.
_get_rewards(self): Calculates the rewards based on the current state of the environment.
_get_zero_rewards(self): Returns zero rewards for both presidents.
_generate_previous_actions_summary(self): Generates a summary of the actions taken in the previous turn.
_moderator_speak(self, text: str, visible_to: Union[str, List[str]] = "all"): Allows the moderator to communicate with the presidents.
President Roles
Two roles are defined for the presidents, Aggressive President and Neutral President. Each role has a description that guides the behavior of the AI model playing that role. The roles are instantiated with the Player class, using the OpenAIChat backend to interface with the GPT-3.5-turbo model from OpenAI.

Simulation Logic
The simulation is carried out in a turn-based manner. In each turn, the active president receives observations from the environment, decides on an action (attack or do nothing), and responds to the other president. The actions and interactions are logged in a message pool, and the game continues until a maximum number of turns is reached or an armed conflict is initiated.

Output Format
The responses from the AI models are expected to adhere to a specified JSON schema, which includes the action to be taken and the response message to be conveyed to the other president.

Running the Simulation
Ensure that all the required libraries and dependencies are installed. Run the chatarenatutorial_ai_jams.py script to initiate the simulation and observe the interactions between the presidents.
