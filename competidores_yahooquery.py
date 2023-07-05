import funcionesCompetidores_yahooquery
from funcionesCompetidores_yahooquery import *
import os
from datetime import datetime
import pandas as pd
import yahooquery as yq
from yahooquery import Ticker
import math
import finnhub

finnhub_client = finnhub.Client(api_key="cee6jviad3i92cealk5gcee6jviad3i92cealk60")
tiempoInicial = time.time() #Registramos el inicio de ejecucion

## Cargamos el dataframe
try:
  filename = sys.argv[1]
  if ".csv" in filename:
    data = str(pd.read_csv(filename)).replace("[","").replace("]","").replace(" ","").split(":")[1].split("\n")[0].split(",")
    print(data)
  elif "," in filename:
    data = filename.split(",")
    print(data)
  else:#Cuando aparece un stock solo
    data = [filename]
    print(data)
except:
  data = pd.read_csv("LISTADARIOACTUALIZADA.csv")
  data = list(data["Symbol"])

totalStocks = data #data[40:70] #PARA PROBAR VEO LAS PRIMERAS 20
print("Stocks a analizar: " + str(totalStocks))
mercados = ["NASDAQ","NYSE"]

#(para ahorrar tiempo) Se agarra el nombre de unas estadisticas, usando un stock que sabemos que las tiene(Meli por ejemplo)
accion2 = "MELI";symbol2 = yq.Ticker(accion2);infoFinanciera2 = symbol2.financial_data #Usamos MELI que sabemos que va a tener esta info
estadistica = list(infoFinanciera2[accion2]) 
otrasEstadisticas = ["Price/Earning","Return on Sales","Days Receivable","Days Inventory","Debt to Assets","Leverage","Times Interest Earned"]

##  BUSQUEDA DE COMPETIDORES ##

