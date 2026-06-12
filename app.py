import streamlit as st
import pandas as pd
import hashlib
import requests
import json

# ── Configuración Supabase ───────────────────────────────────────────────────
SUPABASE_URL = "https://ngoxhgvuhmlyvugztjhh.supabase.co"
ANON_KEY     = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5nb3hoZ3Z1aG1seXZ1Z3p0amhoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQ1NTMxNzUsImV4cCI6MjA5MDEyOTE3NX0.dTa1DKQs69UbizjQLhBNA5IirDZMRcOpfkPRFaWZmOY"
SERVICE_KEY  = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5nb3hoZ3Z1aG1seXZ1Z3p0amhoIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NDU1MzE3NSwiZXhwIjoyMDkwMTI5MTc1fQ.hzYYA20ccer8hMtGNa-lxGhsj27sIzq2PVulZHBx9SM"
TABLE        = "seguros_activos"

def h(admin=False):
    key = SERVICE_KEY if admin else ANON_KEY
    return {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }

ADMIN_HASH = hashlib.sha256(b"Verisure2024!").hexdigest()
def check_password(pwd):
    return hashlib.sha256(pwd.encode()).hexdigest() == ADMIN_HASH

# ── Supabase helpers ──────────────────────────────────────────────────────────
def buscar(numero):
    url = f"{SUPABASE_URL}/rest/v1/{TABLE}?instalacion=eq.{numero}&limit=1"
    r = requests.get(url, headers=h(False))
    if r.status_code == 200:
        data = r.json()
        return data[0] if data else None
    return None

def contar():
    url = f"{SUPABASE_URL}/rest/v1/{TABLE}?select=id"
    r = requests.get(url, headers={**h(False), "Prefer": "count=exact", "Range": "0-0"})
    try:
        return int(r.headers.get("Content-Range", "0/0").split("/")[-1])
    except:
        return 0

def subir(registros):
    # 1. Borrar todos los registros actuales
    r = requests.delete(
        f"{SUPABASE_URL}/rest/v1/{TABLE}?id=gte.0",
        headers=h(True)
    )
    if r.status_code not in (200, 204):
        return False, f"Error al limpiar tabla: {r.text}"

    # 2. Insertar en lotes de 500
    for i in range(0, len(registros), 500):
        chunk = registros[i:i+500]
        r = requests.post(
            f"{SUPABASE_URL}/rest/v1/{TABLE}",
            headers=h(True),
            data=json.dumps(chunk)
        )
        if r.status_code not in (200, 201):
            return False, f"Error al insertar lote {i//500+1}: {r.text}"

    return True, f"{len(registros):,} registros cargados correctamente."

# ── Página ────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Consulta de Seguro", page_icon="🔒", layout="centered")

st.markdown("""
<style>
    .stApp { background-color: #0a0f1e; }
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding-top: 2.5rem; max-width: 580px; }

    .titulo-header { text-align: center; margin-bottom: 2rem; }
    .titulo-header h1 { color: #fff; font-size: 1.6rem; font-weight: 700; letter-spacing:.04em; margin-bottom:.2rem; }
    .titulo-header p  { color: #6b7a99; font-size:.88rem; margin:0; }

    .resultado-card { border-radius:12px; padding:1.6rem 2rem; margin-top:1.4rem; text-align:center; }
    .tiene-seguro   { background:linear-gradient(135deg,#0d2b1a,#0f3520); border:1px solid #1a6b3a; }
    .no-seguro      { background:linear-gradient(135deg,#2b0d0d,#350f0f); border:1px solid #6b1a1a; }
    .r-icon  { font-size:2.8rem; margin-bottom:.5rem; }
    .r-title { font-size:1.3rem; font-weight:700; margin-bottom:.3rem; }
    .tiene-seguro .r-title { color:#4ade80; }
    .no-seguro    .r-title { color:#f87171; }
    .r-sub   { font-size:.85rem; color:#9ca3af; }
    .r-extra { font-size:.82rem; margin-top:.8rem; padding-top:.8rem;
               border-top:1px solid rgba(255,255,255,.08); color:#d1d5db; line-height:1.9; }

    .stTextInput input {
        background:#111827 !important; border:1px solid #2d3748 !important;
        border-radius:8px !important; color:#fff !important;
        font-size:1rem !important; padding:.6rem 1rem !important;
    }
    .stTextInput input:focus { border-color:#3b82f6 !important; box-shadow:0 0 0 2px rgba(59,130,246,.2) !important; }

    .stButton>button {
        width:100%; background:linear-gradient(135deg,#1d4ed8,#2563eb);
        color:#fff; border:none; border-radius:8px; padding:.65rem;
        font-size:.95rem; font-weight:600; margin-top:.3rem;
    }
    .stButton>button:hover { opacity:.88; border:none; }

    [data-testid="stFileUploaderDropzone"] {
        background:#111827 !important; border:1px dashed #2d3748 !important; border-radius:8px !important;
    }
    [data-testid="stSidebar"] { background:#0d1424; border-right:1px solid #1e2a3a; }
    [data-testid="stSidebar"] * { color:#9ca3af; }

    .badge       { display:inline-block; background:#1e2a3a; border-radius:6px; padding:.2rem .7rem; font-size:.78rem; color:#6b7a99; margin-top:.4rem; }
    .badge-green { display:inline-block; background:#1a2e1a; border:1px solid #1a6b3a; border-radius:6px; padding:.2rem .8rem; font-size:.78rem; color:#4ade80; margin-bottom:.8rem; }
    label { color:#9ca3af !important; font-size:.85rem !important; }
    hr    { border-color:#1e2a3a; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="titulo-header">
    <h1>🔒 Consulta de Seguro</h1>
    <p>Verifica si una instalación tiene seguro activo</p>
</div>
""", unsafe_allow_html=True)

