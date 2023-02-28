#Librerias
import requests,json,time,sys
import pandas as pd, numpy as np
import matplotlib.pyplot as plt
import difflib #probabilidad
import yfinance as yf
from datetime import date, datetime, timedelta
from IPython.display import clear_output #Para borrar la salida de codigo
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from IPython.display import clear_output

#Configuramos selenium
service = Service(executable_path="chromedriver.exe")
service.start()
options = webdriver.ChromeOptions()
options.add_argument("--disable-extensions")
options.add_argument("--disable-gpu")
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument('--disable-dev-shm-usage')
clear_output()
import finnhub
# Setup client
finnhub_client = finnhub.Client(api_key="cee6jviad3i92cealk5gcee6jviad3i92cealk60")

### Comienzo ###
#Cargamos el dataframe 
#Hemos cambiado para que se pueda poner tambien el numero de dias que se quiere
try:
  filename = sys.argv[1]
  if ".csv" in filename:
    lista = str(pd.read_csv(filename)).replace("[","").replace("]","").replace(" ","").split(":")[1].split("\n")[0].split(",")
    print(lista)
    print(".csv")
  elif ',' in filename:
    lista = filename.split(",")
    print(lista)
    print("Lista")
except:
  Dataframe = pd.concat([pd.read_csv("stocks1.csv"),pd.read_csv("stocks2.csv")])
  print("DataframeViejo")
  

try:
  filename1 = sys.argv[1]
except:
  print("no filename1")
try:
  filename2 = sys.argv[2]
except:
  print("no filename2")
try:
  if filename.isnumeric():
    diasAtras = int(filename)
  elif filename2.isnumeric():
    diasAtras = int(filename2)
except:
  diasAtras = 360

print("dias atras: "+str(diasAtras))

try:
  stocksTotales = list(Dataframe["Symbol"].head(200)) #Sacar el head 100 luego#Sacar el head 100 luego#Sacar el head 100 luego#Sacar el head 100 luego#Sacar el head 100 luego
except:
  stocksTotales = lista

#stocksTotales = stocksTotales[0:25]##
print("El largo del stocksTotales es: "+str(len(stocksTotales)))
print(stocksTotales,end=",")

##Hacemos la funcion para buscar los insider traders
#Para no sobrecargar finhub(Pagina donde sacamos los datos de insiders traders)...
#...Se debe hacer que cada 50 stocks frene unos 5-10 segundos.


