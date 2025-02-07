import time
import matplotlib.pyplot as plt
import arcade
import numpy as np


from Logica.AILogica import DQNAgent
from Logica.ImpostazioniLogica import ImpostazioniLogica
from Logica.PlayerLogica import Player
from schermate.ImpostazioniScreen import ImpostazioniScreen
from utils.RoundedButtons import RoundedButton

TILE_SCALING = 1.0
PLAYER_SPEED = 5
GRAVITY = 0.5
TILE_WIDTH = 32
TILE_HEIGHT = 32

class GiocoLogica():
    def __init__(self, window, mappa, view, training_mode=True):
        self.camera = arcade.camera.Camera2D()
        self.window = window
        self.view = view
        self.mappa = mappa
        self.tilemap = None
        self.load_map()
        self.load()
        self.cuoriList = []
        self.moneteList = []
        self.playerposition_x = 150
        self.playerposition_y = 300
        self.player = Player(150, 300)
        self.start_time = time.time()
        self.tile_grid = self._build_tile_grid()
        self.start_pause = 0
        self.saved = False
        self.finish = None

        self.training_mode = training_mode
        self.agent = DQNAgent(state_shape=(20, 20, 1), action_size=5)
        self.last_state = None
        self.last_action = None
        self.total_reward = 0
        self.episode = 0
        self.last_x = 0
        self.health = 0
        self.collected_coins = 0
        self.last_position = (0, 0)
        self.checkpoint = 100
        self.flag = False
        self.episode_rewards = []
        self.episode_numbers = []
        self.max_x = 0
        self.last_checkpoint = 0
        self.reward_funcution = self.get_reward


    def load_map(self):
        self.tilemap = arcade.load_tilemap(f"Media/mappe/{self.mappa}",TILE_SCALING if not ImpostazioniLogica().is_fullscreen() else 1.3)
        self.scene = arcade.Scene.from_tilemap(self.tilemap)
        self.ostacoli = self.scene["ostacoli"] if "ostacoli" in self.scene else arcade.SpriteList()
        self.bombe = self.scene["bombe"] if "bombe" in self.scene else arcade.Sprite()
        self.monete = self.scene["monete"] if "monete" in self.scene else arcade.SpriteList()
        self.danni = self.scene["danni"] if "danni" in self.scene else arcade.SpriteList()
        self.cuori = self.scene["cuori"] if "cuori" in self.scene else arcade.SpriteList()

    def load(self):
        self.monete.rescale(1.3)
        self.cuore_pieno_sprite = arcade.Sprite("Media/img/cuore_pieno.png", scale=1.3)
        self.cuore_vuoto_sprite = arcade.Sprite("Media/img/cuore_vuoto.png", scale=1.3)

    def resize(self):
        self.monetepos = []
        for moneta in self.monete:
            self.monetepos.append((moneta.center_x, moneta.center_y))
        self.monete.rescale(1.3)
        for moneta, pos in zip(self.monete, self.monetepos):
            moneta.center_x, moneta.center_y = pos
        self.cuori = self.scene["cuori"] if "cuori" in self.scene else arcade.SpriteList()
        self.danni = self.scene["danni"] if "danni" in self.scene else arcade.SpriteList()
        self.scaling = TILE_SCALING if not ImpostazioniLogica().is_fullscreen() else 1.3
        for moneta in list(self.monete):
            posizione = (round(moneta.center_x / self.scaling), round(moneta.center_y / self.scaling))
            if posizione in self.moneteList:
                moneta.remove_from_sprite_lists()
        for cuore in list(self.cuori):
            posizione = (round(cuore.center_x / self.scaling), round(cuore.center_y / self.scaling))
            if posizione in self.cuoriList:
                cuore.remove_from_sprite_lists()
        self.player.center_x = round(self.playerposition_x * self.scaling)
        self.player.center_y = round(self.playerposition_y * self.scaling)

    def print_player_grid(self):
        """
        Stampa una porzione della griglia centrata sul giocatore.
        """
        grid = self.player.get_surrounding_grid(self.tile_grid)

        print("\nGriglia centrata sul giocatore:")
        for row in grid[::-1]:
            print(row)
        print("\n")

    def _build_tile_grid(self):
        grid = [["[]" for _ in range(self.tilemap.width)] for _ in range(self.tilemap.height)]

        for sprites in [self.ostacoli, self.monete, self.cuori, self.danni]:
            for sprite in sprites:
                x = int(sprite.center_x // self.tilemap.tile_width)
                y = int(sprite.center_y // self.tilemap.tile_height)
                if 0 <= x < self.tilemap.width and 0 <= y < self.tilemap.height:
                    grid[y][x] = sprite.properties.get("tipo", "ostacoli")

        return grid

    def _create_buttons(self):
        button_height = 60
        button_width = 350
        button_spacing = 30
        buttons_data = [
            ("Torna al menu ", lambda:  self._go_menu()),
            ("Come giocare ", lambda: print("aa")),
            ("Impostazioni ", lambda: self.window.show_view(ImpostazioniScreen(self.view))),
            ("Torna al gioco ", lambda: setattr(self, "start_pause", 0)),

        ]

        start_y = self.window.height - 540

        self.paused_buttons = []
        self.finish_buttons_gameover = []
        self.finish_buttons_win = []

        for i, (label, callback) in enumerate(buttons_data):
            x = self.camera.position[0]
            y = start_y + i * (button_height + button_spacing)

            button = RoundedButton(
                text=label,
                center_x=x,
                center_y=y,
                width=button_width,
                height=button_height,
                bg_color=(240,255,240),
                bg_hover=(217, 147, 8),
                text_color=arcade.color.BLACK,
                text_size=20,
                hover_text_color=arcade.color.WHITE,
                callback=callback,
                bold=True
            )
            self.paused_buttons.append(button)

        self.finish_buttons_gameover.append(RoundedButton(
            text="Riprova!",
            center_x=self.camera.position[0] - 200,
            center_y=self.camera.position[1] - (200 if not ImpostazioniLogica().is_fullscreen() else 180),
            width=button_width,
            height=button_height,
            bg_color=(240, 255, 240),
            bg_hover=(217, 147, 8),
            text_color=arcade.color.BLACK,
            text_size=20,
            hover_text_color=arcade.color.WHITE,
            callback=lambda: self.retry,
            bold=True
        ))

        self.finish_buttons_gameover.append(RoundedButton(
            text="Torna al menu!",
            center_x=self.camera.position[0] + 200,
            center_y=self.camera.position[1] - (200 if not ImpostazioniLogica().is_fullscreen() else 180),
            width=button_width,
            height=button_height,
            bg_color=(240, 255, 240),
            bg_hover=(217, 147, 8),
            text_color=arcade.color.BLACK,
            text_size=20,
            hover_text_color=arcade.color.WHITE,
            callback= lambda: self._go_menu(),
            bold=True
        ))

        self.finish_buttons_win.append(RoundedButton(
            text="Nuova partita",
            center_x=self.camera.position[0] - 200,
            center_y=self.camera.position[1] - (200 if not ImpostazioniLogica().is_fullscreen() else 180),
            width=button_width,
            height=button_height,
            bg_color=(240, 255, 240),
            bg_hover=(217, 147, 8),
            text_color=arcade.color.BLACK,
            text_size=20,
            hover_text_color=arcade.color.WHITE,
            callback=self.go_to_mappe,
            bold=True
        ))

        self.finish_buttons_win.append(RoundedButton(
            text="Torna al menu!",
            center_x=self.camera.position[0] + 200,
            center_y=self.camera.position[1] - (200 if not ImpostazioniLogica().is_fullscreen() else 180),
            width=button_width,
            height=button_height,
            bg_color=(240, 255, 240),
            bg_hover=(217, 147, 8),
            text_color=arcade.color.BLACK,
            text_size=20,
            hover_text_color=arcade.color.WHITE,
            callback=lambda: self._go_menu(),
            bold=True
        ))

    def go_to_mappe(self):
        from schermate.MappeScreen import MappeScreen
        self.window.show_view(MappeScreen(False))

    def _aggiorna_posizione_pulsanti(self):
        start_y = self.window.height - 540

        for i, button in enumerate(self.paused_buttons):
            button.center_x = self.camera.position[0]
            button.center_y = start_y + i * (button.height + 30)

        self.finish_buttons_gameover[0].center_x = self.camera.position[0] - 200
        self.finish_buttons_gameover[1].center_x = self.camera.position[0] + 200


        self.finish_buttons_gameover[0].center_y = self.camera.position[1] - 200
        self.finish_buttons_gameover[1].center_y = self.camera.position[1] - 200

        self.finish_buttons_win[0].center_x = self.camera.position[0] - 200
        self.finish_buttons_win[1].center_x = self.camera.position[0] + 200

        self.finish_buttons_win[0].center_y = self.camera.position[1] - 200
        self.finish_buttons_win[1].center_y = self.camera.position[1] - 200

    def _muovi_camera(self):
        screen_center_x = self.player.center_x - (self.window.width *0.5)
        screen_center_y = self.window.height *0.5

        if screen_center_x < 0:
            screen_center_x = 0

        map_width = self.tilemap.width * self.tilemap.tile_width
        if ImpostazioniLogica().is_fullscreen():
            map_width *=1.3
        if screen_center_x > map_width - self.window.width:
            screen_center_x = map_width - self.window.width

        if self.player.center_x > self.window.width *0.5:
            self.camera.position = (screen_center_x + self.window.width *0.5, screen_center_y)
        self._aggiorna_posizione_pulsanti()

    def collisioni(self):
        oggetti_colpiti = {
            "ostacoli": arcade.check_for_collision_with_list(self.player, self.ostacoli),
            "monete": arcade.check_for_collision_with_list(self.player, self.monete),
            "cuori": arcade.check_for_collision_with_list(self.player, self.cuori),
            "danni": arcade.check_for_collision_with_list(self.player, self.danni)
        }

        if oggetti_colpiti["ostacoli"]:
            self.player.center_x -= self.player.change_x
            self.player.center_y -= self.player.change_y

        for moneta in oggetti_colpiti["monete"]:
            self.moneteList.append((round(moneta.center_x / self.scaling), round(moneta.center_y / self.scaling)))
            moneta.remove_from_sprite_lists()
            self.player.coins += 1
            #if ImpostazioniLogica().is_audio():
                #sound = arcade.Sound("Media/Sounds/coin_sound.mp3")
                #sound.play(volume=0.5)
            self.tile_grid = self._build_tile_grid()
            print(f"Moneta raccolta! Monete totali: {self.player.coins}")

        for cuore in oggetti_colpiti["cuori"]:
            self.cuoriList.append((round(cuore.center_x / self.scaling), round(cuore.center_y / self.scaling)))
            cuore.remove_from_sprite_lists()
            self.player.add_health(1)
            self.tile_grid = self._build_tile_grid()
            print(f"Vita raccolta! Vita attuale: {self.player.health}")

        if oggetti_colpiti["danni"]:
            self.player.rem_health(1)
        if self.player.health <= 0:
            self.finish = "Gameover"
        if self.player.center_x <= self.camera.position[0] - self.window.width //2 :
            self.player.center_x -= self.player.change_x
            self.player.center_y -= self.player.change_y
        if self.player.center_y <= self.camera.position[1] - self.window.height //2:
            self.player.center_x -= self.player.change_x
            self.player.center_y -= self.player.change_y
        if self.player.center_y >= self.camera.position[1] + self.window.height //2:
            self.player.center_x -= self.player.change_x
            self.player.center_y -= self.player.change_y

        map_width = self.tilemap.width * self.tilemap.tile_width
        if ImpostazioniLogica().is_fullscreen():
            map_width *= 1.3
        if self.player.center_x > map_width - 48:
            self.finish = "Win"

    def pausa(self):
        if self.finish == "Gameover":
            pass
        elif self.start_pause == 0:
            self.playerposition_x = round(self.player.center_x / self.scaling)
            self.playerposition_y = round(self.player.center_y / self.scaling)
            self.start_pause = time.time()
        else:
            self.start_time += int(time.time() - self.start_pause)
            self.start_pause = 0

    def _go_menu(self):
        from schermate.MenuScreen import MenuScreen
        self.camera.position =(self.window.width *0.5, self.window.height *0.5)
        self.camera.use()
        self.window.show_view(MenuScreen(True))

    def retry(self):
        from schermate.GiocoScreen import GiocoScreen
        self.window.show_view(GiocoScreen(self.mappa))

    def get_state(self):
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
                self.player.change_x = -PLAYER_SPEED*3
            self.last_action = 0
        elif action == 1:
            if self.flag:# right
                self.player.change_x = PLAYER_SPEED*3
            self.last_action = 1
        elif action == 2:
            if self.flag:# up
                self.player.change_y = PLAYER_SPEED*3
            self.last_action = 2
        elif action == 3:
            if self.flag:# down
                self.player.change_y = -PLAYER_SPEED*3
            self.last_action = 3
        elif action == 4:  # no action
            self.player.change_x = 0
            self.last_action = 4
            self.player.change_y = 0
        self.update(1/500)  # Simula un frame
        done = self.finish is not None
        reward = self.reward_funcution()
        return self.get_state(), reward, done

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
        if len(self.episode_numbers) >= 150:
            self.reward_funcution = self.get_reward_1
            self.mappa = "test.tmx"
        if len(self.episode_numbers) >= 600:
            self.reward_funcution = self.get_reward_2
            self.mappa = "foresta.tmx"
        if self.agent.epsilon > self.agent.epsilon_min:
            self.agent.epsilon *= self.agent.epsilon_decay

    def get_reward(self):
        reward = 0
        if self.last_action==1:
            reward += 1
        else:
            reward -= 1
        # 5. Ricompensa per raggiungere la fine
        if self.finish == "Win":
            return 500  # Ricompensa grande per il successo
        if self.finish == "Gameover":
            return -100
        return reward

    def get_reward_1(self):
        reward = 0
        if self.last_action == 1:
            reward += 1
        oggetti_colpiti = {
            "ostacoli": arcade.check_for_collision_with_list(self.player, self.ostacoli),
            "monete": arcade.check_for_collision_with_list(self.player, self.monete),
            "cuori": arcade.check_for_collision_with_list(self.player, self.cuori),
            "danni": arcade.check_for_collision_with_list(self.player, self.danni)
        }

        if oggetti_colpiti["ostacoli"]:
            reward -= 1
        if oggetti_colpiti["monete"]:
            reward += 1
        if oggetti_colpiti["cuori"]:
            reward += 1
        if oggetti_colpiti["danni"]:
            reward -= 1

        # 5. Ricompensa per raggiungere la fine
        if self.finish == "Win":
            return 500  # Ricompensa grande per il successo
        if self.finish == "Gameover":
            return -100
        return reward

    def get_reward_2(self):
        reward = 0
        current_x = self.player.center_x

        # 1. Ricompensa principale per il movimento a destra
        dx = current_x - self.last_x
        reward += max(dx, 0) * 5  # Incentivo più forte a muoversi a destra

        # 2. Penalità per muoversi a sinistra
        if dx < 0:
            reward -= abs(dx) * 2  # Penalità più severa per il movimento a sinistra

        oggetti_colpiti = {
            "ostacoli": arcade.check_for_collision_with_list(self.player, self.ostacoli),
            "monete": arcade.check_for_collision_with_list(self.player, self.monete),
            "cuori": arcade.check_for_collision_with_list(self.player, self.cuori),
            "danni": arcade.check_for_collision_with_list(self.player, self.danni)
        }

        if oggetti_colpiti["ostacoli"]:
            reward -= 1
        if oggetti_colpiti["monete"]:
            reward += 1
        if oggetti_colpiti["cuori"]:
            reward += 1
        if oggetti_colpiti["danni"]:
            reward -= 1

        # 5. Ricompensa per raggiungere la fine
        if self.finish == "Win":
            return 500  # Ricompensa grande per il successo
        if self.finish == "Gameover":
            return -100

        # 6. Penalità per inattività
        if dx == 0:
            reward -= 5  # Penalizza se l'agente resta fermo

        # 7. Aggiorna stato
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

    def update(self, delta_time):
        """
        Aggiorna lo stato del gioco per un determinato intervallo di tempo.
        Puoi includere qui l'aggiornamento del giocatore, le collisioni, l'animazione,
        lo spostamento della camera, ecc.
        """
        # Se il gioco è in pausa o terminato, non aggiornare
        if self.start_pause != 0 or self.finish is not None:
            return
        # Aggiorna il giocatore
        self.player.update()


        # Gestisci le collisioni
        self.collisioni()

        # Aggiorna l'animazione della scena
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