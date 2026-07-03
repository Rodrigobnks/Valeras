import base64
import json
import re
import unicodedata
import urllib.request
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

try:
    from streamlit_plotly_events import plotly_events
except Exception:
    plotly_events = None


# ======================================================
# CONFIGURACIÓN GENERAL
# ======================================================
st.set_page_config(
    page_title="Valeras",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="collapsed",
)

BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"

FONDO = ASSETS_DIR / "fondo_caprepa.png"
ARCHIVO_ESTRUCTURA = BASE_DIR / "Estructura vales.xlsx"
ARCHIVO_DISTRIBUIDORAS_MX = BASE_DIR / "Distribuidoras Vale MX.csv"
ARCHIVO_DISPERSION = BASE_DIR / "Dispersion diaria.csv"
ARCHIVO_PLAZO_COMPOSICION = BASE_DIR / "Plazo y composicion de dispersión.csv"
ARCHIVO_GEOJSON_MX = BASE_DIR / "mexico_estados.geojson"
ARCHIVO_GEOJSON_PE = BASE_DIR / "peru_departamentos.geojson"
ARCHIVO_GEOJSON_MUN_MX = BASE_DIR / "mexico_municipios.geojson"


# ======================================================
# UTILIDADES DE IMAGEN
# ======================================================
def image_to_base64(path: Path) -> str:
    with open(path, "rb") as file:
        return base64.b64encode(file.read()).decode("utf-8")


def image_mime(path: Path) -> str:
    suffix = path.suffix.lower()

    if suffix in [".jpg", ".jpeg"]:
        return "image/jpeg"

    if suffix == ".webp":
        return "image/webp"

    return "image/png"


def img_src(path: Path) -> str:
    if not path.exists():
        return ""

    return f"data:{image_mime(path)};base64,{image_to_base64(path)}"


def buscar_asset(nombres: list[str]) -> Path:
    # Busca primero dentro de assets/ y después en la raíz del repositorio.
    # Esto permite que los logos funcionen aunque se hayan subido sueltos a GitHub.
    for nombre in nombres:
        ruta = ASSETS_DIR / nombre
        if ruta.exists():
            return ruta

        ruta = BASE_DIR / nombre
        if ruta.exists():
            return ruta

    return ASSETS_DIR / nombres[0]


# ======================================================
# TARJETAS DE ENTRADA
# ======================================================
VALES = [
    {
        "nombre": "Vale Amigo",
        "logo": buscar_asset(
            [
                "logo_vale_amigo.jpg",
                "logo_vale_amigo.png",
                "logo_vale_amigo.jpeg",
            ]
        ),
        "param": "vale_amigo",
        "carteras": ["Vale Amigo"],
        "pais_exclusivo": "MÉXICO",
        "usar_distribuidoras_mx": True,
        "stagger": "stagger-1",
    },
    {
        "nombre": "Viva Vale",
        "logo": buscar_asset(
            [
                "logo_viva_vale.jpg",
                "logo_viva_vale.png",
                "logo_viva_vale.jpeg",
            ]
        ),
        "param": "viva_vale",
        "carteras": ["Viva Vale"],
        "pais_exclusivo": None,
        "usar_distribuidoras_mx": False,
        "stagger": "stagger-2",
    },
    {
        "nombre": "Rapivale",
        "logo": buscar_asset(
            [
                "logo_rapivale.png",
                "logo_rapivale.jpg",
                "logo_rapivale.jpeg",
            ]
        ),
        "param": "rapivale",
        "carteras": ["RapiVale", "Rapivale"],
        "pais_exclusivo": None,
        "usar_distribuidoras_mx": False,
        "stagger": "stagger-3",
    },
    {
        "nombre": "Vale Amigo Perú",
        "logo": buscar_asset(
            [
                "logo_vale_amigo_peru.jpeg.jpeg",
                "logo_vale_amigo_peru.jpeg",
                "logo_vale_amigo_peru.jpg",
                "logo_vale_amigo_peru.png",
                "WhatsApp Image 2026-06-26 at 12.26.08 PM.jpeg",
            ]
        ),
        "param": "vale_amigo_peru",
        "carteras": ["Vale Perú", "Vale Peru", "Vale Amigo"],
        "pais_exclusivo": "PERÚ",
        "usar_distribuidoras_mx": False,
        "stagger": "stagger-4",
    },
]


# ======================================================
# COORDENADAS Y ESTADOS POR SUCURSAL
# ======================================================
COORDS_SUCURSAL = {
    "ACAPONETA": (22.4964, -105.3594),
    "ACAPULCO": (16.8531, -99.8237),
    "ACAYUCAN": (17.9498, -94.9146),
    "ACUNA": (29.3232, -100.9522),
    "ALTAMIRA": (22.3922, -97.9387),
    "CABO SAN LUCAS": (22.8905, -109.9167),
    "CABORCA": (30.7186, -112.1594),
    "CADEREYTA": (25.5906, -100.0010),
    "CAMARGO": (27.6784, -105.1714),
    "CANANEA": (30.9869, -110.2900),
    "CARDENAS": (18.0013, -93.3756),
    "CARDENAS 2": (18.0013, -93.3756),
    "CASAS GRANDES": (30.3744, -107.9514),
    "CD MANTE": (22.7430, -98.9739),
    "CIUDAD MANTE": (22.7430, -98.9739),
    "CD VICTORIA": (23.7369, -99.1411),
    "CIUDAD VICTORIA": (23.7369, -99.1411),
    "CD JUAREZ": (31.6904, -106.4245),
    "CD JUAREZ 2": (31.6904, -106.4245),
    "CD CONSTITUCION": (25.0321, -111.6707),
    "CELAYA": (20.5235, -100.8157),
    "CENTLA": (18.5344, -92.6469),
    "CHIHUAHUA": (28.6320, -106.0691),
    "CHIHUAHUA CENTRO": (28.6320, -106.0691),
    "CHIHUAHUA SUR": (28.6320, -106.0691),
    "CHIHUAHUA NORTE": (28.6320, -106.0691),
    "CHILPANCINGO": (17.5515, -99.5006),
    "CIUDAD VALLES": (21.9963, -99.0109),
    "COATZACOALCOS": (18.1345, -94.4589),
    "COATZACOALCOS 2": (18.1345, -94.4589),
    "COMALCALCO": (18.2632, -93.2237),
    "COMITAN": (16.2510, -92.1340),
    "COMPOSTELA": (21.2378, -104.9000),
    "CORDOBA": (18.8842, -96.9256),
    "COSTA RICA": (24.5965, -107.3898),
    "COYUCA DE BENITEZ": (17.0087, -100.0871),
    "CUAUHTEMOC": (28.4050, -106.8667),
    "CULIACAN": (24.8091, -107.3940),
    "CULIACAN CENTRO": (24.8091, -107.3940),
    "CULIACAN SAN ISIDRO": (24.8091, -107.3940),
    "DELICIAS": (28.1901, -105.4701),
    "DURANGO": (24.0277, -104.6532),
    "EJECUTIVO PATZCUARO": (19.5159, -101.6091),
    "EL DORADO": (24.3239, -107.3614),
    "EL SALTO": (23.7808, -105.3619),
    "EMPALME": (27.9617, -110.8144),
    "ENSENADA": (31.8667, -116.5964),
    "ESCARCEGA": (18.6089, -90.7454),
    "ESCUINAPA": (22.8328, -105.7777),
    "FRESNILLO": (23.1757, -102.8666),
    "GUADALUPE VICTORIA": (24.4455, -104.1235),
    "GUAMUCHIL": (25.4587, -108.0773),
    "GUAYMAS": (27.9187, -110.8975),
    "HERMOSILLO": (29.0729, -110.9559),
    "HUACHINANGO": (20.1760, -98.0540),
    "HUATABAMPO": (26.8261, -109.6428),
    "HUATULCO": (15.7753, -96.2626),
    "HUEJUTLA": (21.1400, -98.4194),
    "IGUALA": (18.3454, -99.5413),
    "IMURIS": (30.7861, -110.8456),
    "IRAPUATO": (20.6787, -101.3544),
    "IXTEPEC": (16.5613, -95.1024),
    "JEREZ": (22.6497, -102.9903),
    "JIMENEZ": (27.1306, -104.9072),
    "JONUTA": (18.0894, -92.1383),
    "JUCHITAN": (16.4360, -95.0197),
    "LA CRUZ": (23.9214, -106.8928),
    "LA PAZ": (24.1426, -110.3128),
    "LA PAZ 2": (24.1426, -110.3128),
    "LA PAZ 3": (24.1426, -110.3128),
    "LA PAZ 4": (24.1426, -110.3128),
    "LINARES": (24.8578, -99.5677),
    "LORETO": (26.0111, -111.3447),
    "LOS CABOS": (22.8905, -109.9167),
    "MACUSPANA": (17.7605, -92.5954),
    "MAGDALENA": (30.6279, -110.9627),
    "MARTINEZ DE LA TORRE": (20.0708, -97.0608),
    "MATAMOROS": (25.8690, -97.5027),
    "MATEHUALA": (23.6482, -100.6433),
    "MATIAS ROMERO": (16.8796, -95.0399),
    "MAZATLAN": (23.2494, -106.4111),
    "MAZATLAN CENTRO": (23.2494, -106.4111),
    "MEOQUI": (28.2721, -105.4825),
    "MEXICALI": (32.6245, -115.4523),
    "MEZCALES": (20.7330, -105.2820),
    "MINATITLAN": (17.9869, -94.5561),
    "MINATITLAN 1": (17.9869, -94.5561),
    "MONCLOVA": (26.9080, -101.4216),
    "MORELIA": (19.7008, -101.1844),
    "NAVOJOA": (27.0728, -109.4437),
    "NAVOLATO": (24.7672, -107.6961),
    "NOGALES": (31.3012, -110.9381),
    "OBREGON CENTRO": (27.4864, -109.9408),
    "OBREGON CENTRO 1": (27.4864, -109.9408),
    "OBREGON ESPERANZA": (27.4864, -109.9408),
    "OBREGON PERISUR": (27.4864, -109.9408),
    "ORIZABA": (18.8516, -97.0990),
    "PALENQUE": (17.5100, -91.9825),
    "PAPANTLA": (20.4465, -97.3249),
    "PARAISO": (18.4006, -93.2142),
    "PARRAL": (26.9329, -105.6660),
    "PARRAS": (25.4419, -102.1799),
    "PIEDRAS NEGRAS": (28.7001, -100.5235),
    "PINOTEPA NACIONAL": (16.3412, -98.0537),
    "POZA RICA": (20.5333, -97.4500),
    "POZA RICA 2": (20.5333, -97.4500),
    "PUERTO ESCONDIDO": (15.8719, -97.0767),
    "PUERTO PENASCO": (31.3268, -113.5312),
    "REYNOSA": (26.0922, -98.2778),
    "RIO GRANDE": (23.8265, -103.0306),
    "ROSA MORADA": (22.1247, -105.2058),
    "ROSARIO": (22.9928, -105.8569),
    "ROSARITO": (32.3661, -117.0618),
    "RUIZ": (21.9514, -105.1433),
    "SALINA CRUZ": (16.1840, -95.2018),
    "SALTILLO": (25.4380, -100.9737),
    "SAN ANDRES TUXTLA": (18.4487, -95.2133),
    "SAN JOSE DEL CABO": (23.0614, -109.7080),
    "SAN LUIS": (22.1565, -100.9855),
    "SAN LUIS POTOSI": (22.1565, -100.9855),
    "SAN LUIS RIO COLORADO": (32.4561, -114.7719),
    "SAN PEDRO": (25.7575, -102.9838),
    "SAN QUINTIN": (30.5608, -115.9403),
    "SANTA ANA": (30.5408, -111.1192),
    "SANTA ROSALIA": (27.3365, -112.2676),
    "SANTIAGO IXCUINTLA": (21.8125, -105.2071),
    "SANTIAGO PAPASQUIARO": (25.0436, -105.4208),
    "TAMPICO": (22.2553, -97.8686),
    "TAMPICO CENTRO": (22.2553, -97.8686),
    "TAMPICO MADERO": (22.2475, -97.8364),
    "TAMPICO NORTE": (22.2553, -97.8686),
    "TAPACHULA": (14.9056, -92.2634),
    "TEAPA": (17.5497, -92.9521),
    "TECATE": (32.5668, -116.6254),
    "TECUALA": (22.3978, -105.4569),
    "TEHUANTEPEC": (16.3246, -95.2410),
    "TEPIC": (21.5042, -104.8946),
    "TIJUANA": (32.5149, -117.0382),
    "TIJUANA 2": (32.5149, -117.0382),
    "TONALA": (16.0898, -93.7548),
    "TUXPAN": (20.9577, -97.4081),
    "TUXPAN NAYARIT": (21.9438, -105.2989),
    "TUXTLA GUTIERREZ": (16.7516, -93.1160),
    "URUAPAN": (19.4208, -102.0628),
    "VALLARTA": (20.6534, -105.2253),
    "VERACRUZ": (19.1738, -96.1342),
    "VERACRUZ CENTRO": (19.1738, -96.1342),
    "VERACRUZ NORTE": (19.1738, -96.1342),
    "VERACRUZ SUR": (19.1738, -96.1342),
    "VILLA FLORES": (16.2333, -93.2667),
    "VILLAHERMOSA": (17.9892, -92.9475),
    "VILLAHERMOSA 2": (17.9892, -92.9475),
    "VIZCAINO": (27.6500, -113.3833),
    "XALAPA": (19.5438, -96.9102),
    "ZACATECAS": (22.7709, -102.5832),

    # PERÚ
    "EL PORVENIR": (-8.0833, -79.0000),
    "LA ESPERANZA": (-8.0725, -79.0458),
    "LAREDO": (-8.0897, -78.9600),
    "TRUJILLO": (-8.1116, -79.0287),
}


ESTADO_SUCURSAL = {
    "ACAPONETA": "Nayarit",
    "ACAPULCO": "Guerrero",
    "ACAYUCAN": "Veracruz",
    "ACUNA": "Coahuila",
    "ALTAMIRA": "Tamaulipas",
    "CABO SAN LUCAS": "Baja California Sur",
    "CABORCA": "Sonora",
    "CADEREYTA": "Nuevo León",
    "CAMARGO": "Chihuahua",
    "CANANEA": "Sonora",
    "CARDENAS": "Tabasco",
    "CARDENAS 2": "Tabasco",
    "CASAS GRANDES": "Chihuahua",
    "CD MANTE": "Tamaulipas",
    "CIUDAD MANTE": "Tamaulipas",
    "CD VICTORIA": "Tamaulipas",
    "CIUDAD VICTORIA": "Tamaulipas",
    "CD JUAREZ": "Chihuahua",
    "CD JUAREZ 2": "Chihuahua",
    "CD CONSTITUCION": "Baja California Sur",
    "CELAYA": "Guanajuato",
    "CENTLA": "Tabasco",
    "CHIHUAHUA": "Chihuahua",
    "CHIHUAHUA CENTRO": "Chihuahua",
    "CHIHUAHUA SUR": "Chihuahua",
    "CHIHUAHUA NORTE": "Chihuahua",
    "CHILPANCINGO": "Guerrero",
    "CIUDAD VALLES": "San Luis Potosí",
    "COATZACOALCOS": "Veracruz",
    "COATZACOALCOS 2": "Veracruz",
    "COMALCALCO": "Tabasco",
    "COMITAN": "Chiapas",
    "COMPOSTELA": "Nayarit",
    "CORDOBA": "Veracruz",
    "COSTA RICA": "Sinaloa",
    "COYUCA DE BENITEZ": "Guerrero",
    "CUAUHTEMOC": "Chihuahua",
    "CULIACAN": "Sinaloa",
    "CULIACAN CENTRO": "Sinaloa",
    "CULIACAN SAN ISIDRO": "Sinaloa",
    "DELICIAS": "Chihuahua",
    "DURANGO": "Durango",
    "EJECUTIVO PATZCUARO": "Michoacán",
    "EL DORADO": "Sinaloa",
    "EL SALTO": "Durango",
    "EMPALME": "Sonora",
    "ENSENADA": "Baja California",
    "ESCARCEGA": "Campeche",
    "ESCUINAPA": "Sinaloa",
    "FRESNILLO": "Zacatecas",
    "GUADALUPE VICTORIA": "Durango",
    "GUAMUCHIL": "Sinaloa",
    "GUAYMAS": "Sonora",
    "HERMOSILLO": "Sonora",
    "HUACHINANGO": "Puebla",
    "HUATABAMPO": "Sonora",
    "HUATULCO": "Oaxaca",
    "HUEJUTLA": "Hidalgo",
    "IGUALA": "Guerrero",
    "IMURIS": "Sonora",
    "IRAPUATO": "Guanajuato",
    "IXTEPEC": "Oaxaca",
    "JEREZ": "Zacatecas",
    "JIMENEZ": "Chihuahua",
    "JONUTA": "Tabasco",
    "JUCHITAN": "Oaxaca",
    "LA CRUZ": "Sinaloa",
    "LA PAZ": "Baja California Sur",
    "LA PAZ 2": "Baja California Sur",
    "LA PAZ 3": "Baja California Sur",
    "LA PAZ 4": "Baja California Sur",
    "LINARES": "Nuevo León",
    "LORETO": "Baja California Sur",
    "LOS CABOS": "Baja California Sur",
    "MACUSPANA": "Tabasco",
    "MAGDALENA": "Sonora",
    "MARTINEZ DE LA TORRE": "Veracruz",
    "MATAMOROS": "Tamaulipas",
    "MATEHUALA": "San Luis Potosí",
    "MATIAS ROMERO": "Oaxaca",
    "MAZATLAN": "Sinaloa",
    "MAZATLAN CENTRO": "Sinaloa",
    "MEOQUI": "Chihuahua",
    "MEXICALI": "Baja California",
    "MEZCALES": "Nayarit",
    "MINATITLAN": "Veracruz",
    "MINATITLAN 1": "Veracruz",
    "MONCLOVA": "Coahuila",
    "MORELIA": "Michoacán",
    "NAVOJOA": "Sonora",
    "NAVOLATO": "Sinaloa",
    "NOGALES": "Sonora",
    "OBREGON CENTRO": "Sonora",
    "OBREGON CENTRO 1": "Sonora",
    "OBREGON ESPERANZA": "Sonora",
    "OBREGON PERISUR": "Sonora",
    "ORIZABA": "Veracruz",
    "PALENQUE": "Chiapas",
    "PAPANTLA": "Veracruz",
    "PARAISO": "Tabasco",
    "PARRAL": "Chihuahua",
    "PARRAS": "Coahuila",
    "PIEDRAS NEGRAS": "Coahuila",
    "PINOTEPA NACIONAL": "Oaxaca",
    "POZA RICA": "Veracruz",
    "POZA RICA 2": "Veracruz",
    "PUERTO ESCONDIDO": "Oaxaca",
    "PUERTO PENASCO": "Sonora",
    "REYNOSA": "Tamaulipas",
    "RIO GRANDE": "Zacatecas",
    "ROSA MORADA": "Nayarit",
    "ROSARIO": "Sinaloa",
    "ROSARITO": "Baja California",
    "RUIZ": "Nayarit",
    "SALINA CRUZ": "Oaxaca",
    "SALTILLO": "Coahuila",
    "SAN ANDRES TUXTLA": "Veracruz",
    "SAN JOSE DEL CABO": "Baja California Sur",
    "SAN LUIS": "San Luis Potosí",
    "SAN LUIS POTOSI": "San Luis Potosí",
    "SAN LUIS RIO COLORADO": "Sonora",
    "SAN PEDRO": "Coahuila",
    "SAN QUINTIN": "Baja California",
    "SANTA ANA": "Sonora",
    "SANTA ROSALIA": "Baja California Sur",
    "SANTIAGO IXCUINTLA": "Nayarit",
    "SANTIAGO PAPASQUIARO": "Durango",
    "TAMPICO": "Tamaulipas",
    "TAMPICO CENTRO": "Tamaulipas",
    "TAMPICO MADERO": "Tamaulipas",
    "TAMPICO NORTE": "Tamaulipas",
    "TAPACHULA": "Chiapas",
    "TEAPA": "Tabasco",
    "TECATE": "Baja California",
    "TECUALA": "Nayarit",
    "TEHUANTEPEC": "Oaxaca",
    "TEPIC": "Nayarit",
    "TIJUANA": "Baja California",
    "TIJUANA 2": "Baja California",
    "TONALA": "Chiapas",
    "TUXPAN": "Veracruz",
    "TUXPAN NAYARIT": "Nayarit",
    "TUXTLA GUTIERREZ": "Chiapas",
    "URUAPAN": "Michoacán",
    "VALLARTA": "Jalisco",
    "VERACRUZ": "Veracruz",
    "VERACRUZ CENTRO": "Veracruz",
    "VERACRUZ NORTE": "Veracruz",
    "VERACRUZ SUR": "Veracruz",
    "VILLA FLORES": "Chiapas",
    "VILLAHERMOSA": "Tabasco",
    "VILLAHERMOSA 2": "Tabasco",
    "VIZCAINO": "Baja California Sur",
    "XALAPA": "Veracruz",
    "ZACATECAS": "Zacatecas",

    # PERÚ
    "EL PORVENIR": "La Libertad",
    "LA ESPERANZA": "La Libertad",
    "LAREDO": "La Libertad",
    "TRUJILLO": "La Libertad",
}


# ======================================================
# UTILIDADES DE TEXTO Y DATOS
# ======================================================
def limpiar_texto(valor) -> str:
    if pd.isna(valor):
        return ""

    texto = str(valor).strip()
    texto = arreglar_mojibake(texto)
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    texto = texto.upper()
    texto = re.sub(r"\s+", " ", texto)
    return texto.strip()


def arreglar_mojibake(texto: str) -> str:
    if not isinstance(texto, str):
        return texto

    try:
        return texto.encode("latin1").decode("utf-8")
    except Exception:
        return texto


def normalizar_sucursal(valor) -> str:
    texto = limpiar_texto(valor)
    texto = texto.replace(".", "")
    texto = texto.replace(" DIGITAL", "")
    texto = texto.replace("CIUDAD JUAREZ", "CD JUAREZ")
    texto = texto.replace("CD JUAREZ", "CD JUAREZ")
    texto = texto.replace("CD CONSTITUCION", "CD CONSTITUCION")
    texto = texto.replace("POR ASIGNAR", "")
    texto = texto.strip()
    return texto


def detectar_pais(row) -> str:
    texto = " ".join(
        [
            limpiar_texto(row.get("Marca", "")),
            limpiar_texto(row.get("Dir", "")),
            limpiar_texto(row.get("Subdirección", "")),
            limpiar_texto(row.get("Zona", "")),
            limpiar_texto(row.get("Sucursal", "")),
            limpiar_texto(row.get("Red", "")),
            limpiar_texto(row.get("Cartera", "")),
        ]
    )

    if "PERU" in texto:
        return "PERÚ"

    return "MÉXICO"


def aplicar_coordenadas_y_estado(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    latitudes = []
    longitudes = []
    suc_norm = []
    estados = []

    for sucursal in df["Sucursal"]:
        clave = normalizar_sucursal(sucursal)
        suc_norm.append(clave)

        coords = COORDS_SUCURSAL.get(clave)

        if coords is None:
            clave_sin_numero = re.sub(r"\s+\d+$", "", clave).strip()
            coords = COORDS_SUCURSAL.get(clave_sin_numero)
        else:
            clave_sin_numero = clave

        estado = ESTADO_SUCURSAL.get(clave)
        if estado is None:
            estado = ESTADO_SUCURSAL.get(clave_sin_numero)

        if coords is None:
            latitudes.append(None)
            longitudes.append(None)
        else:
            latitudes.append(coords[0])
            longitudes.append(coords[1])

        estados.append(estado if estado else "Sin estado")

    df["Sucursal_Normalizada"] = suc_norm
    df["Latitud"] = latitudes
    df["Longitud"] = longitudes
    df["Estado"] = estados

    return df


def get_query_param(nombre: str, default: str = "") -> str:
    try:
        valor = st.query_params.get(nombre, default)
        if isinstance(valor, list):
            return valor[0] if valor else default
        return valor
    except Exception:
        params = st.experimental_get_query_params()
        valor = params.get(nombre, [default])
        return valor[0] if valor else default


def set_query_params(**kwargs):
    try:
        st.query_params.clear()
        for k, v in kwargs.items():
            if v is not None and v != "":
                st.query_params[k] = v
    except Exception:
        st.experimental_set_query_params(**kwargs)


def leer_csv_seguro(path: Path) -> pd.DataFrame:
    encodings = ["utf-8-sig", "utf-8", "latin1", "cp1252"]
    ultimo_error = None

    for enc in encodings:
        try:
            df = pd.read_csv(path, encoding=enc)
            df.columns = [arreglar_mojibake(str(c)).replace("\ufeff", "").strip() for c in df.columns]
            for col in df.select_dtypes(include=["object"]).columns:
                df[col] = df[col].map(lambda x: arreglar_mojibake(x) if isinstance(x, str) else x)
            return df
        except Exception as e:
            ultimo_error = e

    raise ValueError(f"No pude leer el CSV {path.name}. Último error: {ultimo_error}")


def convertir_numero(serie: pd.Series) -> pd.Series:
    if serie.dtype == object:
        serie = (
            serie.astype(str)
            .str.replace(",", "", regex=False)
            .str.replace("%", "", regex=False)
            .str.strip()
        )

    return pd.to_numeric(serie, errors="coerce")


def formatear_fecha(valor) -> str:
    fecha = pd.to_datetime(valor, errors="coerce", dayfirst=True)
    if pd.isna(fecha):
        return str(valor)
    return fecha.strftime("%d/%m/%Y")


def geojson_peru_fallback_la_libertad() -> dict:
    """
    Fallback local para que Vale Amigo Perú pueda pintar La Libertad
    aunque el archivo peru_departamentos.geojson descargado tenga propiedades
    diferentes o aunque no haya internet.
    """
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "name": "La Libertad",
                    "__region_norm": "LA LIBERTAD",
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[
                        [-79.75, -6.85],
                        [-77.95, -6.95],
                        [-76.75, -7.65],
                        [-76.90, -8.85],
                        [-78.35, -8.95],
                        [-79.70, -8.20],
                        [-79.75, -6.85],
                    ]],
                },
            }
        ],
    }


def geojson_contiene_region(geojson: dict, region: str) -> bool:
    region_norm = limpiar_texto(region)
    for feature in geojson.get("features", []):
        props = feature.get("properties", {})
        for valor in props.values():
            texto = limpiar_texto(valor)
            texto = texto.replace("_", " ").replace("-", " ")
            if region_norm in texto or texto in region_norm:
                return True
    return False


def detectar_region_feature(feature: dict, pais: str) -> str:
    props = feature.get("properties", {})
    valores = [limpiar_texto(v).replace("_", " ").replace("-", " ") for v in props.values()]
    texto_total = " ".join(valores)

    if limpiar_texto(pais) == limpiar_texto("PERÚ"):
        regiones = [
            "AMAZONAS", "ANCASH", "APURIMAC", "AREQUIPA", "AYACUCHO",
            "CAJAMARCA", "CALLAO", "CUSCO", "HUANCAVELICA", "HUANUCO",
            "ICA", "JUNIN", "LA LIBERTAD", "LAMBAYEQUE", "LIMA",
            "LORETO", "MADRE DE DIOS", "MOQUEGUA", "PASCO", "PIURA",
            "PUNO", "SAN MARTIN", "TACNA", "TUMBES", "UCAYALI",
        ]
        for region in regiones:
            if region in texto_total:
                return region
            if region == "LA LIBERTAD" and "LIBERTAD" in texto_total:
                return region

    return ""


def preparar_geojson_region_norm(geojson: dict, pais: str) -> tuple[dict, str, dict]:
    """
    Agrega una propiedad estándar __region_norm a cada feature.
    Así evitamos depender de si el GeoJSON usa name, NOMBDEP, DEPARTAMENTO, etc.
    """
    geojson = json.loads(json.dumps(geojson))
    mapa_geo = {}

    for feature in geojson.get("features", []):
        region_norm = detectar_region_feature(feature, pais)
        if not region_norm:
            # Último intento: usar la primera propiedad de texto no vacía.
            for valor in feature.get("properties", {}).values():
                region_norm = normalizar_nombre_region(valor)
                if region_norm:
                    break

        feature.setdefault("properties", {})["__region_norm"] = region_norm

        if region_norm:
            mapa_geo[region_norm] = region_norm

    return geojson, "__region_norm", mapa_geo


# ======================================================
# GEOJSON MÉXICO
# ======================================================
@st.cache_data(show_spinner=False)
def cargar_geojson_mexico() -> dict:
    if ARCHIVO_GEOJSON_MX.exists():
        with open(ARCHIVO_GEOJSON_MX, "r", encoding="utf-8") as f:
            return json.load(f)

    urls = [
        "https://raw.githubusercontent.com/angelnmara/geojson/master/mexicoHigh.json",
        "https://raw.githubusercontent.com/angelnmara/geojson/master/mexico.json",
    ]

    ultimo_error = None

    for url in urls:
        try:
            with urllib.request.urlopen(url, timeout=20) as response:
                data = json.loads(response.read().decode("utf-8"))

            with open(ARCHIVO_GEOJSON_MX, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False)

            return data

        except Exception as e:
            ultimo_error = e

    raise ValueError(
        "No pude cargar el GeoJSON de México. "
        "Verifica internet o coloca un archivo mexico_estados.geojson en la carpeta Web Vales. "
        f"Último error: {ultimo_error}"
    )



