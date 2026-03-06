# Importar as bibliotecas necessárias
from flask import Flask, jsonify ,request , send_from_directory
import json
import logging
import json
import os
import threading
import time
import random

app = Flask(__name__)
logging.basicConfig( level=logging.DEBUG )
DEFAULT_PORT = 22349

project_root = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(project_root, 'static', 'images')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config[ 'TEMPLATES_AUTO_RELOAD' ] = True
app.config["SESSION_PERMANENT"] = False

def loadData(fName):
    try:
        with open( fName, encoding='utf-8') as f:
            data = json.load(f)
        f.close()
        return data
    except Exception as e:
        logging.debug(f"Não foi possível carregar os dados do {fName}...")
        return json.dumps({})

def loadDataConcelho(fName,districtID):
    logging.debug( f"Loading data from {fName}..." )
    data = list()
    counter = 0
    try:
        with open(fName, encoding='utf-8') as f:
            logging.debug( f"Loading data from {fName}..." )
            dados = f.readlines()
            for linha in dados:
                linha.strip()
                linha = linha.split(";")
                if (int(linha[0]) == int(districtID)):
                    concelho = f"{linha[2]}"
                    if not any(concelho == item['Valor'] for item in data):
                        data.append({"ID": counter, "Valor": concelho})
                        counter += 1
        f.close()
        return data
    except Exception as e:
        logging.debug("Erro a extrair os concelhos do distrito...")
        return json.dumps({})
    

#Função auxiliar que retorna o nome do distrito, concelho e código postal em vez do seu ID
def getMorada(distritoID,concelhoID,cpID):
    logging.debug("A obter os nome do distrito,concelho e código-postal através dos seus respetivos ID's.")
    dataDistritos = loadData("./private/cp-districts.json")
    dataConcelhos = loadDataConcelho("./private/concelhos-utf8.txt",distritoID)
    dataCP = loadDataCP("./private/cp-utf8.txt",distritoID,int(concelhoID) + 1)
    for distritos in dataDistritos:
        if distritos['ID'] == distritoID:
            distritoNome =  distritos['Valor'].strip()

    for concelhos in dataConcelhos:
        if int(concelhos['ID']) == int(concelhoID) :
            concelhoNome = concelhos['Valor'].strip()

    for cps in dataCP:
        if int(cps['ID']) == int(cpID):
            cpNome = cps['Valor']

    return distritoNome,concelhoNome,cpNome

def loadDataCP(fName,districtID,countyID):
    logging.debug( f"Loading data from {fName}..." )
    data = list()
    counter = 0
    try:
        with open( fName,'r', encoding='utf-8') as f:
            dados = f.readlines()
            for linha in dados:
                linha.strip()
                linha = linha.split(";")
                if int(linha[0]) == int(districtID) and int(linha[1]) == int(countyID):
                    zip_code = f"{linha[14]}-{linha[15]}, {linha[3]}"
                    data.append({"ID": counter, "Valor": zip_code})
                    counter = counter + 1
        f.close()
        return data
    except Exception as e:
        logging.debug("Erro a extrair os concelhos do distrito...")
        return json.dumps({})

#
# Função auxiliar para escrever dados JSON (em formato utf-8) num ficheiro
#
def saveData(fName, data):
    logging.debug( f"Saving data to {fName}..." )

    data_json = json.dumps( data, indent=4)

    with open( fName, "w", encoding='utf-8') as f:
        f.write( data_json )
    f.close()

    return data

# Função para remover logins inativos
# Tentar arranjar para que os logging apareçam só depois dos logs iniciais do servidor
def removeLogins():
    logging.info("Remove Logins functions called...")
    db = loadData('./private/logins.json')
    
    logins = db['logins']
    index = 0
    
    for login in logins:
        if (login['active'] == False):
            logins.pop(index)
            logging.debug(f"Login de indice {index} apagado...")
        index += 1
    
    logging.info(f"Não existem mais logins inativos...")
    
    saveData('./private/logins.json', db)

def findUserByEmail(logins, email):
    return next((login for login in logins if login['email'] == email), None)
    
@app.route("/api/users/phone/<phoneNumber>", methods = ["GET"])
def findAccByPhone(phoneNumber):
    db = loadData("./private/logins.json")
    logins = db['logins']
    for login in logins:
        if login['phoneNumber'] == str(phoneNumber):
            logging.debug("User found by phone number.")
            return json.dumps({"isUserFound": 1}) , 200
                
    logging.debug("User not found by phone number.")
    return json.dumps({"isUserFound": 0}) , 200

