import pygame
import pygame.gfxdraw

FPS = 15
PREFIX = "/home/pi/dev/py-hilga/"       # trailing '/' must

MEMOIZED = {}
def memoize(fun):
    def mfun(*args, **kwargs):
        mm = MEMOIZED[fun]
        if not kwargs and mm.has_key(args):
            return mm[args]

        rv = apply(fun, args, kwargs)
        if not kwargs:
            mm[args] = rv
        return rv
    MEMOIZED[fun] = {}
    return mfun

def maybe_prepend(s, pref):
    return s if s.startswith(pref) else pref+s

@memoize
def load_texture(path, alpha=False):
    surf = pygame.image.load(PREFIX + maybe_prepend(path, "textures/"))
    if alpha:
        return surf.convert_alpha()
    surf.set_colorkey((0,0,0))          # Mac OS X workaround!
    return surf.convert()

@memoize
def load_font(path, size):
    if path.endswith(".ttf"):
        return pygame.font.Font(PREFIX + maybe_prepend(path, "fonts/"), size)
    return pygame.font.SysFont(path, size)

@memoize
def load_sound(path):
    return pygame.mixer.Sound(PREFIX + maybe_prepend(path, "audio/"))

def play_sound(snd, stop=False, **kwargs):
    """Play sound SND."""
    if type(snd) == str:
        return play_sound(load_sound(snd), stop, **kwargs)

    if stop:
        snd.stop()

    _sc = snd.play(**kwargs)
    if _sc and kwargs.has_key("volume"):
        _sc.set_volume(kwargs["volume"])

    if kwargs.has_key("fadeout"):
        _sc.fadeout(kwargs['fadeout'])
    return _sc
