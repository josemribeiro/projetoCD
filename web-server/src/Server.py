#
# Importar as bibliotecas necessárias
from flask import Flask, jsonify, redirect, send_file, request, render_template, session, send_from_directory, url_for , Response
from flask_session import Session
from flask_mail import Mail, Message
from flask_cors import CORS
import paho.mqtt.client as mqtt
import time
import threading
import requests
import logging
import json
import re
import secrets
import os
from itsdangerous import URLSafeTimedSerializer
import secrets
from dotenv import load_dotenv
load_dotenv()

DEFAULT_PORT = int(os.getenv('DEFAULT_PORT',22349))

# Configurações do broker
MQTT_SERVER = os.getenv('MQTT_SERVER','')
MQTT_PORT = int(os.getenv('MQTT_PORT',1883))
MQTT_TOPIC1 = os.getenv('MQTT_TOPIC1','')
MQTT_TOPIC2 = os.getenv('MQTT_TOPIC2','')
MQTT_USER = os.getenv('MQTT_USER','cd')
MQTT_PASSWORD = os.getenv('MQTT_USER','')

mqtt_client = None
mqtt_connected = False
latest_image_endpoints = {}
rest_endpoints = {
    '1': os.getenv('REST_ENDPOINT_1',''),
    '2': os.getenv('REST_ENDPOINT_2','')
}

DEFAULT_HOST_NAME = os.getenv('DEFAULT_HOST_NAME','')
DB_SERVER_URL = os.getenv('DB_SERVER_URL','')

vatRegEx = r"^\d{9}$"
passwordRegEx = r"^\w{3,7}$"
emailRegEx = r"^[a-zA-Z0-9_.+\\-]+@[a-zA-Z0-9\\-]+\.[a-zA-Z0-9.]+$"

#
# Flask application object (app) no contexto do módulo Python currente
#
app = Flask(__name__, static_url_path='/static', static_folder='static')
CORS(app)
app.url_map.strict_slashes = False

# Isto supostamente faz com a cena de guardar as fotografias dos carros funcionar
# Não faço ideia se isto funciona sempre e em todos os computadores

app.config[ 'TEMPLATES_AUTO_RELOAD' ] = True

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = os.getenv('SESSION_TYPE','')

app.config[ 'MAIL_SERVER' ]= os.getenv('MAIL_SERVER','')
app.config[ 'MAIL_PORT' ] = int(os.getenv('MAIL_PORT',1))
app.config[ 'MAIL_USERNAME' ] = os.getenv('MAIL_USERNAME','')
app.config[ 'MAIL_PASSWORD' ] = os.getenv('MAIL_PASSWORD','')
app.config[ 'MAIL_USE_TLS' ] = False
app.config[ 'MAIL_USE_SSL' ] = True

app.config['SECRET_KEY'] = secrets.token_hex(16)

Session(app)
mail = Mail(app)

#
# Ativar o nível de log para debug
#
logging.basicConfig( level=logging.DEBUG )

#
# Adicionar o tratamento das rotas / e /static e /static/
#
# Redirecionar para a página de index (/static/index.html)
#
@app.route('/')
@app.route('/static')
@app.route('/templates')
@app.route('/images')
@app.route('/Proj')
@app.route('/scripts')
@app.route('/external')
@app.route('/leaflet')
@app.route('/jwplayer6')
@app.route('/VTT')
@app.route('/Sprites')

def getRoot():
    logging.debug( f"Route / called..." )
    if 'email' not in session:
        session['email'] = None
    return render_template( "menuInicial.html", code=302 )

@app.route('/favicon.ico')
def getFavicon():
    logging.debug( f"Route /favicon.ico called..." )
    return send_file( "./static/carIcon.png", as_attachment=True, max_age=1 )

@app.route('/isUserLoggedIn', methods=['GET'])
def isUserLoggedIn():
    logging.debug("Checking if user is logged in...")
    if session.get('email') is not None:
        return {'loggedIn': 1}
    return {'loggedIn': 0}

@app.route('/formLogin')
def buildFormLogin():
    logging.debug( f"Route /buildFormLogin called..." )

    return render_template( 'formLoginT.html', vatRegEx=vatRegEx, passwordRegEx=passwordRegEx )

