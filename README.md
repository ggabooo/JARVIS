# J.A.R.V.I.S. — versión web para Streamlit

Agente económico con Groq, 21 indicadores del Banco Mundial, deuda del FMI, divisas,
criptoactivos y memoria por conversación. La página usa fondo oscuro, texto blanco,
acentos celestes y amarillos, y las tipografías Oxanium y Space Grotesk.

## Desplegar en tu flujo de GitHub → Streamlit

1. Descomprime el paquete. Sube **el contenido de `jarvis_streamlit`** a un repositorio,
   conservando `assets`, `sql` y `.streamlit`. No subas el ZIP como único archivo.
2. Coloca tu imagen **`JARVIS.png` junto a `app.py`**, con esas mayúsculas exactas.
   Se muestra arriba, centrada y enlazada al inicio del chat. El paquete no contiene
   tu imagen; mientras la añades, aparece un emblema tipográfico J.
3. En Streamlit Community Cloud selecciona el repositorio y su rama, con
   **Main file path: `app.py`**. Selecciona **Python 3.12** en Advanced settings.
   Si subiste la carpeta entera como subcarpeta, ajusta el archivo principal a
   `jarvis_streamlit/app.py`; es preferible usar su contenido en la raíz.
4. En **Advanced settings → Secrets** (o Settings → Secrets tras desplegar), pega:

   ```toml
   GROQ_API_KEY = "TU_CLAVE_GROQ"
   GROQ_MODEL = "openai/gpt-oss-120b"
   ```

5. Pulsa **Deploy**. Streamlit instala `requirements.txt` y ejecuta la web.
   El chat ya funciona con memoria durante la sesión, aun sin Supabase. [1–3]

Las claves se configuran en Secrets, no en el código que subes a GitHub.
`secrets.toml.example` es una plantilla, no un archivo con credenciales reales.
No subas `.env` ni `.streamlit/secrets.toml`. El `.gitignore` incluido los excluye,
pero no protege archivos que ya estuvieran registrados en un repositorio. [2]

## Conservar el historial en Supabase

Si quieres mantener el guardado que ya configuraste:

1. Ejecuta una vez **`sql/supabase_sessions.sql`** en el SQL Editor de tu proyecto.
   Crea la tabla si falta o añade `session_id` a la que ya existe, sin borrar filas.
2. Añade a los Secrets de Streamlit:

   ```toml
   SUPABASE_URL = "https://TU_PROYECTO.supabase.co"
   SUPABASE_KEY = "TU_CLAVE_SECRET_DE_BACKEND"
   ```

La clave secreta permanece en el servidor Python. Nunca se envía al navegador ni se
incluye en la imagen, CSS o respuestas del agente. RLS se conserva habilitado. La
memoria de esta web filtra por un UUID de conversación generado en el servidor;
no consulta todo el historial como la versión original de consola. [4]

**Alcance de la memoria:** cada pestaña/sesión de Streamlit tiene su conversación.
Los mensajes se conservan durante las interacciones y pueden guardarse en Supabase.
Recargar la página, abrir otra pestaña o pulsar «Nueva conversación» puede iniciar
una sesión nueva. No se implementa recuperación de conversaciones entre dispositivos
ni inicio de sesión individual. Las filas antiguas, sin `session_id`, no se asignan
automáticamente a ningún visitante. «Nueva conversación» no borra datos de Supabase.

La configuración presupone una tabla con `role`, `content` y `created_at`, como la
que utilizaba el código original. Si modificaste esas columnas, adapta la migración.
Si Supabase falla, la conversación sigue en la sesión y aparece un aviso de que no
se pudo guardar permanentemente. Los mensajes fallidos no se reenvían a la base de
datos automáticamente. La migración no modifica políticas públicas preexistentes.

## Proteger tu prototipo

Opcionalmente agrega una contraseña de acceso en Secrets:

```toml
APP_PASSWORD = "UNA_CONTRASENA_LARGA_ELEGIDA_POR_TI"
```

La pantalla de acceso se evalúa antes de crear los clientes. Si omites esta variable,
la aplicación permite consultar a quienes tengan acceso a su URL y las llamadas se
cargan a tu cuenta Groq. La contraseña compartida es una barrera básica para el
prototipo: no sustituye un sistema de usuarios con recuperación, MFA o límites por
cuenta. Esta versión no impone cuotas por visitante.

## Qué cambió respecto a la consola

| Archivo | Función |
|---|---|
| `app.py` | Entrada web, interfaz, sesiones, chat, consultas rápidas y descarga del diálogo. |
| `jarvis_agent.py` | Cliente Groq y selección automática de las seis herramientas. |
| `JARVISTools.py` | Consultas externas con fecha, unidad y fuente. |
| `basic_memory.py` | Memoria separada por conversación y persistencia opcional. |
| `catalogo.py` | Rubros, etiquetas, países e indicadores. |
| `assets/style.css` | Tipografía, colores, detalles tecnológicos y adaptación a móvil. |
| `.streamlit/config.toml` | Tema oscuro y texto blanco. |
| `.streamlit/secrets.toml.example` | Plantilla para Secrets. |
| `requirements.txt` | Versiones de las dependencias usadas en la verificación local. |
| `sql/supabase_sessions.sql` | Adaptación de la tabla para la web. |

