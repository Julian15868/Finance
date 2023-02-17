from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from selenium.common.exceptions import WebDriverException
import requests
import sys
#
import yfinance as yf
import yahoo_fin.stock_info as si
from yahoo_fin.stock_info import get_data
##
import math, pandas as pd, numpy as np,matplotlib.pyplot as plt
import time, datetime
from statistics import mean
from datetime import date
from IPython.display import clear_output #Borrar output
##
#Configuramos selenium
from selenium.webdriver.chrome.service import Service
service = Service(executable_path="chromedriver.exe")
service.start()
options = webdriver.ChromeOptions()
options.add_argument("--disable-extensions")
options.add_argument("--disable-gpu")
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument('--disable-dev-shm-usage')

#####           Funciones         #####
def insertarAdelante(lista,elemento):
  lista = list(set(lista))
  try:
    lista.remove(elemento)
    lista.insert(0,elemento)
  except:
    lista.insert(0,elemento)
  return lista

#Funcion para sacar la primera tanda de competencia de una accion
def buscarPrimeraTandaCompetencia(accion,accionPrincipal):
  link = "https://www.marketwatch.com/investing/stock/"+accion+"?mod=search_symbol"
  driver = webdriver.Chrome(service=service, options=options)
  driver.get(link)
  page = BeautifulSoup(driver.page_source,"html.parser")
  #HAY UN PROBLEMA CON GUARDAR QUE DEBO SOLUCIONAR
  for busqueda in page.findAll("div",attrs={"class":"element element--table overflow--table Competitors"}):
    guardar = busqueda
  stocks = []
  for i in range(len(str(guardar).split("href"))):
    try:
      stocks.append(str(guardar).split("href")[i].split("stock")[1].split("?")[0].replace("/",""))
    except:
      continue
  stocks = insertarAdelante(stocks,accionPrincipal)
  #print(", ".join(stocks))
  return stocks

# Funcion para asignar una relevancia a los competidores encontrados, nos fijamos si coincide el sector y la industria y asignamos una puntuacion
def puntajesStocks(stocksTotales,industriaPrincipal,sectorPrincipal):
  puntajes = []
  for i in range(len(stocksTotales)):
    puntaje = 0
    accion = yf.Ticker(stocksTotales[i])
    try:
      resumenPerfil = accion.stats()["summaryProfile"]
      try:
        if((resumenPerfil["sector"] == sectorPrincipal) | (resumenPerfil["industry"] == sectorPrincipal)):
          puntaje+=1;
        if((resumenPerfil["industry"] == industriaPrincipal) | (resumenPerfil["sector"] == industriaPrincipal)):
          puntaje+=1;
      except:
          puntaje+=0
    except:
      puntaje+=0
    puntajes.append(puntaje)
  #Muestro los puntajes(Esto  se va a quitar, es util por ahora)
  print("Puntajes:")
  for i in puntajes:
    print(i,end=",")
  return puntajes

# Funcion para sacar la competencia de una accion, dividimos en dos lugares para buscar la competencia asi no hay problemas con las paginas.-> ademas tarda menos de esta forma
def buscarCompetencia(accion,mercados):
  textoClean = []
  for i in range(len(mercados)):
    link = "https://www.marketbeat.com/stocks/"+mercados[i]+"/"+str(accion)+"/competitors-and-alternatives/"
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(link)
    page = BeautifulSoup(driver.page_source,"html")
    # Competencia de la accion
    texto = str(page.findAll("h2",attrs={"class":"h3 mt-0"}))
    texto = texto.split(">")
    try:
      textoClean = texto[1].replace("</h2"," ").replace("vs"," ").replace("."," ").replace("'"," ").replace("and"," ").replace(","," ").replace("    "," ").replace("  "," ") #Limpieza muy manual
      textoClean = textoClean.split(" ")[:-1]
    except:
      continue
  return textoClean

#Hacemos un funcion para cambiar el string que contiene un numero abreviado con un + "B" "M" o "T" a un entero
def strToNum(string):
    string = str(string)
    if "T" in string.upper(): trillon = math.pow(10,18); return float(string.split("T")[0])*trillon
    if "B" in string.upper(): billon = math.pow(10,9); return float(string.split("B")[0])*billon
    if "M" in string.upper(): millon = math.pow(10,6); return float(string.split("M")[0])*millon
    return string

# Para que el dataframe quede prolijo necesitamos una funcion que transforme un texto asi: "returnOnAssets" a "Return On Assets".
def separarMayus(palabra):
  mayus,i = 0,0
  while i < len(palabra):
    if palabra[i].isupper():
      mayus = mayus+1
      if mayus>1:
        palabra = palabra[0:i]+" "+palabra[i:]
        i=i+1
    i=i+1
  return palabra
#Hacemos una funcion para complementar los marketCap que le falta a yahoofinance dentro del ciclo-> la sacamos de companiesmarketcap.com
#Recibe el stock, una cantidad de años y retorna el marketCap para cada uno de esos ultimosNAnios registrados
def marketCapFunc(stock,ultimosNanios):
  link = "https://www.google.com/search?q=companiesmarketcap+"+stock+"+marketcap"
  linkFinal = ""
  driver = webdriver.Chrome(service=service, options=options)
  driver.get(link)
  page = BeautifulSoup(driver.page_source,"html.parser")
  fecMarCap = []
  for i in str(page.findAll("div",attrs={"class":"v7W49e"})).split("href"):
    if "companiesmarketcap" in i and "marketcap/" in i:
      linkFinal= str(i)
      break;
  try:
    linkFinal = linkFinal.split('"')[1]
    driver.get(linkFinal)
    page = BeautifulSoup(driver.page_source,"html.parser")
    fechaMarketCap = (page.find("tbody").text).replace("\n","").split("%") #text solo en find
    for arreglo in fechaMarketCap:
      fecMarCap.append(arreglo.split("$")) 
    largo = len(fecMarCap)
    while(largo < ultimosNanios):
      ultimosNanios = ultimosNanios-1
    fecMarCap = fecMarCap[0:ultimosNanios]
    for i in range(ultimosNanios):
      fecMarCap[i][1] = strToNum(fecMarCap[i][1])
    fecMarCap.sort(key=lambda a: a[0])
  except:
    print("No tiene link")
  return fecMarCap

  # Para que el dataframe quede prolijo necesitamos una funcion que transforme un texto asi: "returnOnAssets" a "Return On Assets".
def separarMayus(palabra):
  mayus, i = 0,0
  while i < len(palabra):
    if palabra[i].isupper():
      mayus = mayus+1
      if mayus>1:
        palabra = palabra[0:i]+" "+palabra[i:]
        i=i+1
    i=i+1
  return palabra

#####         Funciones fin       #####