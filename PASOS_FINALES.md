# 🚀 Pasos Finales para el Simulador de tu Hijo (ICFES Sim)

¡Ya casi estamos! Para que el simulador funcione en internet y guarde el progreso de todos los amigos, sigue esta lista:

### 1️⃣ Crear el "Cerebro" en la Nube (Supabase)
1. Ve a [Supabase.com](https://supabase.com) y entra con tu cuenta de GitHub.
2. Dale a **"New Project"** y ponle de nombre: `icfes-sim-master`.
3. Guarda bien la contraseña que elijas.
4. Ve a **Project Settings** > **Database** y busca la **"Connection String"** (la que empieza por `postgresql://...`).
5. **¡IMPORTANTE!** Copia esa URL y pégala en tu archivo `.env` del proyecto ICFES donde dice `DATABASE_URL`.

### 2️⃣ Subir el Código a GitHub
Abre la terminal en la carpeta `icfes_sim` y corre esto:
```powershell
git remote add origin https://github.com/TU_USUARIO/icfes_sim.git
git branch -M main
git push -u origin main
```

### 3️⃣ Lanzar a Internet (Streamlit Cloud)
1. Ve a [share.streamlit.io](https://share.streamlit.io).
2. Conecta tu repositorio `icfes_sim`.
3. Antes de lanzar, ve a **Advanced Settings** y en la caja de **Secrets**, pega esto:
```toml
GEMINI_API_KEY = "TU_LLAVE_DE_GOOGLE"
DATABASE_URL = "LA_URL_DE_SUPABASE_QUE_COPIASTE"
```
4. Dale a **"Deploy!"** y ¡listo!

---
> [!TIP]
> Una vez esté funcionando, pásale el link de Streamlit a tu hijo por WhatsApp. Él mismo podrá registrar su usuario y empezar a practicar. Mikey. 🛡️🎯💎