@st.cache_data(show_spinner=False)
def cargar_geojson_peru() -> dict:
    # Si ya existe, úsalo sólo si realmente trae La Libertad.
    if ARCHIVO_GEOJSON_PE.exists():
        try:
            with open(ARCHIVO_GEOJSON_PE, "r", encoding="utf-8") as f:
                data = json.load(f)

            if geojson_contiene_region(data, "La Libertad"):
                return data
        except Exception:
            pass

    urls = [
        "https://raw.githubusercontent.com/juaneladio/peru-geojson/master/peru_departamental_simple.geojson",
        "https://raw.githubusercontent.com/juaneladio/peru-geojson/master/peru_departamental.geojson",
        "https://raw.githubusercontent.com/juaneladio/peru-geojson/master/peru_departamentos.geojson",
    ]

    for url in urls:
        try:
            with urllib.request.urlopen(url, timeout=20) as response:
                data = json.loads(response.read().decode("utf-8"))

            if geojson_contiene_region(data, "La Libertad"):
                with open(ARCHIVO_GEOJSON_PE, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False)
                return data

        except Exception:
            pass

    # Fallback para que la vista de Perú no quede vacía.
    data = geojson_peru_fallback_la_libertad()
    try:
        with open(ARCHIVO_GEOJSON_PE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
    except Exception:
        pass

    return data


def cargar_geojson_por_pais(pais: str) -> dict:
    if limpiar_texto(pais) == limpiar_texto("PERÚ"):
        return cargar_geojson_peru()

    return cargar_geojson_mexico()


def detectar_propiedad_estado(geojson: dict) -> str:
    """
    Detecta la propiedad del GeoJSON que realmente contiene el nombre
    del estado/departamento.

    En algunos GeoJSON de Perú la primera propiedad no es el nombre; por eso
    no basta con tomar el primer campo. Esta función revisa todas las features
    y prioriza campos cuyos valores contienen nombres conocidos como
    LA LIBERTAD, LIMA, PIURA, etc.
    """
    features = geojson.get("features", [])

    if not features:
        return "name"

    props_primera = features[0].get("properties", {})
    llaves = list(props_primera.keys())

    candidatos_prioritarios = [
        "NOMBDEP",
        "NOMB_DEP",
        "NOMBDIST",
        "NOMBPROV",
        "DEPARTAMEN",
        "DEPARTAMENTO",
        "departamento",
        "Departamento",
        "NOMGEO",
        "NOM_ENT",
        "NOM_ENTIDAD",
        "name",
        "NAME",
        "admin_name",
        "estado",
        "Estado",
    ]

    nombres_esperados = {
        "LA LIBERTAD",
        "LIMA",
        "PIURA",
        "LAMBAYEQUE",
        "AREQUIPA",
        "CUSCO",
        "VERACRUZ",
        "CHIHUAHUA",
        "SINALOA",
        "TABASCO",
        "NAYARIT",
        "SONORA",
        "COAHUILA",
    }

    def puntaje_llave(llave: str) -> int:
        valores = []
        for feature in features:
            props = feature.get("properties", {})
            if llave in props:
                valores.append(normalizar_nombre_region(props.get(llave, "")))

        valores_set = set(v for v in valores if v)
        score = 0

        if llave in candidatos_prioritarios:
            score += 50

        score += len(valores_set & nombres_esperados) * 100

        # Penaliza campos tipo id/código que tienen pocos caracteres o casi todos numéricos.
        if valores_set:
            promedio_largo = sum(len(v) for v in valores_set) / len(valores_set)
            if promedio_largo < 4:
                score -= 30

            numericos = sum(v.replace(".", "", 1).isdigit() for v in valores_set)
            if numericos >= max(1, len(valores_set) * 0.7):
                score -= 100

        return score

    mejor = max(llaves, key=puntaje_llave)
    return mejor


def normalizar_nombre_region(valor) -> str:
    texto = limpiar_texto(valor)

    texto = texto.replace("_", " ")
    texto = texto.replace("-", " ")
    texto = texto.replace("/", " ")
    texto = re.sub(r"\s+", " ", texto).strip()

    prefijos = [
        "DEPARTAMENTO DE ",
        "REGION ",
        "REGIÓN ",
        "ESTADO DE ",
        "PROVINCIA DE ",
    ]

    for prefijo in prefijos:
        if texto.startswith(limpiar_texto(prefijo)):
            texto = texto[len(limpiar_texto(prefijo)):].strip()

    reemplazos = {
        "MICHOACAN DE OCAMPO": "MICHOACAN",
        "MICHOACAN": "MICHOACAN",
        "VERACRUZ DE IGNACIO DE LA LLAVE": "VERACRUZ",
        "COAHUILA DE ZARAGOZA": "COAHUILA",
        "NUEVO LEON": "NUEVO LEON",
        "MEXICO": "ESTADO DE MEXICO",
        "DISTRITO FEDERAL": "CIUDAD DE MEXICO",
        "CDMX": "CIUDAD DE MEXICO",
        "LA LIBERTAD": "LA LIBERTAD",
        "LIBERTAD": "LA LIBERTAD",
        "LIMA PROVINCIAS": "LIMA",
        "LIMA METROPOLITANA": "LIMA",
    }

    return reemplazos.get(texto, texto)


def normalizar_estado_geo(valor) -> str:
    return normalizar_nombre_region(valor)


def normalizar_estado_datos(valor) -> str:
    return normalizar_nombre_region(valor)


def resolver_estado_geo(estado_normalizado: str, mapa_geo: dict) -> str | None:
    """
    Encuentra el nombre exacto del GeoJSON para un estado/departamento de los datos.
    Primero intenta match exacto y luego match flexible.
    """
    if not estado_normalizado:
        return None

    if estado_normalizado in mapa_geo:
        return mapa_geo[estado_normalizado]

    for geo_norm, geo_original in mapa_geo.items():
        if estado_normalizado == geo_norm:
            return geo_original

        if estado_normalizado in geo_norm or geo_norm in estado_normalizado:
            return geo_original

    # Fallback específico para Perú cuando el GeoJSON usa una variante de nombre.
    if estado_normalizado == "LA LIBERTAD":
        for geo_norm, geo_original in mapa_geo.items():
            if "LIBERTAD" in geo_norm:
                return geo_original

    return None


def preparar_geojson_y_mapeo(geojson: dict) -> tuple[dict, str, dict]:
    prop_estado = detectar_propiedad_estado(geojson)
    mapa_geo = {}

    for feature in geojson.get("features", []):
        nombre_geo = str(feature.get("properties", {}).get(prop_estado, ""))
        norm_geo = normalizar_estado_geo(nombre_geo)

        if norm_geo:
            mapa_geo[norm_geo] = nombre_geo

    return geojson, prop_estado, mapa_geo


def filtrar_geojson_estado(geojson: dict, prop_estado: str, estado_geo: str) -> dict:
    features = []

    for feature in geojson["features"]:
        if str(feature["properties"].get(prop_estado, "")) == estado_geo:
            features.append(feature)

    return {
        "type": "FeatureCollection",
        "features": features,
    }


# ======================================================
# LECTURA DEL EXCEL DE ESTRUCTURA
# ======================================================
@st.cache_data(show_spinner=False)
def cargar_estructura(path: str) -> pd.DataFrame:
    df = pd.read_excel(path)

    columnas_requeridas = [
        "Coordinacion",
        "Marca",
        "Dir",
        "Subdirección",
        "Zona",
        "Sucursal",
        "Red",
        "Cartera",
    ]

    faltantes = [col for col in columnas_requeridas if col not in df.columns]

    if faltantes:
        raise ValueError(
            "El archivo Estructura vales.xlsx no tiene estas columnas: "
            + ", ".join(faltantes)
        )

    df = df[columnas_requeridas].copy()

    for col in columnas_requeridas:
        df[col] = df[col].fillna("Sin dato").astype(str).str.strip()
        df[col] = df[col].replace("", "Sin dato")

    df["País"] = df.apply(detectar_pais, axis=1)
    df["Conteo"] = 1
    df = aplicar_coordenadas_y_estado(df)

    return df


# ======================================================
# LECTURA DE DISTRIBUIDORAS VALE MX
# ======================================================
@st.cache_data(show_spinner=False)
def cargar_distribuidoras_mx(path: str) -> pd.DataFrame:
    df = leer_csv_seguro(Path(path))

    col_fecha = None
    posibles_fecha = [
        "Fecha de Corte",
        "Última fecha: Fecha de Corte",
        "Ultima fecha: Fecha de Corte",
        "Ãltima fecha: Fecha de Corte",
    ]

    for col in posibles_fecha:
        if col in df.columns:
            col_fecha = col
            break

    columnas_requeridas = [
        "Sub",
        "Zona",
        "Sucursal",
        "Coordinacion",
        "Calidad de Cartera H",
        "Distribuidoras Totales H",
        "Distribuidoras al Corriente H",
    ]

    columnas_opcionales = [
        "Distribuidoras en Mora H",
        "Var Dist Corriente",
        "Var Dist en Mora",
    ]

    if col_fecha is None:
        raise ValueError("El archivo Distribuidoras Vale MX.csv no tiene la columna Fecha de Corte.")

    faltantes = [col for col in columnas_requeridas if col not in df.columns]

    if faltantes:
        raise ValueError(
            "El archivo Distribuidoras Vale MX.csv no tiene estas columnas: "
            + ", ".join(faltantes)
        )

    columnas_presentes = columnas_requeridas + [c for c in columnas_opcionales if c in df.columns] + [col_fecha]
    df = df[columnas_presentes].copy()

    renombres = {
        "Sub": "Subdirección",
        "Calidad de Cartera H": "Calidad de Cartera",
        "Distribuidoras Totales H": "Distribuidoras Totales",
        "Distribuidoras al Corriente H": "Distribuidoras al Corriente",
        "Distribuidoras en Mora H": "Distribuidoras en Mora",
        "Var Dist Corriente": "Var Dist Corriente",
        "Var Dist en Mora": "Var Dist en Mora",
        col_fecha: "Fecha de Corte",
    }
    df = df.rename(columns=renombres)

    for col in ["Subdirección", "Zona", "Sucursal", "Coordinacion"]:
        df[col] = df[col].fillna("Sin dato").astype(str).str.strip()
        df[col] = df[col].replace("", "Sin dato")
        df[col] = df[col].map(lambda x: arreglar_mojibake(x) if isinstance(x, str) else x)

    for col in [
        "Calidad de Cartera",
        "Distribuidoras Totales",
        "Distribuidoras al Corriente",
        "Distribuidoras en Mora",
        "Var Dist Corriente",
        "Var Dist en Mora",
    ]:
        if col not in df.columns:
            df[col] = 0
        df[col] = convertir_numero(df[col]).fillna(0)

    # Calidad de Cartera se recalcula a nivel fila para que después,
    # al elegir Subdirección / Zona / Sucursal, la tabla muestre el promedio
    # real de la calidad dentro del nivel de estructura seleccionado.
    df["Calidad de Cartera"] = df.apply(
        lambda r: (
            pd.to_numeric(r["Distribuidoras al Corriente"], errors="coerce")
            / pd.to_numeric(r["Distribuidoras Totales"], errors="coerce")
            * 100
        )
        if pd.to_numeric(r["Distribuidoras Totales"], errors="coerce")
        else 0,
        axis=1,
    ).fillna(0)

    df["Semaforo Variacion"] = df.apply(
        lambda r: "Verde" if pd.to_numeric(r["Var Dist Corriente"], errors="coerce") > 0 else "Rojo",
        axis=1,
    )

    df["Fecha de Corte"] = pd.to_datetime(df["Fecha de Corte"], errors="coerce", dayfirst=True)
    df["Fecha de Corte Texto"] = df["Fecha de Corte"].dt.strftime("%d/%m/%Y")

    df["País"] = "MÉXICO"
    df["Cartera"] = "Vale Amigo"
    df["Marca"] = "Vale Amigo"
    df["Dir"] = "Sin dato"
    df["Red"] = "Sin dato"
    df["Conteo"] = 1

    df = aplicar_coordenadas_y_estado(df)

    return df




# ======================================================
# LECTURA E INTEGRACIÓN DE DISPERSIÓN DIARIA
# ======================================================
def resolver_archivo_dispersion() -> Path | None:
    """
    Busca el archivo de dispersión diaria en la misma carpeta que app.py.
    Acepta nombres como:
    - Dispersion diaria.csv
    - Dispersion diaria(2).csv
    - Dispersión diaria.csv
    """
    candidatos = [
        ARCHIVO_DISPERSION,
        BASE_DIR / "Dispersion diaria(2).csv",
        BASE_DIR / "Dispersión diaria.csv",
        BASE_DIR / "Dispersión diaria(2).csv",
    ]

    for ruta in candidatos:
        if ruta.exists():
            return ruta

    for ruta in BASE_DIR.glob("*Dispersion*diaria*.csv"):
        if ruta.exists():
            return ruta

    for ruta in BASE_DIR.glob("*Dispersión*diaria*.csv"):
        if ruta.exists():
            return ruta

    return None


def normalizar_llave(valor) -> str:
    return limpiar_texto(valor)


def normalizar_llave_sucursal(valor) -> str:
    """
    Normaliza la sucursal para cruzar dispersión contra estructura.

    La base de dispersión puede traer sucursales operativas con sufijo numérico
    como "Poza Rica 2", "Cardenas 2" o "Coatzacoalcos 2", mientras
    la estructura/Distribuidoras MX las trae como "Poza Rica", "Cardenas"
    o "Coatzacoalcos".

    Si no quitamos ese sufijo, esos importes sí están dentro de la fecha de corte
    pero no hacen match y se pierden del acumulado mostrado.
    """
    texto = limpiar_texto(valor)
    texto = re.sub(r"\s+\d+$", "", texto).strip()
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto


@st.cache_data(show_spinner=False)
def cargar_dispersion_diaria(path: str) -> pd.DataFrame:
    df = leer_csv_seguro(Path(path))

    renombres = {}
    for col in df.columns:
        col_norm = limpiar_texto(col)
        if col_norm == "DATE":
            renombres[col] = "Date"
        elif col_norm == "MARCA":
            renombres[col] = "Marca"
        elif col_norm in ["SUBDIRECCION", "SUBDIRECCIÓN"]:
            renombres[col] = "Subdirección"
        elif col_norm == "ZONA":
            renombres[col] = "Zona"
        elif col_norm == "SUCURSAL":
            renombres[col] = "Sucursal"
        elif col_norm in ["TOTAL DISP", "TOTAL DISPERSADO", "TOTAL_DISP", "TOTAL DIS"]:
            renombres[col] = "Total Dispersado"
        elif col_norm in ["CANJES", "CANJE"]:
            renombres[col] = "Canjes"
        elif col_norm in ["CANJE PROM", "CANJE PROMEDIO", "CANJE_PROM"]:
            renombres[col] = "Canje Promedio Diario"

    df = df.rename(columns=renombres)

    columnas_requeridas = [
        "Date",
        "Marca",
        "Subdirección",
        "Zona",
        "Sucursal",
        "Total Dispersado",
        "Canjes",
    ]

    faltantes = [col for col in columnas_requeridas if col not in df.columns]
    if faltantes:
        raise ValueError(
            "El archivo de dispersión diaria no tiene estas columnas: "
            + ", ".join(faltantes)
        )

    df = df[columnas_requeridas + (["Canje Promedio Diario"] if "Canje Promedio Diario" in df.columns else [])].copy()

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce", dayfirst=False)

    for col in ["Marca", "Subdirección", "Zona", "Sucursal"]:
        df[col] = df[col].fillna("Sin dato").astype(str).str.strip()
        df[col] = df[col].replace("", "Sin dato")
        df[col] = df[col].map(lambda x: arreglar_mojibake(x) if isinstance(x, str) else x)

    for col in ["Total Dispersado", "Canjes", "Canje Promedio Diario"]:
        if col in df.columns:
            df[col] = convertir_numero(df[col]).fillna(0)

    df = df.dropna(subset=["Date"]).copy()

    for col in ["Marca", "Subdirección", "Zona"]:
        df[f"__{col}_norm"] = df[col].map(normalizar_llave)
    df["__Sucursal_norm"] = df["Sucursal"].map(normalizar_llave_sucursal)

    return df


def agregar_columnas_dispersion_vacias(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for col in ["Total Dispersado", "Canjes", "Canje Promedio Acumulado", "Canjes Fecha Corte", "Total Dispersado Fecha Corte"]:
        if col not in df.columns:
            df[col] = 0
    return df


def integrar_dispersion_acumulada(
    df_base: pd.DataFrame,
    fecha_corte_texto: str,
) -> pd.DataFrame:
    """
    Integra dispersión acumulada hasta la fecha de corte seleccionada y,
    además, conserva los canjes/importe sólo del día de corte para el mapa de calor.

    La estructura puede traer varias filas para una misma Sucursal porque cada fila
    puede representar una Coordinación. La dispersión viene a nivel
    Marca + Subdirección + Zona + Sucursal. Para evitar duplicar importes al hacer
    merge contra la estructura, se reparte el acumulado y el dato diario entre las
    filas de estructura que comparten la misma llave.
    """
    df_base = df_base.copy()
    ruta_dispersion = resolver_archivo_dispersion()

    if ruta_dispersion is None:
        return agregar_columnas_dispersion_vacias(df_base)

    try:
        df_disp = cargar_dispersion_diaria(str(ruta_dispersion))
    except Exception as e:
        st.warning(f"No pude leer el archivo de dispersión diaria: {e}")
        return agregar_columnas_dispersion_vacias(df_base)

    fecha_corte = pd.to_datetime(fecha_corte_texto, errors="coerce", dayfirst=True)
    if pd.isna(fecha_corte):
        return agregar_columnas_dispersion_vacias(df_base)

    # Acumulado real: todas las fechas menores o iguales al corte seleccionado.
    df_disp_acum = df_disp[df_disp["Date"] <= fecha_corte].copy()

    # Dato del día: sólo la fecha de corte seleccionada. Esto se usa para Color Canjes.
    df_disp_dia = df_disp[df_disp["Date"].dt.normalize() == fecha_corte.normalize()].copy()

    if df_disp_acum.empty and df_disp_dia.empty:
        return agregar_columnas_dispersion_vacias(df_base)

    llaves_norm = ["__Marca_norm", "__Subdirección_norm", "__Zona_norm", "__Sucursal_norm"]

    for col in ["Marca", "Subdirección", "Zona", "Sucursal"]:
        if col not in df_base.columns:
            df_base[col] = "Sin dato"

    for col in ["Marca", "Subdirección", "Zona"]:
        df_base[f"__{col}_norm"] = df_base[col].map(normalizar_llave)
    df_base["__Sucursal_norm"] = df_base["Sucursal"].map(normalizar_llave_sucursal)

    conteo_base = (
        df_base.groupby(llaves_norm, as_index=False)
        .size()
        .rename(columns={"size": "__filas_estructura"})
    )

    if df_disp_acum.empty:
        disp_agg = conteo_base.copy()
        disp_agg["Total_Dispersado"] = 0
        disp_agg["Canjes_Acumulados"] = 0
    else:
        disp_agg = (
            df_disp_acum.groupby(llaves_norm, as_index=False)
            .agg(
                Total_Dispersado=("Total Dispersado", "sum"),
                Canjes_Acumulados=("Canjes", "sum"),
            )
        )
        disp_agg = disp_agg.merge(conteo_base, on=llaves_norm, how="left")

    if df_disp_dia.empty:
        disp_dia = conteo_base.copy()
        disp_dia["Total_Dispersado_Dia"] = 0
        disp_dia["Canjes_Dia"] = 0
    else:
        disp_dia = (
            df_disp_dia.groupby(llaves_norm, as_index=False)
            .agg(
                Total_Dispersado_Dia=("Total Dispersado", "sum"),
                Canjes_Dia=("Canjes", "sum"),
            )
        )

    disp_agg = disp_agg.merge(disp_dia, on=llaves_norm, how="left")

    if "__filas_estructura" not in disp_agg.columns:
        disp_agg = disp_agg.merge(conteo_base, on=llaves_norm, how="left")

    disp_agg["__filas_estructura"] = (
        pd.to_numeric(disp_agg["__filas_estructura"], errors="coerce")
        .fillna(1)
        .replace(0, 1)
    )

    for col in ["Total_Dispersado", "Canjes_Acumulados", "Total_Dispersado_Dia", "Canjes_Dia"]:
        if col not in disp_agg.columns:
            disp_agg[col] = 0
        disp_agg[col] = pd.to_numeric(disp_agg[col], errors="coerce").fillna(0)

    # Valores asignados por fila de estructura. Al sumarse de nuevo, regresan
    # al valor real de la sucursal, sin duplicarse por coordinación.
    disp_agg["Total_Dispersado_Fila"] = disp_agg["Total_Dispersado"] / disp_agg["__filas_estructura"]
    disp_agg["Canjes_Fila"] = disp_agg["Canjes_Acumulados"] / disp_agg["__filas_estructura"]
    disp_agg["Total_Dispersado_Dia_Fila"] = disp_agg["Total_Dispersado_Dia"] / disp_agg["__filas_estructura"]
    disp_agg["Canjes_Dia_Fila"] = disp_agg["Canjes_Dia"] / disp_agg["__filas_estructura"]

    df_base = df_base.merge(disp_agg, on=llaves_norm, how="left")

    df_base["Total Dispersado"] = pd.to_numeric(
        df_base["Total_Dispersado_Fila"], errors="coerce"
    ).fillna(0)
    df_base["Canjes"] = pd.to_numeric(df_base["Canjes_Fila"], errors="coerce").fillna(0)
    df_base["Total Dispersado Fecha Corte"] = pd.to_numeric(
        df_base["Total_Dispersado_Dia_Fila"], errors="coerce"
    ).fillna(0)
    df_base["Canjes Fecha Corte"] = pd.to_numeric(
        df_base["Canjes_Dia_Fila"], errors="coerce"
    ).fillna(0)

    # El promedio acumulado se recalcula siempre con los importes acumulados.
    df_base["Canje Promedio Acumulado"] = df_base.apply(
        lambda r: r["Total Dispersado"] / r["Canjes"] if pd.to_numeric(r["Canjes"], errors="coerce") else 0,
        axis=1,
    )

    columnas_aux = [
        "__Marca_norm",
        "__Subdirección_norm",
        "__Zona_norm",
        "__Sucursal_norm",
        "Total_Dispersado",
        "Canjes_Acumulados",
        "Total_Dispersado_Dia",
        "Canjes_Dia",
        "__filas_estructura",
        "Total_Dispersado_Fila",
        "Canjes_Fila",
        "Total_Dispersado_Dia_Fila",
        "Canjes_Dia_Fila",
    ]
    df_base = df_base.drop(columns=[c for c in columnas_aux if c in df_base.columns])

    return df_base

def recalcular_canje_promedio(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if "Total Dispersado" not in df.columns:
        df["Total Dispersado"] = 0
    if "Canjes" not in df.columns:
        df["Canjes"] = 0
    if "Canjes Fecha Corte" not in df.columns:
        df["Canjes Fecha Corte"] = 0
    if "Total Dispersado Fecha Corte" not in df.columns:
        df["Total Dispersado Fecha Corte"] = 0

    df["Canje Promedio Acumulado"] = df.apply(
        lambda r: r["Total Dispersado"] / r["Canjes"] if pd.to_numeric(r["Canjes"], errors="coerce") else 0,
        axis=1,
    )
    return df




# ======================================================
# LECTURA E INTEGRACIÓN DE PLAZO Y COMPOSICIÓN DE DISPERSIÓN
# ======================================================
def resolver_archivo_plazo_composicion() -> Path | None:
    """
    Busca el archivo que alimenta la lectura financiera del detalle por estado.
    Si existen varias versiones, usa la más reciente por fecha de modificación.
    La fecha/corte que se muestra en esta vista sale de la columna Corte de este archivo,
    no de la fecha de corte de las demás visualizaciones.
    """
    candidatos = [
        ARCHIVO_PLAZO_COMPOSICION,
        BASE_DIR / "Plazo y composicion de dispersión.csv",
        BASE_DIR / "Plazo y composicion de dispersión(1).csv",
        BASE_DIR / "Plazo y composicion de dispersión(2).csv",
        BASE_DIR / "Plazo y composicion de dispersión(3).csv",
        BASE_DIR / "Plazo y composicion de dispersión(4).csv",
        BASE_DIR / "Plazo y composición de dispersión.csv",
        BASE_DIR / "Plazo y composición de dispersión(1).csv",
        BASE_DIR / "Plazo y composición de dispersión(2).csv",
        BASE_DIR / "Plazo y composición de dispersión(3).csv",
        BASE_DIR / "Plazo y composición de dispersión(4).csv",
        BASE_DIR / "Plazo y composicion de dispersion.csv",
        BASE_DIR / "Plazo y composicion de dispersion(1).csv",
        BASE_DIR / "Plazo y composicion de dispersion(2).csv",
        BASE_DIR / "Plazo y composicion de dispersion(3).csv",
        BASE_DIR / "Plazo y composicion de dispersion(4).csv",
    ]

    patrones = [
        "*Plazo*composicion*dispers*.csv",
        "*Plazo*composición*dispers*.csv",
        "*plazo*composicion*dispers*.csv",
        "*plazo*composición*dispers*.csv",
    ]

    encontrados = []
    vistos = set()

    for ruta in candidatos:
        if ruta.exists() and ruta not in vistos:
            encontrados.append(ruta)
            vistos.add(ruta)

    for patron in patrones:
        for ruta in BASE_DIR.glob(patron):
            if ruta.exists() and ruta not in vistos:
                encontrados.append(ruta)
                vistos.add(ruta)

    if not encontrados:
        return None

    encontrados = sorted(encontrados, key=lambda p: p.stat().st_mtime, reverse=True)
    return encontrados[0]

def convertir_porcentaje(serie: pd.Series) -> pd.Series:
    if serie.dtype == object:
        texto = serie.astype(str).str.strip()
        tiene_pct = texto.str.contains("%", regex=False, na=False)
        valores = texto.str.replace("%", "", regex=False).str.replace(",", "", regex=False)
        num = pd.to_numeric(valores, errors="coerce")
        # Si venía como 20.16%, se conserva como 20.16. Si venía como 0.2016, se lleva a 20.16.
        num = num.where(tiene_pct | (num > 1), num * 100)
        return num

    num = pd.to_numeric(serie, errors="coerce")
    return num.where(num > 1, num * 100)



def extraer_fecha_corte(valor):
    """
    Convierte textos como 'Corte 02 julio 2026' a fecha.
    También soporta formatos tipo 02/07/2026, 2026-07-02 o fechas reconocibles por pandas.
    """
    if pd.isna(valor):
        return pd.NaT

    texto = arreglar_mojibake(str(valor)).strip()
    if not texto:
        return pd.NaT

    meses = {
        "ENERO": 1,
        "FEBRERO": 2,
        "MARZO": 3,
        "ABRIL": 4,
        "MAYO": 5,
        "JUNIO": 6,
        "JULIO": 7,
        "AGOSTO": 8,
        "SEPTIEMBRE": 9,
        "SETIEMBRE": 9,
        "OCTUBRE": 10,
        "NOVIEMBRE": 11,
        "DICIEMBRE": 12,
    }

    texto_norm = limpiar_texto(texto)
    match = re.search(
        r"(\d{1,2})\s+("
        r"ENERO|FEBRERO|MARZO|ABRIL|MAYO|JUNIO|JULIO|AGOSTO|SEPTIEMBRE|SETIEMBRE|OCTUBRE|NOVIEMBRE|DICIEMBRE"
        r")\s+(\d{4})",
        texto_norm,
    )

    if match:
        dia = int(match.group(1))
        mes = meses.get(match.group(2))
        anio = int(match.group(3))
        if mes:
            return pd.Timestamp(year=anio, month=mes, day=dia)

    return pd.to_datetime(texto, errors="coerce", dayfirst=True)



def formatear_corte_plazo(valor) -> str:
    """
    Devuelve el corte como texto visible para la vista Plazo y composición.
    Si viene como fecha, lo muestra dd/mm/aaaa. Si viene como texto, conserva el texto.
    """
    if pd.isna(valor):
        return ""

    texto = arreglar_mojibake(str(valor)).strip()
    if not texto:
        return ""

    fecha = extraer_fecha_corte(texto)
    if not pd.isna(fecha):
        return pd.to_datetime(fecha).strftime("%d/%m/%Y")

    return texto



def obtener_corte_visible_plazo() -> str:
    """
    Lee directamente el archivo de Plazo y composición y devuelve el último Corte visible.
    Esto evita que el corte se pierda por cruces de estructura, filtros de estado o cache de otras vistas.
    """
    ruta = resolver_archivo_plazo_composicion()
    if ruta is None:
        return ""

    try:
        df_raw = leer_csv_seguro(ruta)
    except Exception:
        return ""

    col_corte = None
    for col in df_raw.columns:
        if limpiar_texto(col) == "CORTE":
            col_corte = col
            break

    if col_corte is None:
        return ""

    serie = (
        df_raw[col_corte]
        .dropna()
        .astype(str)
        .map(lambda x: arreglar_mojibake(x).strip())
    )
    serie = serie[serie != ""]

    if serie.empty:
        return ""

    return formatear_corte_plazo(serie.iloc[-1])


def filtrar_ultimo_corte_plazo(df: pd.DataFrame) -> pd.DataFrame:
    """
    Conserva únicamente el último dato real de la columna Corte.

    Esta vista tiene su propio corte porque se alimenta de una base distinta.
    Por eso NO usa la fecha de corte del tablero principal.
    """
    df = df.copy()

    if "Corte" not in df.columns:
        df["Corte"] = ""
        df["Corte Fecha"] = pd.NaT
        df["Corte Texto"] = ""
        return df

    df["Corte"] = df["Corte"].fillna("").astype(str).map(lambda x: arreglar_mojibake(x).strip())
    df["Corte Fecha"] = df["Corte"].map(extraer_fecha_corte)
    df["Corte Texto"] = df["Corte"].map(formatear_corte_plazo)

    cortes_en_orden = [c for c in df["Corte"].tolist() if str(c).strip()]
    if cortes_en_orden:
        ultimo_corte = cortes_en_orden[-1]
        return df[df["Corte"] == ultimo_corte].copy()

    return df

@st.cache_data(show_spinner=False)
def cargar_plazo_composicion(path: str) -> pd.DataFrame:
    df = leer_csv_seguro(Path(path))

    renombres = {}
    for col in df.columns:
        col_norm = limpiar_texto(col)
        if col_norm in ["SUBDIRECCION", "SUBDIRECCIÓN"]:
            renombres[col] = "Subdirección"
        elif col_norm == "ZONA":
            renombres[col] = "Zona"
        elif col_norm == "SUCURSAL":
            renombres[col] = "Sucursal"
        elif col_norm == "CORTE":
            renombres[col] = "Corte"
        elif col_norm == "PLAZO":
            renombres[col] = "Plazo"
        elif col_norm == "CAPITAL":
            renombres[col] = "Capital"
        elif col_norm in ["INTERES", "INTERÉS"]:
            renombres[col] = "Interes"
        elif col_norm == "TOTAL":
            renombres[col] = "Total"
        elif col_norm in ["TASA DE GANANCIA", "TASA GANANCIA", "TASA"]:
            renombres[col] = "Tasa de Ganancia"
        elif col_norm in ["VALES", "CANJES"]:
            renombres[col] = "Vales"

    df = df.rename(columns=renombres)

    columnas_requeridas = [
        "Subdirección",
        "Zona",
        "Sucursal",
        "Plazo",
        "Capital",
        "Interes",
        "Total",
        "Tasa de Ganancia",
        "Vales",
    ]

    faltantes = [col for col in columnas_requeridas if col not in df.columns]
    if faltantes:
        raise ValueError(
            "El archivo Plazo y composición de dispersión no tiene estas columnas: "
            + ", ".join(faltantes)
        )

    columnas_uso = columnas_requeridas.copy()
    if "Corte" in df.columns:
        columnas_uso = ["Corte"] + columnas_uso

    df = df[columnas_uso].copy()

    # Se conservan todos los cortes para que la tarjeta Corte pueda cambiar
    # la lectura del treemap sin depender del encabezado general ni del último corte.
    if "Corte" not in df.columns:
        df["Corte"] = ""
    df["Corte"] = df["Corte"].fillna("").astype(str).map(lambda x: arreglar_mojibake(x).strip())
    df["Corte Fecha"] = df["Corte"].map(extraer_fecha_corte)
    df["Corte Texto"] = df["Corte"].map(formatear_corte_plazo)

    for col in ["Subdirección", "Zona", "Sucursal"]:
        df[col] = df[col].fillna("Sin dato").astype(str).str.strip().replace("", "Sin dato")
        df[col] = df[col].map(lambda x: arreglar_mojibake(x) if isinstance(x, str) else x)

    if "Corte" not in df.columns:
        df["Corte"] = ""
    df["Corte"] = df["Corte"].fillna("").astype(str).map(lambda x: arreglar_mojibake(x).strip())
    df["Corte Texto"] = df["Corte"].map(formatear_corte_plazo)

    for col in ["Plazo", "Capital", "Interes", "Total", "Vales"]:
        df[col] = convertir_numero(df[col]).fillna(0)

    df["Tasa de Ganancia"] = convertir_porcentaje(df["Tasa de Ganancia"]).fillna(0)

    for col in ["Subdirección", "Zona"]:
        df[f"__{col}_norm"] = df[col].map(normalizar_llave)
    df["__Sucursal_norm"] = df["Sucursal"].map(normalizar_llave_sucursal)

    # El plazo se mantiene EXACTAMENTE como viene en el archivo.
    # Por eso se agrupa incluyendo Plazo y no se calcula promedio ni ponderado.
    agrupado = (
        df.groupby(["__Subdirección_norm", "__Zona_norm", "__Sucursal_norm", "Corte", "Corte Texto", "Plazo"], as_index=False)
        .agg(
            Subdirección=("Subdirección", "first"),
            Zona=("Zona", "first"),
            Sucursal=("Sucursal", "first"),
            Capital=("Capital", "sum"),
            Interes=("Interes", "sum"),
            Total=("Total", "sum"),
            Vales=("Vales", "sum"),
        )
    )

    agrupado["Tasa de Ganancia"] = agrupado.apply(
        lambda r: r["Interes"] / r["Capital"] * 100 if pd.to_numeric(r["Capital"], errors="coerce") else 0,
        axis=1,
    )
    agrupado["Ganancia"] = agrupado["Total"] - agrupado["Capital"]

    return agrupado

def preparar_sucursales_financieras_para_mapa(df_estado: pd.DataFrame) -> pd.DataFrame:
    df_suc = preparar_sucursales_para_mapa(df_estado).copy()

    for col in ["Capital", "Interes", "Total", "Tasa de Ganancia", "Plazo", "Vales", "Ganancia"]:
        df_suc[col] = 0
    df_suc["Corte"] = ""
    df_suc["Corte Texto"] = ""

    ruta_plazo = resolver_archivo_plazo_composicion()
    if ruta_plazo is None:
        return df_suc

    try:
        df_fin = cargar_plazo_composicion(str(ruta_plazo))
    except Exception as e:
        st.warning(f"No pude leer el archivo de plazo y composición de dispersión: {e}")
        return df_suc

    if df_fin.empty:
        return df_suc

    for col in ["Subdirección", "Zona"]:
        df_suc[f"__{col}_norm"] = df_suc[col].map(normalizar_llave)
    df_suc["__Sucursal_norm"] = df_suc["Sucursal"].map(normalizar_llave_sucursal)

    cols_fin = [
        "__Subdirección_norm",
        "__Zona_norm",
        "__Sucursal_norm",
        "Capital",
        "Interes",
        "Total",
        "Tasa de Ganancia",
        "Plazo",
        "Vales",
        "Ganancia",
        "Corte",
        "Corte Texto",
    ]

    df_suc_base = df_suc.drop(
        columns=["Capital", "Interes", "Total", "Tasa de Ganancia", "Plazo", "Vales", "Ganancia", "Corte", "Corte Texto"],
        errors="ignore",
    )

    df_suc_match = df_suc_base.merge(
        df_fin[cols_fin],
        on=["__Subdirección_norm", "__Zona_norm", "__Sucursal_norm"],
        how="left",
    )

    # Fallback por sucursal cuando subdirección o zona no coinciden exactamente.
    faltantes = df_suc_match["Capital"].isna()
    if faltantes.any():
        df_fin_suc = (
            df_fin.groupby(["__Sucursal_norm", "Corte", "Corte Texto", "Plazo"], as_index=False)
            .agg(
                Capital=("Capital", "sum"),
                Interes=("Interes", "sum"),
                Total=("Total", "sum"),
                Vales=("Vales", "sum"),
                Ganancia=("Ganancia", "sum"),
            )
        )
        df_fin_suc["Tasa de Ganancia"] = df_fin_suc.apply(
            lambda r: r["Interes"] / r["Capital"] * 100 if r["Capital"] else 0,
            axis=1,
        )

        df_faltantes = df_suc_base.loc[faltantes].merge(df_fin_suc, on="__Sucursal_norm", how="left")

        df_suc_match = pd.concat(
            [df_suc_match.loc[~faltantes].copy(), df_faltantes.copy()],
            ignore_index=True,
        )

    for col in ["Capital", "Interes", "Total", "Tasa de Ganancia", "Plazo", "Vales", "Ganancia"]:
        df_suc_match[col] = pd.to_numeric(df_suc_match[col], errors="coerce").fillna(0)

    if "Corte" not in df_suc_match.columns:
        df_suc_match["Corte"] = ""
    df_suc_match["Corte"] = df_suc_match["Corte"].fillna("").astype(str)

    if "Corte Texto" not in df_suc_match.columns:
        df_suc_match["Corte Texto"] = ""
    df_suc_match["Corte Texto"] = df_suc_match["Corte Texto"].fillna("").astype(str)

    corte_visible_fallback = obtener_corte_visible_plazo()
    if corte_visible_fallback:
        df_suc_match["Corte Texto"] = df_suc_match["Corte Texto"].replace("", corte_visible_fallback)
        if "Corte" in df_suc_match.columns:
            df_suc_match["Corte"] = df_suc_match["Corte"].replace("", corte_visible_fallback)

    columnas_aux = [c for c in df_suc_match.columns if c.startswith("__") or c.endswith("_suc")]
    df_suc_match = df_suc_match.drop(columns=columnas_aux, errors="ignore")

    return df_suc_match

def formato_moneda(valor) -> str:
    numero = pd.to_numeric(valor, errors="coerce")
    if pd.isna(numero):
        numero = 0
    return f"${float(numero):,.0f}"


def formato_numero(valor) -> str:
    numero = pd.to_numeric(valor, errors="coerce")
    if pd.isna(numero):
        numero = 0
    return f"{float(numero):,.0f}"



# ======================================================
# TEMA DE COLORES POR VALERA
# ======================================================
TEMAS_VALERA = {
    "default": {
        "primario": "#0B2A6F",
        "oscuro": "#071E55",
        "texto": "#10264B",
        "acento": "#D8C92E",
        "suave": "rgba(11, 42, 111, 0.10)",
    },
    "vale_amigo": {
        "primario": "#1B236C",
        "oscuro": "#0B1550",
        "texto": "#111B55",
        "acento": "#86B4DD",
        "suave": "rgba(27, 35, 108, 0.12)",
    },
    "viva_vale": {
        "primario": "#8DB55D",
        "oscuro": "#5F8436",
        "texto": "#476A2F",
        "acento": "#E6D95B",
        "suave": "rgba(141, 181, 93, 0.15)",
    },
    "rapivale": {
        "primario": "#F37021",
        "oscuro": "#C95513",
        "texto": "#204B26",
        "acento": "#72B34A",
        "suave": "rgba(243, 112, 33, 0.14)",
    },
    "vale_amigo_peru": {
        "primario": "#1B236C",
        "oscuro": "#0B1550",
        "texto": "#111B55",
        "acento": "#0D6FAE",
        "suave": "rgba(27, 35, 108, 0.12)",
    },
}


def obtener_tema_actual() -> dict:
    valera_actual = get_query_param("valera", "")
    return TEMAS_VALERA.get(valera_actual, TEMAS_VALERA["default"])


def hex_a_rgba(hex_color: str, alpha: float) -> str:
    hex_color = str(hex_color).strip().lstrip("#")
    if len(hex_color) != 6:
        return f"rgba(11,42,111,{alpha})"
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


TEMA_ACTUAL = obtener_tema_actual()
COLOR_PRIMARIO = TEMA_ACTUAL["primario"]
COLOR_OSCURO = TEMA_ACTUAL["oscuro"]
COLOR_TEXTO = TEMA_ACTUAL["texto"]
COLOR_ACENTO = TEMA_ACTUAL["acento"]
COLOR_BORDE = TEMA_ACTUAL["suave"]
COLOR_LINEA_MAPA_35 = hex_a_rgba(COLOR_PRIMARIO, 0.35)
COLOR_LINEA_MAPA_45 = hex_a_rgba(COLOR_PRIMARIO, 0.45)
COLOR_LINEA_MAPA_48 = hex_a_rgba(COLOR_PRIMARIO, 0.48)
COLOR_LINEA_MAPA_55 = hex_a_rgba(COLOR_PRIMARIO, 0.55)
COLOR_LINEA_MAPA_65 = hex_a_rgba(COLOR_PRIMARIO, 0.65)

# ======================================================
# ESTILOS
# ======================================================
bg_src = img_src(FONDO)

st.markdown(
    f"""
<style>
:root {{
    --azul: {COLOR_PRIMARIO};
    --azul-oscuro: {COLOR_OSCURO};
    --texto: {COLOR_TEXTO};
    --acento: {COLOR_ACENTO};
    --borde: {COLOR_BORDE};
}}

#MainMenu, footer, header {{
    visibility: hidden;
}}

.stApp {{
    background-color: white;
    background-image:
        linear-gradient(rgba(255,255,255,0.80), rgba(255,255,255,0.95)),
        url("{bg_src}");
    background-size: cover;
    background-position: center top;
    background-repeat: no-repeat;
    color: var(--texto);
}}

.block-container {{
    padding-top: 2.2rem;
    padding-bottom: 3rem;
    max-width: 1800px;
}}

.hero {{
    text-align: center;
    margin: 0 auto 34px auto;
    max-width: 1050px;
}}

.hero h1 {{
    color: var(--azul);
    font-size: clamp(38px, 3vw, 62px);
    line-height: 1.05;
    font-weight: 900;
    margin-bottom: 22px;
    letter-spacing: -0.8px;
}}

.hero .subtitulo {{
    color: var(--texto);
    font-size: 20px;
    font-weight: 700;
    margin-bottom: 34px;
}}

.hero .descripcion {{
    color: var(--texto);
    font-size: 21px;
    font-weight: 500;
    line-height: 1.55;
    margin: 0 auto;
    max-width: 980px;
}}

.cards-grid {{
    display: grid;
    grid-template-columns: repeat(4, minmax(230px, 1fr));
    gap: 22px;
    width: 100%;
    margin: 0 auto;
    align-items: start;
}}

.card-link {{
    text-decoration: none !important;
    color: inherit !important;
    display: block;
}}

.valera-card {{
    min-height: 255px;
    background: rgba(255,255,255,0.94);
    border: 1px solid var(--borde);
    border-radius: 26px;
    box-shadow: 0 18px 42px rgba(12, 33, 74, 0.10);
    padding: 34px 28px 26px 28px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    overflow: hidden;
    cursor: pointer;
    transition: 0.18s ease;
}}

.valera-card:hover {{
    transform: translateY(-4px);
    box-shadow: 0 24px 54px rgba(12, 33, 74, 0.18);
    border-color: rgba(11, 42, 111, 0.24);
}}

.valera-card img {{
    max-width: 90%;
    max-height: 132px;
    object-fit: contain;
    margin-bottom: 24px;
}}

.valera-card h2 {{
    color: var(--azul);
    font-size: 25px;
    line-height: 1.1;
    font-weight: 900;
    margin: 0;
}}

.stagger-1 {{ margin-top: 0px; }}
.stagger-2 {{ margin-top: 65px; }}
.stagger-3 {{ margin-top: 130px; }}
.stagger-4 {{ margin-top: 195px; }}

.top-bar {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 14px;
    margin-bottom: 22px;
}}

.back-link {{
    display: inline-flex;
    align-items: center;
    justify-content: center;
    background: var(--azul);
    color: white !important;
    text-decoration: none !important;
    padding: 11px 18px;
    border-radius: 10px;
    font-weight: 800;
    box-shadow: 0 8px 18px rgba(11, 42, 111, 0.18);
}}

.back-link:hover {{
    background: var(--azul-oscuro);
}}

.map-title {{
    color: var(--azul);
    font-size: 42px;
    font-weight: 900;
    margin: 0;
}}

.kpi-grid {{
    display: grid;
    grid-template-columns: repeat(4, minmax(180px, 1fr));
    gap: 16px;
    margin-bottom: 22px;
}}

.kpi-card {{
    background: rgba(255,255,255,0.94);
    border: 1px solid var(--borde);
    border-radius: 18px;
    padding: 18px 20px;
    box-shadow: 0 12px 28px rgba(12, 33, 74, 0.08);
}}

.kpi-label {{
    color: var(--texto);
    font-size: 13px;
    font-weight: 700;
    opacity: 0.78;
    margin-bottom: 6px;
}}

.kpi-value {{
    color: var(--azul);
    font-size: 30px;
    font-weight: 900;
    line-height: 1;
}}

.selector-box {{
    background: rgba(255,255,255,0.94);
    border: 1px solid var(--borde);
    border-radius: 18px;
    padding: 16px 18px;
    box-shadow: 0 12px 28px rgba(12, 33, 74, 0.08);
    margin-bottom: 18px;
}}

.small-caption {{
    font-size: 13px;
    font-weight: 700;
    color: var(--texto);
    opacity: 0.72;
    margin-bottom: 7px;
}}

.resumen-title-box {{
    background: rgba(255,255,255,0.94);
    border: 1px solid var(--borde);
    border-radius: 18px;
    padding: 13px 18px;
    box-shadow: 0 12px 28px rgba(12, 33, 74, 0.08);
    min-height: 42px;
    display: flex;
    align-items: center;
}}

.resumen-title-text {{
    font-size: 13px;
    font-weight: 800;
    color: var(--texto);
    opacity: 0.78;
}}



/* Botones y controles con el color de la valera seleccionada */
.stButton > button[kind="primary"] {{
    background: var(--azul) !important;
    border-color: var(--azul) !important;
    color: white !important;
    font-weight: 800 !important;
}}

.stButton > button[kind="primary"]:hover {{
    background: var(--azul-oscuro) !important;
    border-color: var(--azul-oscuro) !important;
    color: white !important;
}}

.stButton > button[kind="secondary"] {{
    color: var(--azul) !important;
    border-color: rgba(0,0,0,0.18) !important;
    background: rgba(255,255,255,0.92) !important;
}}

.stButton > button[kind="secondary"]:hover {{
    border-color: var(--azul) !important;
    color: var(--azul-oscuro) !important;
}}

.stSelectbox div[data-baseweb="select"] > div {{
    border-color: var(--azul) !important;
}}

.valera-card h2 {{
    color: var(--card-primary, var(--azul)) !important;
}}

.card-link:hover .valera-card {{
    border-color: var(--card-primary, var(--azul)) !important;
    box-shadow: 0 24px 54px rgba(12, 33, 74, 0.18), 0 0 0 2px var(--card-soft, var(--borde));
}}

.tabla-valeras-wrap {{
    width: 100%;
    max-width: 100%;
    overflow-x: visible;
    margin-top: 8px;
}}

.tabla-valeras-wrap.scroll-interno {{
    max-height: 565px;
    overflow-y: auto;
    border-radius: 10px;
}}

.tabla-valeras-wrap.scroll-interno table thead th {{
    position: sticky;
    top: 0;
    z-index: 5;
}}

.tabla-valeras-wrap table {{
    width: 100% !important;
}}

.ai-panel {{
    background: rgba(255,255,255,0.96);
    border: 1px solid var(--borde);
    border-left: 7px solid var(--azul);
    border-radius: 20px;
    padding: 22px 24px;
    margin: 22px 0 18px 0;
    box-shadow: 0 14px 34px rgba(12, 33, 74, 0.08);
}}

.ai-panel h3 {{
    color: var(--azul);
    font-size: 22px;
    font-weight: 900;
    margin: 0 0 10px 0;
}}

.ai-panel p {{
    color: var(--texto);
    font-size: 15px;
    line-height: 1.55;
    margin: 8px 0;
}}

.ai-grid {{
    display: grid;
    grid-template-columns: repeat(3, minmax(220px, 1fr));
    gap: 14px;
    margin: 16px 0 20px 0;
}}

.ai-card {{
    background: linear-gradient(180deg, rgba(255,255,255,0.98), rgba(250,252,255,0.96));
    border: 1px solid var(--borde);
    border-radius: 18px;
    padding: 17px 18px;
    box-shadow: 0 10px 25px rgba(12, 33, 74, 0.07);
}}

.ai-card .ai-label {{
    color: var(--texto);
    font-size: 12px;
    font-weight: 800;
    opacity: 0.72;
    margin-bottom: 7px;
    text-transform: uppercase;
    letter-spacing: 0.3px;
}}

.ai-card .ai-value {{
    color: var(--azul);
    font-size: 20px;
    font-weight: 900;
    line-height: 1.15;
}}

.ai-card .ai-note {{
    color: var(--texto);
    font-size: 13px;
    font-weight: 600;
    opacity: 0.82;
    margin-top: 8px;
    line-height: 1.35;
}}

.ai-guide {{
    display: grid;
    grid-template-columns: repeat(2, minmax(260px, 1fr));
    gap: 14px;
    margin-top: 14px;
}}

.ai-guide-card {{
    background: rgba(255,255,255,0.92);
    border: 1px solid var(--borde);
    border-radius: 16px;
    padding: 15px 17px;
}}

.ai-guide-card h4 {{
    color: var(--azul);
    font-size: 15px;
    font-weight: 900;
    margin: 0 0 8px 0;
}}

.ai-guide-card ul {{
    margin: 0;
    padding-left: 18px;
}}

.ai-guide-card li {{
    color: var(--texto);
    font-size: 13px;
    line-height: 1.45;
    margin-bottom: 5px;
}}

.map-guide-side {{
    background: linear-gradient(180deg, rgba(255,255,255,0.98), rgba(250,252,255,0.96));
    border: 1px solid var(--borde);
    border-left: 7px solid var(--azul);
    border-radius: 20px;
    padding: 22px 24px;
    margin: 0 0 18px 0;
    box-shadow: 0 14px 34px rgba(12, 33, 74, 0.08);
}}

.map-guide-side h3 {{
    color: var(--azul);
    font-size: 24px;
    font-weight: 950;
    margin: 0 0 12px 0;
    letter-spacing: -0.2px;
}}

.map-guide-side p {{
    color: var(--texto);
    font-size: 16px;
    line-height: 1.55;
    font-weight: 600;
    margin: 0 0 14px 0;
}}

.map-guide-side ul {{
    margin: 0;
    padding-left: 20px;
}}

.map-guide-side li {{
    color: var(--texto);
    font-size: 15px;
    line-height: 1.55;
    font-weight: 600;
    margin-bottom: 7px;
}}

.map-guide-side b {{
    color: var(--azul);
    font-weight: 900;
}}

@media (max-width: 900px) {{
    .ai-grid,
    .ai-guide {{
        grid-template-columns: 1fr;
    }}
}}


@media (max-width: 1100px) {{
    .cards-grid {{
        grid-template-columns: repeat(2, minmax(250px, 1fr));
    }}

    .stagger-1,
    .stagger-2,
    .stagger-3,
    .stagger-4 {{
        margin-top: 0px;
    }}
}}

@media (max-width: 700px) {{
    .cards-grid {{
        grid-template-columns: 1fr;
        gap: 18px;
    }}

    .valera-card {{
        min-height: 220px;
    }}

    .hero h1 {{
        font-size: 38px;
    }}

    .hero .descripcion {{
        font-size: 17px;
    }}

    .kpi-grid {{
        grid-template-columns: 1fr 1fr;
    }}

    .top-bar {{
        flex-direction: column;
        align-items: flex-start;
    }}
}}
</style>
""",
    unsafe_allow_html=True,
)


# ======================================================
# PÁGINA PRINCIPAL
# ======================================================
def mostrar_inicio():
    st.markdown(
        """
<section class="hero">
<h1>Valeras</h1>
<div class="subtitulo">Semanal</div>
<p class="descripcion">
En esta página puedes consultar la evolución semanal, revisar KPIs,
comparar contra la semana anterior, identificar mejores y peores semanas,
analizar movimientos de coordinadoras y generar un resumen ejecutivo
por país o valera.
</p>
</section>
""",
        unsafe_allow_html=True,
    )

    cards_html = '<section class="cards-grid">'

    for item in VALES:
        logo = img_src(item["logo"])
        nombre = item["nombre"]
        param = item["param"]
        stagger = item["stagger"]

        tema_card = TEMAS_VALERA.get(param, TEMAS_VALERA["default"])
        estilo_card = (
            f"--card-primary:{tema_card['primario']};"
            f"--card-accent:{tema_card['acento']};"
            f"--card-soft:{tema_card['suave']};"
        )

        cards_html += (
            f'<a class="card-link {stagger}" style="{estilo_card}" href="?valera={param}" target="_self">'
            f'<div class="valera-card">'
            f'<img src="{logo}" alt="{nombre}">'
            f'<h2>{nombre}</h2>'
            f'</div>'
            f'</a>'
        )

    cards_html += "</section>"

    st.markdown(cards_html, unsafe_allow_html=True)


# ======================================================
# BOTONES
# ======================================================
def selector_botones(titulo: str, opciones: list[str], key: str, default: str) -> str:
    if titulo:
        st.markdown(
            f"""
<div class="selector-box">
<div class="small-caption">{titulo}</div>
</div>
""",
            unsafe_allow_html=True,
        )

    if key not in st.session_state:
        st.session_state[key] = default

    cols = st.columns(len(opciones))

    for col, opcion in zip(cols, opciones):
        tipo = "primary" if st.session_state[key] == opcion else "secondary"
        if col.button(opcion, type=tipo, use_container_width=True, key=f"{key}_{opcion}"):
            st.session_state[key] = opcion
            st.rerun()

    return st.session_state[key]


# ======================================================
# RESÚMENES
# ======================================================
def preparar_mapa_por_nivel(
    df: pd.DataFrame,
    nivel_vista: str,
    variable_tamano: str,
) -> pd.DataFrame:
    df = df.dropna(subset=["Latitud", "Longitud"]).copy()

    if df.empty:
        return df

    if nivel_vista == "Subdirección":
        group_cols = ["País", "Subdirección"]
        nombre_col = "Subdirección"
    elif nivel_vista == "Zona":
        group_cols = ["País", "Subdirección", "Zona"]
        nombre_col = "Zona"
    else:
        group_cols = ["País", "Subdirección", "Zona", "Sucursal"]
        nombre_col = "Sucursal"

    agg_dict = {
        "Latitud": ("Latitud", "mean"),
        "Longitud": ("Longitud", "mean"),
        "Coordinaciones": ("Coordinacion", "nunique"),
        "Sucursales": ("Sucursal", "nunique"),
        "Zonas": ("Zona", "nunique"),
        "Distribuidoras en Mora": ("Distribuidoras en Mora", "sum"),
        "Var Dist Corriente": ("Var Dist Corriente", "sum"),
        "Var Dist en Mora": ("Var Dist en Mora", "sum"),
        "Total Dispersado": ("Total Dispersado", "sum"),
        "Canjes": ("Canjes", "sum"),
        "Canjes Fecha Corte": ("Canjes Fecha Corte", "sum"),
        "Total Dispersado Fecha Corte": ("Total Dispersado Fecha Corte", "sum"),
    }

    if variable_tamano == "Calidad de Cartera":
        agg_dict[variable_tamano] = (variable_tamano, "mean")
    else:
        agg_dict[variable_tamano] = (variable_tamano, "sum")

    for col in ["Calidad de Cartera", "Distribuidoras Totales", "Distribuidoras al Corriente"]:
        if col not in agg_dict and col in df.columns:
            agg_dict[col] = (col, "mean" if col == "Calidad de Cartera" else "sum")

    df_agg = (
        df.groupby(group_cols, as_index=False)
        .agg(**agg_dict)
        .sort_values(variable_tamano, ascending=False)
    )

    for col in ["Subdirección", "Zona", "Sucursal"]:
        if col not in df_agg.columns:
            df_agg[col] = "Todos"

    df_agg[nivel_vista] = df_agg[nombre_col]
    df_agg = agregar_columnas_variacion(df_agg)
    df_agg = recalcular_canje_promedio(df_agg)

    return df_agg


def aplicar_filtro_tabla(df: pd.DataFrame, modo: str, variable_tamano: str) -> pd.DataFrame:
    if df.empty:
        return df

    df = df.copy()

    if modo == "Top 10":
        return df.sort_values(variable_tamano, ascending=False).head(10)

    if modo == "Bottom 10":
        return df.sort_values(variable_tamano, ascending=True).head(10)

    return df.sort_values(variable_tamano, ascending=False)


def preparar_resumen_estado(df: pd.DataFrame, geojson: dict, prop_estado: str, mapa_geo: dict) -> pd.DataFrame:
    df = df[df["Estado"] != "Sin estado"].copy()

    if df.empty:
        return df

    resumen = (
        df.groupby(["Estado", "Subdirección"], as_index=False)
        .agg(
            Calidad_de_Cartera=("Calidad de Cartera", "mean"),
            Distribuidoras_Totales=("Distribuidoras Totales", "sum"),
            Distribuidoras_al_Corriente=("Distribuidoras al Corriente", "sum"),
            Sucursales=("Sucursal", "nunique"),
            Coordinaciones=("Coordinacion", "nunique"),
        )
    )

    idx = resumen.groupby("Estado")["Distribuidoras_Totales"].idxmax()
    principal = resumen.loc[idx, ["Estado", "Subdirección"]].rename(
        columns={"Subdirección": "Subdirección Principal"}
    )

    resumen_estado = (
        df.groupby("Estado", as_index=False)
        .agg(
            Calidad_de_Cartera=("Calidad de Cartera", "mean"),
            Distribuidoras_Totales=("Distribuidoras Totales", "sum"),
            Distribuidoras_al_Corriente=("Distribuidoras al Corriente", "sum"),
            Sucursales=("Sucursal", "nunique"),
            Coordinaciones=("Coordinacion", "nunique"),
        )
        .merge(principal, on="Estado", how="left")
    )

    resumen_suc = (
        df.groupby(["Estado", "Sucursal"], as_index=False)
        .agg(
            Calidad_de_Cartera=("Calidad de Cartera", "mean"),
            Distribuidoras_Totales=("Distribuidoras Totales", "sum"),
            Distribuidoras_al_Corriente=("Distribuidoras al Corriente", "sum"),
        )
        .sort_values(["Estado", "Distribuidoras_Totales"], ascending=[True, False])
    )

    textos = {}

    for estado, g in resumen_suc.groupby("Estado"):
        lineas = []

        for _, r in g.iterrows():
            lineas.append(
                f"{r['Sucursal']}: "
                f"CC {r['Calidad_de_Cartera']:.2f}% | "
                f"Tot {r['Distribuidoras_Totales']:,.0f} | "
                f"Cte {r['Distribuidoras_al_Corriente']:,.0f}"
            )

        textos[estado] = "<br>".join(lineas[:25])

    resumen_estado["Resumen Sucursales"] = resumen_estado["Estado"].map(textos).fillna("")
    resumen_estado["Estado Normalizado"] = resumen_estado["Estado"].map(normalizar_estado_datos)
    resumen_estado["Estado Geo"] = resumen_estado["Estado Normalizado"].apply(
        lambda x: resolver_estado_geo(x, mapa_geo)
    )

    sin_match = resumen_estado[resumen_estado["Estado Geo"].isna()]["Estado"].dropna().unique().tolist()
    resumen_estado = resumen_estado.dropna(subset=["Estado Geo"])

    if resumen_estado.empty and sin_match:
        st.warning(
            "No hubo coincidencia entre los departamentos/estados de la base y el GeoJSON. "
            f"Sin coincidencia: {', '.join(map(str, sin_match))}."
        )

    resumen_estado = resumen_estado.rename(
        columns={
            "Calidad_de_Cartera": "Calidad de Cartera",
            "Distribuidoras_Totales": "Distribuidoras Totales",
            "Distribuidoras_al_Corriente": "Distribuidoras al Corriente",
        }
    )

    return resumen_estado



# ======================================================
# MUNICIPIOS / ESTILOS DE TABLAS
# ======================================================
@st.cache_data(show_spinner=False)
def cargar_geojson_municipios_mexico() -> dict:
    if ARCHIVO_GEOJSON_MUN_MX.exists():
        with open(ARCHIVO_GEOJSON_MUN_MX, "r", encoding="utf-8") as f:
            return json.load(f)

    urls = [
        # Archivo real del repositorio angelnmara/geojson.
        # Los nombres mexicoMun.json / mexicoMunicipios.json ya no existen y daban 404.
        "https://raw.githubusercontent.com/angelnmara/geojson/master/MunicipiosMexico.json",
        "https://github.com/angelnmara/geojson/raw/master/MunicipiosMexico.json",
    ]

    ultimo_error = None
    for url in urls:
        try:
            with urllib.request.urlopen(url, timeout=25) as response:
                data = json.loads(response.read().decode("utf-8"))
            with open(ARCHIVO_GEOJSON_MUN_MX, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False)
            return data
        except Exception as e:
            ultimo_error = e

    raise ValueError(
        "No pude cargar el GeoJSON municipal de México. "
        "Descarga el archivo MunicipiosMexico.json y guárdalo en esta carpeta con el nombre "
        "mexico_municipios.geojson. "
        "También revisa que la PC tenga internet y que GitHub no esté bloqueado. "
        f"Último error: {ultimo_error}"
    )


def detectar_propiedad_municipio_estado(geojson: dict) -> tuple[str | None, str | None]:
    props = geojson.get("features", [{}])[0].get("properties", {})
    candidatos_estado = ["state_name", "NAME_1", "NOM_ENT", "nom_ent", "ESTADO", "estado", "admin1", "entidad"]
    candidatos_mun = ["mun_name", "NAME_2", "NOM_MUN", "nom_mun", "MUNICIPIO", "municipio", "admin2", "name"]

    prop_estado = next((c for c in candidatos_estado if c in props), None)
    prop_mun = next((c for c in candidatos_mun if c in props), None)
    return prop_estado, prop_mun


def filtrar_geojson_municipios_por_estado(estado: str) -> dict | None:
    try:
        geo_mun = cargar_geojson_municipios_mexico()
    except Exception:
        return None

    prop_estado, _ = detectar_propiedad_municipio_estado(geo_mun)
    if not prop_estado:
        return None

    estado_norm = normalizar_estado_datos(estado)
    features = []
    for feature in geo_mun.get("features", []):
        nombre_estado = feature.get("properties", {}).get(prop_estado, "")
        if normalizar_estado_geo(nombre_estado) == estado_norm:
            features.append(feature)

    if not features:
        return None

    return {"type": "FeatureCollection", "features": features}


def agregar_columnas_variacion(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for col in ["Distribuidoras en Mora", "Var Dist Corriente", "Var Dist en Mora"]:
        if col not in df.columns:
            df[col] = 0
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    df["Semaforo Variacion"] = df.apply(
        lambda r: "Verde" if pd.to_numeric(r["Var Dist Corriente"], errors="coerce") > 0 else "Rojo",
        axis=1,
    )
    return df


def estilo_variacion(row):
    """Colorea únicamente Var Dist Corriente, no toda la fila."""
    estado = str(row.get("Semaforo Variacion", ""))
    estilos = []
    for col in row.index:
        if col == "Var Dist Corriente":
            if estado == "Verde":
                estilos.append("background-color: #DFF5E1; color: #0B5D1E; font-weight: 700")
            elif estado == "Rojo":
                estilos.append("background-color: #FDE2E2; color: #8A1F1F; font-weight: 700")
            else:
                estilos.append("")
        else:
            estilos.append("")
    return estilos


def formatear_porcentaje_tabla(valor) -> str:
    numero = pd.to_numeric(valor, errors="coerce")
    if pd.isna(numero):
        return ""

    # Si el archivo viene como 0.6244 lo mostramos como 62.44%;
    # si viene como 62.44 lo mostramos como 62.44%.
    if abs(float(numero)) <= 1:
        numero = float(numero) * 100

    return f"{float(numero):,.2f}%"


def formatear_entero_miles(valor) -> str:
    numero = pd.to_numeric(valor, errors="coerce")
    if pd.isna(numero):
        return ""

    return f"{float(numero):,.0f}"


def formatear_decimal(valor) -> str:
    numero = pd.to_numeric(valor, errors="coerce")
    if pd.isna(numero):
        return ""

    return f"{float(numero):,.2f}"


def configurar_columnas_tabla(df: pd.DataFrame) -> dict:
    """
    Se conserva por compatibilidad, pero las tablas principales se renderizan
    como HTML para ocupar todo el ancho disponible, mostrar encabezados completos
    y evitar la barra horizontal.
    """
    config = {}

    columnas_grandes = {
        "Calidad de Cartera",
        "Distribuidoras Totales",
        "Distribuidoras al Corriente",
        "Distribuidoras en Mora",
        "Var Dist Corriente",
        "Var Dist en Mora",
        "Total Dispersado",
        "Canjes",
        "Canje Promedio Acumulado",
    }

    columnas_medias = {
        "Subdirección",
        "Subdirección Principal",
        "Coordinaciones",
        "Sucursales",
        "Zonas",
        "Estado",
        "Sucursal",
        "Zona",
        "País",
    }

    for col in df.columns:
        if col == "Semaforo Variacion":
            continue

        if col in columnas_grandes:
            ancho = "large"
        elif col in columnas_medias or len(str(col)) >= 14:
            ancho = "medium"
        else:
            ancho = "small"

        config[col] = st.column_config.TextColumn(label=str(col), width=ancho)

    return config


def preparar_tabla_para_mostrar(
    df: pd.DataFrame,
    columnas_ocultas: list[str] | None = None,
) -> pd.DataFrame:
    """Formatea valores visibles sin modificar los datos originales."""
    tabla = df.copy()

    # La columna se usa sólo para colorear filas; no debe mostrarse.
    if "Semaforo Variacion" in tabla.columns:
        tabla = tabla.drop(columns=["Semaforo Variacion"])

    if columnas_ocultas:
        existentes = [col for col in columnas_ocultas if col in tabla.columns]
        if existentes:
            tabla = tabla.drop(columns=existentes)

    if "Calidad de Cartera" in tabla.columns:
        tabla["Calidad de Cartera"] = tabla["Calidad de Cartera"].map(formatear_porcentaje_tabla)

    columnas_miles = [
        "Coordinaciones",
        "Sucursales",
        "Zonas",
        "Subdirecciones",
        "Distribuidoras Totales",
        "Distribuidoras al Corriente",
        "Distribuidoras en Mora",
        "Var Dist Corriente",
        "Var Dist en Mora",
        "Canjes",
        "Canjes Fecha Corte",
    ]

    columnas_moneda = [
        "Total Dispersado",
        "Canje Promedio Acumulado",
        "Total Dispersado Fecha Corte",
    ]

    for col in columnas_miles:
        if col in tabla.columns:
            tabla[col] = tabla[col].map(formatear_entero_miles)

    for col in columnas_moneda:
        if col in tabla.columns:
            tabla[col] = tabla[col].map(formato_moneda)

    return tabla.fillna("")


def estilo_variacion_visible(row):
    """Colorea sólo Var Dist Corriente: verde si es positivo y rojo si es negativo o cero."""
    estado = str(row.get("__semaforo__", ""))
    estilos = []

    for col in row.index:
        if col == "Var Dist Corriente":
            if estado == "Verde":
                estilos.append("background-color: #DFF5E1; color: #0B5D1E; font-weight: 700")
            elif estado == "Rojo":
                estilos.append("background-color: #FDE2E2; color: #8A1F1F; font-weight: 700")
            else:
                estilos.append("")
        else:
            estilos.append("")

    return estilos


def mostrar_tabla_variacion(
    df: pd.DataFrame,
    columnas_ocultas: list[str] | None = None,
    scroll_interno: bool = False,
    mostrar_indice_ordenado: bool = False,
):
    if df.empty:
        st.dataframe(df, use_container_width=True, hide_index=True)
        return

    semaforo = df["Semaforo Variacion"].copy() if "Semaforo Variacion" in df.columns else pd.Series("", index=df.index)
    tabla = preparar_tabla_para_mostrar(df, columnas_ocultas=columnas_ocultas)

    # Para Top 10 y Bottom 10, la primera columna debe ser ranking 1, 2, 3...
    # En Todos no se muestra índice para evitar la columna de números.
    if mostrar_indice_ordenado:
        tabla = tabla.reset_index(drop=True)
        tabla.index = range(1, len(tabla) + 1)
        tabla.index.name = ""

    tabla["__semaforo__"] = semaforo.values

    styler_base = (
        tabla.style
        .apply(estilo_variacion_visible, axis=1)
        .hide(axis="columns", subset=["__semaforo__"])
    )

    if not mostrar_indice_ordenado:
        styler_base = styler_base.hide(axis="index")

    styler = (
        styler_base
        .set_table_styles(
            [
                {
                    "selector": "table",
                    "props": [
                        ("width", "100%"),
                        ("table-layout", "fixed"),
                        ("border-collapse", "collapse"),
                    ],
                },
                {
                    "selector": "th",
                    "props": [
                        ("white-space", "normal"),
                        ("word-break", "normal"),
                        ("overflow-wrap", "break-word"),
                        ("font-weight", "700"),
                        ("font-size", "13px"),
                        ("line-height", "1.18"),
                        ("text-align", "left"),
                        ("padding", "8px 8px"),
                        ("background-color", "#F4F6FA"),
                        ("color", "#34507A"),
                        ("border", "1px solid rgba(11,42,111,0.12)"),
                    ],
                },
                {
                    "selector": "td",
                    "props": [
                        ("white-space", "normal"),
                        ("word-break", "normal"),
                        ("overflow-wrap", "break-word"),
                        ("font-size", "13px"),
                        ("line-height", "1.18"),
                        ("padding", "8px 8px"),
                        ("border", "1px solid rgba(11,42,111,0.10)"),
                    ],
                },
            ]
        )
    )

    clase_scroll = " scroll-interno" if scroll_interno else ""

    st.markdown(
        f"""
<div class="tabla-valeras-wrap{clase_scroll}">
{styler.to_html()}
</div>
""",
        unsafe_allow_html=True,
    )




# ======================================================
# COMENTARIOS TIPO IA / GUÍA DE INTERACCIÓN
# ======================================================
def obtener_top_registro(df: pd.DataFrame, campo: str, nombre_col: str = "Sucursal") -> tuple[str, float]:
    if df.empty or campo not in df.columns or nombre_col not in df.columns:
        return "Sin dato", 0

    tmp = df.copy()
    tmp[campo] = pd.to_numeric(tmp[campo], errors="coerce").fillna(0)
    if tmp.empty:
        return "Sin dato", 0

    idx = tmp[campo].idxmax()
    if pd.isna(idx):
        return "Sin dato", 0

    return str(tmp.loc[idx, nombre_col]), float(tmp.loc[idx, campo])


def texto_tipo_mapa(tipo_mapa: str) -> str:
    if tipo_mapa == "Calor Canjes":
        return "El mapa de calor está mostrando canjes del día exacto de la fecha de corte: rojo indica menor volumen y verde mayor volumen."
    if tipo_mapa == "Calor Dispersado":
        return "El mapa de calor está mostrando dispersado del día exacto de la fecha de corte: rojo indica menor importe y verde mayor importe."
    return "El mapa está coloreando las sucursales por Subdirección, útil para identificar cobertura territorial y concentración operativa."


def html_guia_mapa_previa(tipo_mapa: str) -> str:
    """Devuelve la guía del mapa en formato ejecutivo para colocarla junto a Tipo de mapa."""
    return f"""
<div class="map-guide-side">
    <h3>Cómo interactuar con el mapa</h3>
    <p>{texto_tipo_mapa(tipo_mapa)}</p>
    <ul>
        <li>Pasa el cursor sobre una bolita para consultar sucursal, subdirección, zona, calidad, distribuidoras, canjes y dispersión.</li>
        <li>Usa <b>Subdirección</b> para identificar cobertura territorial por estructura operativa.</li>
        <li>Usa <b>Calor Canjes</b> para detectar concentración de canjes del día exacto de corte.</li>
        <li>Usa <b>Calor Dispersado</b> para ubicar la concentración del importe dispersado en el día exacto de corte.</li>
        <li>Da clic en un estado para entrar al detalle territorial y vuelve con el botón de regreso.</li>
    </ul>
</div>
"""


def mostrar_guia_mapa_previa(tipo_mapa: str):
    """Muestra la explicación del mapa."""
    st.markdown(html_guia_mapa_previa(tipo_mapa), unsafe_allow_html=True)


def mostrar_comentarios_ia(
    df_resumen_base: pd.DataFrame,
    df_mapa: pd.DataFrame,
    resumen_pais: pd.DataFrame,
    nombre_valera: str,
    fecha_sel: str,
    nivel_vista: str,
    variable_tamano: str,
    tipo_mapa: str,
    solo_ejecutivo: bool = False,
    ocultar_ejecutivo: bool = False,
    conservar_tarjetas: bool = False,
):
    if df_resumen_base.empty:
        return

    fecha_sel = obtener_corte_desde_base(df_resumen_base, fecha_sel)

    total_distribuidoras = pd.to_numeric(df_resumen_base.get("Distribuidoras Totales", 0), errors="coerce").fillna(0).sum()
    total_corriente = pd.to_numeric(df_resumen_base.get("Distribuidoras al Corriente", 0), errors="coerce").fillna(0).sum()
    total_mora = pd.to_numeric(df_resumen_base.get("Distribuidoras en Mora", 0), errors="coerce").fillna(0).sum()
    var_corriente = pd.to_numeric(df_resumen_base.get("Var Dist Corriente", 0), errors="coerce").fillna(0).sum()
    var_mora = pd.to_numeric(df_resumen_base.get("Var Dist en Mora", 0), errors="coerce").fillna(0).sum()
    total_dispersado = pd.to_numeric(df_resumen_base.get("Total Dispersado", 0), errors="coerce").fillna(0).sum()
    total_canjes = pd.to_numeric(df_resumen_base.get("Canjes", 0), errors="coerce").fillna(0).sum()
    canjes_dia = pd.to_numeric(df_resumen_base.get("Canjes Fecha Corte", 0), errors="coerce").fillna(0).sum()
    dispersado_dia = pd.to_numeric(df_resumen_base.get("Total Dispersado Fecha Corte", 0), errors="coerce").fillna(0).sum()

    calidad = (total_corriente / total_distribuidoras * 100) if total_distribuidoras else 0
    pct_corriente = calidad
    pct_mora = (total_mora / total_distribuidoras * 100) if total_distribuidoras else 0
    canje_promedio = (total_dispersado / total_canjes) if total_canjes else 0
    canje_promedio_dia = (dispersado_dia / canjes_dia) if canjes_dia else 0

    paises_contexto = ", ".join(sorted(df_resumen_base.get("País", pd.Series(dtype=str)).dropna().astype(str).unique().tolist()))
    estados_contexto = sorted(df_resumen_base.get("Estado", pd.Series(dtype=str)).dropna().astype(str).unique().tolist())
    if len(estados_contexto) == 1:
        alcance_contexto = f"Estado/departamento activo: <b>{estados_contexto[0]}</b>."
    elif paises_contexto:
        alcance_contexto = f"Vista consolidada para <b>{paises_contexto}</b>."
    else:
        alcance_contexto = "Vista consolidada de la selección actual."

    modo_tabla_actual_ia = st.session_state.get("modo_tabla_resumen", "Todos")
    busqueda_actual_ia = st.session_state.get(f"busqueda_resumen_{nivel_vista.lower()}", "")
    filtro_resumen_ia = (
        f" Resumen activo: <b>{modo_tabla_actual_ia}</b>, nivel <b>{nivel_vista}</b>, "
        f"variable de orden <b>{variable_tamano}</b>."
    )
    if str(busqueda_actual_ia).strip():
        filtro_resumen_ia += f" Búsqueda aplicada: <b>{busqueda_actual_ia}</b>."

    busqueda_texto_ia = ""
    if str(busqueda_actual_ia).strip():
        busqueda_texto_ia = f" La búsqueda activa es <b>{busqueda_actual_ia}</b>."

    if calidad >= 70:
        lectura_calidad = "La calidad de cartera se mantiene en un rango sólido; el objetivo debe ser sostener la disciplina operativa y proteger las zonas que explican la mayor base al corriente."
    elif calidad >= 55:
        lectura_calidad = "La calidad de cartera se ubica en un rango intermedio; existe una base relevante al corriente, aunque la mora todavía presiona el desempeño y requiere gestión puntual por zona y sucursal."
    else:
        lectura_calidad = "La calidad de cartera se encuentra en zona de atención; la prioridad debe centrarse en recuperación, seguimiento a sucursales críticas y contención del deterioro operativo."

    if canjes_dia > 0:
        lectura_corte = (
            f"En el día de corte se registraron <b>{formato_numero(canjes_dia)}</b> canjes "
            f"por <b>{formato_moneda(dispersado_dia)}</b>, con un canje promedio del día de "
            f"<b>{formato_moneda(canje_promedio_dia)}</b>."
        )
    else:
        lectura_corte = "En el día de corte no se observan canjes registrados; conviene validar si la operación diaria ya fue cargada en la base de dispersión."

    if var_corriente > 0:
        lectura_var = "La variación de distribuidoras al corriente es positiva, por lo que la señal operativa del corte es favorable."
        tono_var = "Mejora operativa"
        prioridad_ia = "Prioridad sugerida: identificar las sucursales que explican la mejora al corriente y replicar esas prácticas en zonas con menor calidad o menor productividad del corte."
    elif var_corriente < 0:
        lectura_var = "La variación de distribuidoras al corriente es negativa, por lo que conviene revisar las zonas o sucursales con mayor deterioro."
        tono_var = "Atención requerida"
        prioridad_ia = "Prioridad sugerida: revisar las sucursales con caída en distribuidoras al corriente, contrastarlas contra los canjes del día y enfocar el seguimiento donde coincidan baja calidad y alta mora."
    else:
        lectura_var = "La variación de distribuidoras al corriente se mantiene estable; el foco debe ser sostener la base al corriente."
        tono_var = "Estabilidad"
        prioridad_ia = "Prioridad sugerida: mantener vigilancia sobre calidad y dispersión; con el movimiento al corriente estable, el siguiente foco debe ser mejorar la conversión por sucursal."

    def resumen_base_por_sucursal() -> pd.DataFrame:
        columnas_necesarias = ["Sucursal"]
        if not all(col in df_resumen_base.columns for col in columnas_necesarias):
            return pd.DataFrame()

        df_tmp = df_resumen_base.copy()
        for col in [
            "Distribuidoras Totales",
            "Distribuidoras al Corriente",
            "Distribuidoras en Mora",
            "Var Dist Corriente",
            "Var Dist en Mora",
            "Total Dispersado",
            "Canjes",
            "Canjes Fecha Corte",
            "Total Dispersado Fecha Corte",
        ]:
            if col not in df_tmp.columns:
                df_tmp[col] = 0
            df_tmp[col] = pd.to_numeric(df_tmp[col], errors="coerce").fillna(0)

        g = (
            df_tmp.groupby("Sucursal", as_index=False)
            .agg(
                Distribuidoras_Totales=("Distribuidoras Totales", "sum"),
                Distribuidoras_al_Corriente=("Distribuidoras al Corriente", "sum"),
                Distribuidoras_en_Mora=("Distribuidoras en Mora", "sum"),
                Var_Dist_Corriente=("Var Dist Corriente", "sum"),
                Var_Dist_en_Mora=("Var Dist en Mora", "sum"),
                Total_Dispersado=("Total Dispersado", "sum"),
                Canjes=("Canjes", "sum"),
                Canjes_Fecha_Corte=("Canjes Fecha Corte", "sum"),
                Total_Dispersado_Fecha_Corte=("Total Dispersado Fecha Corte", "sum"),
            )
        )
        g["Calidad_Calculada"] = g.apply(
            lambda r: (r["Distribuidoras_al_Corriente"] / r["Distribuidoras_Totales"] * 100) if r["Distribuidoras_Totales"] else 0,
            axis=1,
        )
        return g

    base_sucursal = resumen_base_por_sucursal()

    if not base_sucursal.empty:
        mayor_mora = base_sucursal.sort_values("Distribuidoras_en_Mora", ascending=False).iloc[0]
        mayor_caida = base_sucursal.sort_values("Var_Dist_Corriente", ascending=True).iloc[0]
        mayor_canjes_dia = base_sucursal.sort_values("Canjes_Fecha_Corte", ascending=False).iloc[0]
        mayor_disp_dia_base = base_sucursal.sort_values("Total_Dispersado_Fecha_Corte", ascending=False).iloc[0]

        lectura_base_oculta = (
            "La base completa señala que "
            f"<b>{mayor_mora['Sucursal']}</b> concentra la mayor mora con <b>{formato_numero(mayor_mora['Distribuidoras_en_Mora'])}</b> distribuidoras en mora; "
            f"<b>{mayor_caida['Sucursal']}</b> presenta la mayor caída al corriente con <b>{formato_numero(mayor_caida['Var_Dist_Corriente'])}</b>; "
            f"mientras que en el día de corte la mayor actividad comercial se concentra en <b>{mayor_canjes_dia['Sucursal']}</b> por canjes "
            f"y en <b>{mayor_disp_dia_base['Sucursal']}</b> por dispersión."
        )
    else:
        lectura_base_oculta = "La lectura adicional de base no encontró un nivel de sucursal suficiente para generar alertas complementarias."

    top_disp_nombre, top_disp_valor = obtener_top_registro(df_mapa, "Total Dispersado", nivel_vista)
    top_canjes_nombre, top_canjes_valor = obtener_top_registro(df_mapa, "Canjes Fecha Corte", nivel_vista)
    top_dia_nombre, top_dia_valor = obtener_top_registro(df_mapa, "Total Dispersado Fecha Corte", nivel_vista)

    resumen_html = f"""
<div class="ai-panel">
    <p>
        Al corte <b>{fecha_sel}</b>.
    </p>
    <p>
        La cartera analizada concentra <b>{formato_numero(total_distribuidoras)}</b> distribuidoras:
        <b>{formato_numero(total_corriente)}</b> al corriente (<b>{pct_corriente:,.2f}%</b>) y
        <b>{formato_numero(total_mora)}</b> en mora (<b>{pct_mora:,.2f}%</b>). {lectura_calidad}
    </p>
    <p>
        En actividad comercial, la dispersión acumulada alcanza <b>{formato_moneda(total_dispersado)}</b>,
        soportada por <b>{formato_numero(total_canjes)}</b> canjes y un ticket promedio acumulado de
        <b>{formato_moneda(canje_promedio)}</b>. {lectura_corte}
    </p>
    <p>
        <b>{tono_var}:</b> {lectura_var} El movimiento neto al corriente es de
        <b>{formato_numero(var_corriente)}</b>, frente a una variación en mora de
        <b>{formato_numero(var_mora)}</b>. {prioridad_ia}
    </p>
    <p>
        <b>Foco operativo:</b> {lectura_base_oculta}
    </p>
</div>

<div class="ai-grid">
    <div class="ai-card">
        <div class="ai-label">Mayor dispersión acumulada</div>
        <div class="ai-value">{top_disp_nombre}</div>
        <div class="ai-note">Acumulado: {formato_moneda(top_disp_valor)}</div>
    </div>
    <div class="ai-card">
        <div class="ai-label">Más canjes en fecha de corte</div>
        <div class="ai-value">{top_canjes_nombre}</div>
        <div class="ai-note">Canjes del corte: {formato_numero(top_canjes_valor)}</div>
    </div>
    <div class="ai-card">
        <div class="ai-label">Mayor dispersado del corte</div>
        <div class="ai-value">{top_dia_nombre}</div>
        <div class="ai-note">Dispersado del día: {formato_moneda(top_dia_valor)}</div>
    </div>
</div>

<div class="ai-panel">
    <h3>Cómo usar los botones de resumen</h3>
    <div class="ai-guide">
        <div class="ai-guide-card">
            <h4>Botones de resumen</h4>
            <ul>
                <li><b>Subdirección, Zona y Sucursal</b> cambian el nivel de análisis del mapa y de la tabla inferior.</li>
                <li><b>Calidad de Cartera, Distribuidoras Totales y Distribuidoras al Corriente</b> cambian el tamaño de las bolitas.</li>
                <li><b>Todos</b> muestra el universo completo con scroll interno; <b>Top 10</b> y <b>Bottom 10</b> aíslan mejores y peores registros.</li>
                <li>El buscador filtra por el nivel activo: subdirección, zona o sucursal.</li>
            </ul>
        </div>
    </div>
</div>
"""
    if solo_ejecutivo:
        if conservar_tarjetas:
            partes = resumen_html.split('\n\n<div class="ai-panel">\n    <h3>Cómo usar los botones de resumen</h3>', 1)
            resumen_html = partes[0]
        else:
            resumen_html = resumen_html.split("\n\n<div class=\"ai-grid\">", 1)[0]
    elif ocultar_ejecutivo:
        partes = resumen_html.split("\n\n<div class=\"ai-grid\">", 1)
        if len(partes) > 1:
            resumen_html = '<div class="ai-grid">' + partes[1]
            resumen_html = resumen_html.split('\n\n<div class="ai-panel">\n    <h3>Cómo usar los botones de resumen</h3>', 1)[0]

    st.markdown(resumen_html, unsafe_allow_html=True)




def obtener_corte_desde_base(df: pd.DataFrame | None, default: str = "") -> str:
    """
    Obtiene el corte desde la base que alimenta el objeto visual.
    Prioriza Corte Texto/Corte para Plazo y composición, y después Fecha de Corte Texto
    para estructura/distribuidoras. Sólo usa default si la base no trae corte.
    """
    if df is not None and not df.empty:
        for col in ["Corte Texto", "Corte", "Fecha de Corte Texto", "Fecha de Corte"]:
            if col in df.columns:
                serie = df[col].dropna().astype(str).map(lambda x: arreglar_mojibake(x).strip())
                serie = serie[(serie != "") & (serie.str.upper() != "NAT") & (serie.str.upper() != "SIN FECHA")]
                if not serie.empty:
                    valor = serie.iloc[-1]
                    if col == "Corte":
                        valor_fmt = formatear_corte_plazo(valor)
                        return valor_fmt or valor
                    if col == "Fecha de Corte":
                        return formatear_fecha(valor)
                    return valor
    return default

def _sumar_columna(df: pd.DataFrame, columna: str) -> float:
    if df is None or df.empty or columna not in df.columns:
        return 0.0
    return float(pd.to_numeric(df[columna], errors="coerce").fillna(0).sum())


def _promedio_ponderado_calidad(df: pd.DataFrame) -> float:
    total = _sumar_columna(df, "Distribuidoras Totales")
    corriente = _sumar_columna(df, "Distribuidoras al Corriente")
    return (corriente / total * 100) if total else 0.0


def _nombre_alcance_mapa(df_contexto: pd.DataFrame) -> str:
    if df_contexto is None or df_contexto.empty:
        return "la selección actual"

    estados = sorted(df_contexto.get("Estado", pd.Series(dtype=str)).dropna().astype(str).unique().tolist())
    paises = sorted(df_contexto.get("País", pd.Series(dtype=str)).dropna().astype(str).unique().tolist())

    if len(estados) == 1:
        return f"{estados[0]}"
    if len(paises) == 1:
        return f"{paises[0]}"
    return "la selección actual"


def _top_por_columna(df: pd.DataFrame, columna: str, nivel: str) -> tuple[str, float]:
    if df is None or df.empty or columna not in df.columns or nivel not in df.columns:
        return "Sin dato", 0.0

    tmp = df.copy()
    tmp[columna] = pd.to_numeric(tmp[columna], errors="coerce").fillna(0)
    if tmp.empty:
        return "Sin dato", 0.0

    fila = tmp.sort_values(columna, ascending=False).iloc[0]
    return str(fila[nivel]), float(fila[columna])


def construir_comentario_ia_mapa(
    df_contexto: pd.DataFrame,
    df_mapa: pd.DataFrame,
    nombre_valera: str,
    fecha_sel: str,
    nivel_vista: str,
    variable_tamano: str,
    tipo_mapa: str,
    modo_tabla: str = "Todos",
    texto_busqueda: str = "",
    estado_sel: str = "",
) -> str:
    if df_contexto is None or df_contexto.empty:
        return ""

    fecha_sel = obtener_corte_desde_base(df_contexto, fecha_sel)

    alcance = _nombre_alcance_mapa(df_contexto)
    total = _sumar_columna(df_contexto, "Distribuidoras Totales")
    corriente = _sumar_columna(df_contexto, "Distribuidoras al Corriente")
    mora = _sumar_columna(df_contexto, "Distribuidoras en Mora")
    calidad = _promedio_ponderado_calidad(df_contexto)
    var_corriente = _sumar_columna(df_contexto, "Var Dist Corriente")
    var_mora = _sumar_columna(df_contexto, "Var Dist en Mora")
    canjes_dia = _sumar_columna(df_contexto, "Canjes Fecha Corte")
    dispersado_dia = _sumar_columna(df_contexto, "Total Dispersado Fecha Corte")

    if tipo_mapa == "Calor Canjes":
        top_nombre, top_valor = _top_por_columna(df_mapa, "Canjes Fecha Corte", nivel_vista)
        lectura_color = (
            f"El color está priorizando los <b>canjes del día de corte</b>. "
            f"El mayor punto en la vista activa es <b>{top_nombre}</b>, con <b>{formato_numero(top_valor)}</b> canjes del corte."
        )
    elif tipo_mapa == "Calor Dispersado":
        top_nombre, top_valor = _top_por_columna(df_mapa, "Total Dispersado Fecha Corte", nivel_vista)
        lectura_color = (
            f"El color está priorizando el <b>importe dispersado del día de corte</b>. "
            f"El mayor punto en la vista activa es <b>{top_nombre}</b>, con <b>{formato_moneda(top_valor)}</b> dispersados en el corte."
        )
    else:
        top_nombre, top_valor = _top_por_columna(df_mapa, variable_tamano, nivel_vista)
        lectura_color = (
            f"El color está mostrando la <b>estructura por Subdirección</b> y el tamaño de las bolitas responde a <b>{variable_tamano}</b>. "
            f"El elemento con mayor peso en esa variable es <b>{top_nombre}</b>, con <b>{formato_numero(top_valor) if variable_tamano != 'Calidad de Cartera' else f'{top_valor:,.2f}%'}</b>."
        )

    if calidad >= 70:
        semaforo = "La calidad general es favorable; la lectura del mapa debe enfocarse en sostener cobertura y replicar las zonas fuertes."
    elif calidad >= 55:
        semaforo = "La calidad está en rango medio; conviene usar el mapa para separar zonas con buen volumen de zonas con presión de mora."
    else:
        semaforo = "La calidad está en zona de atención; el mapa debe usarse para ubicar focos de recuperación y priorizar seguimiento operativo."

    if var_corriente > var_mora:
        lectura_var = "La variación favorece a distribuidoras al corriente frente a mora, señal positiva para el corte."
    elif var_corriente < var_mora:
        lectura_var = "La variación en mora pesa más que la mejora al corriente; la interacción debe concentrarse en los puntos rojos o de menor calidad."
    else:
        lectura_var = "La variación está equilibrada; el foco debe pasar a conversión comercial y calidad por zona."

    filtro = ""
    if modo_tabla in ["Top 10", "Bottom 10"]:
        filtro += f" La vista está filtrada en <b>{modo_tabla}</b>, por lo que el mapa resalta sólo los extremos de la variable activa."
    if str(texto_busqueda).strip():
        filtro += f" La búsqueda activa es <b>{texto_busqueda}</b>, así que la lectura queda acotada al texto filtrado."

    ultimo_click = st.session_state.get("ia_mapa_ultimo_click", "")
    lectura_click = ""
    if ultimo_click:
        lectura_click = f" Última interacción detectada: <b>{ultimo_click}</b>; las métricas y la tabla ya se recalcularon con ese contexto."

    return f"""
<div class="ai-panel">
    <p>
        Al corte <b>{fecha_sel}</b>, el mapa de <b>{nombre_valera}</b> está leyendo <b>{alcance}</b> a nivel <b>{nivel_vista}</b>.
        La selección concentra <b>{formato_numero(total)}</b> distribuidoras, con <b>{formato_numero(corriente)}</b> al corriente,
        <b>{formato_numero(mora)}</b> en mora y una calidad de cartera de <b>{calidad:,.2f}%</b>.
    </p>
    <p>{lectura_color} {semaforo}</p>
    <p>
        En el corte del día se observan <b>{formato_numero(canjes_dia)}</b> canjes por <b>{formato_moneda(dispersado_dia)}</b>.
        {lectura_var}{filtro}{lectura_click}
    </p>
</div>
"""


def mostrar_comentario_ia_mapa(*args, **kwargs):
    html = construir_comentario_ia_mapa(*args, **kwargs)
    if html:
        st.markdown(html, unsafe_allow_html=True)


def construir_comentario_ia_tabla_resumen(
    resumen_tabla: pd.DataFrame,
    nivel_vista: str,
    variable_tamano: str,
    modo_tabla: str,
    texto_busqueda: str,
    fecha_sel: str,
    df_fuente: pd.DataFrame | None = None,
) -> str:
    fecha_sel = obtener_corte_desde_base(df_fuente if df_fuente is not None else resumen_tabla, fecha_sel)

    if resumen_tabla is None or resumen_tabla.empty:
        return f"""
<div class="ai-panel">
    <p>No hay registros visibles para la tabla con los filtros actuales. Revisa el buscador o cambia el nivel de resumen.</p>
</div>
"""

    total = _sumar_columna(resumen_tabla, "Distribuidoras Totales")
    corriente = _sumar_columna(resumen_tabla, "Distribuidoras al Corriente")
    mora = _sumar_columna(resumen_tabla, "Distribuidoras en Mora")
    calidad = (corriente / total * 100) if total else 0
    var_corriente = _sumar_columna(resumen_tabla, "Var Dist Corriente")
    var_mora = _sumar_columna(resumen_tabla, "Var Dist en Mora")
    dispersado = _sumar_columna(resumen_tabla, "Total Dispersado")
    canjes = _sumar_columna(resumen_tabla, "Canjes")
    ticket = (dispersado / canjes) if canjes else 0

    top_calidad, top_calidad_val = _top_por_columna(resumen_tabla, "Calidad de Cartera", nivel_vista)
    top_mora, top_mora_val = _top_por_columna(resumen_tabla, "Distribuidoras en Mora", nivel_vista)
    top_disp, top_disp_val = _top_por_columna(resumen_tabla, "Total Dispersado", nivel_vista)
    top_variable, top_variable_val = _top_por_columna(resumen_tabla, variable_tamano, nivel_vista)

    if var_corriente > 0 and var_corriente > var_mora:
        lectura = "La tabla muestra una señal favorable: la mejora al corriente supera la presión de mora."
    elif var_corriente < 0:
        lectura = "La tabla muestra deterioro en distribuidoras al corriente; conviene revisar primero los registros con mayor mora y caída."
    elif var_mora > var_corriente:
        lectura = "La mora está creciendo más que la base al corriente; la prioridad es contener deterioro en los registros con mayor volumen."
    else:
        lectura = "La tabla muestra estabilidad relativa; el foco debe estar en elevar calidad sin sacrificar dispersión."

    filtro = f"Vista <b>{modo_tabla}</b> ordenada por <b>{variable_tamano}</b>."
    if str(texto_busqueda).strip():
        filtro += f" Búsqueda aplicada: <b>{texto_busqueda}</b>."

    valor_top_variable = f"{top_variable_val:,.2f}%" if variable_tamano == "Calidad de Cartera" else formato_numero(top_variable_val)

    return f"""
<div class="ai-panel">
    <p>
        Al corte <b>{fecha_sel}</b>, la tabla visible por <b>{nivel_vista}</b> resume <b>{len(resumen_tabla):,}</b> registros. {filtro}
        En conjunto concentra <b>{formato_numero(total)}</b> distribuidoras, con calidad de cartera de <b>{calidad:,.2f}%</b>
        y ticket promedio acumulado de <b>{formato_moneda(ticket)}</b>.
    </p>
    <p>
        {lectura} El registro líder en <b>{variable_tamano}</b> es <b>{top_variable}</b> con <b>{valor_top_variable}</b>.
        La mayor calidad aparece en <b>{top_calidad}</b> (<b>{top_calidad_val:,.2f}%</b>), mientras que el mayor foco de mora está en
        <b>{top_mora}</b> con <b>{formato_numero(top_mora_val)}</b> distribuidoras en mora.
    </p>
    <p>
        En lectura comercial, <b>{top_disp}</b> concentra la mayor dispersión acumulada visible con <b>{formato_moneda(top_disp_val)}</b>.
        Usa esta tabla para priorizar dónde hay más volumen, dónde se deteriora la cartera y dónde la dispersión requiere seguimiento.
    </p>
</div>
"""


def mostrar_comentario_ia_tabla_resumen(*args, **kwargs):
    html = construir_comentario_ia_tabla_resumen(*args, **kwargs)
    if html:
        st.markdown(html, unsafe_allow_html=True)

# ======================================================
# DIVISIÓN POLÍTICA EXACTA POR SUBDIRECCIÓN
# ======================================================
def extraer_puntos_geometria(geometry: dict) -> list[tuple[float, float]]:
    """Devuelve pares (lon, lat) desde Polygon o MultiPolygon."""
    puntos: list[tuple[float, float]] = []

    def recorrer(obj):
        if not isinstance(obj, list):
            return

        if len(obj) >= 2 and all(isinstance(x, (int, float)) for x in obj[:2]):
            puntos.append((float(obj[0]), float(obj[1])))
            return

        for item in obj:
            recorrer(item)

    recorrer(geometry.get("coordinates", []))
    return puntos


def centroide_feature(feature: dict) -> tuple[float | None, float | None]:
    puntos = extraer_puntos_geometria(feature.get("geometry", {}))
    if not puntos:
        return None, None

    lon = sum(p[0] for p in puntos) / len(puntos)
    lat = sum(p[1] for p in puntos) / len(puntos)
    return lat, lon


def normalizar_municipio(valor) -> str:
    texto = normalizar_nombre_region(valor)
    texto = texto.replace("MUNICIPIO DE ", "")
    texto = texto.replace("MUNICIPIO ", "")
    texto = texto.replace("CIUDAD ", "CD ")
    texto = texto.replace("BENITO JUAREZ", "BENITO JUAREZ")
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto


def detectar_propiedad_municipio_estado(geojson: dict) -> tuple[str | None, str | None]:
    """
    Detecta de forma más robusta las propiedades de estado y municipio.
    Algunos GeoJSON usan NAME_1/NAME_2; otros NOM_ENT/NOM_MUN, state_name/mun_name, etc.
    """
    features = geojson.get("features", [])
    if not features:
        return None, None

    llaves = set()
    for feature in features[:80]:
        llaves.update(feature.get("properties", {}).keys())

    estados_esperados = {
        "BAJA CALIFORNIA", "BAJA CALIFORNIA SUR", "CHIHUAHUA", "COAHUILA",
        "DURANGO", "GUERRERO", "NAYARIT", "NUEVO LEON", "OAXACA", "SINALOA",
        "SONORA", "TABASCO", "TAMAULIPAS", "VERACRUZ", "ZACATECAS", "CHIAPAS",
        "SAN LUIS POTOSI", "MICHOACAN", "JALISCO", "GUANAJUATO", "HIDALGO", "PUEBLA",
    }

    municipios_esperados = {
        "ACAPONETA", "ACAPULCO", "ACAYUCAN", "ALTAMIRA", "CABORCA", "CADEREYTA",
        "CHIHUAHUA", "CULIACAN", "DURANGO", "ENSENADA", "GUAYMAS", "HERMOSILLO",
        "JUAREZ", "LA PAZ", "MAZATLAN", "MEXICALI", "NAVOJOA", "NOGALES",
        "REYNOSA", "SALTILLO", "TEPIC", "TIJUANA", "VERACRUZ", "VILLAHERMOSA",
    }

    candidatos_estado = ["state_name", "NAME_1", "NOM_ENT", "nom_ent", "ESTADO", "estado", "admin1", "entidad", "NAMEUNIT"]
    candidatos_mun = ["mun_name", "NAME_2", "NOM_MUN", "nom_mun", "MUNICIPIO", "municipio", "admin2", "name", "NOMGEO", "NOMBRE"]

    def score(llave: str, esperados: set[str], candidatos: list[str]) -> int:
        valores = []
        for feature in features[:300]:
            props = feature.get("properties", {})
            if llave in props:
                valores.append(normalizar_municipio(props.get(llave, "")))

        valores_set = {v for v in valores if v}
        s = 0
        if llave in candidatos:
            s += 60
        s += len(valores_set & esperados) * 100
        if valores_set:
            promedio = sum(len(v) for v in valores_set) / len(valores_set)
            if promedio < 4:
                s -= 50
            numericos = sum(v.replace(".", "", 1).isdigit() for v in valores_set)
            if numericos >= max(1, len(valores_set) * 0.6):
                s -= 200
        return s

    prop_estado = max(llaves, key=lambda k: score(k, estados_esperados, candidatos_estado), default=None)
    prop_mun = max(llaves, key=lambda k: score(k, municipios_esperados, candidatos_mun), default=None)

    return prop_estado, prop_mun


def sucursal_coincide_con_municipio(sucursal_norm: str, municipio_norm: str) -> bool:
    if not sucursal_norm or not municipio_norm:
        return False

    if sucursal_norm == municipio_norm:
        return True

    if sucursal_norm.startswith(municipio_norm + " "):
        return True

    if municipio_norm.startswith(sucursal_norm + " "):
        return True

    # Casos comunes: municipio JUAREZ y sucursal CD JUAREZ / CIUDAD JUAREZ.
    if municipio_norm == "JUAREZ" and "JUAREZ" in sucursal_norm:
        return True

    if municipio_norm == "MADERO" and "MADERO" in sucursal_norm:
        return True

    return False


def preparar_sucursales_para_mapa(df: pd.DataFrame) -> pd.DataFrame:
    df_suc = (
        df.dropna(subset=["Latitud", "Longitud"])
        .groupby(["Estado", "Subdirección", "Zona", "Sucursal", "Latitud", "Longitud"], as_index=False)
        .agg(
            Calidad_de_Cartera=("Calidad de Cartera", "mean"),
            Distribuidoras_Totales=("Distribuidoras Totales", "sum"),
            Distribuidoras_al_Corriente=("Distribuidoras al Corriente", "sum"),
            Distribuidoras_en_Mora=("Distribuidoras en Mora", "sum"),
            Var_Dist_Corriente=("Var Dist Corriente", "sum"),
            Var_Dist_en_Mora=("Var Dist en Mora", "sum"),
            Total_Dispersado=("Total Dispersado", "sum"),
            Canjes=("Canjes", "sum"),
            Canjes_Fecha_Corte=("Canjes Fecha Corte", "sum"),
            Total_Dispersado_Fecha_Corte=("Total Dispersado Fecha Corte", "sum"),
            Coordinaciones=("Coordinacion", "nunique"),
        )
    )

    df_suc = df_suc.rename(
        columns={
            "Calidad_de_Cartera": "Calidad de Cartera",
            "Distribuidoras_Totales": "Distribuidoras Totales",
            "Distribuidoras_al_Corriente": "Distribuidoras al Corriente",
            "Distribuidoras_en_Mora": "Distribuidoras en Mora",
            "Var_Dist_Corriente": "Var Dist Corriente",
            "Var_Dist_en_Mora": "Var Dist en Mora",
            "Total_Dispersado": "Total Dispersado",
            "Canjes_Fecha_Corte": "Canjes Fecha Corte",
            "Total_Dispersado_Fecha_Corte": "Total Dispersado Fecha Corte",
        }
    )

    df_suc = recalcular_canje_promedio(df_suc)
    df_suc["Estado Normalizado"] = df_suc["Estado"].map(normalizar_estado_datos)
    df_suc["Sucursal Normalizada Mapa"] = df_suc["Sucursal"].map(normalizar_sucursal).map(normalizar_municipio)
    df_suc = agregar_columnas_variacion(df_suc)
    return df_suc


def elegir_sucursal_para_municipio(
    g_estado: pd.DataFrame,
    municipio_norm: str,
    lat_mun: float | None,
    lon_mun: float | None,
) -> pd.Series | None:
    if g_estado.empty:
        return None

    exactas = g_estado[
        g_estado["Sucursal Normalizada Mapa"].apply(
            lambda x: sucursal_coincide_con_municipio(str(x), municipio_norm)
        )
    ].copy()

    if not exactas.empty:
        exactas = exactas.sort_values("Distribuidoras Totales", ascending=False)
        return exactas.iloc[0]

    if lat_mun is None or lon_mun is None:
        g_estado = g_estado.sort_values("Distribuidoras Totales", ascending=False)
        return g_estado.iloc[0]

    dist = (g_estado["Latitud"] - lat_mun) ** 2 + (g_estado["Longitud"] - lon_mun) ** 2
    return g_estado.loc[dist.idxmin()]




def reducir_coordenadas_geojson(obj, precision: int = 4, salto: int = 4):
    """
    Reduce el tamaño del GeoJSON enviado al navegador.

    Streamlit manda el mapa completo al browser. El GeoJSON municipal de México
    puede rebasar 200 MB ya convertido a mensaje interno de Plotly. Esta función
    conserva la división municipal, pero redondea coordenadas y elimina puntos
    intermedios para que el mapa cargue sin MessageSizeError.
    """
    if isinstance(obj, (int, float)):
        return round(float(obj), precision)

    if not isinstance(obj, list):
        return obj

    # Par [lon, lat]
    if len(obj) >= 2 and all(isinstance(x, (int, float)) for x in obj[:2]):
        return [round(float(obj[0]), precision), round(float(obj[1]), precision)]

    # Anillo de coordenadas: [[lon,lat], [lon,lat], ...]
    if obj and isinstance(obj[0], list) and len(obj[0]) >= 2 and all(isinstance(x, (int, float)) for x in obj[0][:2]):
        puntos = obj
        if salto and salto > 1 and len(puntos) > 12:
            reducidos = puntos[::salto]
            if puntos[-1] != reducidos[-1]:
                reducidos.append(puntos[-1])
            if reducidos[0] != reducidos[-1]:
                reducidos.append(reducidos[0])
            puntos = reducidos
        return [reducir_coordenadas_geojson(p, precision=precision, salto=1) for p in puntos]

    return [reducir_coordenadas_geojson(x, precision=precision, salto=salto) for x in obj]


def preparar_feature_ligera(feature: dict, feature_id: str, estado_norm: str, municipio_norm: str, precision: int = 4, salto: int = 4) -> dict:
    """Crea un feature mínimo para Plotly: sólo id, propiedades necesarias y geometría reducida."""
    geom = feature.get("geometry", {})
    geom_ligera = {
        "type": geom.get("type"),
        "coordinates": reducir_coordenadas_geojson(
            geom.get("coordinates", []),
            precision=precision,
            salto=salto,
        ),
    }
    return {
        "type": "Feature",
        "id": feature_id,
        "properties": {
            "__feature_id": feature_id,
            "__estado_norm": estado_norm,
            "__municipio_norm": municipio_norm,
        },
        "geometry": geom_ligera,
    }

def construir_municipios_coloreados_por_subdireccion(
    df: pd.DataFrame,
    estados_objetivo: list[str] | None = None,
    precision_geojson: int | None = None,
    salto_geojson: int | None = None,
) -> tuple[pd.DataFrame, dict]:
    """
    Devuelve un GeoJSON municipal y una tabla donde cada municipio se colorea
    por Subdirección. Si un estado tiene sucursales de distintas subdirecciones,
    sus municipios quedan en más de un color.
    """
    geo_mun = cargar_geojson_municipios_mexico()
    prop_estado, prop_mun_nombre = detectar_propiedad_municipio_estado(geo_mun)

    if not prop_estado or not prop_mun_nombre:
        raise ValueError(
            "No pude detectar las propiedades de estado y municipio en mexico_municipios.geojson."
        )

    df_suc = preparar_sucursales_para_mapa(df)
    if df_suc.empty:
        return pd.DataFrame(), {"type": "FeatureCollection", "features": []}

    # En mapa nacional reducimos más para no rebasar el límite interno de Streamlit.
    # En vista por estado se conserva más detalle porque son menos municipios.
    if precision_geojson is None:
        precision_geojson = 4 if not estados_objetivo else 5
    if salto_geojson is None:
        salto_geojson = 5 if not estados_objetivo else 2

    estados_datos = set(df_suc["Estado Normalizado"].dropna().unique().tolist())
    if estados_objetivo:
        estados_objetivo_norm = {normalizar_estado_datos(e) for e in estados_objetivo}
        estados_datos = estados_datos & estados_objetivo_norm

    features = []
    filas = []

    for idx, feature in enumerate(geo_mun.get("features", [])):
        props = feature.get("properties", {})
        estado_geo = props.get(prop_estado, "")
        estado_norm = normalizar_estado_geo(estado_geo)

        if estado_norm not in estados_datos:
            continue

        municipio_geo = props.get(prop_mun_nombre, "Municipio")
        municipio_norm = normalizar_municipio(municipio_geo)
        lat_mun, lon_mun = centroide_feature(feature)

        g_estado = df_suc[df_suc["Estado Normalizado"] == estado_norm].copy()
        suc = elegir_sucursal_para_municipio(g_estado, municipio_norm, lat_mun, lon_mun)
        if suc is None:
            continue

        feature_id = f"mun_{idx}"
        feature_ligera = preparar_feature_ligera(
            feature=feature,
            feature_id=feature_id,
            estado_norm=estado_norm,
            municipio_norm=municipio_norm,
            precision=precision_geojson,
            salto=salto_geojson,
        )
        features.append(feature_ligera)

        filas.append(
            {
                "__feature_id": feature_id,
                "Estado": suc["Estado"],
                "Municipio": str(municipio_geo),
                "Subdirección": suc["Subdirección"],
                "Zona": suc["Zona"],
                "Sucursal Asignada": suc["Sucursal"],
                "Calidad de Cartera": float(suc["Calidad de Cartera"]),
                "Distribuidoras Totales": float(suc["Distribuidoras Totales"]),
                "Distribuidoras al Corriente": float(suc["Distribuidoras al Corriente"]),
                "Distribuidoras en Mora": float(suc["Distribuidoras en Mora"]),
                "Coordinaciones": float(suc["Coordinaciones"]),
            }
        )

    geo_filtrado = {"type": "FeatureCollection", "features": features}
    df_mun = pd.DataFrame(filas)
    return df_mun, geo_filtrado


def aplicar_estilo_geografico(fig: go.Figure, altura: int = 720):
    fig.update_geos(
        fitbounds="locations",
        visible=True,
        showcountries=True,
        countrycolor=COLOR_LINEA_MAPA_55,
        showsubunits=True,
        subunitcolor=COLOR_LINEA_MAPA_35,
        showland=True,
        landcolor="rgba(245,247,252,1)",
        showocean=True,
        oceancolor="rgba(220,235,250,1)",
        coastlinecolor=COLOR_LINEA_MAPA_45,
        showframe=False,
        lataxis_showgrid=False,
        lonaxis_showgrid=False,
    )

    fig.update_layout(
        height=altura,
        margin=dict(t=70, l=10, r=10, b=10),
        paper_bgcolor="rgba(255,255,255,0)",
        plot_bgcolor="rgba(255,255,255,0)",
        legend_title_text="Subdirección",
        font=dict(size=14),
        geo=dict(bgcolor="rgba(255,255,255,0)"),
    )

def texto_guia_interaccion_mapa(tipo_mapa: str) -> str:
    """
    Devuelve el texto ejecutivo de ayuda del mapa.
    Se usa en un recuadro flotante externo a Plotly para que pueda cerrarse
    al dar clic fuera, sin depender de botones internos del gráfico.
    """
    if tipo_mapa == "Calor Canjes":
        lectura = "Estás viendo el mapa en modo <b>Calor Canjes</b>. En esta lectura, cada bolita se colorea según los canjes realizados exactamente en la fecha de corte."
        foco = "Los tonos de menor intensidad ayudan a detectar sucursales con baja actividad del día, mientras que los tonos más altos muestran dónde se concentró el mayor número de canjes."
    elif tipo_mapa == "Calor Dispersado":
        lectura = "Estás viendo el mapa en modo <b>Calor Dispersado</b>. En esta lectura, cada bolita se colorea según el importe dispersado exactamente en la fecha de corte."
        foco = "Los tonos de menor intensidad permiten ubicar territorios con baja dispersión diaria; los tonos más altos señalan las sucursales donde se concentró el mayor monto colocado."
    else:
        lectura = "Estás viendo el mapa en modo <b>Subdirección</b>. En esta lectura, el color no mide desempeño, sino estructura: cada bolita se pinta según la Subdirección a la que pertenece la sucursal."
        foco = "Esto sirve para leer rápidamente la cobertura territorial, identificar concentración operativa por estructura y ubicar qué subdirecciones tienen presencia en cada zona del mapa."

    return (
        "<b>Guía ejecutiva del mapa</b><br>"
        f"{lectura} "
        f"{foco}<br><br>"
        "<b>Botones de tipo de mapa:</b> usa <b>Subdirección</b> cuando quieras entender la distribución territorial de la estructura; "
        "usa <b>Calor Canjes</b> cuando quieras comparar la actividad del día por número de canjes; "
        "y usa <b>Calor Dispersado</b> cuando quieras comparar dónde se concentró el importe dispersado del corte. "
        "Los tres botones conservan las mismas sucursales y KPIs; lo que cambia es la forma de colorear el mapa para responder una pregunta distinta.<br><br>"
        "<b>Cómo leerlo:</b> coloca el cursor sobre una bolita para consultar el detalle de la sucursal: "
        "calidad de cartera, distribuidoras, canjes y dispersión. Así puedes interpretar cada punto sin perder la vista general del territorio.<br>"
        "<b>Cómo profundizar:</b> da clic sobre un estado o departamento para abrir su detalle territorial. "
        "Dentro del estado, el mapa cambia a una lectura local con la división municipal o departamental y las sucursales correspondientes.<br>"
        "<b>Top/Bottom:</b> cuando uses esos botones, el mapa se enfoca sólo en la selección activa para comparar con mayor claridad los mejores y peores desempeños."
    )


def renderizar_guia_interaccion_mapa(tipo_mapa: str):
    """
    Muestra un ícono de ayuda flotante sobre el mapa.
    Al hacer clic en el ícono se abre el recuadro; mientras está abierto,
    el ícono desaparece. Al hacer clic fuera del recuadro, se cierra solo.
    """
    texto_guia = texto_guia_interaccion_mapa(tipo_mapa)
    ayuda_id = "map_help_" + re.sub(r"[^a-zA-Z0-9_]", "_", limpiar_texto(tipo_mapa).lower())

    st.markdown(
        f"""
<style>
.map-help-layer {{
    position: relative;
    height: 0;
    z-index: 50;
}}

.map-help-checkbox {{
    display: none;
}}

.map-help-widget {{
    position: fixed;
    top: 86px;
    left: 18px;
    z-index: 9999;
    display: inline-block;
}}

.map-help-button {{
    width: 38px;
    height: 38px;
    border-radius: 8px;
    border: 1px solid {COLOR_LINEA_MAPA_65};
    background: rgba(255,255,255,0.96);
    color: {COLOR_TEXTO};
    font-size: 18px;
    font-weight: 900;
    cursor: pointer;
    box-shadow: 0 8px 18px rgba(12, 33, 74, 0.08);
    display: inline-flex;
    align-items: center;
    justify-content: center;
    user-select: none;
}}

.map-help-button:hover {{
    background: rgba(255,255,255,1);
    border-color: {COLOR_PRIMARIO};
}}

.map-help-backdrop {{
    display: none;
    position: fixed;
    inset: 0;
    z-index: 9990;
    cursor: default;
    background: rgba(255,255,255,0);
}}

.map-help-panel {{
    display: none;
    margin-top: 8px;
    width: min(1120px, calc(100vw - 100px));
    max-width: calc(100vw - 100px);
    background: rgba(255,255,255,0.97);
    border: 1px solid {COLOR_LINEA_MAPA_65};
    color: {COLOR_TEXTO};
    padding: 14px 16px;
    font-size: 14px;
    line-height: 1.45;
    box-shadow: 0 14px 32px rgba(12, 33, 74, 0.10);
    position: relative;
    z-index: 9999;
}}

#{ayuda_id}:checked ~ .map-help-widget .map-help-button {{
    display: none;
}}

#{ayuda_id}:checked ~ .map-help-widget .map-help-panel {{
    display: block;
}}

#{ayuda_id}:checked ~ .map-help-backdrop {{
    display: block;
}}
</style>
<div class="map-help-layer">
    <input class="map-help-checkbox" id="{ayuda_id}" type="checkbox">
    <label class="map-help-backdrop" for="{ayuda_id}" aria-label="Cerrar guía del mapa"></label>
    <div class="map-help-widget">
        <label class="map-help-button" for="{ayuda_id}" aria-label="Abrir guía del mapa">ⓘ</label>
        <div class="map-help-panel">{texto_guia}</div>
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

def calcular_resumen_nivel_tabla(
    df_resumen_base: pd.DataFrame,
    nivel_vista: str,
    variable_tamano: str,
) -> pd.DataFrame:
    """
    Calcula la misma tabla que se muestra abajo.
    Se usa también antes de pintar el mapa para saber qué Top/Bottom resaltar.
    """
    df_mapa = preparar_mapa_por_nivel(
        df=df_resumen_base,
        nivel_vista=nivel_vista,
        variable_tamano=variable_tamano,
    )

    if df_mapa.empty:
        return pd.DataFrame()

    resumen_nivel = (
        df_mapa.groupby([nivel_vista], as_index=False)
        .agg(
            Coordinaciones=("Coordinaciones", "sum"),
            Sucursales=("Sucursales", "sum"),
            Zonas=("Zonas", "sum"),
            Calidad_de_Cartera=("Calidad de Cartera", "mean"),
            Distribuidoras_Totales=("Distribuidoras Totales", "sum"),
            Distribuidoras_al_Corriente=("Distribuidoras al Corriente", "sum"),
            Distribuidoras_en_Mora=("Distribuidoras en Mora", "sum"),
            Var_Dist_Corriente=("Var Dist Corriente", "sum"),
            Var_Dist_en_Mora=("Var Dist en Mora", "sum"),
            Total_Dispersado=("Total Dispersado", "sum"),
            Canjes=("Canjes", "sum"),
            Canjes_Fecha_Corte=("Canjes Fecha Corte", "sum"),
            Total_Dispersado_Fecha_Corte=("Total Dispersado Fecha Corte", "sum"),
        )
    )

    resumen_nivel = resumen_nivel.rename(
        columns={
            "Calidad_de_Cartera": "Calidad de Cartera",
            "Distribuidoras_Totales": "Distribuidoras Totales",
            "Distribuidoras_al_Corriente": "Distribuidoras al Corriente",
            "Distribuidoras_en_Mora": "Distribuidoras en Mora",
            "Var_Dist_Corriente": "Var Dist Corriente",
            "Var_Dist_en_Mora": "Var Dist en Mora",
            "Total_Dispersado": "Total Dispersado",
            "Canjes_Fecha_Corte": "Canjes Fecha Corte",
            "Total_Dispersado_Fecha_Corte": "Total Dispersado Fecha Corte",
        }
    )
    resumen_nivel = agregar_columnas_variacion(resumen_nivel)
    resumen_nivel = recalcular_canje_promedio(resumen_nivel)
    return resumen_nivel


def calcular_destacados_mapa(
    df_resumen_base: pd.DataFrame,
    nivel_vista: str,
    variable_tamano: str,
    modo_tabla: str,
    texto_busqueda: str,
) -> list[str]:
    """Devuelve los valores del Top/Bottom que deben resaltarse en el mapa."""
    if modo_tabla not in ["Top 10", "Bottom 10"]:
        return []

    resumen_nivel = calcular_resumen_nivel_tabla(
        df_resumen_base=df_resumen_base,
        nivel_vista=nivel_vista,
        variable_tamano=variable_tamano,
    )

    if resumen_nivel.empty or nivel_vista not in resumen_nivel.columns:
        return []

    if texto_busqueda.strip():
        busqueda_norm = limpiar_texto(texto_busqueda)
        resumen_nivel = resumen_nivel[
            resumen_nivel[nivel_vista].astype(str).map(limpiar_texto).str.contains(
                busqueda_norm,
                na=False,
                regex=False,
            )
        ].copy()

    resumen_nivel = aplicar_filtro_tabla(
        df=resumen_nivel,
        modo=modo_tabla,
        variable_tamano=variable_tamano,
    )

    return resumen_nivel[nivel_vista].astype(str).map(limpiar_texto).dropna().unique().tolist()

# ======================================================
# MAPA CON DIVISIÓN POLÍTICA + BURBUJAS POR SUBDIRECCIÓN
# ======================================================
def agregar_burbujas_sucursales(
    fig: go.Figure,
    df_suc: pd.DataFrame,
    variable_tamano: str,
    sufijo_nombre: str = "sucursales",
    destacar_nivel: str | None = None,
    destacar_valores: list[str] | None = None,
    tipo_mapa: str = "Subdirección",
):
    """
    Agrega las sucursales como bolitas.
    - Subdirección: color por Subdirección.
    - Calor Canjes: color rojo→verde por Canjes de la fecha de corte.
    - Calor Dispersado: color rojo→verde por Total Dispersado de la fecha de corte.
    """
    if df_suc.empty:
        return

    destacar_valores_norm = set(destacar_valores or [])

    # Cuando se elige Top 10 o Bottom 10, conserva sólo las bolitas
    # que pertenecen a la selección y oculta las demás.
    if destacar_nivel and destacar_valores_norm and destacar_nivel in df_suc.columns:
        df_plot = df_suc[
            df_suc[destacar_nivel].astype(str).map(limpiar_texto).isin(destacar_valores_norm)
        ].copy()
    else:
        df_plot = df_suc.copy()

    if df_plot.empty:
        return

    max_global = pd.to_numeric(df_suc[variable_tamano], errors="coerce").fillna(0).max()
    sizeref = max(max_global, 1) / 55

    for col in ["Total Dispersado", "Canjes", "Canje Promedio Acumulado", "Canjes Fecha Corte", "Total Dispersado Fecha Corte"]:
        if col not in df_plot.columns:
            df_plot[col] = 0
        df_plot[col] = pd.to_numeric(df_plot[col], errors="coerce").fillna(0)

    custom_cols = [
        "Estado",
        "Subdirección",
        "Zona",
        "Calidad de Cartera",
        "Distribuidoras Totales",
        "Distribuidoras al Corriente",
        "Distribuidoras en Mora",
        "Var Dist Corriente",
        "Var Dist en Mora",
        "Semaforo Variacion",
        "Coordinaciones",
        "Total Dispersado",
        "Canjes",
        "Canje Promedio Acumulado",
        "Canjes Fecha Corte",
        "Total Dispersado Fecha Corte",
    ]

    for col in custom_cols:
        if col not in df_plot.columns:
            df_plot[col] = 0 if col not in ["Estado", "Subdirección", "Zona", "Semaforo Variacion"] else ""

    hover = (
        "<b>%{text}</b><br>"
        "Estado/Departamento: %{customdata[0]}<br>"
        "Subdirección: %{customdata[1]}<br>"
        "Zona: %{customdata[2]}<br><br>"
        "Calidad de Cartera: %{customdata[3]:,.2f}%<br>"
        "Distribuidoras Totales: %{customdata[4]:,.0f}<br>"
        "Distribuidoras al Corriente: %{customdata[5]:,.0f}<br>"
        "Distribuidoras en Mora: %{customdata[6]:,.0f}<br>"
        "Var Corriente: %{customdata[7]:,.0f}<br>"
        "Var Mora: %{customdata[8]:,.0f}<br>"
        "Resultado: %{customdata[9]}<br>"
        "Coordinaciones: %{customdata[10]:,.0f}<br><br>"
        "<b>Dispersión acumulada</b><br>"
        "Total Dispersado: $%{customdata[11]:,.0f}<br>"
        "Canjes: %{customdata[12]:,.0f}<br>"
        "Canje Promedio Acum.: $%{customdata[13]:,.0f}<br>"
        "Canjes fecha corte: %{customdata[14]:,.0f}"
        "<extra></extra>"
    )

    if tipo_mapa in ["Calor Canjes", "Calor Dispersado"]:
        heat_col = "Canjes Fecha Corte" if tipo_mapa == "Calor Canjes" else "Total Dispersado Fecha Corte"
        titulo_color = "Canjes fecha corte" if tipo_mapa == "Calor Canjes" else "Dispersado fecha corte"

        fig.add_trace(
            go.Scattergeo(
                lat=df_plot["Latitud"],
                lon=df_plot["Longitud"],
                mode="markers",
                marker=dict(
                    size=pd.to_numeric(df_plot[variable_tamano], errors="coerce").fillna(0),
                    sizemode="area",
                    sizeref=sizeref,
                    sizemin=8,
                    color=pd.to_numeric(df_plot[heat_col], errors="coerce").fillna(0),
                    colorscale=[
                        [0.0, "#D73027"],
                        [0.5, "#FEE08B"],
                        [1.0, "#1A9850"],
                    ],
                    showscale=True,
                    colorbar=dict(title=titulo_color),
                    line=dict(width=1.1, color=COLOR_LINEA_MAPA_65),
                    opacity=0.92,
                ),
                name=f"Mapa de calor - {titulo_color}",
                text=df_plot["Sucursal"],
                customdata=df_plot[custom_cols],
                hovertemplate=hover,
            )
        )
        return

    colores = px.colors.qualitative.Set2 + px.colors.qualitative.Pastel + px.colors.qualitative.Dark24
    subdirs = sorted(df_plot["Subdirección"].dropna().unique().tolist())
    mapa_color = {s: colores[i % len(colores)] for i, s in enumerate(subdirs)}

    for subdir in subdirs:
        g = df_plot[df_plot["Subdirección"] == subdir].copy()
        if g.empty:
            continue

        fig.add_trace(
            go.Scattergeo(
                lat=g["Latitud"],
                lon=g["Longitud"],
                mode="markers",
                marker=dict(
                    size=pd.to_numeric(g[variable_tamano], errors="coerce").fillna(0),
                    sizemode="area",
                    sizeref=sizeref,
                    sizemin=8,
                    color=mapa_color[subdir],
                    line=dict(width=1.1, color=COLOR_LINEA_MAPA_65),
                    opacity=0.90,
                ),
                name=f"{subdir} - {sufijo_nombre}",
                text=g["Sucursal"],
                customdata=g[custom_cols],
                hovertemplate=hover,
            )
        )


def agregar_poligonos_neutros_estado_departamento(
    fig: go.Figure,
    resumen_estado: pd.DataFrame,
    geojson: dict,
    prop_estado: str,
    nombre_traza: str,
):
    """
    Pinta la división política con un color neutro. El mapa ya no se colorea
    por Subdirección; la Subdirección vive en las bolitas de sucursal.
    """
    fig.add_trace(
        go.Choropleth(
            geojson=geojson,
            locations=resumen_estado["Estado Geo"],
            z=[1] * len(resumen_estado),
            featureidkey=f"properties.{prop_estado}",
            colorscale=[[0, "rgba(235,241,252,0.92)"], [1, "rgba(235,241,252,0.92)"]],
            showscale=False,
            marker_line_color=COLOR_LINEA_MAPA_65,
            marker_line_width=0.75,
            name=nombre_traza,
            text=resumen_estado["Estado"],
            customdata=resumen_estado[
                [
                    "Estado",
                    "Subdirección Principal",
                    "Calidad de Cartera",
                    "Distribuidoras Totales",
                    "Distribuidoras al Corriente",
                    "Resumen Sucursales",
                ]
            ],
            # El polígono del estado/departamento se mantiene seleccionable,
            # pero no muestra recuadro emergente al pasar el cursor.
            # Usamos "none" en lugar de "skip" porque "skip" también bloquea
            # eventos de selección/clic en Plotly.
            # El tooltip ejecutivo queda únicamente en las bolitas de sucursal.
            hoverinfo="none",
            hovertemplate=None,
        )
    )


def construir_mapa_estados_mexico(
    df: pd.DataFrame,
    nombre_valera: str,
    variable_tamano: str,
    fecha_texto: str,
    destacar_nivel: str | None = None,
    destacar_valores: list[str] | None = None,
    tipo_mapa: str = "Subdirección",
):
    try:
        geojson = cargar_geojson_mexico()
        geojson, prop_estado, mapa_geo = preparar_geojson_y_mapeo(geojson)
    except Exception as e:
        st.error(str(e))
        return

    resumen_estado = preparar_resumen_estado(
        df=df,
        geojson=geojson,
        prop_estado=prop_estado,
        mapa_geo=mapa_geo,
    )

    df_suc = preparar_sucursales_para_mapa(df)

    if resumen_estado.empty:
        st.warning("No hay estados con datos para pintar en el mapa.")
        return

    fig = go.Figure()

    agregar_poligonos_neutros_estado_departamento(
        fig=fig,
        resumen_estado=resumen_estado,
        geojson=geojson,
        prop_estado=prop_estado,
        nombre_traza="División política estatal",
    )

    agregar_burbujas_sucursales(
        fig=fig,
        df_suc=df_suc,
        variable_tamano=variable_tamano,
        sufijo_nombre="sucursales",
        destacar_nivel=destacar_nivel,
        destacar_valores=destacar_valores,
        tipo_mapa=tipo_mapa,
    )

    aplicar_estilo_geografico(fig, altura=720)
    fig.update_layout(
        title=f"Mapa político de México con sucursales por Subdirección - {nombre_valera} - {fecha_texto}",
    )
    renderizar_guia_interaccion_mapa(tipo_mapa)

    evento = None

    try:
        evento = st.plotly_chart(
            fig,
            use_container_width=True,
            on_select="rerun",
            selection_mode="points",
        )
    except TypeError:
        st.plotly_chart(fig, use_container_width=True)

    if evento:
        try:
            puntos = evento["selection"]["points"]
        except Exception:
            puntos = []

        if puntos:
            punto = puntos[0]
            estado_real = None

            # Si el clic fue en un polígono de estado.
            estado_geo = punto.get("location")
            if estado_geo:
                serie_estado = resumen_estado.loc[
                    resumen_estado["Estado Geo"] == estado_geo,
                    "Estado",
                ]
                if not serie_estado.empty:
                    estado_real = serie_estado.iloc[0]

            # Si el clic fue en una bolita de sucursal.
            if estado_real is None:
                customdata = punto.get("customdata")
                if customdata and len(customdata) > 0:
                    estado_real = customdata[0]

            if estado_real:
                st.session_state["ia_mapa_ultimo_click"] = estado_real
                set_query_params(
                    valera=get_query_param("valera", ""),
                    estado=estado_real,
                )
                st.rerun()


def construir_mapa_estados_peru(
    df: pd.DataFrame,
    nombre_valera: str,
    variable_tamano: str,
    fecha_texto: str,
    destacar_nivel: str | None = None,
    destacar_valores: list[str] | None = None,
    tipo_mapa: str = "Subdirección",
):
    try:
        geojson = cargar_geojson_peru()
        geojson, prop_estado, mapa_geo = preparar_geojson_region_norm(geojson, "PERÚ")
    except Exception as e:
        st.error(str(e))
        return

    resumen_estado = preparar_resumen_estado(
        df=df,
        geojson=geojson,
        prop_estado=prop_estado,
        mapa_geo=mapa_geo,
    )

    df_suc = preparar_sucursales_para_mapa(df)

    if resumen_estado.empty:
        st.warning("No hay departamentos con datos para pintar en el mapa de Perú.")
        return

    fig = go.Figure()

    agregar_poligonos_neutros_estado_departamento(
        fig=fig,
        resumen_estado=resumen_estado,
        geojson=geojson,
        prop_estado=prop_estado,
        nombre_traza="División política departamental",
    )

    agregar_burbujas_sucursales(
        fig=fig,
        df_suc=df_suc,
        variable_tamano=variable_tamano,
        sufijo_nombre="sucursales",
        destacar_nivel=destacar_nivel,
        destacar_valores=destacar_valores,
        tipo_mapa=tipo_mapa,
    )

    aplicar_estilo_geografico(fig, altura=720)
    fig.update_layout(
        title=f"Mapa político de Perú con sucursales por Subdirección - {nombre_valera} - {fecha_texto}",
    )
    renderizar_guia_interaccion_mapa(tipo_mapa)

    evento = None

    try:
        evento = st.plotly_chart(
            fig,
            use_container_width=True,
            on_select="rerun",
            selection_mode="points",
        )
    except TypeError:
        st.plotly_chart(fig, use_container_width=True)

    if evento:
        try:
            puntos = evento["selection"]["points"]
        except Exception:
            puntos = []

        if puntos:
            punto = puntos[0]
            estado_real = None

            estado_geo = punto.get("location")
            if estado_geo:
                serie_estado = resumen_estado.loc[
                    resumen_estado["Estado Geo"] == estado_geo,
                    "Estado",
                ]
                if not serie_estado.empty:
                    estado_real = serie_estado.iloc[0]

            if estado_real is None:
                customdata = punto.get("customdata")
                if customdata and len(customdata) > 0:
                    estado_real = customdata[0]

            if estado_real:
                st.session_state["ia_mapa_ultimo_click"] = estado_real
                set_query_params(
                    valera=get_query_param("valera", ""),
                    estado=estado_real,
                )
                st.rerun()


# ======================================================
# MAPA ESTADO CON DIVISIÓN MUNICIPAL NEUTRA + BURBUJAS
# ======================================================
def preparar_geojson_municipios_neutro_por_estado(estado: str) -> tuple[pd.DataFrame, dict, str] | tuple[pd.DataFrame, None, None]:
    """
    Devuelve sólo los municipios del estado seleccionado. Se conserva la geometría
    original del archivo para que la división municipal se vea lo más exacta posible,
    pero se eliminan propiedades innecesarias para evitar mensajes pesados.
    """
    try:
        geo_mun = cargar_geojson_municipios_mexico()
    except Exception:
        return pd.DataFrame(), None, None

    prop_estado, prop_mun = detectar_propiedad_municipio_estado(geo_mun)
    if not prop_estado:
        return pd.DataFrame(), None, None

    estado_norm = normalizar_estado_datos(estado)
    features = []
    filas = []

    for idx, feature in enumerate(geo_mun.get("features", [])):
        props = feature.get("properties", {})
        nombre_estado = props.get(prop_estado, "")

        if normalizar_estado_geo(nombre_estado) != estado_norm:
            continue

        nombre_mun = props.get(prop_mun, "Municipio") if prop_mun else "Municipio"
        feature_id = f"mun_{idx}"

        features.append(
            {
                "type": "Feature",
                "id": feature_id,
                "properties": {
                    "__feature_id": feature_id,
                    "municipio": str(nombre_mun),
                },
                "geometry": feature.get("geometry"),
            }
        )
        filas.append(
            {
                "__feature_id": feature_id,
                "Municipio": str(nombre_mun),
            }
        )

    if not features:
        return pd.DataFrame(), None, None

    return pd.DataFrame(filas), {"type": "FeatureCollection", "features": features}, "id"


def construir_mapa_estado_burbujas(
    df: pd.DataFrame,
    nombre_valera: str,
    estado: str,
    variable_tamano: str,
    fecha_texto: str,
    pais: str = "MÉXICO",
    destacar_nivel: str | None = None,
    destacar_valores: list[str] | None = None,
    tipo_mapa: str = "Subdirección",
):
    df_estado = df[df["Estado"].apply(limpiar_texto) == limpiar_texto(estado)].copy()

    if df_estado.empty:
        st.warning(f"No hay datos para {estado}.")
        return

    df_suc = preparar_sucursales_para_mapa(df_estado)

    if df_suc.empty:
        st.warning("No hay sucursales con coordenadas para este estado/departamento.")
        return

    fig = go.Figure()
    titulo_division = "División política"

    if limpiar_texto(pais) == limpiar_texto("MÉXICO"):
        df_mun, geo_mun, featureidkey = preparar_geojson_municipios_neutro_por_estado(estado)

        if geo_mun and not df_mun.empty:
            fig.add_trace(
                go.Choropleth(
                    geojson=geo_mun,
                    locations=df_mun["__feature_id"],
                    z=[1] * len(df_mun),
                    featureidkey=featureidkey,
                    colorscale=[[0, "rgba(235,241,252,0.88)"], [1, "rgba(235,241,252,0.88)"]],
                    showscale=False,
                    marker_line_color=COLOR_LINEA_MAPA_48,
                    marker_line_width=0.45,
                    name="División municipal",
                    text=df_mun["Municipio"],
                    hovertemplate="<b>%{text}</b><br>Municipio<extra></extra>",
                )
            )
            titulo_division = "División municipal"
        else:
            try:
                geojson = cargar_geojson_mexico()
                geojson, prop_estado, mapa_geo = preparar_geojson_y_mapeo(geojson)
                estado_norm = normalizar_estado_datos(estado)
                estado_geo = mapa_geo.get(estado_norm)
                if estado_geo:
                    geo_estado = filtrar_geojson_estado(geojson, prop_estado, estado_geo)
                    fig.add_trace(
                        go.Choropleth(
                            geojson=geo_estado,
                            locations=[estado_geo],
                            z=[1],
                            featureidkey=f"properties.{prop_estado}",
                            colorscale=[[0, "rgba(235,241,252,0.92)"], [1, "rgba(235,241,252,0.92)"]],
                            showscale=False,
                            marker_line_color=COLOR_LINEA_MAPA_65,
                            marker_line_width=1,
                            hoverinfo="skip",
                            name=estado,
                        )
                    )
                titulo_division = "Contorno estatal"
            except Exception:
                pass
    else:
        try:
            geojson = cargar_geojson_por_pais(pais)
            geojson, prop_estado, mapa_geo = preparar_geojson_region_norm(geojson, "PERÚ")
            estado_norm = normalizar_estado_datos(estado)
            estado_geo = mapa_geo.get(estado_norm)
            if estado_geo:
                geo_estado = filtrar_geojson_estado(geojson, prop_estado, estado_geo)
                fig.add_trace(
                    go.Choropleth(
                        geojson=geo_estado,
                        locations=[estado_geo],
                        z=[1],
                        featureidkey=f"properties.{prop_estado}",
                        colorscale=[[0, "rgba(235,241,252,0.92)"], [1, "rgba(235,241,252,0.92)"]],
                        showscale=False,
                        marker_line_color=COLOR_LINEA_MAPA_65,
                        marker_line_width=1,
                        hoverinfo="skip",
                        name=estado,
                    )
                )
            titulo_division = "Departamento"
        except Exception as e:
            st.error(str(e))
            return

    agregar_burbujas_sucursales(
        fig=fig,
        df_suc=df_suc,
        variable_tamano=variable_tamano,
        sufijo_nombre="sucursales",
        destacar_nivel=destacar_nivel,
        destacar_valores=destacar_valores,
        tipo_mapa=tipo_mapa,
    )

    aplicar_estilo_geografico(fig, altura=720)

    fig.update_layout(
        title=f"{estado} - {titulo_division} con sucursales por Subdirección - {nombre_valera} - {fecha_texto}",
    )
    renderizar_guia_interaccion_mapa(tipo_mapa)

    st.plotly_chart(fig, use_container_width=True)


def texto_guia_interaccion_mapa_financiero() -> str:
    return (
        "<b>Guía ejecutiva del mapa financiero</b><br>"
        "Estás viendo el detalle por estado en modo <b>Plazo y composición</b>. "
        "Esta vista ya no usa bolitas: usa un <b>treemap jerárquico</b>, como el mapa de estructura, "
        "para leer la composición financiera dentro del estado seleccionado.<br><br>"
        "<b>Jerarquía:</b> Estado → Subdirección → Zona → Sucursal. "
        "Cada bloque se agrupa dentro de su estructura operativa, permitiendo identificar rápidamente "
        "dónde se concentra el capital, qué zonas pesan más y qué sucursales aportan más volumen.<br><br>"
        "<b>Tamaño del bloque:</b> representa el <b>capital</b>. Un bloque más grande significa mayor concentración "
        "de capital en esa parte de la estructura.<br><br>"
        "<b>Color del bloque:</b> representa la <b>tasa de ganancia</b>. Los tonos bajos señalan menor rentabilidad relativa; "
        "los tonos altos señalan mayor rentabilidad relativa. Así puedes detectar estructuras grandes con baja rentabilidad "
        "o estructuras pequeñas con buen desempeño.<br><br>"
        "<b>Plazo:</b> arriba del treemap puedes tocar la tarjeta Plazo para cambiar la lectura. "
        "Al elegir un plazo, el treemap y los KPIs se recalculan únicamente con ese plazo seleccionado. También puedes tocar la tarjeta Corte para cambiar entre cortes disponibles. "
        "El plazo se muestra como <b>plazo ponderado por capital</b>, por lo que refleja mejor la exposición real del dinero "
        "que un promedio simple. Una sucursal con plazo alto recupera capital más lento; si además tiene baja tasa de ganancia, "
        "conviene revisarla con prioridad.<br><br>"
        "<b>Switch de detalle:</b> usa <b>Estructura</b> para mantener el mapa territorial original con división municipal y sucursales; "
        "usa <b>Plazo y composición</b> para cambiar a esta lectura financiera por capital, interés, ganancia, tasa y plazo, "
        "sin modificar la selección del estado ni las tablas inferiores. Al dar clic en un bloque del treemap, las tarjetas se recalculan para ese estado, subdirección, zona o sucursal seleccionada. El cuadro emergente del cursor queda desactivado para que la interacción principal sea el clic sobre el bloque.<br><br><b>Corte:</b> esta vista toma el último dato real de la columna <b>Corte</b> del archivo Plazo y composición; no usa la fecha de corte de las demás visualizaciones.<br><br><b>Cálculo de tarjetas:</b> Capital, Interés, Total, Ganancia y Vales son sumas del corte y plazo seleccionados. La Tasa de ganancia se recalcula como <b>Interés / Capital</b>. Monto Vale se calcula como <b>Capital / Vales</b>, es decir, el ticket promedio colocado por vale dentro del plazo seleccionado."
    )


def renderizar_guia_interaccion_mapa_financiero():
    texto_guia = texto_guia_interaccion_mapa_financiero()
    ayuda_id = "map_help_plazo_composicion"

    st.markdown(
        f"""
<style>
.map-help-layer {{
    position: relative;
    height: 0;
    z-index: 50;
}}

.map-help-checkbox {{
    display: none;
}}

.map-help-widget {{
    position: fixed;
    top: 86px;
    left: 18px;
    z-index: 9999;
    display: inline-block;
}}

.map-help-button {{
    width: 38px;
    height: 38px;
    border-radius: 8px;
    border: 1px solid {COLOR_LINEA_MAPA_65};
    background: rgba(255,255,255,0.96);
    color: {COLOR_TEXTO};
    font-size: 18px;
    font-weight: 900;
    cursor: pointer;
    box-shadow: 0 8px 18px rgba(12, 33, 74, 0.08);
    display: inline-flex;
    align-items: center;
    justify-content: center;
    user-select: none;
}}

.map-help-button:hover {{
    background: rgba(255,255,255,1);
    border-color: {COLOR_PRIMARIO};
}}

.map-help-backdrop {{
    display: none;
    position: fixed;
    inset: 0;
    z-index: 9990;
    cursor: default;
    background: rgba(255,255,255,0);
}}

.map-help-panel {{
    display: none;
    margin-top: 8px;
    width: min(1120px, calc(100vw - 100px));
    max-width: calc(100vw - 100px);
    background: rgba(255,255,255,0.97);
    border: 1px solid {COLOR_LINEA_MAPA_65};
    color: {COLOR_TEXTO};
    padding: 14px 16px;
    font-size: 14px;
    line-height: 1.45;
    box-shadow: 0 14px 32px rgba(12, 33, 74, 0.10);
    position: relative;
    z-index: 9999;
}}

#{ayuda_id}:checked ~ .map-help-widget .map-help-button {{
    display: none;
}}

#{ayuda_id}:checked ~ .map-help-widget .map-help-panel {{
    display: block;
}}

#{ayuda_id}:checked ~ .map-help-backdrop {{
    display: block;
}}
</style>
<div class="map-help-layer">
    <input class="map-help-checkbox" id="{ayuda_id}" type="checkbox">
    <label class="map-help-backdrop" for="{ayuda_id}" aria-label="Cerrar guía del mapa"></label>
    <div class="map-help-widget">
        <label class="map-help-button" for="{ayuda_id}" aria-label="Abrir guía del mapa">ⓘ</label>
        <div class="map-help-panel">{texto_guia}</div>
    </div>
