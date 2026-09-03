import os
from pathlib import Path

import pandas as pd
import json

import numpy as np
import matplotlib.pyplot as plt

import functions


# This sets up the general class, which creates the appropriate dictionary
# with month keys and a method to get the average value.
class Money:
    def __init__(self, money_list):
        self.__list__ = money_list
        self.dict = functions.to_month_dict(self.__list__)
    
    def average(self):
        return np.average(list(self.dict.values()))
    
    def sum(self):
        return sum(self.dict.values())
    

# This class is defined for expenses, and gains a new method that determines
# which month or months have the largest expense.
class Expense(Money):
    def __init__(self, money_list, name):
        self.name = name
        if type(money_list) == list:
            super().__init__(money_list)
        elif type(money_list) == pd.DataFrame:
            self.__dataframe__ = money_list
            self.dict = dict(zip(money_list.index, money_list['amount']))

    def maximum(self):
        self.__maximum_value__ = max(self.dict.values())
        if (self.__maximum_value__ == 0):
            print(f'There was no month with a maximum expense for {self.name} '
                  'since it was $0.')
        else:
            self.__keys__ = [month for month, value in self.dict.items()
                             if value == self.__maximum_value__]
            if (len(self.__keys__) == 1):
                print(f'The month with the maximum expense in {self.name} was '
                      f'{self.__keys__[0]}, spending ${self.__maximum_value__:.2f}.')
            else:
                print(f'The months with the maximum expense in {self.name} were '
                      f'{', '.join(self.__keys__)}. You spent ${self.__maximum_value__:.2f}'
                      ' in each month.')
    

# This class is defined just for monthly income, with the method determining
# which month or months that had the greatest income. This is solely for
# when income is not necessarily the same every month, as opposed to an
# annual income that is considered distributed equally every month.
class Income(Money):
    def __init__(self, money_list):
        if type(money_list) == list:
            super().__init__(money_list)
        elif type(money_list) == pd.DataFrame:
            self.__dataframe__ = money_list
            self.dict = dict(zip(money_list.index, money_list['income']))

    def maximum(self):
        self.__maximum_value__ = max(self.dict.values())
        self.__keys__ = [month for month, value in self.dict.items()
                         if value == self.__maximum_value__]
        if (len(self.__keys__) == 1):
            print(f'The month with the maximum income was {self.__keys__[0]}, making '
                  f'${self.__maximum_value__:.2f}.')
        else:
            print(f'The months with the maximum income were {', '.join(self.__keys__)}. '
                  f'You made ${self.__maximum_value__:.2f} in each month.')




annual_vs_monthly = input("Enter 'annual' to input your annual income or "
                          "'monthly' to input monthly incomes: ")
# This checks that the input is only either 'annual' or 'monthly' and no
# other inputs are allowed.
while (annual_vs_monthly.lower() != 'annual' and annual_vs_monthly.lower() != 'monthly'):
    annual_vs_monthly = input('Your input could not be accepted. Please type '
                              'annual or monthly: ')

# This checks thats the input can be converted into float and are within
# the allowed range.
if annual_vs_monthly.lower() == 'annual':
    income = input('Enter your current annual income: ')
    acceptable_income = False
    while (not acceptable_income):
        try:
            income = float(income) / 12
        except ValueError:
            income = input('Your input could not be read. Please try again. Do '
                           'not include the $ character. ')
            continue
        
        if (income > functions.maximum_value_allowed or income < 0):
            income = input('Your input was outside the allowed range (0 to 1M). '
                           'Please choose a different number: ')
            continue

        acceptable_income = True
