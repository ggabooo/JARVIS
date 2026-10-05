# JARVIS en Streamlit con Supabase

Esta versión conecta obligatoriamente con Supabase. Usa la tabla `jarvis_messages`,
lee el historial de la conversación y guarda pregunta y respuesta juntas.
Si falta la configuración o falla Supabase, muestra un error claro. No sustituye
silenciosamente la base de datos por memoria temporal.

## 1. Prepara los archivos

Descomprime el ZIP. Usa juntos los archivos de la carpeta `jarvis_streamlit` y sube
su contenido a la raíz de tu repositorio. Conserva las carpetas `assets`, `sql` y
`.streamlit`.

El archivo de entrada es **app.py**. El `JARVIS.py` de consola se mantiene aparte;
esta versión web utiliza `jarvis_agent.py` para generar las respuestas.

Coloca tu imagen **JARVIS.png** al lado de `app.py`, respetando mayúsculas.
La imagen no venía adjunta y no se incluye. Mientras la añades aparece una J.

## 2. Prepara la tabla de Supabase

Entra al mismo proyecto donde ya tienes `jarvis_messages`:

1. Abre **SQL Editor** y crea una consulta con **New query**.
2. Copia todo el contenido de **sql/supabase_sessions.sql**.
3. Pégalo y pulsa **Run**.

Si la tabla existe, el script conserva sus datos. Añade la columna `session_id`,
crea un índice y mantiene RLS habilitado. Si la tabla falta, la crea.

En tu tabla existente, la modificación de estructura es:

```sql
alter table public.jarvis_messages
add column if not exists session_id uuid;
```

La tabla usada por el código necesita estas columnas:

| Columna | Uso |
|---|---|
| role | `user` para tu pregunta y `assistant` para la respuesta. |
| content | Texto del mensaje. |
| created_at | Fecha y hora del mensaje. |
| session_id | Identificador que separa conversaciones. |

El script también define `id` cuando crea una tabla nueva. No cambia el tipo de
`id` de tu tabla existente. Los mensajes anteriores sin `session_id` siguen en la
base, pero no se muestran a los visitantes de una conversación nueva.

## 3. Ten a mano las tres variables

- **GROQ_API_KEY:** tu clave de Groq que ya utilizabas.
- **SUPABASE_URL:** URL de tu proyecto, con formato `https://...supabase.co`;
  puedes copiarla desde el diálogo **Connect** del proyecto.
- **SUPABASE_KEY:** clave **Secret** (`sb_secret_...`) de ese mismo proyecto,
  disponible en **Settings → API Keys**. Si ya configuraste una clave `service_role`
  que funciona, esta aplicación también puede usarla. [1]

La clave secreta se usa solo en el servidor Python de Streamlit. Tiene permisos
amplios y omite RLS: consérvala en Secrets, sin publicarla en GitHub ni incluirla en
archivos que distribuyas. No necesitas desactivar RLS ni crear políticas de acceso
público para esta versión. [1]

## 4. Configura Streamlit

Al desplegar desde tu repositorio:

- **Main file path:** `app.py`.
- **Python version:** `3.12`.
- **Advanced settings → Secrets:** pega lo siguiente, sustituyendo los tres valores:

```toml
GROQ_API_KEY = "TU_CLAVE_GROQ"
SUPABASE_URL = "https://TU_PROYECTO.supabase.co"
SUPABASE_KEY = "TU_CLAVE_SECRETA_SUPABASE"
```

Si la app ya existe, abre **Settings → Secrets**, pega las mismas variables y guarda.
Los nombres van exactamente así y los valores entre comillas. No uses secciones
como `[supabase]`; este código lee las tres variables en la raíz del archivo. [2]

Pulsa **Deploy**. Si ya estaba desplegada, guarda los cambios y recarga la app.
Streamlit instala las dependencias de `requirements.txt`. No hace falta subir tu
`.env` ni activar tu entorno virtual de Windows en Streamlit. [2,3]

## 5. Comprueba el guardado real

1. Abre la web. Si la lectura inicial funciona, al pie aparecerá
   **Historial leído desde Supabase.**
2. Escribe una pregunta de prueba y espera la respuesta.
3. Después del guardado aparecerá **Historial guardado en Supabase.**
4. En Supabase abre **Table Editor → jarvis_messages** y actualiza la vista.
5. Comprueba las dos filas más recientes: una con `role = user` y otra con
   `role = assistant`. Ambas deben tener el mismo `session_id` y el texto de tu prueba.

Esta prueba confirma la conexión de escritura, no solo la creación del cliente.
Crear un cliente Supabase por sí solo no demuestra que una inserción funcione. [4]

## Cómo queda la memoria

Los mensajes se guardan en Supabase y no se borran cuando cierras la web.
Durante la conversación, JARVIS usa los últimos 20 mensajes como contexto.
Cada sesión de Streamlit tiene un identificador propio. Al recargar, abrir otra
pestaña o pulsar **Nueva conversación**, puede comenzar otra conversación.

No se implementa recuperación de chats entre dispositivos ni cuentas de usuario.
Esto evita que una persona vea el historial de otra, sin añadir un sistema de login.
El filtro de sesión se aplica en el backend; no se comparte un cache global.

## Si aparece un error

| Error | Qué revisar |
|---|---|
| Faltan variables en Secrets | Pega las tres variables con los nombres exactos. |
| No se pudo leer el historial | Comprueba URL, clave del mismo proyecto y tabla con `session_id`. |
| `session_id` no existe | Ejecuta el archivo SQL del paso 2. |
| Error RLS / `42501` al guardar | Revisa que uses la clave secreta de backend y los permisos de la tabla. |
| Responde pero no confirma el guardado | Revisa Table Editor antes de repetir: una interrupción de red puede impedir confirmar una escritura que sí llegó. |
| No aparece la imagen | Verifica `JARVIS.png` junto a `app.py` y sus mayúsculas. |

La aplicación no imprime tus claves ni muestra excepciones completas a los visitantes.

## Prueba local, si la necesitas

Con tu entorno virtual activado, dentro de la carpeta del proyecto:

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Localmente admite tu `.env` con las mismas tres variables. En Streamlit Cloud usa
**Secrets**. Si configuras ambos, Secrets tiene prioridad. El `.gitignore` incluido
excluye `.env` y `.streamlit/secrets.toml`.

## Opciones que puedes dejar para después

El modelo predeterminado es `openai/gpt-oss-120b`; no necesitas configurar nada más.
Puedes restringir el acceso al prototipo añadiendo `APP_PASSWORD` en Secrets.
Si la omites, quienes tengan acceso a la página podrán hacer consultas que usarán
tu cuenta Groq. La contraseña compartida no equivale a cuentas individuales.

El diseño oscuro, el texto blanco, los rubros y las herramientas económicas se
mantienen. Los datos se consultan al recibir preguntas; no hay tareas programadas.
Al actualizar la rama desplegada en GitHub, Streamlit actualiza la app. [3]

## Referencias

1. Supabase. API keys [Internet]. [citado 5 oct 2026]. Disponible en: https://supabase.com/docs/guides/getting-started/api-keys
2. Streamlit. Secrets management for your Community Cloud app [Internet]. [citado 5 oct 2026]. Disponible en: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management
3. Streamlit. Manage your app [Internet]. [citado 5 oct 2026]. Disponible en: https://docs.streamlit.io/deploy/streamlit-community-cloud/manage-your-app
4. Supabase. Python: Initializing [Internet]. [citado 5 oct 2026]. Disponible en: https://supabase.com/docs/reference/python/initializing
