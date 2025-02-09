import time
import matplotlib.pyplot as plt
import arcade
import numpy as np
from sympy.printing.pretty.pretty_symbology import center
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
    "ostacoli"  : ("Ostacoli.tmx", 5000),
    "danni"     : ("danni.tmx", 6000),
    "raccolta"  : ("raccolta.tmx", 7500),
    "goal"      : ("goal.tmx", 8500)
}

#Episode: 187, Reward: 1665, Epsilon: 0.4433730476621029, Decay 0.993 per ostacoli migliroe
#Episode: 240, Reward: -195, Epsilon: 0.2496820394481045, Decay 0.988  per ostacoli migliroe1
#Episode: 8, Reward: -305, Epsilon: 0.6244504783240336, Decay 0.995
# Episode: 38, Reward: 890, Epsilon: 0.5372673201835692, Decay 0.995

class GiocoLogicaAi(GiocoLogica):
    def __init__(self, window, mappa, view, training_mode=True, multiple = 1):
        self.fase = "movimento"
        super().__init__(window, FASI_TRAINING[self.fase][0], view, multiple)
        self.training_mode = training_mode
        self.multiple = multiple
        self.agents = [DQNAgent(state_shape=(20, 20, 1), action_size=5) for i in range(0, multiple)]
        for agent in self.agents:
            agent.load("pesi.pth")
        self.last_state = None
        self.last_action = None
        self.total_reward = 0
        self.episode = 0
        self.collected_coins = 0
        self.last_position = (0, 0)
        self.checkpoint = 100
        self.flag = True
        self.episode_rewards = []
        self.episode_numbers = []
        self.last_checkpoint = 0
        self.reward_function = self.get_reward_by_phase

        self.multiplier = 3


        #attributi per tenere traccia reward cumulativi
        self.last_dx = [0 for _ in range(self.multiple)]
        self.last_colpito = [False for _ in range(self.multiple)]
        self.max_x = [0 for _ in range(self.multiple)]
        self.collision_cooldown = 1
        self.last_hit_time = [0 for _ in range(self.multiple)]
        self.last_x = [0 for _ in range(self.multiple)]
        self.finish = [None for _ in range(self.multiple)]

    def get_state(self, index):
        """
        Crea una rappresentazione dello stato attorno al player specificato
        """
        grid = self.players[index].get_surrounding_grid(self.tile_grid)
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

    def step(self, actions):
        next_states = []
        rewards = []
        dones_list = []

        for index in range(0, self.multiple):
            action = actions[index]
                # Mappatura delle azioni per ogni agente
            if action == 0:  # left
                if self.flag:
                    self.players[index].change_x = -PLAYER_SPEED
                    #self.players[index].update()
                self.last_action[index] = 0
            elif action == 1:  # right
                if self.flag:
                    self.players[index].change_x = PLAYER_SPEED
                    #self.players[index].update()
                self.last_action[index] = 1
            elif action == 2:  # up
                if self.flag:
                    self.players[index].change_y = PLAYER_SPEED
                    #self.players[index].update()
                self.last_action[index] = 2
            elif action == 3:  # down
                if self.flag:
                    self.players[index].change_y = -PLAYER_SPEED
                    #self.players[index].update()
                self.last_action[index] = 3
            elif action == 4:  # no action
                self.players[index].change_x = 0
                self.players[index].change_y = 0
                self.last_action[index] = 4
            #print(f"index {index} {self.players[index].center_x} {self.players[index].center_y} ")


        # Dopo aver aggiornato le azioni di tutti gli agenti, aggiorniamo l'ambiente
        self.update(1 / 240)  # Questo aggiorna tutto insieme

        # Ora raccogliamo i risultati per ogni agente
        for i, agent in enumerate(self.agents):
            print(f"flag - {i} con {self.finish}")
            next_state = self.get_state(i)
            reward = self.reward_function(i)
            done = self.finish[i] is not None  # Ogni agente ha il proprio flag di fine

            next_states.append(next_state)
            rewards.append(reward)
            dones_list.append(done)

        return next_states, rewards, dones_list

    def _is_action_safe(self):
        # Aggiungere logica contestuale per valutare la sicurezza dell'azione
        return self.player.health > 2

    def train_episode(self):
        self.reset()
        states = [self.get_state(i) for i in range(self.multiple)]  # Ogni agente ha il proprio stato iniziale
        dones = [False for _ in self.agents]
        total_rewards = [0 for _ in self.agents]
        step_count = 0
        max_steps = 1000

        while not all(dones) and step_count < max_steps:
            actions = []

            # Ogni agente sceglie un'azione basata sul proprio stato
            for i, agent in enumerate(self.agents):
                if not dones[i]:
                    action = agent.act(states[i]) #if self.flag else self.get_action()
                    actions.append(action)
                    #print(f"aggiunta action {action} ora {actions}")
                else:
                    actions.append(None)  # L'agente ha finito, quindi non fa nulla

            # Esegui tutte le azioni simultaneamente nell'ambiente
            next_states, rewards, dones_list = self.step(actions)

            # Ogni agente aggiorna la propria memoria ed effettua il replay
            for i, agent in enumerate(self.agents):
                if not dones[i]:
                    agent.remember(states[i], actions[i], rewards[i], next_states[i], dones_list[i])
                    agent.replay()

                    states[i] = next_states[i]
                    total_rewards[i] += rewards[i]
                    dones[i] = dones_list[i]

            step_count += 1
            yield

        self.episode_rewards.append(np.mean(total_rewards))
        self.episode_numbers.append(self.episode)

        print(f"Episode: {self.episode}, Mean Reward: {np.mean(total_rewards)}, Epsilon: {self.agents[0].epsilon}")

        self.plot_rewards()

        # Aggiornamento modelli ogni 100 episodi
        if self.episode > 0 and self.episode % 100 == 0:
            for i, agent in enumerate(self.agents):
                agent.update_target_model()
                agent.save(f"pesi_agent_{i}.pth")
                agent.epsilon_decay -= 0.002
                print(f"Decay rate aumentato per Agent {i}: {agent.epsilon}")

        self.episode += 1

        # Cambio fase se necessario
        if np.mean(total_rewards) > FASI_TRAINING[self.fase][1]:
            fasi_keys = list(FASI_TRAINING.keys())
            current_index = fasi_keys.index(self.fase)
            if current_index < len(fasi_keys) - 1:
                self.fase = fasi_keys[current_index + 1]
                self.mappa = FASI_TRAINING[self.fase][0]
                print(f"Fase cambiata a: {self.fase}, nuova mappa: {self.mappa}")

                for agent in self.agents:
                    agent.epsilon = 1
                    agent.epsilon_decay = 0.995

                self.load_map()
                self.episode = 0

        # Decay epsilon per tutti gli agenti
        for agent in self.agents:
            if agent.epsilon > agent.epsilon_min:
                agent.epsilon *= agent.epsilon_decay

    def get_reward_by_phase(self, index):
        reward = 0
        fase = self.fase
        current_time = time.time()

        dx = self.players[index].center_x - self.last_x[index]

        #print(f"{oggetti_colpiti["ostacoli"]}")

        if dx < 0:
            reward -= 10  #penalita se torna indietro
            if self.last_dx[index] < 0:
                reward -= 20 # penalita se continua ad tornare indietro
        elif dx > 0:
            reward += 10  # reward destra
            if self.last_dx[index] > 0:
                reward += 20  # reward destra continua
        elif dx == 0:
            reward -= 15 #penalita per starsi ferm
            if self.last_dx[index] == 0:
                reward -= 25 #penalita se si sta ancora fermo

        if fase != "movimento":
            #fase ostacoli
            if self.oggetti_colpiti[index]["ostacoli"]:
                if current_time - self.last_hit_time[index] > self.collision_cooldown:
                    reward -= 10 #
                    #print("Colpito -10")
                    if self.last_colpito[index]:
                        reward -= 10  # penalita aggiuntiva se continua a colpire
                        #print("Colpito ancora -20")
                    self.last_hit_time[index] = current_time
                    self.last_colpito[index] = True
                else:
                    self.last_colpito[index] = False
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
                if self.players[index].center_x > self.max_x[index]:
                    reward += 10
                    #print("nuovo traguardo +10")
                    if not self.last_colpito:
                        reward += 20
                        #print("nuovo traguardo ancora +20")
                    self.last_colpito[index] = False
                    # se era anche vicino ad un ostacolo ma non ha colpito
                    if self.players[index].ostacolo_vicino:
                        reward += 10



        self.last_x[index] = self.players[index].center_x
        self.last_dx[index] = dx
        if self.players[index].center_x > self.max_x[index]:
            self.max_x[index] = self.players[index].center_x + 32

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
        if self.start_pause != 0:
            for finish in self.finish:
                if finish is not None:
                    #print("esco")
                    return

        for index in range(self.multiple):
            #print("Update ")
            self.players[index].update()

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

        for p in self.players:
            p.center_x = 150  # oppure un valore iniziale che preferisci
            p.center_y = 300
            p.coins = 0
            p.health = 5


        self.checkpoint = 100

        self.last_checkpoint = 0
        self.last_dx = [0 for _ in range(self.multiple)]
        self.last_colpito = [False for _ in range(self.multiple)]
        self.max_x = [0 for _ in range(self.multiple)]
        self.collision_cooldown = 1
        self.last_hit_time = [0 for _ in range(self.multiple)]
        self.last_x = [0 for _ in range(self.multiple)]

        # Resetta il tempo di inizio e lo stato di fine partita
        self.start_time = time.time()
        self.finish = [None for _ in range (self.multiple)]
        self.total_reward = 0
        self.heath = 0
        self.collected_coins = 0
        self.last_position = (self.player.center_x, self.player.center_y)
        self.last_action = [0 for i in range(self.multiple)]
        # Se necessario, ricarica la mappa o riposiziona gli oggetti
        self.load_map()
        self.camera = arcade.camera.Camera2D()
        self.tile_grid = self._build_tile_grid()


    def get_action(self):
        key = self.view.get_key()
        self.last_action = key
        return key