for i in range(len(totalStocks)):
  try:#new
    estadisticasDefinidas = estadistica
    #Buscamos la primera tanda de competencia
    accion,accionPrincipal = totalStocks[i],totalStocks[i] #Nos va a servir posteriormente tener dos nombres para la accion a analizar.
    print("Competencia de "+accion+":")
    try:
      stocks = buscarPrimeraTandaCompetencia(accion,accionPrincipal)
    except: # por si no esta la accion en la pagina de la funcion anterior
      stocks = buscarCompetencia(totalStocks[i],["NASDAQ","NYSE"]) #ca,boe stocks por totalStocks

    compe = []
    for i in range(len(stocks)):
      if i%4 == 0: time.sleep(1) #Esto quizas se pueda sacar si funciona bien ##(PROBAR)##
      compe.append(buscarCompetencia(stocks[i],["NASDAQ","NYSE"]))
    compe = list(set([item for sublist in compe for item in sublist])) #Unimos las distintas extracciones y sacamos los repetidos
    compe = insertarAdelante(compe,accionPrincipal) #Insertamos la accionPrincipal al principio
    print(compe)

    # Daremos un puntaje a las acciones si es que Sector/industria coinciden con la accionPrincipal
    accion = yq.Ticker(accionPrincipal)
    time.sleep(0.3)
    resumenPerfil = accion.asset_profile
    time.sleep(0.3)
    sectorPrincipal = resumenPerfil[accionPrincipal]["sector"]
    industriaPrincipal = resumenPerfil[accionPrincipal]["industry"]
    print("Sector principal: "+str(sectorPrincipal)+", Industria principal: "+str(industriaPrincipal))
    puntajes = puntajesStocks(compe,industriaPrincipal,sectorPrincipal) #Aca sacamos los puntajes
    stocksGanadores=[]
    #Si hay pocas que coinciden en los dos, les agregamos tambien aquellos que coinciden en solo uno.
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

    print("Busqueda de competidores terminada, ahora se buscara las estadisticas de cada uno. \n\n")

    ## Nos quedamos con N competidores con mayor marketcap.(En nuestro caso seran 6)
    marketCapFiltrados = []
    for i in range(len(stocksGanadores)):
      accion = stocksGanadores[i]
      symbol = yq.Ticker(accion)
      try:
        marketCapFiltrados.append(symbol.quotes[accion]["marketCap"])
      except:
        marketCapFiltrados.append(0)
    dataframeFiltrados = pd.DataFrame({"stocks":stocksGanadores,"market":marketCapFiltrados})
    dataframeFiltrados = dataframeFiltrados.sort_values("market",ascending=False)
    maxCompetidores = 6
    stocksGanadores = list(dataframeFiltrados["stocks"][0:maxCompetidores])
    stocksGanadores = insertarAdelante(stocksGanadores, accionPrincipal) 
    print(stocksGanadores)
    #Despues se podria quitar la busqueda de market cap aunque no se si conviene
  
    
    #Utilizamos yahooquery para buscar las estadisticas que nos falten para cada uno de los competidores
    allValues = []
    for i in range(len(stocksGanadores)): 
      #aca deberiamos poner para intentar leer el competidores.csv. En caso que se pueda
      #preguntamos si el stockganador actual esta dentro de la columna stock de competidores.csv
      #si llega a estar cargamos las columnas que conforman al ALLvalues [2:]
      #Si no llega a estar sguimos con el codigo
      #Si es except continuamos con el codigo tambien

      accion = stocksGanadores[i]
      symbol = yq.Ticker(accion)
      #newnew

      estaEnDfAntiguo = False
      import os #newnew
      """archivo_csv = "Competidores.csv"
      if os.path.isfile(archivo_csv):
        print("Existe el dataframe competi")
        dataframeExtraccion = pd.read_csv("Competidores.csv").copy()
        if str(accion) in dataframeExtraccion["Stock"].values.tolist():
          estaEnDfAntiguo = True
          print("ESTA EN COMPETIDORES ANTIGUO")
      else:
        print("No existe el dataframe competi")

      #if estaEnDfAntiguo == False:"""

      #problemas = False
      try:
        infoFinanciera = str(symbol.financial_data[accion]) #problema aca creo, #asset_profile era antes
      except:
        print("problemas")
      valor = []
      try:
        largo = len(infoFinanciera)
      except:
        print("Problemas")
        break
      for j in range(len(estadistica)): 
        problemas = False
        try:
          estadisticaYvalor = ((str(infoFinanciera).split(","))[j].replace("{","").replace("}","").replace("'","").replace(" ","",2).split(":"))
          estadisticaPalabra = str(estadisticaYvalor[0][0]).upper()+str(estadisticaYvalor[0][1:])
          estadisticaPalabra = separarMayus(estadisticaPalabra)
          valor.append(str(estadisticaYvalor[1]))
        except:
          problemas = True
          valor.append("CHEQUEO") # En vez de chequeo seria cero (0)-> pero esta solucion si bien es fea, nos conviene.

      #Utilizamos yahooQuery (yaho finance no funciona mas)
      ticker_object = yq.Ticker(accion)
      income_statement = ticker_object.income_statement()
      incomeStatement = income_statement.T.iloc[0:,0:1].T
      financials = ticker_object.financial_data[accion]
      balance_sheet = ticker_object.balance_sheet()

      #Datos del ultimo año
      # Price earning #
      try:
        priceEarning = ticker_object.summary_detail[accion]["trailingPE"]
      except:
        priceEarning = 0
      valor.append(priceEarning)

      # Profilability ratios  #
      try:
        returnOnSales = int(pd.DataFrame(incomeStatement)["NetIncome"])/financials["totalRevenue"] #PARECE QUE SI
      except:
        returnOnSales = 0 #era none
      valor.append(returnOnSales)

      # Activity ratios #
      try:
        totalSales = financials["totalRevenue"] #ESTE NO ESTOY MUY SEGURO POR EL TOTAL SALES 
        daysReceivable = (balance_sheet["AccountsReceivable"][-1]/totalSales)*365
      except:
        daysReceivable = 0 #era none
      valor.append(daysReceivable)

      try:
        cogs = income_statement["CostOfRevenue"][-1]#cost of goods solds -> es costOfRevenue al parecer
        daysInventory = balance_sheet["Inventory"][-1]/(cogs/365) 
      except:
        daysInventory = 0 #era none
      valor.append(daysInventory)

      # Debt ratios #
      try:
        debtToAssets = balance_sheet["TotalDebt"][-1]/balance_sheet["TotalAssets"][-1] 
      except:
        debtToAssets = 0 #era none
      valor.append(debtToAssets)

      try:
        ownersEquity = balance_sheet["StockholdersEquity"][-1] ##PARECE QUE SI
        leverage = balance_sheet["TotalAssets"][-1]/ownersEquity
      except:
        leverage = 0 #era none
      valor.append(leverage)

      try: 
        interest = income_statement["InterestExpense"][-1] #PARECE QUE SI
        timeInterestEarned = income_statement["EBIT"][-1]/(interest)
      except:
        timeInterestEarned = 0 #era none
      valor.append(timeInterestEarned)
      #Esto nisiqueira lo modificamos
      allValues.append(valor) #Es necesario tener allvalues y valor por separado? quizas sacar  uno de los dos (NEWNEW)
      print("allVALUIEs no sacado")
      print(allValues)

      if problemas == True:
        print("No se pudo con "+str(accion))
        
      """else:
        allValues.append(list(dataframeExtraccion[dataframeExtraccion["Stock"]==accion].iloc[:,3:].values.tolist()[0]))
        print("SACADO")
        print(allValues)
        print("Anteior sacado")"""


    #Comienzo nivel 2
    #Agregamos a la estadisticas las nuevas columnas

    estadisticasDefinidas = estadisticasDefinidas + otrasEstadisticas

    #Agregamos el NOMBRE EXTENDIDO de la accion principal : ACLARACION: Esto se podia poner antes asi no se repite pa
    ticker_object = yq.Ticker(accionPrincipal)
    try:
      nombre = ticker_object.summary_profile[accionPrincipal]["longBusinessSummary"]
    except:
      nombre = "NAN"
    if nombre == "NAN":
      try:
        str(finnhub_client.company_profile2(symbol='AAPL')["name"])
      except:
        print("nombreExtendidoNAN")
    if len(nombre.split(".")[0].split(" "))>4:
      if len(nombre.split(",")[0].split(" "))<=4:
        nombre = nombre.split(",")[0]
      else:
        nombre = " ".join((nombre.replace(".","").replace(",","").split(" "))[0:4])
    else:
      nombre = nombre.split(".")[0]
    
    #Hacemos un dataframe con los stocks para visualizar si hay algun Noone
    dataframe2 = pd.DataFrame({"Competidor":[0],"Nombre":[0],"Stock":[0]}) #Tendria que ser, competidor, nombre competidor y stock
    dataframe2[estadisticasDefinidas] = 0

    #Ponemos en el dataframe el nombre del competidor y a que competidor pertenece cada stock.
    for i in range(len(allValues)): 
      allValues[i].insert(0,accionPrincipal)
      allValues[i].insert(1,nombre)
      allValues[i].insert(2,stocksGanadores[i])
      dataframe2.loc[i] = allValues[i]

    ## Como se aclaro antes, hay veces que yahoofinance no te tira el marketcap para ciertos stocks en la primera pasada:
    # 1) Para resolver esto, si yahoo finance no tiene los datos, los sacamos de la pagina que mencionamos en la funcion anterior.
    marketCap = ["MarketCap"] 
    marketCapAsecas = []
    marketCapOrdenado =  []
    for i in range(len(stocksGanadores)):
      stock = stocksGanadores[i]
      accion = yq.Ticker(stock)
      try:
        mcap = accion.summary_detail[stock]["marketCap"]#Muchos cambios
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

    #marketCap ordenado y los respectivos nombre.
    marketCapOrdenado.sort(reverse=True)
    marketCapTop  = [] 
    marketCapTopNombres = [] 
    for i in range(len(marketCapOrdenado)):
      marketCapTop.append(marketCapOrdenado[i][0]) #->marketCap
      marketCapTopNombres.append(marketCapOrdenado[i][1])
    print(str(marketCapTop)+"<->"+str(marketCapTopNombres))

  ####
    #Agrego marketcap al dataframe->#Esta parte puede traer errores? deberia poner otra cosa en except? fijarse
    print("DFrame2")
    try:
      dataframe2.insert(3,"MarketCap",marketCapAsecas)
    except:
      print("dataframe2 no se utilizo")

    dataframe2[otrasEstadisticas+["debtToEquity"]] = dataframe2[otrasEstadisticas+["debtToEquity"]].fillna(0) 
    #Guardamos para ver como quedo
    dataframe2Renovado = dataframe2 # Lo dejo asi porque luego cambie el nombre del dataframe a este.
    #print("dataframe2Renovado1")
    #print(dataframe2Renovado) ##AGREGADO

    try:
      dfCompetidores = pd.read_csv("Competidores.csv")
    except:
      dfCompetidores = pd.DataFrame()

    #Tomamos la fila del stockPrincipal para reinsertarla al principio luego de ordenar por marketCap el dataframe
    accionprincipalFila = dataframe2Renovado.drop(dataframe2Renovado.index[1:])
    dataframe2Renovado = dataframe2Renovado.drop(dataframe2Renovado.index[0])
    dataframe2Renovado = dataframe2Renovado.sort_values(by='MarketCap', ascending=False) 
    dataframe2Renovado = pd.concat([accionprincipalFila,dataframe2Renovado]).reset_index(drop=True)
    #Este de abajo es importante, se puede reducir aun mas la cantidad de acciones que tomamos en su orden por el marketCap!.
    dataframe2Renovado = dataframe2Renovado.head(6) ## No tiene sentido ahora esto, ya que solo nos muestran 6 con mas marketCap cambio de 15->6 # quizas se pueda borrar despues

    print("dataframe2Renovado2")
    print(dfCompetidores) ##AGREGADO

    try:
      dfCompetidores = pd.concat([dfCompetidores,dataframe2Renovado])
    except:
      dfCompetidores = dataframe2Renovado

    print("DFCOMPETIDOSDOS2")
    print(dfCompetidores) ##AGREGADO

    dfCompetidores = dfCompetidores.replace("None",0) #lo deberia hacer antes esto, no aca, porque aca agrra a todos
    dfCompetidores.to_csv("Competidores.csv",index = False)
    #Habra que guardar de una forma diferente el competidores.csv, asi tenemos en cuenta al dataframe viejo, es decir el anterior!

    clear_output()
    print(str(i)+"/"+str(len(totalStocks))) #Esto no funciona como deberia porque hay muchos i-> lo soluciono luego

    print("Terminado",accionPrincipal)
  except: #NEWNEW
    print("No se puedo con",accionPrincipal)
    #aca deberia sacar la accionPrincipal de la lista si lo que quiero despues es ir rellenando el csv de 1 en 1 #NEWNEW

  
