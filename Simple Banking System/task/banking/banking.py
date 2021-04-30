# Write your code here
from random import randint
import sqlite3


def get_pin():
    return "{}{}{}{}".format(randint(0, 9), randint(0, 9), randint(0, 9), randint(0, 9))


def print_details(card_number, check_sum, pin):
    print('\nYour card has been created')
    print('Your card number:')
    print('400000' + str(card_number).zfill(9) + check_sum)
    print('Your card PIN:')
    print(pin + '\n')


def get_check_sum(card_number):
    '''Luhn alogrithm'''
    card_number = list(map(int, list(card_number)))
    # multiply odd numbers with 2
    for i, val in enumerate(card_number):
        if i % 2 == 0:
            card_number[i] = val * 2
    # subtract 9 from numbers over 9
    for i, val in enumerate(card_number):
        if val > 9:
            card_number[i] = val - 9
    total = sum(card_number)
    return str((10 - (total % 10)) % 10)


def create_account():
    global array, cur, conn
    card_number, pin = array[-1][0] + 1, get_pin()
    card_num = '400000' + str(card_number).zfill(9)
    check_sum = get_check_sum(card_num)
    card_num = card_num + check_sum
    array.append([card_number, check_sum, pin])
    cur.execute("INSERT INTO card VALUES ({}, '{}', '{}', 0)".format(card_number, card_num, pin))
    conn.commit()
    print_details(card_number, check_sum, pin)


def print_login():
    print('1. Balance')
    print('2. Add income')
    print('3. Do transfer')
    print('4. Close account')
    print('5. Log out')
    print('0. Exit')


def add_income(output, amount):
    global cur, conn
    output = cur.execute("SELECT * FROM card WHERE id = ?", (output[0], ))
    output = output.fetchall()[0]
    amount = amount + output[3]
    cur.execute("UPDATE card SET balance = ? WHERE id = ?", (amount, output[0],))
    conn.commit()


def get_card(card_number):
    global cur
    out = cur.execute("SELECT * FROM card WHERE number = ?", (card_number,))
    return out.fetchall()


def transfer_money(from_card, to_card):
    amount = int(input('Enter how much money you want to transfer:\n'))
    if get_balance(from_card) < amount:
        print('Not enough money!\n')
    else:
        add_income(from_card, -amount)
        add_income(to_card, amount)
        print('Success!\n')


def do_transfer(from_card):
    print('Transfer')
    card_number = input('Enter card number:\n')
    check_sum = get_check_sum(card_number[:15])
    if check_sum != card_number[-1]:
        print('Probably you made a mistake in the card number. Please try again!\n')
        return
    to_card = get_card(card_number)
    if not to_card:
        print('Such a card does not exist.\n')
        return
    transfer_money(from_card, to_card[0])


def close_account(output):
    global cur, conn
    cur.execute("DELETE FROM card WHERE id = ?", (output[0],))
    conn.commit()
    print('\nThe account has been closed!\n')


def get_balance(output):
    global cur
    cur.execute("SELECT * FROM card WHERE id = ?", (output[0], ))
    return cur.fetchall()[0][3]


def login_process(n, output):
    if n == '0':
        print('\nBye!')
        exit(0)
    elif n == '1':
        print('\nBalance: {}\n'.format(get_balance(output)))
    elif n == '2':
        amount = int(input('Enter income:\n'))
        add_income(output, amount)
        print('Income was added!\n')
    elif n == '3':
        do_transfer(output)
    elif n == '4':
        close_account(output)
    elif n == '5':
        print('\nYou have successfully logged out!\n')


def login(output):
    n = 0
    while n != '5':
        print_login()
        n = input()
        login_process(n, output)


def check_login():
    global array, cur
    card_number = input('Enter your card number:\n')
    pin = input('Enter your PIN:\n')
    bin_condition = '400000' == card_number[:6]
    output = cur.execute("SELECT * FROM card WHERE number='{}' and pin = '{}'".format(card_number, pin))
    output = output.fetchall()
    if bin_condition and output:
        print('\nYou have successfully logged in!\n')
        login(output[0])
    else:
        print('\nWrong card number or PIN!\n')


def main_process(n):
    if n == '0':
        print('\nBye!')
        exit(0)
    elif n == '1':
        create_account()
    elif n == '2':
        check_login()


def print_home():
    print('1. Create an account')
    print('2. Log into account')
    print('0. Exit')


def main():
    print_home()
    n = input()
    main_process(n)


if __name__ == '__main__':
    array = [[0, 0, 0000]]
    conn = sqlite3.connect('card.s3db')
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS card(id INTEGER, number TEXT, pin TEXT, balance INTEGER DEFAULT 0)")
    conn.commit()
    output = cur.execute("SELECT * FROM card").fetchall()
    if output:
        output = output[-1]
        array.append([output[0], output[1][-1], output[2]])
    while True:
        main()
    conn.close()
