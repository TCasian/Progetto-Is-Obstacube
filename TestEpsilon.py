from collections import namedtuple
import math
import arcade
import cProfile
import random
from Logica.ImpostazioniLogica import ImpostazioniLogica
from schermate.AiScreen import GiocoScreen
from Logica import GiocoAI
def main():

    larghezza_schermo = 1184
    altezza_schermo = 768
    window = arcade.Window(larghezza_schermo, altezza_schermo, "Obstacube", visible=True)
    ImpostazioniLogica().audio_var = False
    random_epsilon = random.sample([random.uniform(0.90, 1) for _ in range(1000)], 50)
    random_decay = random.sample([random.uniform(0.990, 0.999) for _ in range(1000)], 50)
    rewards_list = []
    Rewards = namedtuple("Rewards", ["reward_medio", "epsilon", "epsilon_decay"])
    game_view = GiocoScreen("ostacoli.tmx", training_mode=True)
    game_view.gioco.flag = True
    window.show_view(game_view)
    window.set_update_rate(1 / 240)


    i = 0
    while i <= 50:
        print(f"Epsilon dato all'agente: {random_epsilon[i]}, Decay dato all'agente: {random_decay[i]}")
        game_view.gioco.agents[0].epsilon = random_epsilon[i]
        game_view.gioco.agents[0].epsilon_decay = random_decay[i]
        arcade.run()

        media_rewards = sum(GiocoAI.episode_rewards)/len(GiocoAI.episode_rewards)
        rewards_list.append(Rewards(media_rewards, random_epsilon[i], random_decay[i]))
        window = arcade.Window(larghezza_schermo, altezza_schermo, "Obstacube", visible=True)
        game_view = GiocoScreen("ostacoli.tmx", training_mode=True)
        game_view.gioco.flag = True
        window.show_view(game_view)
        window.set_update_rate(1 / 240)
        i += 1

    try:
        with open("media_rewards.txt", "a+") as f:
            for el in rewards_list:
                f.write(f"Epsilon: {el.epsilon} Decay: {el.epsilon_decay} Reward medio: {el.reward_medio}0\n")
    except FileNotFoundError:
        print("Media rewards file not found")


if __name__ == "__main__":
    profiler = cProfile.Profile()
    profiler.enable()
    main()
    profiler.disable()
    profiler.dump_stats('risultati.prof')
