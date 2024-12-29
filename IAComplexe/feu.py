from color import Color

class Feu:
    def __init__(self):
        self.symbole = Color.RED +'F' + Color.END

    def est_actif(self):
        return True
