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
      try:
        dataframeExtraccion = pd.read_csv("competidores.csv")
        if accion in list(dataframeExtraccion["stock"]):
          estaEnDfAntiguo = True
      except:
        print("No se ha creado aun competidores.csv")
      #newnew

      estaEnDfAntiguo = False

      if estaEnDfAntiguo == False:
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
        print("allVALUIEs")
        print(allValues)

        if problemas == True:
          print("No se pudo con "+str(accion))
      #PODEMOS SALIR DE ACA DE ALGUNA MANER
      else: #newnewnew
        dataframeExtraccion = dataframeExtraccion[dataframeExtraccion["stock"]==accion]
        allValues.append(list(dataframeExtraccion.iloc[:,2:].values.tolist()[0]))

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
dataFrame = pd.read_csv("Competidores.csv")
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
      print(accion)
      try:
        financialData = aapl.all_financial_data()
        cashflow = aapl.cash_flow()
        balanceSheet = aapl.balance_sheet()
      except:
        continue;
      revenueGrowth = 0 #Vemos el crecimiento
      try:
        largo = len(financialData["TotalRevenue"])
      except:
        continue

      for i in range(1,largo):
        crecimiento = ((financialData["TotalRevenue"][-i]-financialData["TotalRevenue"][-i-1])/financialData["TotalRevenue"][-i-1])*100
        #print(crecimiento) #UTIL#UTIL#UTIL#UTIL
        revenueGrowth += crecimiento
      revenueGrowth = revenueGrowth/(largo-1) #Promedio de crecimiento en los ultimos años
      #print("\nRevenue Growth:"+str(revenueGrowth))  #UTIL#UTIL#UTIL#UTIL

      #Habra que hacer un try except con todos 
      try:
        capex = (cashflow["CapitalExpenditure"].mean())#/millon
      except:
        capex = 0
      try:
        depreciation = (cashflow["depreciation"].mean())#/millon ##OR  financialData["Depreciation"]
      except:
        depreciation = 0
      sales = financialData["TotalRevenue"].mean() #Mantenemos unas ventas promedio
      
      cantidadAniosRegistrados = 5 # Si lo cambio tengo que cambiar todos los range
      sales *= 0.8 #este lo puso Dario newnew

      try:
        COGStoSales = financialData["CostOfRevenue"].mean()/sales*100
      except:
        COGStoSales = 0
      try:
        SGandAtoSales = financialData["SellingGeneralAndAdministration"].mean()/sales*100
      except:
        SGandAtoSales = 0
      taxRate = 28/100
      try:
        currentAssetsToSales = financialData["CurrentAssets"].mean()/sales*100
      except:
        currentAssetsToSales = 0
      try:
        currentLiabilitiesToSales = financialData["CurrentLiabilities"].mean()/sales*100
      except:
        currentLiabilitiesToSales = 0

      #ABAJO ESTA COST OF CAPITAL
      terminalGrowthRate = 0 # ES parametro este se ajusta
      revenueGrowth = 0 #parameter, better than 5 years average

      #revenue = revenue_anterior*(1+revenueGrowth/100) #Si es cero, el revenue anterior es el  primer revenue (osea el sales-> TOmo el promedio como esta arriba o pongo devuelta?)
      revenue = []
      for i in range(cantidadAniosRegistrados):
        if i==0:  revenue.append((sales*(1+revenueGrowth/100)))#/millon)
        else: revenue.append(revenue[-1]*(1+revenueGrowth/100))
 
      #currentAssets = revenue*currentAssetsToSales/100
      #currentLiabilities = revenue*currentLiabilitiesToSales/100
      currentAssets = []
      currentLiabilities = []
      try:
        for i in range(cantidadAniosRegistrados):
          if i == 0:
            currentAssets.append((financialData["CurrentAssets"].mean()))#/millon)
            currentLiabilities.append((financialData["CurrentLiabilities"].mean()))#/millon)
          else:
            currentAssets.append((currentAssetsToSales*revenue[i]/100))
            currentLiabilities.append((currentLiabilitiesToSales*revenue[i]/100))
      except:
        currentAssets = [0 for x in range(cantidadAniosRegistrados)]
        currentLiabilities = [0 for x in range(cantidadAniosRegistrados)]
      
      #   2(DOS)
      #revenue lo pusimos arriba
      operatingIncome = [(revenue[i]*(100-COGStoSales-SGandAtoSales)/100) for i in range(cantidadAniosRegistrados)]
      taxes = [(operatingIncome[i]*taxRate/100) for i in range(cantidadAniosRegistrados)]
      nopat = [(operatingIncome[i]-taxes[i]) for x in range(cantidadAniosRegistrados)]

      # Valores estaticos NEWNEW # CAMBIAR TOODOS AC ACCION PRINCIPAL y cambiar el aapl
      risk = 3.75/100
      marketPremium = 6/100
      kd = 6/100
      # Valores dinamicos NEWNEW
      beta = aapl.summary_detail[stocksTotales[acc]]["beta"] #volatilidad con respecto al mercado
      try:
        debt = aapl.balance_sheet().loc[:,"LongTermDebt"][-1] #Aca puse long term debt
      except:
        debt = 0
      marketCap = aapl.summary_detail[stocksTotales[acc]]["marketCap"]
      ke = risk + marketPremium*beta
      costOfCapital = kd*(1-taxRate)*debt/(debt+marketCap)+ke*marketCap/(debt+marketCap) #el tax rate es 28/1000

      #changeInNwc = (currentAssets-currentLiabilities)-(currentAssets_anterior-currentLiabilities_anterior)
      changeInNwc = []
      try:
        currentLiabilitiesAnterior = (financialData["CurrentLiabilities"][-1])#/millon #Aca cambie la media por el ultimo
      except:
        currentLiabilitiesAnterior = 0
      for i in range(cantidadAniosRegistrados):
        if i==0:
          try:
            changeInNwc.append((int((currentAssets[i]-currentLiabilities[i])-(sales-currentLiabilitiesAnterior))))#millon)
          except:
            changeInNwc.append(0)
        else:
          try:
            changeInNwc.append((currentAssets[i]-currentLiabilities[i])-(currentAssets[i-1]-currentLiabilities[i-1]))
          except:
            changeInNwc.append(0)
        
      FCF = [nopat[i]-capex+depreciation-changeInNwc[i] for i in range(cantidadAniosRegistrados)]
      
      terminalValue = [0 for i in range(cantidadAniosRegistrados)]
      terminalValue[-1] = (FCF[-1]*100*(1+(terminalGrowthRate)/100)/(costOfCapital-terminalGrowthRate)) #el numero 10 lo modificamos
      totalCashFlow = [(FCF[i]+terminalValue[i]) for i in range(cantidadAniosRegistrados)]
      presentValueOfFlows = [totalCashFlow[i]/pow((1+costOfCapital/100),i) for i in range(cantidadAniosRegistrados)] # Cambiamos cantidaddeanioosregistrados por i 

      #   3(TRES) Estas no son listas, son valores nada mas.
      enterPriseValue = sum(presentValueOfFlows)#/millon
      try:
        lessCurrentOutstandingDebt = balanceSheet["LongTermDebt"].mean()#/millon 
      except:
        lessCurrentOutstandingDebt = 0
      equityValue = (enterPriseValue -lessCurrentOutstandingDebt)
      try:
        modules = 'defaultKeyStatistics'
        currentSharesOutstanding = int(str(aapl.get_modules(modules)).split("sharesOutstanding")[1].split(":")[1].split(",")[0])
      except:
        continue
      
      equityValuePerShare = equityValue/currentSharesOutstanding  # dividir por 100 parecia lo correcto

      #   4(CUATRO) 
      currentSharePrice = aapl.financial_data[accion]["currentPrice"] 
      discount = (equityValuePerShare-currentSharePrice)/currentSharePrice*100 #

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
print("VALOR INTRINSECO TERMINADO\n-> Codigo finalizado <-")

tiempoFinal= time.time()
print("Tiempo total:" +str(tiempoFinal-tiempoInicial))