else:
    # In the monthly case, the input may either be a csv/tsv file or a JSON file
    # to be read, or values the user provides directly. We check that the input
    # is allowed, then move on. If yes, the user is prompted to enter the name
    # for their file. If not, the user provides values directly.
    data_frame_exist = input('If you would like to read a csv/tsv, an excel, or a '
                             'JSON file, type csv for csv/tsv, excel for excel, or '
                             'json for JSON. Otherwise, type n to directly input '
                             'into a list: ')
    while (data_frame_exist.lower() != 'csv' and data_frame_exist.lower() != 'excel'
           and data_frame_exist.lower() != 'json' and data_frame_exist.lower() != 'n'):
        data_frame_exist = input('Your input could not be accepted. Please '
                                 'type csv, excel, json, or n: ')
    
    if (data_frame_exist.lower() == 'csv'):
        csv_to_read = input('Enter the path of the file you would like to read: ').strip()
        # The file is checked to ensure it is a valid file. Otherwise, the user is
        # prompted to input a new file or change their original file first.
        readable = False
        while (not readable):
            try:
                # The file is checked if it exists within the allowed directory.
                csv_to_read = (functions.parent_path/csv_to_read).resolve()

                if not csv_to_read.is_relative_to(functions.parent_path):
                    csv_to_read = input('Your file path was inaccessible. Please choose a '
                                        'different file: ').strip()
                    continue
                # The file may not have more than 12 lines, excluding the header.                
                with open(csv_to_read, 'r', encoding='utf-8-sig') as f:
                    lines = []
                    for _ in range(14):
                        line = f.readline()
                        if not line:
                            break
                        lines.append(line)
                
                if (len(lines) > 13):
                    csv_to_read = input('Your file contained too many values. Please change your '
                                        'file or choose a new file: ').strip()
                    continue
                # The file is first read based on the month and income columns.
                monthly_income = pd.read_csv(csv_to_read, sep=r'[,\t]', engine='python',
                                             usecols = ['month', 'income'], encoding='utf-8-sig')
                # This ensures that the months names are in 3-letter abbreviation
                # for later dictionary conversion.
                monthly_income['month'] = monthly_income['month'].str.strip().str[0:3]
                # If there are any invalid month names, the user is prompted to
                # fix them before reentering.
                if (not monthly_income['month'].isin(functions.months).all()):
                    csv_to_read = input('Your file contains an invalid month. Please change your '
                                        'file or choose a new file: ').strip()
                    continue
                # If the file is empty, then the values are presumed to be all zeroes.
                if monthly_income.empty:
                    print('Since you had no input, all values will default to 0.')
                    monthly_income = [0 for _ in range(12)]
                    readable = True
                    break
                # If the file contains any duplicate months, the user is prompted
                # to correct them before reentry.
                if monthly_income['month'].duplicated().any():
                    csv_to_read = input('Your file contained duplicated months. Please change your '
                                        'file or choose a new file: ').strip()
                    continue
                # The values in the file are checked to be numerical and not over
                # the maximum allowed value. Any NaN values will be regarded as zero.
                monthly_income['income'] = pd.to_numeric(monthly_income['income'], errors = 'raise').fillna(0)

                if ((monthly_income['income'] > functions.maximum_value_allowed).any() or (monthly_income['income'] < 0).any()):
                    csv_to_read = input('Your file contained values outside the allowed range (-1M to 1M). '
                                        'Please choose a different file: ').strip()
                    continue
                # If any months are missing in between provided months, then their
                # values are defaulted to zero.
                monthly_income = monthly_income.set_index('month')
                last_month = monthly_income.index[-1]
                index = functions.months.index(last_month)
                existing_months = functions.months[:index + 1]
                monthly_income = monthly_income.reindex(existing_months, fill_value=0)
                readable = True
                break
            # If there are any errors while reading or checking values, the user is
            # prompted to fix them or choose a new file.
            except UnicodeDecodeError:
                csv_to_read = input('Your file is in an unreadable format. Please save it in '
                                    'standard UTF-8 or choose a different file: ')
                continue
            except (ValueError, KeyError, TypeError, AttributeError, pd.errors.EmptyDataError, pd.errors.ParserError):
                csv_to_read = input('Your file could not be properly read. Please check your '
                                    'file or choose a different file: ')
                continue
            except FileNotFoundError:
                csv_to_read = input('Your file could not be found. Please check your file name: ')
                continue
            except (PermissionError, IsADirectoryError):
                csv_to_read = input('Your file may have actually been a folder or your file '
                                    'is currently open. Please try again: ')
                continue
    
    elif (data_frame_exist.lower() == 'excel'):
        excel_to_read = input('Enter the path of the file you would like to read: ').strip()

        readable = False
        while (not readable):
            try:
                excel_to_read = (functions.parent_path/excel_to_read).resolve()

                if not excel_to_read.is_relative_to(functions.parent_path):
                    excel_to_read = input('Your file path was inaccessible. Please choose a '
                                          'different file: ').strip()
                    continue

                if (excel_to_read.suffix != '.xlsx'):
                    excel_to_read = input('Only .xlsx Excel files are accepted. Please choose a '
                                          'different file: ')
                    continue

                excel_file = pd.ExcelFile(excel_to_read)
                sheets = excel_file.sheet_names
                num_sheets = len(sheets)
                
                if num_sheets > 20:
                    excel_to_read = input('Your file contains too many sheets (max 20). Please choose a '
                                          'different file: ')
                    continue
                    
                elif num_sheets == 1:
                    selected_sheet = sheets[0]
                    
                else:
                    sheet_choice = input('Your file contains multiple sheets. Please type the name of '
                                         'the sheet you would like: ').strip()
                    
                    if sheet_choice in sheets:
                        selected_sheet = sheet_choice
                    else:
                        excel_to_read = input('That sheet does not exist. Please re-enter your file '
                                              'path and try again, or choose a new file: ')
                        continue
                
                monthly_income = excel_file.parse(sheet_name=selected_sheet, nrows=13, usecols=['month', 'income'])

                if (len(monthly_income) > 12):
                    excel_to_read = input('Your sheet contained too many values. Please change your '
                                          'file or choose a new file: ').strip()
                    continue

                monthly_income['month'] = monthly_income['month'].str.strip().str[0:3]

                if (not monthly_income['month'].isin(functions.months).all()):
                    excel_to_read = input('Your file contains an invalid month. Please change your '
                                          'file or choose a new file: ').strip()
                    continue

                if monthly_income.empty:
                    print('Since you had no input, all values will default to 0.')
                    monthly_income = [0 for _ in range(12)]
                    readable = True
                    break

                if monthly_income['month'].duplicated().any():
                    excel_to_read = input('Your file contained duplicated months. Please change your '
                                          'file or choose a new file: ').strip()
                    continue

                monthly_income['income'] = pd.to_numeric(monthly_income['income'], errors = 'raise').fillna(0)

                if ((monthly_income['income'] > functions.maximum_value_allowed).any() or (monthly_income['income'] < 0).any()):
                    excel_to_read = input('Your file contained values outside the allowed range (-1M to 1M). '
                                          'Please choose a different file: ').strip()
                    continue

                monthly_income = monthly_income.set_index('month')
                last_month = monthly_income.index[-1]
                index = functions.months.index(last_month)
                existing_months = functions.months[:index + 1]
                monthly_income = monthly_income.reindex(existing_months, fill_value=0)
                readable = True
                break

            except (ValueError, KeyError, TypeError, AttributeError, Exception):
                excel_to_read = input('Your file could not be properly read. Please check your '
                                      'file or choose a different file: ')
                continue
            
            except FileNotFoundError:
                excel_to_read = input('Your file could not be found. Please check your file name: ')
                
            except (PermissionError, IsADirectoryError):
                excel_to_read = input('Your file may have actually been a folder or your file'
                                      ' is currently open. Please try again: ')
                continue

    elif (data_frame_exist == 'json'):
        json_to_read = input('Enter the path of the file you would like to read: ').strip()

        readable = False
        while (not readable):
            try:
                json_to_read = (functions.parent_path/json_to_read).resolve()

                if not json_to_read.is_relative_to(functions.parent_path):
                    json_to_read = input('Your file path was inaccessible. Please choose a '
                                         'different file: ').strip()
                    continue

                json_size = os.path.getsize(json_to_read)
                if (json_size > 50000):
                    json_to_read = input('Your file is too large (max 50 KB). Please choose a '
                                         'different file: ')
                    continue

                with open(json_to_read, 'r', encoding='utf-8') as f:
                    json_object = json.load(f)
                
                if (type(json_object) is list):
                    orientation = 'records'
                elif (type(json_object) is dict):
                    orientation = 'index'
                else:
                    json_to_read = input('Your file could not be properly read into a DataFrame. '
                                         'Please check your file or choose a different file: ')
                
                monthly_income = pd.read_json(json_to_read, orient=orientation, encoding='utf-8')[['month', 'income']]

                if (len(monthly_income) > 12):
                    json_to_read = input('Your sheet contained too many values. Please change your '
                                         'file or choose a new file: ').strip()
                    continue

                monthly_income['month'] = monthly_income['month'].str.strip().str[0:3]

                if (not monthly_income['month'].isin(functions.months).all()):
                    json_to_read = input('Your file contains an invalid month. Please change your '
                                         'file or choose a new file: ').strip()
                    continue

                if monthly_income.empty:
                    print('Since you had no input, all values will default to 0.')
                    monthly_income = [0 for _ in range(12)]
                    readable = True
                    break

                if monthly_income['month'].duplicated().any():
                    json_to_read = input('Your file contained duplicated months. Please change your '
                                         'file or choose a new file: ').strip()
                    continue

                monthly_income['income'] = pd.to_numeric(monthly_income['income'], errors = 'raise').fillna(0)

                if ((monthly_income['income'] > functions.maximum_value_allowed).any() or (monthly_income['income'] < 0).any()):
                    excel_to_read = input('Your file contained values outside the allowed range (-1M to 1M). '
                                          'Please choose a different file: ').strip()
                    continue

                monthly_income = monthly_income.set_index('month')
                last_month = monthly_income.index[-1]
                index = functions.months.index(last_month)
                existing_months = functions.months[:index + 1]
                monthly_income = monthly_income.reindex(existing_months, fill_value=0)
                readable = True
                break

            except UnicodeDecodeError:
                csv_to_read = input('Your file is in an unreadable format. Please save it in '
                                    'standard UTF-8 or choose a different file: ')
                continue
            
            except (ValueError, KeyError, TypeError, AttributeError, Exception):
                json_to_read = input('Your file could not be properly read. Please check your '
                                     'file or choose a different file: ')
                continue
                    
            except FileNotFoundError:
                json_to_read = input('Your file could not be found. Please check your file name: ')
                        
            except (PermissionError, IsADirectoryError):
                json_to_read = input('Your file may have actually been a folder or your file'
                                     ' is currently open. Please try again: ')
                continue

    else:
        monthly_income = input('Enter your income for every month to date: ').split()
        # This checks that every input can be converted into a float, and that
        # there are not more than 12 inputs. Values also cannot be outside
        # the allowed range.
        income_condition = True
        while income_condition:
            if (len(monthly_income) > 12):
                monthly_income = input('You have input too many values. Please try again: ').split()
                continue
            try:
                monthly_income = [float(val) for val in monthly_income]
            except ValueError:
                monthly_income = input('One input could not be read. Please try again: ').split()
                continue

            if (max(monthly_income) > functions.maximum_value_allowed or min(monthly_income) < 0):
                monthly_income = input('Your inputs contained values outside the allowed range (-1M to 1M).'
                                       ' Please input acceptable values: ').split()
                continue

            income_condition = False
    
    income = Income(monthly_income)




