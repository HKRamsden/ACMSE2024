import pandas as pd
import sys
import subprocess

# portfolio is cash and the stocks as a dictionary
# stocks[id] = shares
cash = 10000
stocks = {}


def share_price(data, day, open, id):
  """
  Return the price of the stock on a given day. If the stock is not in
  the data, return the next price.
  data - The data frame
  day - The day_number of the quote
  open - True if we want open price, False if we want close price
  id - id of stock to quote
  """
  # Filter data for the specified stock ID
  stock_data = data[data['id'] == id]

  # Further filter data for the specified day, if not found look for the next available day
  day_data = stock_data[stock_data['day_number'] >= day].sort_values(
      by='day_number')
  if not day_data.empty:
    day_row = day_data.iloc[0]  # First row of the filtered data
    if open:
      return day_row['open']
    else:
      return day_row['close']
  else:
    return None  # Or raise an error if preferred


def buy(data, day, open, shares, id):
  global cash
  global stocks

  price = share_price(data, day, open, id)
  if price is None:
    #abort if the stock is gone
    return

  #limit the number of shares to buy
  cost = price * shares
  if cost > cash:
    shares = int(cash / price)
    cost = price * shares
  print("buying {shares} shares of {id} at {price}".format(shares=shares,
                                                           id=id,
                                                           price=price))

  # make the transaction
  cash -= cost
  if id in stocks:
    stocks[id] += shares
  else:
    stocks[id] = shares


def sell(data, day, open, shares, id):
  global cash
  global stocks

  price = share_price(data, day, open, id)
  if price is None or id not in stocks:
    #abort if the stock is gone
    return

  #limit the number of shares to sell
  shares = min(shares, stocks[id])
  print("selling {shares} of {id} at {price}".format(shares=shares,
                                                     id=id,
                                                     price=price))

  #compute the total
  cost = price * shares

  # make the transaction
  cash += cost
  stocks[id] -= shares
  if stocks[id] == 0:
    del stocks[id]


def portfolio_value(data, day):
  """
  Return the total value of the portfolio at the close of the given day.
  """
  global cash
  global stocks

  #get the cash value
  total = cash

  #add the stock value at close
  for id in stocks:
    total += share_price(data, day, False, id) * stocks[id]

  return total


def portfolio_str(data, day):
  """
  Create a string representation of the portfolio in the following format:
  cash
  total_value
  num_stocks
  id qty 
  """
  global cash
  global stocks

  result = []
  result.append(str(cash))
  result.append(str(portfolio_value(data, day)))
  result.append(str(len(stocks)))
  for id in stocks:
    result.append("{id} {qty}".format(id=id, qty=stocks[id]))
  return '\n'.join(result)


def load_data(filename):
  """
  Load the date from the specified csv file. The data fields are
  expected to be:
  - id: unique id for the stock
  - day_of_week: day of week (1 = Monday, 7 = Sunday)
  - day_number: The number identifier of the day.
  - open: opening price of the stock
  - high: highest price of the stock
  - low: lowest price of the stock
  - close: closing price of the stock
  - volume: volume traded of the stock
  """
  # attempt to load the data frame from the filename
  try:
    df = pd.read_csv(filename)
  except Exception:
    # if the file cannot be loaded, print an error message and exit
    print("Error: Unable to load data from file {}".format(filename))
    sys.exit(1)

  # verify that the data frame has the expected columns
  if set(df.columns) != {
      "id", "day_of_week", "day_number", "open", "high", "low", "close",
      "volume"
  }:
    print("Error: Unexpected columns in data file {}".format(filename))
    sys.exit(1)

  # return the data frame
  return df


def parse_args(args):
  """
  Parses the command line arguments into a dictionary.
  If the user does not specify the correct arguments, it will
  print the usage message and exit the program.
  If the arguments are invalid, it will also print an error message.
  The required arguments are:
    1.) Input File
    2.) Command to test
    3.) Start day
    4.) End day
  On success, it will return a dictionary with the arguments.
  """
  # check for the appropriate number of arguments
  if len(args) != 5:
    print(
        "Usage: python3 simulate.py <input file> <command> <start day> <end day>"
    )
    sys.exit(1)

  result = {}

  # populate the result dictionary with arguments
  result['data'] = load_data(args[1])
  result['cmd'] = args[2]
  result['start'] = int(args[3])
  result['end'] = int(args[4])

  # verify that the start day is less than the end day
  if result['start'] > result['end']:
    print(
        f"Error: Start day {result['start']} is greater than end day {result['end']}"
    )
    exit(1)

  # verify that the start day is contained within the data
  if result['start'] < result['data']['day_number'].min() or \
     result['start'] > result['data']['day_number'].max():
    print(
        f"Error: Start day {result['start']} is not contained within the data")
    exit(1)

  # verify that the end day is contained within the data
  if result['end'] < result['data']['day_number'].min() or \
     result['end'] > result['data']['day_number'].max():
    print(f"Error: End day {result['end']} is not contained within the data")
    exit(1)

  return result


def execute_orders(data, day, orders):
  """
  Execute the orders on a given day. The orders are strings of the form:
    BO ID SHARES  - buy shares of ID at open
    BC ID SHARES  - buy shares of ID at close
    SO ID SHARES  - sell shares of ID at open
    SC ID SHARES  - sell shares of ID at close
  Each order is on a line by itself
  """
  # split the orders into individual commands
  orders = orders.split('\n')
  for order in orders:
    #skip blank orders
    if not order:
      continue
      
    # split the command into its constituent parts
    try:
      action, id, shares = order.split(' ')
      id = int(id)
      shares = int(shares)
      if action == 'BO':
        buy(data, day, True, shares, id)
      elif action == 'BC':
        buy(data, day, False, shares, id)
      elif action == 'SO':
        sell(data, day, True, shares, id)
      elif action == 'SC':
        sell(data, day, False, shares, id)
    except Exception as ex:
      print("ACK!", ex)
      continue


def simulate(data, cmd, day):
  """
  Simulates the stock market for the specified day.
  """
  # create a utf-8 string containing the day's stock data in csv format
  day_data = data[data['day_number'] == day].to_csv(index=False)

  # data to send
  day_dump = '\n'.join([str(day), portfolio_str(data, day), day_data])

  # run the command, opening channels for its stdin and stdout
  p = subprocess.Popen(cmd,
                       stdin=subprocess.PIPE,
                       stdout=subprocess.PIPE)
  # send the data to the command
  orders,errors = p.communicate(day_dump.encode('utf-8'))
  execute_orders(data, day + 1, orders.decode('utf-8'))

def day_header(data, day, log):
  print()
  print("Day {day}".format(day=day))
  print('==========================================')
  value = portfolio_value(data, day)
  print("Value: {value}".format(value=value))
  print("{day},{value}".format(day=day, value=value), file=log)
  
def main(args):
  params = parse_args(args)
  log=open('simulate-history.csv', 'w')
  print("day,value", file=log) 
  for day in range(params['start'], params['end']):
    day_header(params['data'], day, log)
    simulate(params['data'], params['cmd'], day)
  day_header(params['data'], params['end'], log)
  log.close()


if __name__ == "__main__":
  main(sys.argv)
