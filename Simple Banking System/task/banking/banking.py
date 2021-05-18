# Write your code here
import random
import sqlite3

connection = sqlite3.connect('card.s3db')  # create connection to built-in SQLite DB
cursor = connection.cursor()  # create a cursor for our connection with DB
cursor.execute('''CREATE TABLE IF NOT EXISTS card 
                  (id integer PRIMARY KEY, number text, pin text, balance integer default 0)''')
connection.commit()
card_number = ''
pin_code = ''
card_bin = 400000
checksum = 0
is_logged_in = False
user_input = ''
login_card = ''
login_pin = ''
card_balance = 0


def print_logged_out_menu():
    print("\n1. Create an account", "2. Log into account", "0. Exit", sep="\n")


def print_logged_in_menu():
    print("\n1. Balance", "2. Add income", "3. Do transfer", "4. Close account",
          "5. Log out", "0. Exit", sep="\n")


def get_input():
    user_input = int(input())
    return user_input


def generate_card_number():
# method to generate new card number using Luhn's algorithm, used for new account creation
# no input, return 16-digit string card number
    card_list = []  # temporary variable needed to calculate checksum
    sum = 0  # sum of altered 15 digits according to Luhn's algorithm
    divisor = 100000000000000  # temporary variable needed to iterate through generated integer to put it into the list
    account_identifier = random.randint(0, 999999999)  # randomly generated, unique part of the card number
    temporary_card_number = account_identifier + card_bin * 1000000000  # 15-digit number, input for Luhn's algorithm
    generated_card_number = str(temporary_card_number)  # generated 15-digit number
    for i in range(15):  # loop to convert generated int to the list type
        card_list.append(int(temporary_card_number // divisor))
        temporary_card_number = temporary_card_number % divisor
        divisor /= 10
    for i in range(0, 15, 1):  # Luhn's algorithm: odd digits are multiplied by 2 and if > 9 subtracted by 9
        if i % 2 == 0:
            card_list[i] *= 2
            if card_list[i] > 9:
                card_list[i] -= 9
        sum += card_list[i]
    if sum % 10 == 0:  # 16th digit in valid cards should make sum of all digits divisible by 10
        checksum = 0
    else:
        checksum = 10 - sum % 10
    generated_card_number = generated_card_number + str(checksum)  # final generated card number
    return generated_card_number



def verify_luhn(number):
# verify if card 16-digit card number is valid according to Luhn's algorithm
# takes string or integer as an input, return Boolean
    checksum = int(int(number) % 10)  # store last digit to a variable (needed in Luhn's algorithm)
    luhn_temp = int(number) // 10  # get 15-digit card number without checksum digit
    card_list = []  # temporary variable to operate with card number while checking on Luhns'
    divisor = 100000000000000
    sum = 0
    for i in range(15):  # loop to convert generated int to the list type
        card_list.append(int(luhn_temp // divisor))
        luhn_temp = luhn_temp % divisor
        divisor /= 10
    for i in range(0, 15, 1):  # Luhn's algorithm: odd digits are multiplied by 2 and if > 9 subtracted by 9
        if i % 2 == 0:
            card_list[i] *= 2
            if card_list[i] > 9:
                card_list[i] -= 9
        sum += card_list[i]
    if (sum + checksum) % 10 == 0:
        return True



def generate_pin_code():
# method to generate pincode for newly created card, no input, return 4-digit string
    pin_code = random.randint(0, 9999)
    if pin_code < 10:
        pin_code = '000' + str(pin_code)
    elif pin_code < 100:
        pin_code = '00' + str(pin_code)
    elif pin_code < 1000:
        pin_code = '0' + str(pin_code)
    else:
        pin_code = str(pin_code)
    return pin_code


# main program
print_logged_out_menu()
user_input = get_input()
while user_input != 0:  # execute program until user enters "0. Exit"
    if user_input == 1 and is_logged_in is False:  # create account menu item
        card_number = generate_card_number()
        pin_code = generate_pin_code()
        cursor.execute('INSERT INTO card (number, pin) VALUES (?, ?)', (card_number, pin_code))
        connection.commit()
        print("\nYour card has been created")
        print("Your card number:", card_number, sep="\n")
        print("Your card PIN:", pin_code, sep="\n")
        print_logged_out_menu()
    elif user_input == 2 and is_logged_in is False:  # login menu item
        while not is_logged_in:
            login_card = input("\nEnter your card number:\n")
            if login_card == '0':
                connection.close()
                print('\nBye!')
                exit()
            else:
                login_pin = input("Enter your PIN:\n")
                if login_pin == '0':
                    connection.close()
                    print('\nBye!')
                    exit()
                cursor.execute("SELECT * FROM card WHERE number=?", (login_card,))
                card_info = cursor.fetchone()
                if card_info is not None:
                    card_number = card_info[1]
                    pin_code = card_info[2]
                    if login_card == card_number and login_pin == pin_code:
                        is_logged_in = True
                        print("\nYou have successfully logged in!")
                        print_logged_in_menu()
                    else:
                        print("\nWrong card number or PIN!\n")
                        print_logged_out_menu()
                else:
                    print("\nWrong card number or PIN!\n")
                    print_logged_out_menu()
    elif user_input == 1 and is_logged_in is True:  # show balance menu item
        cursor.execute("SELECT balance FROM card WHERE number=?", (card_number,))
        card_balance = cursor.fetchone()[0]
        print("\nBalance: ", card_balance)
        print_logged_in_menu()
    elif user_input == 2 and is_logged_in is True:  # increase balance menu item
        income = int(input('\nEnter income:\n'))
        cursor.execute("SELECT balance FROM card WHERE number=?", (login_card,))
        card_balance = cursor.fetchone()[0]
        card_balance += income
        cursor.execute("UPDATE card SET balance=? WHERE number=?", (card_balance, card_number))
        connection.commit()
        print('Income was added!\n')
        print_logged_in_menu()
    elif user_input == 3 and is_logged_in is True:  # transfer to another card menu item
        print('\nTransfer\n')
        target_card = input('Enter card number:\n')
        if not verify_luhn(target_card):
            print('Probably you made a mistake in the card number. Please try again!\n')
            print_logged_in_menu()
        else:
            cursor.execute("SELECT COUNT (number) FROM card WHERE number=?", (target_card,))
            is_card_in_db = cursor.fetchone()[0]
            if is_card_in_db == 0:
                print('Such a card does not exist.')
                print_logged_in_menu()
            elif target_card == card_number:
                print("You can't transfer money to the same account!")
                print_logged_in_menu()
            else:
                transfer_amount = int(input('Enter how much money you want to transfer:'))
                cursor.execute("SELECT balance FROM card WHERE number=?", (card_number,))
                card_balance = int(cursor.fetchone()[0])
                if transfer_amount > card_balance:
                    print('Not enough money!')
                    print_logged_in_menu()
                else:
                    card_balance -= transfer_amount
                    cursor.execute("UPDATE card SET balance=? WHERE number=?", (card_balance, card_number))
                    connection.commit()
                    cursor.execute("SELECT balance FROM card WHERE number=?", (target_card,))
                    card_balance = int(cursor.fetchone()[0])
                    card_balance += transfer_amount
                    cursor.execute("UPDATE card SET balance=? WHERE number=?", (card_balance, target_card))
                    connection.commit()
                    print('Success!')
                    print_logged_in_menu()
    elif user_input == 4 and is_logged_in is True:
        cursor.execute("DELETE FROM card WHERE number=?", (login_card,))
        connection.commit()
        print('The account has been closed!')
        print_logged_out_menu()
    elif user_input == 5 and is_logged_in is True:
        is_logged_in = False
        print("\nYou have successfully logged out!")
        print_logged_out_menu()
    else:
        print("Invalid input")
    user_input = get_input()
connection.close()
print('\nBye!')