initial_balance = input('Enter how much money you had at the beginning of the year. '
                        'Do not include the $ character. ')
# This checks that the input can be converted into float and is within
# acceptable range.
acceptable_balance = True
while acceptable_balance:
    try:
        initial_balance = float(initial_balance)
    except ValueError:
        initial_balance = input('Your input could not be read. Please try again, and '
                                'do not include the $ character. ')
        continue

    if (initial_balance > functions.maximum_value_allowed or initial_balance
        < functions.minimum_value_allowed):
        initial_balance = input('Your input was outside the allowed range (-1M to 1M).'
                                ' Please choose an acceptable value: ')
        continue

    acceptable_balance = False


savings_goal = input('Enter how much you would like to save every year. Enter ' 
                     '$ amount (include $ character) or % of income (include % '
                     'character): ')
# This checks if a percentage or a dollar amount is to be saved, then
# converted to float appropriately. No other inputs are allowed.
savings_goal_value = None
savings_goal_percent = None
while (savings_goal_value == None and savings_goal_percent == None):
    if (savings_goal[0] == '$'):
        try:
            savings_goal = float(savings_goal[1:])
        except ValueError:
            savings_goal = input('Your value could not be read. Please enter again: ')
            continue
        
        if (savings_goal > functions.maximum_value_allowed or savings_goal < 0):
            savings_goal = input('Your value was outside the allowed range (0 to 1M).'
                                 ' Please choose an acceptable value: ')
            continue

        savings_goal_value = savings_goal
    elif (savings_goal[-1] == '%'):
        try:
            savings_goal = float(savings_goal[:-1])
        except ValueError:
            savings_goal = input('Your value could not be read. Please enter again: ')
            continue

        if (savings_goal > 100 or savings_goal < 0):
            savings_goal = input('Your value was outside the allowed range (0% to 100%).'
                                 ' Please choose an acceptable percentage: ')
            continue

        savings_goal_percent = savings_goal
    else:
        savings_goal = input('Your input could not be read. Please enter as $x or x%: ')
        continue
    



