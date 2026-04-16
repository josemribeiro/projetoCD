# ChaçoVirtual

Aplicação desenvolvida nas Unidades Curriculares de Programação Web e Computação Distribuída.

---

### Autores

- Dinis Carraça
- José Ribeiro
- José Feiteira

Classificação: 14.65 (0-20)

### Arquitetura do Projeto

O projeto está dividido em dois serviços principais:

```
project
│
├── db-server
│   ├── src
│   │   ├── private
│   │   ├── Server.py
│   │   └── requirements.txt
│   └── Dockerfile
│
├── web-server
│   ├── src
│   │   ├── static
│   │   ├── templates
│   │   ├── views
│   │   ├── Server.py
│   │   └── requirements.txt
│   └── Dockerfile
│
├── shared-images
├── docker-compose.yml
├── .env.example
└── README.md
```

---

### Requisitos

* Python
* Docker
* Docker Compose

---

### Instalação

```bash
git clone https://github.com/yourusername/projetoCD.git
cd project-name
```

---

### Configuração

O projeto utiliza **variáveis de ambiente** para configuração.

Criar o ficheiro `.env` a partir do exemplo:

```bash
cp .env.example .env
```

Depois editar o ficheiro `.env` com as configurações necessárias.

---

### Variáveis de Ambiente

Exemplo de configuração:

```
DEFAULT_PORT=22349
MQTT_SERVER=your_mqtt_server
MQTT_PORT=1883
MQTT_USER=your_user
MQTT_PASSWORD=your_password

MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_email_app_password
```

---

### Executar com Docker

Para iniciar todos os serviços:

```bash
docker-compose up --build --remove-orphans
```

O sistema ficará disponível nos serviços configurados.


---
English Description
---

# ChaçoVirtual

Application developed in the Web Programming and Distributed Computing course units.

---

### Authors

- Dinis Carrapato
- José Ribeiro
- José Feiteira

Rating: 14.65 (0-20)

### Project Architecture

The project is divided into two main services:

```
project
│
├── db-server
│ ├── src
│ │ ├── private
│ │ ├── Server.py
│ │ └── requirements.txt
│ └── Dockerfile
│
├── web-server
│ ├── src
│ │ ├── static
│ │ ├── templates
│ │ ├── views
│ │ ├── Server.py
│ │ └── requirements.txt
│ └── Dockerfile
│
├── shared-images
├── docker-compose.yml
├── .env.example
└── README.md

```

---

### Requirements

* Python
* Docker
* Docker Compose

---

### Installation

```bash
git clone https://github.com/yourusername/projetoCD.git
cd Project-Name


---

### Configuration

The project uses **environment variables** for configuration.

Create the `.env` file from the example:

```bash
cp .env.example .env

```

Then edit the `.env` file with the necessary settings.

---

### Environment Variables

Example configuration:

``` DEFAULT_PORT=22349
MQTT_SERVER=your_mqtt_server
MQTT_PORT=1883
MQTT_USER=your_user
MQTT_PASSWORD=your_password

MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_email_app_password
```

---

### Running with Docker

To start all services:

```bash
docker-compose up --build --remove-orphans
```

The system will be available in the configured services.