@app.route('/doLogin', methods=(['POST']) )
def doLogin():
    
    logging.debug( f"Route /doLogin called..." )
    found_user = False
    
    email = request.form[ 'email' ]
    logging.debug( f"Email recebido: {email}" )

    password = request.form[ 'passwordName' ]
    logging.debug( f"Password recebida: {password}" )
    
    passworCheck = re.search( passwordRegEx, password)
    logging.debug( f"Check password: {passworCheck}" )

    if not email or "@" not in email:
        logging.debug( "Campo Email inválido" )
        return render_template('dadosInvalidosT.html',errorMessage = "Campo Email inválido" , redirectURL = request.referrer)
    
    session[ 'email'] = email
    responseByDB = requests.get(f"{DB_SERVER_URL}/api/users/active",params={'email': email})
    response = responseByDB.json()
    found_user = int(response['isUserFound'])

    if (passworCheck==False):
        return render_template( 'dadosInvalidosT.html', errorMessage="Formato dos dados inválido", redirectURL=request.referrer )

    elif (checkUser(email, password) == -1):
        return render_template( 'dadosInvalidosT.html', errorMessage="Login Inválido", redirectURL=request.referrer )
    
    elif (found_user == 0):
        return render_template( 'dadosInvalidosT.html', errorMessage="Login não ativo", redirectURL=request.referrer )
    
    elif(found_user == -1):
        return render_template( 'dadosInvalidosT.html', errorMessage="Login não encontrado", redirectURL=request.referrer )
    
    return buildMenuInicial()

#Fazer Logout
@app.route("/doLogout")
def doLogout():
    logging.debug( f"Route /doLogout called..." )
    logging.debug(f"A apagar: {session[ 'email' ]}")
    session[ 'email' ] = None
    
    return redirect( "/" )
    
@app.route('/menuInicial')
def buildMenuInicial():
    logging.debug(f"Route /menuInicial")
    
    return render_template('menuInicial.html')

#Envia o email para confirmar a conta
@app.route('/sendEmailVer')
def sendEmailVer(email, token):
    activation_link = url_for('activateLogin', token=token, _external=True)
    
    senderName = 'NoReplyTester123'
    senderEmail = 'testerdnc123@gmail.com'
    subject = "Ative sua conta"
    body = f"Por favor, clique no link abaixo para ativar sua conta:\n{activation_link}"

    msg = Message( 
        subject=subject, 
        sender=(senderName, senderEmail), 
        recipients=[email] )
    
    msg.body = body

    mail.send(msg)
    logging.debug(f"Email de ativação enviado para {email}")
    
# Rota e função para ativar o login
@app.route('/activate/<token>')
def activateLogin(token):
    try:
        email = s.loads(token, salt= "email-confirm", max_age= 600) #Token expira em 10 minutos
        email = email.strip()
    except Exception as erro:
        logging.error(f"Erro ao validar o token: {erro}")
        return render_template('dadosInvalidosT.html', errorMessage = "Erro ao ativar o login", redirectURL = request.referrer)
    
    logging.info(f"\nEmail recebido para procurar na database: {email}")
    
    body = {"email": email}
    responseByDB = requests.get(f"{DB_SERVER_URL}/api/users/active",params={"email": email})
    response = responseByDB.json()
    if response['isUserFound'] == 0:
        body2 = {"email": email}
        response2ByDB = requests.post(f"{DB_SERVER_URL}/api/users/email/activate",json=body2)
        response2 = response2ByDB.json()
        if int(response2["sucesso"]) == 1:
            logging.debug("Login ativado")
            return buildFormLogin()
    logging.debug("Utilizador não encontrado")
    return buildFormRegisto()

#Form de criar a conta
@app.route('/formRegistoT')
def buildFormRegisto():
    logging.debug( f"Route /formRegistoT called..." )
    responseByDB = requests.get(f'{DB_SERVER_URL}/api/address/districts').json()
    return render_template( 'formRegistoT.html', districts=responseByDB , vatRegEx=vatRegEx, passwordRegEx=passwordRegEx , emailRegEx = emailRegEx )

s = URLSafeTimedSerializer(app.config['SECRET_KEY']) #Para gerar o token para ativação do login