# Each expense may be entered as a csv/tsv or JSON file or direct input.
file_read = input('If you would like to read a file for housing expenses, '
                  'type y for yes, or n for no to type your own input: ')
while (file_read.lower() != 'y' and file_read.lower() != 'n'):
    file_read = input('Your input could not be accepted. Please type y or n: ')

if (file_read.lower() == 'y'):
    file_type = input('Enter what type of file you would like to input, csv '
                      'for csv/tsv, excel for excel, or json for JSON: ')
    while (file_type.lower() != 'csv' and file_type.lower() != 'excel'
           and file_type.lower() != 'json'):
        file_type = input('Your input could not be accepted. Please type csv, excel, or json: ')
    
    house = functions.choice('housing', file_type.lower())

else:
    house = functions.choice('housing')

housing = Expense(house, 'housing')


file_read = input('If you would like to read a file for food expenses, '
                  'type y for yes, or n for no to type your own input: ')
while (file_read.lower() != 'y' and file_read.lower() != 'n'):
    file_read = input('Your input could not be accepted. Please type y or n: ')

if (file_read.lower() == 'y'):
    file_type = input('Enter what type of file you would like to input, csv '
                      'for csv/tsv, excel for excel, or json for JSON: ')
    while (file_type.lower() != 'csv' and file_type.lower() != 'excel'
           and file_type.lower() != 'json'):
        file_type = input('Your input could not be accepted. Please type csv, excel, or json: ')
    
    foods = functions.choice('food', file_type.lower())

