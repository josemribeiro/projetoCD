export function loadMarcaSelectOptions() {
  let xmlHttp = GetXmlHttpObject();
  xmlHttp.open("GET", "/api/car-list", true);
  xmlHttp.onreadystatechange = function () {
    if (xmlHttp.readyState === 4) {
      let marcas = JSON.parse(xmlHttp.responseText);

      let marcaSelect = document.getElementById("marca");
      let modeloSelect = document.getElementById("modelo");

      marcaSelect.options.length = 0;

      let defaultOption = document.createElement("option");
      let defaultOptionModelo = document.createElement("option");
      defaultOption.text = "Selecione uma Marca";
      defaultOption.value = "-1";
      defaultOptionModelo.text = "Selecione um Modelo";
      defaultOptionModelo.value = "-1";
      modeloSelect.add(defaultOptionModelo);
      marcaSelect.add(defaultOption);

      for (let i = 0; i < marcas.length; i++) {
        let option = document.createElement("option");
        option.text = marcas[i].brand;
        option.value = marcas[i].brand;
        marcaSelect.add(option);
      }
    }
  };
  xmlHttp.send(null);
}

export function SelectMarcaChange() {
  let marcaSeleciada = document.getElementById("marca").value;
  if (marcaSeleciada == -1) {
    document.getElementById("modelo").disabled = true;
    return; //Nenhuma marca foi selecionada
  }
  let xmlHttp = GetXmlHttpObject();
  xmlHttp.open(
    "GET",
    "/api/car-list-models?marcaSelecionada=" + marcaSeleciada,
    true
  );
  xmlHttp.onreadystatechange = function () {
    if (xmlHttp.readyState === 4) {
      let modeloSelect = document.getElementById("modelo");
      modeloSelect.options.length = 0;
      modeloSelect.disabled = false;

      let modelos = JSON.parse(xmlHttp.responseText);
      for (let i = 0; i < modelos.length; i++) {
        let option = document.createElement("option");
        option.text = modelos[i];
        option.value = modelos[i];
        modeloSelect.add(option);
      }
    }
  };
  xmlHttp.send(null);
}

export function validarFormAnuncio(event) {
  if (event) event.preventDefault();

  // Verificar o ano do carro
  let carYear = document.getElementById("carYear");
  if (!(carYear.value < 2002 && carYear.value > 1985)) {
    console.log(carYear.value);
    alert("Carro tem de ser até ao ano 2002");
    carYear.focus();
    return false;
  }

  // Verificar a potência
  let potencia = document.getElementById("horsePower");
  if (potencia.value > 500 || potencia.value < 50) {
    alert("Potência tem de ser entre 50cv e 500cv");
    potencia.focus();
    return false;
  }

  // Verificar a cilindrada
  let cilindrada = document.getElementById("displacement");
  if (cilindrada.value > 3500 || cilindrada.value < 900) {
    alert("Cilindrada tem de ser entre 900cc e 3500cc");
    cilindrada.focus();
    return false;
  }

  // Verificar o preço
  let preco = document.getElementById("carPrice");
  if (preco.value > 1500000) {
    alert("O preço não pode ultrapassar 1500000");
    preco.focus();
    return false;
  }

  // Verificar os quilómetros
  let kms = document.getElementById("numberKilometers");
  if (kms.value > 2000000) {
    alert("Número de quilómetros não pode ser maior do que 2000000");
    kms.focus();
    return false;
  }

  // Se todas as validações passarem, envia o formulário
  document.getElementById("addCarro").submit();
  return true;
}

