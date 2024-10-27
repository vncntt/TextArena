""" Don't Say It Game Environment """
import textarena as ta

import random
import nltk
from nltk import pos_tag
from nltk.corpus import words
from typing import Any, Dict, Optional, Tuple, List


nltk.download("words")
nltk.download("averaged_perceptron_tagger_eng")


class DontSayItEnv(ta.Env):
    """Environment for Don't Say It game"""
    def __init__(
        self,
        hardcore: Optional[bool] = False,
        max_turns: Optional[int] = None,
    ):
        """
        Initialize the 'Don't Say It' game environment.

        Args:
            hardcore (bool): If True, use the full English word set; otherwise, use a simplified word set.
            max_turns (int): Maximum number of turns before the game ends in a draw.
        """
        # Load the word list
        self._load_word_list(hardcore=hardcore)

        # Initialize game state (mostly used by wrappers, especially rendering)
        self.state = ta.State(
            num_players=2,
            max_turns=max_turns,
            render_keys=["target_words"],
        )

    def _load_word_list(self, hardcore: bool = False) -> None:
        """
        Load the word list based on the 'hardcore' parameter.

        Args:
            hardcore (bool): Determines whether to load the full or simplified word list.
        """
        # Get word list
        if hardcore:
            word_list = words.words("en")
        else:
            word_list = words.words("en-basic")

        # Filter words based on POS tags
        # NN: Noun, VB: Verb, JJ: Adjective
        self.word_list = [
            word for word in word_list if pos_tag([word])[0][1] in ["NN", "VB", "JJ"]
        ]

    def reset(
        self, seed: Optional[int] = None
    ) -> Optional[ta.Observations]:
        """
        Reset the 'Don't Say It' game to its initial state.

        Args:
            seed (Optional[int]): Seed for the random number generator to ensure reproducibility.

        Returns:
            Optional[ta.Observations]: Initial observations for both players as a dictionary.
        """
        if seed is not None:
            random.seed(seed)
        else:
            random.seed()

        # Assign secret words to players
        target_words = {
            0: random.choice(self.word_list),
            1: random.choice(self.word_list),
        }
        while target_words[0] == target_words[1]:
            target_words[1] = random.choice(self.word_list)

        return self.state.reset(
            game_state={"target_words": target_words},
            player_prompt_function=self._generate_player_prompt
        )


    def _generate_player_prompt(self, player_id: int) -> str:
        """
        Generate the initial prompt for a player, providing them with their secret word and instructions.

        Args:
            player_id (int): ID of the player (0 or 1).

        Returns:
            ta.Message: Initial prompt for the player.
        """
        prompt = (
            f"You are playing 'Don't Say It'. You are Player {player_id}\n"
            f"Your secret word is: '{self.state.game_state['target_words'][player_id]}'.\n"
            "Your goal is to get the other player to say your secret word before you say theirs.\n"
            "You can converse freely, but try to be subtle to avoid making it obvious.\n"
            "On your turn, simply type your message.\n"
        )
        if self.state.max_turns:
            prompt += f"The game lasts for {self.state.max_turns} turns in total.\n"
        return prompt

    def step(
        self,
        player_id: int,
        action: str,
    ) -> Tuple[
        Optional[ta.Observations], # Observations: Dict[int, Tuple[int, str]]
        Optional[ta.Rewards], # Rewards: Dict[int, int]
        bool, # Truncated
        bool, # Terminated
        ta.Info, # Info: Optional[Dict[str, Any]]
    ]:
        """
        Process the player's action.

        Args:
            player_id (int): The player's ID (0 or 1).
            action (str): The player's message.

        Returns:
            tuple: (observations, rewards, truncated, terminated, info)
        """
        # check the player_id and action fromat
        self.state.check_action_format(
            action=action,
            player_id=player_id
        )

        # update the observations and log the action
        self.state.add_observation(
            from_id=player_id,
            to_id=-1, # Broadcast to all
            message=action,
            for_logging=True
        )

        # Check if the action mentions the opponent's secret word
        if self.state.game_state["target_words"][1 - player_id].lower() in action.lower():
            self.state.set_winners(
                player_ids=[1-player_id], # opponent wins
                reason=f"Player {player_id} mentioned the opponent's secret word."
            )            

        return self.state.step()


    def render(self):
        """
        Render minimal game state.
        """
        print(f"Turn: {self.state.turn}")
        print("\nRecent Game Logs:")
        recent_logs = self.state.logs[-5:]  # Display the last 5 logs
        for sender_id, log in recent_logs:
            if sender_id == ta.GAME_ID:
                print(f"[GAME] {log}")
            else:
                print(f"[Player {sender_id}] {log}")

