export var nameRegEx = /^[\d]{9}$/;
export var passwordRegEx = /^[\w]{3,7}$/;
export var emailRegEx = /^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$/;

export async function CheckAccount(
  emailValue,
  passwordValue,
  numTelemovel,
  tipoOp
) {
  try {
    let body = {
      emailValue: emailValue,
      passwordValue: passwordValue,
      numTelemovel: numTelemovel,
      tipoOp: tipoOp
    };
    
    let response = await fetch("/api/logins", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(body)
    });
    
    let data = await response.json();
    
    if (tipoOp == 1) {
      let isEmailValid = false;
      if(data.isEmailOnDB == 1){
        isEmailValid = true;
      }

      return isEmailValid;
    }
    
    if (tipoOp == 2) {
      let isAccValid = false;
      if(data.isAccOnDB == 1) {
        isAccValid = true;
      }
      return isAccValid;
    }
    
    if (tipoOp == 3) {
      let isAccValid = false;
      if(data.isPhoneOnDB == 1) {
        isAccValid = true;
      }
      return isAccValid;
    }
  } 
  
  catch (error) {
    console.error("Error loading JSON:", error);
    return false;
  }
}

export async function FormLoginValidator(event) {
  if (event) event.preventDefault();

  const emailValue = document.getElementById("email").value;
  const passwordValue = document.getElementById("passwordID").value;

  const isValidLogin = await CheckAccount(emailValue, passwordValue, null, 2);

  if (!isValidLogin) {
    alert("Login Inválido");
    return false;
  } else {
    alert("Login efetuado com sucesso!!");
    document.getElementById("formRT").submit();
    return true;
  }
}

export async function validarFormEdit(event) {
  event.preventDefault();

  let nome = document.getElementById("novoNome").value;
  let apelido = document.getElementById("novoSurname").value;
  let email = document.getElementById("novoEmail").value;
  let telefone = document.getElementById("novoPhoneNumber").value;
  let distrito = document.getElementById("district").value;
  let concelho = document.getElementById("county").value;
  let codigoPostal = document.getElementById("zip").value;
  //Campo usado para enviar os campos editados para o Server
  let infoEditada = document.getElementById("infoEditada");
  let infoAenviar = {
    nomeE: "vazio",
    apelidoE: "vazio",
    emailE: "vazio",
    distritoE: "vazio",
    concelhoE: "vazio",
    codigoPostalE: "vazio",
    telefoneE: "vazio",
  };

  //Verificar primeiro se algum atributo foi modificado
  if (
    nome == "" &&
    apelido == "" &&
    email == "" &&
    distrito == "-1" &&
    telefone == ""
  ) {
    alert("Tem de editar pelo menos 1 campo para submeter edição.");
    return false;
  }

  if (nome != "") {
    if (nome.length < 3) {
      document.getElementById("novoNome").style.border = "2px solid red";
      return false;
    } else {
      infoAenviar.nomeE = nome;
    }
  }

  if (apelido != "") {
    if (apelido.length < 3) {
      document.getElementById("novoSurname").style.border = "2px solid red";
      return false;
    } else {
      infoAenviar.apelidoE = apelido;
    }
  }

  if (email != "") {
    if (!emailRegEx.test(email)) {
      document.getElementById("novoEmail").style.border = "2px solid red";
      return false;
    } else {
      //await espera pelo retorno da função CheckAccount para prosseguir
      let isEmailValido = await CheckAccount(email, null, null, 1);
      if (isEmailValido) {
        alert("Email já em uso!");
        document.getElementById("novoEmail").style.border = "2px solid red";
        return false;
      } else {
        infoAenviar.emailE = email;
      }
    }
  }

  if (distrito != "-1") {
    if (document.getElementById("zip").disabled) {
      document.getElementById("district").style.border = "2px solid red";
      document.getElementById("county").style.border = "2px solid red";
      document.getElementById("zip").style.border = "2px solid red";
      return false;
    } else {
      infoAenviar.distritoE = distrito;
      infoAenviar.concelhoE = concelho;
      infoAenviar.codigoPostalE = codigoPostal;
    }
  }

  if (telefone != "") {
    if (!/^\d{9}$/.test(telefone)) {
      alert("Formato de número de telefone inválido!");
      document.getElementById("novoPhoneNumber").style.border = "2px solid red";
      return false;
    } else {
      let isTelefoneValido = await CheckAccount(null, null, telefone, 3);
      if (!isTelefoneValido) {
        infoAenviar.telefoneE = telefone;
      } else {
        alert("Número de telefone já em uso!");
        document.getElementById("novoPhoneNumber").style.border =
          "2px solid red";
        return false;
      }
    }
  }

  if (infoEditada != null) infoEditada.value = JSON.stringify(infoAenviar);
  document.getElementById("formEPT").submit();
  return true;
}

export function resetBordersInputEdit() {
  document.getElementById("novoNome").style.border = "";
  document.getElementById("novoSurname").style.border = "";
  document.getElementById("novoEmail").style.border = "";
  document.getElementById("novoPhoneNumber").style.border = "";
  document.getElementById("district").style.border = "";
  document.getElementById("county").style.border = "";
  document.getElementById("zip").style.border = "";
}
