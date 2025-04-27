import pygame
import random
import sys

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tower Battle")
font = pygame.font.SysFont(None, 28)
clock = pygame.time.Clock()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)

try:
    victory_image = pygame.image.load("2052048d-6dfb-475d-875f-f00d7e56f764.png")
    victory_image = pygame.transform.scale(victory_image, (WIDTH, HEIGHT))
except Exception as e:
    print("submit wrong：", e)
    victory_image = None

def draw_text(text, x, y):
    line = font.render(text, True, BLACK)
    screen.blit(line, (x, y))

class Button:
    def __init__(self, text, x, y, w, h, callback):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.callback = callback

    def draw(self):
        pygame.draw.rect(screen, GRAY, self.rect)
        txt = font.render(self.text, True, BLACK)
        screen.blit(txt, (self.rect.x + 10, self.rect.y + 10))

    def check_click(self, pos):
        if self.rect.collidepoint(pos):
            self.callback()

def load_monsters():
    monsters = []
    with open("monsters.txt", "r", encoding="utf-8") as f:
        lines = f.readlines()[1:]
        for line in lines:
            parts = line.strip().split(",")
            if len(parts) != 3:
                continue
            name, mtype, hp = parts
            monsters.append({"name": name, "type": mtype, "hp": int(hp), "max_hp": int(hp)})
    return monsters

def is_effective(attacker, defender):
    return (attacker == "Water" and defender == "Fire") or \
           (attacker == "Fire" and defender == "Grass") or \
           (attacker == "Grass" and defender == "Water")

def is_weak(attacker, defender):
    return is_effective(defender, attacker)

boss = {
    "name": "Monster Pillar",
    "type": "Fire",
    "hp": 100,
    "max_hp": 100
}

monsters = load_monsters()
player = random.choice([
    {"name": "Ignibra", "type": "Fire", "hp": 40, "max_hp": 40},
    {"name": "Glacoon", "type": "Water", "hp": 45, "max_hp": 45},
    {"name": "Sprigup", "type": "Grass", "hp": 50, "max_hp": 50}
])
team = [player]
max_team_size = 6
enemy = random.choice(monsters)
enemy["hp"] = enemy["max_hp"]
log = []
reward_pending = False
floor = 1
items = []
game_result = None

def choose_reward(capture):
    global enemy, team, monsters, log, reward_pending
    if capture:
        if len(team) < max_team_size:
            new_mon = enemy.copy()
            new_mon["hp"] = new_mon["max_hp"]  
            team.append(new_mon)
            log.append(f"You captured {enemy['name']}!")
        else:
            log.append("Team full. Can't capture more.")
    else:
        item = random.choice(["sword", "shield"])
        items.append(item)
        log.append(f"You received a {item}!")
    reward_pending = "next"

def check_battle_end():
    global enemy, team, log, reward_pending, game_result
    if enemy["hp"] <= 0:
        enemy["hp"] = 0
        log.append(f"Enemy {enemy['name']} defeated!")
        if enemy["name"] == "Monster Pillar":
            log.append("You defeated the Boss! Victory!")
            reward_pending = True
            game_result = "win"
            return True
        reward_pending = True
        return True

    if team and team[0]["hp"] <= 0:
        log.append(f"{team[0]['name']} fainted!")
        team.pop(0)
        if not team:
            log.append("All Pokemon fainted! Game Over.")
            game_result = "lose"
        else:
            if team[0]["hp"] <= 0:
                team[0]["hp"] = team[0]["max_hp"]
            log.append(f"Switched to {team[0]['name']}!")
    return False

def attack():
    global enemy, log
    if enemy["hp"] <= 0 or not team or reward_pending:
        return
    player = team[0]
    damage = player["max_hp"] // 8
    if "sword" in items:
        damage *= 2
        log.append("Sword used! Attack doubled!")
        items.remove("sword")
    enemy["hp"] -= damage
    log.append(f"You used Attack! Damage: {damage}")
    if check_battle_end():
        return
    enemy_turn()

