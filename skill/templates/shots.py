"""<Title>: one function per shot (shot id "1" -> shot_1). See the animate skill, workflow/3-animation.md."""
import math

import numpy as np
from animkit import *  # noqa: F401,F403


# ---------- the film's style: shared by every shot (see STYLE.md) ----------

def finish_frame(img, s):
    """The film's last pass on every shot: grade, vignette, palette guard... Keep it the same for all shots."""
    return np.clip(vignette(img, 0.4), 0, 1)


# ---------- shots ----------

def shot_1(s):
    img = blank()
    return finish_frame(img, s)
