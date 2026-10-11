from animkit import *
def shot_1(s):
    img = load_plate("bg", expo=0.6)
    k = ease(ramp(s.t, s.c("L1:world"), s.c("L1:world")+0.5))
    L = Layer(); bb = text(L.ctx, "WORLD", W/2, H/2, size=120, col=(1,.8,.5), a=k); s.box("title", bb)
    return glow(L.over(img), thresh=0.5)
def shot_2(s):
    img = blank()
    return screen(img, radial(W/2, H/2, 300, (1,.6,.2), k=ramp(s.t,0,1)))
