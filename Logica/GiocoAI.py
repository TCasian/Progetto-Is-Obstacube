import time
import matplotlib.pyplot as plt
import arcade
import numpy as np
from sympy.strategies.core import switch

from Logica.AILogica import DQNAgent
from Logica.ImpostazioniLogica import ImpostazioniLogica
from Logica.PlayerLogica import Player
from schermate.ImpostazioniScreen import ImpostazioniScreen
from utils.RoundedButtons import RoundedButton
from Logica.GiocoLogica import GiocoLogica

TILE_SCALING = 1.0
PLAYER_SPEED = 5
GRAVITY = 0.5
TILE_WIDTH = 32
TILE_HEIGHT = 32

class GiocoLogicaAi(GiocoLogica):
    def __init__(self, window, mappa, view, training_mode=True):
        super().__init__(window, mappa, view)

        self.training_mode = training_mode
        self.agent = DQNAgent(state_shape=(20, 20, 1), action_size=5)
        self.last_state = None
        self.last_action = None
        self.total_reward = 0
        self.episode = 0
        self.last_x = 0
        self.collected_coins = 0
        self.last_position = (0, 0)
        self.checkpoint = 100
        self.flag = False
        self.episode_rewards = []
        self.episode_numbers = []
        self.max_x = 0
        self.last_checkpoint = 0
        self.fase = "movimento"
        self.reward_function = self.get_reward_by_phase

        self.multiplier = 3






    def get_state(self):
        """
        crea una rappresentazione dello state attorno al player
        """

        grid = self.player.get_surrounding_grid(self.tile_grid)
        rows = len(grid)
        cols = len(grid[0]) if rows > 0 else 0
        state = np.zeros((rows, cols, 1))
        for i in range(rows):
            for j in range(cols):
                cell = grid[i][j]
                if cell == "ostacoli":
                    state[i][j][0] = -1
                elif cell == "monete":
                    state[i][j][0] = 1
                elif cell == "danni":
                    state[i][j][0] = -0.5
        return state

    def step(self, action):
        # Mappatura azioni
        if action == 0:
            if self.flag:# left
                self.player.change_x = -PLAYER_SPEED
            self.last_action = 0
        elif action == 1:
            if self.flag:# right
                self.player.change_x = PLAYER_SPEED
            self.last_action = 1
        elif action == 2:
            if self.flag:# up
                self.player.change_y = PLAYER_SPEED
            self.last_action = 2
        elif action == 3:
            if self.flag:# down
                self.player.change_y = -PLAYER_SPEED
            self.last_action = 3
        elif action == 4:  # no action
            self.player.change_x = 0
            self.last_action = 4
            self.player.change_y = 0
        self.update()

        return self.get_state(), self.reward_function(), self.finish is not None

    def _is_action_safe(self):
        # Aggiungere logica contestuale per valutare la sicurezza dell'azione
        return self.player.health > 2

    def train_episode(self):
        self.reset()
        state = self.get_state()
        done = False
        self.total_reward = 0
        step_count = 0
        max_steps = 1000

        while not done and step_count < max_steps:
            # Logica di selezione azione basata sul flag
            if self.flag:
                action = self.agent.act(state)
            else:
                action = self.get_action()  # Metodo alternativo (es. input umano)

            next_state, reward, done = self.step(action)

            # Experience replay indipendente dal flag
            self.agent.remember(state, action, reward, next_state, done)
            self.agent.replay()

            state = next_state
            self.total_reward += reward
            step_count += 1

            if step_count > 1000:
                done = True
            yield
        self.episode_rewards.append(self.total_reward)
        self.episode_numbers.append(self.episode)

        print(f"Episode: {self.episode}, Reward: {self.total_reward}, Epsilon: {self.agent.epsilon}")

        self.plot_rewards()

        if self.episode % 100 == 0:
            self.agent.update_target_model()
        self.episode += 1
        """
        if len(self.episode_numbers) >= 150:
            self.reward_function = self.get_reward_1
            self.mappa = "test.tmx"
        if len(self.episode_numbers) >= 600:
            self.reward_function = self.get_reward_2
            self.mappa = "foresta.tmx"""
        if self.agent.epsilon > self.agent.epsilon_min:
            self.agent.epsilon *= self.agent.epsilon_decay


    def get_reward_by_phase(self):
        reward = 0
        fase = self.fase
        oggetti_colpiti = {
            "ostacoli": arcade.check_for_collision_with_list(self.player, self.ostacoli),
            "monete": arcade.check_for_collision_with_list(self.player, self.monete),
            "cuori": arcade.check_for_collision_with_list(self.player, self.cuori),
            "danni": arcade.check_for_collision_with_list(self.player, self.danni)
        }



        current_x = self.player.center_x
        dx = current_x - self.last_x


        if dx < 0:
            reward -= 10 # Penalità verso sinstra
        elif dx > 0:
            reward += 10 # reward destra
        elif dx == 0:
            reward -= 15 #penalita per starsi fermo

        if fase != "movimento":
            #fase ostacoli
            if oggetti_colpiti["ostacoli"]:
                reward -= 5
            if fase != "ostacoli":
                #fase danni
                if oggetti_colpiti["danni"]:
                    reward -= 10
                    if fase != "danni":
                        #fase raccolta
                        if oggetti_colpiti["monete"]:
                            reward += 2
                        if oggetti_colpiti["cuori"]:
                            reward += 5
                            if fase != "raccolta":
                                #fase goal
                                if self.finish == "Win":
                                    reward += 500
                                if self.finish == "Gameover":
                                   reward -= 100

        self.last_x = current_x

        return reward




    def plot_rewards(self):
        plt.figure(figsize=(12, 6))
        plt.plot(self.episode_numbers, self.episode_rewards, 'b-')
        plt.xlabel('Episodi', fontsize=14)
        plt.ylabel('Reward Totale', fontsize=14)
        plt.title('Andamento del Reward durante l\'Addestramento', fontsize=16)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.savefig('training_rewards.png')
        plt.close()

    def update(self, delta_time=10):
        """
        Aggiorna lo stato del gioco per un determinato intervallo di tempo.
        Puoi includere qui l'aggiornamento del giocatore, le collisioni, l'animazione,
        lo spostamento della camera, ecc.
        """
        if self.start_pause != 0 or self.finish is not None:
            return
        self.player.update()

        # Gestisci le collisioni
        self.collisioni()

        #self.scene.update_animation(delta_time)

        # Muovi la camera
        self._muovi_camera()

    def reset(self):
        """
        Reinizializza lo stato del gioco per far partire un nuovo episodio.
        Puoi resettare la posizione del giocatore, il punteggio, la salute e altri parametri.
        """
        # Ad esempio, resetta lo stato del giocatore
        self.player.center_x = 150  # oppure un valore iniziale che preferisci
        self.player.center_y = 300
        self.player.coins = 0
        self.player.health = self.player.max_life
        self.checkpoint = 100
        self.max_x = 0
        self.last_checkpoint = 0
        self.last_x = self.player.center_x

        # Resetta il tempo di inizio e lo stato di fine partita
        self.start_time = time.time()
        self.finish = None
        self.total_reward = 0
        self.heath = 0
        self.collected_coins = 0
        self.last_position = (self.player.center_x, self.player.center_y)
        self.last_action = 0
        # Se necessario, ricarica la mappa o riposiziona gli oggetti
        self.load_map()
        self.camera = arcade.camera.Camera2D()
        self.tile_grid = self._build_tile_grid()


    def get_action(self):
        key = self.view.get_key()
        self.last_action = key
        return key