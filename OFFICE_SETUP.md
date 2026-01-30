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

## 🆘 ¿Qué pasa si el código de mi oficina está desactualizado? (Rescate)

Si ya estuviste trabajando en la oficina y tienes miedo de perder esos cambios al bajar la versión "maestra" de GitHub, sigue este protocolo de seguridad:

### Paso 1: Guarda tus cambios locales (Protección)
En la terminal de tu oficina:
```powershell
git add .
git commit -m "Mis cambios locales de la oficina antes de sincronizar"
```

### Paso 2: Trae la versión de "Cali/Casa" (Sincronización)
```powershell
git pull origin main
```

### Paso 3: Resolver Conflictos (Si aparecen)
Si Git te dice que hay "Conflicts", no entres en pánico. 
- Abre los archivos marcados. 
- Verás marcas como `<<<<<< HEAD`. 
- Elige lo que quieras conservar y borra las marcas.
- Luego: `git add .` y `git commit -m "Conflictos resueltos"`.

---

> [!TIP]
> **Recomendación Mikey**: A partir de ahora, haz que sea un hábito:
> 1. LLego a la oficina -> `git pull`
> 2. Me voy de la oficina -> `git push`
> 3. Llego a casa -> `git pull`
> 4. Me voy a dormir -> `git push`
> Así nunca tendrás versiones diferentes. 🛡️🎯💎
