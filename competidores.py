import funcionesCompetidores
from funcionesCompetidores import *

### Codigo real ###
## Cargamos el dataframe
data = pd.read_csv("stocks1.csv") 
totalStocks = list(data["Symbol"][0:2]) #Aca estoy haciendo que agarre menos stocks para probar
totalStocks = ["FLWS"]
print("Stocks a analizar: " + str(totalStocks))
mercados = ["NASDAQ","NYSE"]

#Este codigo lo sacamos del ciclo para que se ahorre tiempo
#El codigo agarra el nombre de unas estadisticas, para eso usamos un stock conocido->Meli ejemplo.
accion2 = "MELI";symbol2 = yf.Ticker(accion2);infoFinanciera2 = symbol2.stats()["financialData"] #Usamos netflix que sabemos que tiene los datos-> dsp podemos ssacar y poner la lista de una y separar el print por ",
estadistica = list(infoFinanciera2) #Son los nombres de las estadisticas que proporcionan una funcion de YF
otrasEstadisticas = ["Price/Earning","Return on Sales","Days Receivable","Days Inventory","Debt to Assets","Leverage","Times Interest Earned"]#Despues poner el purchases(Days Payable)
print(estadistica)

##Buscamos los competidores de cada stock
for i in range(len(totalStocks)):
  estadisticasDefinidas = estadistica
  #Buscamos la primera tanda de competencia
  accion,accionPrincipal = totalStocks[i],totalStocks[i] #Nos va a servir posteriormente tener dos nombres para la accion a analizar.
  print("Competencia de "+accion+":")
  #textoClean = buscarCompetencia(accion,mercados)
  try:
    stocks = buscarPrimeraTandaCompetencia(accion,accionPrincipal)
  except: # por si no esta la accion en la
    stocks = buscarCompetencia(stocks[i],["NASDAQ","NYSE"])

  compe = []
  for i in range(len(stocks)):
    compe.append(buscarCompetencia(stocks[i],["NASDAQ","NYSE"]))
  compe = list(set([item for sublist in compe for item in sublist])) #Unimos las distintas extracciones y scamos los repetidos
  #Insertamos la accionPrincipal al principio(en caso de estar o no)
  compe = insertarAdelante(compe,accionPrincipal)

  #Filtramos por Sector e industria-> Que sean como la accionPrincipal
  accion = yf.Ticker(accionPrincipal)
  resumenPerfil = accion.stats()["summaryProfile"]
  sectorPrincipal = resumenPerfil["sector"]
  industriaPrincipal = resumenPerfil["industry"]
  puntajes = puntajesStocks(compe,industriaPrincipal,sectorPrincipal)
  stocksGanadores=[]
  #Si vemos las coincidencias-> si son muy pocas agregamos a los que se relacionan por lo menos en algunas de las dos.
  for i in range(len(compe)):
    if puntajes[i] >= 2:
      stocksGanadores.append(compe[i]) #Tendriamos que remover aquellos que vamos poniendo en compe(con su puntuacion correspondiente)-> no es tan relevante en tiempo hacer esto
  if len(stocksGanadores) <=4:
    for i in range(len(compe)):
      if puntajes[i]==1:
        stocksGanadores.append(compe[i])

  stocksGanadores = insertarAdelante(stocksGanadores, accionPrincipal)
  print("\n")
  print(", ".join(stocksGanadores))

  #termina en un stocksGanadores
  print("TERMINO \n\n")
  #Hasta aca queda la busqueda de competidores, ahora vamos a sacar estadisticas o modificar cosas para la visualizacion del informe.

  #Desde YahooFinance se puede ver las estadisticas de cada accion!. Aprovechemos eso para luego hacer las comparaciones en el excel/csv que crearemos.
  stocksUnicos = stocksGanadores
  allValues = []
  for i in range(len(stocksUnicos)):
    accion = stocksUnicos[i]
    symbol = yf.Ticker(accion)
    try:
      infoFinanciera = str(symbol.stats()["financialData"]) 
    except:
      continue
    valor = []
    try:
      largo = len(infoFinanciera)
    except:
      print("Problemas")
      break
    for j in range(len(estadistica)): #cambiar el 30 por el len(blabla)->Como es fijo en esta parte por ahora no importa #-> #-> PRUUEBA ULTIMA SACADA range(30)
      problemas = False
      try:
        estadisticaYvalor = ((str(infoFinanciera).split(","))[j].replace("{","").replace("}","").replace("'","").replace(" ","",2).split(":"))
        estadisticaPalabra = str(estadisticaYvalor[0][0]).upper()+str(estadisticaYvalor[0][1:])
        estadisticaPalabra = separarMayus(estadisticaPalabra)
        valor.append(str(estadisticaYvalor[1]))
      except:
        problemas = True
        valor.append("CHEQUEO") # EN VEZ DE "CHEQUEO" LO DEBO CAMBIAR POR CEROS
    #Aca hay que hacer un for que se encargue de las demas columnas que son -> Price earning,Return on Sales, Days rec... y eso,deb assets levereage time interest earnid
    #Para eso tambien debemos agregar a estadistica a estas columnas nuevas, pero esto lo tenemos que hacer fuera del for claramente->>>>>>>>
    #PONEMOS ACCION
    ######->>>>
    
    ticker_object = symbol #cambiamos accionPrincipal por accion #cambiamos yf.ticker(accion)->por simbol de arriba asi no gasta ese tiempo
    # get financial statements
    time.sleep(0.5)
    balancesheet = ticker_object.balancesheet
    time.sleep(0.5)
    cashflow = ticker_object.cashflow
    time.sleep(0.5)
    financials = ticker_object.get_financials()
    time.sleep(0.5)
    #Del ultimo año
    try: # VER OTRA FORMA MAS DE PONER PRICE EARNING# VER OTRA FORMA MAS DE PONER PRICE EARNING# VER OTRA FORMA MAS DE PONER PRICE EARNING
      quote_table = si.get_quote_table(accion, dict_result=False)
      priceEarning = list(quote_table[quote_table["attribute"]=="PE Ratio (TTM)"]["value"])[0] 
      #print("priceEarning:  "+str(priceEarning))
    except:
      priceEarning = 0 #era none
    if ((priceEarning is None) or (str(priceEarning)=="nan")):
      priceEarning = 0
    valor.append(priceEarning)
    
    ## profilability ratios
    try:
      returnOnSales = financials.iloc[0:,0]["NetIncome"]/financials.iloc[0:,0]["TotalRevenue"] #PARECE QUE SI
      #print("returnOnSales:  "+str(returnOnSales))
    except:
      returnOnSales = 0 #era none
    valor.append(returnOnSales)

    #ACTIVITY RATIOS
    try:
      totalSales = financials.iloc[0:,0]["TotalRevenue"] #ESTE NO ESTOY MUY SEGURO POR EL TOTAL SALES 
      daysReceivable = (balancesheet.iloc[0:,0]["Accounts Receivable"]/totalSales)*365
      #print("daysReceivable:  "+str(daysReceivable))
    except:
      daysReceivable = 0 #era none
    valor.append(daysReceivable)

    try:
      cogs = financials.iloc[0:,0]["CostOfRevenue"]#cost of goods solds -> es costOfRevenue al parecer
      daysInventory = balancesheet.iloc[0:,0]["Inventory"]/(cogs/365) 
      #print("daysInventory:  "+str(daysInventory))
    except:
      daysInventory = 0 #era none
    valor.append(daysInventory)

    ##DEBT RATIOS
    #leverage ownersEquity(stocksholders equity) #PARECE QUE SI
    #Formula deb assets : total debt/total ASsets
    try:
      debtToAssets = balancesheet.iloc[0:,0]["Total Debt"]/balancesheet.iloc[0:,0]["Total Assets"] #SI
      #print("DebtToASsets:  "+str(debtToAssets))
    except:
      debtToAssets = 0 #era none
    valor.append(debtToAssets)

    try:
      ownersEquity = balancesheet.iloc[0:,0]["Stockholders Equity"] ##PARECE QUE SI
      leverage = balancesheet.iloc[0:,0]["Total Assets"]/ownersEquity
      #print("levereage:  "+str(leverage))
    except:
      ownersEquity = 0 #era none
    valor.append(leverage)

    try:
      interest = financials.iloc[0:,0]["InterestExpense"] #PARECE QUE SI
      timeInterestEarned = financials.iloc[0:,0]["EBIT"]/(interest)
      #print("timeInterestEarned:  "+str(timeInterestEarned))
    except:
      timeInterestEarned = 0 #era none
    valor.append(timeInterestEarned)
    #####<<<<<-

    #A valor hay que agregarle las otrasEstadisticas-> ya fueron agregadas atras
    allValues.append(valor)
    if problemas == True:
      print("No se pudo con "+str(accion))
  print("Estadisticas a visualizar:")
  #<<<<<----- aca denbemos agregar a la estadistica las nuevas columnas
  estadisticasDefinidas = estadisticasDefinidas + otrasEstadisticas
  for i in estadisticasDefinidas:
    print(i,end=", ")

  ##Vamos a agregar el nombre extendido de la accion principal
  ticker_object = yf.Ticker(accionPrincipal)
  nombre = ticker_object.info['longBusinessSummary']
  if len(nombre.split(".")[0].split(" "))>4:
    if len(nombre.split(",")[0].split(" "))<=4:
      nombre = nombre.split(",")[0]
    else:
      nombre = " ".join((nombre.replace(".","").replace(",","").split(" "))[0:4])
  else:
    nombre = nombre.split(".")[0]
  
  ### Hacemos un dataframe con los stocks para visualizar si hay algun Noone
  dataframe2 = pd.DataFrame({"Competidor":[0],"Nombre":[0],"Stock":[0]}) #Tendria que ser, competidor, nombre competidor y stock
  dataframe2[estadisticasDefinidas] = 0

  for i in range(len(allValues)): #Ponemos en el dataframe el nombre del competidor y a que competidor pertenece cada stock.
    allValues[i].insert(0,accionPrincipal)
    allValues[i].insert(1,nombre)
    allValues[i].insert(2,stocksUnicos[i])
    dataframe2.loc[i] = allValues[i]

  #ULTIMO #ULTIMO #ULTIMO #ULTIMO Esta funcion str To num la subimos arriba en el py original
  #Hacemos un funcion para cambiar el string que contiene un numero abreviado con un + "B" "M" o "T" a un entero
  def strToNum(string):
    string = str(string)
    if "T" in string.upper(): trillon = math.pow(10,18); return float(string.split("T")[0])*trillon
    if "B" in string.upper(): billon = math.pow(10,9); return float(string.split("B")[0])*billon
    if "M" in string.upper(): millon = math.pow(10,6); return float(string.split("M")[0])*millon
    return string

  ## Como se aclaro antes, hay veces que yahoofinance no te tira el marketcap para ciertos stocks en la primera pasada:
  # 1) Para resolver esto, si yahoo finance no tiene los datos, los sacamos de la pagina que mencionamos en la funcion anterior.
  marketCap = ["MarketCap"] 
  marketCapAsecas = []
  marketCapOrdenado =  []
  for i in range(len(stocksGanadores)):
    stock = stocksGanadores[i]
    accion = yf.Ticker(stock)
    try:
      mcap = accion.stats()["summaryDetail"]["marketCap"]
    except:
      mcap = 0
    if ((mcap == 0) or (mcap is None)):
      try:
        mcap = marketCapFunc(stock,1)[0][1]
      except:
        mcap = 0
    if mcap is None:
      mcap = 0 

    marketCapOrdenado.append([mcap,stock])
    marketCapAsecas.append(mcap)
    try:
      marketCap.append(str(round(int(mcap)/math.pow(10,6),1))+"M") #->Lo puedo sacar desde mcap sin tener que fijarnos devuelta accion stats
    except:
      marketCap.append("CHEQUEO") ## Luego revisar todas las lineas que tienen ("CHEQUEO")

  #marketCapo ordenado y los respectivos nombres (Revisar si se puede sacar, ya que luego ordeno el dataframe por la columna marketCap y queda igual)
  marketCapOrdenado.sort(reverse=True)
  marketCapTop  = [] 
  marketCapTopNombres = [] 
  for i in range(len(marketCapOrdenado)):
    marketCapTop.append(marketCapOrdenado[i][0]) #->marketCap
    marketCapTopNombres.append(marketCapOrdenado[i][1])
  print(str(marketCapTop)+"<->"+str(marketCapTopNombres))


  #Agrego marketcap al dataframe->#Esta parte puede traer errores? deberia poner otra cosa en except? fijarse
  try:
    dataframe2.insert(3,"MarketCap",marketCapAsecas)
  except:
    continue

  dataframe2[otrasEstadisticas+["debtToEquity"]] = dataframe2[otrasEstadisticas+["debtToEquity"]].fillna(0) #VER#VER#VER#VER#VER#VER#VER#VER#VER#VER#VER#VER#VER#VER#VER#VER#VER#VER#VER#VER
  #Guardamos para ver como quedo
  dataframe2Renovado = dataframe2 #BORRAR DATAFRAME2RENOVADO y dejar dataframe2 cambiandolo de las filas que siguen #BORRAR DATAFRAME2RENOVADO#BORRAR DATAFRAME2RENOVADO#BORRAR DATAFRAME2RENOVADO
  #dataframe2Renovado.to_csv("Competidores"+str(accionPrincipal)+".csv",index=False) # Creado para ell google data studio #Vamos a llamarlo solamente competidores despues, esto es prueba de poner competidores de "blabla"

  # ACA VA A ESTAR EL EXCEL CON TODAS LAS EMPREsAS Y COMPETIDORES TODAS JUNTAS ESTE ES PARA EL GOOGLE DATA STUDIO 
  # VER SI ESTA BIEN ESTO DE ABAJO DE LOS TRY EXCEPT
  try:
    dfCompetidores = pd.read_csv("Competidores.csv")
  except:
    dfCompetidores = pd.DataFrame()

  #Hay que modificar estas 4 lineas para que siempre se tome a la fila donde esta la accion principal
  accionprincipalFila = dataframe2Renovado.drop(dataframe2Renovado.index[1:])
  dataframe2Renovado = dataframe2Renovado.drop(dataframe2Renovado.index[0])
  dataframe2Renovado = dataframe2Renovado.sort_values(by='MarketCap', ascending=False) #aca ordeno por marketcap->de aca me fijo las cosas
  dataframe2Renovado = pd.concat([accionprincipalFila,dataframe2Renovado]).reset_index(drop=True)

  dataframe2Renovado = dataframe2Renovado.head(15) ##Vamos a dejar los primeros 15 que mas marketCap tienen->Me parece que tiene mas sentido y los graficos se van a ver mas

  try:
    dfCompetidores = pd.concat([dfCompetidores,dataframe2Renovado])
  except:
    dfCompetidores = dataframe2Renovado
    
  dfCompetidores = dfCompetidores.replace("None",0) #lo deberia hacer antes esto, no aca, porque aca agrra a todos
  #dfCompetidores.replace(to_replace="None",value=0) #Quizas sacarlo
  dfCompetidores.to_csv("Competidores.csv",index = False)
  #dfCompetidores.to_csv("Competidores"+str(datetime.datetime.now())+".csv",index = False) #esto agregarlo luego al igual que abajo, de todas formas fijar

  #clear_output()
  print(str(i)+"/"+str(len(totalStocks))) #Esto no funciona como deberia porque hay muchos i-> lo soluciono luego