def generate_random_id():
    #Gerar um número aleatório de 6 digitos
    return ''.join(str(random.randint(0, 9)) for _ in range(6))

@app.route("/api/ads/add", methods = ["POST"])
def addAnuncioHandler():
    db = loadData('./private/carros.json')
    logins = loadData('./private/logins.json')
    carList = db['carros']
    dados = request.form
    logging.debug(f"request.form: {request.form}")
    email = dados["email"]
    file = request.files["photos"]

    phoneNumber = None
    for user in logins['logins']:
        if user['email'] == email:
            phoneNumber = user['phoneNumber']
            break

    id = generate_random_id()
    for carro in carList:
        if carro['id'] == id:
            id = generate_random_id()
    
    carList.append({
        "marca": dados["marca"],
        "modelo": dados["modelo"],
        "ano": dados["ano"],
        "preco": dados["preco"],
        "combustivel": dados["combustivel"],
        "caixa": dados["caixa"],
        "numKilometers": dados["numKilometers"],
        "potencia": dados["potencia"],
        "cilindrada": dados["cilindrada"],
        "telemovel": phoneNumber,
        "descricao": dados["descricao"],
        "email": email,
        "fotografias": file.filename if file else None,
        "latitude": dados["latitude"],
        "longitude": dados["longitude"],
        "id": id
    })

    try:
        if file:
            logging.debug(f"Saving file: {file.filename}")
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            logging.debug(f"Saving to path: {save_path}")
            file.save(save_path)
        saveData('./private/carros.json', db)
        return {"sucesso": 1}
    except Exception as e:
        logging.error(f"Erro ao salvar arquivo ou dados: {e}")
        return {"sucesso": 0}
    
@app.route("/api/users/email",methods = ['POST'])
def findAccByEmail():
    db = loadData('./private/logins.json')
    logins = db['logins']
    dados = request.get_json()
    email = dados["email"]
    login = findUserByEmail(logins, email)
    if login:
        logging.debug(f"A enviar conta com o email {email}")
        return json.dumps(login)
    else:
        return json.dumps([])
    
@app.route("/api/users/editprofile",methods = ['PUT'])
def editProfileRequestHandle():
    logging.debug("Rota /users/editprofile chamada.")
    try:
        db = loadData('./private/logins.json')
        logins = db['logins']
        dados = request.get_json()
        infoEditada = dados['novosDados']
        dbCarros = loadData('./private/carros.json')
        carros = dbCarros['carros']
        userCurrentInfo = findUserByEmail(logins,dados['email'])
    
        # Verifica se o email novo já está em uso
        if "emailE" in infoEditada:
            if userCurrentInfo:
                return json.dumps({"sucesso": 0, "erro": "Email já em uso."})
        
        if "telefoneE" in infoEditada:
            # Confirma se telefone já está em uso por outro utilizador
            for login in logins:
                if login['phoneNumber'] == infoEditada["telefoneE"] and login['email'] != dados['email']:
                    return json.dumps({"sucesso": 0, "erro": "Telefone já em uso."})
        
        if "nomeE" in infoEditada:
            userCurrentInfo['name'] = infoEditada["nomeE"]
        if "apelidoE" in infoEditada:
            userCurrentInfo['surname'] = infoEditada["apelidoE"]
        if "emailE" in infoEditada:
            userCurrentInfo['email'] = infoEditada["emailE"]
        if "distritoE" in infoEditada:
            userCurrentInfo['morada']['distrito'] = infoEditada["distritoE"]
        if "concelhoE" in infoEditada:
            userCurrentInfo['morada']['concelho'] = infoEditada["concelhoE"]
        if "codigoPostalE" in infoEditada:
            userCurrentInfo['morada']['cod-postal'] = infoEditada["codigoPostalE"]
            userCurrentInfo['morada']['distrito'] , userCurrentInfo['morada']['concelho'] , userCurrentInfo['morada']['cod-postal'] = getMorada(userCurrentInfo['morada']['distrito'],userCurrentInfo['morada']['concelho'],userCurrentInfo['morada']['cod-postal'])
        if "telefoneE" in infoEditada:
            userCurrentInfo['phoneNumber'] = infoEditada["telefoneE"]
        # Atualizar carros (email e/ou telefone)
        for carro in carros:
            if carro['email'] == dados['email']:
                if "emailE" in infoEditada:
                    carro['email'] = infoEditada["emailE"]
            if carro['telemovel'] == userCurrentInfo['phoneNumber']:
                if "telefoneE" in infoEditada:
                    carro['telemovel'] = infoEditada["telefoneE"]

        saveData('./private/logins.json', db)
        saveData('./private/carros.json', dbCarros)
        logging.debug("Informações editadas com sucesso.")
        return json.dumps({"sucesso": 1})
    except Exception as e:
        logging.debug("Informações editadas sem sucesso.")
        return json.dumps({"sucesso": 0, "erro": str(e)})