</div>
""",
        unsafe_allow_html=True,
    )



def formatear_plazo_opcion(valor) -> str:
    if valor == "Todos":
        return "Todos los plazos"

    numero = pd.to_numeric(valor, errors="coerce")
    if pd.isna(numero):
        return str(valor)

    numero = float(numero)
    if abs(numero - round(numero)) < 0.00001:
        return f"{int(round(numero))} semanas"

    return f"{numero:,.1f} semanas"

def plazo_display_desde_valores(valores) -> str:
    serie = pd.to_numeric(pd.Series(valores), errors="coerce").dropna()

    if serie.empty:
        return ""

    unicos = sorted(serie.unique().tolist())

    if len(unicos) == 1:
        valor = float(unicos[0])
        if abs(valor - round(valor)) < 0.00001:
            return f"{int(round(valor))} sem"
        return f"{valor:,.1f} sem"

    return "Varios"


def calcular_metricas_plazo(df_suc: pd.DataFrame) -> dict:
    df_tmp = df_suc.copy()

    for col in ["Capital", "Interes", "Total", "Ganancia", "Tasa de Ganancia", "Plazo", "Vales"]:
        if col not in df_tmp.columns:
            df_tmp[col] = 0
        df_tmp[col] = pd.to_numeric(df_tmp[col], errors="coerce").fillna(0)

    capital = float(df_tmp["Capital"].sum())
    interes = float(df_tmp["Interes"].sum())
    total = float(df_tmp["Total"].sum())
    ganancia = float(df_tmp["Ganancia"].sum())
    vales = float(df_tmp["Vales"].sum())

    if ganancia == 0 and total > 0 and capital > 0:
        ganancia = total - capital

    tasa = (interes / capital * 100) if capital else 0

    # Monto Vale = Capital / Vales.
    monto_vale = (capital / vales) if vales else 0

    # El plazo NO se promedia. Se muestra exactamente el plazo que trae el archivo.
    # Si la vista está en "Todos los plazos" y hay más de uno, se muestra "Varios".
    plazo_texto = plazo_display_desde_valores(df_tmp["Plazo"])

    corte = ""
    if "Corte Texto" in df_tmp.columns:
        corte = next((c for c in df_tmp["Corte Texto"].dropna().astype(str).unique().tolist() if c), "")

    if not corte and "Corte" in df_tmp.columns:
        corte = next((formatear_corte_plazo(c) for c in df_tmp["Corte"].dropna().astype(str).unique().tolist() if str(c).strip()), "")

    if not corte:
        corte = obtener_corte_visible_plazo()

    return {
        "Capital": capital,
        "Interes": interes,
        "Total": total,
        "Ganancia": ganancia,
        "Tasa de Ganancia": tasa,
        "Plazo": plazo_texto,
        "Vales": vales,
        "Monto Vale": monto_vale,
        "Corte": corte,
    }

def renderizar_tarjeta_kpi_plazo(titulo: str, valor: str):
    st.markdown(
        f"""
