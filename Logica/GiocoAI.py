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
import math

TILE_SCALING = 1.0
PLAYER_SPEED = 10
GRAVITY = 0.5
TILE_WIDTH = 32
TILE_HEIGHT = 32

# fase - mappa - reward per next mappa

FASI_TRAINING = {
    "movimento" : ("intro.tmx", 2800),
    "ostacoli"  : ("ostacoli.tmx", 5000),
    "danni"     : ("danni.tmx", 6000),
    "raccolta"  : ("raccolta.tmx", 7500),
    "goal"      : ("goal.tmx", 8500)
}

#Episode: 187, Reward: 1665, Epsilon: 0.4433730476621029, Decay 0.993 per ostacoli migliroe
#Episode: 240, Reward: -195, Epsilon: 0.2496820394481045, Decay 0.988  per ostacoli migliroe1


class GiocoLogicaAi(GiocoLogica):
    def __init__(self, window, mappa, view, training_mode=True):
        self.fase = "movimento"
        super().__init__(window, FASI_TRAINING[self.fase][0], view)

        self.training_mode = training_mode
        self.agent = DQNAgent(state_shape=(20, 20, 1), action_size=5)
        self.agent.load("pesi.pth")
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
        self.reward_function = self.get_reward_by_phase

        self.multiplier = 3

        #attributi per tenere traccia reward cumulativi
        self.last_dx = 0
        self.last_colpito = False
        self.max_x = 0
        self.collision_cooldown = 0.3
        self.last_hit_time = 0


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
                if cell == 1:
                    state[i][j][0] = -1
                elif cell == 3:
                    state[i][j][0] = 1
                elif cell == 2:
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
        self.update(1 / 120)

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

        print(f"Episode: {self.episode}, Reward: {self.total_reward}, Epsilon: {self.agent.epsilon}, Decay {self.agent.epsilon_decay}")

        self.plot_rewards()

        if self.episode > 0 and self.episode % 100 == 0:
            self.agent.update_target_model()
            self.agent.save("pesi.pth")
            self.agent.epsilon_decay -= 0.005
            print(f"Decay rate aumentato a {self.agent.epsilon}")

        self.episode += 1

        #print(f"{self.total_reward} > {FASI_TRAINING[self.fase][1]} = {self.total_reward > FASI_TRAINING[self.fase][1]}")
        if self.total_reward > FASI_TRAINING[self.fase][1]:

            fasi_keys = list(FASI_TRAINING.keys())
            current_index = fasi_keys.index(self.fase)
            if current_index < len(fasi_keys) - 1:
                self.fase = fasi_keys[current_index + 1]
                self.mappa = FASI_TRAINING[self.fase][0]
                print(f"Fase cambiata a: {self.fase}, nuova mappa: {self.mappa}, Epsilon 1 decay 0.990")
                self.agent.epsilon = 1
                self.agent.epsilon_decay = 0.998
                #chiamata per aggiornare la lista ostacoli ecc
                self.load_map()
                self.episode = 0

        if self.agent.epsilon > self.agent.epsilon_min:
            self.agent.epsilon *= self.agent.epsilon_decay


    def get_reward_by_phase(self):
        reward = 0
        fase = self.fase
        current_time = time.time()

        dx = self.player.center_x - self.last_x

        #print(f"{oggetti_colpiti["ostacoli"]}")

        if dx < 0:
            reward -= 10  #penalita se torna indietro
            if self.last_dx < 0:
                reward -= 20 # penalita se continua ad tornare indietro
        elif dx > 0:
            reward += 10  # reward destra
            if self.last_dx > 0:
                reward += 20  # reward destra continua
        elif dx == 0:
            reward -= 15 #penalita per starsi ferm
            if self.last_dx == 0:
                reward -= 25 #penalita se si sta ancora fermo

        if fase != "movimento":
            #fase ostacoli
            if self.oggetti_colpiti["ostacoli"]:
                if current_time - self.last_hit_time > self.collision_cooldown:
                    reward -= 10 #
                    #print("Colpito -10")
                    if self.last_colpito:
                        reward -= 20  # penalita aggiuntiva se continua a colpire
                        #print("Colpito ancora -20")
                    self.last_hit_time = current_time
                    self.last_colpito = True
                else:
                    self.last_colpito = False
                if fase != "ostacoli":
                        #fase danni
                        if self.oggetti_colpiti["danni"]:
                            reward -= 10
                            if fase != "danni":
                                #fase raccolta
                                if self.oggetti_colpiti["monete"]:
                                    reward += 3
                                if self.oggetti_colpiti["cuori"]:
                                    reward += 5
                                    if fase != "raccolta":
                                        #fase goal
                                        if self.finish == "Win":
                                            reward += 500
                                        if self.finish == "Gameover":
                                           reward -= 100
            else:
                # non ha colpito reward se non è mai arrivato qua (32 px per grid per evitare reward continui ad ogni movimento)
                if self.player.center_x > self.max_x:
                    reward += 10
                    #print("nuovo traguardo +10")
                    if not self.last_colpito:
                        reward += 20
                        #print("nuovo traguardo ancora +20")
                    self.last_colpito = False
                    # se era anche vicino ad un ostacolo ma non ha colpito
                    if self.player.ostacolo_vicino:
                        reward += 10



        self.last_x = self.player.center_x
        self.last_dx = dx
        if self.player.center_x > self.max_x:
            self.max_x = self.player.center_x + 32

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

    def update(self, delta_time):
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

        self.scene.update_animation(delta_time)

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