@app.route("/api/auth/login",methods = ['POST'])
def checkUserOnDBbyEmailNPass():
    db = loadData("./private/logins.json")
    logins = db['logins']
    data = request.get_json()
    dados = data["data"]
    email = dados["email"]
    password = dados["password"]
    login = findUserByEmail(logins, email)
    
    if login and login['password'] == password:
        logging.debug("User found by password and login.")
        return json.dumps({"isAccOnDB": 1})
    return json.dumps({"isAccOnDB": 0})

    
@app.route("/api/users/email/activate",methods = ['POST'])
def activateAcc():
    db = loadData("./private/logins.json")
    logins = db['logins']
    dados = request.get_json()
    email = dados["email"]
    try:
        for login in logins:
            if login['email'] == email:
                login['active'] = True
                login['token'] = None
                saveData("./private/logins.json", db)
        return json.dumps({"sucesso": 1})
    except Exception as e:
        return json.dumps({"sucesso": 0, "erro": str(e)})
    
@app.route("/api/users/active",methods = ['GET'])
def checkUserOnDBbyEmail():
    db = loadData("./private/logins.json")
    logins = db['logins']
    email = request.args.get('email')
    login = findUserByEmail(logins,email)
    if login:
        logging.debug("Login active..." if login["active"] else "Login not active...")
        return json.dumps({"isUserFound": 1 if login["active"] else 0})
    return json.dumps({"isUserFound": -1})

@app.route('/api/users/delete',methods = ['DELETE'])
def deleteAccountHandler():
    dados = request.get_json()
    email = dados["email"]
    contaApagada = False
    if not email:
        return json.dumps({"sucesso": 0, "erro": "Email não fornecido"})
    try:
        db = loadData('./private/logins.json')
        logins = db['logins']
        dbCarros = loadData('./private/carros.json')
        carros = dbCarros['carros']

        loginsAtualizados = [login for login in logins if login['email'] != email]
        
        if len(logins) != len(loginsAtualizados):
            contaApagada = True

        # Remover carros associados
        carrosAtualizados = [carro for carro in carros if carro['email'] != email]

        # Guardar alterações se houver
        if contaApagada:
            db['logins'] = loginsAtualizados
            dbCarros['carros'] = carrosAtualizados
            saveData('./private/logins.json', db)
            saveData('./private/carros.json', dbCarros)
            return json.dumps({"sucesso": 1})
        else:
            return json.dumps({"sucesso": 0, "erro": "Conta não encontrada"})

    except Exception as e:
        return json.dumps({"sucesso": 0, "erro": str(e)})

@app.route("/api/auth/validate/<int:tipoOp>", methods=["POST"])
def jsAccValidityRequestsHandle(tipoOp):
    db = loadData("./private/logins.json")
    logins = db['logins']
    req = request.get_json()
    dados = req['data']

    match tipoOp:
        case 1:
            for login in logins:
                if login['email'] == dados['email']:
                    logging.debug("Email encontra-se registado na base de dados.")
                    return jsonify({"isEmailOnDB": 1})
            return jsonify({"isEmailOnDB": 0})

        case 2:
            for login in logins:
                if login['email'] == dados['email'] and login['password'] == dados['password']:
                    logging.debug("Conta encontra-se registada na base de dados.")
                    return jsonify({"isAccOnDB": 1})
            return jsonify({"isAccOnDB": 0})

        case 3:
            for login in logins:
                if login['phoneNumber'] == dados['numTelemovel']:
                    logging.debug("Número encontra-se registado na base de dados.")
                    return jsonify({"isPhoneOnDB": 1})
            return jsonify({"isPhoneOnDB": 0})

    # Caso não bata em nenhum case, devolve um erro:
    return jsonify({"error": "Invalid tipoOp"}), 400

def getCarList():
    try:
        dbCarList = loadData("./private/car-list.json")
        return dbCarList
    except Exception as e:
        logging.debug("Não foi possível carregar a lista de marcas...")
        return json.dumps([])

