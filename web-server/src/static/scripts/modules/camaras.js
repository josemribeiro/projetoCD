// Estado compartilhado para as câmaras
export const cameraState = {
  updateInterval: null,
  currentConnection: null,
  currentConnectionType: null,
  currentCamera: null,
  isConnecting: false,
}

export function connect() {
  // Evitar que existam várias conexões ao mesmo tempo
  if (cameraState.isConnecting) {
    return
  }

  const elements = window.cameraElements || {}
  if (!elements.connectionType || !elements.cameraSelect) {
    return
  }

  // Escolhas do utilizador, tipo conexão e num da camara
  const type = elements.connectionType.value
  const camera = elements.cameraSelect.value

  // Atualiza o estado global da camara
  cameraState.isConnecting = true
  cameraState.currentConnectionType = type
  cameraState.currentCamera = camera

  // Limpar os pedidos anteriores 
  if (cameraState.updateInterval) {
    clearInterval(cameraState.updateInterval)
    cameraState.updateInterval = null
  }

  // Escolhe o tipo de conexão
  if (type === "mqtt") {
    connectMQTT()
  } else {
    connectREST()
  }
}

// Conectar o Mqtt
export function connectMQTT() {
  console.log("A ligar MQTT...")

  // Define o intervalo para buscar as imagens 
  cameraState.updateInterval = setInterval(() => {

    // Verifica se se está realmente a tentar conectar através do Mqtt
    if (cameraState.currentConnectionType !== "mqtt") {
      return
    }

    // Rota da camara a utilizar 
    const endpoint = `/api/camera/${cameraState.currentCamera}/image`

    // Busca a imagem 
    fetch(endpoint)
      .then((response) => {
        // Resposta válida por parte do Mqtt
        if (response.ok && response.headers.get("content-type")?.includes("image")) {
          return response.blob()
        }
        throw new Error("Invalid response")
      })

      // blod -> imagem recebida 
      .then((blob) => {
        
        if (cameraState.currentConnectionType !== "mqtt") return

        if (blob.size > 100) {
          const imageUrl = URL.createObjectURL(blob)
          showCameraImage(imageUrl)
          updateLastUpdate()

          // No caso da conexão não ser Mqtt
          if (cameraState.currentConnection !== "mqtt") {
            updateStatus("connected", "MQTT")
            cameraState.currentConnection = "mqtt"
            updateConnectButton(true)
            cameraState.isConnecting = false
          }
        }
      })
      .catch((error) => {
        console.error("Erro no MQTT:", error)
        if (cameraState.currentConnectionType === "mqtt" && cameraState.currentConnection === "mqtt") {
          updateStatus("disconnected", "")
          cameraState.currentConnection = null
          updateConnectButton(false)
          hideCameraImage()
          cameraState.isConnecting = false
        }
      })
  }, 5000)
}

export function connectREST() {
  // Obter os elementos da página e a key
  const elements = window.cameraElements || {}
  const apiKey = elements.apiKey?.value.trim()

  if (!apiKey) {
    alert("Por favor, introduza a chave API")
    cameraState.isConnecting = false
    return
  }

  console.log("A ligar ao servidor através de REST...")

  // Intervalo para buscar as imagens 
  cameraState.updateInterval = setInterval(() => {
    
    // Verifica se se está realmente a tentar conectar através do Rest
    if (cameraState.currentConnectionType !== "rest") {
      console.log("Connection type changed, stopping REST")
      return
    }

    // Rota da camara a utilizar
    const endpoint = `/api/camera/${cameraState.currentCamera}/image-rest`

    // Key do Cors ()
    fetch(endpoint, {
      headers: {
        "x-custom-key": apiKey,
      },
    }) 
      // Verifica se a resposta é uma imagem
      .then((response) => {
        if (response.ok && response.headers.get("content-type")?.includes("image")) {
          return response.blob()
        }
        throw new Error("Invalid response")
      })

      // Mostra a imagem 
      .then((blob) => {
        if (cameraState.currentConnectionType !== "rest") return

        if (blob.size > 100) {
          const imageUrl = URL.createObjectURL(blob)
          showCameraImage(imageUrl)
          updateLastUpdate()

          // Atualiza o estado da ligação 
          if (cameraState.currentConnection !== "rest") {
            updateStatus("connected", "REST")
            cameraState.currentConnection = "rest"
            updateConnectButton(true)
            cameraState.isConnecting = false
          }
        }
      })
      .catch((error) => {
        console.error("Erro no REST:", error)
        if (cameraState.currentConnectionType === "rest" && cameraState.currentConnection === "rest") {
          updateStatus("disconnected", "")
          cameraState.currentConnection = null
          updateConnectButton(false)
          hideCameraImage()
          cameraState.isConnecting = false
        }
      })
  }, 5000)
}

export async function disconnect() {
  console.log("A desconectar de: ", cameraState.currentConnectionType)

  // Para o intervalo 
  if (cameraState.updateInterval) {
    clearInterval(cameraState.updateInterval)
    cameraState.updateInterval = null
  }

  // No caso da ligação ser Mqtt
  if (cameraState.currentConnectionType === "mqtt") {
    let response = await fetch("/api/camera/on-disconnect-endpoint", {method: "POST",})
    let data = await response.json()

    // Confirma que o servidor Mqtt desligou a conexão
    if (data.status === "disconnected") {
      updateStatus("disconnected", "")
      cameraState.currentConnection = null
      cameraState.currentConnectionType = null
      cameraState.currentCamera = null
      cameraState.isConnecting = false
      updateConnectButton(false)
      hideCameraImage()
    }
  }

  // Garante sempre que seja tudo limpo por default
  updateStatus("disconnected", "")
  cameraState.currentConnection = null
  cameraState.currentConnectionType = null
  cameraState.currentCamera = null
  cameraState.isConnecting = false
  updateConnectButton(false)
  hideCameraImage()
}

export function showCameraImage(src) {
  const elements = window.cameraElements || {}
  if (elements.cameraImage && elements.cameraPlaceholder) {
    elements.cameraImage.src = src
    elements.cameraImage.classList.remove("hidden")
    elements.cameraPlaceholder.classList.add("hidden")
  }
}

export function hideCameraImage() {
  const elements = window.cameraElements || {}
  if (elements.cameraImage && elements.cameraPlaceholder) {
    elements.cameraImage.classList.add("hidden")
    elements.cameraPlaceholder.classList.remove("hidden")
  }
}

export function updateConnectButton(connected) {
  const elements = window.cameraElements || {}
  if (elements.connectBtn) {
    if (connected) {
      elements.connectBtn.innerHTML = '<i class="fa-solid fa-stop"></i> Desconectar'
      elements.connectBtn.classList.add("btn-secondary")
      elements.connectBtn.classList.remove("btn-primary")
    } else {
      elements.connectBtn.innerHTML = '<i class="fa-solid fa-play"></i> Conectar'
      elements.connectBtn.classList.add("btn-primary")
      elements.connectBtn.classList.remove("btn-secondary")
    }
  }
}

export function updateStatus(status, type) {
  const elements = window.cameraElements || {}
  if (elements.connectionStatus) {
    const statusElement = elements.connectionStatus
    statusElement.className = `status ${status}`

    if (status === "connected") {
      statusElement.innerHTML = `<span class="status-dot"></span>Conectado (${type})`
    } else {
      statusElement.innerHTML = '<span class="status-dot"></span>Desconectado'
    }
  }
}

export function updateLastUpdate() {
  const elements = window.cameraElements || {}
  if (elements.lastUpdate) {
    elements.lastUpdate.textContent = new Date().toLocaleTimeString("pt-PT")
  }
}
