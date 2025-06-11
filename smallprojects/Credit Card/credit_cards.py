import random

# Function that checks if a given input (credit card number passes the luhn algorithm test)
def luhn_algorithm_for_checking_credit_card_numbers(num):
    # The input , is converted into a list of ingegers of the length of the number of digits of the number
    number_to_list = list(map(int, str(num)))
    l = len(number_to_list)
    # A for loop in every run of the loop the starting index i is decremented by a factor of 2.
    # The starting number is the length of the list minus two, because we are staring our search
    # from the position of the number that is right next to the number in the last position.
    # The number where our for loop stops is -1 so  in actuality the for loop goes from l-2 to 0.
    for i in range(l-2, -1, -2):
        # We double every second number starting from the number right next to the last one.
        number_to_list[i] = (2*int(number_to_list[i]))
        # If after the multiplication the  number is two digits 
        if number_to_list[i] >= 10:
            number_to_list[i] = (sum(list(map(int, str(number_to_list[i]))))) #then we replace that number with the sum of the digits.
        else:
            pass # In every other case we don't do anything.
# We create a variable that stores the "supposed" last digit of the number.
# We calculate it by first calculating the remainder of the division of the
# sum of all the digits of our new number but without the last digit and 10.
# Then on this number the remainder of division is calculated once more.
# This second calculation of the remainder is done so to be prepared
# for a case when the remainder of the first division calculation is 0,
# (the sum of the digits is divisible by 10).
    checksum_last_digit = ((10 - (sum(number_to_list[0:l-1]) % 10)) % 10)

    if checksum_last_digit == number_to_list[-1]: # If the "supposed" last digit is the true value of the last digit of the number then it passed the luhn's test 
        print(" The number", num, "is VALID" "\n" "__________________")
        return(True)
    else: #If it's not then that means it is not a valid credit card number. 
        print(" The number", num, "is not valid " "\n" "__________________")


def check_user_input(): #This function checks for user input so a credit card number that is presented by the user.

    while True: #This while loop is always True so always repeating until a break statement breaks the loop.
        number_to_check = input("Please enter a credit card number from 13 to 16 digits ") # Here the input is given
        if (number_to_check.isdigit() and len(str(int(number_to_check))) in range(12, 17)): # We check if the input meets our requirements.
            luhn_algorithm_for_checking_credit_card_numbers(number_to_check) # If it checks the requirements then it is checked by the luhn algorithm's function. 
            break

        else:
            print("ERROR: The number has to be a positive integer and has to be between 13 and 16 digits") # If the inputted data doesn't meet the requirements an error is thrown.
    start_the_credit_card_validator()


def check_for_generated_random_numbers(n): 
# This function generates random credit card numbers from 13 to 16 digits. 
# It takes one argument the number of numbers to be generated.
    valid_number_list = [] # This list stores the valid credit card numbers.
    number_of_valid_credit_card_numbers = 0 # This variable stores the number of valid credit card numbers. Initially the number is set to 0.
    number_of_generated_credit_card_numbers = n # This variable stores the number passed to the function as the number of credit card numbers to be generated. 
    for i in range(0, number_of_generated_credit_card_numbers):
        # This for loop runs for as many times as the number of credit card numbers to be generated.
        number_of_characters_of_the_credit_card = int((random.randint(13, 16))) 
        # This variable stores the number of digits that the number should have it is either 13,14,15,16
        random_credit_card_number = random.randint(10**(number_of_characters_of_the_credit_card-1), (10**(number_of_characters_of_the_credit_card))-1)
        # The credit card is a random number in specific range. 
        # This range where the starting point is 10 to the power of (the number of characters), we subtract 1 from the exponent.
        # The ending point is 10 to the power of the number of characters but this time we subtract one from the whole number.
        # This approach ensures that the random number stays in this specific narrow range of digits.

        
        if luhn_algorithm_for_checking_credit_card_numbers(random_credit_card_number): 
            # We check the random number through the function of the luhn algorithm if the function returns true (the number is valid)
            number_of_valid_credit_card_numbers += 1 # We increment the number of valid credit card numbers by 1.
            valid_number_list.append(random_credit_card_number) # We add this random credit card number to our list.
    ratio_of_validity_percentage = (number_of_valid_credit_card_numbers/number_of_generated_credit_card_numbers)*100 # We calculate the percentage of valid credit card numbers.
    print(number_of_generated_credit_card_numbers, "randomly generated credit card numbers have been generated and checked with the luhn algorithm.", # We display every information
          "\n", ratio_of_validity_percentage, "% of the numbers are valid" "\n" "********************" "\n" "This is the list of valid credit card numbers: ")

    for i in (valid_number_list): # This loop is used for displaying the list of valid numbers.
        print(i)

    

def start_the_credit_card_validator(): # This function starts the random card generation.
 while True: # The while loop runs until break.
    n = (input("How many random credit card numbers do you want to generate? ")) # The user is asked for input 
    if (n.isnumeric() and int(n)>0): # If input is numeric and greater than zero the proceed to the statement below.
        check_for_generated_random_numbers(int(n)) # The function for generating random credit card numbers is called with this input.
        break
    else:
        print("Enter a correct number! ") # If the input doesn't meet the criteria, ask for another number. 
        
check_user_input()
