import os
import datetime

from pathlib import Path
from collections import Counter as cn

import csv
import pandas as pd
import json
# This list is used to order the months.
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct',
          'Nov', 'Dec']
# A parent path exists to ensure that the script cannot access unauthorized
# or inaccessible files for the csv cases.
parent_path = Path(__file__).resolve().parent

# There is a maximum and minimum values allowed for any numerical inputs to
# prevent overflow.
maximum_value_allowed = 1000000
minimum_value_allowed = maximum_value_allowed * -1

# This creates a dictionary with months as keys and floats as values. The
# dictionary will only be as long as the number of values provided.
def to_month_dict(values):
    monthly_dict = dict(zip(months, values))
    return monthly_dict

# This creates a new dictionary that sums up three or more dictionaries,
# but the difference for just two.
def total(dict1, dict2, dict3 = None, dict4 = None, dict5 = None):
    if dict3 == None:
        total_dict = cn(dict1)
        total_dict.subtract(cn(dict2))
    else:
        total_dict = cn(dict1) + cn(dict2) + cn(dict3) + cn(dict4) + cn(dict5)
    return total_dict

def choice(name, file_type = None):
    if (file_type == None):
        headers = ['date', 'amount', 'description']
        entries = 0
        file_name = name + '.csv'

        new_csv = (parent_path/file_name).resolve()
        with open(new_csv, mode='w', newline='', encoding='utf-8') as f:
            file = csv.DictWriter(f, fieldnames=headers)
            file.writeheader()

            while True:
                if (entries > 25):
                    print('Maximum number of inputs is 25. Your entries will now be saved '
                          'in a file called housing.csv in your parent directory.')
                    break

                date = input('Enter a date with a 4-digit year string or exit to exit: ').strip()
                if (date.lower() == 'exit'):
                    break

                try:
                    pd.to_datetime(date, format='mixed')
                
                except (ValueError, TypeError):
                    print('Your date format was not acceptable. Please enter as YYYYMMDD.')
                    continue

                while True:
                    amount = input('Enter an amount: ').strip()
                    
                    try:
                        if (float(amount) > maximum_value_allowed or float(amount) < 0):
                            print('Your value was outside the acceptable range (0 to 1M). Please '
                                  'try again.')
                            continue
                        break

                    except ValueError:
                        print('Your input was not a number. Please try again.')
                        continue
                
                while True:
                    description = input('Enter a description of the charge: ').strip()
                    
                    if (len(description) > 20):
                        print('Your description is too long (max 20 chars). Please try again.')
                        continue

                    break
                
                file.writerow({
                    'date': date,
                    'amount': amount,
                    'description': description
                })

                entries += 1
        
        print(f'Your new file is {name}.csv.')
        expense = choice(name, 'csv')
    else:
        if (file_type.lower() == 'csv'):
            csv_to_read = input('Enter the name of the file you would like to read: ')
            readable = False
            while (not readable):
                try:
                    csv_to_read = Path(parent_path/csv_to_read).resolve()
                    if not csv_to_read.is_relative_to(parent_path):
                        csv_to_read = input('Your file path was inaccessible. Please choose '
                                            'a different file: ').strip()
                        continue
                    with open(csv_to_read, 'r', encoding='utf-8-sig') as f:
                        lines = []
                        for _ in range(27):
                            line = f.readline()
                            if not line:
                                break
                            lines.append(line)

                    if (len(lines) > 26):
                        csv_to_read = input('Your file contained too many values. Please '
                                            'change your file or choose a new file: ').strip()
                        continue
                    
                    expense = pd.read_csv(csv_to_read, sep=r'[,\t]', engine='python',
                                          usecols=['date', 'amount', 'description'], encoding='utf-8-sig')
                    
                    if expense.empty:
                        print('Since you had no input, all values will default to 0.')
                        expense = [0 for _ in range(12)]
                        readable = True
                        break

                    dates = expense['date'].dropna().astype(str).str.strip()
                    year_exists = dates.str.contains(r'\d{4}')
                    if not year_exists.all():
                        csv_to_read = input('Your file contains dates missing a four-digit year. '
                                            'Please change your file or choose a new file: ').strip()
                        continue
                        
                    # Convert date column into a short 3-letter month name string
                    expense['month'] = pd.to_datetime(expense['date'], format='mixed',
                                                      errors='raise').dt.strftime('%b')
                    if (not expense['month'].isin(months).all()):
                        csv_to_read = input('Your file contains an invalid date string. Please change your file: ')
                        continue
                        
                    # Numeric conversion and range
                    expense['amount'] = pd.to_numeric(expense['amount'], errors='raise').fillna(0)
                    if ((expense['amount'] > maximum_value_allowed).any() or (expense['amount'] < 0).any()):
                        csv_to_read = input('Your file contained values outside the allowed range (0 to 1M). Please '
                                            'choose a different file: ')
                        continue
                        
                    # Group by month
                    expense = expense.groupby('month', as_index=False)[['amount']].sum()
                    expense = expense.set_index('month')
                    
                    # Clean up timeline indexing so each intermediate month has value of 0
                    last_month = expense.index[-1]
                    index = months.index(last_month)
                    existing_months = months[:index + 1]
                    expense = expense.reindex(existing_months, fill_value=0)
                    
                    readable = True
                    break
                except UnicodeDecodeError:
                    csv_to_read = input('Your file is in an unreadable format. Please save it in '
                                        'standard UTF-8 or choose a different file: ')
                    continue
                except (ValueError, KeyError, TypeError, AttributeError, pd.errors.EmptyDataError,
                        pd.errors.ParserError) as e:
                    csv_to_read = input(f'Your file could not be properly read. Please check your '
                                        'file or choose a different file: {e}')
                    continue
                except FileNotFoundError:
                    csv_to_read = input('Your file could not be found. Please check your file name: ')
                    continue
                except (PermissionError, IsADirectoryError):
                    csv_to_read = input('Your file may have actually been a folder or your file is '
                                        'currently open. Please try again: ')
                    continue

        # ==========================================
        # EXCEL SELECTION
        # ==========================================
        elif (file_type.lower() == 'excel'):
            excel_to_read = input('Enter the path of the file you would like to read: ').strip()
            readable = False
            while (not readable):
                try:
                    excel_to_read = (parent_path/excel_to_read).resolve()
                    if not excel_to_read.is_relative_to(parent_path):
                        excel_to_read = input('Your file path was inaccessible. Please choose a '
                                              'different file: ').strip()
                        continue
                    if (excel_to_read.suffix != '.xlsx'):
                        excel_to_read = input('Only .xlsx Excel files are accepted. Please choose '
                                              'a different file: ')
                        continue

                    excel_file = pd.ExcelFile(excel_to_read)
                    sheets = excel_file.sheet_names
                    num_sheets = len(sheets)
                    if num_sheets > 20:
                        excel_to_read = input('Your file contains too many sheets (max 20). Please '
                                              'choose a different file: ')
                        continue
                    elif num_sheets == 1:
                        selected_sheet = sheets[0]
                    else:
                        sheet_choice = input('Your file contains multiple sheets. Please type the '
                                             'name of the sheet you would like: ').strip()
                        if sheet_choice in sheets:
                            selected_sheet = sheet_choice
                        else:
                            excel_to_read = input('That sheet does not exist. Please re-enter your file '
                                                  'path and try again, or choose a new file: ')
                            continue
                            
                    expense = excel_file.parse(sheet_name=selected_sheet, nrows=26,
                                               usecols=['date', 'amount', 'description'])
                    if (len(expense) > 25):
                        excel_to_read = input('Your sheet contained too many values. Please change '
                                              'your file or choose a new file: ').strip()
                        continue
                        
                    if expense.empty:
                        print('Since you had no input, all values will default to 0.')
                        expense = [0 for _ in range(12)]
                        readable = True
                        break

                    dates = expense['date'].dropna().astype(str).str.strip()
                    year_exists = dates.str.contains(r'\d{4}')
                    if not year_exists.all():
                        excel_to_read = input('Your file contains dates missing a four-digit year. '
                                              'Please change your file or choose a new file: ').strip()
                        continue
                        
                    expense['month'] = pd.to_datetime(expense['date'], format='mixed',
                                                      errors='raise').dt.strftime('%b')
                    if (not expense['month'].isin(months).all()):
                        excel_to_read = input('Your file contains an invalid date string. Please '
                                              'change your file: ').strip()
                        continue
                        
                    expense['amount'] = pd.to_numeric(df['amount'], errors='raise').fillna(0)
                    if ((expense['amount'] > maximum_value_allowed).any() or (df['amount'] < 0).any()):
                        excel_to_read = input('Your file contained values outside the allowed range '
                                              '(0 to 1M). Please choose a different file: ').strip()
                        continue
                        
                    expense = expense.groupby('month', as_index=False)[['amount']].sum()
                    
                    last_month = expense.index[-1]
                    index = months.index(last_month)
                    existing_months = months[:index + 1]
                    expense = expense.reindex(existing_months, fill_value=0)
                    
                    readable = True
                    break
                except (ValueError, KeyError, TypeError, AttributeError, Exception):
                    excel_to_read = input('Your file could not be properly read. Please check '
                                          'your file or choose a different file: ')
                    continue
                except FileNotFoundError:
                    excel_to_read = input('Your file could not be found. Please check your '
                                          'file name: ')
                except (PermissionError, IsADirectoryError):
                    excel_to_read = input('Your file may have actually been a folder or your '
                                          'file is currently open. Please try again: ')
                    continue

        # ==========================================
        # JSON SELECTION
        # ==========================================
        else:
            json_to_read = input('Enter the path of the file you would like to read: ').strip()
            readable = False
            while (not readable):
                try:
                    json_to_read = (parent_path/json_to_read).resolve()
                    if not json_to_read.is_relative_to(parent_path):
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
                        continue
                        
                    df = pd.read_json(json_to_read, orient=orientation, encoding='utf-8')[['date', 'amount', 'description']]
                    if (len(df) > 25):
                        json_to_read = input('Your file contained too many values. Please change your '
                                             'file or choose a new file: ').strip()
                        continue
                        
                    if df.empty:
                        print('Since you had no input, all values will default to 0.')
                        expense = [0 for _ in range(12)]
                        readable = True

                    dates = expense['date'].dropna().astype(str).str.strip()
                    year_exists = dates.str.contains(r'\d{4}')
                    if not year_exists.all():
                        excel_to_read = input('Your file contains dates missing a four-digit year. '
                                              'Please change your file or choose a new file: ').strip()
                        continue
                        
                    expense['month'] = pd.to_datetime(expense['date'], format='mixed',
                                                      errors='raise').dt.strftime('%b')
                    if (not expense['month'].isin(months).all()):
                        excel_to_read = input('Your file contains an invalid date string. Please '
                                              'change your file: ').strip()
                        continue
                        
                    expense['amount'] = pd.to_numeric(df['amount'], errors='raise').fillna(0)
                    if ((expense['amount'] > maximum_value_allowed).any() or (df['amount'] < 0).any()):
                        excel_to_read = input('Your file contained values outside the allowed range '
                                              '(0 to 1M). Please choose a different file: ').strip()
                        continue
                        
                    expense = expense.groupby('month', as_index=False)[['amount']].sum()
                    
                    last_month = expense.index[-1]
                    index = months.index(last_month)
                    existing_months = months[:index + 1]
                    expense = expense.reindex(existing_months, fill_value=0)
                    
                    readable = True
                    break
                except (ValueError, KeyError, TypeError, AttributeError, Exception):
                    excel_to_read = input('Your file could not be properly read. Please check '
                                          'your file or choose a different file: ')
                    continue
                except FileNotFoundError:
                    excel_to_read = input('Your file could not be found. Please check your '
                                          'file name: ')
                except (PermissionError, IsADirectoryError):
                    excel_to_read = input('Your file may have actually been a folder or your '
                                          'file is currently open. Please try again: ')
                    continue
    
    return expense