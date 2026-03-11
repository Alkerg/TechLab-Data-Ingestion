const express = require("express");
const path = require("path");
const fs = require("fs");
const http = require("http");
const { execFile } = require("child_process");
const { promisify } = require("util");

const router = express.Router();
const execFileAsync = promisify(execFile);

const MQTT_CONFIG_PATH = process.env.MQTT_CONFIG_PATH || path.join(__dirname, "..", "mqtt_config");
const MQTT_BROKER_CONTAINER = process.env.MQTT_BROKER_CONTAINER || "mqtt-broker";

function reloadMqttBroker() {
    return new Promise((resolve) => {
        const options = {
            socketPath: "/var/run/docker.sock",
            path: `/containers/${MQTT_BROKER_CONTAINER}/kill?signal=SIGHUP`,
            method: "POST"
        };
        const req = http.request(options, (res) => {
            if (res.statusCode === 204) {
                console.log("SIGHUP enviado a mqtt-broker, configuración recargada");
            } else {
                console.error(`Error al enviar SIGHUP: status ${res.statusCode}`);
            }
            resolve();
        });
        req.on("error", (err) => {
            console.error("No se pudo enviar SIGHUP a mqtt-broker:", err.message);
            resolve();
        });
        req.end();
    });
}

function parseAcl(content) {
    const lines = content.split("\n");
    const entries = [];
    let current = null;
    for (const line of lines) {
        const trimmed = line.trim();
        if (trimmed.startsWith("user ")) {
            if (current) entries.push(current);
            current = { user: trimmed.slice(5).trim(), topics: [] };
        } else if (trimmed.startsWith("topic ") && current) {
            const parts = trimmed.slice(6).trim().split(/\s+/);
            if (parts.length === 1) {
                current.topics.push({ permission: "readwrite", topic: parts[0] });
            } else {
                current.topics.push({ permission: parts[0], topic: parts.slice(1).join(" ") });
            }
        }
    }
    if (current) entries.push(current);
    return entries;
}

function serializeAcl(entries) {
    return entries.map(e => {
        const lines = [`user ${e.user}`];
        for (const t of e.topics) {
            lines.push(`topic ${t.permission} ${t.topic}`);
        }
        return lines.join("\n");
    }).join("\n\n") + "\n";
}

// Listar usuarios MQTT
router.get("/api/mqtt/users", async (req, res) => {
    try {
        const passwdPath = path.join(MQTT_CONFIG_PATH, "passwd");
        const content = await fs.promises.readFile(passwdPath, "utf-8");
        const users = content.split("\n").filter(l => l.trim()).map(l => l.split(":")[0]);
        res.json(users);
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// Registrar usuario MQTT
router.post("/api/mqtt/users", async (req, res) => {
    const { username, password } = req.body;
    if (!username || !password) {
        return res.status(400).json({ error: "Username y password son obligatorios" });
    }
    if (!/^[a-zA-Z0-9_-]+$/.test(username)) {
        return res.status(400).json({ error: "Username solo puede contener letras, números, guiones y guiones bajos" });
    }
    if (password.length < 4) {
        return res.status(400).json({ error: "La contraseña debe tener al menos 4 caracteres" });
    }
    try {
        const passwdPath = path.join(MQTT_CONFIG_PATH, "passwd");
        await execFileAsync("mosquitto_passwd", ["-b", passwdPath, username, password]);
        await reloadMqttBroker();
        res.json({ status: "created", username });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// Eliminar usuario MQTT
router.delete("/api/mqtt/users/:username", async (req, res) => {
    const { username } = req.params;
    if (!/^[a-zA-Z0-9_-]+$/.test(username)) {
        return res.status(400).json({ error: "Username inválido" });
    }
    try {
        const passwdPath = path.join(MQTT_CONFIG_PATH, "passwd");
        await execFileAsync("mosquitto_passwd", ["-D", passwdPath, username]);
        const aclPath = path.join(MQTT_CONFIG_PATH, "acl");
        const content = await fs.promises.readFile(aclPath, "utf-8");
        const entries = parseAcl(content).filter(e => e.user !== username);
        await fs.promises.writeFile(aclPath, serializeAcl(entries));
        await reloadMqttBroker();
        res.json({ status: "deleted", username });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// Listar reglas ACL
router.get("/api/mqtt/acl", async (req, res) => {
    try {
        const aclPath = path.join(MQTT_CONFIG_PATH, "acl");
        const content = await fs.promises.readFile(aclPath, "utf-8");
        const entries = parseAcl(content);
        const rules = [];
        for (const e of entries) {
            for (const t of e.topics) {
                rules.push({ user: e.user, permission: t.permission, topic: t.topic });
            }
        }
        res.json(rules);
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// Agregar regla ACL
router.post("/api/mqtt/acl", async (req, res) => {
    const { username, permission, topic } = req.body;
    if (!username || !topic) {
        return res.status(400).json({ error: "Username y topic son obligatorios" });
    }
    if (!/^[a-zA-Z0-9_-]+$/.test(username)) {
        return res.status(400).json({ error: "Username inválido" });
    }
    const validPerms = ["read", "write", "readwrite"];
    const perm = permission || "readwrite";
    if (!validPerms.includes(perm)) {
        return res.status(400).json({ error: "Permiso debe ser: read, write o readwrite" });
    }
    if (!/^[a-zA-Z0-9_\-\/#+]+$/.test(topic)) {
        return res.status(400).json({ error: "Topic contiene caracteres inválidos" });
    }
    try {
        const aclPath = path.join(MQTT_CONFIG_PATH, "acl");
        const content = await fs.promises.readFile(aclPath, "utf-8");
        const entries = parseAcl(content);
        const existing = entries.find(e => e.user === username);
        if (existing) {
            existing.topics.push({ permission: perm, topic });
        } else {
            entries.push({ user: username, topics: [{ permission: perm, topic }] });
        }
        await fs.promises.writeFile(aclPath, serializeAcl(entries));
        await reloadMqttBroker();
        res.json({ status: "created", username, permission: perm, topic });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// Eliminar regla ACL
router.delete("/api/mqtt/acl", async (req, res) => {
    const { username, permission, topic } = req.body;
    if (!username || !topic) {
        return res.status(400).json({ error: "Username y topic son obligatorios" });
    }
    try {
        const aclPath = path.join(MQTT_CONFIG_PATH, "acl");
        const content = await fs.promises.readFile(aclPath, "utf-8");
        const entries = parseAcl(content);
        let found = false;
        for (const entry of entries) {
            if (entry.user === username) {
                const before = entry.topics.length;
                entry.topics = entry.topics.filter(t => !(t.permission === permission && t.topic === topic));
                if (entry.topics.length < before) found = true;
            }
        }
        if (!found) {
            return res.status(404).json({ error: "Regla no encontrada" });
        }
        const filtered = entries.filter(e => e.topics.length > 0);
        await fs.promises.writeFile(aclPath, serializeAcl(filtered));
        await reloadMqttBroker();
        res.json({ status: "deleted", username, permission, topic });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

module.exports = router;
