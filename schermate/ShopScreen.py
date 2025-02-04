import os
import time

import arcade
import xml.etree.ElementTree as ET

from Logica.ImpostazioniLogica import ImpostazioniLogica
from Persistenza import PlayerJSON, SkinJSON
from utils.RectangleBorder import RectangleBorder
from utils.RoundedButtons import RoundedButton


class ShopScreen(arcade.View):

    def __init__(self):
        super().__init__()
        self.frames_dict = {}
        self.sprites = []
        self.selezionata = None
        self.buttons = []
        self.skins = []
        self.player = PlayerJSON.load_player()
        self.insufficienti = False
        self.time_insufficienti = 0

    def setup(self):
        self.camera = arcade.camera.Camera2D()

    def on_show_view(self):
        arcade.set_background_color((240, 255, 240))
        self.setup()
        self._carica_locali()
        self.create_buttons()

    def _carica_locali(self):
        dir = "./Media/Skins"
        files = os.listdir("./Media/Skins")
        files = [f for f in files if os.path.isfile(os.path.join(dir, f))]
        files = [f for f in files if f.endswith(f".tsx")]
        for file in files:
            self.skins.append(file[:-4])

        self.skin_list = SkinJSON.load_skins()
        # Estrai i nomi di tutte le skin presenti nella skin_list
        nomi_presenti = [s["nome"] for s in self.skin_list]
        for skin in self.skins:
            if skin not in nomi_presenti:
                SkinJSON.add_skin(skin)
        self.skin_list = SkinJSON.load_skins()

    def load_frames_from_tsx(self, tsx_path, skin_name):
        """
        Carica i frame da un file TSX e li associa alla skin 'skin_name'.
        """
        tree = ET.parse(tsx_path)
        root = tree.getroot()

        image_source = root.find("image").attrib["source"]
        # Carica la texture intera (l'immagine della tileset)
        image = arcade.load_texture("Media/Skins/" + image_source)

        tile_width = int(root.attrib["tilewidth"])
        tile_height = int(root.attrib["tileheight"])
        columns = int(root.attrib["columns"])

        # Prepara le liste per i frame e le durate
        frames = []
        frame_durations = []

        animation_frames = root.find("tile/animation")
        if animation_frames is None:
            # Se non esiste una sezione di animazione, potresti voler gestire il caso
            print(f"Nessuna animazione trovata per la skin {skin_name}")
            return

        for frame in animation_frames.findall("frame"):
            tile_id = int(frame.attrib["tileid"])
            duration = int(frame.attrib["duration"]) / 1000.0  # da ms a secondi

            col = tile_id % columns
            row = tile_id // columns

            # Ottieni la sottotexture (frame) tagliando l'immagine principale
            cropped_texture = image.crop(
                col * tile_width, row * tile_height,
                tile_width, tile_height
            )
            frames.append(cropped_texture)
            frame_durations.append(duration)
            # Salva i frame nel nuovo dizionario
            self.frames_dict[skin_name] = {
                "frames": frames,
                "durations": frame_durations,
                "position": (0, 0),
                "current_frame": 0
            }


    def create_buttons(self):
        skin_width = self.window.width - 100
        button_width = 150
        button_height = 50
        spacing = 40
        start_x = (self.window.width / 2) - ((skin_width*0.08 + 10) * (10 / 2 - 0.5)) + 30
        start_y = self.window.height - 90  # Regolato per spazio
        self.buttons = []
        self.sprites = []
        altezza_col = 0
        j=0
        for i, skin in enumerate(self.skin_list):
            nome = skin["nome"]
            costo = skin["costo"]
            acquistato = skin["acquistata"]
            j+=1
            if i % 5 == 0 and not ImpostazioniLogica().is_fullscreen():
                altezza_col += 200
                j=0
            elif i % 6 == 0 and ImpostazioniLogica().is_fullscreen():
                altezza_col += 200
                j = 0
            x_pos = start_x + (button_width + spacing) * j
            y_pos = start_y - 115 - altezza_col + 200



            self.load_frames_from_tsx(f"Media/Skins/{nome}.tsx", nome)
            self.frames_dict[nome]["position"] = (x_pos, y_pos)

            # Testo del pulsante
            if not acquistato:
                button_text = f"Compra: {costo}"
                button_callback = lambda i=i: self.acquista(i)
            elif nome == self.player["corrente"]:
                button_text = "Selezionata"
                button_callback = None
            else:
                button_text = "Seleziona"
                button_callback = lambda i=i: self.select_skin(i)

            # Creazione pulsante
            button = RoundedButton(
                text=button_text,
                center_x=start_x + (button_width + spacing) * j,
                center_y=start_y - altezza_col,
                width=button_width,
                height=button_height,
                bg_color=(240, 255, 240),
                bg_hover=(217, 147, 8),
                text_color=arcade.color.BLACK,
                text_size=14,
                hover_text_color=arcade.color.WHITE,
                bold=True,
                callback=button_callback,
                bg_selected=arcade.color.GREEN,
            )
            button.selected = self.player["corrente"].strip().lower() == nome.strip().lower()
            self.buttons.append(button)


    def acquista(self, numero_skin):
        if int(self.player["monete"])>= int(self.skin_list[numero_skin]["costo"]):
            temp =  int(self.player["monete"]) - int(self.skin_list[numero_skin]["costo"])
            PlayerJSON.save_player(temp, self.player["corrente"])
            self.player = PlayerJSON.load_player()
            self.skin_list[numero_skin]["acquistata"] = True  # Aggiorna lo stato della skin
            SkinJSON.save_skins(self.skin_list)  # Salva le skin aggiornate
            self.create_buttons()
        else:
            self.monete_insufficienti()

    def monete_insufficienti(self):
        self.time_insufficienti = time.time()
        self.insufficienti = True




    def select_skin(self, numero_skin):
        PlayerJSON.save_player(int(self.player["monete"]), self.skin_list[numero_skin]["nome"])
        self.player = PlayerJSON.load_player()
        self.create_buttons()



    def on_update(self, delta_time):
        frame_duration = 0.5
        for skin, skin_data in self.frames_dict.items():
            skin_data.setdefault("time_since_last_frame", 0)  # Inizializza il tempo se non esiste
            skin_data["time_since_last_frame"] += delta_time

            if skin_data["time_since_last_frame"] >= frame_duration:
                skin_data["current_frame"] = (skin_data.get("current_frame", 0) + 1) % len(skin_data["frames"])
                skin_data["time_since_last_frame"] = 0  # Resetta il tempo per il prossimo cambio di frame
        if time.time() > self.time_insufficienti+1:
            self.insufficienti = False



    def on_show(self):
        arcade.set_background_color(arcade.color.DARK_GRAY)

    def on_draw(self):
        self.clear()
        skin_width = self.window.width - 100
        skin_height = self.window.height - 70

        RectangleBorder(
            center_x=self.window.width / 2,
            center_y=self.window.height / 2,
            width=skin_width,
            height=skin_height,
            bg_color=(217, 147, 8),
            border=True
        ).draw()

        arcade.draw_text(
            text="SKIN",
            y=self.window.height - 100,
            x=self.window.width / 2,
            anchor_x='center',
            font_size=45,
            bold=True,
        )
        arcade.draw_text(
            text=self.player["monete"],
            y=self.window.height - 100,
            x=self.window.width - 120,
            anchor_x='right',
            font_size=45,
            bold=True,
        )
        moneta_sprite = arcade.Sprite("Media/img/coin.png", scale=1.2)
        moneta_sprite.center_x = self.window.width - 80
        moneta_sprite.center_y = self.window.height- 80
        arcade.draw_texture_rect(moneta_sprite.texture, moneta_sprite.rect)

        self.draw_all_skins()
        for button in self.buttons:
            button.draw()
        if self.insufficienti:
            RectangleBorder(
                center_x=self.window.width / 2,
                center_y=self.window.height / 2,
                width=650,
                height=100,
                bg_color=(217, 147, 8),
                border=True
            ).draw()
            arcade.draw_text(
                text="Monete insufficienti",
                y=self.window.height/ 2,
                x=self.window.width / 2,
                anchor_x='center',
                anchor_y='center',
                font_size=45,
                bold=True,
        )


        # Stampa il nome delle skin sotto lo sprite
        for i, skin in enumerate(self.skin_list):
            if i >= len(self.sprites):  # Se non ci sono abbastanza sprite, interrompi
                #print(f"Attenzione: mancano sprite per {skin['nome']}")
                continue
            x_pos = self.sprites[i].center_x
            y_pos = self.sprites[i].center_y - 40
            arcade.draw_text(
                skin["nome"], x_pos, y_pos, arcade.color.BLACK, 14, anchor_x="center"
            )

            # Se la skin non è acquistata, mostra il costo sotto il nome
            if not skin["acquistata"]:
                arcade.draw_text(
                    f"{skin['costo']}G", x_pos, y_pos - 20, arcade.color.RED, 12, anchor_x="center"
                )

    def draw_all_skins(self):
        """
        Disegna tutte le skin caricate a schermo.
        In questo esempio, le skin vengono disposte in orizzontale, ognuna a una distanza fissa.
        """
        margin = 20  # spazio tra le skin
        # Posizione di partenza
        start_x = 100
        start_y = 100

        current_x = start_x

        for skin_name, skin_data in self.frames_dict.items():
            # Seleziona il primo frame della skin
            frame_texture = skin_data["frames"][skin_data["current_frame"]]
            x, y = skin_data["position"]
            # Crea il rettangolo per il disegno
            rect = arcade.Rect(
                x - self.width // 2,
                x + self.width // 2,
                y + self.height // 2,
                y - self.height // 2,
                100,
                100,
                x,
                y
            )

            # Disegna la texture all'interno del rettangolo
            arcade.draw_texture_rect(
                texture=frame_texture,
                rect=rect
            )

            # Aggiorna la posizione per la skin successiva
            current_x += 50 + margin



    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            from schermate.MenuScreen import MenuScreen
            self.window.show_view(MenuScreen(True))

    def on_mouse_motion(self, x, y, dx, dy):
        for button in self.buttons:
            button.on_hover(x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            for btn in self.buttons:
                btn.on_click(x, y)