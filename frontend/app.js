const express = require("express");
const fetch = require("node-fetch");
const path = require("path");
const session = require("express-session");
const bcrypt = require("bcryptjs");
const { Pool } = require("pg");
require("dotenv").config();
const PORT = process.env.PORT || 3001;

const app = express();
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(session({
  secret: process.env.SESSION_SECRET || "secret",
  resave: false,
  saveUninitialized: false,
  cookie: {
    httpOnly: true,
    sameSite: "lax",
    maxAge: 1000 * 60 * 60 * 4 // 4 horas
  }
}));

app.use(express.static("public", { index: false }));

const ORION_URL = process.env.ORION_URL || "http://localhost:1026";

const pool = new Pool({
  host: process.env.DB_HOST || "localhost",
  port: Number(process.env.DB_PORT || 5432),
  user: process.env.DB_USER || "techlab",
  password: process.env.DB_PASSWORD || "techlabpw",
  database: process.env.DB_NAME || "techlab"
});

async function initDb() {
  await pool.query(`
    CREATE TABLE IF NOT EXISTS users (
      id SERIAL PRIMARY KEY,
      email TEXT UNIQUE NOT NULL,
      password_hash TEXT NOT NULL,
      created_at TIMESTAMP DEFAULT NOW()
    );
  `);
}

//Crear una nueva entidad
app.post("/api/entities", async (req, res) => {
  try {
    const entity = req.body;

    if (!entity.id || !entity.type) {
      return res.status(400).json({
        error: "La entidad debe tener al menos id y type"
      });
    }

    const r = await fetch(`${ORION_URL}/v2/entities`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(entity)
    });

    if (!r.ok) {
      const text = await r.text();
      return res.status(400).json({ error: text });
    }

    res.json({
      status: "created",
      entityId: entity.id
    });

  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

//Mostrar todas las entidades creadas
app.get("/api/entities", async (req, res) => {
  try {
    const r = await fetch(`${ORION_URL}/v2/entities`);
    const data = await r.json();
    res.json(data);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

//Suscribir una entidad a un endpoint
app.post("/api/subscribe", async (req, res) => {
  const { entityId, entityType, attrs, endpoint } = req.body;

  const subscription = {
    description: `Suscripción para ${entityId}`,
    subject: {
      entities: [
        {
          id: entityId,
          type: entityType
        }
      ],
      condition: {
        attrs: attrs
      }
    },
    notification: {
      http: {
        url: endpoint
      },
      attrs: attrs
    }
  };

  try {
    const r = await fetch(`${ORION_URL}/v2/subscriptions`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(subscription)
    });

    const text = await r.text();
    res.json({ status: r.status, response: text });

  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

//Mostrar todas las suscripciones por entidad
app.get("/api/subscriptions", async (req, res) => {
  try {
    const r = await fetch(`${ORION_URL}/v2/subscriptions`);
    const data = await r.json();

    const clean = data.map(sub => ({
      entityId: sub.subject.entities[0]?.id || "N/A",
      entityType: sub.subject.entities[0]?.type || "N/A",
      endpoint: sub.notification.http.url
    }));

    res.json(clean);

  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

//Eliminar una entidad por ID
app.delete("/api/entities/:id", async (req, res) => {
  const { id } = req.params;

  try {
    const r = await fetch(`${ORION_URL}/v2/entities/${id}`, {
      method: "DELETE"
    });

    if (!r.ok) {
      return res.status(404).json({ error: "Entidad no encontrada" });
    }

    res.json({
      status: "deleted",
      entityId: id
    });

  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});


// Autenticación
function requireAuth(req, res, next) {
  if (req.session && req.session.userId) return next();
  return res.redirect("/login?error=auth");
}

// Rutas de vistas
app.get("/", (req, res) => {
  return res.redirect("/login");
});

app.get("/login", (req, res) => {
  res.sendFile(path.join(__dirname, "public","html", "login.html"));
});

app.post("/login", async (req, res) => {
  const { email, password } = req.body;
  try {
    if (!email || !password) return res.redirect("/login?error=1");
    const { rows } = await pool.query("SELECT id, password_hash FROM users WHERE email = $1", [email]);
    if (rows.length === 0) return res.redirect("/login?error=1");
    const user = rows[0];
    const ok = await bcrypt.compare(password, user.password_hash);
    if (!ok) return res.redirect("/login?error=1");
    req.session.userId = user.id;
    return res.redirect("/dashboard");
  } catch (e) {
    console.error(e);
    return res.redirect("/login?error=1");
  }
});

app.get("/register", (req, res) => {
  res.sendFile(path.join(__dirname, "public","html", "register.html"));
});

app.post("/register", async (req, res) => {
  const { email, password, password2 } = req.body;
  try {
    if (!email || !password || !password2 || password !== password2) {
      return res.redirect("/register?error=1");
    }
    const hash = await bcrypt.hash(password, 10);
    await pool.query("INSERT INTO users(email, password_hash) VALUES($1, $2)", [email, hash]);
    return res.redirect("/login?registered=1");
  } catch (e) {
    console.error(e);
    return res.redirect("/register?error=exists");
  }
});

app.get("/dashboard", requireAuth, (req, res) => {
  res.sendFile(path.join(__dirname, "public","html","dashboard.html"));
});

app.get("/logout", (req, res) => {
  req.session.destroy(() => res.redirect("/login"));
});

//Iniciar el servidor del frontend
initDb()
  .then(() => {
    app.listen(PORT, () => {
      console.log(`Panel de control disponible en el puerto ${PORT}`);
    });
  })
  .catch((e) => {
    console.error("DB init error:", e);
    process.exit(1);
  });