time.sleep(1)

print("BUSCAREMOS LAS OCUPACIONES DE CADA UNO")
## Sacaremos la informacion de que se ocupa la accion desde sec.gov
# Para eso primero buscamos el CIK asociado al stock, ya que el link que buscamos usa esto.
dataFrame = pd.read_csv("Competidores.csv").copy()
analizados = list(set(dataFrame["Competidor"]))
#
link = "https://www.sec.gov/include/ticker.txt"
driver = webdriver.Chrome(service=service, options=options)
driver.implicitly_wait(1)
driver.get(link)
page = BeautifulSoup(driver.page_source,"html.parser")
driver.quit()
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
  stocksGanadores = list((dataFrame[dataFrame["Competidor"]==analizados[j]])["Stock"])
  nombre = list((dataFrame[dataFrame["Competidor"]==analizados[j]])["Nombre"])[0]
  competidor = []
  linkEmpresa = []
  ocupacionEmpresas = []
  empresas = []
  print(nombre)
  
  #MODIFICADO DESDE ACA->>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
  for i in range(len(stocksGanadores)):
    accion = stocksGanadores[i]
    symbol = yq.Ticker(accion) ############MODIFICADO
    empresa = str(stocksGanadores[i])
    link = []
    try:
      ocupacionEmpresa = symbol.summary_profile[accion]["longBusinessSummary"]
    except:
      ocupacionEmpresa = "NAN"
    #Si yahoofinance no funco 
    if (ocupacionEmpresa == "NAN"): #ULTIMO MODIFICADO
      try: ## CONVERTIR LO DE ABAJO EN FUNCION
        link = "https://www.wsj.com/market-data/quotes/"+str("NFLX")+"/company-people"
        driver = webdriver.Chrome(service=service, options=options)
        driver.implicitly_wait(0.5)
        driver.get(link)
        page = BeautifulSoup(driver.page_source,"html.parser")
        driver.quit()
        ocupacionEmpresa = page.find("p",attrs={"class":"txtBody"})
        ocupacionEmpresa = str(ocupacionEmpresa.text) 
      except:
        print("OcupacionNan")
    try:
      for u in range(len(stockCIK)):
          if(stockCIK[u]== str(accion).lower()):
            link = (str("https://www.sec.gov/edgar/browse/?CIK="+str(stockCIK[u+1])+"&owner=exclude"))
    except:
      link = []
    empresas.append(empresa)
    #Esto de aca abajo es para recortar el largo de ocupaciones sino data estudio no funcion-> Esto podria ser una funcion y pasarla al otro archivo # NEWNEW
    try:
      indice = ocupacionEmpresa[1900:2000].find(".")
      ocupacionEmpresa = ocupacionEmpresa[0:1900+indice]
    except:
      ocupacionEmpresa = ocupacionEmpresa[:2000]

    ocupacionEmpresas.append(ocupacionEmpresa) 
    if str(link) == "[]":
      linkEmpresa.append("No disponible")
    else:
      linkEmpresa.append(link)
    competidor.append(analizados[j])
  
  data = pd.DataFrame({"Competidor":competidor,"Nombre":nombre,"Empresa":empresas,"Ocupacion":ocupacionEmpresas,"Link":linkEmpresa})
  try:
    dataEyO = pd.concat([dataEyO, data])
  except:
    dataEyO = pd.DataFrame({"Competidor":competidor,"Nombre":nombre,"Empresa":empresas,"Ocupacion":ocupacionEmpresas,"Link":linkEmpresa})

