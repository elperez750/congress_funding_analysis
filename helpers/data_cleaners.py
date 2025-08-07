import re
import datetime

# Function to parse strings such as '$1,100,900'
def parse_currency_string(value):
    if value[0] == "-":
        return -1 * int(value[1:].strip('$').replace(',', ''))

    return int(value.strip('$').replace(',', ''))


# This function will be similar but will parse string such as '$11.7M' or '$11.7B'
def parse_abbreviated_number(string_amount):
    scale_factors = {'M': 1_000_000, 'K': 1_000, 'B': 1_000_000_000}
    cleaned_string = string_amount.strip().strip('$')
    try:

        scale = cleaned_string[-1].upper()
        numerical_part = cleaned_string[:-1]
        factor = scale_factors[scale]
        return int(float(numerical_part) * factor)

    except (KeyError, ValueError, IndexError) as e:
        print(f"Error: {e}")
        return None


# Function will convert text into valid key
# For example, 'PAC Contributions' will be equal to pac_contributions
def clean_key(raw_string):
    s = raw_string.lower()
    s = re.sub(r'[^a-z0-9\s]', '', s)
    s = re.sub(r'\s+', '_', s)
    s = s.strip('_')
    return s


print(clean_key(' Contributions*'))


# We will convert the string '12' or '02' to be 12 and 2 respectively first
# We will then pass it into the function
def convert_two_digit_year(year):
    int_year = int(year)
    current_year_two_digit = datetime.datetime.now().year % 100
    if int_year <= current_year_two_digit:
        return 2000 + int_year
    else:
        return 1900 + int_year