# Rota para remover um anúncio
@app.route('/removerAnuncio', methods=['POST'])
def removerAnuncio():
    logging.debug("Route /removerAnuncio called...")
    
    # Obtém o ID do carro dos parâmetros da requisição
    idCarro = request.args.get('idCarro')
    
    # Validação básica
    if not idCarro:
        return jsonify({'sucesso': 0, 'mensagem': 'ID do carro não fornecido'}), 400
    
    try:
        responseByDB = requests.delete(f'{DB_SERVER_URL}/api/cars/remove/{idCarro}').json()
    
        if responseByDB['sucesso'] == 1:
            return jsonify({'sucesso': 1, 'mensagem': 'Carro removido com sucesso'})
        else:
            return jsonify({
                'sucesso': 0,
                'mensagem': responseByDB['mensagem']
            })
    except Exception as e:
        logging.error(f"Erro ao remover carro: {e}")
        return jsonify({'sucesso': 0, 'mensagem': 'Erro ao comunicar com o servidor'}), 500

@app.route('/apagarConta', methods=['POST'])
def apagarConta():
    logging.debug( f"Route /apagarConta called..." )
    emailConta = request.args['emailConta']

    if not emailConta:
        return jsonify({'sucesso': 0, 'erro': 'Email não fornecido'})

    try:
        body = {"email": emailConta}
        responseByDB  = requests.delete(f"{DB_SERVER_URL}/api/users/delete",json = body)
        response = responseByDB.json()
        if int(response["sucesso"]) == 1:
            session['email'] = None
            logging.debug(f"Conta com email {emailConta} apagada com sucesso.")
        else:
            logging.debug(f"Erro ao apagar conta com email {emailConta}.")
        return jsonify(response)
    except Exception as e:
        logging.error(f"Erro ao apagar conta: {e}")
        return jsonify()

@app.route('/counties')
def getListOfCounties():
    logging.debug( f"Route /getListOfCounties called..." )
    districtID = request.args[ 'idDistrict' ]
    try:
        responseByDB = requests.get(f"{DB_SERVER_URL}/api/address/{districtID}/counties").json()
        return jsonify(responseByDB)
    except OSError as e:
        logging.debug( f"County ID ({districtID}) not found ..." )
        return { "concelhos" : [] }

@app.route('/zipcodes')
def getListOfzipCodes():
    logging.debug( f"Route /getListOfzipCodes called..." )
    districtID = int(request.args[ 'idDistrict' ])
    countyID = int(request.args[ 'idCounty' ]) + 1
    try:
        body = {
                "districtID": districtID,
                "countyID": countyID,
            }
        responseByDB = requests.get(f"{DB_SERVER_URL}/api/district/{districtID}/county/{countyID}/zipcodes",json=body).json()
        return jsonify(responseByDB)
    except OSError as e:
        logging.debug( f"ZIP Codes of (District ID:{districtID}\tCounty ID:{countyID}) not found ..." )
        return jsonify([])