<div class="kpi-plazo-card">
    <div class="kpi-plazo-label">{titulo}</div>
    <div class="kpi-plazo-value">{valor}</div>
</div>
""",
        unsafe_allow_html=True,
    )



def filtrar_df_por_nodo_treemap(df: pd.DataFrame, node_id: str | None) -> pd.DataFrame:
    """
    Filtra la base financiera según el bloque seleccionado en el treemap.
    Los ids se construyen como:
    - estado::<estado>
    - sub::<subdirección>
    - zona::<subdirección>::<zona>
    - suc::<subdirección>::<zona>::<sucursal>
    """
    if not node_id:
        return df.copy()

    partes = str(node_id).split("::")
    if not partes:
        return df.copy()

    tipo = partes[0]
    filtrado = df.copy()

    if tipo == "estado":
        return filtrado

    if tipo == "sub" and len(partes) >= 2 and "Subdirección" in filtrado.columns:
        return filtrado[filtrado["Subdirección"].astype(str) == partes[1]].copy()

    if tipo == "zona" and len(partes) >= 3:
        if "Subdirección" in filtrado.columns:
            filtrado = filtrado[filtrado["Subdirección"].astype(str) == partes[1]].copy()
        if "Zona" in filtrado.columns:
            filtrado = filtrado[filtrado["Zona"].astype(str) == partes[2]].copy()
        return filtrado

    if tipo == "suc" and len(partes) >= 4:
        if "Subdirección" in filtrado.columns:
            filtrado = filtrado[filtrado["Subdirección"].astype(str) == partes[1]].copy()
        if "Zona" in filtrado.columns:
            filtrado = filtrado[filtrado["Zona"].astype(str) == partes[2]].copy()
        if "Sucursal" in filtrado.columns:
            filtrado = filtrado[filtrado["Sucursal"].astype(str) == partes[3]].copy()
        return filtrado

    return df.copy()


def etiqueta_nodo_treemap(node_id: str | None) -> str:
    if not node_id:
        return "Total visible"

    partes = str(node_id).split("::")
    if not partes:
        return "Total visible"

    tipo = partes[0]

    if tipo == "estado" and len(partes) >= 2:
        return partes[1]
    if tipo == "sub" and len(partes) >= 2:
        return f"Subdirección: {partes[1]}"
    if tipo == "zona" and len(partes) >= 3:
        return f"Zona: {partes[2]}"
    if tipo == "suc" and len(partes) >= 4:
        return f"Sucursal: {partes[3]}"

    return "Total visible"


def extraer_node_id_evento_plotly(evento) -> str | None:
    """
    Extrae el id del bloque seleccionado desde la respuesta de st.plotly_chart.
    Funciona con el dict de selección de Streamlit y tolera variaciones de estructura.
    """
    if not evento:
        return None

    try:
        seleccion = evento.get("selection", {}) if isinstance(evento, dict) else getattr(evento, "selection", {})
        puntos = seleccion.get("points", []) if isinstance(seleccion, dict) else getattr(seleccion, "points", [])
    except Exception:
        return None

    if not puntos:
        return None

    punto = puntos[0]

    if isinstance(punto, dict):
        for llave in ["id", "point_id", "pointId"]:
            valor = punto.get(llave)
            if valor:
                return str(valor)

        customdata = punto.get("customdata")
        if isinstance(customdata, (list, tuple)) and len(customdata) >= 9:
            return str(customdata[8])

    for llave in ["id", "point_id", "pointId"]:
        valor = getattr(punto, llave, None)
        if valor:
            return str(valor)

    return None


def renderizar_selector_plazo_y_kpis(
    df_suc: pd.DataFrame,
    estado: str,
    selected_node_id: str | None = None,
) -> tuple[pd.DataFrame, str, dict]:
    df_base = df_suc.copy()

    if "Plazo" not in df_base.columns:
        df_base["Plazo"] = 0
    if "Capital" not in df_base.columns:
        df_base["Capital"] = 0
    if "Corte" not in df_base.columns:
        df_base["Corte"] = ""
    if "Corte Texto" not in df_base.columns:
        df_base["Corte Texto"] = df_base["Corte"].map(formatear_corte_plazo)

    df_base["Plazo"] = pd.to_numeric(df_base["Plazo"], errors="coerce").fillna(0)
    df_base["Capital"] = pd.to_numeric(df_base["Capital"], errors="coerce").fillna(0)
    df_base["Corte"] = df_base["Corte"].fillna("").astype(str).map(lambda x: arreglar_mojibake(x).strip())
    df_base["Corte Texto"] = df_base["Corte Texto"].fillna("").astype(str).map(lambda x: arreglar_mojibake(x).strip())
    df_base.loc[df_base["Corte Texto"] == "", "Corte Texto"] = df_base.loc[df_base["Corte Texto"] == "", "Corte"].map(formatear_corte_plazo)
    df_base["__Corte Fecha Orden"] = df_base["Corte Texto"].map(extraer_fecha_corte)

    cortes_df = (
        df_base[df_base["Capital"] > 0][["Corte Texto", "__Corte Fecha Orden"]]
        .dropna(subset=["Corte Texto"])
        .drop_duplicates()
        .copy()
    )
    cortes_df = cortes_df[cortes_df["Corte Texto"].astype(str).str.strip() != ""]
    if cortes_df.empty:
        cortes_opciones = ["Sin corte"]
    else:
        cortes_df["__orden"] = cortes_df["__Corte Fecha Orden"].fillna(pd.Timestamp.min)
        cortes_df = cortes_df.sort_values("__orden", ascending=False)
        cortes_opciones = cortes_df["Corte Texto"].astype(str).tolist()

    estado_norm = limpiar_texto(estado)
    key_corte = f"selector_corte_plazo_composicion_{estado_norm}"
    key_plazo = f"selector_plazo_composicion_{estado_norm}"

    if key_corte not in st.session_state or st.session_state[key_corte] not in cortes_opciones:
        st.session_state[key_corte] = cortes_opciones[0]

    corte_sel = st.session_state[key_corte]
    if corte_sel == "Sin corte":
        df_corte = df_base.copy()
    else:
        df_corte = df_base[df_base["Corte Texto"] == corte_sel].copy()

    plazos = (
        df_corte.loc[df_corte["Capital"] > 0, "Plazo"]
        .dropna()
        .sort_values()
        .unique()
        .tolist()
    )
    opciones = ["Todos"] + plazos

    if key_plazo not in st.session_state or st.session_state[key_plazo] not in opciones:
        st.session_state[key_plazo] = opciones[0]

    plazo_sel = st.session_state[key_plazo]

    def seleccionar_opcion_session_state(key: str, valor):
        st.session_state[key] = valor

    def renderizar_tarjeta_selector(
        titulo: str,
        valor_visible: str,
        key: str,
        opciones_disponibles: list,
        format_func=lambda x: x,
        help_text: str = "",
    ):
        # La tarjeta conserva el mismo formato visual de los KPI y el popover
        # se abre directamente al tocarla, sin texto auxiliar ni flecha visible.
        etiqueta_tarjeta = f"{titulo}\n\n{valor_visible}"

        if hasattr(st, "popover"):
            with st.popover(etiqueta_tarjeta, use_container_width=True, help=help_text):
                st.markdown("<div class='selector-tarjeta-opciones-popover'>", unsafe_allow_html=True)
                for i, opcion in enumerate(opciones_disponibles):
                    etiqueta = format_func(opcion)
                    if pd.isna(opcion) if not isinstance(opcion, str) else False:
                        etiqueta = "Sin dato"
                    etiqueta = str(etiqueta)
                    seleccionado = opcion == st.session_state.get(key)
                    st.button(
                        etiqueta,
                        key=f"opt_{key}_{i}_{limpiar_texto(etiqueta)}",
                        type="primary" if seleccionado else "secondary",
                        use_container_width=True,
                        on_click=seleccionar_opcion_session_state,
                        args=(key, opcion),
                    )
                st.markdown("</div>", unsafe_allow_html=True)
        else:
            # Fallback para versiones antiguas de Streamlit: mantiene el cambio funcional.
            idx_actual = 0
            for i, opcion in enumerate(opciones_disponibles):
                if opcion == st.session_state.get(key):
                    idx_actual = i
                    break
            st.selectbox(
                titulo,
                opciones_disponibles,
                index=idx_actual,
                key=key,
                format_func=format_func,
                label_visibility="collapsed",
                help=help_text,
            )

    st.markdown(
        f"""
