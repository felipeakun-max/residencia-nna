# 🚀 GUÍA: Poner en línea Gestión Residencia NNA
## Desde tu iPhone, sin computador

---

## PASO 1 — Crear cuenta en GitHub (5 min)

1. Ve a **github.com** desde Safari
2. Toca "Sign up"
3. Crea cuenta con tu email
4. Confirma el correo

GitHub es donde guardaremos el código para subirlo a internet.

---

## PASO 2 — Crear cuenta en Railway (3 min)

1. Ve a **railway.app**
2. Toca "Start a New Project"
3. Inicia sesión con tu cuenta de GitHub (más fácil)

Railway es el servidor gratuito donde vivirá tu app.

---

## PASO 3 — Crear base de datos MongoDB gratis (5 min)

1. Ve a **cloud.mongodb.com**
2. Crea cuenta gratis
3. Elige "Free Tier" (M0 Sandbox)
4. Región: cualquiera de Sudamérica
5. Una vez creado, ve a **Connect → Drivers**
6. Copia la URL que dice algo como:
   `mongodb+srv://usuario:password@cluster0.xxxxx.mongodb.net/`
7. ⚠️ Guarda esa URL, la necesitas en el Paso 5

---

## PASO 4 — Subir el código a GitHub

Desde tu iPhone:
1. Descarga la app **"Working Copy"** (App Store, tiene versión gratis)
2. Conéctala con tu cuenta de GitHub
3. Crea un repositorio nuevo llamado "residencia-nna"
4. Sube la carpeta `backend` con todos los archivos

---

## PASO 5 — Conectar Railway con GitHub

En railway.app:
1. "New Project" → "Deploy from GitHub repo"
2. Selecciona el repo "residencia-nna"
3. Ve a **Variables** y agrega estas 3:

```
MONGO_URL = (la URL de MongoDB del Paso 3)
DB_NAME = residencia_nna
SECRET_KEY = (cualquier texto largo, ej: MiClaveSecreta2025NNA!)
```

4. Railway desplegará automáticamente
5. En **Settings → Networking → Generate Domain**
6. Obtendrás una URL como: `https://residencia-nna.up.railway.app`

---

## PASO 6 — Conectar el frontend con tu backend

En el archivo `gestion-nna.html`, busca esta línea al inicio del JavaScript:

```javascript
const API_URL = "TU_URL_AQUI";
```

Reemplaza con tu URL de Railway:
```javascript
const API_URL = "https://residencia-nna.up.railway.app";
```

Guarda y abre desde el celu. ¡Listo!

---

## ✅ Resultado final

- Login real con usuarios de base de datos
- Solo entran personas que tú autorices
- Datos guardados permanentemente
- Accesible desde cualquier celular con la URL

---

## 💰 Costos

| Servicio | Costo |
|----------|-------|
| GitHub | Gratis |
| MongoDB Atlas M0 | Gratis |
| Railway Starter | $5 USD/mes |

Railway tiene $5 de crédito gratis al inicio, así que el primer mes es gratis.

---

## 🆘 ¿Necesitas ayuda?

Comparte la pantalla o cuéntame en qué paso estás y te guío.
