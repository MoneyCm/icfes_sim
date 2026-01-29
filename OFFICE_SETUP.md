# 🏢 Guía de Trabajo Remoto: DIAN Sim & ICFES Sim

¡Excelente pregunta! Gracias a que configuramos **GitHub** (para el código) y **Supabase** (para los datos), tu oficina será como una extensión de tu casa. 🚀

## 1. Antes de Salir de Casa (Sincronización FINAL)
Asegúrate de que el código más reciente esté en GitHub. Abre la terminal y haz esto en ambas carpetas:

**Para DIAN Sim:**
```powershell
cd C:\Proyectos\CesarWorkspace\dian_sim
git add .
git commit -m "Sincronización para oficina"
git push origin main
```

**Para ICFES Sim:**
```powershell
cd C:\Users\Usuario\.gemini\antigravity\scratch\icfes_sim
git add .
git commit -m "Sincronización para oficina"
git push origin main
```

---

## 2. Al llegar a la Oficina (Instalación ÚNICA)
Solo la primera vez, descarga los proyectos en tu PC de la oficina:

1. **Clonar Repo DIAN:** `git clone https://github.com/MoneyCm/dian_sim.git`
2. **Clonar Repo ICFES:** `git clone https://github.com/MoneyCm/icfes_sim.git`
3. **Archivo .env:** Crea un archivo `.env` en cada carpeta y pega las llaves correspondientes (Gemini y Supabase) que usamos aquí.

---

## 3. Flujo Diario de Trabajo (El "Ritual")

### 📥 Empezar el día (Bajar cambios)
Antes de programar en la oficina, corre esto:
- `git pull origin main` (en ambas carpetas).

### 📤 Terminar el día (Subir cambios)
Antes de apagar la oficina para volver a casa:
- `git add .`
- `git commit -m "Avances en la oficina"`
- `git push origin main`

---

> [!IMPORTANT]
> **No te preocupes por la Base de Datos**: Como usamos Supabase, si tu hijo registra una pregunta desde casa mientras tú estás en la oficina, la verás aparecer en el ranking al instante sin hacer nada. ¡Los datos viven en internet! 🛡️🎯💎
