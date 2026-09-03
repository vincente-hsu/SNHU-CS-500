import math

print("Choose one of the following operations:\n addition\n subtraction\n multiplication\n division")
operations = input()

while(operations != 'exit'):
    if ((operations != 'addition') and (operations != 'subtraction') and (operations != 'multiplication') and (operations != 'division')):
        operations = input('Your operation was not an acceptable input. Please try again: ')
    else:
        numbers = input('Choose two numbers: ').split()
        while (all(isinstance(val, float) for val in numbers) != True):
            for i in range(2):
                try:
                    numbers[i] = float(numbers[i])
                except ValueError:
                    if ('/' in numbers[i]):
                        fraction = numbers[i].split('/')
                        for j in range(2):
                            if (fraction[j] == 'pi'):
                                fraction[j] = math.pi
                            elif (fraction[j] == 'e'):
                                fraction[j] = math.e
                        numbers[i] = float(fraction[0]) / float(fraction[1])
                    elif ('sqrt(' in numbers[i]):
                        if (numbers[i][5:-1] == 'pi'):
                            number = math.pi
                        elif (numbers[i][5:-1] == 'e'):
                            number = math.e
                        else:
                            number = float(numbers[i][5:-1])
                        numbers[i] = math.sqrt(number)
                    elif (numbers[i] == 'pi'):
                        numbers[i] = math.pi
                    elif (numbers[i] == 'e'):
                        numbers[i] = math.e
                    else:
                        numbers = input('At least one of your numbers is not acceptable. Please try again: ').split()

        if (operations == 'addition'):
            print(f'{(numbers[0] + numbers[1]):.8g}')
        elif (operations == 'subtraction'):
            print(f'{(numbers[0] - numbers[1]):.8g}')
        elif (operations == 'multiplication'):
            print(numbers[0] * numbers[1])
        else:
            if (numbers[1] == 0):
                print('Cannot divide by 0.')
            else:
                print(numbers[0] / numbers[1])
    
        operations = input('Choose another operation or type exit to leave the program: ')