from Persistenza.ImpostazioniJSON import load_settings, save_settings

class ImpostazioniLogica:

    def __init__(self):
        self.settings = load_settings()
        self.fullscreen = self.settings["fullscreen"]
        self.audio = self.settings["audio"]
        if self.fullscreen == "si":
            self.fullscreen_var = True
        else:
            self.fullscreen_var = False
        if self.audio == "si":
            self.audio_var = True
        else:
            self.audio_var = False

    def is_fullscreen(self):
        return self.fullscreen_var

    def is_audio(self):
        return self.audio_var

    def set_fullscreen(self, window):
        self.fullscreen_var = not self.fullscreen_var
        window.set_fullscreen(self.fullscreen_var)
        save_settings(self.fullscreen_var, self.audio_var)

    def set_audio(self):
        self.audio_var = not self.audio_var
        save_settings(self.fullscreen_var, self.audio_var)