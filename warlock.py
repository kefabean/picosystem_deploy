import io
import math
import time
import random
import json


selected = 0
blip = Voice(10, 10, 10, 10, 40, 2)
lose = Voice(10, 10, 10, 40, -2, 10, 100, 100)
win  = Voice(10, 10, 30, 40, 20, 10, 0, 0)


class Player:

    def __init__(self):
        self._skill   = random.randint(1, 6) + 6
        self._stamina = random.randint(1, 6) + random.randint(1, 6) + 12
        self._luck    = random.randint(1, 6) + 6
        self._gold    = 0
        self._hero    = 0

    def skill(self, delta = 0):
        self._skill = max(min(12, self._skill + delta), 1)
        return self._skill
        
    def stamina(self, delta = 0):
        self._stamina = max(min(24, self._stamina + delta), 1)
        return self._stamina

    def luck(self, delta = 0):
        self._luck = max(min(24, self._luck + delta), 1)
        return self._luck

    def gold(self, delta = 0):
        self._gold = max(self._gold + delta, 0)
        return self._gold

    def hero(self, delta = 0):
        self._hero = max(self._hero + delta, 0)
        return self._hero

class SceneNote:

    def __init__(self, player, monster):
        letters = 'abcdefghijklmnopqrstuvwxyz1234567890 '
        self.buttons  = [
            LetterButton(char, 11 * (count % 11),  17 * (count // 11), player.gold) for count, char in enumerate(letters)
        ]
        
    def draw(self):
        pass


class SceneAttr:

    def __init__(self, player, monster):
        self.buttons  = [
            NumberButton("Gold", 1,  1, player.gold),
            NumberButton("Hero", 41,  1, player.hero)
        ]
        
    def draw(self):
        pass


class SceneDice:

    def __init__(self, player, monster):
        self.step     = 0
        self.player   = player
        self.monster  = monster
        self.dice     = []
        self.buttons  = [
            NumberButton("Skill", 1,  1, player.skill),
            NumberButton("Stam", 41,  1, player.stamina),
            NumberButton("Luck", 81,  1, player.luck),
            NumberButton("Skill", 1, 60, monster.skill),
            NumberButton("Stam", 41, 60, monster.stamina),
            Button("Roll",       81, 60, self.roll)
        ]
    
    def roll(self):
        if self.step == 0:
            self.dice = [ random.randint(1, 6) for r in range(4) ]
            self.player_attack  = sum(self.dice[0:2]) + self.player.skill()
            self.monster_attack = sum(self.dice[2:4]) + self.monster.skill()
        self.step += 1
        if self.step == 5:
            if self.player_attack > self.monster_attack:
                self.monster.stamina(-1) 
                win.play(1200, 180, 100)
            if self.player_attack < self.monster_attack:
                self.player.stamina(-1)
                lose.play(1200, 180, 100)
        self.step %= 5

    def draw_dice(self, x, y, val):
        pen(10, 10, 10)
        frect(x, y, 20, 20)
        pen(0, 0, 0)
        text(str(val), x + 7, y +7)
        
    def draw(self):
        if self.player.stamina() == 0:
            pen(15, 0, 0)
            text("Player dead!", 1, 39)
            return
        if self.monster.stamina() == 0:
            pen(15, 0, 0)
            text("Monster killed!", 1, 98)
            return
        if self.step > 0:
            self.draw_dice(1, 33, self.dice[0])
        if self.step > 1:
            self.draw_dice(28, 33, self.dice[1])
            pen(15, 0, 0)
            text("Attack = " + str(self.player_attack), 53, 39)
        if self.step > 2:
            self.draw_dice(1, 92, self.dice[2])
        if self.step > 3:
            self.draw_dice(28, 92, self.dice[3])
            pen(15, 0, 0)
            text("Attack = " + str(self.monster_attack), 53, 98)


class Button:

    def __init__(self, message, x, y, func):
        self.x = x
        self.y = y
        self.message = message
        self.func = func
        self.col = (10, 10, 15)
        
    def draw(self, is_selected):
        pen(*self.col)
        if is_selected:
            frect(self.x, self.y, 38, 12)
            pen(0, 0, 0)
        else:
            rect(self.x, self.y, 38, 12)
        text(self.message, self.x + 2, self.y + 2)
        
    def press_a(self):
        blip.play(500, 120, 100)
        self.func()   
    
    def press_down(self):
        pass
    
    def press_up(self):
        pass


class NumberButton(Button):

    def __init__(self, message, x, y, func):
        super().__init__(message, x, y, func)    
        self.col = (15, 10, 15)
        
    def draw(self, is_selected):
        pen(*self.col)
        rect(self.x, self.y + 11, 38, 15)
        text(str(self.func()), self.x + 2, self.y + 15)
        pen(*self.col)
        super().draw(is_selected)
        
    def press_a(self):
        pass
    
    def press_down(self):
        blip.play(200, 18, 100)
        self.func(-1)
    
    def press_up(self):
        blip.play(800, 18, 50)
        self.func(1)


class LetterButton(Button):

    def __init__(self, message, x, y, func):
        super().__init__(message, x, y, func)    
        self.col = (5, 5, 10)
        
    def draw(self, is_selected):
        pen(*self.col)
        if is_selected:
            frect(self.x, self.y, 10, 15)
            pen(0, 0, 0)
        else:
            rect(self.x, self.y, 10, 15)
        text(self.message, self.x + 2, self.y + 4)
        
    def press_a(self):
        pass
    
    def press_down(self):
        blip.play(200, 18, 100)
        self.func(-1)
    
    def press_up(self):
        blip.play(800, 18, 50)
        self.func(1)


class Game:

    def __init__(self):
        self.scene   = 0
        self.button  = 0
        self.player  = Player()
        self.monster = Player()
        self.scenes  = [
            SceneDice(self.player, self.monster),
            SceneAttr(self.player, self.monster),
            SceneNote(self.player, self.monster)
        ]

    def draw(self, tick):
        pen(0, 0, 0)
        clear()
        for count, b in enumerate(self.scenes[self.scene].buttons):
            b.draw(self.button == count)
        self.scenes[self.scene].draw()

    def nav_left(self):
        if self.button == 0:
            if self.scene == 0:
                pass
            else:
                self.scene -= 1
                self.button = len(self.scenes[self.scene].buttons) - 1
        else:
            self.button -= 1

    def nav_right(self):
        if self.button == (len(self.scenes[self.scene].buttons) - 1):
            if self.scene == (len(self.scenes) - 1):
                pass
            else:
                self.scene += 1
                self.button = 0
        else:
            self.button += 1
        
    def update(self, tick):
        if pressed(LEFT):
            blip.play(1600, 30, 100)
            self.nav_left()
        if pressed(RIGHT):
            blip.play(1800, 30, 100)
            self.nav_right()
        button = self.scenes[self.scene].buttons[self.button]
        if pressed(A):
            button.press_a()
        if pressed(UP):
            button.press_up()
        if pressed(DOWN):
            button.press_down()
        # if buttons[4].val == 0:
        #     selected = 4
        #     if len(buttons) == 6:
        #         buttons.pop(5)
        # elif buttons[1].val == 0:
        #     selected = 1
        #     if len(buttons) == 6:
        #         buttons.pop(5)
        # else:
        #     if len(buttons) == 5:
        #         buttons.append(Button("Roll", 81, 60))

 
def update(tick):
    global g
    g.update(tick)
        

def draw(tick):
    global g
    g.draw(tick)


g = Game()
start()