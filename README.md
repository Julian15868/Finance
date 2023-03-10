# Finance work
#### Intro:
With this work done in Python and Data Studio, the goal is to identify stocks with possible future growth, compare each stock with its competitors using different competitive metrics, and see the transactions of the company's own stocks made by people within the company to stay informed on how they anticipate their future value.

------------

#### **This work is divided into the following three programs:**

- **Competidores** : For each stock on a given list, we aim to find their competitors, filtered and sorted by their market capitalization. Once this search is complete, we look for information and ratios to compare them, including: Price/Earnings, Free Cashflow, PTFCF, Profitability Ratios, Activity Ratios, Liquidity Ratios, and Debt Ratios. Finally, a description of the company is provided.

- **Insiders** : For each stock, we want to know what people within the company are doing with their own stocks. With this information, along with their job titles, transaction dates, amounts, and other details, we compare it with the historical price of the stock over a certain number of days. The goal is to predict what will happen in the future with the stock. For example, if they start buying a significant amount of shares at once, it suggests they believe the value of their stock in the market will increase.

- **accionesBaratas**: We use this program to identify stocks that are cheap given a list of them, and we do so by sector, industry, and sub-industry, taking into account the order, on one hand, by Price-to-Book and on the other, by Price/Earnings.

------------
#### **As an example we show images of each one**
- **Competidores**: 
(Some sections of the report)

<img src="https://i.ibb.co/8bFgtQN/competidores-foto1.png" width="750" height="525">

<img src="https://i.ibb.co/ww3PsJP/competidores-foto2.png" width="750" height="525">

- **Insiders transactions**

<img src="https://i.ibb.co/p3ww77L/insider-foto1.png" width="750" height="525">




- **accionesBaratas**
<img src="https://i.ibb.co/xSSwH6h/accionesbaratas-foto1.png" width="750" height="525">

------------

#### **Here is a description of the functions of each program:**

 **Competidores** :
 
- **insertarAdelante(lista,elemento)** : It receives a list and an element, if it was already in the list, it deletes it to enter it at the beginning, and if it wasn't, it enters it at the beginning. It is important in the context of our competition program to always leave the Principalstock at the top of the list.

- **buscarPrimeraTandaCompetencia(accion)**: It searches for the first batch of competitors for the stock we enter. We use this to search for the first batch and not subsequent ones because it is more varied and accurate in the first search for the competition than the function "buscarCompetencia(accion,mercados)" but it is not very good at searching for subsequent batches because it has little variation.

- **buscarCompetencia(accion,mercados)**: It searches for subsequent batches of competitors for the stock, and we specify the markets that we want our function to search.

- **puntajesStocks(stocksTotales)**: Taking into account the sector and industry of the main stock, we add 1 ("one") to the competitor stock's score for each match.

- **strToNum(string)**: We receive information about the value of market cap (or others) as a string, such as 1T (one trillion) or 1B (one billion). We convert this to a number to compare each stock later.

- **separarMayus(palabra)**: It receives a string in the format "ReturnOnAssets" and converts it to "Return On Assets". We use this function to clarify column names in a dataframe.

- **marketCapFunc(stock,ultimosNanios)**: It receives a stock and a number of years, and returns a list of the market cap for the last n years.

**Insiders:**

-  **insiderTraders(stocksCargados,diasAtras)**: It receives one or more stocks and a number of days, and generates two CSV files. One file contains the historical prices of the stock to be analyzed within a range of n days, and the other contains information on insider traders, including their purchase and sale of shares with corresponding dates and job titles.

-  **masProbable(nombre1,lista)**: It receives a name and a list of names. Given this name, we return the name that is the closest match to the list. If the probability is low, it returns "No Match". We use this function because we need to triangulate information from two different pages. We triangulate this information using the name, specifically, we want to use the name to add information about the person's job title in the company.

------------

**Running the code**

Each of these programs can be run by uploading a .csv file with the same name and analogous structure, or by updating the same file to the current date and time, i.e.:
```ShellSession
python "program.py"
```

For competidores and insiders, there are two options. The first option is to upload a .csv file containing the information inside of it, in the format "NFLX, TSLA, CMRX". The second option is to provide the information directly in the command line:
```ShellSession
python "program.py" file.csv
```
```ShellSession
python "program.py" "NFLX, TSLA, CMRX"
```

For the accionesBaratas program, only a dataframe containing the following columns ("Symbol", "Sector", "Industry", "Same Sub-Industry As", "Market Capitalization", "Price/Book (MRQ)", "Price/Earnings (TTM)") can be passed. In other words, the dataframe should have the same structure as the original .csv file.

------------

### Python Requirements <a name = "pyinstalling"></a>

1. Now you need to create environment and install the required python packages:
    ```ShellSession
    pip install -r requirements.txt
    ```
------------

### Next steps after the execution of our programs

**After execution of "competidores.py"**:

&nbsp;&nbsp;We will get three .csv files:

- The first one, CompetidoresPtfc.csv, will be located in the dropdown menu below the text "stocks to analyze," and in the chart below the text "price to free cash flow (top4)," both of which are at the beginning of the report, at the top right.
- The second one, ocupaciones.csv, will be located in the rectangular chart above the "profitability ratios" section.
- The third one, competidores.csv, will be located in all other charts/menus (there are 16 other ones).

*Link to the report*: https://lookerstudio.google.com/reporting/d8c8ffaf-b0e0-419e-a9df-4143bd89cdf7


**After execution of "insiders.py"** :

&nbsp;&nbsp; We will get two .csv files: 

- The first one, preciosHist.csv, will be located in the top-left chart (within which is the text **historical prices**).
- The second one, insidersInfo.csv, will be located in all other charts/menus (there are 11 other ones).

*Link to the report:*: https://lookerstudio.google.com/reporting/c0b4bd5e-cdf0-4671-a5a1-a093f8b0d6a7

**After execution of accionesBaratas.py**:

&nbsp;&nbsp;We will get two .csv files: 

- The first one, priceToBook.csv, will be located in the first column of charts, below **ordered by price to book**.
- The second one, PriceEarnings.csv, will be located in the second column of charts, below **ordered by price/earnings**.

*Link to the report:*: https://lookerstudio.google.com/reporting/e25be8c8-f2f4-4241-9bd9-b2ff4a3f11de