#Guardar os dados na database depois da conta ser criada
@app.route('/doRegisto',  methods=(['POST']) )
def doRegisto():
    logging.debug(f"Route /doRegisto called...")
    
    name = request.form['firstName']
    logging.debug(f"Nome recebido: {name}")
    
    surName = request.form['surName']
    logging.debug(f"Apelido recebibo: {surName}")
    
    tipo = request.form['opcao']
    logging.debug(f"Tipo recebido: {tipo}")
    
    distritoID = request.form['districtName']
    logging.debug(f"ID do Distrito recebido: {distritoID}")

    concelhoID = request.form['countyName']
    logging.debug(f"ID do Concelho recebido: {concelhoID}")

    codPostalID = request.form['zipName']
    logging.debug(f"ID do código-postal recebido: {codPostalID}")

    email = request.form['emailName']
    logging.debug(f"Email recebido: {email}")

    phoneNumber = request.form['phoneName']
    logging.debug(f"Email recebido: {phoneNumber}")
    
    password = request.form['passwordName']
    logging.debug(f"Password recebida: {password}")
    
    passwordCheck = request.form['passwordCheck']
    logging.debug(f"Password recebida para verificação: {passwordCheck}")

    if not name or not name.strip() or not surName or not surName.strip() or tipo not in ["Stand", "Particular"] or not phoneNumber or len(phoneNumber) < 9 or distritoID == "-1" or concelhoID == "-1" or codPostalID == "-1" or not email or "@" not in email:
        logging.debug( "Todos campos necessitam de estar preenchidos!" )
        return render_template('dadosInvalidosT.html',errorMessage = "Todos campos necessitam de estar preenchidos!" , redirectURL = request.referrer)

    response1ByDB = requests.get(f"{DB_SERVER_URL}/api/users/active",params={"email": email}).json()
    response2ByDB = requests.get(f"{DB_SERVER_URL}/api/users/phone/{phoneNumber}").json()
    response3ByDB = requests.get(f"{DB_SERVER_URL}/api/district/{distritoID}/county/{concelhoID}/zipcode/{codPostalID}/address").json()

    if int(response1ByDB['isUserFound']) == 1 or int(response2ByDB['isUserFound']) == 1:
        logging.debug( "Dados registados a outro utilizador!" )
        return render_template("dadosInvalidosT.html", errorMessage = "Utilizador com esses dados já registado", redirectURL = request.referrer)

    chPassword = passwordChecking(password, passwordCheck)
    chData = checkData(name, surName, email)

    if response3ByDB['sucesso'] == 1:
        response3ByDBdata = response3ByDB['data']
        distrito,concelho,codPostal = response3ByDBdata['distrito'] , response3ByDBdata['concelho'] , response3ByDBdata['codPostal']
        logging.debug(f"Morada:\n\t-Distrito: {distrito}\n\t-Concelho: {concelho}\n\t-Código-Postal: {codPostal}")
    else:
        logging.debug( "Erro a obter morada!" )
        return render_template("dadosInvalidosT.html", errorMessage = "Erro a obter morada", redirectURL = request.referrer)
    
    if chPassword == 1 and chData ==1 :
        token = s.dumps(email, salt='email-confirm') # Gera o token
        body = {
            "nome": name,
            "surName": surName,
            "type": tipo,
            "morada": {
                "distrito": distrito,
                "concelho": concelho,
                "codPostal": codPostal
            },
            "email": email,
            "password": password,
            "phoneNumber": phoneNumber,
            "token": token,
            "active": False
        }
        logging.debug(f"A enviar dados ao servidor da base de dados...")
        responseByDB = requests.post(f"{DB_SERVER_URL}/api/users/register", json = body).json()
        if int(responseByDB['doRegisto']) == 1:
            logging.debug(f"Conta criada com sucesso!")
            sendEmailVer(email ,token)
        
        return render_template('redirectT.html', redirectMessage="Obrigado por se registar no Autochaço. Para concluir o processo ative a conta no email", redirectURL= request.referrer)
    else:
        return render_template("dadosInvalidosT.html", errorMessage = "Dados inválidos", redirectURL = request.referrer)