print("AHORA LAS OCUPACIONES")

## Sacaremos la informacion de que se ocupa la accion desde sec.gov
# Para eso primero buscamos el CIK asociado al stock, ya que el link que buscamos usa esto.
dataFrame = pd.read_csv("Competidores.csv")
analizados = list(set(dataFrame["Competidor"]))
#
link = "https://www.sec.gov/include/ticker.txt"
driver = webdriver.Chrome(service=service, options=options)
driver.get(link)
page = BeautifulSoup(driver.page_source,"html.parser")
for busqueda in page.findAll("pre",attrs={"style":"word-wrap: break-word; white-space: pre-wrap;"}):
  guardar = busqueda.text
stockCIK  = str(guardar.replace("\t","\n")).split("\n")
# Aqui ponemos todos los links segun el CIK.
empresas = []
ocupacionEmpresas = []
linkEmpresa = []
competidor = []
dataEyO = pd.DataFrame({"Competidor":[],"Nombre":[],"Empresa":[],"Ocupacion":[],"Link":[]})
for j in range(len(analizados)):
  stocksUnicos = list((dataFrame[dataFrame["Competidor"]==analizados[j]])["Stock"])
  nombre = list((dataFrame[dataFrame["Competidor"]==analizados[j]])["Nombre"])[0]
  competidor = []
  linkEmpresa = []
  ocupacionEmpresas = []
  empresas = []
  print(nombre)
  for i in range(len(stocksUnicos)):
    accion = stocksUnicos[i]
    symbol = yf.Ticker(accion)
    empresa = str(stocksUnicos[i])
    link = []
    try:
      ocupacionEmpresa = symbol.info["longBusinessSummary"] 
    except:
      ocupacionEmpresa = "NAN"
    try:
      for u in range(len(stockCIK)):
          if(stockCIK[u]== str(accion).lower()):
            link = (str("https://www.sec.gov/edgar/browse/?CIK="+str(stockCIK[u+1])+"&owner=exclude"))
    except:
      link = []
    empresas.append(empresa)
    ocupacionEmpresas.append(ocupacionEmpresa)
    if str(link) == "[]":
      linkEmpresa.append("No disponible")
    else:
      linkEmpresa.append(link)
    competidor.append(analizados[j])
  
  data = pd.DataFrame({"Competidor":competidor,"Nombre":nombre,"Empresa":empresas,"Ocupacion":ocupacionEmpresas,"Link":linkEmpresa})
  try:
    print("A")
    dataEyO = dataEyO.append(data)
  except:
    print("B")
    dataEyO = pd.DataFrame({"Competidor":competidor,"Nombre":nombre,"Empresa":empresas,"Ocupacion":ocupacionEmpresas,"Link":linkEmpresa})