if "admin_ok" not in st.session_state:
    st.session_state.admin_ok = False

# ── Sidebar admin ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📂 Administrador")

    if not st.session_state.admin_ok:
        st.markdown("<small>Ingresa la contraseña para cargar datos.</small>", unsafe_allow_html=True)
        pwd = st.text_input("Contraseña", type="password", placeholder="••••••••", label_visibility="collapsed")
        if st.button("Ingresar"):
            if check_password(pwd):
                st.session_state.admin_ok = True
                st.rerun()
            else:
                st.error("Contraseña incorrecta.")
    else:
        st.markdown('<div class="badge-green">✅ Modo administrador</div>', unsafe_allow_html=True)

        total = contar()
        label = f"📦 {total:,} registros en Supabase" if total > 0 else "⚠️ Sin datos cargados aún"
        st.markdown(f'<div class="badge">{label}</div>', unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("**Cargar nuevo archivo:**")
        st.markdown("<small>Reemplaza todos los registros actuales.</small>", unsafe_allow_html=True)

        archivo = st.file_uploader("Archivo Excel o CSV", type=["xlsx","xls","csv"], label_visibility="collapsed")

        if archivo:
            try:
                df = pd.read_csv(archivo, dtype=str) if archivo.name.endswith(".csv") else pd.read_excel(archivo, dtype=str)
                df.columns = df.columns.str.strip()
                col = st.selectbox("Columna N° instalación", df.columns.tolist(), index=0)
                st.markdown(f"<small>{len(df):,} filas detectadas</small>", unsafe_allow_html=True)

                if st.button("⬆️ Subir a Supabase"):
                    cols_extra = [c for c in df.columns if c != col]
                    registros = []
                    for _, row in df.iterrows():
                        num = str(row[col]).strip().upper()
                        if num and num != "NAN":
                            # Columnas extra van todas dentro del campo JSON "datos"
                            datos_extra = {}
                            for c in cols_extra:
                                v = str(row[c]).strip()
                                if v and v != "nan":
                                    datos_extra[c] = v
                            registros.append({
                                "instalacion": num,
                                "datos": json.dumps(datos_extra, ensure_ascii=False)
                            })

                    with st.spinner(f"Subiendo {len(registros):,} registros..."):
                        ok, msg = subir(registros)
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

            except Exception as e:
                st.error(f"Error al leer el archivo: {e}")

        st.markdown("---")
        if st.button("Cerrar sesión"):
            st.session_state.admin_ok = False
            st.rerun()

    st.markdown("---")
    st.markdown("<small style='color:#3d4f6b'>Verisure Chile · CI&C</small>", unsafe_allow_html=True)

# ── Consulta principal ────────────────────────────────────────────────────────
num = st.text_input("Número de instalación", placeholder="Ej: 123456", max_chars=20)

if st.button("Consultar"):
    if not num.strip():
        st.warning("Ingresa un número de instalación.")
    else:
        with st.spinner("Consultando..."):
            res = buscar(num.strip().upper())

        if res is not None:
            # Mostrar campos extra del JSON si existen
            extra = ""
            if res.get("datos"):
                try:
                    datos = json.loads(res["datos"]) if isinstance(res["datos"], str) else res["datos"]
                    items = [f"<b>{k}:</b> {v}" for k, v in datos.items() if v and str(v) not in ("None","nan","")]
                    if items:
                        extra = '<div class="r-extra">' + "<br>".join(items) + "</div>"
                except:
                    pass

            st.markdown(f"""
            <div class="resultado-card tiene-seguro">
                <div class="r-icon">✅</div>
                <div class="r-title">Cliente tiene seguro activo</div>
                <div class="r-sub">Instalación N° {num.strip()}</div>
                {extra}
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="resultado-card no-seguro">
                <div class="r-icon">❌</div>
                <div class="r-title">Cliente no tiene seguro</div>
                <div class="r-sub">Instalación N° {num.strip()} — no encontrada en el registro</div>
            </div>""", unsafe_allow_html=True)