def special():
    global enemy, log
    if enemy["hp"] <= 0 or not team or reward_pending:
        return
    player = team[0]
    if is_effective(player["type"], enemy["type"]):
        damage = player["max_hp"] // 4
        log.append("Super Effective!")
    elif is_weak(player["type"], enemy["type"]):
        damage = (player["max_hp"] // 6) // 2
        log.append("Not very effective...")
    else:
        damage = player["max_hp"] // 6
    if "sword" in items:
        damage *= 2
        log.append("Sword used! Special attack doubled!")
        items.remove("sword")
    enemy["hp"] -= damage
    log.append(f"You used Special! Damage: {damage}")
    if check_battle_end():
        return
    enemy_turn()

def defend(defending=True):
    global log
    if enemy["hp"] <= 0 or not team or reward_pending:
        return
    log.append("You defended. Damage next turn will be halved.")
    enemy_turn(defending=True)

def enemy_turn(defending=False):
    global log
    if enemy["hp"] <= 0 or not team:
        return
    if len(team) == 0:
        return
    player = team[0]
    if enemy["name"] == "Monster Pillar":
        if enemy["hp"] < enemy["max_hp"] * 0.2:
            damage = enemy["max_hp"] // 4
            log.append("Boss used SPECIAL attack!")
        else:
            damage = enemy["max_hp"] // 8
            log.append("Boss used regular attack.")
    else:
        damage = enemy["max_hp"] // 8
    if defending:
        damage //= 2
        log.append("You defended! Damage halved.")
    if "shield" in items:
        damage //= 2
        log.append("Shield used! Enemy damage halved.")
        items.remove("shield")
    player["hp"] -= damage
    log.append(f"Enemy attacks! You take damage: {damage}")
    if check_battle_end():
        return

buttons = [
    Button("Attack", 100, 500, 150, 40, attack),
    Button("Special Attack", 300, 500, 200, 40, special),
    Button("Defend", 550, 500, 150, 40, defend),
    Button("Capture", 200, 400, 150, 40, lambda: choose_reward(True)),
    Button("Item", 450, 400, 150, 40, lambda: choose_reward(False)),
    Button("Next Floor", 325, 450, 150, 40, lambda: None)
]

running = True
while running:
    screen.fill(WHITE)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            for btn in buttons:
                if reward_pending == "next" and btn.text == "Next Floor":
                    floor += 1
                    if floor == 20:
                        enemy = boss.copy()
                    else:
                        enemy = random.choice(monsters)
                        enemy["hp"] = enemy["max_hp"]
                    if team:
                        if team[0]["hp"] <= 0:
                            log.append(f"{team[0]['name']} fainted after reward. Switching...")
                            team.pop(0)
                            if not team:
                                log.append("All Pokemon fainted! Game Over.")
                                game_result = "lose"
                    if team:
                        team[0]["hp"] = team[0]["max_hp"]
                    reward_pending = False
                else:
                    btn.check_click(event.pos)

    if game_result == "lose":
        draw_text("YOU LOSE!", WIDTH // 2 - 60, HEIGHT // 2)
    elif game_result == "win":
        draw_text("YOU WIN!", WIDTH // 2 - 60, HEIGHT // 2)
    else:
        draw_text(f"Floor: {floor}", 50, 10)
        if team:
            player = team[0]
            draw_text(f"Your Pokemon: {player['name']}  Type: {player['type']}  HP: {player['hp']}", 50, 40)
        draw_text(f"Enemy: {enemy['name']}  Type: {enemy['type']}  HP: {enemy['hp']}", 50, 80)

        y = 130
        for line in log[-6:]:
            draw_text(line, 50, y)
            y += 30

        for btn in buttons:
            if reward_pending == True and btn.text in ["Attack", "Special Attack", "Defend", "Next Floor"]:
                continue
            if reward_pending == "next" and btn.text not in ["Next Floor"]:
                continue
            if not reward_pending and btn.text in ["Capture", "Item", "Next Floor"]:
                continue
            btn.draw()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