<style>
.kpi-plazo-card {{
    background: rgba(255,255,255,0.96);
    border: 1px solid {COLOR_BORDE};
    border-radius: 16px;
    padding: 12px 14px;
    min-height: 82px;
    box-shadow: 0 10px 22px rgba(12, 33, 74, 0.07);
    display: flex;
    flex-direction: column;
    justify-content: center;
    overflow: hidden;
}}

.kpi-plazo-label {{
    color: {COLOR_TEXTO};
    font-size: 13px;
    font-weight: 700;
    opacity: 0.86;
    margin-bottom: 7px;
    white-space: nowrap;
}}

.kpi-plazo-value {{
    color: {COLOR_PRIMARIO};
    font-size: clamp(18px, 1.45vw, 30px);
    font-weight: 900;
    line-height: 1.04;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}}

.plazo-filter-note {{
    color: {COLOR_TEXTO};
    font-size: 12px;
    font-weight: 700;
    opacity: 0.72;
    margin-top: 8px;
    line-height: 1.3;
}}

.plazo-kpi-note {{
    color: {COLOR_TEXTO};
    font-size: 11px;
    font-weight: 650;
    opacity: 0.70;
    margin-top: 6px;
    line-height: 1.25;
}}

.corte-plazo-card {{
    background: rgba(255,255,255,0.96);
    border: 1px solid {COLOR_BORDE};
    border-radius: 16px;
    padding: 12px 14px;
    min-height: 82px;
    box-shadow: 0 10px 22px rgba(12, 33, 74, 0.07);
    display: flex;
    flex-direction: column;
    justify-content: center;
    overflow: hidden;
}}

