"""Entrada para Streamlit: streamlit run app.py."""

import base64
import hmac
import os
from pathlib import Path
from uuid import uuid4

import streamlit as st
from dotenv import load_dotenv

from basic_memory import BasicMemory
from catalogo import INDICADORES, PAISES, RUBROS, etiqueta
from jarvis_agent import JarvisAgent

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")
st.set_page_config(page_title="J.A.R.V.I.S. | Agente económico", page_icon="◈", layout="wide",
                   initial_sidebar_state="expanded")
st.markdown(f"<style>{(ROOT / 'assets/style.css').read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


def setting(name, default=""):
    """Secrets de Streamlit tienen prioridad sobre el entorno local."""
    try:
        value = st.secrets.get(name)
    except (FileNotFoundError, st.errors.StreamlitSecretNotFoundError):
        value = None
    return str(value if value is not None else os.environ.get(name, default)).strip()


def reset_chat():
    for name in ("memory", "agent", "messages", "session_id", "pending_prompt", "last_error"):
        st.session_state.pop(name, None)


def queue_prompt(prompt):
    st.session_state.pending_prompt = prompt


def render_hero():
    # No se depende de una URL externa ni de las mayúsculas del equipo del autor.
    # El nombre solicitado se conserva exactamente: JARVIS.png.
    image_path = ROOT / "JARVIS.png"
    if image_path.is_file():
        encoded = base64.b64encode(image_path.read_bytes()).decode("ascii")
        logo = f'<img class="brand-image" src="data:image/png;base64,{encoded}" alt="JARVIS, página principal del chat">'
    else:
        logo = '<div class="core" aria-label="JARVIS"><span>J</span></div>'
    st.markdown(f"""
    <div id="inicio" class="topline"><span class="home-label">CHAT PRINCIPAL</span><span class="top-index">ECONOMÍA / INTELIGENCIA</span></div>
    <section class="hero">
      <a class="logo-home" href="#inicio" aria-label="Ir al inicio del chat">{logo}</a>
      <div class="eyebrow">J.A.R.V.I.S.</div>
      <h1>La economía, a un<br>mensaje de distancia.</h1>
      <p>Explora indicadores, conecta ideas y entiende lo que mueve al mundo.<br>Tu agente económico, con Guatemala como punto de partida.</p>
      <div class="hero-rule"></div>
    </section>
    <div class="overview"><span><i></i>{len(INDICADORES)} indicadores macro</span><span><i></i>{len(RUBROS)} rubros económicos</span><span><i></i>Fuentes en cada consulta</span></div>
    """, unsafe_allow_html=True)


password = setting("APP_PASSWORD")
if password and not st.session_state.get("access_ok"):
    render_hero()
    _, center, _ = st.columns([1, 2, 1])
    with center:
        with st.form("access_form"):
            st.markdown("**Entra a tu espacio de consulta**")
            supplied = st.text_input("Contraseña de acceso", type="password")
            submitted = st.form_submit_button("Entrar a JARVIS", type="primary", use_container_width=True)
        if submitted:
            if hmac.compare_digest(supplied.encode("utf-8"), password.encode("utf-8")):
                st.session_state.access_ok = True
                st.rerun()
            st.error("La contraseña no coincide. Inténtalo de nuevo.")
    st.stop()

api_key = setting("GROQ_API_KEY")
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid4())
if "memory" not in st.session_state:
    st.session_state.memory = BasicMemory(
        st.session_state.session_id, max_messages=20,
        supabase_url=setting("SUPABASE_URL"), supabase_key=setting("SUPABASE_KEY"),
    )
if "messages" not in st.session_state:
    st.session_state.messages = st.session_state.memory.messages()