#Form para adicionar um carro
@app.route('/formAddCarro')
def buildFormAddCarro():
    logging.debug(f"Route /formAddCarro...")
    if session.get('email') is None:
        logging.debug(f"User is not logged in...")
        return render_template('formLoginT.html', message="Por favor dê login para colocar chaços à venda!")

    return render_template('formAddCarroT.html')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'} 
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#Guardar as infos do carro na database
@app.route('/doAddCarro', methods=['POST'])
def doAddCarro():
    logging.debug(f"Route /doAddCarro called...")
    email = session['email']

    brand = request.form['marca']
    carModel = request.form['modelo']
    carPrice = request.form['carPrice']
    carYear = request.form['carYear']
    petroleo = request.form['petroleo']
    caixa = request.form['caixa']
    horsePower = request.form['horsePower']
    displacement = request.form['displacement']
    numberKilometers = request.form['numberKilometers']
    description = request.form['description']
    latitude = request.form['latitude']
    longitude = request.form['longitude']

    logging.debug(f"Marca recebida: {brand}")
    logging.debug(f"Modelo recebido: {carModel}")
    logging.debug(f"Preço recebido: {carPrice}")
    logging.debug(f"Ano recebido: {carYear}")
    logging.debug(f"Tipo de combustível recebido: {petroleo}")
    logging.debug(f"Caixa recebida: {caixa}")
    logging.debug(f"Potência recebida: {horsePower}")
    logging.debug(f"Cilindrada recebida: {displacement}")
    logging.debug(f"Número de quilómetros recebido: {numberKilometers}")
    logging.debug(f"Descrição do veículo recebida: {description}")
    logging.debug(f"Latitude recebida: {latitude}")
    logging.debug(f"Longitude recebida: {longitude}")
    logging.debug(f"Request files: {request.files}")

    file = request.files.get('photos')  # caso possa ser vazio, usar get()

    data = {
        "marca": brand,
        "modelo": carModel,
        "ano": carYear,
        "preco": carPrice,
        "combustivel": petroleo,
        "caixa": caixa,
        "numKilometers": numberKilometers,
        "potencia": horsePower,
        "cilindrada": displacement,
        "descricao": description,
        "email": email,
        "latitude": latitude,
        "longitude": longitude,
    }

    files = {}
    if file and file.filename != '':
        files['photos'] = (file.filename, file.stream, file.mimetype)

    responseByDB = requests.post(f"{DB_SERVER_URL}/api/ads/add",data=data,files=files)

    try:
        response = responseByDB.json()
    except Exception as e:
        logging.error(f"Erro ao decodificar JSON da resposta: {e}")
        return render_template("dadosInvalidosT.html", errorMessage="Erro no servidor ao processar o arquivo.", redirectURL=request.referrer)

    if response["sucesso"] == 1:
        logging.debug(f"Carro para venda adicionado pelo utilizador: Email: {email}")
        return render_template('redirectT.html', redirectMessage="Carro adicionado com sucesso.", redirectURL=request.referrer)
    else:
        logging.debug(f"Erro ao adicionar carro pelo utilizador: Email: {email}")
        return render_template("dadosInvalidosT.html", errorMessage="Erro ao adicionar carro.", redirectURL=request.referrer)


@app.route('/meusAnuncios')
def buildFromMeusAnuncios():
    logging.debug("Route /meusAnuncios called... ")
    email = checkSessionEmail()
    
    if email == -1:
        logging.debug(f"User is not logged in...")
        return render_template('formLoginT.html', message="Por favor dê login para editar o seu perfil!")
    
    elif email == 1:
        # Aparecem os anúncios associados ao email da sessão
        data = get_car_data("email", session['email'])
        return render_template('meusAnunciosT.html', carros = data)

#Construtor para a pag de editar o perfil
@app.route('/formEditarPerfil')
def buildFormEditarPerfil():
    logging.debug("Route /formEditarPerfil called... ")
    #Checkar se o email do utilizador está na database
    if(checkSessionEmail() == -1):
        logging.debug(f"User is not logged in...")
        return render_template('formLoginT.html', message="Por favor dê login para editar o seu perfil!")
    
    responseByDB = requests.get(f"{DB_SERVER_URL}/api/address/districts")
    districts = responseByDB.json()

    body = {"email": session['email']}
    responseByDB = requests.post(f"{DB_SERVER_URL}/api/users/email", json = body)
    conta = responseByDB.json()
    
    return render_template('formEditarPerfilT.html', conta = conta , districts = districts , emailRegEx = emailRegEx )

@app.route('/doEditarPerfil', methods=(['POST']) ) 
def doEditarPerfil():
    
    logging.debug("Route /doEditarPerfil called...")
    email = session['email']
    if not email:
        return render_template("dadosInvalidosT.html", errorMessage="Utilizador não autenticado.", redirectURL=request.referrer)

    infoRecebida = json.loads(request.form['infoEditada'])
    infoEditada = dict()
    
    for keysDic , valuesDic in infoRecebida.items():
        if valuesDic != "vazio":
            infoEditada.update({f"{keysDic}": f"{valuesDic}"})
    logging.debug(f"infoEditada: {infoEditada}")

    if not infoEditada :
        return render_template("dadosInvalidosT.html", errorMessage="Nenhum campo foi selecionado!", redirectURL=request.referrer)
    
    body = {
            "email": email,
            "novosDados": infoEditada,
            "subType": 'doEditProfile'
        }
    
    responseByDB = requests.put(f"{DB_SERVER_URL}/api/users/editprofile", json = body)
    response = responseByDB.json()

    if response["sucesso"] == 1:
        if "emailE" in infoEditada:
            session["email"] = infoEditada["emailE"]
        logging.debug("Dados alterados com sucesso.")
        return render_template('redirectT.html', redirectMessage="Dados alterados com sucesso", redirectURL=request.referrer)
    else:
        return render_template("dadosInvalidosT.html", errorMessage=response.get("erro", "Erro ao editar perfil"), redirectURL=request.referrer)

