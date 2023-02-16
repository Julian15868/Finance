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

#Configuramos selenium
service = Service(executable_path="chromedriver.exe")
service.start()
options = webdriver.ChromeOptions()
options.add_argument("--disable-extensions")
options.add_argument("--disable-gpu")
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument('--disable-dev-shm-usage')

### Comienzo ###
#Cargamos el dataframe 
try:
  filename = sys.argv[1]
  Dataframe = pd.read_csv(filename)
except:
  Dataframe = pd.concat([pd.read_csv("stocks1.csv"),pd.read_csv("stocks2.csv")])
  
#Dataframe = pd.read_csv('stocks1.csv') #-> Hay que actualizar este por el que tiene 0 recomendaciones que tenemos guardado
stocksTotales = list(Dataframe["Symbol"].head(100)) #Sacar el head luego
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
    r = requests.get('https://finnhub.io/api/v1/stock/insider-transactions?symbol='+stock+'&token=ccvhh7qad3i3vkhgju30ccvhh7qad3i3vkhgju3g') #(30 calls per second limit: https://finnhub.io/docs/api/rate-limit).
    test = json.loads(r.text) # cargamos el JSON file como string.
    try:
      df = pd.DataFrame(data=test['data'])
    except:
      for variable in (cantComprasTodos,montComprasTodos,cantVentasTodos,montVentasTodos):
        variable.append(0)
    # atributos derivados de los datos
    try:
      df['dollarAmount'] = df['change']*df['transactionPrice']
    except:
      df['dollarAmount'] = 0
    try:
      df['insiderPortfolioChange'] = df['change']/(df['share'] - df['change'])
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
    dfUltimosNdias = df[(df['transactionDate'] >= ultimosNdias) & (df['transactionDate'] <= hoy)] #Filtramos por el rango de fecha elegido

    ## Queremos añadirle el cargo de la persona al dataframe de insider transactions
    # Para eso vamos a sacar algunos datos de sec.gov (el CIK de un stock particular), y triangular la informacion (En nuestro caso de nombre-nombre para obtener el cargo)
    import re
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
      nombre = "not avaible"
    if len(nombre.split(".")[0].split(" "))>4:
      if len(nombre.split(",")[0].split(" "))<=4:
        nombre = nombre.split(",")[0]
      else:
        nombre = " ".join((nombre.replace(".","").replace(",","").split(" "))[0:4])
    else:
      nombre = nombre.split(".")[0]
    print(nombre)
    time.sleep(0.5)

    dfNombreCargo = pd.DataFrame({"Nombre":nombresFinal,"Cargo":cargosFinal,"NombreMasProbable":nombresProbables})
    dfBuyOrSale = dfUltimosNdias[(dfUltimosNdias["buyOrSale"] == "Buy") | (dfUltimosNdias["buyOrSale"] == "Sale")]
    dfBuyOrSale["Position"] = ""
    dfBuyOrSale = dfBuyOrSale.rename(columns={"symbol": "Stock"})
    dfBuyOrSale["Extended name"] = nombre
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
      dfBuyOrSale.to_csv("insidersInfo.csv",index=False)
      time.sleep(1)

    ## Hacemos un dataframe con el rango de fechas a analizar y los valores historicos hasta esa fecha del precio del stock
    datos = pd.DataFrame(accion.history(str(diasAtras)+"d")) # tiempo atras, se pone en el formato (diasAtras)+"d"
    fechas = []
    for i in range(len(datos.index)):
      fechas.append(datetime.date(list(datos.index)[i]))
    valores = list(datos["Close"])
    valoreStock = pd.DataFrame({"Fecha":fechas,"Stock":str(stockPrincipal),"Valores":valores,"Extended name":nombre})
    try:
      valoresTotales = pd.concat([pd.read_csv("preciosHistoricos.csv"),valoreStock])
      valoresTotales.to_csv("preciosHistoricos.csv",index = False)
    except:
      valoreStock.to_csv("preciosHistoricos.csv",index = False)
      time.sleep(1)
    print(nombre)


# Deshabilitar las advertencias para pandas
pd.options.mode.chained_assignment = None
#
stocksCargados = ["MELI","AMZN","TSLA","ASTL","ACU","AZPN","ARCH","CMRX"] #De prueba son
diasAtras = 180
#Vamos a poner casi mil de stocksTotales, en vez de stocksCargados
insiderTraders(stocksCargados,diasAtras) ##cambiar
#
# Volver a habilitar las advertenciasde pandas
pd.options.mode.chained_assignment = 'warn'