else:
    foods = functions.choice('food')

food = Expense(foods, 'food')


file_read = input('If you would like to read a file for transportation expenses, '
                  'type y for yes, or n for no to type your own input: ')
while (file_read.lower() != 'y' and file_read.lower() != 'n'):
    file_read = input('Your input could not be accepted. Please type y or n: ')

if (file_read.lower() == 'y'):
    file_type = input('Enter what type of file you would like to input, csv '
                      'for csv/tsv, excel for excel, or json for JSON: ')
    while (file_type.lower() != 'csv' and file_type.lower() != 'excel'
           and file_type.lower() != 'json'):
        file_type = input('Your input could not be accepted. Please type csv, excel, or json: ')
    
    transport = functions.choice('transportation', file_type.lower())

else:
    transport = functions.choice('transportation')

transportation = Expense(transport, 'transportation')


file_read = input('If you would like to read a file for entertainment expenses, '
                  'type y for yes, or n for no to type your own input: ')
while (file_read.lower() != 'y' and file_read.lower() != 'n'):
    file_read = input('Your input could not be accepted. Please type y or n: ')

if (file_read.lower() == 'y'):
    file_type = input('Enter what type of file you would like to input, csv '
                      'for csv/tsv, excel for excel, or json for JSON: ')
    while (file_type.lower() != 'csv' and file_type.lower() != 'excel'
           and file_type.lower() != 'json'):
        file_type = input('Your input could not be accepted. Please type csv, excel, or json: ')
    
    entertain = functions.choice('entertainment', file_type.lower())