# Função para verificar se o email da sessão atual existe na database / Se existe de todo
def checkSessionEmail():
    logging.debug(f"Emai de sessão: {session.get('email')}")
    responseByDB = requests.get(f"{DB_SERVER_URL}/api/users/active",params={'email': session.get('email')})
    response = responseByDB.json()
    return int(response['isUserFound'])

# Constroi o formulário de procurar o carro 
@app.route('/formProcuraCarro')
def buildformProcuraCarro():

    return render_template('formProcura.html')

# Função para procurar os carros na database
@app.route('/doProcuraCarro', methods=(['POST']))
def doProcuraCarro():
    escolha = request.form['opcao']
    logging.debug(f"Escolha recebida: {escolha}")

    # Se o texto de procura estiver preenchido ele usa-o, senão é usado o select
    if request.form['textoProcurar'] != "":
        nome = request.form['textoProcurar']
    else:
        nome = request.form['selectProcura']

    logging.debug(f"Texto a procurar: {nome}")

    body = {"nome": nome,"escolha": escolha}
    responseByDB = requests.post(f"{DB_SERVER_URL}/api/ads/search", json = body)
    response = responseByDB.json()

    if response["sucesso"] == 1:
        return render_template("infoCarro.html", carros = response["data"])
    else:
        return render_template("dadosInvalidosT.html", errorMessage="Carro não encontrado", redirectURL=request.referrer)

#Verificar se um utilizador existe
def checkUser(email, password):
    logging.debug("Checking login...")
    body = {"data": {
                "email": email,
                "password": password
            }
        }
    responseByDB = requests.post(f"{DB_SERVER_URL}/api/auth/login", json = body)
    response = responseByDB.json()

    if int(response['isAccOnDB']) == 1:
        logging.debug(f"Utilizador existente na database...")
        return 1
    else:
        logging.debug(f"Dados de login inválidos...")
        return -1

def checkData(nome, apelido, email):
    
    if (nome == " ") or nome.isdigit():
        return -1
    
    if (apelido == " ") or apelido.isdigit():
        return -1
    
    if (email == " ") or ('@' not in email):
        return -1
    
    return 1
        
#Verificar se as passwords quando se cria uma conta
def passwordChecking(passwordOriginal, passwordCheck):
    if (passwordOriginal != passwordCheck):
        return -1
    else:
        return 1
    
# Rota para o javascript poder acessar a base de dados na pasta private
@app.route('/api/logins', methods=['POST'])
def isLoginValid():
    logging.debug(f"Route /api/logins called")
    data = request.get_json()
    emailValue = data['emailValue']
    numTelemovel = data['numTelemovel']
    passwordValue = data['passwordValue']
    subTipoOp = data['tipoOp']

    body = {"data": {
                "email": emailValue,
                "numTelemovel": numTelemovel,
                "password": passwordValue,
            }
        }
    
    responseByDB = requests.post(f"{DB_SERVER_URL}/api/auth/validate/{subTipoOp}", json = body).json()
    return jsonify(responseByDB)

# Rota para o javascript poder acessar a base de dados na pasta private
@app.route('/api/car-list', methods=['GET'])
def getListOfBrands():
    logging.debug(f"Rota /api/car-list chamada")
    try:
        responseByDB = requests.get(f"{DB_SERVER_URL}/api/cars").json()
        return jsonify(responseByDB)
    except Exception as e:
        logging.debug("Não foi possível carregar a lista de marcas...")
        return jsonify([])

def getIndexMarca(marca):
    responseByDB = requests.get(f"{DB_SERVER_URL}/api/cars/index/{marca}")
    response = responseByDB.json()
    return int(response['brandIndex'])
    