with st.sidebar:
    st.markdown('<div class="side-brand"><div class="side-mark">J</div><div><strong>JARVIS</strong><small>ECONOMIC INTELLIGENCE</small></div></div>', unsafe_allow_html=True)
    st.button("Nueva conversación", icon=":material/add:", use_container_width=True, on_click=reset_chat)
    st.markdown('<div class="side-section">EXPLORA LA ECONOMÍA</div>', unsafe_allow_html=True)
    rubro = st.selectbox("Rubro", list(RUBROS), index=1)
    if rubro == "Divisas":
        base = st.selectbox("Moneda de origen", ["USD", "GTQ", "EUR", "MXN", "GBP", "CAD", "JPY"])
        target = st.selectbox("Moneda de destino", ["GTQ", "USD", "EUR", "MXN", "GBP", "CAD", "JPY"])
        guided = f"¿Cuántos {target} equivalen a 1 {base}? Indica la fecha y la fuente de la tasa."
    elif rubro == "Criptoactivos":
        crypto = st.selectbox("Criptoactivo", ["Bitcoin", "Ethereum", "Solana", "Dogecoin"])
        guided = f"Consulta el precio de {crypto} en dólares e indica fecha y fuente."
    else:
        indicator = st.selectbox("Indicador", RUBROS[rubro], format_func=etiqueta)
        country = st.selectbox("País", [*PAISES, "Otro país (código ISO)"])
        code = PAISES.get(country)
        if code is None:
            code = st.text_input("Código ISO de tres letras", max_chars=3, placeholder="Ejemplo: FRA").strip().upper()
            country = code
        guided = f"Consulta {etiqueta(indicator).lower()} de {country} ({code}), indicador {indicator}. Incluye último valor disponible, año, unidad y fuente; explica si hay rezago o estimación."
    valid_code = rubro in ("Divisas", "Criptoactivos") or (len(code or "") == 3 and code.isascii() and code.isalpha())
    st.button("Consultar indicador", type="primary", icon=":material/arrow_forward:", use_container_width=True,
              on_click=queue_prompt, args=(guided,), disabled=not api_key or not valid_code)
    st.markdown('<div class="side-note">También puedes preguntar con tus palabras o comparar países directamente en el chat.</div>', unsafe_allow_html=True)
    st.divider()
    st.markdown('<div class="side-section">TU CONVERSACIÓN</div>', unsafe_allow_html=True)
    transcript = "# Conversación con J.A.R.V.I.S.\n\n" + "\n\n".join(
        f"**{'Tú' if m['role'] == 'user' else 'JARVIS'}**\n\n{m['content']}" for m in st.session_state.messages)
    st.download_button("Descargar conversación", transcript, file_name="conversacion_jarvis.md", mime="text/markdown",
                       icon=":material/download:", use_container_width=True, disabled=not st.session_state.messages)
    with st.expander("Qué puedes consultar"):
        st.markdown("**Macroeconomía:** producción, precios, empleo, finanzas públicas, sector externo, inversión, consumo y población.\n\n**Mercados:** divisas y cuatro criptoactivos.\n\nCada fuente publica con una frecuencia distinta; JARVIS muestra el año o fecha del dato.")
    st.markdown('<div class="sidebar-foot">JUST A RATIONAL VALUATION<br>& INTELLIGENT SYSTEM</div>', unsafe_allow_html=True)
    if password:
        if st.button("Cerrar sesión", icon=":material/logout:", use_container_width=True):
            reset_chat()
            st.session_state.access_ok = False
            st.rerun()

render_hero()

if not api_key:
    st.info("La interfaz está lista. Configura GROQ_API_KEY en los Secrets de la aplicación para activar las respuestas.")