else:
    entertain = functions.choice('entertainment')

entertainment = Expense(entertain, 'entertainment')


file_read = input('If you would like to read a file for all other expenses, '
                  'type y for yes, or n for no to type your own input: ')
while (file_read.lower() != 'y' and file_read.lower() != 'n'):
    file_read = input('Your input could not be accepted. Please type y or n: ')

if (file_read.lower() == 'y'):
    file_type = input('Enter what type of file you would like to input, csv '
                      'for csv/tsv, excel for excel, or json for JSON: ')
    while (file_type.lower() != 'csv' and file_type.lower() != 'excel'
           and file_type.lower() != 'json'):
        file_type = input('Your input could not be accepted. Please type csv, excel, or json: ')
    
    others = functions.choice('other', file_type.lower())

else:
    others = functions.choice('other')

other = Expense(others, 'other')

# This sums up all the expenses into a total, but only up to the last month
# of the shortest list.The shortest expense list is used in case that particular
# expense in later months was unknown while other expenses were known.
total_list = [h + f + t + e + o for h, f, t, e, o in zip(housing.dict.values(),
                                                         food.dict.values(), transportation.dict.values(), entertainment.dict.values(),
                                                         other.dict.values())]
total = Expense(total_list, 'total')

# The length of that shortest list is used for determining where the list of
# average expenses will start.
dict_list = [housing.dict, food.dict, transportation.dict, entertainment.dict, other.dict]
min_len = min(len(dictionary) for dictionary in dict_list)


# This sets up the average expenses in later months when it is not known or
# recorded. The offset range is created for plotting purposes.
expenses_average = (housing.average() + food.average() + transportation.average()
                     + entertainment.average() + other.average())
expenses_list = [expenses_average for _ in range(12)]
expenses_average_dict = functions.to_month_dict(expenses_list)
expenses_average_dict = {month: expenses_average_dict[month] for month 
                         in list(expenses_average_dict.keys())[min_len:]}
expense_month_offset = range(min_len, 12)

# The loop is used to remove the average value in months where an expense is known.
# The shortest expense list will not be looped through because its months do not
# appear. However, known expenses may appear, so are added to the corresponding months.
for month in expenses_average_dict:
    for dict in dict_list:
        if (month in dict.keys()):
            expenses_average_dict[month] = (expenses_average_dict[month] - np.average(list(dict.values()))
                                            + dict[month])

# This creates the graph of expenses.
expenses_total = functions.total(housing.dict, food.dict, transportation.dict,
                                 entertainment.dict, other.dict)
plt.plot(expenses_total.values(), label = 'Total expenses')
plt.plot(housing.dict.values(), label = 'Housing expenses')
plt.plot(food.dict.values(), label = 'Food expenses')
plt.plot(transportation.dict.values(), label = 'Transportation expenses')
plt.plot(entertainment.dict.values(), label = 'Entertainment expenses')
plt.plot(other.dict.values(), label = 'Other expenses')
plt.ylabel('Amount of money')
plt.xlabel('Months')
plt.xticks(ticks=range(12), labels=functions.months)
plt.title('Expenses')
plt.legend()
plt.savefig('Graph of Expenses.png')
plt.close()


# This checks if we are using the annual or monthly income version to determine how
# much money a person makes or loses in a month.
month_income = None
if (type(income) == float):
    month_income_list = [income for _ in range(12)]
    month_income = functions.to_month_dict(month_income_list)
    difference = functions.total(month_income, total.dict)
    difference = {month: difference[month] for month in list(difference.keys())[:len(total.dict)]}