.corte-plazo-label {{
    color: {COLOR_TEXTO};
    font-size: 13px;
    font-weight: 700;
    opacity: 0.86;
    margin-bottom: 7px;
    white-space: nowrap;
}}

.corte-plazo-value {{
    color: {COLOR_PRIMARIO};
    font-size: clamp(18px, 1.25vw, 26px);
    font-weight: 900;
    line-height: 1.04;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}}

.treemap-selection-note {{
    margin-top: 7px;
    color: {COLOR_PRIMARIO};
    font-size: 12px;
    font-weight: 800;
    line-height: 1.25;
}}

.plazo-popover-title {{
    color: {COLOR_PRIMARIO};
    font-size: 13px;
    font-weight: 900;
    margin-bottom: 8px;
}}

.kpi-plazo-card-clickable {{
    cursor: pointer;
    transition: border-color 0.18s ease, box-shadow 0.18s ease, transform 0.18s ease;
}}

.kpi-plazo-card-clickable:hover {{
    border-color: {COLOR_PRIMARIO};
    box-shadow: 0 12px 26px rgba(12, 33, 74, 0.12);
    transform: translateY(-1px);
}}

div[data-testid="stButton"] > button[kind="tertiary"],
div[data-testid="stButton"] > button[data-testid="baseButton-tertiary"],
div[data-testid="stButton"] > button:has(p:empty),
div[data-testid="stButton"] > button:has(p span:empty) {{
    margin-top: -82px;
    min-height: 82px;
    height: 82px;
    width: 100%;
    padding: 0 !important;
    background: transparent !important;
    border: 0 !important;
    box-shadow: none !important;
    color: transparent !important;
    opacity: 0.01 !important;
    position: relative;
    z-index: 5;
}}

