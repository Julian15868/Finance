# Trabajo de finanzas
#### Intro:
Con este trabajo realizado en Python y Data Studio, lo que se busca es, identificar stocks con posibles crecimientos en el futuro, comparar cada stocks con su competencia dado diferentes metricas competitivas, y ver las transacciones de las propias acciones que hacen las personas que estan dentro de la empresa para estar al tanto de como preven su valor futuro.

------------

#### **Este trabajo se divide en los siguientes tres programas (.py):**

- **Competidores** : Se busca para cada uno de los stocks de una lista, sus competidores, filtrados y ordenados por su market capitalization. Terminada esta busqueda se busca informacion, ratios para compararlos, entre ellos estan: Price/Earnings,  Free cashflow, PTFCF, Profitability ratios, Activity ratios,Liquidity ratios,Debt ratios. Como ultimo se da una descripcion de la empresa.
- ** Insiders** : Para cada uno de los stocks queremos saber que es lo que hacen con sus propias acciones las personas que estan dentro de la empresa, entonces teniendo esta informacion junto con el cargo de aquellos, con las fechas de las transacciones, las cantidades y demas, las comparamos con el precio historico de la accion en una cierta cantidad de dias. Con esto buscamos preveer que pasara en el futuro con la accion. Por ejemplo: Si dado un momento ellos empiezan a comprar una cantidad apreciable de acciones a la vez, piensan que el valor de su stock en el mercado va a subir.
- **accionesBaratas**: Usamos este programa para identificar stocks que estan baratos dado una lista de ellos, y lo hacemos por Sector, Industria y Subindustria, teniendo en cuenta el orden, por un lado por el Price to book y por otro, el Price/Earnings.

------------
#### **A modo de ejemplo mostramos imagenes de cada uno:**
- **Competidores**: 
(Algunas secciones del informe)

![](https://i.ibb.co/8bFgtQN/competidores-foto1.png)

![](https://i.ibb.co/ww3PsJP/competidores-foto2.png)


- **Insiders transactions**

![](https://i.ibb.co/p3ww77L/insider-foto1.png)

- **accionesBaratas**

![](https://i.ibb.co/xSSwH6h/accionesbaratas-foto1.png)

------------

#### **Aqui se encuentra una descripcion de las funciones de cada programa:**

 **Competidores** :
 
- **insertarAdelante(lista,elemento)** : Recibe una lista y un elemento, si en la lista ya se encontraba este, lo borra para ingresarlo al principio, y si no estaba lo ingresa al principio. Es importante en el contexto de nuestro programa de competidores para dejar al stockPrincipal siempre al principio de la lista.

- **buscarPrimeraTandaCompetencia(accion)**: Busca la primera tanda de competidores de la accion que ingresamos. Se utiliza esta para buscar la primera tanda y no las siguientes porque: Es mas variada y acertada en la primera busqueda de la competencia que la funcion "buscarCompetencia(accion,mercados)", pero no es muy buena para buscar las siguientes tandas, tiene poca variacion.

- **buscarCompetencia(accion,mercados)**: Busca las tandas siguientes de competidores de la accion, y ponemos los mercados que queremos que busque nuestra funcion.

- **puntajesStocks(stocksTotales)**: Teniendo en cuenta el sector e industria de la accion Principal le vamos sumando 1("uno") al puntaje del stock competidor por cada coincidencia.

- **strToNum(string)**: Se recibe la informacion del valor del marketCap(u otros) como string, es decir del estilo 1T(un trillon), 1B(un billon).. lo pasamos a numero para poder comparar cada stock luego.

- **separarMayus(palabra)**: Recibe un string del estilo "ReturnOnAssets" y lo convertimos en "Return On Assets". Usamos esta funcion para clarificar los nombres de las columnas en un dataframe.

- **marketCapFunc(stock,ultimosNanios)**: Recibe un stock y una cantidad n de años y devuelve una lista del marketCap de los ultimos n años.

**Insiders:**

-  **insiderTraders(stocksCargados,diasAtras)**: Recibe stock/s y una cantidad n de dias, y genera dos archivos csv de los cuales uno tiene los precios historicos de la accion a analizar en un rango de n dias; Y el otro tiene informacion de los insider traders, de las compras y ventas de sus acciones con sus fechas correspondientes, sus puestos.

-  **masProbable(nombre1,lista)**: Recibe un nombre y una lista de nombres. Y dado este nombre vamos a devolver cual es el nombre mas parecido a el de la lista, si la probabilidad es baja devuelve un "No Match". Comentario aparte: Utilizamos esta funcion debido a que tenemos que triangular informacion de dos paginas, esta informacion la triangulamos con el nombre, mas especificamente queremos a partir del nombre podamos agregar la informacion del puesto de la persona en la empresa.

------------