else:
    if (len(income.dict) > len(total.dict)):
        difference = functions.total(income.dict, total.dict)
        difference = {month: difference[month] for month in list(difference.keys())[:len(total.dict)]}
    elif (len(income.dict) < len(total.dict)):
        difference = functions.total(income.dict, total.dict)
        difference = {month: difference[month] for month in list(difference.keys())[:len(income.dict)]}
    else:
        difference = functions.total(income.dict, total.dict)
    
# This sets up the average income in later months when it is not known how much the
# income will be.
    average_income_list = [income.average() for _ in range(12)]
    average_income = functions.to_month_dict(average_income_list)
    average_income = {month: average_income[month] for month
                      in list(average_income.keys())[len(income.dict):]}


# This creates the balance, then changed according to the difference of expenses from
# income. If total is empty, then difference is empty, so the balance is just the
# inital balance plus income in January.
if difference:
    balance_list = [difference['Jan'] + initial_balance]
else:
    if month_income:
        balance_list = [initial_balance + month_income['Jan']]
    else:
        balance_list = [initial_balance + income.dict['Jan']]
difference_list = list(difference.values())
for i in range(1, len(difference)):
    balance_list.append(difference_list[i] + balance_list[i - 1])
balance = Income(balance_list)

# This sets up the expected balance in later months when it is not known, due to
# either unknown income or unknown expenses.
last_month = list(balance.dict)[-1]
last_balance = balance.dict[last_month]
start = functions.months.index(last_month) + 1
if (last_month != 'Dec'):
    last_month = functions.months[start]
else:
    last_month = None


# The first case is the annual income, so the expected balance is determined by
# the expected expenses in later months. The list of expected expenses must be
# shorter that that of income, because income here is all 12 months. Expected
# expenses cannot be all 12 months because every expense must have a value in
# January. If a user provides no input, then that expense list will default
# to all 0s, so will not be the shortest list.
if (month_income):
    plt.plot(month_income.values(), label = 'Income')
    if last_month:
        expected_balance = {last_month: last_balance + month_income[last_month]
                            - expenses_average_dict[last_month]}
        for month in list(expenses_average_dict)[1:]:
            expected_balance[month] = (expected_balance[last_month]
                                       + month_income[month] - expenses_average_dict[month])
            last_month = list(expected_balance)[-1]
        plt.plot(expense_month_offset, expected_balance.values(), label = 'Expected Balance')
# The second case is the monthly income, so there are three scenarios. If
# monthly income does not cover all 12 months, then it is possible for the
# list of total expenses to be longer than the list of income. Therefore,
# the expected balance starts the month after the shorter one of these two lists.
else:
    plt.plot(income.dict.values(), label = 'Income')
# The first case runs if monthly income is not known for the entire year.
    if average_income:
        income_month_offset = range(len(income.dict), len(income.dict) + len(average_income))
        plt.plot(income_month_offset, average_income.values(), label = 'Average Expected Income')
# Each case runs in the scenario that either monthly expenses isn't known
# for the entire year, and could either be known less than monthly income
# is or more than monthly income is.
        if last_month:
            if (min_len <= len(income.dict)):
                expected_balance = {last_month: last_balance + income.dict[last_month]
                                    - expenses_average_dict[last_month]}
                shared_months = [month for month in list(expenses_average_dict)[1:]
                                 if month in income.dict]
                unshared_months = [month for month in list(expenses_average_dict)[1:]
                                   if month in average_income]
                for month in shared_months:
                    expected_balance[month] = (expected_balance[last_month]
                                               + income.dict[month] - expenses_average_dict[month])
                    last_month = list(expected_balance)[-1]
                for month in unshared_months:
                    expected_balance[month] = (expected_balance[last_month]
                                               + average_income[month] - expenses_average_dict[month])
                    last_month = list(expected_balance)[-1]
                plt.plot(expense_month_offset, expected_balance.values(), label = 'Expected Balance')
            else:
                expected_balance = {last_month: last_balance + average_income[last_month]
                                    - total.dict[last_month]}
                shared_months = [month for month in total.dict if month in list(average_income)[1:]]
                unshared_months = [month for month in expenses_average_dict if month
                                   in list(average_income)[1:]]
                for month in shared_months:
                    expected_balance[month] = (expected_balance[last_month]
                                               + average_income[month] - total.dict[month])
                    last_month = list(expected_balance)[-1]
                for month in unshared_months:
                    expected_balance[month] = (expected_balance[last_month]
                                               + average_income[month] - expenses_average_dict[month])
                    last_month = list(expected_balance)[-1]
                plt.plot(income_month_offset, expected_balance.values(), label = 'Expected Balance')
