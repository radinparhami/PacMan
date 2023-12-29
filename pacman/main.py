from map_draw import array_map, CdtSelector, get_centers, get_space, mouse_inside
from threading import Thread
from random import choice
from time import sleep
import pygame

pygame.init()

screen_width, screen_height = 995, 610
accident_area = 25
two_tile_step = 24
space_between = 5
magnet_result = 0
points_radius = 3
pacman_steps = 5
souls_speed = 2
rect_sizes = 50 or 35
score = ""

except_points = []
loop_event = False
tmp_show_pacman_cm = 0
clock = pygame.time.Clock()

screen = pygame.display.set_mode((screen_width, screen_height))

intro_audio = pygame.mixer.Sound(r"sounds/pacman_beginning.wav")
eat_audio = pygame.mixer.Sound(r"sounds/pacman_eatfruit.wav")
death_audio = pygame.mixer.Sound(r"sounds/pacman_death.wav")
win_audio = pygame.mixer.Sound(r"sounds/pacman_win.mp3")
in_game_audio = pygame.mixer.Sound(r"sounds/in_game.mp3")

GameOver, WIN = pygame.image.load(r"imgs/GameOver.png"), pygame.image.load(r"imgs/Win.png")
pacman_right = pygame.image.load(r"imgs/pacman.png")
pacman_c_m = pygame.image.load(r"imgs/pacman_cm.png")
pacman_up = pygame.transform.rotate(pacman_right, 90)
pacman_left = pygame.transform.rotate(pacman_up, 90)
pacman_down = pygame.transform.rotate(pacman_left, 90)
pacman = pacman_right

game_map_pixel = [
    ['tl', 't', 'rl', 't', 't', 't', 'rl', 't', 'rt', 'rl', 't', 't', 'rl', 't', 'rt', 'rl', 't', 'rt'],
    ['l', '0', 'rl', '0', '0', '0', 'rl', '0', 'r', 'rl', '0', '0', 'rl', '0', 'r', 'rl', '0', 'r'],
    ['l', '0', 'rl', '0', '0', '0', 'rl', '0', 'r', 'rl', '0', '0', 'rl', '0', 'r', 'rl', '0', 'r'],
    ['l', '0', 'rl', '0', '0', '0', 'rl', '0', 'r', 'rl', '0', '0', 'rl', '0', 'r', 'rl', '0', 'r'],
    ['td', 'td', '0', 'td', 'td', 'td', '0', 'td', 'td', '0', 'td', 'td', '0', 'td', 'td', '0', 'td', 'td'],
    ['l', '0', 'rl', '0', '0', '0', 'rl', '0', 'r', 'rl', '0', '0', 'rlq', '0', 'r', 'rl', '0', 'r'],
    ['l', '0', 'rl', '0', '0', '0', 'rl', '0', 'r', 'rl', '0', 'r0', 'q', 'l0', 'r', 'rl', '0', 'r'],
    ['l', '0', 'rl', '0', '0', '0', 'rl', '0', 'r', 'rl', '0', '0', 'lrq', '0', 'r', 'rl', '0', 'r'],
    ['td', 'td', '0', 'td', 'td', 'td', '0', 'td', 'td', '0', 'td', 'td', '0', 'td', 'td', '0', 'td', 'td'],
    ['l', '0', 'rl', '0', '0', '0', 'rl', '0', 'r', 'rl', '0', '0', 'rl', '0', 'r', 'rl', '0', 'r'],
    ['ld', '0d', 'rl', '0d', '0d', '0d', 'rl', '0d', 'rd', 'rl', '0d', '0d', 'rl', '0d', 'rd', 'rl', '0d', 'rd'],
]


def game_map_reset():
    global game_map, important_points, intersection
    screen.fill('black')
    game_map = array_map(screen, game_map_pixel, rect_sizes, space_between, 'red')
    intersection = CdtSelector(game_map_pixel, game_map, [game_map[4][12].cdt]).get_intersections(True)
    important_points = CdtSelector(
        game_map_pixel, game_map,
        [game_map[5][12].cdt, game_map[4][0].cdt] + except_points,
        intersection + [game_map[4][12].cdt]
    ).array_filter(lambda o, _: 'rl' in o or 'td' in o, )
    for ob in important_points:
        pygame.draw.circle(screen, 'white' if ob.cdt in intersection else 'yellow', ob.get_center, points_radius)


game_map_reset()
except_points.extend([i.cdt for i in important_points[1:]])
start_point = game_map[4][0]
ppd = start_point.get_center_for_shape(pacman)
ppx, ppy = ppd

ok_point_for_enemies = [i.cdt for i in important_points + [game_map[4][0]]], intersection
centers = get_centers(important_points, intersection, shape=pacman)
my_font = pygame.font.SysFont('Comic Sans MS', 30)

ens = {
    'en1': {'image': r"imgs/Clyde.png"},
    'en2': {'image': r"imgs/Blinky.png"},
    'en3': {'image': r"imgs/Inky.png"},
    'en4': {'image': r"imgs/Pinky.png"},
}

intersection_xs, intersection_ys = [cdt[0] for cdt in centers], [cdt[1] for cdt in centers]


def load_enemies():
    for name, enemy in ens.items():
        enemy['load'], enemy['point'] = pygame.image.load(enemy['image']), choice(important_points)
        enemy['cdt'], enemy['rnd_cdt'] = enemy['point'].get_center_for_shape(enemy['load']), []
        enemy['rnd_steps'] = CdtSelector(game_map_pixel, game_map).get_random_path(
            enemy['point'],
            *ok_point_for_enemies
        )