export function loadOpcoesPesquisa() {
  let radios = document.querySelectorAll("input[name='opcao']");
  let procura = document.getElementById("textoProcurar");
  let selectProcura = document.getElementById("selectProcura");

  let placeholders = {
    Marca: "Introduza a marca do carro",
    Modelo: "Introduza o modelo do carro",
    Descricao: "Introduza uma descrição do carro",
  };

  let opcoesDisponiveis = {
    Combustivel: [
      { opcao: "Gasolina", valor: "Gasolina" },
      { opcao: "Diesel", valor: "Diesel" },
    ],
    Caixa: [
      { opcao: "Manual", valor: "Manual" },
      { opcao: "Automatico", valor: "Automatico" },
    ],
  };

  for (let i = 0; i < radios.length; i++) {
    radios[i].addEventListener("change", function () {
      let radioSelecionado = this.value;

      // Se for selecionado o radio do combustivel ou caixa
      if (opcoesDisponiveis[radioSelecionado]) {
        procura.style.display = "none";
        selectProcura.style.display = "block";

        //Remover as opções previamente carregadas (Se houver)
        selectProcura.innerHTML = "";

        let options = opcoesDisponiveis[radioSelecionado];
        for (let j = 0; j < options.length; j++) {
          let value = options[j].valor;
          let option = options[j].opcao;

          try {
            selectProcura.add(new Option("", value), null);
          } catch (e) {
            selectProcura.add(new Option("", value));
          }

          selectProcura.options[j].innerHTML = option;
        }
      } else {
        procura.style.display = "block";
        selectProcura.style.display = "none";

        procura.placeholder = placeholders[radioSelecionado];
      }
    });
  }
}

export async function validarFormPesquisa(event) {
  if (event) event.preventDefault();

  let radios = document.querySelectorAll("input[name='opcao']");
  let textoProcurar = document.getElementById("textoProcurar");
  let selectProcura = document.getElementById("selectProcura");
  let valorProcura = null;
  let opcaoSelecionada = null;

  // Verificar se algum radio está selecionado
  for (let i = 0; i < radios.length; i++) {
    if (radios[i].checked) {
      opcaoSelecionada = radios[i].value;
      break;
    }
  }

  if (!opcaoSelecionada) {
    alert("Por favor, selecione uma opção de pesquisa.");
    return false;
  }

  // Select de procura está ativo (Caixa ou Combustivel)
  if (selectProcura.style.display == "block") {
    valorProcura = selectProcura.value;
  } else {
    valorProcura = textoProcurar.value.trim();
  }

  if (!valorProcura) {
    alert("Por favor, preencha o campo de pesquisa.");
    textoProcurar.style.border = "2px solid red";
    return false;
  }

  if (opcaoSelecionada == "Marca") {
    let isMarcaValida = await CheckCarro(textoProcurar.value, null, 1);
    if (!isMarcaValida) {
      alert("Não foram encontrados anuncios com essa Marca!");
      textoProcurar.style.border = "2px solid red";
      return false;
    }
  }

  if (opcaoSelecionada == "Modelo") {
    let isModeloValido = await CheckCarro(null, textoProcurar.value, 2);
    if (!isModeloValido) {
      alert("Não foram encontrados anuncios com esse Modelo!");
      textoProcurar.style.border = "2px solid red";
      return false;
    }
  }

  document.getElementById("formPC").submit();
  return true;
}

export async function CheckCarro(marca, modelo, tipoSel) {
  try {
    let response = await fetch("/api/anuncios");
    let data = await response.json();
    let anuncios = data.carros;
    if (tipoSel == 1) {
      let marcaEncontrada = false;
      for (let i = 0; i < anuncios.length; i++) {
        let marcaAtual = anuncios[i].marca;
        if (marcaAtual == marca) {
          marcaEncontrada = true;
          break;
        }
      }
      return marcaEncontrada;
    }
    if (tipoSel == 2) {
      let todosModelos = [];
      let modeloEncontrado = false;
      // Obter Lista de todos os modelos
      for (let i = 0; i < anuncios.length; i++) {
        let anuncioAtual = anuncios[i]; // Objeto da marca atual
        todosModelos.push(anuncioAtual.modelo);
      }
      // Comparar modelo escrito pelo utilizador com lista de modelos
      for (let k = 0; k < todosModelos.length; k++) {
        let modeloAtual = todosModelos[k];
        if (modeloAtual == modelo) {
          modeloEncontrado = true;
          break;
        }
      }
      return modeloEncontrado;
    }
  } catch (error) {
    console.error("Error loading JSON:", error);
    return false;
  }
}


export function resetPesquisa() {
  document.getElementById("textoProcurar").style.border = "";
  document.getElementById("selectProcura").style.border = "";
}