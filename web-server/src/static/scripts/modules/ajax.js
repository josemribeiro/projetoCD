export function GetXmlHttpObject() {
    try {
      return new ActiveXObject("Msxml2.XMLHTTP");
    } catch(e) {} // Internet Explorer
    try {
      return new ActiveXObject("Microsoft.XMLHTTP");
    } catch(e) {} // Internet Explorer
    try {
      return new XMLHttpRequest();
    } catch(e) {} // Firefox, Opera 8.0+, Safari
    alert("XMLHttpRequest not supported");
    return null;
}

export function removerAnuncio(idCarro) {
  let confirmar = confirm("Tem certeza de que deseja apagar este anúncio?");
  if (!confirmar) return;
  let xmlHttp = GetXmlHttpObject();
  xmlHttp.open(
    "POST",
    "/removerAnuncio?idCarro=" + idCarro,
    true
  );
  xmlHttp.onreadystatechange = function () {
    if (xmlHttp.readyState === 4) {
      let isAnuncioApagado = JSON.parse(xmlHttp.responseText);
      if (isAnuncioApagado.sucesso == 1) {
        alert("Anúncio removido com sucesso!");
        window.location.replace("/meusAnuncios");
      }
      else {
        alert("Erro ao remover o anúncio.\nTente novamente mais tarde.");
    }
    }
  };
  xmlHttp.send(null);
}

export function removerConta(email) {
  let confirmar = confirm("Tem certeza de que deseja apagar a sua conta?");
  if (!confirmar) return;
  let xmlHttp = GetXmlHttpObject();
  xmlHttp.open(
    "POST",
    "/apagarConta?emailConta=" + email,
    true
  );
  xmlHttp.onreadystatechange = function () {
    if (xmlHttp.readyState === 4) {
      let isContaApagada = JSON.parse(xmlHttp.responseText);
      if (isContaApagada.sucesso == 1) {
        alert("Conta removida com sucesso!");
        window.location.replace("/");
      }
      else {
        alert("Erro ao apagar conta.\nTente novamente mais tarde");
    }
    }
  };
  xmlHttp.send(null);
}