load_enemies()


def check_magnet(cdt, cdts):
    global magnet_result
    for core in cdts:
        if magnet_result >= 3 and cdt != core and (cdt - pacman_steps <= core <= cdt + pacman_steps):
            magnet_result = 0
            return core
    magnet_result += 1
    return cdt


def loop_key():
    global loop_event, pacman, ppx, ppy, magnet_result, tmp_show_pacman_cm
    loop_event = True
    while loop_event:
        if ppy in intersection_ys:
            sleep(0.005)
            ppx = check_magnet(ppx, intersection_xs)
            if event.key == pygame.K_LEFT:
                if ppx <= two_tile_step - (space_between * pacman_steps):
                    ppx = screen_width + two_tile_step
                pacman = pacman_left
                ppx -= pacman_steps
            elif event.key == pygame.K_RIGHT:
                if ppx >= screen_width + two_tile_step:
                    ppx = two_tile_step - (space_between * pacman_steps)
                pacman = pacman_right
                ppx += pacman_steps
        if ppx in intersection_xs:
            ppy = check_magnet(ppy, intersection_ys)
            if event.key == pygame.K_UP:
                if ppy <= two_tile_step - (space_between * pacman_steps):
                    ppy = screen_height + two_tile_step
                pacman = pacman_up
                ppy -= pacman_steps
            elif event.key == pygame.K_DOWN:
                if ppy >= screen_height + two_tile_step:
                    ppy = two_tile_step - (space_between * pacman_steps)
                pacman = pacman_down
                ppy += pacman_steps
        for ob in important_points:
            if ob.inside(*ob.get_center, pacman_steps, (ppx, ppy), pacman):
                tmp_show_pacman_cm = 10  # frame
                except_points.append(ob.cdt)
                Thread(target=pygame.mixer.Sound.play, args=(eat_audio,)).start()
        sleep(.03)


def reload_enemy(enemy):
    if not enemy['rnd_cdt']:
        tmp_rnd_step, enemy['rnd_steps'] = enemy['rnd_steps'][0], enemy['rnd_steps'][1:]
        if not enemy['rnd_steps']:
            enemy['rnd_steps'] = CdtSelector(game_map_pixel, game_map).get_random_path(
                tmp_rnd_step,
                *ok_point_for_enemies
            )
        enemy['rnd_cdt'] = get_space(enemy['cdt'], enemy['rnd_steps'][0], enemy['load'], souls_speed)
    else:
        enemy['cdt'], enemy['rnd_cdt'] = enemy['rnd_cdt'][0], enemy['rnd_cdt'][1:]


def enemy_movement():
    for enemy in ens.values():
        Thread(target=reload_enemy, args=(enemy,)).start()


def wait_for_music(music):
    def play(music):
        while pygame.mixer.get_busy():
            pygame.time.delay(100)
        pygame.mixer.Sound.play(music)

    Thread(target=play, args=(music,)).start()


def end_game():
    global running, loop_event, score
    max_score = len(ok_point_for_enemies[0])
    running, loop_event, score = False, False, f"your score: {max_score - len(important_points)}/{max_score}"
    pygame.mixer.Sound.stop(in_game_audio), pygame.mixer.Sound.stop(intro_audio)


def restart_game():
    global running, except_points, pacman, ppx, ppy
    running, except_points, pacman = True, [], pacman_right
    Thread(target=pygame.mixer.Sound.play, args=(intro_audio,)).start()
    wait_for_music(in_game_audio)
    ppx, ppy = ppd
    load_enemies()


restart_game()

running = True
while True:
    if running:
        for x, y in (enemy['cdt'] for enemy in ens.values()):
            if (
                    ppx - accident_area <= x <= ppx + accident_area and
                    ppy - accident_area <= y <= ppy + accident_area
            ):
                Thread(target=pygame.mixer.Sound.play, args=(death_audio,)).start(), end_game()
        if not important_points:
            Thread(target=pygame.mixer.Sound.play, args=(win_audio,)).start(), end_game()

        Thread(target=enemy_movement).start(), Thread(target=game_map_reset).start()
        if tmp_show_pacman_cm:
            tmp_show_pacman_cm -= 1
            screen.blit(pacman_c_m, (ppx, ppy))
        else:
            screen.blit(pacman, (ppx, ppy))

        for name, enemy in ens.items():
            screen.blit(enemy['load'], enemy['cdt'])
    else:
        img = GameOver if important_points else WIN
        cdt = img.get_size()
        opacity_animation = pygame.Surface((screen_width, screen_height))
        opacity_animation.set_alpha(10), opacity_animation.fill((128,) * 3)
        screen.blit(opacity_animation, (0, 0)), img.set_alpha(50)
        screen.blit(img, (cdt[0] + 5, cdt[1]))

        score_surface = my_font.render(score, False, (0, 255, 10))
        screen.blit(score_surface, (cdt[0] + 50, cdt[1] + 65))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
        if running:
            if event.type == pygame.KEYDOWN:
                Thread(target=loop_key).start()
            elif event.type == pygame.KEYUP:
                loop_event = False
        else:
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if mouse_inside((348, 327), (482, 354), pos):
                    restart_game()
                elif mouse_inside((567, 331), (628, 357), pos):
                    pygame.quit()

    pygame.display.flip()
    clock.tick(60)
