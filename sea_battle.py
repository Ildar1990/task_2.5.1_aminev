from random import randint


class BoardOutException(Exception):
    def __str__(self):
        return 'Вы пытаетесь выстрелить в клетку за пределами поля.'


class BoardUsedException(Exception):
    def __str__(self):
        return 'Вы пытаетесь стрелять в одну и ту же клетку.'


class ShipErrorException(Exception):
    pass


class Dot:  # Класс точек на поле
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):                            # Метод проверки равенства точек
        return self.x == other.x and self.y == other.y


class Ship:  # Класс корабля
    def __init__(self, length, bow, orient, life):
        self.length = length                            # Длина корабля
        self.bow = bow                                  # Точка, где расположен нос корабля
        self.orient = orient                            # Направление корабля
        self.life = life                                # Количество жизни

    def dots(self):                                     # Метод возврата списка всех точек корабля
        ship_dots = []

        for d in range(self.length):
            ship_x = self.bow.x
            ship_y = self.bow.y
            if self.orient == 1:
                ship_x += d
            elif self.orient == 0:
                ship_y += d
            ship_dots.append(Dot(ship_x, ship_y))

        return ship_dots


class Board:  # Класс игровой доски
    def __init__(self):
        self.field = [['O' for _ in range(6)] for _ in range(6)]     # Двумерный список
        self.ship_list = []                         # Список кораблей доски
        self.hid = None                             # Параметр скрытия кораблей на доске
        self.live_ships = 7                         # Количество живых кораблей
        self.busy_dots = []                         # В этот список будут включаться точки кораблей и их контуров
        self.attacked_dots = []                     # В этот список будут включаться точки выстрелов

    def add_ship(self, ship):                       # Метод установки кораблей

        for i in ship.dots():
            if self.out(i) or i in self.busy_dots:
                raise ShipErrorException()          # Выбрасывание исключения при невозможности установки корабля

        for i in ship.dots():
            self.field[i.x][i.y] = "■"              # Отображение корабля
            self.busy_dots.append(i)

        self.ship_list.append(ship)
        self.contour(ship)

    def contour(self, ship):                        # Метод обводки корабля по контуру
        around = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        for i in ship.dots():
            for jx, jy in around:
                cell = Dot(i.x + jx, i.y + jy)
                if not (self.out(cell)) and cell not in self.busy_dots:
                    self.busy_dots.append(cell)

    def __str__(self):                              # Метод визуализации доски на консоле
        board = ' |1|2|3|4|5|6|'
        for i in range(6):
            row = '|'.join(self.field[i])
            board += f'\n{i + 1}|{row}|'

        if self.hid:
            board = board.replace("■", "O")

        return board

    @staticmethod
    def out(dot_out):                               # Проверяем, что точки находятся в пределах доски
        return dot_out.x < 0 or dot_out.x > 5 or dot_out.y < 0 or dot_out.y > 5

    def shot(self, shot_dot):                       # Метод вызова выстрела
        if self.out(shot_dot):
            raise BoardOutException()               # Выбрасывание исключения при попытке выстрела за пределы поля

        if shot_dot in self.attacked_dots:
            raise BoardUsedException()              # Выбрасывание исключения при выстреле в одну и ту же клетку

        self.attacked_dots.append(shot_dot)

        for ship in self.ship_list:
            if shot_dot in ship.dots():
                ship.life -= 1
                self.field[shot_dot.x][shot_dot.y] = "X"  # Обозначение подбитого корабля
                if ship.life == 0:
                    self.live_ships -= 1
                    self.contour(ship)
                    print("Уничтожен.")
                    return True
                else:
                    print("Ранен.")
                    return True

        self.field[shot_dot.x][shot_dot.y] = "T"          # Обозначение промаха
        print("Промах.")
        return False


class Player:  # Класс игрока
    def __init__(self, own_board, enemy_board):
        self.own_board = own_board                        # Собственная доска
        self.enemy_board = enemy_board                    # Доска врага

    def ask(self):
        raise NotImplementedError()                       # В классах AI, User опеределим метод

    def move(self):                                       # Выполнение хода
        while True:
            try:
                ask_dot = self.ask()                      # Вызываем метод ask
                return self.enemy_board.shot(ask_dot)     # Возвращаем результат выстрела
            except BoardOutException as e:                # Отлавливание исключения при выстреле за пределы поля
                print(e)
            except BoardUsedException as e:               # Отлавливание исключения при выстреле в одну и ту же клетку
                print(e)


class AI(Player):
    def ask(self):
        ai_shot = Dot(randint(0, 5), randint(0, 5))  # Выбор случайной точки
        return ai_shot


class User(Player):
    def ask(self):
        while True:
            x = input('Введите координату строки: ')
            y = input('Введите координату столбца: ')

            if not (x.isdigit()) or not (y.isdigit()):
                print('Введите числа.')
                continue

            x = int(x)
            y = int(y)

            return Dot(x - 1, y - 1)


class Game:  # Класс игры
    def __init__(self):
        user_board = self.random_board()                    # Доска пользователя
        user_board.hid = False
        ai_board = self.random_board()                      # Доска компьютера
        ai_board.hid = True
        self.player_user = User(user_board, ai_board)       # Игрок-пльзователь
        self.player_AI = AI(ai_board, user_board)           # Игрок-компьютер

    def random_board(self):                                 # Генерация случайной доски
        board = None
        while board is None:
            board = self.forming_board()
        return board

    @staticmethod
    def forming_board():
        ship_length = [3, 2, 2, 1, 1, 1, 1]                 # Список длин кораблей
        board = Board()
        attempt = 0

        for i in ship_length:
            while True:
                attempt += 1
                if attempt > 3000:
                    return None
                s = Ship(i, Dot(randint(0, 5), randint(0, 5)), randint(0, 1), i)
                try:
                    board.add_ship(s)
                    break
                except ShipErrorException:
                    pass
        return board

    @staticmethod
    def greet():                                                    # Приветствие
        print('     "Морской бой" приветствует Вас.\n'
              'Цель игры - потопить все корабли противника.\n'
              '   На игровом поле хаотично расположены\n'
              ' корабли: 4 однопалубных, 2 двухпалубных,\n'
              ' 1 трехпалубный. Чтобы сделать ход, введи\n'
              '        номера строки и столбца.')

    def loop(self):                 # Игровой цикл
        num = 0
        while True:
            print('')
            print('Доска пользователя:')
            print(self.player_user.own_board)
            print('')
            print('Доска компьютера:')
            print(self.player_AI.own_board)
            print('')

            if num % 2 == 0:
                print("Ход игрока:")
                additional_move = self.player_user.move()
            else:
                print("Ход компьютера:")
                additional_move = self.player_AI.move()

            if additional_move:
                num -= 1

            if self.player_AI.own_board.live_ships == 0:
                print('')
                print("Пользователь выиграл!")
                break

            if self.player_user.own_board.live_ships == 0:
                print('')
                print("Компьютер выиграл!")
                break

            num += 1

    def start(self):        # Запуск игры
        self.greet()
        self.loop()


game = Game()
game.start()
input('Нажмите Enter, чтобы закрыть окно')