const express = require("express");
const fetch = require("node-fetch");
require("dotenv").config();

const app = express();
app.use(express.json());
app.use(express.static("public"));

const ORION_URL = process.env.ORION_URL || "http://localhost:1026";

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

//Iniciar el servidor del microfrontend
app.listen(3000, () => {
  console.log("Microfrontend disponible en http://localhost:3000");
});