El `while True` / `input()` original se reemplaza por `st.chat_input`, `st.chat_message`
y estado de sesión. No debes importar el `JARVIS.py` original desde la web, porque
su bucle de consola bloquearía la ejecución. Los archivos de este paquete forman
una versión web independiente. [1]

## Rubros incluidos

- **Producción y crecimiento:** PIB, PIB por habitante y crecimiento del PIB.
- **Precios y empleo:** inflación y desempleo.
- **Finanzas públicas:** deuda del gobierno central (Banco Mundial), deuda del
  gobierno general (FMI), impuestos y gasto educativo.
- **Sector externo:** remesas, exportaciones, importaciones, cuenta corriente,
  inversión extranjera y deuda externa.
- **Inversión y consumo:** formación de capital, capital fijo, ahorro bruto,
  consumo de los hogares y del gobierno.
- **Población:** habitantes y crecimiento poblacional.
- **Divisas:** tipo de cambio entre monedas, con acceso rápido dólar/quetzal.
- **Criptoactivos:** bitcoin, ethereum, solana y dogecoin.

Puedes escribir el país directamente en el chat. El explorador incluye países
frecuentes y admite otro código ISO alpha-3. Los datos se solicitan cuando preguntas;
no se cargan 21 indicadores cada vez que se redibuja la interfaz.

## Respuestas y límites de las fuentes

- El Banco Mundial devuelve el último valor no vacío disponible y su año.
  «Último publicado» puede corresponder a un período anterior al actual.
- La deuda FMI/WEO usa el último año disponible que no sea futuro y advierte que
  puede ser una estimación. No se confunde con la cobertura de gobierno central.
- ExchangeRate-API devuelve una referencia; no se presenta como cotización oficial
  de Banguat ni como precio de compra o venta de un banco.
- Frankfurter puede no cubrir algunas monedas. El agente puede usar otra herramienta.
- La API pública de CoinGecko puede limitar llamadas. Se informa el error en lugar
  de inventar un precio.
- Las herramientas actuales consultan últimos valores; no descargan series históricas
  completas ni hacen pronósticos propios. Las explicaciones del modelo pueden
  requerir revisión. Se solicita citar fuentes en formato Vancouver.
- El contexto del modelo conserva los últimos 20 mensajes; la interfaz muestra hasta
  100. Hay un límite de consultas a herramientas por respuesta para evitar bucles.

## Ejecución local

En la carpeta del proyecto, con tu entorno virtual activado:

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Completa `.streamlit/secrets.toml` a partir de su plantilla, o usa un `.env` local.
Los Secrets tienen prioridad sobre `.env`. No ejecutes `python app.py`: utiliza
el comando de Streamlit.

## Funcionamiento después del despliegue

La app se ejecuta en Streamlit: tu computadora no necesita permanecer encendida.
El usuario envía una pregunta y el agente elige las herramientas, consulta las
fuentes y responde. Al actualizar la rama desplegada en GitHub, Streamlit refleja
los cambios y reinstala dependencias si cambias `requirements.txt`. [3]

Esto no programa tareas ni ejecuta consultas en segundo plano. Community Cloud
puede hibernar la app tras inactividad y mostrar un botón para reactivarla. [3]

## Si algo falla

| Mensaje o síntoma | Revisión |
|---|---|
| Falta `GROQ_API_KEY` | Configura Secrets en la app correcta y guarda. |
| Error de autenticación Groq | Revisa que la clave siga activa y esté copiada sin espacios. |
| Límite de consultas | Espera y revisa los límites de tu cuenta Groq. |
| No guarda permanentemente | Revisa el SQL de sesiones, URL y clave secreta del proyecto Supabase. |
| No aparece tu imagen | Sube `JARVIS.png` junto a `app.py`, con ese nombre exacto. |
| Se ve sin tipografía especial | Las fuentes de Google no cargaron; funciona con la alternativa local sans-serif. |
| La app carga la consola anterior | Cambia Main file path a `app.py`. |

## Referencias

1. Streamlit. Build a basic LLM chat app [Internet]. [citado 5 oct 2026]. Disponible en: https://docs.streamlit.io/develop/tutorials/chat-and-llm-apps/build-conversational-apps
2. Streamlit. Secrets management for your Community Cloud app [Internet]. [citado 5 oct 2026]. Disponible en: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management
3. Streamlit. Manage your app [Internet]. [citado 5 oct 2026]. Disponible en: https://docs.streamlit.io/deploy/streamlit-community-cloud/manage-your-app
4. Supabase. API keys [Internet]. [citado 5 oct 2026]. Disponible en: https://supabase.com/docs/guides/getting-started/api-keys
5. Groq. Supported models [Internet]. [citado 5 oct 2026]. Disponible en: https://console.groq.com/docs/models