###
dataSinModificar = dataEyO
dataEyO['Ocupacion'] = dataEyO['Ocupacion'].str.replace(',', '-')
dataEyO
dataEyO.to_csv("Ocupaciones.csv",sep=",",index=False)


## Por ultimo Buscaremos el PTFCF de los 4 primeros stocks con mas marketCap
# y luego guardamos esta info en un .csv
from datetime import datetime
df = pd.read_csv("Competidores.csv")
competidores = list(set(df["Competidor"]))

for h in range(len(competidores)):
  df = pd.read_csv("Competidores.csv")
  competi = list(df[df["Competidor"]==competidores[h]]["Stock"][0:4]) # EL stock principal y los 3 competidores con mas marketcap
  nombre = list(df[df["Competidor"]==competidores[h]]["Nombre"][0:1])[0]
  print(nombre)
  print(competi)
  stocksTotales = competi
  df = pd.DataFrame()
  for k in range(len(stocksTotales)):
    print(str(k)+"/"+str(len(stocksTotales)))
    print(stocksTotales[k])
    time.sleep(1)
    FreeCashflowAnioStock = []
    stock = stocksTotales[k]
    accion = yf.Ticker(stock)
    time.sleep(1)
    try:
      FreeCashflowAnioStock = list((accion.cash_flow).loc["Free Cash Flow"]) 
    except:
      continue;
    timestamp = list(accion.cash_flow.columns)
    tiempo = []
    for i in range(len(timestamp)):
      dt_object = datetime.strptime(str(timestamp[i]), '%Y-%m-%d %H:%M:%S')
      tiempo.append(dt_object.strftime("%Y"))


    ###
    marketCapYear = marketCapFunc(stock,7)
    ptfcf = []
    tiempo = tiempo[::-1]
    FreeCashflowAnioStock = FreeCashflowAnioStock[::-1]
    tiempoReal = list(set(tiempo) & set([x[0] for x in marketCapYear]))
    FreeCashflowReal = []
    for i in range(len(tiempo)):
      for j in range(len(tiempoReal)):
        if(tiempo[i] == tiempoReal[j]):
          FreeCashflowReal.append(FreeCashflowAnioStock[i])
          continue

    #hacer variable tiempo real
    for i in range(len(tiempoReal)):
      for j in range(len(marketCapYear)):
        if(tiempoReal[i]==marketCapYear[j][0]):
          ptfcf.append(marketCapYear[j][1]/FreeCashflowReal[i])
          continue;
    
    print(ptfcf)
    df = df.append(pd.DataFrame({"Competidor":competidores[h],"Nombre":nombre,"Stock":stocksTotales[k],"Año":tiempoReal,"PriceToFreeCashFlow":ptfcf})) #poner el stock actual
  try:
    dataframeTotal = pd.read_csv("CompetidoresPtfc.csv")
    dataframeTotal = dataframeTotal.append(df)
    dataframeTotal.to_csv("CompetidoresPtfc.csv",index=False)
  except:
    df.to_csv("CompetidoresPtfc.csv",index=False)