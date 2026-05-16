def print_board(board): #Вывод игрового поля

    print("\n")
    print("  0 | 1 | 2 ") #+ номера столбцов
    for i, row in enumerate(board):
        print(f'{i}'" " + " | ".join(row)) #+ номера строк
        if i < 2:
            print(" ---|---|---")
    print("\n")


def check_win(board, player): #Проверка на победу

    #Проверка строк / столбцов
    for i in range(3):
        if all(board[i][j] == player for j in range(3)):  # строки
            return True
        if all(board[j][i] == player for j in range(3)):  # столбцы
            return True
    #Проверка диагонали
    if all(board[i][i] == player for i in range(3)):  # главная
        return True
    if all(board[i][2 - i] == player for i in range(3)):  # обратная
        return True
    return False


def is_full(board): #Проверка доски на свободные ячейки

    return all(cell != " " for row in board for cell in row)


def tic_tac(): #Функция игры

    board = [[" " for _ in range(3)] for _ in range(3)]
    current_player = "X"

    print("Игра Крестики-нолики")
    print("Игрок 1 - Х, Игрок 2 - 0")

    while True:
        print_board(board)
        print(f"Ход игрока '{current_player}'")
        print("Введите ход: строка (от 0 до 2) и столбец (от 0 до 2)")

        try:
            row = int(input("Строка (0-2): "))
            col = int(input("Столбец (0-2): "))

            if not (0 <= row <= 2 and 0 <= col <= 2):
                print("Ошибка: введите координаты хода в формате числа от 0 до 2")
                continue

            if board[row][col] != " ":
                print("Ошибка: ячейка занята, повторите попытку")
                continue

            board[row][col] = current_player

            if check_win(board, current_player):
                print_board(board)
                print(f"Игрок '{current_player}' победил!")
                break

            if is_full(board):
                print_board(board)
                print("Ничья")
                break

            current_player = "O" if current_player == "X" else "X"

        except ValueError:
            print("Ошибка: введите числа!")


# Запуск игры
tic_tac()