###
#dataSinModificar = dataEyO #NEWNEW sacado ultimo
#Guardamos las ocupaciones!
dataEyO['Ocupacion'] = dataEyO['Ocupacion'].str.replace(',', '-')
dataEyO
dataEyO.to_csv("Ocupaciones.csv",sep=",",index=False) #
time.sleep(1)


##  BUSCAMOS EL VALOR INTRINSECO  ##
print("BUSCAREMOS EL VALOR INTRINSECO DE CADA ACCION")
dfcompeti = pd.read_csv("Competidores.csv")
competidores = list(set(dfcompeti["Competidor"]))
print(competidores)
df = pd.DataFrame()


for h in range(len(competidores)):
  dfcompeti = pd.read_csv("Competidores.csv")
  competi = list(dfcompeti[dfcompeti["Competidor"]==competidores[h]]["Stock"]) # EL stock principal y los 3 competidores con mas marketcap->aca deberia cambiar por si tiene menos competidores, hacer un try poniendo todos
  print(competi)
  nombre = list(dfcompeti[dfcompeti["Competidor"]==competidores[h]]["Nombre"][0:1])[0]
  print(nombre)
  stocksTotales = competi
  
  #factor = math.pow(10,0) #cambiando esto deberia dar lo mismo ya que es solo ver que numeros
  #nombre = "AMZN"
  #stocksTotales = ["WIRE","NFLX","AMZN","MELI","AAPL","META","CMRX"] #SACARLOOOOOOOO #Descomentar
  #stocksTotales = ["WIRE","NOG","SD","ROCC","JAKK","CALM","ADTH","OVV","HCC","CHRD","CRDE","PDCE","RRC","NEX","ESTE"]

  precio = []
  valorIntrinseco = []
  margen = []
  stock = []
  competidor = []
  competitorOf = []
  for acc in range(len(stocksTotales)):
    try:
      accion = stocksTotales[acc]
      aapl = Ticker(accion) #Deberia no llamarse aapl
      print("\n")
      print(str(accion)+":  ")
      try:
        financialData = aapl.all_financial_data()
        cashflow = aapl.cash_flow()
        balanceSheet = aapl.balance_sheet()
      except:
        continue
      try:
        largo = len(financialData["TotalRevenue"])
      except:
        continue

      revenueGrowth = 0 
      for i in range(1,largo):
        crecimiento = ((financialData["TotalRevenue"][-i]-financialData["TotalRevenue"][-i-1])/financialData["TotalRevenue"][-i-1])*100
        revenueGrowth += crecimiento
      revenueGrowth = np.round(revenueGrowth/(largo-1),0) #Promedio de crecimiento en los ultimos años

      revenueGrowth = 0

      try:
        capex = np.round((cashflow["CapitalExpenditure"][-1]),2) # es un menos en realidad pero no importa porque en changenwc lo ponemos alrevez al giso
      except:
        capex = 0
      try:
        depreciation = np.round((cashflow["DepreciationAndAmortization"][-1]),0) ##OR  financialData["Depreciation"] #Ver
      except:
        depreciation = 0
      sales = np.round(financialData["TotalRevenue"][-1],0) #Mantenemos unas ventas promedio

      
      cantidadAniosRegistrados = 5 # Verificar
      sales *= 1 # En 1 dio buenos resultados

      try:
        COGStoSales = np.round((financialData["CostOfRevenue"][-1]/sales)*100,0)
      except:
        COGStoSales = 0
      try:
        SGandAtoSales = np.round((financialData["SellingGeneralAndAdministration"][-1]/sales)*100,0)
      except:
        SGandAtoSales = 0
      taxRate = 23
      try:
        currentAssetsToSales = np.round((financialData["CurrentAssets"][-1]/sales)*100,0)
      except:
        currentAssetsToSales = 0
      try:
        currentLiabilitiesToSales = np.round((financialData["CurrentLiabilities"][-1]/sales)*100,0)
      except:
        currentLiabilitiesToSales = 0
