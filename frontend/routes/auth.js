const express = require("express");
const path = require("path");
const bcrypt = require("bcryptjs");
const { Pool } = require("pg");

const router = express.Router();

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

function requireAuth(req, res, next) {
    if (req.session && req.session.userId) return next();
    return res.redirect("/login?error=auth");
}

router.get("/", (req, res) => {
    return res.redirect("/login");
});

router.get("/login", (req, res) => {
    res.sendFile(path.join(__dirname, "..", "public", "html", "login.html"));
});

router.post("/login", async (req, res) => {
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

router.get("/register", (req, res) => {
    res.sendFile(path.join(__dirname, "..", "public", "html", "register.html"));
});

router.post("/register", async (req, res) => {
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

router.get("/dashboard", requireAuth, (req, res) => {
    res.sendFile(path.join(__dirname, "..", "public", "html", "dashboard.html"));
});

router.get("/logout", (req, res) => {
    req.session.destroy(() => res.redirect("/login"));
});

module.exports = { router, initDb, requireAuth };
