var xmlHttp

import { GetXmlHttpObject, removerAnuncio, removerConta } from "./modules/ajax.js"

import {
  cameraState,
  connect,
  connectMQTT,
  connectREST,
  disconnect,
  hideCameraImage,
  updateConnectButton,
  updateStatus,
  updateLastUpdate,
} from "./modules/camaras.js"

import {
  CheckAccount,
  FormLoginValidator,
  validarFormEdit,
  resetBordersInputEdit,
  emailRegEx,
  passwordRegEx,
  nameRegEx,
} from "./modules/forms.js"

import {
  resetBordersInputReg,
  validarFormRegisto,
  SelectDistrictChange,
  SelectCountyChange,
} from "./modules/register.js"

import {
  loadMarcaSelectOptions,
  loadOpcoesPesquisa,
  SelectMarcaChange,
  validarFormAnuncio,
  validarFormPesquisa,
  resetPesquisa,
  CheckCarro,
} from "./modules/anuncio.js"

import { initMapa, resetMap, showMapa } from "./modules/mapas.js"

// Expor funções para uso global (sem tentar reatribuir constantes)
// camaras.js
window.cameraState = cameraState
window.connect = connect
window.connectMQTT = connectMQTT
window.connectREST = connectREST
window.disconnect = disconnect
window.hideCameraImage = hideCameraImage
window.updateConnectButton = updateConnectButton
window.updateStatus = updateStatus
window.updateLastUpdate = updateLastUpdate

//ajax.js
window.GetXmlHttpObject = GetXmlHttpObject
window.removerAnuncio = removerAnuncio
window.removerConta = removerConta

//forms.js
window.FormLoginValidator = FormLoginValidator
window.CheckAccount = CheckAccount
window.resetBordersInputEdit = resetBordersInputEdit
window.validarFormEdit = validarFormEdit
window.emailRegEx = emailRegEx
window.passwordRegEx = passwordRegEx
window.nameRegEx = nameRegEx

//register.js
window.resetBordersInputReg = resetBordersInputReg
window.validarFormRegisto = validarFormRegisto
window.SelectDistrictChange = SelectDistrictChange
window.SelectCountyChange = SelectCountyChange

//anuncio.js
window.loadMarcaSelectOptions = loadMarcaSelectOptions
window.loadOpcoesPesquisa = loadOpcoesPesquisa
window.SelectMarcaChange = SelectMarcaChange
window.validarFormAnuncio = validarFormAnuncio
window.resetPesquisa = resetPesquisa
window.CheckCarro = CheckCarro
window.validarFormPesquisa = validarFormPesquisa

//mapas.js
window.initMapa = initMapa
window.resetMap = resetMap
window.showMapa = showMapa

function showPopup(message) {
  alert(message)
}

function updatedLoggedInState() {
  xmlHttp = GetXmlHttpObject()
  xmlHttp.open("GET", "/isUserLoggedIn", true)
  xmlHttp.onreadystatechange = () => {
    if (xmlHttp.readyState === 4) {
      const isUserLoggedIn = JSON.parse(xmlHttp.responseText)

      // Referências aos elementos
      const loginOp = document.getElementById("loginOp")
      const registarOp = document.getElementById("registarOp")
      const menuPerfil = document.getElementById("menuPerfil")

      if (isUserLoggedIn.loggedIn) {
        // Esconder login e criar conta
        loginOp.style.display = "none"
        registarOp.style.display = "none"

        // Mostrar menu "Meu Perfil"
        menuPerfil.style.display = "block"
      } else {
        // Mostrar login e criar conta
        loginOp.style.display = "block"
        loginOp.href = "/formLogin"
        registarOp.style.display = "block"

        // Esconder menu "Meu Perfil"
        menuPerfil.style.display = "none"
      }
    }
  }
  xmlHttp.send(null)
}

// Inicializar elementos das câmaras quando o DOM estiver pronto
function initializeCameraElements() {
  window.cameraElements = {
    vehicleSelect: document.getElementById("vehicleSelect"),
    connectionType: document.getElementById("connectionType"),
    apiKeyGroup: document.getElementById("apiKeyGroup"),
    apiKey: document.getElementById("apiKey"),
    cameraSelect: document.getElementById("cameraSelect"),
    connectBtn: document.getElementById("connectBtn"),
    cameraImage: document.getElementById("cameraImage"),
    cameraPlaceholder: document.getElementById("cameraPlaceholder"),
    currentVehicle: document.getElementById("currentVehicle"),
    currentCamera: document.getElementById("currentCamera"),
    connectionStatus: document.getElementById("connectionStatus"),
    lastUpdate: document.getElementById("lastUpdate"),
  }

  const elements = window.cameraElements

  // Só adicionar event listeners se os elementos existirem
  if (elements.vehicleSelect) {
    elements.vehicleSelect.addEventListener("change", function () {
      const selectedText = this.options[this.selectedIndex].text
      if (elements.currentVehicle) {
        elements.currentVehicle.textContent = selectedText
      }
    })
  }

  if (elements.connectionType) {
    elements.connectionType.addEventListener("change", function () {
      if (this.value === "rest") {
        elements.apiKeyGroup?.classList.remove("hidden")
      } else {
        elements.apiKeyGroup?.classList.add("hidden")
      }

      if (cameraState.currentConnection && cameraState.currentConnectionType !== this.value) {
        disconnect()
      }
    })
  }

  if (elements.cameraSelect) {
    elements.cameraSelect.addEventListener("change", function () {
      if (elements.currentCamera) {
        elements.currentCamera.textContent = this.value
      }

      if (cameraState.currentConnection) {
        cameraState.currentCamera = this.value
      }
    })
  }

  if (elements.connectBtn) {
    elements.connectBtn.addEventListener("click", () => {
      if (cameraState.currentConnection) {
        disconnect()
      } else {
        connect()
      }
    })
  }

  // Inicialização
  if (elements.currentCamera && elements.cameraSelect) {
    elements.currentCamera.textContent = elements.cameraSelect.value
    cameraState.currentCamera = elements.cameraSelect.value
  }

  if (elements.currentVehicle && elements.vehicleSelect) {
    elements.currentVehicle.textContent = elements.vehicleSelect.options[elements.vehicleSelect.selectedIndex].text
  }
}

document.addEventListener("DOMContentLoaded", loadMarcaSelectOptions)
document.addEventListener("DOMContentLoaded", loadOpcoesPesquisa)
document.addEventListener("DOMContentLoaded", initializeCameraElements)

//main.js
window.showPopup = showPopup
window.updatedLoggedInState = updatedLoggedInState
window.xmlHttp = xmlHttp
window.initializeCameraElements = initializeCameraElements