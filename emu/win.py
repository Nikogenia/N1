# Standard modules
from __future__ import annotations
import threading as th

# External libraries
import pygame as pg

# Local modules
from constants import *
from common import *
from n1 import N1


class Win(th.Thread):

    def __init__(self, glob: Global) -> None:

        th.Thread.__init__(self, name="Window")

        self.glob: Global = glob

        self.clock: pg.time.Clock = pg.time.Clock()
        self.screen: pg.Surface = pg.Surface((0, 0))

        self.font: pg.font.Font = None

        self.running = True

    def run(self) -> None:

        pg.init()

        self.font = pg.font.SysFont("consolas", 20)

        self.screen = pg.display.set_mode((W_WIDTH, W_HEIGHT))

        while self.running:

            self.clock.tick(30)

            for event in pg.event.get():
                self.event(event)

            self.render()

        pg.quit()

    def event(self, event: pg.event.Event) -> None:

        if event.type == pg.QUIT:
            self.running = False

    def render(self) -> None:

        self.screen.fill(C_BG1)

        exit_str = "----" if self.glob.n1.exit == -1 else "0x" + number2str(self.glob.n1.exit, 2)
        self.screen.blit(self.font.render("Exit", True, C_FG3), (5, 524))
        self.screen.blit(self.font.render(exit_str, True, C_FG1), (60, 524))

        for i, r in enumerate("abcdhlzf"):
            r_str = "0x" + number2str(self.glob.n1.registers[r], 2)
            self.screen.blit(self.font.render(r.upper(), True, C_FG3), (5, 550 + i * 18))
            self.screen.blit(self.font.render(r_str, True, C_FG1), (60, 550 + i * 18))

        pc_str = "0x" + number2str(self.glob.n1.pc[0], 2) + number2str(self.glob.n1.pc[1], 2)
        self.screen.blit(self.font.render("PC", True, C_FG3), (120, 524))
        self.screen.blit(self.font.render(pc_str, True, C_FG1), (175, 524))

        sp_str = "0x" + number2str(self.glob.n1.sp[0], 2) + number2str(self.glob.n1.sp[1], 2)
        self.screen.blit(self.font.render("SP", True, C_FG3), (120, 550))
        self.screen.blit(self.font.render(sp_str, True, C_FG1), (175, 550))

        mb_str = "0x" + number2str(self.glob.n1.mb, 2)
        self.screen.blit(self.font.render("MB", True, C_FG3), (120, 576))
        self.screen.blit(self.font.render(mb_str, True, C_FG1), (175, 576))

        self.screen.blit(render_display(None), (3, 3))

        pg.display.flip()


def render_display(n1: N1) -> None:

    surf: pg.Surface = pg.Surface((D_WIDTH * P_WIDTH + 4, D_HEIGHT * P_HEIGHT + 4))

    pg.draw.rect(surf, C_LAMP_OFF, (2, 2, D_WIDTH * P_WIDTH, D_HEIGHT * P_HEIGHT))
    #pg.draw.rect(surf, C_LAMP_ON, (2, 2, D_WIDTH * P_WIDTH, D_HEIGHT * P_HEIGHT))

    for x in range(D_WIDTH):
        for y in range(D_HEIGHT):
            pg.draw.rect(surf, C_LAMP_BORDER, (2 + x * P_WIDTH, 2 + y * P_HEIGHT, P_WIDTH, P_HEIGHT), 1)
            
    pg.draw.rect(surf, C_BORDER, (1, 1, D_WIDTH * P_WIDTH + 2, D_HEIGHT * P_HEIGHT + 2), 2)

    return surf

