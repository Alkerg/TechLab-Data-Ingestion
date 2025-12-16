async function getEntities() {
  try {
    const r = await fetch("/api/entities");
    const data = await r.json();
    document.getElementById("entities").textContent = JSON.stringify(data, null, 2);
  } catch (e) {
    document.getElementById("entities").textContent = "Error: " + e.message;
  }
}

async function subscribe() {
  const entityId = document.getElementById("entityId").value;
  const entityType = document.getElementById("entityType").value;
  const attrsVal = document.getElementById("attrs").value;
  const endpoint = document.getElementById("endpoint").value;

  if(!entityId || !endpoint) {
      alert("ID y Endpoint son obligatorios");
      return;
  }

  const attrs = attrsVal ? attrsVal.split(",") : [];

  try {
    const r = await fetch("/api/subscribe", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ entityId, entityType, attrs, endpoint })
    });
    const data = await r.json();
    document.getElementById("result").textContent = JSON.stringify(data, null, 2);
  } catch (e) {
    document.getElementById("result").textContent = "Error: " + e.message;
  }
}

async function getSubscriptions() {
    try {
      const r = await fetch("/api/subscriptions");
      const data = await r.json();
      const table = document.getElementById("subscriptions");
      table.innerHTML = "";
      
      if(data.length === 0) {
         table.innerHTML = "<tr><td colspan='3'>No hay suscripciones encontradas</td></tr>";
         return;
      }
      
      data.forEach(sub => {
      const row = `<tr><td>${sub.entityId}</td><td>${sub.entityType}</td><td>${sub.endpoint}</td></tr>`;
      table.innerHTML += row;
      });
    } catch (e) {
      console.error(e);
      alert("Error cargando suscripciones");
    }
}

async function deleteEntity() {
    const id = document.getElementById("deleteEntityId").value;
    if (!id) { alert("Ingresa un ID"); return; }
    
    try {
      const r = await fetch(`/api/entities/${id}`, { method: "DELETE" });
      const data = await r.json();
      const statusElem = document.getElementById("deleteStatus");
      
      if (r.ok) {
          statusElem.style.color = "#27ae60"; // Verde
          statusElem.textContent = `Entidad eliminada: ${data.entityId}`;
      } else {
          statusElem.style.color = "#e74c3c"; // Rojo
          statusElem.textContent = `Error: ${data.error || 'Desconocido'}`;
      }
    } catch(e) {
       alert("Error de conexión");
    }
}

async function createEntity() {
    const id = document.getElementById("newEntityId").value;
    const type = document.getElementById("newEntityType").value;
    const attrsText = document.getElementById("newEntityAttrs").value;

    if (!id || !type) { alert("ID y TYPE son obligatorios"); return; }

    let attrs;
    try { attrs = JSON.parse(attrsText); } catch { alert("JSON inválido"); return; }

    const entity = { id, type, ...attrs };

    try {
      const r = await fetch("/api/entities", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(entity)
      });
      const data = await r.json();
      const statusElem = document.getElementById("createStatus");

      if (r.ok) {
          statusElem.style.color = "#27ae60";
          statusElem.textContent = `Entidad creada: ${data.entityId}`;
      } else {
          statusElem.style.color = "#e74c3c";
          statusElem.textContent = `Error: ${data.error}`;
      }
    } catch (e) {
       alert("Error al crear entidad");
    }
}