# This case runs if monthly income is provided for every month, so the
# expected balance is determined by the expected expenses.
    else:
        if last_month:
            expected_balance = {month: balance_list[-1] + income[month]
                                - expenses_average_dict[month] for month in expenses_average_dict}
            plt.plot(expense_month_offset, expected_balance.values(), label = 'Expected Balance')



# This plots the total expenses known.
plt.plot(total.dict.values(), label = 'Current Expenses')
# This plot only happens if not all expenses are known.
if expenses_average_dict:
    plt.plot(expense_month_offset, expenses_average_dict.values(), label = ('Average Expected '
                                                                            'Total Expenses'))
# This plots the balance.
plt.plot(balance.dict.values(), label = 'Balance')
plt.ylabel('Amount of money')
plt.xlabel('Months')
plt.xticks(ticks=range(12), labels=functions.months)
plt.title('Income vs. Expenses')


# This checks how much money is available at the end of the year with
# average income and expenses.
expenses_annual_average = expenses_average * 12
if (type(income) == float):
    available = balance.dict['Jan'] + income * 12 - expenses_annual_average
else:
    available = (balance.dict['Jan'] + (sum(income.dict.values()) / len(income.dict))
                 * 12 - expenses_annual_average)

# This checks whether there will be any money at the end of the year. If
# not, then no savings are possible.
if (available < 0):
    available = 0
    print('You are unable to save any money due to your average expenses exceeding your '
          'average income.')
    plt.plot([], [], label = 'No savings possible')
else:
# In this scenario, there is still money at the end of the year, but it
# still needs to be checked whether the desired savings goal is
# reasonable. If not, a new goal is provided. Savings are then plotted
# over each month.
    if (savings_goal_value):
        if (available < savings_goal_value):
            print('Based on your current average expenses and income, you cannot save '
                  f'{savings_goal} per year. We will recommend a new savings goal.')
            savings_goal_value = (available // 10) * 10
            print(f'You should save ${savings_goal_value:.2f} annually.')
        else:
            print(f'Your goal of saving {savings_goal} per year is possible.')
        plt.plot([savings_goal_value / 12 for _ in range(12)], label = 'Savings per month')
    else:
        if (type(income) == float):
            if (available < income * 12 * savings_goal_percent / 100):
                print('Based on your current average expenses and income, you cannot save '
                      f'{savings_goal} of your income per year. We will recommend a new '
                      'savings goal.')
                savings_goal_percent = (available / (income * 12)) * 100
                print(f'You should save {savings_goal_percent:.2f}% of your income annually.')
            else:
                print(f'Your goal of saving {savings_goal} of your income per year is possible.')
        else:
            total_income = (sum(income.dict.values()) / len(income.dict)) * 12
            if (available < total_income * savings_goal_percent / 100):
                print('Based on your current average expenses and income, you cannot save '
                      f'{savings_goal} of your income per year. We will recommend a new savings '
                      'goal.')
                savings_goal_percent = (available / total_income) * 100
                print(f'You should save {savings_goal_percent:.2f}% of your income annually.')
            else:
                print(f'Your goal of saving {savings_goal} of your income per year is possible.')
        percentage = [value * savings_goal_percent / 100 for value in balance.dict.values()]
        plt.plot(percentage, label = 'Savings per month')

# Lastly, we save the graph and close it.
plt.legend()
plt.savefig('Balance and Savings.png')
plt.close()


# Here, we print out the months with the maximum expenses. If a monthly
# income was provided, the month with the maximum income is printed.
if (month_income == None):
    income.maximum()

housing.maximum()
food.maximum()
transportation.maximum()
entertainment.maximum()
other.maximum()
total.maximum()