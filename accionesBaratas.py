import pandas as pd
import sys
#Se puede agregar para que puedas tomar los primeros n que quieras(10)

#Cargamos el dataframe
try:
  filename = sys.argv[1]
  df = pd.read_csv(filename)
except:
  df = pd.read_csv("ResultsGraficoTorta.csv")

df = df[["Symbol","Sector","Industry","Same Sub-Industry As","Market Capitalization","Price/Book (MRQ)","Price/Earnings (TTM)"]]
df = df.rename(columns={'Price/Book (MRQ)':'PriceToBook',"Price/Earnings (TTM)":"Price/Earnings"})

#Separamos en Price to book y Price Earnings
dfPB = df[df["PriceToBook"]!="--"].sort_values(by="PriceToBook",ascending=True)
dfPE = df[df["Price/Earnings"]!="--"].sort_values(by="Price/Earnings",ascending=True)

### Price to earning ###
#Separamos cada categoria
industry,sector,sameSubIndustry = [],[],[]
industry, sector, sameSubIndustry = [dfPE[col].value_counts().head(10).tolist() for col in ["Industry", "Sector", "Same Sub-Industry As"]]
#Armamos el dataframe
dfPECants = pd.DataFrame({"Industry":dfPE["Industry"].value_counts().head(10).index,"Industry amount":industry,
              "Sector":dfPE["Sector"].value_counts().head(10).index,"Sector amount":sector,
              "Same Sub-Industry As":dfPE["Same Sub-Industry As"].value_counts().head(10).index,"SubIndustry amount":sameSubIndustry})
dfPECants = dfPECants.set_index("Industry")
#Guardamos el dataframe
dfPECants.to_csv("orderedByPriceEarnings.csv")  


### Price to Book ###
#Separamos cada categoria
industry,sector,sameSubIndustry = [],[],[]
industry, sector, sameSubIndustry = [dfPB[col].value_counts().head(10).tolist() for col in ["Industry", "Sector", "Same Sub-Industry As"]]
#Armamos el dataframe
dfPBCants = pd.DataFrame({"Industry":dfPB["Industry"].value_counts().head(10).index,"Industry amount":industry,
              "Sector":dfPB["Same Sub-Industry As"].value_counts().head(10).index,"Sector amount":sector,
              "Same Sub-Industry As":dfPB["Same Sub-Industry As"].value_counts().head(10).index,"SubIndustry amount":sameSubIndustry})
dfPBCants = dfPBCants.set_index("Industry")
#Guardamos el dataframe
dfPBCants.to_csv("orderedByPriceToBook.csv")  