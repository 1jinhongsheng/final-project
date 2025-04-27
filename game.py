import random

# ===== 读取怪物数据 =====
def load_monsters():
    monsters = []
    with open("monsters.txt", "r", encoding="utf-8") as f:
        lines = f.readlines()
        for line in lines[1:]:
            parts = line.strip().split(",")
            if len(parts) != 3:
                continue
            name, mtype, hp = parts
            monster = {"name": name, "type": mtype, "hp": int(hp), "attack": 10, "max_hp": int(hp)}
            monsters.append(monster)
    return monsters

# ===== 初始宝可梦选择 =====
def choose_starter():
    starters = [
        {"name": "Ignibra", "type": "Fire", "hp": 40, "attack": 10, "max_hp": 40},
        {"name": "Glacoon", "type": "Water", "hp": 45, "attack": 10, "max_hp": 45},
        {"name": "Sprigup", "type": "Grass", "hp": 50, "attack": 10, "max_hp": 50}
    ]
    starter = random.choice(starters)
    print("You got:", starter["name"])
    return starter

# ===== 属性相克判断 =====
def is_effective(attacker, defender):
    return (attacker == "Water" and defender == "Fire") or \
           (attacker == "Fire" and defender == "Grass") or \
           (attacker == "Grass" and defender == "Water")

def is_weak(attacker, defender):
    return is_effective(defender, attacker)

# ===== 楼层怪物生成 =====
def get_monsters_for_level(level, all_monsters):
    if level <= 5:
        return random.sample(all_monsters, 1)
    elif level <= 10:
        return random.sample(all_monsters, 2)
    elif level <= 15:
        return random.sample(all_monsters, 3)
    elif level <= 19:
        return random.sample(all_monsters, 4)
    else:
        return [{"name": "Monster Pillar", "type": "Fire", "hp": 200, "attack": 25, "max_hp": 200}]

# ===== 战斗系统 =====
def battle(team, enemy, items):
    while len(team) > 0 and enemy["hp"] > 0:
        player = team[0]
        print("\nYour Pokemon:", player["name"], "Type:", player["type"], "HP:", player["hp"])
        print("Enemy:", enemy["name"], "Type:", enemy["type"], "HP:", enemy["hp"])

        print("\nChoose an action: [1] Attack  [2] Special Attack  [3] Defend")
        choice = input("Your move: ")

        if choice == "1":
            damage = player["max_hp"] // 8
            if "sword" in items:
                damage *= 2
                print("Sword used! Attack doubled!")
                items.remove("sword")
            enemy["hp"] -= damage
            print("You used Attack! Damage:", damage)

        elif choice == "2":
            if is_effective(player["type"], enemy["type"]):
                damage = player["max_hp"] // 4
                print("Super Effective!")
            elif is_weak(player["type"], enemy["type"]):
                damage = (player["max_hp"] // 6) // 2
                print("Not very effective...")
            else:
                damage = player["max_hp"] // 6
            if "sword" in items:
                damage *= 2
                print("Sword used! Special attack doubled!")
                items.remove("sword")
            enemy["hp"] -= damage
            print("You used Special Attack! Damage:", damage)

        elif choice == "3":
            print("You are defending this turn.")
        else:
            print("Invalid input. Turn skipped.")
            continue

        if enemy["hp"] <= 0:
            print("Enemy defeated!")
            return True

        if enemy["name"] == "Monster Pillar":
            if enemy["hp"] < 40:
                actual_attack = enemy["max_hp"] // 4
                print("Boss uses Special Attack!")
            else:
                actual_attack = enemy["max_hp"] // 8
                print("Boss uses Normal Attack!")
        else:
            enemy_choice = random.choice(["normal", "special"])
            if enemy_choice == "normal":
                actual_attack = enemy["max_hp"] // 8
                print("Enemy uses normal attack!")
            else:
                if is_effective(enemy["type"], player["type"]):
                    actual_attack = enemy["max_hp"] // 4
                    print("Enemy uses special attack! It's super effective!")
                elif is_weak(enemy["type"], player["type"]):
                    actual_attack = (enemy["max_hp"] // 6) // 2
                    print("Enemy uses special attack! It's not very effective...")
                else:
                    actual_attack = enemy["max_hp"] // 6
                    print("Enemy uses special attack!")

        if choice == "3":
            actual_attack //= 2
            print("You defended! Damage halved.")

        if "shield" in items:
            actual_attack //= 2
            print("Shield used! Enemy damage halved again!")
            items.remove("shield")

        player["hp"] -= actual_attack
        print("Enemy attacks! You take damage:", actual_attack)

        if player["hp"] <= 0:
            print(player["name"], "has fainted!")
            team.pop(0)

    return enemy["hp"] <= 0

# ===== 单局游戏逻辑 =====
def run_game():
    monsters = load_monsters()
    team = [choose_starter()]
    items = []

    for level in range(1, 21):
        print("\n====================")
        print("Floor", level)
        enemies = get_monsters_for_level(level, monsters)

        for enemy in enemies:
            if len(team) == 0:
                print("All Pokemon fainted. Game Over. Restarting...\n")
                return False

            win = battle(team, enemy, items)

            if not win:
                continue

            if enemy["name"] == "Monster Pillar":
                print("You defeated the Boss! YOU WIN!")
                return True

            if len(team) > 0:
                team[0]["hp"] = team[0]["max_hp"]
                print("You are fully healed for the next battle!")

            print("Choose reward: 1.Capture  2.Item")
            reward = input("Your choice: ")
            if reward == "1":
                if len(team) >= 4:
                    print("Team full. Can't capture.")
                else:
                    enemy_copy = enemy.copy()
                    team.append(enemy_copy)
                    print("Captured", enemy["name"])
            elif reward == "2":
                item = random.choice(["sword", "shield"])
                print("You got a", item)
                items.append(item)
            else:
                print("No reward.")
    return True

# ===== 主流程循环 =====
def play_game():
    while True:
        success = run_game()
        if success:
            break

# ===== 启动游戏 =====
play_game()