@app.route("/api/cars", methods = ["GET"])
def getFullListCars():
    return json.dumps(getCarList())

@app.route("/api/cars/index/<brand_name>", methods = ["GET"])
def getIndexMarca(brand_name):
    dbCarList = getCarList()
    
    brand = brand_name
    
    for i in range(len(dbCarList)):
        if(dbCarList[i]['brand'] == brand):
            logging.debug(f"A enviar o index {i} da Marca {brand} na lista dos carros.")
            return json.dumps({'brandIndex': i})
    return json.dumps({'brandIndex': -1})

@app.route("/api/cars/<brandIndex>/models", methods = ["GET"])
def getListModels(brandIndex):
    dbCarList = getCarList()
    index = brandIndex
    logging.debug(f"A enviar a lista de modelos da marca de index {index}.")
    index = int(index)
    return json.dumps(dbCarList[index]['models'])
    
@app.route("/api/address/<districtID>/counties", methods = ["GET"])
def getListOfCounties(districtID):
    logging.debug(f"Rota /address/getCounties/{districtID} chamada.")
    try:
        return json.dumps(loadDataConcelho("./private/concelhos-utf8.txt",districtID))
    except Exception as e:
        logging.debug(f"Não foi possível carregar a lista de concelhos do distrito {districtID}...")
        return json.dumps([])

@app.route('/api/district/<districtID>/county/<countyID>/zipcodes', methods=['GET'])
def getListOfzipCodes(districtID,countyID):
    try:
        data = loadDataCP("./private/cp-utf8.txt",districtID,countyID)
        return json.dumps(data)
    except Exception as e:
        logging.debug(f"Não foi possível carregar a lista de códigos de postal do concelho {countyID} do distrito {districtID}...")
        return json.dumps([])
            
@app.route('/api/address/districts', methods=['GET'])
def getDistricts():
    try:
        return json.dumps(loadData('./private/cp-districts.json' ))
    except Exception as e:
        logging.debug("Não foi possível carregar a lista de distritos...")
        return json.dumps([])
    
@app.route('/api/district/<district_id>/county/<county_id>/zipcode/<zipcode_id>/address', methods=['GET'])
def getMoradaEndPoint(district_id,county_id,zipcode_id):
    districtID = district_id
    countyID = county_id
    zipCodeID = zipcode_id

    try:
        district , county , zipCode = getMorada(districtID , countyID , zipCodeID)
        return json.dumps({"sucesso": 1,
                "data":{"distrito":district,
                        "concelho":county,
                        "codPostal":zipCode
                        }
                })
    except Exception as e:
        logging.debug(f"Não foi possível carregar a morada...")
        return json.dumps([{"sucesso": 0}])
            
@app.route('/api/cars/remove/<int:carID>', methods=['DELETE'])
def deleteAd(carID):
    try:
        # Carrega os dados atuais
        data = loadData('./private/carros.json')
        carros = data['carros']
        logging.debug(f"IDs atuais: {[carro['id'] for carro in carros]}")

        
        # Filtra o carro a ser removido
        carrosAtualizados = [carro for carro in carros if int(carro['id']) != carID]
        
        # Verifica se o carro foi encontrado
        if len(carros) == len(carrosAtualizados):
            return jsonify({'sucesso': 0, 'mensagem': 'Carro não encontrado'}), 404
        
        # Atualiza os dados e salva
        data['carros'] = carrosAtualizados
        if saveData('./private/carros.json', data):
            return jsonify({'sucesso': 1, 'mensagem': 'Carro removido com sucesso'})
        else:
            return jsonify({'sucesso': 0, 'mensagem': 'Erro ao salvar dados'}), 500
    except Exception as e:
        logging.error(f"Erro ao remover carro: {e}")
        return jsonify({'sucesso': 0, 'mensagem': 'Erro interno do servidor'}), 500
    
