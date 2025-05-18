// Credit goes to Simon Plenderleith.  https://simonplend.com/how-to-use-fetch-to-post-form-data-as-json-to-your-api/

async function postFormDataAsJson({ url, formData }) {
  const plainFormData = Object.fromEntries(formData.entries());
  const formDataJsonString = JSON.stringify(plainFormData);

  const fetchOptions = {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Accept": "application/json"
    },
    body: formDataJsonString,
  };

  const response = await fetch(url, fetchOptions);
  if (!response.ok) {
    const errorMessage = await response.text();
    throw new Error(errorMessage);
  }
  return response.json();
}

async function getDataAsJson(url) {
  const fetchOptions = {
    method: "GET",
    headers: { "Accept": "application/json" }
  };
  const response = await fetch(url, fetchOptions);
  if (!response.ok) {
    const errorMessage = await response.text();
    throw new Error(errorMessage);
  }
  return response.json();
}

async function deleteObject(url) {
  const fetchOptions = { method: "DELETE" };
  const response = await fetch(url, fetchOptions);
  if (!response.ok) {
    const errorMessage = await response.text();
    throw new Error(errorMessage);
  }
  // Refresh list after successful deletion
  listiraamatud();
}

async function downloadRaamat(url, filename) {
  try {
    const res = await fetch(url);
    if (!res.ok) throw new Error(`Download failed: ${res.status}`);
    const blob = await res.blob();
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    link.remove();
  } catch (err) {
    console.error("Download error:", err);
    alert("Raamatu allalaadimine ebaõnnestus");
  }
  // Refresh list after download
  listiraamatud();
}

function handleResponse(form, responseData) {
  const resultElement = document.getElementById("tulemus");
  if (form.id === "frontform") {
    // New book created
    resultElement.innerHTML = responseData.tulemus;
    listiraamatud();
  }
  if (form.id === "otsinguform") {
    // Search results
    let output = `Sõne ${responseData.sone} leiti järgmistest raamatutest:<br/>`;
    for (const tulemus of responseData.tulemused) {
      output += `Raamat ${tulemus.raamatu_id} - ${tulemus.leitud} korda!<br/>`;
    }
    resultElement.innerHTML = output;
  }
}

async function handleFormSubmit(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const url = form.action;
  try {
    const formData = new FormData(form);
    const responseData = await postFormDataAsJson({ url, formData });
    console.log({ responseData });
    handleResponse(form, responseData);
  } catch (error) {
    console.error(error);
  }
}

async function listiraamatud() {
  try {
    const responseData = await getDataAsJson("fetch-books-backend-atfma3ccece9bma5.northeurope-01.azurewebsites.net/raamatud/");
    const resultElement = document.getElementById("raamatud_result");
    resultElement.innerHTML = "";

    for (const filename of responseData.raamatud) {
      const raamatId = filename.endsWith(".txt") ? filename.slice(0, -4) : filename;
      const downloadUrl = `fetch-books-backend-atfma3ccece9bma5.northeurope-01.azurewebsites.net/raamatud/${raamatId}`;
      const deleteUrl = downloadUrl;
      resultElement.innerHTML +=
        `<a href="#" onclick="downloadRaamat('${downloadUrl}', '${raamatId}.txt'); return false;">${raamatId}.txt</a> ` +
        `<a href="#" onclick="deleteObject('${deleteUrl}'); return false;">[kustuta]</a><br>`;
    }
  } catch (err) {
    console.error("Failed to list books:", err);
    document.getElementById("raamatud_result").innerText =
      "Viga raamatute nimekirja laadimisel.";
  }
}