#######

      print("\n")
      print("Depreciation")
      print(depreciation)
      #print("CostOfRevenue")
      #print(financialData["CostOfRevenue"])
      #
      print("revenueGrowth")
      print(revenueGrowth)
      print("capex")
      print(capex)
      print("depreciation")
      print(depreciation)
      print("cantidadAniosRegistrados")
      print(cantidadAniosRegistrados)
      print("COGStoSales")
      print(COGStoSales)
      print("SGandAtoSales")
      print(SGandAtoSales)
      print("currentAssetsToSales")
      print(currentAssetsToSales)
      print("currentLiabilitiesToSales")
      print(currentLiabilitiesToSales)
      #

      print("\n")
      
      terminalGrowthRate = 0 # 
      

      #revenue = revenue_anterior*(1+revenueGrowth/100) #Si es cero, el revenue anterior es el  primer revenue (osea el sales-> TOmo el promedio como esta arriba o pongo devuelta?)
      revenue = []
      for i in range(cantidadAniosRegistrados):
        if i==0:  revenue.append((sales*(1+revenueGrowth/100)))
        else: revenue.append(np.round(revenue[-1]*(1+revenueGrowth/100)))

      #NEENEENEENEENEENEENEENEENEENEE
      try:
        currentLiabilitiesAnterior = np.round(financialData["CurrentLiabilities"][-1],0) #AO QUIZAS PONER -2 ACA#AO QUIZAS PONER -2 ACA#AO QUIZAS PONER -2 ACA#AO QUIZAS PONER -2 ACA
        currentAssetsAnterior = np.round(financialData["CurrentAssets"][-1],0) #AO QUIZAS PONER -2 ACA#AO QUIZAS PONER -2 ACA#AO QUIZAS PONER -2 ACA
      except:
        currentLiabilitiesAnterior = 0
        currentAssetsAnterior = 0
      #NEENEENEENEENEENEENEENEE
      
      currentAssets = []
      currentLiabilities = []
      try:
        for i in range(cantidadAniosRegistrados):
          currentAssets.append(round((currentAssetsAnterior/sales*100)*revenue[i]/100,1)) # 100 fueron agregados porque estaba en porcentaje antes
          currentLiabilities.append(round((currentLiabilitiesAnterior/sales*100)*revenue[i]/100,1)) #100 fueron agregados orque estaba en porcentaje antes
      except:
        currentAssets = [0 for x in range(cantidadAniosRegistrados)]
        currentLiabilities = [0 for x in range(cantidadAniosRegistrados)]


        """##ULTIMO CAMBIO#ULTIMO CAMBIO#ULTIMO CAMBIO
        currentAssets = []
      currentLiabilities = []
      try:
        for i in range(cantidadAniosRegistrados):
          if i == 0:
            currentAssets.append(round(financialData["CurrentAssets"][-1],1)) # ACA QUIZAS PONNER CANTIDAD DE AÑOS REGISTRADOS MAS UNO Y SACAR EL PRIMER AÑO!!!
            currentLiabilities.append(round(financialData["CurrentLiabilities"][-1],1))
          else:
            currentAssets.append(round(currentAssetsToSales*revenue[i]/100,1)) # 100 fueron agregados porque estaba en porcentaje antes
            currentLiabilities.append(round(currentLiabilitiesToSales*revenue[i]/100,1)) #100 fueron agregados orque estaba en porcentaje antes
      except:
        currentAssets = [0 for x in range(cantidadAniosRegistrados)]
        currentLiabilities = [0 for x in range(cantidadAniosRegistrados)]

        """


      #   2(DOS)
      # Verificar
      operatingIncome = [np.round(((revenue[i]*(100-COGStoSales-SGandAtoSales)/100)),0) for i in range(cantidadAniosRegistrados)] #ESTA BIEN LO DE ADENTRO?
      taxes = [np.round((operatingIncome[i]*taxRate/100),0) for i in range(cantidadAniosRegistrados)]
      nopat = [np.round((operatingIncome[i]-taxes[i]),0) for i in range(cantidadAniosRegistrados)]

      # cambiar acc, y aapl.(*nombres)
      #ESTO ES ASI?
      risk = 3.75/100
      marketPremium = 6/100
      kd = 6/100
      # Valores dinamicos NEWNEW
      beta = aapl.summary_detail[stocksTotales[acc]]["beta"] # Volatilidad con respecto al mercado
      try:
        debt = aapl.balance_sheet().loc[:,"LongTermDebt"][-1] # Preguntar longTermDebt si esta bien
      except:
        debt = 0
      marketCap = aapl.summary_detail[stocksTotales[acc]]["marketCap"]
      if marketCap>pow(10,9):
        sizePremium = 1/100
      else:
        sizePremium = 2/100
      ke = risk + marketPremium*beta + sizePremium
      costOfCapital = np.round(kd*(1-taxRate/100)*debt/(debt+marketCap)+ke*marketCap/(debt+marketCap),4) #*100 QUITAR posiblemente, Verificar esto, el 100 me olvide de anotar porque lo puse, verificar

      print("revenue")
      print(revenue)
      print("currentAssets")
      print(currentAssets)
      print("currentLiabilities")
      print(currentLiabilities)
      print("operatingIncome")
      print(operatingIncome)
      print("taxes")
      print(taxes)
      print("nopat")
      print(nopat)
      print("debt")
      print(debt)
      print("marketCap")
      print(marketCap)
      print("ke")
      print(ke)
      print("costOfCapital")
      print(costOfCapital)
      print("beta")
      print(beta)
      print("\n")
      #HASTA ACA PARECE TODO BIEN?
      ###HASTA ACA
      #changeInNwc = (currentAssets-currentLiabilities)-(currentAssets_anterior-currentLiabilities_anterior)
      changeInNwc = []
      """try:
        currentLiabilitiesAnterior = np.round(financialData["CurrentLiabilities"][-1],0) #AO QUIZAS PONER -2 ACA#AO QUIZAS PONER -2 ACA#AO QUIZAS PONER -2 ACA#AO QUIZAS PONER -2 ACA
        currentAssetsAnterior = np.round(financialData["CurrentAssets"][-1],0) #AO QUIZAS PONER -2 ACA#AO QUIZAS PONER -2 ACA#AO QUIZAS PONER -2 ACA
      except:
        currentLiabilitiesAnterior = 0
        currentAssetsAnterior = 0"""
      
      #MODIFICADOS
      for i in range(cantidadAniosRegistrados): 
        if i==0:
          try:
            changeInNwc.append((currentAssets[i]-currentLiabilities[i])-(currentAssetsAnterior-currentLiabilitiesAnterior)) #este sales deberia ser currentAssents anterior #MODIFICADO ULTIMO
            #print("\nVALORES")
            #print(currentAssets[i],currentLiabilities[i],currentAssetsAnterior,currentLiabilitiesAnterior)
          except:
            changeInNwc.append(0)
        else:
          try:
            changeInNwc.append((currentAssets[i]-currentLiabilities[i])-(currentAssets[i-1]-currentLiabilities[i-1]))
          except:
            changeInNwc.append(0)

      FCF = [np.round(nopat[i]+capex+depreciation-changeInNwc[i],0) for i in range(cantidadAniosRegistrados)]
      """print("\nCHANGE")
      for ajk in range(cantidadAniosRegistrados):
        print(nopat[ajk])
        print(capex)
        print(depreciation)
        print(changeInNwc[ajk])
      print("\nCHANGE")"""


      print("currentLiabilitiesAnterior")
      print(currentLiabilitiesAnterior)
      print("currentAssetsAnterior")
      print(currentAssetsAnterior)

      print("FCF")
      print(FCF)

      print("changeInNwc")
      print(changeInNwc)

      
      terminalValue = [0 for i in range(cantidadAniosRegistrados)]
      terminalValue[-1] = np.round((FCF[-1]*(1+(terminalGrowthRate)/100)/(costOfCapital-terminalGrowthRate)),0) #SACAR EL 100 de FCF[-1]*100 -> el de terminalgrowthrate esta bien

      totalCashFlow = [np.round((FCF[i]+terminalValue[i]),0) for i in range(cantidadAniosRegistrados)]
      presentValueOfFlows = [np.round(totalCashFlow[i]/pow((1+costOfCapital),i+1),0) for i in range(cantidadAniosRegistrados)] #CAMBIAR EL i por i+1 #NEW#NEW#NEW#NEW # AL CAMBIAR ESTO FUNCIONO!!! #NEWNEWNEWNEW

      #   3(TRES) Estas no son listas, son valores nada mas.
      enterPriseValue = np.round(sum(presentValueOfFlows),0)

      try:
        lessCurrentOutstandingDebt = np.round(balanceSheet["LongTermDebt"][-1],0)
      except:
        lessCurrentOutstandingDebt = 0
      equityValue = (enterPriseValue -lessCurrentOutstandingDebt) #Falta mas exceso de cash pero no hay en estos casos
      try:
        modules = 'defaultKeyStatistics'
        currentSharesOutstanding = np.round(float(str(aapl.get_modules(modules)).split("sharesOutstanding")[1].split(":")[1].split(",")[0]),2) ##FALTA np.round(
      except:
        continue
    
      equityValuePerShare = equityValue/currentSharesOutstanding  
      
      #   4(CUATRO) 
      currentSharePrice = aapl.financial_data[accion]["currentPrice"]
      
      discount = (equityValuePerShare-currentSharePrice)/currentSharePrice*100 #

      print("changeInNwc")
      print(changeInNwc)
      print("currentLiabilitiesAnterior")
      print(currentLiabilitiesAnterior)
      print("terminalValue")
      print(terminalValue)
      print("totalCashFlow")
      print(totalCashFlow)
      print("presentValueOfFlows")
      print(presentValueOfFlows)
      print("enterPriseValue")
      print(enterPriseValue)
      print("lessCurrentOutstandingDebt")
      print(lessCurrentOutstandingDebt)
      print("equityValue")
      print(equityValue)
      print("currentSharesOutstanding")
      print(currentSharesOutstanding)
      print("equityValuePerShare")
      print(equityValuePerShare)
      print("currentSharePrice")
      print(currentSharePrice)
      print("discount")
      print(discount)

      #HASTA ACA REGISTRADO: CHEQUEAR ENTERPRISE VALLUE
      
      
      valorIntrinseco.append(round(equityValuePerShare,2))
      precio.append(round(currentSharePrice,2))
      margen.append(str(round(discount,2))+"%")
      stock.append(stocksTotales[acc])
      competidor.append(competidores[h])
      competitorOf.append(nombre)
  
      dfnew =  pd.DataFrame({"Competidor":competidor,"Nombre":competitorOf,"Stock":stock,"Price":precio,"intrinsic value":valorIntrinseco,"Safety margin":margen})
    except:
      continue

  df = pd.concat([df,dfnew]) 

df.to_csv("ValorIntrinseco.csv",index=False)
print(dfnew)
print("VALOR INTRINSECO TERMINADO\n-> Codigo finalizado <-")

tiempoFinal= time.time()
print("Tiempo total:" +str(tiempoFinal-tiempoInicial))

