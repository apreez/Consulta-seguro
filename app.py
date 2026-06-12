import streamlit as st
import pandas as pd
import hashlib

# ── Configuración de página ──────────────────────────────────────────────────
st.set_page_config(
    page_title="Consulta de Seguro",
    page_icon="🔒",
    layout="centered",
)

# ── Contraseña admin (cambiar aquí) ─────────────────────────────────────────
# Para cambiarla: reemplaza el string dentro de hashlib.sha256(b"TU_CLAVE_AQUI")
ADMIN_PASSWORD_HASH = hashlib.sha256(b"Verisure2024!").hexdigest()

def check_password(pwd: str) -> bool:
    return hashlib.sha256(pwd.encode()).hexdigest() == ADMIN_PASSWORD_HASH

# ── Estilos ──────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .stApp { background-color: #0a0f1e; }
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding-top: 2.5rem; max-width: 560px; }

    .titulo-header { text-align: center; margin-bottom: 2rem; }
    .titulo-header h1 { color: #ffffff; font-size: 1.6rem; font-weight: 700; letter-spacing: 0.04em; margin-bottom: 0.2rem; }
    .titulo-header p { color: #6b7a99; font-size: 0.88rem; margin: 0; }

    .resultado-card { border-radius: 12px; padding: 1.6rem 2rem; margin-top: 1.4rem; text-align: center; }
    .tiene-seguro { background: linear-gradient(135deg, #0d2b1a 0%, #0f3520 100%); border: 1px solid #1a6b3a; }
    .no-tiene-seguro { background: linear-gradient(135deg, #2b0d0d 0%, #350f0f 100%); border: 1px solid #6b1a1a; }
    .resultado-icon { font-size: 2.8rem; margin-bottom: 0.5rem; }
    .resultado-titulo { font-size: 1.3rem; font-weight: 700; margin-bottom: 0.3rem; }
    .tiene-seguro .resultado-titulo { color: #4ade80; }
    .no-tiene-seguro .resultado-titulo { color: #f87171; }
    .resultado-instalacion { font-size: 0.85rem; color: #9ca3af; }
    .resultado-detalle { font-size: 0.82rem; margin-top: 0.8rem; padding-top: 0.8rem; border-top: 1px solid rgba(255,255,255,0.08); color: #d1d5db; }

    .stTextInput input {
        background-color: #111827 !important; border: 1px solid #2d3748 !important;
        border-radius: 8px !important; color: #ffffff !important;
        font-size: 1rem !important; padding: 0.6rem 1rem !important; letter-spacing: 0.04em;
    }
    .stTextInput input:focus { border-color: #3b82f6 !important; box-shadow: 0 0 0 2px rgba(59,130,246,0.2) !important; }

    .stButton > button {
        width: 100%; background: linear-gradient(135deg, #1d4ed8, #2563eb);
        color: white; border: none; border-radius: 8px; padding: 0.65rem;
        font-size: 0.95rem; font-weight: 600; letter-spacing: 0.03em; transition: opacity 0.15s; margin-top: 0.3rem;
    }
    .stButton > button:hover { opacity: 0.88; border: none; }

    [data-testid="stFileUploaderDropzone"] {
        background-color: #111827 !important; border: 1px dashed #2d3748 !important; border-radius: 8px !important;
    }
    [data-testid="stSidebar"] { background-color: #0d1424; border-right: 1px solid #1e2a3a; }
    [data-testid="stSidebar"] * { color: #9ca3af; }

    .info-badge { display: inline-block; background: #1e2a3a; border-radius: 6px; padding: 0.2rem 0.7rem; font-size: 0.78rem; color: #6b7a99; margin-top: 0.6rem; }
    .admin-badge { display: inline-block; background: #1a2e1a; border: 1px solid #1a6b3a; border-radius: 6px; padding: 0.2rem 0.8rem; font-size: 0.78rem; color: #4ade80; margin-bottom: 0.8rem; }
    label { color: #9ca3af !important; font-size: 0.85rem !important; }
    hr { border-color: #1e2a3a; }

    /* Login box en sidebar */
    .login-box { background: #111827; border: 1px solid #2d3748; border-radius: 10px; padding: 1rem; margin-top: 0.5rem; }
</style>
""", unsafe_allow_html=True)


# ── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="titulo-header">
    <h1>🔒 Consulta de Seguro</h1>
    <p>Verifica si una instalación tiene seguro activo</p>
</div>
""", unsafe_allow_html=True)


# ── Estado de sesión ──────────────────────────────────────────────────────────
if "admin_ok" not in st.session_state:
    st.session_state.admin_ok = False
if "df_seguros" not in st.session_state:
    st.session_state.df_seguros = None
if "columna_instalacion" not in st.session_state:
    st.session_state.columna_instalacion = None


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📂 Cargar datos")

    if not st.session_state.admin_ok:
        st.markdown("<small>Acceso restringido. Ingresa la contraseña de administrador para cargar el archivo.</small>", unsafe_allow_html=True)
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        pwd_input = st.text_input("Contraseña", type="password", placeholder="••••••••", label_visibility="collapsed")
        if st.button("Ingresar"):
            if check_password(pwd_input):
                st.session_state.admin_ok = True
                st.rerun()
            else:
                st.error("Contraseña incorrecta.")
        st.markdown('</div>', unsafe_allow_html=True)

    else:
        st.markdown('<div class="admin-badge">✅ Modo administrador</div>', unsafe_allow_html=True)

        archivo = st.file_uploader(
            "Selecciona el archivo",
            type=["xlsx", "xls", "csv"],
            label_visibility="collapsed"
        )

        if archivo:
            try:
                if archivo.name.endswith(".csv"):
                    df_raw = pd.read_csv(archivo, dtype=str)
                else:
                    df_raw = pd.read_excel(archivo, dtype=str)

                df_raw.columns = df_raw.columns.str.strip()
                st.markdown("---")
                st.markdown("**Columna de N° instalación:**")

                columnas = list(df_raw.columns)
                col_sel = st.selectbox("Selecciona columna", columnas, index=0, label_visibility="collapsed")

                if col_sel:
                    df_norm = df_raw.copy()
                    df_norm["_instalacion_norm"] = (
                        df_norm[col_sel].astype(str).str.strip().str.upper()
                    )
                    st.session_state.df_seguros = df_norm
                    st.session_state.columna_instalacion = col_sel
                    total = len(df_norm)
                    st.markdown(f'<div class="info-badge">✅ {total:,} registros cargados</div>', unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Error al leer el archivo: {e}")

        if st.session_state.df_seguros is not None:
            st.markdown("---")
            if st.button("🗑️ Limpiar datos cargados"):
                st.session_state.df_seguros = None
                st.session_state.columna_instalacion = None
                st.rerun()

        st.markdown("---")
        if st.button("Cerrar sesión admin"):
            st.session_state.admin_ok = False
            st.rerun()

    st.markdown("---")
    st.markdown("<small style='color:#3d4f6b'>Verisure Chile · CI&C</small>", unsafe_allow_html=True)


# ── Área principal ────────────────────────────────────────────────────────────
df_seguros = st.session_state.df_seguros
columna_instalacion = st.session_state.columna_instalacion

if df_seguros is None:
    st.info("👈 El administrador debe cargar el archivo de seguros para habilitar las consultas.")
else:
    num_instalacion = st.text_input(
        "Número de instalación",
        placeholder="Ej: 123456",
        max_chars=20
    )

    buscar = st.button("Consultar")

    if buscar:
        if not num_instalacion.strip():
            st.warning("Ingresa un número de instalación.")
        else:
            query = num_instalacion.strip().upper()
            match = df_seguros[df_seguros["_instalacion_norm"] == query]

            if not match.empty:
                fila = match.iloc[0]
                cols_extra = [c for c in df_seguros.columns if c not in ("_instalacion_norm", columna_instalacion)]
                detalle_html = ""
                if cols_extra:
                    items = []
                    for col in cols_extra[:6]:
                        val = fila[col]
                        if pd.notna(val) and str(val).strip() not in ("", "nan"):
                            items.append(f"<b>{col}:</b> {val}")
                    if items:
                        detalle_html = f'<div class="resultado-detalle">{"&nbsp;&nbsp;|&nbsp;&nbsp;".join(items)}</div>'

                st.markdown(f"""
                <div class="resultado-card tiene-seguro">
                    <div class="resultado-icon">✅</div>
                    <div class="resultado-titulo">Cliente tiene seguro activo</div>
                    <div class="resultado-instalacion">Instalación N° {num_instalacion.strip()}</div>
                    {detalle_html}
                </div>
                """, unsafe_allow_html=True)

            else:
                st.markdown(f"""
                <div class="resultado-card no-tiene-seguro">
                    <div class="resultado-icon">❌</div>
                    <div class="resultado-titulo">Cliente no tiene seguro</div>
                    <div class="resultado-instalacion">Instalación N° {num_instalacion.strip()} — no encontrada en el registro</div>
                </div>
                """, unsafe_allow_html=True)