div[data-testid="stButton"] > button[kind="tertiary"] p,
div[data-testid="stButton"] > button[data-testid="baseButton-tertiary"] p,
div[data-testid="stButton"] > button[kind="tertiary"] span,
div[data-testid="stButton"] > button[data-testid="baseButton-tertiary"] span {{
    color: transparent !important;
    opacity: 0 !important;
}}

div[data-testid="stButton"] > button[kind="tertiary"]:hover,
div[data-testid="stButton"] > button[kind="tertiary"]:focus,
div[data-testid="stButton"] > button[kind="tertiary"]:active,
div[data-testid="stButton"] > button[data-testid="baseButton-tertiary"]:hover,
div[data-testid="stButton"] > button[data-testid="baseButton-tertiary"]:focus,
div[data-testid="stButton"] > button[data-testid="baseButton-tertiary"]:active {{
    background: transparent !important;
    border: 0 !important;
    box-shadow: none !important;
    color: transparent !important;
}}

.selector-tarjeta-opciones {{
    margin-top: 8px;
    padding: 10px;
    border: 1px solid {COLOR_BORDE};
    border-radius: 16px;
    background: rgba(255,255,255,0.98);
    box-shadow: 0 12px 26px rgba(12, 33, 74, 0.08);
}}

.selector-tarjeta-opciones div[data-testid="stButton"] > button {{
    margin-top: 0 !important;
    min-height: 40px !important;
    height: auto !important;
    opacity: 1 !important;
    color: {COLOR_PRIMARIO} !important;
    border: 1px solid {COLOR_BORDE} !important;
    border-radius: 12px !important;
    background: rgba(255,255,255,0.96) !important;
    box-shadow: none !important;
    position: static !important;
    z-index: auto !important;
}}

.selector-tarjeta-opciones div[data-testid="stButton"] > button p,
.selector-tarjeta-opciones div[data-testid="stButton"] > button span {{
    color: inherit !important;
    opacity: 1 !important;
}}

/* Tarjeta desplegable profesional para Plazo y Corte */
div[data-testid="stPopover"] > button {{
    background: rgba(255,255,255,0.96) !important;
    border: 1px solid {COLOR_BORDE} !important;
    border-radius: 16px !important;
    padding: 12px 14px !important;
    min-height: 82px !important;
    height: 82px !important;
    width: 100% !important;
    box-shadow: 0 10px 22px rgba(12, 33, 74, 0.07) !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: flex-start !important;
    justify-content: center !important;
    text-align: left !important;
    gap: 6px !important;
}}

div[data-testid="stPopover"] > button:hover,
div[data-testid="stPopover"] > button:focus {{
    border-color: {COLOR_PRIMARIO} !important;
    box-shadow: 0 12px 26px rgba(12, 33, 74, 0.12) !important;
    background: rgba(255,255,255,0.98) !important;
}}

div[data-testid="stPopover"] > button svg {{
    display: none !important;
}}

div[data-testid="stPopover"] > button p {{
    margin: 0 !important;
    color: {COLOR_TEXTO} !important;
    font-size: 13px !important;
    font-weight: 700 !important;
    opacity: 0.86 !important;
    line-height: 1.08 !important;
}}

div[data-testid="stPopover"] > button p:last-child,
div[data-testid="stPopover"] > button div:last-child p:last-child {{
    color: {COLOR_PRIMARIO} !important;
    font-size: clamp(18px, 1.45vw, 30px) !important;
    font-weight: 900 !important;
    opacity: 1 !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
}}

.selector-tarjeta-opciones-popover {{
    min-width: 220px;
    padding: 2px 0 4px 0;
}}

.selector-tarjeta-opciones-popover div[data-testid="stButton"] > button {{
    margin-top: 6px !important;
    min-height: 38px !important;
    border-radius: 12px !important;
}}
</style>
""",
        unsafe_allow_html=True,
    )

    if plazo_sel == "Todos":
        df_filtrado = df_corte.copy()
        plazo_texto = "Todos"
    else:
        plazo_num = float(pd.to_numeric(plazo_sel, errors="coerce"))
        df_filtrado = df_corte[df_corte["Plazo"] == plazo_num].copy()
        plazo_texto = formatear_plazo_opcion(plazo_sel)

    df_metricas = filtrar_df_por_nodo_treemap(df_filtrado, selected_node_id)
    if df_metricas.empty:
        df_metricas = df_filtrado.copy()
        selected_node_id = None

    metricas = calcular_metricas_plazo(df_metricas)
    metricas["Corte"] = corte_sel if corte_sel != "Sin corte" else metricas.get("Corte", "")

    with st.expander("Plazo", expanded=True):
        cols = st.columns([0.82, 0.98, 0.86, 0.98, 0.98, 0.82, 0.72])

        with cols[0]:
            renderizar_tarjeta_selector(
                "Plazo",
                plazo_texto,
                key_plazo,
                opciones,
                format_func=formatear_plazo_opcion,
                help_text="Toca para elegir otro plazo.",
            )

        with cols[1]:
            renderizar_tarjeta_selector(
                "Corte",
                corte_sel if corte_sel != "Sin corte" else "Sin corte",
                key_corte,
                cortes_opciones,
                format_func=lambda x: x,
                help_text="Toca para elegir otro corte.",
            )

        with cols[2]:
            renderizar_tarjeta_kpi_plazo("Monto Vale", formato_moneda(metricas["Monto Vale"]).replace("$", ""))
            st.markdown("<div class='plazo-kpi-note'>Capital / Vales</div>", unsafe_allow_html=True)
        with cols[3]:
            renderizar_tarjeta_kpi_plazo("Capital", formato_moneda(metricas["Capital"]))
        with cols[4]:
            renderizar_tarjeta_kpi_plazo("Interés", formato_moneda(metricas["Interes"]))
        with cols[5]:
            renderizar_tarjeta_kpi_plazo("Tasa ganancia", f"{metricas['Tasa de Ganancia']:,.1f}%")
        with cols[6]:
            renderizar_tarjeta_kpi_plazo("Vales", formato_numero(metricas["Vales"]))


    return df_filtrado, plazo_texto, metricas

def construir_treemap_plazo_composicion(df_suc: pd.DataFrame, estado: str, selected_node_id: str | None = None) -> go.Figure:
    """
    Construye un treemap financiero con la misma lógica visual del mapa de estructura.

    Jerarquía: Estado → Subdirección → Zona → Sucursal.
    Tamaño: Capital.
    Color: Tasa de ganancia.
    Plazo: se muestra exactamente como viene en el archivo. No se promedia.
    """
    df_plot = df_suc.copy()

    for col in ["Subdirección", "Zona", "Sucursal"]:
        if col not in df_plot.columns:
            df_plot[col] = "Sin dato"
        df_plot[col] = df_plot[col].fillna("Sin dato").astype(str).str.strip()
        df_plot[col] = df_plot[col].replace("", "Sin dato")

    if "Corte" not in df_plot.columns:
        df_plot["Corte"] = ""
    df_plot["Corte"] = df_plot["Corte"].fillna("").astype(str)

    if "Corte Texto" not in df_plot.columns:
        df_plot["Corte Texto"] = df_plot["Corte"].map(formatear_corte_plazo)
    df_plot["Corte Texto"] = df_plot["Corte Texto"].fillna("").astype(str)

    for col in ["Capital", "Interes", "Total", "Tasa de Ganancia", "Plazo", "Vales", "Ganancia"]:
        if col not in df_plot.columns:
            df_plot[col] = 0
        df_plot[col] = pd.to_numeric(df_plot[col], errors="coerce").fillna(0)

    df_plot = df_plot[df_plot["Capital"] > 0].copy()

    if df_plot.empty:
        raise ValueError(
            "No hay capital con datos de plazo y composición para las sucursales de este estado. "
            "Revisa que la base Plazo y composicion de dispersión tenga sucursales que coincidan con la estructura."
        )

    def agg_level(cols: list[str]) -> pd.DataFrame:
        g = (
            df_plot.groupby(cols, as_index=False)
            .agg(
                Capital=("Capital", "sum"),
                Interes=("Interes", "sum"),
                Total=("Total", "sum"),
                Ganancia=("Ganancia", "sum"),
                Vales=("Vales", "sum"),
                Corte=("Corte Texto", "first"),
                Plazos_Unicos=("Plazo", lambda x: sorted(pd.to_numeric(x, errors="coerce").dropna().unique().tolist())),
            )
        )
        g["Tasa de Ganancia"] = g.apply(
            lambda r: r["Interes"] / r["Capital"] * 100 if pd.to_numeric(r["Capital"], errors="coerce") else 0,
            axis=1,
        )
        g["Plazo Texto"] = g["Plazos_Unicos"].map(plazo_display_desde_valores)
        return g.drop(columns=["Plazos_Unicos"])

    estado_label = str(estado)

    if "Estado" in df_plot.columns:
        total = agg_level(["Estado"])
        if not total.empty:
            total["Estado"] = estado_label
    else:
        total = pd.DataFrame()

    if total.empty:
        total = pd.DataFrame(
            [{
                "Estado": estado_label,
                "Capital": df_plot["Capital"].sum(),
                "Interes": df_plot["Interes"].sum(),
                "Total": df_plot["Total"].sum(),
                "Ganancia": df_plot["Ganancia"].sum(),
                "Vales": df_plot["Vales"].sum(),
                "Tasa de Ganancia": (
                    df_plot["Interes"].sum() / df_plot["Capital"].sum() * 100
                    if df_plot["Capital"].sum() else 0
                ),
                "Plazo Texto": plazo_display_desde_valores(df_plot["Plazo"]),
                "Corte": next((c for c in df_plot["Corte Texto"].dropna().astype(str).unique().tolist() if c), ""),
            }]
        )

    sub = agg_level(["Subdirección"])
    zona = agg_level(["Subdirección", "Zona"])
    suc = agg_level(["Subdirección", "Zona", "Sucursal"])

    ids = []
    labels = []
    parents = []
    values = []
    colors = []
    custom = []

    def add_node(node_id: str, label: str, parent: str, row: pd.Series):
        capital = float(pd.to_numeric(row.get("Capital", 0), errors="coerce") or 0)
        interes = float(pd.to_numeric(row.get("Interes", 0), errors="coerce") or 0)
        total_val = float(pd.to_numeric(row.get("Total", 0), errors="coerce") or 0)
        ganancia = float(pd.to_numeric(row.get("Ganancia", 0), errors="coerce") or 0)
        tasa = float(pd.to_numeric(row.get("Tasa de Ganancia", 0), errors="coerce") or 0)
        plazo_texto = str(row.get("Plazo Texto", "") or "")
        vales = float(pd.to_numeric(row.get("Vales", 0), errors="coerce") or 0)
        corte = str(row.get("Corte", "") or "")

        ids.append(node_id)
        labels.append(str(label))
        parents.append(parent)
        values.append(capital)
        colors.append(tasa)
        custom.append([capital, interes, total_val, ganancia, tasa, plazo_texto, vales, corte, node_id])

    add_node(f"estado::{estado_label}", estado_label, "", total.iloc[0])

    for _, r in sub.iterrows():
        sub_id = f"sub::{r['Subdirección']}"
        add_node(sub_id, r["Subdirección"], f"estado::{estado_label}", r)

    for _, r in zona.iterrows():
        sub_id = f"sub::{r['Subdirección']}"
        zona_id = f"zona::{r['Subdirección']}::{r['Zona']}"
        add_node(zona_id, r["Zona"], sub_id, r)

    for _, r in suc.iterrows():
        zona_id = f"zona::{r['Subdirección']}::{r['Zona']}"
        suc_id = f"suc::{r['Subdirección']}::{r['Zona']}::{r['Sucursal']}"
        add_node(suc_id, r["Sucursal"], zona_id, r)

    fig = go.Figure(
        go.Treemap(
            ids=ids,
            labels=labels,
            parents=parents,
            values=values,
            branchvalues="total",
            marker=dict(
                colors=colors,
                colorscale=[
                    [0.0, "#D73027"],
                    [0.5, "#FEE08B"],
                    [1.0, "#1A9850"],
                ],
                colorbar=dict(title="Tasa ganancia"),
                line=dict(width=1.5, color="rgba(255,255,255,0.65)"),
            ),
            texttemplate=(
                "<b>%{label}</b><br>"
                "$%{customdata[0]:,.0f}<br>"
                "%{customdata[4]:,.1f}%<br>"
                "%{customdata[5]}"
            ),
            textfont=dict(size=16),
            customdata=custom,
            hoverinfo="none",
            hovertemplate=None,
            maxdepth=4,
        )
    )

    return fig


def renderizar_treemap_plazo_con_click(fig: go.Figure, estado: str, selection_key: str) -> str | None:
    """
    Renderiza el treemap y captura clics en cualquier nivel:
    Estado, Subdirección, Zona o Sucursal.

    Primero usa la selección nativa de Streamlit. Si esa versión de Streamlit
    no la soporta, usa streamlit-plotly-events como respaldo. El popup de hover
    se mantiene desactivado.
    """
    chart_key = f"treemap_plazo_chart_{limpiar_texto(estado)}"

    def resolver_node_id_desde_punto(punto) -> str | None:
        if punto is None:
            return None

        ids_fig = list(fig.data[0].ids) if len(fig.data) and hasattr(fig.data[0], "ids") else []
        labels_fig = list(fig.data[0].labels) if len(fig.data) and hasattr(fig.data[0], "labels") else []
        parents_fig = list(fig.data[0].parents) if len(fig.data) and hasattr(fig.data[0], "parents") else []

        def get_val(obj, key, default=None):
            if isinstance(obj, dict):
                return obj.get(key, default)
            return getattr(obj, key, default)

        # 1) Id directo.
        for llave in ["id", "point_id", "pointId"]:
            valor = get_val(punto, llave)
            if valor:
                return str(valor)

        # 2) Customdata con node_id.
        customdata = get_val(punto, "customdata")
        if isinstance(customdata, (list, tuple)) and len(customdata) >= 9 and customdata[8]:
            return str(customdata[8])

        # 3) Índice del punto contra fig.data[0].ids.
        for llave in ["point_number", "pointNumber", "point_index", "pointIndex", "pointNumber"]:
            valor = get_val(punto, llave)
            if valor is not None:
                try:
                    idx_punto = int(valor)
                    if 0 <= idx_punto < len(ids_fig):
                        return str(ids_fig[idx_punto])
                except Exception:
                    pass

        # 4) currentPath / path de treemap. Ejemplo:
        # /Chihuahua/Chihuahua/Chihuahua Norte/Cd. Juárez
        for llave in ["currentPath", "current_path", "path"]:
            ruta = get_val(punto, llave)
            if ruta:
                partes_ruta = [p for p in str(ruta).split("/") if p]
                if partes_ruta:
                    ultimo = partes_ruta[-1]
                    candidatos = [
                        i for i, label in enumerate(labels_fig)
                        if str(label) == str(ultimo)
                    ]
                    if candidatos:
                        candidatos = sorted(
                            candidatos,
                            key=lambda i: str(ids_fig[i]).count("::") if i < len(ids_fig) else 0,
                            reverse=True,
                        )
                        return str(ids_fig[candidatos[0]])

        # 5) Fallback por label/entry/text. Esto captura hojas internas
        # como Cd. Juárez cuando el evento no trae customdata.
        label_evento = get_val(punto, "label") or get_val(punto, "entry") or get_val(punto, "text")
        parent_evento = get_val(punto, "parent")

        if label_evento:
            label_evento = str(label_evento)
            candidatos = [
                i for i, label in enumerate(labels_fig)
                if str(label) == label_evento
            ]

            if parent_evento:
                parent_evento = str(parent_evento)
                candidatos_parent = []
                for i in candidatos:
                    parent_id = str(parents_fig[i]) if i < len(parents_fig) else ""
                    parent_label = ""
                    if parent_id in ids_fig:
                        try:
                            parent_label = str(labels_fig[ids_fig.index(parent_id)])
                        except Exception:
                            parent_label = ""

                    if parent_evento in [parent_id, parent_label]:
                        candidatos_parent.append(i)

                if candidatos_parent:
                    candidatos = candidatos_parent

            if len(candidatos) == 1:
                return str(ids_fig[candidatos[0]])

            if len(candidatos) > 1:
                candidatos = sorted(
                    candidatos,
                    key=lambda i: str(ids_fig[i]).count("::") if i < len(ids_fig) else 0,
                    reverse=True,
                )
                return str(ids_fig[candidatos[0]])

        return None

    def resolver_node_id_desde_evento(evento) -> str | None:
        if not evento:
            return None

        # Streamlit nativo: evento["selection"]["points"]
        try:
            if isinstance(evento, dict):
                selection = evento.get("selection", {})
                puntos = selection.get("points", []) if isinstance(selection, dict) else []
            else:
                selection = getattr(evento, "selection", None)
                puntos = getattr(selection, "points", []) if selection is not None else []
        except Exception:
            puntos = []

        if puntos:
            return resolver_node_id_desde_punto(puntos[0])

        # streamlit-plotly-events: lista directa de puntos.
        if isinstance(evento, list) and evento:
            return resolver_node_id_desde_punto(evento[0])

        if isinstance(evento, dict):
            return resolver_node_id_desde_punto(evento)

        return None

    # 1) Intento principal: selección nativa de Streamlit.
    try:
        evento = st.plotly_chart(
            fig,
            use_container_width=True,
            key=chart_key,
            on_select="rerun",
            selection_mode="points",
        )
        nuevo_node_id = resolver_node_id_desde_evento(evento)
        if nuevo_node_id and nuevo_node_id != st.session_state.get(selection_key):
            st.session_state[selection_key] = nuevo_node_id
            st.rerun()

        return st.session_state.get(selection_key)

    except TypeError:
        # Versiones anteriores de Streamlit no aceptan on_select/selection_mode.
        pass
    except Exception:
        # Si la selección nativa falla, intenta con el componente externo.
        pass

    # 2) Respaldo: streamlit-plotly-events.
    if plotly_events is not None:
        try:
            eventos = plotly_events(
                fig,
                click_event=True,
                hover_event=False,
                select_event=False,
                override_height=720,
                override_width="100%",
                key=chart_key,
            )

            nuevo_node_id = resolver_node_id_desde_evento(eventos)
            if nuevo_node_id and nuevo_node_id != st.session_state.get(selection_key):
                st.session_state[selection_key] = nuevo_node_id
                st.rerun()

            return st.session_state.get(selection_key)

        except Exception as e:
            st.warning(
                "No pude activar el clic dinámico del treemap. "
                "La gráfica se mostrará normal. Para activar clics, agrega streamlit-plotly-events a requirements.txt. "
                f"Detalle: {e}"
            )

    st.plotly_chart(fig, use_container_width=True)
    return st.session_state.get(selection_key)



def construir_mapa_estado_plazo_composicion(
    df: pd.DataFrame,
    nombre_valera: str,
    estado: str,
    fecha_texto: str,
    pais: str = "MÉXICO",
):
    df_estado = df[df["Estado"].apply(limpiar_texto) == limpiar_texto(estado)].copy()

    if df_estado.empty:
        st.warning(f"No hay datos para {estado}.")
        return

    df_suc = preparar_sucursales_financieras_para_mapa(df_estado)

    if df_suc.empty:
        st.warning("No hay sucursales para este estado/departamento.")
        return

    selection_key = f"treemap_plazo_selected_{limpiar_texto(estado)}"
    selected_node_id = st.session_state.get(selection_key)

    df_suc_filtrado, plazo_texto, metricas_plazo = renderizar_selector_plazo_y_kpis(
        df_suc,
        estado,
        selected_node_id=selected_node_id,
    )

    if df_suc_filtrado.empty:
        st.warning("No hay datos para el plazo seleccionado.")
        return

    try:
        fig = construir_treemap_plazo_composicion(df_suc_filtrado, estado, selected_node_id=selected_node_id)
    except Exception as e:
        st.warning(str(e))
        return

    corte_actual = metricas_plazo.get("Corte", "")
    if not corte_actual and "Corte Texto" in df_suc_filtrado.columns:
        corte_actual = next((c for c in df_suc_filtrado["Corte Texto"].dropna().astype(str).unique().tolist() if c), "")
    if not corte_actual and "Corte" in df_suc_filtrado.columns:
        corte_actual = next((formatear_corte_plazo(c) for c in df_suc_filtrado["Corte"].dropna().astype(str).unique().tolist() if str(c).strip()), "")
    if not corte_actual and "Corte Texto" in df_suc.columns:
        corte_actual = next((c for c in df_suc["Corte Texto"].dropna().astype(str).unique().tolist() if c), "")
    if not corte_actual:
        corte_actual = obtener_corte_visible_plazo()

    st.session_state["corte_plazo_composicion_actual"] = corte_actual

    titulo_corte = f"Corte plazo {corte_actual}" if corte_actual else "Corte plazo no disponible"
    titulo_plazo = "" if plazo_texto == "Todos" else f" - {plazo_texto}"

    fig.update_layout(
        title=f"{estado} - Plazo y composición por estructura - {nombre_valera} - {titulo_corte}{titulo_plazo}",
        height=720,
        margin=dict(l=10, r=10, t=70, b=10),
        paper_bgcolor="rgba(255,255,255,0)",
        plot_bgcolor="rgba(255,255,255,0)",
        font=dict(color=COLOR_TEXTO),
        clickmode="event+select",
        uirevision=f"{estado}-{corte_actual}-{plazo_texto}",
    )

    renderizar_guia_interaccion_mapa_financiero()
    renderizar_treemap_plazo_con_click(fig, estado, selection_key)

# ======================================================
# PÁGINA DE MAPA
# ======================================================
def mostrar_mapa(valera_param: str):
    item_valera = next((x for x in VALES if x["param"] == valera_param), None)

    if item_valera is None:
        mostrar_inicio()
        return

    nombre_valera = item_valera["nombre"]
    pais_exclusivo = item_valera.get("pais_exclusivo")
    usar_distribuidoras_mx = item_valera.get("usar_distribuidoras_mx", False)

    # Al entrar a una valera nueva, fuerza siempre el mapa completo.
    if st.session_state.get("__ultima_valera_abierta") != valera_param:
        st.session_state["__ultima_valera_abierta"] = valera_param
        if get_query_param("estado", ""):
            set_query_params(valera=valera_param)
            st.rerun()

    if usar_distribuidoras_mx and ARCHIVO_DISTRIBUIDORAS_MX.exists():
        try:
            df_filtrado = cargar_distribuidoras_mx(str(ARCHIVO_DISTRIBUIDORAS_MX))
        except Exception as e:
            st.error(f"No pude leer Distribuidoras Vale MX.csv: {e}")
            return
    else:
        if not ARCHIVO_ESTRUCTURA.exists():
            st.error(
                "No encontré el archivo 'Estructura vales.xlsx'. "
                "Debe estar en la misma carpeta que app.py."
            )
            return

        try:
            df = cargar_estructura(str(ARCHIVO_ESTRUCTURA))
        except Exception as e:
            st.error(f"No pude leer el archivo de estructura: {e}")
            return

        carteras_validas = [limpiar_texto(x) for x in item_valera["carteras"]]

        df_filtrado = df[
            df["Cartera"].apply(limpiar_texto).isin(carteras_validas)
        ].copy()

        df_filtrado["Calidad de Cartera"] = 1
        df_filtrado["Distribuidoras Totales"] = 1
        df_filtrado["Distribuidoras al Corriente"] = 1
        df_filtrado["Distribuidoras en Mora"] = 0
        df_filtrado["Var Dist Corriente"] = 0
        df_filtrado["Var Dist en Mora"] = 0
        df_filtrado["Semaforo Variacion"] = "Verde"
        df_filtrado["Fecha de Corte Texto"] = "Sin fecha"

    if pais_exclusivo:
        df_filtrado = df_filtrado[
            df_filtrado["País"].apply(limpiar_texto) == limpiar_texto(pais_exclusivo)
        ].copy()

    st.markdown(
        f"""
