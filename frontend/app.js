const express = require("express");
const session = require("express-session");
require("dotenv").config();

const { router: authRouter, initDb } = require("./routes/auth");
const entitiesRouter = require("./routes/entities");
const mqttRouter = require("./routes/mqtt");

const PORT = process.env.PORT || 3000;

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
    maxAge: 1000 * 60 * 60 * 4
  }
}));

app.use(express.static("public", { index: false }));

app.use(authRouter);
app.use(entitiesRouter);
app.use(mqttRouter);

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
