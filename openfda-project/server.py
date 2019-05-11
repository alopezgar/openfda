import http.client
import http.server
import socketserver
import json

PORT = 8000
socketserver.TCPServer.allow_reuse_address = True

COMPANY_SEARCH = '&search=openfda.manufacturer_name='
DRUG_SEARCH = '&search=active_ingredient='

class testHTTPRequestHandler(http.server.BaseHTTPRequestHandler):

    #Creamos una funcion que establezca conexion con el servidor y obtenga la info pedida
    def establecer_conexion(self,LIMIT = 10):
        conn = http.client.HTTPSConnection('api.fda.gov')
        #Indicamos el limite de datos en la peticion
        conn.request('GET', '/drug/label.json' + '?limit={}'.format(LIMIT))

        #Recibe la informacion y la convierte a string desde JSON
        r1 = conn.getresponse()
        respuesta = r1.read().decode("utf-8")
        conn.close()

        #La informacion está almacenada en 'results'
        json_info = json.loads(respuesta)
        resultados = json_info['results']

        return resultados

    #Creamos una funcion que devuelva el formulario html
    def devolver_formulario(self):
        with open("formulario.html", 'r') as f:
            formulario = f.read()
            return formulario

    #Creamos una funcion a la que le llega la informacion y la convierte en html para enviarla.
    def enviar_info(self,info):
    	mensaje_html = """<html><head><title></title></head>
        <body><ul>"""

    	for i in info:
    	    mensaje_html += "<li>" + i + "</li>"

    	mensaje_html += """</ul></body>
        </html>"""

    	return mensaje_html

    #Creamos la funcion principal que agrupa las funciones anteriores
    def do_GET(self):
        #Dividimos el path para sacar los parámetros
        recursos = self.path.split("?")

        #Valor por defecto del límite de la búsqueda
        LIMIT=10

        #Buscamos los parámetros para ver si han definido un limite
        if len(recursos)>1:
            parametros = recursos[1]
        else:
            parametros= ''
            LIMIT=10

        #Si hay parametros, entonces obtenemos el valor de LIMIT
        if parametros:
            print("Hay parámetros.")
            limite = parametros.split("=")
            if limite[0]=='limit':
                LIMIT= int(limite[1])
        else:
            print("No hay parámetros.")
            #Coge LIMIT = 10, lo hemos definido antes

        #En función del path se va a llevar a cabo una acción u otra
        #Enviamos el formulario
        if self.path == '/':
            print("Enviando formulario.")
            #Mensaje de que todo es correcto
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            formulario = self.devolver_formulario()
            self.wfile.write(bytes(formulario, "utf8"))

        #Si 'searchDrug'está en el path, implementamos otra funcionalidad
        elif 'searchDrug' in self.path:
            print("Buscando medicamentos con el principio activo introducido.")
            #Mensaje de que todo ha funcionado correctamente
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            print("El límite de medicamentos es: ",LIMIT)

            #Dividimos el path por cada =
            #Cogemos el segundo elemento, el principio activo introducido por el usuario
            SEARCH = self.path.split('=')[1]

            #Establecemos conexion con el servidor
            conn = http.client.HTTPSConnection('api.fda.gov')
            #CReamos la URL para la peticion (GET) indicando el farmaco que queremos (SEARCH)
            conn.request("GET", '/drug/label.json' + "?limit={}".format(LIMIT) + DRUG_SEARCH + SEARCH)
            #Obtenemos la respuesta y sacamos la información
            r1 = conn.getresponse()
            respuesta = r1.read()
            json_info = respuesta.decode("utf8")
            resultados = json.loads(json_info)
            drugs = resultados['results']

            #Creamos una lista vacia en la que almacenar los datos que vayamos sacando
            lista_farmacos = []

            #Drugs es un diccionario con la informacion. Cogemos el nombre de cada medicamento si está,y sino ponemos 'Desconocido'
            for elemento in drugs:
                if 'generic_name' in elemento['openfda']:
                    lista_farmacos.append(elemento['openfda']['generic_name'][0])
                else:
                    lista_farmacos.append('Desconocido')

            #Usamos la función creada anteriormente para enviar esta informacion
            info_html = self.enviar_info(lista_farmacos)
            self.wfile.write(bytes(info_html, "utf8"))
            print("Enviando los datos obtenidos.")

        #Ahora, se solicitan las compañias. Usaremos el mismo procedimiento que para obtener los fármacos.
        elif 'searchCompany' in self.path:
            print("Buscando compañías.")
            #Todo ha ido correctamente
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            print("El límite de compañias es: ",LIMIT)

            #Dividimos el path y cogemos el segundo elemento, en este caso el nombre de la compañia
            SEARCH = self.path.split('=')[1]

            #Establecemos conexión con el servidor
            conn = http.client.HTTPSConnection('api.fda.gov')
            #La peticion contiene la compañia que queremos
            conn.request('GET', '/drug/label.json' + '?limit={}'.format(LIMIT) + COMPANY_SEARCH + SEARCH)
            #Llega la resupuesta con la información. La pasamos a String.
            r1 = conn.getresponse()
            respuesta = r1.read()
            json_info = respuesta.decode('utf8')
            resultados = json.loads(json_info)
            info = resultados['results']

            #Creamos una lista vacia para almacenar los datos que obtengamos
            lista_compañias = []

            #Info es el diccionario con los datos.Iteramos sobre él para sacar los nombres de las compñaias.
            for elemento in info:
                if 'manufacturer_name' in elemento['openfda']:
                    lista_compañias.append(elemento['openfda']['manufacturer_name'][0])
                else:
                    lista_compañias.append('Desconocido')

            #Enviamos la informacion usando la funcion definida al principio
            info_html = self.enviar_info(lista_compañias)
            self.wfile.write(bytes(info_html, 'utf8'))
            print("Enviando los datos obtenidos.")

        #EN este caso, 'listCompanies' está en el path, entonces tenemos que devolver una lista con todas las compañias
        elif 'listCompanies' in self.path:
            print("Buscando la lista de compañias. ")
            #Todo ha ido bien
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            print("El límite de compañías es: ",LIMIT)

            #Establecemos conexion con el servidor mediante la funcion creada
            #Devuelve la informacion ('results')
            JSON = self.establecer_conexion(LIMIT)

            #Creamos una lista para almacenar los datos
            compañias = []

            #Iteramos sobre cada elemento de la informacion
            for elemento in JSON:
                if 'manufacturer_name' in elemento['openfda']:
                    compañias.append(elemento['openfda']['manufacturer_name'][0])
                else:
                    compañias.append('Desconocido')

            #Enviamos la informacion al cliente
            info_html = self.enviar_info(compañias)
            self.wfile.write(bytes(info_html, "utf8"))
            print("Enviando los datos obtenidos.")

        #En este caso nos piden la lista de farmacos
        elif 'listDrugs' in self.path:
            print("Buscando la lista de medicamentos.")
            #Todo ha ido bien
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            print("El límite de medicamentos es: ",LIMIT)

            #Igual que en listCompanies, establecemos conexion y
            #obtenemos los datos gracias a la funcion creada al principio
            JSON = self.establecer_conexion(LIMIT)

            #Creamos una lista para almacenar los datos
            farmacos = []

            #Iteramos sobre la informacion y nos quedamos con los nombres
            for elemento in JSON:
                if 'generic_name' in elemento['openfda']:
                    farmacos.append(elemento['openfda']['generic_name'][0])
                else:
                    farmacos.append('Desconocido')

            #Devolvemos la lista de fármacos
            info_html = self.enviar_info(farmacos)
            self.wfile.write(bytes(info_html, "utf8"))
            print("Enviando los datos obtenidos.")

        elif 'listWarnings' in self.path:
            print("Buscando el listado de advertencias.")
            #Todo ha ido correctamente
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            #Establecemos conexion con el servidor y sacamos los datos
            JSON = self.establecer_conexion(LIMIT)

            #CReamos una lista para almacenar los datos
            lista_warnings = []

            #Iteramos sobre la informacion para coger las advertencias
            for elemento in JSON:
                if 'warnings' in elemento:
                    lista_warnings.append(elemento['warnings'][0])
                else:
                    lista_warnings.append('Desconocido')

            #Enviamos la respuesta
            info_html = self.enviar_info(lista_warnings)
            self.wfile.write(bytes(info_html, "utf8"))
            print("Enviando los datos obtenidos.")

        #Extension IV: Redirect y Authentication
        elif 'redirect' in self.path:
            self.send_response(302)
            self.send_header('Location', 'http://localhost:'+str(PORT))
            self.end_headers()

        elif 'secret' in self.path:
            self.send_error(401)
            self.send_header('WWW-Authenticate', 'Basic realm="Mi servidor"')
            self.end_headers()

        #Extension II: Error 404, Not found
        else:
            self.send_error(404)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write("I don't know '{}'.".format(self.path).encode())


Handler = testHTTPRequestHandler
httpd = socketserver.TCPServer(('', PORT), Handler)
print('Serving at port', PORT)

try:
    httpd.serve_forever()
except KeyboardInterrupt:
    print("")
    print("Interrumpido por el usuario")

print("")
print("Servidor parado")
httpd.close()