<div class="top-bar">
    <h1 class="map-title">{nombre_valera}</h1>
    <a class="back-link" href="?home=1" target="_self">← Volver a Valeras</a>
</div>
""",
        unsafe_allow_html=True,
    )

    if df_filtrado.empty:
        st.warning(f"No encontré registros para {nombre_valera}.")
        return

    if "Fecha de Corte Texto" in df_filtrado.columns:
        fechas = sorted(
            [x for x in df_filtrado["Fecha de Corte Texto"].dropna().unique().tolist() if x != "NaT"]
        )
    else:
        fechas = ["Sin fecha"]

    if not fechas:
        fechas = ["Sin fecha"]

    fecha_sel = st.selectbox(
        "Fecha de Corte",
        fechas,
        index=len(fechas) - 1,
        key=f"fecha_corte_{valera_param}",
    )

    if "Fecha de Corte Texto" in df_filtrado.columns and fecha_sel != "Sin fecha":
        df_filtrado = df_filtrado[df_filtrado["Fecha de Corte Texto"] == fecha_sel].copy()

    df_filtrado = integrar_dispersion_acumulada(df_filtrado, fecha_sel)
    df_filtrado = agregar_columnas_variacion(df_filtrado)
    df_filtrado = recalcular_canje_promedio(df_filtrado)

    estado_sel = get_query_param("estado", "")
    df_resumen_base = df_filtrado.copy()
    if estado_sel:
        df_resumen_base = df_filtrado[
            df_filtrado["Estado"].apply(limpiar_texto) == limpiar_texto(estado_sel)
        ].copy()
        if df_resumen_base.empty:
            df_resumen_base = df_filtrado.copy()

    total_coord = int(df_resumen_base["Coordinacion"].nunique())
    total_suc = int(df_resumen_base["Sucursal"].nunique())
    total_zonas = int(df_resumen_base["Zona"].nunique())
    total_sub = int(df_resumen_base["Subdirección"].nunique())
    total_dispersado_acum = pd.to_numeric(df_resumen_base.get("Total Dispersado", 0), errors="coerce").fillna(0).sum()
    total_canjes_acum = pd.to_numeric(df_resumen_base.get("Canjes", 0), errors="coerce").fillna(0).sum()
    canje_promedio_acum = total_dispersado_acum / total_canjes_acum if total_canjes_acum else 0


    st.markdown(
        f"""
<div class="kpi-grid">
    <div class="kpi-card">
        <div class="kpi-label">Coordinaciones</div>
        <div class="kpi-value">{total_coord:,}</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-label">Sucursales</div>
        <div class="kpi-value">{total_suc:,}</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-label">Zonas</div>
        <div class="kpi-value">{total_zonas:,}</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-label">Subdirecciones</div>
        <div class="kpi-value">{total_sub:,}</div>
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
<div class="kpi-grid">
    <div class="kpi-card">
        <div class="kpi-label">Dispersado acumulado</div>
        <div class="kpi-value">{formato_moneda(total_dispersado_acum)}</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-label">Canjes acumulados</div>
        <div class="kpi-value">{formato_numero(total_canjes_acum)}</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-label">Canje promedio acumulado</div>
        <div class="kpi-value">{formato_moneda(canje_promedio_acum)}</div>
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

    # Los botones de Vista y Tamaño se muestran debajo del mapa.
    # Aquí sólo tomamos el valor guardado para construir el mapa antes de renderizar los controles.
    if "nivel_vista" not in st.session_state:
        st.session_state["nivel_vista"] = "Sucursal"
    if "variable_tamano" not in st.session_state:
        st.session_state["variable_tamano"] = "Distribuidoras Totales"

    nivel_vista = st.session_state["nivel_vista"]
    variable_tamano = st.session_state["variable_tamano"]

    # Resumen IA ejecutivo + Tipo de mapa / guía ejecutiva.
    df_mapa_previo = preparar_mapa_por_nivel(
        df=df_resumen_base,
        nivel_vista=nivel_vista,
        variable_tamano=variable_tamano,
    )

    tipo_mapa = st.session_state.get("tipo_mapa_valeras", "Subdirección")

    cols_ia_tipo_mapa = st.columns([2.2, 1])
    with cols_ia_tipo_mapa[0]:
        mostrar_comentarios_ia(
            df_resumen_base=df_resumen_base,
            df_mapa=df_mapa_previo,
            resumen_pais=pd.DataFrame(),
            nombre_valera=nombre_valera,
            fecha_sel=fecha_sel,
            nivel_vista=nivel_vista,
            variable_tamano=variable_tamano,
            tipo_mapa=tipo_mapa,
            solo_ejecutivo=True,
            conservar_tarjetas=bool(estado_sel),
        )

    # Detecta el país de los datos actuales, aunque la marca no tenga pais_exclusivo configurado.
    paises_datos = sorted(df_filtrado["País"].dropna().unique().tolist())
    pais_actual = paises_datos[0] if len(paises_datos) == 1 else ""
    es_mexico = len(paises_datos) == 1 and limpiar_texto(pais_actual) == limpiar_texto("MÉXICO")
    es_peru = len(paises_datos) == 1 and limpiar_texto(pais_actual) == limpiar_texto("PERÚ")

    detalle_estado_activo = bool(estado_sel and (es_mexico or es_peru))
    elementos_estructura_actual = int(df_mapa_previo[nivel_vista].nunique()) if nivel_vista in df_mapa_previo.columns else 0
    mostrar_top_bottom_detalle = (not detalle_estado_activo) or elementos_estructura_actual >= 20

    if not mostrar_top_bottom_detalle and st.session_state.get("modo_tabla_resumen") in ["Top 10", "Bottom 10"]:
        st.session_state["modo_tabla_resumen"] = "Todos"

    modo_tabla_actual = st.session_state.get("modo_tabla_resumen", "Todos")
    texto_busqueda_actual = st.session_state.get(f"busqueda_resumen_{nivel_vista.lower()}", "")
    valores_destacados_mapa = calcular_destacados_mapa(
        df_resumen_base=df_resumen_base,
        nivel_vista=nivel_vista,
        variable_tamano=variable_tamano,
        modo_tabla=modo_tabla_actual,
        texto_busqueda=texto_busqueda_actual,
    )

    if estado_sel and (es_mexico or es_peru):
        nombre_pais_volver = "México" if es_mexico else "Perú"
        st.markdown(
            f"""
<a class="back-link" href="?valera={valera_param}" target="_self">← Volver al mapa de {nombre_pais_volver}</a>
""",
            unsafe_allow_html=True,
        )

        vista_detalle_estado = selector_botones(
            "Vista del detalle",
            ["Estructura", "Plazo y composición"],
            "vista_detalle_estado_valeras",
            "Estructura",
        )

        if vista_detalle_estado == "Plazo y composición":
            construir_mapa_estado_plazo_composicion(
                df=df_filtrado,
                nombre_valera=nombre_valera,
                estado=estado_sel,
                fecha_texto=fecha_sel,
                pais=pais_actual,
            )
        else:
            construir_mapa_estado_burbujas(
                df=df_filtrado,
                nombre_valera=nombre_valera,
                estado=estado_sel,
                variable_tamano=variable_tamano,
                fecha_texto=fecha_sel,
                pais=pais_actual,
                destacar_nivel=nivel_vista,
                destacar_valores=valores_destacados_mapa,
                tipo_mapa=tipo_mapa,
            )
    elif es_mexico:
        construir_mapa_estados_mexico(
            df=df_filtrado,
            nombre_valera=nombre_valera,
            variable_tamano=variable_tamano,
            fecha_texto=fecha_sel,
            destacar_nivel=nivel_vista,
            destacar_valores=valores_destacados_mapa,
            tipo_mapa=tipo_mapa,
        )
    elif es_peru:
        construir_mapa_estados_peru(
            df=df_filtrado,
            nombre_valera=nombre_valera,
            variable_tamano=variable_tamano,
            fecha_texto=fecha_sel,
            destacar_nivel=nivel_vista,
            destacar_valores=valores_destacados_mapa,
            tipo_mapa=tipo_mapa,
        )
    else:
        df_mapa = preparar_mapa_por_nivel(
            df=df_filtrado,
            nivel_vista=nivel_vista,
            variable_tamano=variable_tamano,
        )

        st.warning("La vista política por estado/departamento está configurada para México y Perú. Esta vista conserva el mapa de burbujas.")

    fecha_mapa_ia = fecha_sel
    if estado_sel and (es_mexico or es_peru) and st.session_state.get("vista_detalle_estado_valeras", "Estructura") == "Plazo y composición":
        fecha_mapa_ia = st.session_state.get("corte_plazo_composicion_actual", fecha_sel) or fecha_sel

    mostrar_comentario_ia_mapa(
        df_contexto=df_resumen_base,
        df_mapa=df_mapa_previo,
        nombre_valera=nombre_valera,
        fecha_sel=fecha_mapa_ia,
        nivel_vista=nivel_vista,
        variable_tamano=variable_tamano,
        tipo_mapa=tipo_mapa,
        modo_tabla=modo_tabla_actual,
        texto_busqueda=texto_busqueda_actual,
        estado_sel=estado_sel,
    )

    mostrar_botones_tipo_mapa = True
    if estado_sel and (es_mexico or es_peru):
        vista_detalle_actual = st.session_state.get("vista_detalle_estado_valeras", "Estructura")
        mostrar_botones_tipo_mapa = vista_detalle_actual == "Estructura"

    if mostrar_botones_tipo_mapa:
        cols_tipo_mapa_bajo_leyenda = st.columns([2.2, 1])
        with cols_tipo_mapa_bajo_leyenda[1]:
            tipo_mapa = selector_botones(
                "Tipo de mapa",
                ["Subdirección", "Calor Canjes", "Calor Dispersado"],
                "tipo_mapa_valeras",
                "Subdirección",
            )

    df_mapa = preparar_mapa_por_nivel(
        df=df_resumen_base,
        nivel_vista=nivel_vista,
        variable_tamano=variable_tamano,
    )

    # Opciones del resumen.
    # Los botones de nivel y la variable para Top/Bottom se muestran juntos en el recuadro del resumen.
    opciones_vista = ["Subdirección", "Zona", "Sucursal"]
    opciones_tamano = [
        "Calidad de Cartera",
        "Distribuidoras Totales",
        "Distribuidoras al Corriente",
    ]

    mostrar_resumen_pais = not bool(estado_sel and (es_mexico or es_peru))

    if mostrar_resumen_pais:
        st.subheader("Resumen por país")

    resumen_pais = (
        df_resumen_base.groupby("País", as_index=False)
        .agg(
            Coordinaciones=("Coordinacion", "nunique"),
            Sucursales=("Sucursal", "nunique"),
            Zonas=("Zona", "nunique"),
            Subdirecciones=("Subdirección", "nunique"),
            Calidad_de_Cartera=("Calidad de Cartera", "mean"),
            Distribuidoras_Totales=("Distribuidoras Totales", "sum"),
            Distribuidoras_al_Corriente=("Distribuidoras al Corriente", "sum"),
            Distribuidoras_en_Mora=("Distribuidoras en Mora", "sum"),
            Var_Dist_Corriente=("Var Dist Corriente", "sum"),
            Var_Dist_en_Mora=("Var Dist en Mora", "sum"),
            Total_Dispersado=("Total Dispersado", "sum"),
            Canjes=("Canjes", "sum"),
            Canjes_Fecha_Corte=("Canjes Fecha Corte", "sum"),
            Total_Dispersado_Fecha_Corte=("Total Dispersado Fecha Corte", "sum"),
        )
        .sort_values("Coordinaciones", ascending=False)
    )
    resumen_pais = resumen_pais.rename(
        columns={
            "Calidad_de_Cartera": "Calidad de Cartera",
            "Distribuidoras_Totales": "Distribuidoras Totales",
            "Distribuidoras_al_Corriente": "Distribuidoras al Corriente",
            "Distribuidoras_en_Mora": "Distribuidoras en Mora",
            "Var_Dist_Corriente": "Var Dist Corriente",
            "Var_Dist_en_Mora": "Var Dist en Mora",
            "Total_Dispersado": "Total Dispersado",
            "Canjes_Fecha_Corte": "Canjes Fecha Corte",
            "Total_Dispersado_Fecha_Corte": "Total Dispersado Fecha Corte",
        }
    )
    resumen_pais = agregar_columnas_variacion(resumen_pais)
    resumen_pais = recalcular_canje_promedio(resumen_pais)

    if mostrar_resumen_pais:
        mostrar_comentarios_ia(
            df_resumen_base=df_resumen_base,
            df_mapa=df_mapa,
            resumen_pais=resumen_pais,
            nombre_valera=nombre_valera,
            fecha_sel=fecha_sel,
            nivel_vista=nivel_vista,
            variable_tamano=variable_tamano,
            tipo_mapa=tipo_mapa,
            ocultar_ejecutivo=True,
        )

        mostrar_tabla_variacion(resumen_pais)

        st.markdown("<br>", unsafe_allow_html=True)

    if mostrar_top_bottom_detalle:
        texto_ayuda_resumen = f"""
**Cómo usar los botones de resumen**

**Subdirección, Zona y Sucursal** cambian el nivel de análisis del mapa y de la tabla inferior.

**Todos** muestra el universo completo. **Top 10** y **Bottom 10** aíslan los mejores o peores registros según la variable seleccionada.

**Calidad de Cartera, Distribuidoras Totales y Distribuidoras al Corriente** definen la variable usada para ordenar Top/Bottom y para dimensionar las bolitas del mapa.

Cuando estás dentro del detalle de un estado, los botones **Top 10** y **Bottom 10** sólo se muestran si el nivel seleccionado tiene **20 o más elementos**. En este momento hay **{elementos_estructura_actual:,}** elementos en **{nivel_vista}**, por eso la vista permite comparar extremos sin perder contexto operativo.

El buscador filtra por el nivel activo: subdirección, zona o sucursal.
"""
    else:
        texto_ayuda_resumen = f"""
**Cómo usar los botones de resumen**

**Subdirección, Zona y Sucursal** cambian el nivel de análisis del mapa y de la tabla inferior.

En el detalle de este estado hay **{elementos_estructura_actual:,}** elementos en **{nivel_vista}**. Como son menos de 20, no se muestran los botones **Top 10** y **Bottom 10**, porque segmentar una base tan pequeña puede quitar contexto en lugar de ayudar.

En este caso, la tabla se mantiene completa y se ordena automáticamente de **mayor a menor** según la variable seleccionada: **{variable_tamano}**. Así puedes ver primero las estructuras con mayor peso operativo sin ocultar ningún registro.

**Calidad de Cartera, Distribuidoras Totales y Distribuidoras al Corriente** cambian la variable de ordenamiento y también la referencia de tamaño de las bolitas del mapa.

El buscador filtra por el nivel activo: subdirección, zona o sucursal.
"""

    with st.container(border=True):
        cols_resumen_titulo = st.columns([2.55, 0.25, 1, 1, 1])
        with cols_resumen_titulo[0]:
            st.markdown(
                f'''
<div class="resumen-title-box">
    <div class="resumen-title-text">Resumen por {nivel_vista.lower()}</div>
</div>
''',
                unsafe_allow_html=True,
            )
        with cols_resumen_titulo[1]:
            try:
                with st.popover("ⓘ", use_container_width=True):
                    st.markdown(texto_ayuda_resumen)
            except Exception:
                with st.expander("ⓘ", expanded=False):
                    st.markdown(texto_ayuda_resumen)

        for col, opcion in zip(cols_resumen_titulo[2:], opciones_vista):
            tipo = "primary" if st.session_state.get("nivel_vista") == opcion else "secondary"
            if col.button(opcion, type=tipo, use_container_width=True, key=f"nivel_vista_resumen_{opcion}"):
                st.session_state["nivel_vista"] = opcion
                st.rerun()

        if "modo_tabla_resumen" not in st.session_state:
            st.session_state["modo_tabla_resumen"] = "Todos"

        if mostrar_top_bottom_detalle:
            cols_modo_tabla = st.columns(3)
            for col, opcion in zip(cols_modo_tabla, ["Todos", "Top 10", "Bottom 10"]):
                tipo = "primary" if st.session_state.get("modo_tabla_resumen") == opcion else "secondary"
                if col.button(opcion, type=tipo, use_container_width=True, key=f"modo_tabla_resumen_{opcion}"):
                    st.session_state["modo_tabla_resumen"] = opcion
                    st.rerun()
        else:
            st.session_state["modo_tabla_resumen"] = "Todos"

        modo_tabla = st.session_state["modo_tabla_resumen"]

        cols_variable_top_bottom = st.columns(3)
        for col, opcion in zip(cols_variable_top_bottom, opciones_tamano):
            tipo = "primary" if st.session_state.get("variable_tamano") == opcion else "secondary"
            if col.button(opcion, type=tipo, use_container_width=True, key=f"variable_tamano_resumen_{opcion}"):
                st.session_state["variable_tamano"] = opcion
                st.rerun()

        texto_busqueda = st.text_input(
            f"Buscar {nivel_vista}",
            value="",
            placeholder=f"Escribe para filtrar por {nivel_vista.lower()}...",
            key=f"busqueda_resumen_{nivel_vista.lower()}",
        )

    group_cols = [nivel_vista]

    resumen_nivel = (
        df_mapa.groupby(group_cols, as_index=False)
        .agg(
            Coordinaciones=("Coordinaciones", "sum"),
            Sucursales=("Sucursales", "sum"),
            Zonas=("Zonas", "sum"),
            Calidad_de_Cartera=("Calidad de Cartera", "mean"),
            Distribuidoras_Totales=("Distribuidoras Totales", "sum"),
            Distribuidoras_al_Corriente=("Distribuidoras al Corriente", "sum"),
            Distribuidoras_en_Mora=("Distribuidoras en Mora", "sum"),
            Var_Dist_Corriente=("Var Dist Corriente", "sum"),
            Var_Dist_en_Mora=("Var Dist en Mora", "sum"),
            Total_Dispersado=("Total Dispersado", "sum"),
            Canjes=("Canjes", "sum"),
            Canjes_Fecha_Corte=("Canjes Fecha Corte", "sum"),
            Total_Dispersado_Fecha_Corte=("Total Dispersado Fecha Corte", "sum"),
        )
    )

    resumen_nivel = resumen_nivel.rename(
        columns={
            "Calidad_de_Cartera": "Calidad de Cartera",
            "Distribuidoras_Totales": "Distribuidoras Totales",
            "Distribuidoras_al_Corriente": "Distribuidoras al Corriente",
            "Distribuidoras_en_Mora": "Distribuidoras en Mora",
            "Var_Dist_Corriente": "Var Dist Corriente",
            "Var_Dist_en_Mora": "Var Dist en Mora",
            "Total_Dispersado": "Total Dispersado",
            "Canjes_Fecha_Corte": "Canjes Fecha Corte",
            "Total_Dispersado_Fecha_Corte": "Total Dispersado Fecha Corte",
        }
    )
    resumen_nivel = agregar_columnas_variacion(resumen_nivel)
    resumen_nivel = recalcular_canje_promedio(resumen_nivel)

    if texto_busqueda.strip():
        busqueda_norm = limpiar_texto(texto_busqueda)
        resumen_nivel = resumen_nivel[
            resumen_nivel[nivel_vista].astype(str).map(limpiar_texto).str.contains(
                busqueda_norm,
                na=False,
                regex=False,
            )
        ].copy()

    resumen_nivel = aplicar_filtro_tabla(
        df=resumen_nivel,
        modo=modo_tabla,
        variable_tamano=variable_tamano,
    )

    mostrar_comentario_ia_tabla_resumen(
        resumen_tabla=resumen_nivel,
        nivel_vista=nivel_vista,
        variable_tamano=variable_tamano,
        modo_tabla=modo_tabla,
        texto_busqueda=texto_busqueda,
        fecha_sel=fecha_sel,
        df_fuente=df_resumen_base,
    )

    mostrar_tabla_variacion(
        resumen_nivel,
        columnas_ocultas=["Coordinaciones", "Sucursales", "Zonas"],
        scroll_interno=(modo_tabla == "Todos"),
        mostrar_indice_ordenado=(modo_tabla in ["Top 10", "Bottom 10"]),
    )


# ======================================================
# ROUTER
# ======================================================
home_param = get_query_param("home", "")
valera_seleccionada = get_query_param("valera", "")

# Fuerza portada sólo cuando se presiona "Volver a Valeras".
# No se bloquea ?valera= porque ese mismo parámetro es el que usan las tarjetas para entrar.
if home_param:
    set_query_params()
    mostrar_inicio()
    st.stop()

if valera_seleccionada:
    mostrar_mapa(valera_seleccionada)
else:
    mostrar_inicio()
