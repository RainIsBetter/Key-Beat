# TODO
# x add miss/great banners
# x Add chord names
# x print score
# print score, print grade %
# x add "play" button to start the game

import pygame
import csv
import random
from pygame import mixer

CHORD_TIME_OFFSET = 0
TIME_INTERVAL_RANGE = 50
SPEED_PER_FRAME = 14
MUSIC_OFFSET_TIME = 3300
HIT_SCORE_INCREMENT = 10
HIT_SCORE_DECREMENT = -1
music_started = False
pygame.init()
mixer.init()

clicked = False
score = 0
perfect_score = 0

clock = pygame.time.Clock()
bg = pygame.image.load("img/bg2.png")
bg_game_over = pygame.image.load("img/bg-gameover.png")
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("KeyBeat Game")
button_font = pygame.font.SysFont("dejavuserif", 20)
score_font = pygame.font.SysFont("dejavuserif", 100)

#blueprint for chord pads
class valid_chord_pads:
    def __init__(self, x, y, color1, color2, key, chord_name):
        self.x = x
        self.y = y
        self.chord_name = chord_name
        self.color1 = color1
        self.color2 = color2
        self.key = key
        self.rect = pygame.Rect(self.x, self.y, 100, 60)
        self.handled = False

#creates chord pads
chord_pad_list = [
    valid_chord_pads(100, 500, (255, 0, 0), (143, 54, 54), pygame.K_a, "G4"),
    valid_chord_pads(200, 500, (0, 255, 0), (48, 138, 48), pygame.K_s, "E4"),
    valid_chord_pads(300, 500, (0, 0, 255), (52, 52, 148), pygame.K_d, "D4"),
    valid_chord_pads(400, 500, (255, 255, 0), (135, 135, 49), pygame.K_f, "C4"),
]



class animated_text(pygame.sprite.Sprite):
    def __init__(self, x, y, text):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range(0, 7):
            img = pygame.image.load(f"img/{text}/frame_{num:02d}_delay-0.05s.png")
            self.images.append(img)
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.counter = 0

    def update(self):
        animation_speed = 1
        # update text animation
        self.counter += 1

        if self.counter >= animation_speed and self.index < len(self.images) - 1:
            self.counter = 0
            self.index += 1
            self.image = self.images[self.index]

        # if the animation is complete, reset animation index
        if self.index >= len(self.images) - 1 and self.counter >= animation_speed:
            self.kill()


# define colours
# bgColor = (204, 102, 0)
red = (255, 0, 0)
black = (0, 0, 0)
white = (255, 255, 255)


class button:
    # colours for button and text
    button_col = (117, 20, 122)
    hover_col = (133, 96, 135)
    click_col = (186, 180, 65)
    text_col = black
    width = 110
    height = 50

    def __init__(self, x, y, text):
        self.x = x
        self.y = y
        self.text = text

    def draw_button(self):

        global clicked
        action = False

        # get mouse position
        pos = pygame.mouse.get_pos()

        # create pygame Rect object for the button
        button_rect = pygame.Rect(self.x, self.y, self.width, self.height)

        # check mouseover and clicked conditions
        if button_rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1:
                clicked = True
                pygame.draw.rect(screen, self.click_col, button_rect)
            elif pygame.mouse.get_pressed()[0] == 0 and clicked == True:
                clicked = False
                action = True
            else:
                pygame.draw.rect(screen, self.hover_col, button_rect)
        else:
            pygame.draw.rect(screen, self.button_col, button_rect)

        # add shading to button
        pygame.draw.line(
            screen, white, (self.x, self.y), (self.x + self.width, self.y), 2
        )
        pygame.draw.line(
            screen, white, (self.x, self.y), (self.x, self.y + self.height), 2
        )
        pygame.draw.line(
            screen,
            black,
            (self.x, self.y + self.height),
            (self.x + self.width, self.y + self.height),
            2,
        )
        pygame.draw.line(
            screen,
            black,
            (self.x + self.width, self.y),
            (self.x + self.width, self.y + self.height),
            2,
        )

        # add text to button
        text_img = button_font.render(self.text, True, self.text_col)
        text_len = text_img.get_width()
        screen.blit(
            text_img, (self.x + int(self.width / 2) - int(text_len / 2), self.y + 20)
        )
        return action


def load(map):
    chords = []

    # load chords map from file
    with open(map + ".map") as csv_file:
        mixer.music.load(map + ".mid")
        csv_reader = csv.reader(csv_file, delimiter=",")
        line_count = 0
        for row in csv_reader:
            if row[0].startswith("#"):
                continue

            if line_count == 0:
                print(f'Column names are {", ".join(row)}')
                line_count += 1
            else:
                modifiedTime = int(row[1]) * 2 + CHORD_TIME_OFFSET
                print(f"\t play chord {row[0]} at time {modifiedTime}")
                chords.append([modifiedTime, row[0]])
                line_count += 1
        print(f"Processed {line_count} lines.")

    #return list of lists
    return chords