def insiderTraders(stocksCargados,diasAtras):
  diasEmpiezo = 0
  hoy = date.today()-timedelta(diasEmpiezo,0,0) #se puede tomar otro dia como "hoy", no lo puse como parametro de la funcion porque no se si se usara
  ultimosNdias = date.today()-timedelta(diasAtras,0,0) 

  for ciclo in range(len(stocksCargados)):
    cantComprasTodos, montComprasTodos = [],[]
    cantVentasTodos, montVentasTodos = [],[]
    stock, stockPrincipal = stocksCargados[ciclo],stocksCargados[ciclo]
    accion = yf.Ticker(stock)
    clear_output() #Borramos el output
    print("Generando datos de "+str(stock)+" para la fecha:  "+str(ultimosNdias)+"-"+str(hoy))

    ####Sacamos informacion de insider transactions para el stock actual
    try:
      r = finnhub_client.stock_insider_transactions(stock, ultimosNdias, hoy)
      df = pd.DataFrame(r["data"])
    except:
      continue;

    # atributos derivados de los datos
    try:
        df['dollarAmount'] = df['change']*df['transactionPrice']
    except:
        df['dollarAmount'] = 0

    try:
        df['insiderPortfolioChange'] = df['change']/(df['share'] - df['change'])
        df.loc[df['share'] - df['change'] == 0, "insiderPortfolioChange"] = 1
    except:
        df['insiderPortfolioChange'] = 0

    try:
        conditions = [
            (df['change'] >= 0) & (df['transactionPrice'] > 0),
            (df['change'] <= 0) & (df['transactionPrice'] > 0),
            (df['transactionPrice'] == 0)
        ]
    except:
        conditions = []
    values = ['Buy', 'Sale', 'Gift']
    try:
        df['buyOrSale'] = np.select(conditions, values)
    except:
        df['buyOrSale'] = 0
    try:
        df['transactionDate'] = pd.to_datetime(df['transactionDate']).dt.date
    except:
        df['transactionDate'] = 0

    dfUltimosNdias = df.copy()
    #dfBuyOrSale = dfUltimosNdias[(dfUltimosNdias["buyOrSale"] == "Buy") | (dfUltimosNdias["buyOrSale"] == "Sale")]
    #dfBuyOrSale.to_csv("insidersInfo.csv",index=False,sep = ",")
    
    ## Queremos añadirle el cargo de la persona al dataframe de insider transactions
    # Para eso vamos a sacar algunos datos de sec.gov (el CIK de un stock particular), y triangular la informacion (En nuestro caso de nombre-nombre para obtener el cargo)
    import re
    try:
      link = "https://www.sec.gov/include/ticker.txt"
      driver = webdriver.Chrome(service=service, options=options)
      driver.get(link)
      page = BeautifulSoup(driver.page_source,"html.parser")
      for busqueda in page.findAll("pre",attrs={"style":"word-wrap: break-word; white-space: pre-wrap;"}):
        guardar = busqueda.text
      stockCIK  = str(guardar.replace("\t","\n")).split("\n")
      for u in range(len(stockCIK)):
        if str(stockCIK[u]).upper() == stock:
          cik = str(stockCIK[u+1])
      nombresAponer,cargosAponer = [],[]
      link = "https://www.secform4.com/insider-trading/"+cik+".htm" #Competidores
      driver.get(link)
      page = BeautifulSoup(driver.page_source,"html.parser")
      texto = []
      for parte in page.findAll("table",attrs={"class":"sort-table"}):
        texto.append(str(parte).split("InsiderRelationship"))
      try:
        texto = texto[0][0].split("sec form 4 insider trading")[1:] #PROBLEMA NO HAY NADA
      except:
        continue
    except: #Quizas esta parte se podria reducir
      texto = []
      cargo = []
    nombresAponer, cargosAponer = [],[]
    for i in range(len(texto)):
      texto[i] = str(str((texto[i].split(">")[1:])).split("/span")[0])
      nombre = (texto[i].split(",")[0]).replace("'","").replace("</a","").replace("[","")
      nombresAponer.append(nombre)
      try:
        cargo = texto[i].split(",")[3].replace("'","").replace("<","")[1:].replace("br/","")
      except:
        cargo = []
      cargosAponer.append(cargo)
    dataframe = pd.DataFrame({"Nombre":nombresAponer,"Cargo":cargosAponer}) #Tenemos los nombres con su cargo por un lado de la pagina sec.gov

    ## Aca vemos los nombres que sacamos de FINHUB, los cuales vamos a triangular con los de sec.gov
    try:
      compraronNombres = list(set(dfUltimosNdias[dfUltimosNdias["buyOrSale"]=="Buy"]["name"]))
    except:
      compraronNombres = []
    try:
      vendieronNombres = list(set(dfUltimosNdias[dfUltimosNdias["buyOrSale"]=="Sale"]["name"]))
    except:
      vendieronNombres = []
    nombres = list(set(compraronNombres+vendieronNombres))
    nombresdataframe = pd.DataFrame({"Nombres":nombres})

    ## Como los nombres no son exactos, necesitamos una funcion de probabilidad para matchearlos(libreria difflib)
    def masProbable(nombre1,lista):
      nombreLista = ""
      probabilidad, probMejor = 0,0
      for i in range(len(lista)):
        sm = difflib.SequenceMatcher(None, nombre1,lista[i])
        probabilidad = sm.ratio()
        if ((probabilidad > probMejor) or (i==0)):
          probMejor = probabilidad
          nombreLista = lista[i]
      if probMejor < 0.65:
        nombreLista = "No Match"
      return nombreLista

    ## Triangulando, cargamos los cargos al dataframe
    nombresFinal, cargosFinal, nombresProbables = [],[],[]
    largo = len(nombresdataframe)
    for i in range(largo):
      nombre = list(nombresdataframe["Nombres"])[i]
      nombreProbable = masProbable(nombre,list(dataframe["Nombre"]))
      nombresFinal.append(nombre)
      if nombreProbable!="No Match":
        cargosFinal.append(list(dataframe[dataframe["Nombre"]==nombreProbable]["Cargo"])[0])
      else:
        cargosFinal.append("No Match")
      nombresProbables.append(nombreProbable)
    ##Vamos a agregar el nombre extendido de la accion principal
    time.sleep(0.5)
    try:
      nombre = accion.info['longBusinessSummary']
    except:
      nombre = "No avaible"
    try:
      nombre = str(finnhub_client.company_profile2(symbol='AAPL')["name"])
    except:
      nombre = "No avaible"
    if nombre == "No avaible":
      try:
        #Puesto ultimo#Puesto ultimo # HABRIA QUE HACER UN TRIA ACA ABAJO TAMBIEN# HABRIA QUE HACER UN TRIA ACA ABAJO TAMBIEN
        link = "https://www.wsj.com/market-data/quotes/"+str(stock)+"/company-people"
        texto = []
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(link)
        page = BeautifulSoup(driver.page_source,"html.parser")
        nombreExtendido = page.find("span",attrs={"class":"hdr_co_name"})
        clear_output()
        print(nombre)
        #Puesto ultimo#Puesto ultimo, antes nombre era "no avaible aca abajo"
        nombre = str(nombreExtendido.text) ## ACA VAMOS A HACER MODIFICACIONES PARA SACARLAS DE OTRO LADO
      except:
        nombre = "No avaible"
    try:
      if len(nombre.split(".")[0].split(" "))>4:
        if len(nombre.split(",")[0].split(" "))<=4:
          nombre = nombre.split(",")[0]
        else:
          nombre = " ".join((nombre.replace(".","").replace(",","").split(" "))[0:4])
      else:
        nombre = nombre.split(".")[0]
    except:
      print("continua")
    print(nombre)

    time.sleep(0.5)

    dfNombreCargo = pd.DataFrame({"Nombre":nombresFinal,"Cargo":cargosFinal,"NombreMasProbable":nombresProbables})
    dfBuyOrSale = dfUltimosNdias[(dfUltimosNdias["buyOrSale"] == "Buy") | (dfUltimosNdias["buyOrSale"] == "Sale")]
    dfBuyOrSale["Position"] = ""
    dfBuyOrSale = dfBuyOrSale.rename(columns={"symbol": "Stock"})
    #dfBuyOrSale["Extended name"] = nombre
    #dfBuyOrSale["Stock"] = stock
    
    ### Exportamos el dataframe de insider transactions finalizado
    for i in range(len(dfBuyOrSale)):
      pos = list(dfNombreCargo[dfNombreCargo["Nombre"] == list(dfBuyOrSale["name"])[i]]["Cargo"])[0]
      try:
        dfBuyOrSale["Position"][i:i+1] = pos # ult cambiado
      except:
        dfBuyOrSale["Position"][i:i+1] = "INDEF"
    try:
      df = pd.concat([pd.read_csv("insidersInfo.csv"),dfBuyOrSale])
      df.to_csv("insidersInfo.csv",index=False)
    except:
      #dfBuyOrSale.to_csv("insidersInfo.csv",index=False)
      dfBuyOrSale.to_csv("insidersInfo.csv",index=False)
      time.sleep(2)

    ## Hacemos un dataframe con el rango de fechas a analizar y los valores historicos hasta esa fecha del precio del stock
    datos = pd.DataFrame(accion.history(str(diasAtras)+"d")) # tiempo atras, se pone en el formato (diasAtras)+"d"
    fechas = []
    for i in range(len(datos.index)):
      fechas.append(datetime.date(list(datos.index)[i]))
    valores = list(datos["Close"])
    valoreStock = pd.DataFrame({"Fecha":fechas,"Stock":str(stockPrincipal),"Valores":valores,"Extended name":nombre})
    try:
      valoresTotales = pd.concat([pd.read_csv("preciosHist.csv"),valoreStock])
      #valoresTotales.to_csv("preciosHistoricos.csv",index = False)
      valoresTotales.to_csv("preciosHist.csv",index = False)
    except:
      #valoreStock.to_csv("preciosHistoricos.csv",index = False)
      valoreStock.to_csv("preciosHist.csv",index = False)
      time.sleep(1)
    print(nombre)
    
# Deshabilitar las advertencias para pandas
pd.options.mode.chained_assignment = None
#
#Vamos a poner casi mil de stocksTotales, en vez de stocksCargados
print(diasAtras)
insiderTraders(stocksTotales,diasAtras) ##cambiar

# Volver a habilitar las advertenciasde pandas
pd.options.mode.chained_assignment = 'warn'