quick_area = st.empty()
if not st.session_state.messages:
    with quick_area.container():
        st.markdown('<div class="section-label"><span>UN PUNTO DE PARTIDA</span><span>ELIGE UNA CONSULTA O CREA LA TUYA</span></div>', unsafe_allow_html=True)
        first, second = st.columns(2)
        with first:
            st.button("Inflación de Guatemala", key="quick_inflacion", icon=":material/trending_up:", use_container_width=True,
                      on_click=queue_prompt, args=("¿Cuál es la inflación más reciente publicada para Guatemala? Incluye año, unidad y fuente.",), disabled=not api_key)
            st.button("Crecimiento del PIB", key="quick_pib", icon=":material/bar_chart:", use_container_width=True,
                      on_click=queue_prompt, args=("¿Cuánto creció el PIB real de Guatemala en el último año disponible? Explica brevemente e indica fuente.",), disabled=not api_key)
        with second:
            st.button("Del dólar al quetzal", key="quick_cambio", icon=":material/currency_exchange:", use_container_width=True,
                      on_click=queue_prompt, args=("¿Cuántos quetzales equivalen a 1 dólar? Incluye fecha y fuente.",), disabled=not api_key)
            st.button("Deuda pública y contexto", key="quick_deuda", icon=":material/account_balance:", use_container_width=True,
                      on_click=queue_prompt, args=("Consulta la deuda bruta del gobierno general de Guatemala según el FMI. Explica el porcentaje del PIB y si puede ser una estimación.",), disabled=not api_key)
        st.markdown('<div class="welcome"><div class="intro-line"><i></i>J.A.R.V.I.S. / TU AGENTE ECONÓMICO</div><h3>¿Qué quieres entender hoy?</h3><p>Podemos empezar con un dato, comparar economías o aclarar un concepto.<br>Por ejemplo: «Compara la inflación de Guatemala y México».</p></div>', unsafe_allow_html=True)

for message in st.session_state.messages:
    avatar = ":material/person:" if message["role"] == "user" else ":material/neurology:"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])
        if message.get("sources"):
            with st.expander("Fuentes consultadas"):
                for source in message["sources"]:
                    st.markdown(f"- [{source['nombre']}]({source['url']})")

pending = st.session_state.pop("pending_prompt", None)
with st.container():
    typed = st.chat_input("Pregunta sobre la economía…", max_chars=3000, disabled=not api_key)
st.markdown('<div class="input-note">Los indicadores tienen distintas fechas de publicación. Revisa siempre el período y la fuente.</div>', unsafe_allow_html=True)

prompt = pending or typed
if prompt and api_key:
    quick_area.empty()
    with st.chat_message("user", avatar=":material/person:"):
        st.markdown(prompt)
    try:
        if "agent" not in st.session_state:
            st.session_state.agent = JarvisAgent(api_key, model=setting("GROQ_MODEL", "openai/gpt-oss-120b"))
        with st.chat_message("assistant", avatar=":material/neurology:"):
            with st.status("JARVIS está preparando tu respuesta…", expanded=False) as status:
                answer, sources = st.session_state.agent.answer(
                    prompt, st.session_state.memory.messages(), on_status=lambda label: status.update(label=label))
                status.update(label="Consulta completada", state="complete")
            st.markdown(answer)
        st.session_state.memory.add_turn(prompt, answer)
        st.session_state.messages.extend([
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": answer, "sources": sources},
        ])
        st.session_state.messages = st.session_state.messages[-100:]
        st.rerun()
    except Exception as exc:
        # Mensajes accionables, sin imprimir errores que puedan incluir secretos.
        kind = type(exc).__name__
        if kind == "AuthenticationError":
            st.error("No se pudo autenticar con Groq. Revisa la clave configurada en Secrets.")
        elif kind == "RateLimitError":
            st.warning("Se alcanzó el límite de consultas de Groq. Espera un momento e inténtalo de nuevo.")
        elif kind in ("APITimeoutError", "APIConnectionError"):
            st.warning("La conexión tardó demasiado. Vuelve a enviar tu pregunta.")
        else:
            st.error("No se pudo completar la respuesta. Revisa la configuración del modelo y vuelve a intentarlo.")

if st.session_state.memory.persistence_error:
    st.caption("El chat conserva el contexto en esta sesión, pero no pudo guardar el historial permanente.")
st.markdown('<div class="page-foot"><span>J.A.R.V.I.S. · UNA PERSPECTIVA MÁS CLARA</span><i></i><span>HECHO PARA EXPLORAR</span></div>', unsafe_allow_html=True)
