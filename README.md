# Consulta de Seguro — Verisure CI&C

App Streamlit para verificar si una instalación tiene seguro activo.

## Instalación

```bash
pip install -r requirements.txt
```

## Ejecución

```bash
streamlit run app.py
```

## Uso

1. En el panel izquierdo, sube el Excel o CSV exportado desde SharePoint (solo el archivo de instalaciones CON seguro)
2. Selecciona qué columna contiene el número de instalación
3. En el área principal, ingresa el número a consultar y haz clic en **Consultar**

### Lógica
- Si el número **está** en el archivo → ✅ **Tiene seguro activo**
- Si el número **no está** en el archivo → ❌ **No tiene seguro**

## Notas
- El archivo nunca sale del servidor; se procesa en memoria
- Acepta `.xlsx`, `.xls` y `.csv`
- La búsqueda es insensible a mayúsculas/minúsculas y espacios extras
- Se muestran hasta 6 campos adicionales del registro encontrado