# checks if the time for a chord is now and returns a list of all matching chords
def find_chord(tick, chords):
    # print(tick)
    result = []
    for chord in chords:
        if (
            chord[0] - TIME_INTERVAL_RANGE <= tick
            and tick <= chord[0] + TIME_INTERVAL_RANGE
        ):
            print("Found chord ", chord[1])
            result.append(chord)
            
    return result

#function takes a list of valid chords, checks if they are 
#ex: chord_list = [[3000,G4], [3000,C4]]
# ex: chord_pad_list = [chord_pad1, chord_pad2, chord_pad3, chord_pad4]
def get_pads(chord_list):
    result = []
    for pad in chord_pad_list:
        for chord_inside_list in chord_list:
            if pad.chord_name == chord_inside_list[1]:
                result.append(pad)
    return result

def game_is_over(game_time_counter, loaded_chords):
    for chord in loaded_chords:
        if chord[0] > game_time_counter - MUSIC_OFFSET_TIME - 1000:
            return False
    return True



loaded_chords = load("Mary-Had-a-Little-Lamb")
#loaded_chords = load("test")
perfect_score = len(loaded_chords) * HIT_SCORE_INCREMENT
visible_chords = []
animated_text_group = pygame.sprite.Group()
againButton = button(550, 500, "Restart")
quitButton = button(670, 500, "Quit")

game_start_time = pygame.time.get_ticks()
game_time_counter = 0


# =================================================
# Main loop
# =================================================
while True:
    game_time_counter = pygame.time.get_ticks() - game_start_time
    if game_time_counter > MUSIC_OFFSET_TIME and not music_started:
        mixer.music.play()
        music_started = True


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                quit()

    if game_is_over(game_time_counter, loaded_chords):
        screen.blit(bg_game_over, (0, 0))
        # Draw grades/score
        
        text_img = score_font.render(str(score)+"/"+str(perfect_score), True, (255, 255, 255))
        text_len = text_img.get_width()
        screen.blit(text_img, (250, 300))


    else:    
        screen.blit(bg, (0, 0))
        # Draw score
        text_img = score_font.render(str(score), True, (255, 255, 255))
        text_len = text_img.get_width()
        screen.blit(text_img, (600, 50))

        animated_text_group.draw(screen)
        animated_text_group.update()

        # read chords and add rectangle at correct position if tick matches time
        chords_going_now = find_chord(game_time_counter, loaded_chords)
        valid_chord_pads = get_pads(chords_going_now)
        for pad in valid_chord_pads:
            visible_chords.append(
                pygame.Rect(
                    pad.rect.centerx - 25, pad.rect.centery - 500, 50, 25
                )
            )

        pressed_key = pygame.key.get_pressed()
        for valid_chord_pads in chord_pad_list:
            if pressed_key[valid_chord_pads.key]:
                pygame.draw.rect(screen, valid_chord_pads.color1, valid_chord_pads.rect)
                valid_chord_pads.handled = True
            else:
                pygame.draw.rect(screen, valid_chord_pads.color2, valid_chord_pads.rect)
                valid_chord_pads.handled = False
            # add text to pads
            text_img = button_font.render(valid_chord_pads.chord_name, True, (0, 0, 0))
            text_len = text_img.get_width()
            screen.blit(
                text_img,
                (
                    valid_chord_pads.rect.x + int(valid_chord_pads.rect.width / 2) - int(text_len / 2),
                    valid_chord_pads.rect.y + 20,
                ),
            )


        for rect in visible_chords:
            pygame.draw.rect(screen, (224, 66, 245), rect)
            rect.y += SPEED_PER_FRAME
            for valid_chord_pads in chord_pad_list:
                if (
                    valid_chord_pads.rect.contains(rect) or valid_chord_pads.rect.colliderect(rect)
                ) and valid_chord_pads.handled:
                    print("Hit")
                    great_text = animated_text(
                        600 + random.randrange(-25, 25, 5),
                        250 + random.randrange(-25, 25, 5),
                        "great",
                    )
                    animated_text_group.empty()
                    animated_text_group.add(great_text)
                    visible_chords.remove(rect)
                    score = score + HIT_SCORE_INCREMENT
                elif valid_chord_pads.rect.contains(rect) and not valid_chord_pads.handled:
                    print("Miss")
                    miss_text = animated_text(
                        600 + random.randrange(-25, 25, 5),
                        250 + random.randrange(-25, 25, 5),
                        "miss",
                    )
                    animated_text_group.add(miss_text)
                    score = score + HIT_SCORE_DECREMENT

    if againButton.draw_button():
        print("Again")
        mixer.music.stop()
        score = 0
        music_started = False
        visible_chords = []
        animated_text_group.empty()
        game_start_time = pygame.time.get_ticks()

    if quitButton.draw_button():
        print("Quit")
        pygame.quit()
        quit()
    
    pygame.display.update()
    clock.tick(10)
