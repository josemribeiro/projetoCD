import { 
  CheckAccount,
  emailRegEx
} from "./forms.js";

export function resetBordersInputReg() {
  document.getElementById("firstName").style.border = "";
  document.getElementById("surName").style.border = "";
  document.getElementById("district").style.border = "";
  document.getElementById("county").style.border = "";
  document.getElementById("zip").style.border = "";
  document.getElementById("county").style.border = "";
  document.getElementById("emailID").style.border = "";
  document.getElementById("passwordID").style.border = "";
  document.getElementById("passwordIdRpt").style.border = "";
}

export async function validarFormRegisto(event) {
  if (event) event.preventDefault();

  let firstName = document.getElementById("firstName");
  if (firstName.value.trim() === "" || firstName.value.length < 3) {
    alert("O nome é obrigatório!");
    document.getElementById("firstName").style.border = "2px solid red";
    return false;
  }

  let surName = document.getElementById("surName");
  if (surName.value.trim() === "" || surName.value.length < 3) {
    alert("O apelido é obrigatório!");
    document.getElementById("surName").style.border = "2px solid red";
    return false;
  }

  let opcao = document.querySelector("input[name='opcao']:checked");
  if (!opcao) {
    alert("Por favor, selecione o tipo (Stand ou Particular)!");
    return false;
  }

  let district = document.getElementById("district");
  if (district.value === "-1") {
    alert("Por favor, selecione um distrito!");
    document.getElementById("district").style.border = "2px solid red";
    return false;
  }

  let county = document.getElementById("county");
  if (county.disabled || county.value === "-1") {
    alert("Por favor, selecione um concelho!");
    document.getElementById("county").style.border = "2px solid red";
    return false;
  }

  let zip = document.getElementById("zip");
  if (zip.disabled || zip.value === "-1") {
    alert("Por favor, selecione um código postal!");
    document.getElementById("zip").style.border = "2px solid red";
    return false;
  }

  let email = document.getElementById("emailID");
  if (!emailRegEx.test(email.value)) {
    alert("Por favor, insira um email válido!");
    document.getElementById("emailID").style.border = "2px solid red";
    return false;
  }
  else {
    let isEmailValid = await CheckAccount(email.value,null,null,1);
    if(isEmailValid) {
      alert("Email já em uso por outro utilizador!");
      document.getElementById("emailID").style.border = "2px solid red";
      return false;
    }
  }

  let phone = document.getElementById("phoneID");
  if (phone.value.length < 9) {
    alert("O número de telemóvel deve conter pelo menos 9 números!");
    document.getElementById("phoneID").style.border = "2px solid red";
    return false;
  }
  else {
    let isPhoneValid = await CheckAccount(null,null,phone.value,3);
    if(isPhoneValid) {
      alert("O número de telemóvel já em uso por outro utilizador!");
      document.getElementById("phoneID").style.border = "2px solid red";
      return false;
    }
  }

  let password = document.getElementById("passwordID");
  let confirmPassword = document.getElementById("passwordIdRpt");
  if (password.value !== confirmPassword.value) {
    alert("As palavras-chave não coincidem!");
    document.getElementById("passwordID").style.border = "2px solid red";
    document.getElementById("passwordIdRpt").style.border = "2px solid red";
    return false;
  }

  // Submit the form if everything is valid
  document.getElementById("formRT").submit();
  return true;
}

export function SelectDistrictChange() {
  let districtID = document.getElementById("district").value;
  if (districtID == -1) {
    document.getElementById("county").disabled = false;
    return;
  }
  xmlHttp = GetXmlHttpObject();
  xmlHttp.open("GET", "/counties?idDistrict=" + districtID, true);
  xmlHttp.onreadystatechange = SelectDistrictChangeHandleReply;
  xmlHttp.send(null);
}

function SelectDistrictChangeHandleReply() {
  if (xmlHttp.readyState === 4) {
    let countySelect = document.getElementById("county");
    countySelect.options.length = 0;
    countySelect.disabled = false;

    let counties = JSON.parse(xmlHttp.responseText);

    for (let i = 0; i < counties.length; i++) {
      let currentCounty = counties[i];
      let value = currentCounty.ID;
      let option = currentCounty.Valor;

      try {
        countySelect.add(new Option("", value), null);
      } catch (e) {
        countySelect.add(new Option("", value));
      }

      countySelect.options[i].innerHTML = option;
    }
  }
}

export function SelectCountyChange() {
  let countyID = document.getElementById("county").value;
  let districtID = document.getElementById("district").value;
  if (countyID == -1) {
    document.getElementById("county").disabled = true;
    return; //Nenhum concelho foi selecionado
  }
  xmlHttp = GetXmlHttpObject();
  xmlHttp.open(
    "GET",
    "/zipcodes?idDistrict=" + districtID + "&idCounty=" + countyID,
    true
  );
  xmlHttp.onreadystatechange = SelectCountyCodeChangeHandleReply;
  xmlHttp.send(null);
}

function SelectCountyCodeChangeHandleReply() {
  if (xmlHttp.readyState === 4) {
    let zipcodeSelect = document.getElementById("zip");
    zipcodeSelect.options.length = 0;
    zipcodeSelect.disabled = false;

    let zipcodes = JSON.parse(xmlHttp.responseText);

    for (let i = 0; i < zipcodes.length; i++) {
      let currentZipCode = zipcodes[i];
      let value = currentZipCode.ID;
      let option = currentZipCode.Valor;

      try {
        zipcodeSelect.add(new Option("", value), null);
      } catch (e) {
        zipcodeSelect.add(new Option("", value));
      }

      zipcodeSelect.options[i].innerHTML = option;
    }
  }
}