@app.route('/api/car-list-models')
def getListOfModels():
    marcaSelecionadaString = request.args['marcaSelecionada']
    marcaSelecionada = getIndexMarca(marcaSelecionadaString)

    if marcaSelecionada == -1:
        logging.debug("Não foi possível encontrar a marca " + marcaSelecionadaString + "...")
        return jsonify([])

    logging.debug(f"Rota /api/car-list-models?" + str(marcaSelecionada) + " chamada")
    responseByDB = requests.get(f"{DB_SERVER_URL}/api/cars/{marcaSelecionada}/models")
    response = responseByDB.json()
    return response

# Retorna a lista com todos os carros que partilham um certo atributo
def get_car_data(atributo, texto):
    body = {"atributo": atributo , "texto" : texto}
    responseByDB = requests.post(f"{DB_SERVER_URL}/api/ads/shared-attributes",json=body)
    return responseByDB.json()

@app.route('/api/anuncios')
def get_anuncios():
    responseByDB = requests.get(f"{DB_SERVER_URL}/api/ads")
    response = responseByDB.json()
    
    return jsonify(response)

@app.route("/dashboard-cameras")
def buildCameraVigi():
    responseByDB = requests.get(f"{DB_SERVER_URL}/api/ads")
    response = responseByDB.json()
    carros = response.get('carros')
    neededInfoFromDB = list()
    
    # Lista de todos os anúncios com camara
    for i in range(len(carros)):
        neededInfoFromDB.append({
            "addNumber" : i,
            "marca" : carros[i].get("marca"),
            "modelo" : carros[i].get("modelo")
        })
    return render_template('camaraVigi.html' , carros = neededInfoFromDB)

# Obter as imagens por MQTT 
@app.route("/api/camera/<camera_id>/image")
def getCameraImageByMQTT(camera_id):
    logging.debug(f"Requesting MQTT image for camera {camera_id}")
    logging.debug(f"Available endpoints: {latest_image_endpoints}")
    
    # Camera Id inválido leva a que a camara não seja detetada
    if camera_id not in latest_image_endpoints:
        logging.warning(f"Camera {camera_id} endpoint not found in MQTT data")
        # Não retorna imagem
        return Response(
            b'', 
            mimetype='image/png', 
            status=404,
            headers={'Access-Control-Allow-Origin': '*'}
        )
    
    endpoint = latest_image_endpoints[camera_id]
    logging.debug(f"Using MQTT endpoint for camera {camera_id}: {endpoint}")
    
    # Buscar as imagens 
    try:
        response = requests.get(
            endpoint,
            timeout=10,
            verify=False,
            headers={'User-Agent': 'Camera-Dashboard/1.0'}
        )
        
        # As imagens foram recebidas
        if response.status_code == 200 and len(response.content) > 100:
            return Response(
                response.content,
                mimetype='image/jpeg',
                headers={
                    'Cache-Control': 'no-cache, no-store, must-revalidate',
                    'Pragma': 'no-cache',
                    'Expires': '0',
                    'Access-Control-Allow-Origin': '*'
                }
            )
        # Erro a receber as imagens
        else:
            logging.warning(f"Resposta inválida da câmara nº{camera_id}: status={response.status_code}")
    
    # Erro ao ir buscar as imagens
    except Exception as e:
        logging.error(f"Erro ao obter imagem da câmara nº{camera_id} através de MQTT: {e}")
    
    # No caso de timeout a imagem retornada é vazia
    return Response(
        b'',
        mimetype='image/png',
        status=503,
        headers={'Access-Control-Allow-Origin': '*'}
    )

