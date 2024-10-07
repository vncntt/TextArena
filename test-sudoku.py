from textarena.envs.single_player.sudoku import SudokuEnv
import time, os
from openai import OpenAI

from textarena.wrappers import (
    PrettyRenderWrapper,
    LLMObservationWrapper
)

import textarena

textarena.pprint_registry_detailed()
class GPTAgent:
    def __init__(self, model_name: str):
        """
        Initialize the GPTAgent with the specified OpenRouter model.
        
        Args:
            model_name (str): The name of the OpenAI model to use (e.g., "gpt-4").
        """
        self.model_name = model_name
        self.agent_identifier = model_name
        # Load the OpenAI API key from environment variable
        self.client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.getenv("OPENROUTER_API_KEY"))
        
    def __call__(self, observation: str) -> str:
        """
        Process the observation using the OpenRouter model and return the action.

        Args:
            observation (str): The input string to process.

        Returns:
            str: The response generated by the model.
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "user", "content": observation}
                ],
                temperature=0.7,
            )
            # Extract the assistant's reply
            action = response.choices[0].message.content.strip()
            return action
        except Exception as e:
            return f"An error occurred: {e}"
        
agent_0 = GPTAgent(
    model_name="gpt-4o-mini"
)

env = textarena.make("Sudoku-v0-easy")

env = LLMObservationWrapper(env=env)

env = PrettyRenderWrapper(env=env, max_log_lines=25)

observation, info = env.reset(seed=490)

done = False
while not done:
    # print("Current observation:", observation[0])
    action = agent_0(observation[0])
    observation, reward, truncated, terminated, info = env.step(0, action)
    time.sleep(0.5)  # Sleep for half a second to slow down the game
    env.render()
    done = terminated