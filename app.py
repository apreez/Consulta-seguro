import streamlit as st
import pandas as pd
import re

# ── Configuración de página ──────────────────────────────────────────────────
st.set_page_config(
    page_title="Consulta de Seguro",
    page_icon="🔒",
    layout="centered",
)

# ── Estilos ──────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Fondo general */
    .stApp {
        background-color: #0a0f1e;
    }

    /* Ocultar header/footer de Streamlit */
    #MainMenu, footer, header { visibility: hidden; }

    /* Contenedor principal */
    .block-container {
        padding-top: 2.5rem;
        max-width: 560px;
    }

    /* Logo / título */
    .titulo-header {
        text-align: center;
        margin-bottom: 2rem;
    }
    .titulo-header h1 {
        color: #ffffff;
        font-size: 1.6rem;
        font-weight: 700;
        letter-spacing: 0.04em;
        margin-bottom: 0.2rem;
    }
    .titulo-header p {
        color: #6b7a99;
        font-size: 0.88rem;
        margin: 0;
    }

    /* Card resultado */
    .resultado-card {
        border-radius: 12px;
        padding: 1.6rem 2rem;
        margin-top: 1.4rem;
        text-align: center;
    }
    .tiene-seguro {
        background: linear-gradient(135deg, #0d2b1a 0%, #0f3520 100%);
        border: 1px solid #1a6b3a;
    }
    .no-tiene-seguro {
        background: linear-gradient(135deg, #2b0d0d 0%, #350f0f 100%);
        border: 1px solid #6b1a1a;
    }
    .resultado-icon {
        font-size: 2.8rem;
        margin-bottom: 0.5rem;
    }
    .resultado-titulo {
        font-size: 1.3rem;
        font-weight: 700;
        margin-bottom: 0.3rem;
    }
    .tiene-seguro .resultado-titulo { color: #4ade80; }
    .no-tiene-seguro .resultado-titulo { color: #f87171; }
    .resultado-instalacion {
        font-size: 0.85rem;
        color: #9ca3af;
    }
    .resultado-detalle {
        font-size: 0.82rem;
        margin-top: 0.8rem;
        padding-top: 0.8rem;
        border-top: 1px solid rgba(255,255,255,0.08);
        color: #d1d5db;
    }

    /* Input personalizado */
    .stTextInput input {
        background-color: #111827 !important;
        border: 1px solid #2d3748 !important;
        border-radius: 8px !important;
        color: #ffffff !important;
        font-size: 1rem !important;
        padding: 0.6rem 1rem !important;
        letter-spacing: 0.08em;
    }
    .stTextInput input:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 2px rgba(59,130,246,0.2) !important;
    }

    /* Botón */
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #1d4ed8, #2563eb);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.65rem;
        font-size: 0.95rem;
        font-weight: 600;
        letter-spacing: 0.03em;
        transition: opacity 0.15s;
        margin-top: 0.3rem;
    }
    .stButton > button:hover {
        opacity: 0.88;
        border: none;
    }

    /* Upload zone */
    .stFileUploader {
        border-radius: 8px;
    }
    [data-testid="stFileUploaderDropzone"] {
        background-color: #111827 !important;
        border: 1px dashed #2d3748 !important;
        border-radius: 8px !important;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #0d1424;
        border-right: 1px solid #1e2a3a;
    }
    [data-testid="stSidebar"] * {
        color: #9ca3af;
    }

    /* Métricas pequeñas */
    .info-badge {
        display: inline-block;
        background: #1e2a3a;
        border-radius: 6px;
        padding: 0.2rem 0.7rem;
        font-size: 0.78rem;
        color: #6b7a99;
        margin-top: 0.6rem;
    }

    /* Label del input */
    label { color: #9ca3af !important; font-size: 0.85rem !important; }

    /* Divider */
    hr { border-color: #1e2a3a; }
</style>
""", unsafe_allow_html=True)


# ── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="titulo-header">
    <h1>🔒 Consulta de Seguro</h1>
    <p>Verifica si una instalación tiene seguro activo</p>
</div>
""", unsafe_allow_html=True)


# ── Sidebar: carga del archivo ────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📂 Archivo de seguros")
    st.markdown("<small>Sube el Excel o CSV exportado desde SharePoint</small>", unsafe_allow_html=True)

    archivo = st.file_uploader(
        "Selecciona el archivo",
        type=["xlsx", "xls", "csv"],
        label_visibility="collapsed"
    )

    columna_instalacion = None
    df_seguros = None

    if archivo:
        try:
            if archivo.name.endswith(".csv"):
                df_raw = pd.read_csv(archivo, dtype=str)
            else:
                df_raw = pd.read_excel(archivo, dtype=str)

            # Limpiar columnas
            df_raw.columns = df_raw.columns.str.strip()

            st.markdown("---")
            st.markdown("**Columnas detectadas:**")

            columnas = list(df_raw.columns)
            columna_instalacion = st.selectbox(
                "¿Cuál es la columna del N° de instalación?",
                columnas,
                index=0
            )

            if columna_instalacion:
                # Normalizar: quitar espacios, convertir a string limpio
                df_seguros = df_raw.copy()
                df_seguros["_instalacion_norm"] = (
                    df_seguros[columna_instalacion]
                    .astype(str)
                    .str.strip()
                    .str.upper()
                )
                total = len(df_seguros)
                st.markdown(f'<div class="info-badge">✅ {total:,} registros cargados</div>', unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Error al leer el archivo: {e}")

    st.markdown("---")
    st.markdown("<small style='color:#3d4f6b'>Verisure Chile · CI&C</small>", unsafe_allow_html=True)


# ── Área principal ────────────────────────────────────────────────────────────
if df_seguros is None:
    st.info("👈 Primero sube el archivo de seguros en el panel izquierdo.")
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

            # Búsqueda
            match = df_seguros[df_seguros["_instalacion_norm"] == query]

            if not match.empty:
                fila = match.iloc[0]

                # Armar detalle adicional (todas las columnas excepto la interna)
                cols_extra = [c for c in df_seguros.columns if c != "_instalacion_norm" and c != columna_instalacion]
                detalle_html = ""
                if cols_extra:
                    items = []
                    for col in cols_extra[:6]:  # máx 6 campos extra
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