# Obter as iamgens por Rest 
@app.route("/api/camera/<camera_id>/image-rest")
def getCameraImageByREST(camera_id):
    
    # Busca a key pedida pelo Cors
    api_key = request.headers.get('x-custom-key')
    if not api_key:
        return jsonify({'error': 'Chave necessária'}), 401
    
    if camera_id not in rest_endpoints:
        return jsonify({'error': 'Câmara nao encontrada'}), 404
    
    # Consegue o endPoint 
    endpoint = rest_endpoints[camera_id]
    logging.debug(f"Pedido REST para a câmara Nº{camera_id} no URL com a chave *{api_key}*: {endpoint}")
    
    try:
        # Para usar com o Cors
        headers = {
            "x-custom-key": api_key,
            'User-Agent': 'ChaçoVirtual'
        }
        
        # Envia o pedido para a camara
        response = requests.get(endpoint,headers=headers,timeout=10,verify=False)
         
        # Imagem recebida válida
        if response.status_code == 200 and len(response.content) > 100:
            # Retorna a imagem ao utilizador
            return Response(
                response.content, 
                mimetype='image/jpeg',
                headers={
                    'Cache-Control': 'no-cache, no-store, must-revalidate',
                    'Pragma': 'no-cache',
                    'Expires': '0',
                    'Access-Control-Allow-Origin': '*'
                }
            )
        else:
            logging.warning(f"REST: Resposta inválida do endpoint da câmara nº{camera_id}: status={response.status_code}")
            
    except Exception as e:
        logging.error(f"REST: Erro ao obter imagem da câmara nº{camera_id}: {e}")
    
    return jsonify({'error': 'Câmara não se encontra disponivel'}), 503

# Funções MQTT

# Subscrever os tópicos, neste caso a camara 1 e 2
def on_connect(client, userdata, flags, rc):
    global mqtt_connected
    if rc == 0:
        mqtt_connected = True
        client.subscribe(MQTT_TOPIC1)
        client.subscribe(MQTT_TOPIC2)
    else:
        mqtt_connected = False


@app.route("/api/camera/on-disconnect-endpoint", methods = ["POST"])
def on_disconnect_endpoint():
    global mqtt_connected
    mqtt_connected = False
    logging.debug(f"MQTT desconectado.")
    return jsonify({"status" : "disconnected"})

def on_disconnect(client, userdata, rc):
    global mqtt_connected
    mqtt_connected = False

# Recebe os endpoints da camara selecionada
def on_message(client, userdata, msg):
    global latest_image_endpoints
    topic = msg.topic
    payload = msg.payload.decode()
    logging.debug(f"{topic} -> {payload}")

    try:
        data = json.loads(payload)
        if 'endPoint' in data:
            if topic == "/stream1":
                camera_id = '1'
            elif topic == "/stream2":
                camera_id = '2'
            else:
                logging.warning(f"Topic desconhecido: {topic}")
                return
            
            # Atualiza o endpoint para o mais recente 
            latest_image_endpoints[camera_id] = data['endPoint']
            logging.info(f"Novo endpoint do {camera_id} endpoint: {data['endPoint']}")
            
    except json.JSONDecodeError as e:
        logging.debug("Erro ao descodificar JSON")
    except Exception as e:
        logging.error(f"Erri ao processar mensagem MQTT: {e}")

# Definir o Cliente Mqtt
def setup_mqtt_client():
    global mqtt_client
    
    mqtt_client = mqtt.Client(client_id="cliente-python-123",protocol=mqtt.MQTTv311)
    mqtt_client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_disconnect = on_disconnect
    mqtt_client.on_message = on_message
    
    return mqtt_client

# Mantem o cliente conectado ao Mqtt enquanto a ligação for pedida
def mqtt_client_loop():
    global mqtt_client, mqtt_connected
    while True:
        try:
            if not mqtt_connected:
                mqtt_client = setup_mqtt_client()
                logging.info(f"A conectar ao MQTT broker no {MQTT_SERVER}:{MQTT_PORT} ...")
                mqtt_client.connect(MQTT_SERVER, MQTT_PORT, keepalive=60)
                mqtt_client.loop_start()
                time.sleep(2)
            time.sleep(10)
            
        except Exception as e:
            logging.debug("Erro ao conectar: %s", e)
            mqtt_connected = False
            time.sleep(5)

@app.route("/api/mqtt/status")
def mqtt_status():
    return jsonify({
        'connected': mqtt_connected,
        'endpoints': latest_image_endpoints
    })

# Suporte CORS
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,x-custom-key')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

if __name__ == '__main__':
#    mqtt_thread = threading.Thread(target=mqtt_client_loop, daemon=True)
#    mqtt_thread.start()
    app.run(host="0.0.0.0", port=80, debug=True)