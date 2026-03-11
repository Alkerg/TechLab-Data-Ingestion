async function addMqttUser() {
    const username = document.getElementById("mqttUsername").value;
    const password = document.getElementById("mqttPassword").value;
    const statusElem = document.getElementById("mqttUserStatus");

    if(!username || !password)
    {
        alert("Usuario y contraseña son obligatorios");
        return;
    }

    try{
        const r = await fetch("/api/mqtt/users", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, password })
        });
        const data = await r.json();
        if(r.ok){
            statusElem.className = "text-success fw-bold";
            statusElem.textContent = `Dispositivo registrado: ${data.username}`;
            document.getElementById("mqttUsername").value = "";
            document.getElementById("mqttPassword").value = "";
            getMqttUsers();
        }else{
            statusElem.className = "text-danger fw-bold";
            statusElem.textContent = `Error: ${data.error}`;
        }
    }catch(e){
        alert("Error de conexión");
    }
}

async function getMqttUsers() {
    try{
        const r = await fetch("/api/mqtt/users");
        const data = await r.json();
        const table = document.getElementById("mqttUsers");
        table.innerHTML = "";

        if(data.length === 0){
            table.innerHTML = "<tr><td colspan='2' class='text-center text-muted'>No hay dispositivos registrados</td></tr>";
            return;
        }

        data.forEach(user => {
            const row = document.createElement("tr");
            const tdUser = document.createElement("td");
            tdUser.textContent = user;
            const tdActions = document.createElement("td");
            const btn = document.createElement("button");
            btn.className = "btn btn-danger btn-sm";
            btn.textContent = "Eliminar";
            btn.onclick = () => deleteMqttUser(user);
            tdActions.appendChild(btn);
            row.appendChild(tdUser);
            row.appendChild(tdActions);
            table.appendChild(row);
        });
    }catch(e){
        alert("Error cargando dispositivos MQTT");
    }
}

async function deleteMqttUser(username) {
    if(!confirm(`¿Eliminar el dispositivo "${username}" y sus reglas ACL?`)) return;

    try{
        const r = await fetch(`/api/mqtt/users/${encodeURIComponent(username)}`, { method: "DELETE" });
        const data = await r.json();
        if(r.ok){
            getMqttUsers();
            getAclRules();
        }else{
            alert(`Error: ${data.error}`);
        }
    }catch(e){
        alert("Error de conexión");
    }
}

async function addAclRule() {
    const username = document.getElementById("aclUsername").value;
    const permission = document.getElementById("aclPermission").value;
    const topic = document.getElementById("aclTopic").value;
    const statusElem = document.getElementById("aclStatus");

    if(!username || !topic){
        alert("Usuario y topic son obligatorios");
        return;
    }

    try{
        const r = await fetch("/api/mqtt/acl", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, permission, topic })
        });
        const data = await r.json();
        if(r.ok){
            statusElem.className = "text-success fw-bold";
            statusElem.textContent = `Regla ACL creada: ${data.username} ${data.permission} ${data.topic}`;
            document.getElementById("aclUsername").value = "";
            document.getElementById("aclTopic").value = "";
            getAclRules();
        }else{
            statusElem.className = "text-danger fw-bold";
            statusElem.textContent = `Error: ${data.error}`;
        }
    }catch(e){
        alert("Error de conexión");
    }
}

async function getAclRules() {
    try{
        const r = await fetch("/api/mqtt/acl");
        const data = await r.json();
        const table = document.getElementById("aclRules");
        table.innerHTML = "";

        if (data.length === 0) {
            table.innerHTML = "<tr><td colspan='4' class='text-center text-muted'>No hay reglas ACL configuradas</td></tr>";
            return;
        }

        data.forEach(rule => {
            const row = document.createElement("tr");
            const tdUser = document.createElement("td");
            tdUser.textContent = rule.user;
            const tdPerm = document.createElement("td");
            tdPerm.textContent = rule.permission;
            const tdTopic = document.createElement("td");
            tdTopic.textContent = rule.topic;
            const tdActions = document.createElement("td");
            const btn = document.createElement("button");
            btn.className = "btn btn-danger btn-sm";
            btn.textContent = "Eliminar";
            btn.onclick = () => deleteAclRule(rule.user, rule.permission, rule.topic);
            tdActions.appendChild(btn);
            row.appendChild(tdUser);
            row.appendChild(tdPerm);
            row.appendChild(tdTopic);
            row.appendChild(tdActions);
            table.appendChild(row);
        });
    }catch(e){
        alert("Error cargando reglas ACL");
    }
}

async function deleteAclRule(user, permission, topic) {
    if(!confirm(`¿Eliminar regla: ${user} ${permission} ${topic}?`)) return;

    try{
        const r = await fetch("/api/mqtt/acl", {
            method: "DELETE",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username: user, permission, topic })
        });
        const data = await r.json();
        if(r.ok){
            getAclRules();
        }else{
            alert(`Error: ${data.error}`);
        }
    }catch(e){
        alert("Error de conexión");
    }
}
