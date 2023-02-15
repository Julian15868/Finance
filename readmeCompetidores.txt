insertarAdelante(lista,elemento) : Recibe una lista y un elemento, si en la lista ya se encontraba este, lo borra para ingresarlo al principio, y si no estaba lo ingresa al principio. Es importante en el contexto de nuestro programa de competidores para dejar al stockPrincipal siempre al principio de la lista.

buscarPrimeraTandaCompetencia(accion): Busca la primera tanda de competidores de la accion que ingresamos. Se utiliza esta para buscar la primera tanda y no las siguientes porque: Es mas variada y acertada en la primera busqueda de la competencia que la funcion "buscarCompetencia(accion,mercados)", pero no es muy buena para buscar las siguientes tandas, tiene poca variacion.

buscarCompetencia(accion,mercados): Busca las tandas siguientes de competidores de la accion, y ponemos los mercados que queremos que busque nuestra funcion.

puntajesStocks(stocksTotales): Teniendo en cuenta el sector e industria de la accion Principal le vamos sumando 1("uno") al puntaje del stock competidor por cada coincidencia.

strToNum(string): Se recibe la informacion del valor del marketCap(u otros) como string, es decir del estilo 1T(un trillon), 1B(un billon).. lo pasamos a numero para poder comparar cada stock luego.

separarMayus(palabra): Recibe un string del estilo "ReturnOnAssets" y lo convertimos en "Return On Assets". Usamos esta funcion para clarificar los nombres de las columnas en un dataframe.

marketCapFunc(stock,ultimosNanios): Recibe un stock y una cantidad n de años y devuelve una lista del marketCap de los ultimos n años.