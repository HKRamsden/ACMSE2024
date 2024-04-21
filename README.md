# ACMSE 2024 - Tame Neam 2nd Place Overall
## Kennesaw State University Spring 2024 -- Programming Competiton
The task for this project is to create a program that makes daily stock recommendations at the end of the day. 
The program shall be executed once per day, for 30 days total. 

This project is a desktop based application that utilizes neural networks using LSTM layers to predict stock prices when given a set of data. 
For one step, the project reads the day's data from a CSV file, writes orders for the next day, and terminates.

#### Placing Orders:
Orders are placed in the following format: 

`TYPE ID QUANTITY`

Type can be one of the following:
- BO: Buy at Open
- BC: Buy at Close
- SO: Sell at Open
- SC: Sell at Close


## Usage
1. The user shall run the command `python3 new.py` to train models
2. The user shall run the command `./daily-pick` to run the model

## Installs
For this program, the following libraries have been used:
- NumPy: `pip install numpy`
- Pandas: `pip install pandas`
- SkLearn: `pip install sklearn`
- TensorFlow: `pip intall tensorflow`
- CSV: `pip install csv`