# Função para procurar os carros na database de anuncios
@app.route("/api/ads/search", methods = ["POST"])
def getCarsFromSearch():
    logging.debug("Rota /ads/search chamada.")
    dados = request.get_json()
    nome = dados["nome"]
    escolha = dados["escolha"]

    db = loadData("./private/carros.json")
    logging.debug("Loading data from ./private/carros.json...")

    carros = db['carros']
    for carro in carros:
        if escolha == "Marca":
            data = getCarsSharedAttributes("marca",nome)
            if carro ['marca'] == nome:
                logging.debug("Carro encontrado na database...")
                return json.dumps({"sucesso": 1 , "data" : data})
        if escolha == "Modelo":
            data = getCarsSharedAttributes("modelo",nome)
            if carro ['modelo'] == nome:
                logging.debug("Modelo encontrado na database...")
                return json.dumps({"sucesso": 1 , "data" : data})
        
        if escolha == "Descricao":
            data = getCarsSharedAttributes("descricao",nome)
            if nome in carro ['descricao'] and len(data)>0:
                logging.debug("Descrição encontrada na database...")
                return json.dumps({"sucesso": 1 , "data" : data})
            
        if escolha == "Combustivel":
            data = getCarsSharedAttributes("combustivel", nome)
            if nome in carro ['combustivel']:
                logging.debug("Combubstivel encontrado na database...")
                return json.dumps({"sucesso": 1 , "data" : data})
            
        if escolha == "Caixa":
            data = getCarsSharedAttributes("caixa", nome)
            if nome in carro ['caixa']:
                logging.debug("Caixa encontrada na database...")
                return json.dumps({"sucesso": 1 , "data" : data})
        
    return json.dumps({"sucesso": 0})

def getCarsSharedAttributes(atributo,texto):
    db = loadData('./private/carros.json')
    carros = db['carros']
    if atributo == "marca":
        carrosUti = [carro for carro in carros if carro['marca'] == texto]
    
    if atributo == "modelo":
        carrosUti = [carro for carro in carros if carro['modelo'] == texto]
        
    if atributo == "descricao":
        # Aumenta a precisão da procura, exclui palavras que sejam comuns em muitos anúncios
        keywords = [word for word in texto.split() if word not in {"e", "com", "carro"}]
        carrosUti = [carro for carro in carros if any (palavra in carro['descricao'] for palavra in keywords)]
    
    if atributo == "combustivel":
        carrosUti = [carro for carro in carros if carro['combustivel'] == texto]
    
    if atributo == "caixa":
        carrosUti = [carro for carro in carros if carro['caixa'] == texto]
    
    if atributo == "email":
        carrosUti = [carro for carro in carros if carro['email'] == texto]

    if atributo == "telefone":
        carrosUti = [carro for carro in carros if carro['telemovel'] == texto]
    
    logging.debug("lista com todos os carros que partilham um certo atributo.")
    return carrosUti

# Retorna a lista com todos os carros que partilham um certo atributo
@app.route("/api/ads/shared-attributes", methods = ["POST"])
def getCarsSharedAttributesEndPoint():
    logging.debug("Rota /anuncios/sharedAttribute chamada.")
    dados = request.get_json()
    atributo = dados['atributo']
    texto = dados['texto']
    return json.dumps(getCarsSharedAttributes(atributo,texto))
    

@app.route("/api/ads", methods = ["GET"])
def getAnuncios():
    logging.debug(f"Rota /api/anuncios chamada")
    logging.debug(f"A aceder a ./private/carros.json")
    return json.dumps(loadData("./private/carros.json"))
 
@app.route("/api/users/register", methods = ["POST"])
def doRegistoHandle():
    requestData = request.get_json()
    db = loadData('./private/logins.json')
    logins = db['logins']
    
    userID = generate_random_id()
    while any(userID == login['id'] for login in logins):
        userID = generate_random_id()

    logins.append({
                'id': userID,
                "name" : requestData['nome'],
                "surname":requestData['surName'],
                "morada": {
                    "distrito" : requestData['morada']['distrito'],
                    "concelho" : requestData['morada']['concelho'],
                    "cod-postal": requestData['morada']['codPostal']
                },
                "email": requestData['email'],
                "phoneNumber": requestData['phoneNumber'],
                "tipo" : requestData['type'],
                "password": requestData['password'],
                "token" : requestData['token'],
                "active" : False,
            })

    saveData("./private/logins.json", db)
    return json.dumps({"doRegisto": 1})

def rotina():
    # Para usarmos uma função dentro de outra
    # Permite que a outra thread corra em simultaneo com o resto do servidor
    def wrapper():
        while True:
            try:
                removeLogins()
            except Exception as e:
                logging.error(f"Erro na rotina: {e}")
            time.sleep(600)
    # Criar a thread para a função correr ao mesmo tempo que o servidor
    # Daemon serve para a thread se fechar sozinha
    thread = threading.Thread(target=wrapper, daemon=True)
    thread.start()
    

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=DEFAULT_PORT)
    rotina()