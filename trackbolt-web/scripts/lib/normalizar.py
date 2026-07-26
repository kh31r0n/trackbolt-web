"""Limpieza de texto: el reporte del ERP trae mayusculas, typos y comillas dobles."""
import re
import unicodedata

# Typos y abreviaturas del ERP -> forma correcta. Se aplican sobre texto en minusculas.
CORRECCIONES = {
    "tornilos": "tornillos",
    "tuerga": "tuerca",
    "hexagona ": "hexagonal ",
    "milimerico": "milimetrico",
    "cariaje": "carriage",
    "carriaje": "carriage",
    "avellan ": "avellanado ",
    "sillin": "sillín",
    "aran ": "arandela ",
    "tor ": "tornillo ",
    "seg ": "seguridad ",
    "cab ": "cabeza ",
    "jgo ": "juego ",
    "cilindrica": "cilíndrica",
    "conica": "cónica",
    "plastico": "plástico",
    "esparrago": "espárrago",
    "jiss": "JIS",
    "movil": "móvil",
    "buton": "botón",
    "avellan": "avellanado",
    "zta": "zapata",
}

# Palabras que ya se muestran como especificacion y no deben repetirse en el nombre.
REDUNDANTES = {
    "milimetrico", "milimetrica", "milimétrico", "milimétrica", "mm", "pulgadas",
    "negro", "negra", "zinc", "zincada", "zincado", "inox", "bicro", "pavonado",
    "rex", "kilo", "unidad", "por", "clase", "grado", "cl", "g", "gr", "en", "/",
    "8.8", "10.9", "12.9", "13.9", "8,8", "10,9", "12,9", "2", "5", "8", "10",
    "total", "rosca",
}

# Nombre comercial definitivo para bases que quedan ambiguas tras limpiar.
RENOMBRES = {
    "wasa": "Arandela de presión",
    "wasa de presión": "Arandela de presión",
    "conos": "Arandela cónica",
    "central": "Tornillo de cabeza central",
    "pernos": "Perno",
    "brocas": "Broca",
    "machos": "Macho de roscar",
    "discos de corte": "Disco de corte",
    "chazo plástico": "Chazo plástico",
    "tornillo hexagonal especiales": "Tornillo hexagonal especial",
    "tornillo hexagonal flange": "Tornillo hexagonal flange",
    "tuerca uña": "Tuerca de uña",
    "tuerca pinar": "Tuerca pinar",
    "tuerca 2h": "Tuerca 2H de alta temperatura",
    "espárrago": "Espárrago",
    "espárrago mixto": "Espárrago mixto",
    "varilla": "Varilla roscada",
    "varilla metro": "Varilla roscada por metro",
    "varilla 3 metros": "Varilla roscada por 3 metros",
    "varilla b7 metro": "Varilla roscada B7 por metro",
    "espárrago b7": "Espárrago B7",
    "pin chaveta": "Pin chaveta",
    "pin seguer": "Pin seguer",
    "remache pop": "Remache pop",
    "remache pop ala ancha": "Remache pop de ala ancha",
    "tornillo lámina cabeza hexagonal punta broca": "Tornillo de lámina punta broca",
    "tornillo lámina cabeza cilíndrica pavonado": "Tornillo de lámina cabeza cilíndrica",
    "arandela para sello": "Arandela de sello",
    "arandela sillín": "Arandela de sillín",
    "tuerca zapata": "Tuerca de zapata",
    "tuerca ciega": "Tuerca ciega",
    "tuerca mariposa": "Tuerca mariposa",
    "herramienta sata": "Herramienta Sata",
}

_ESPACIOS = re.compile(r"\s+")
_COMILLAS = re.compile(r'"{2,}')


def limpiar(texto):
    """Colapsa espacios y arregla las comillas triples del ERP (1\"\"\" -> 1\")."""
    if texto is None:
        return ""
    t = str(texto).replace(" ", " ")
    t = t.replace("''", '"')
    t = _COMILLAS.sub('"', t)
    t = _ESPACIOS.sub(" ", t).strip()
    return t


def corregir(texto):
    """Aplica las correcciones de typos conocidos del ERP."""
    t = " " + limpiar(texto).lower() + " "
    for mal, bien in CORRECCIONES.items():
        t = t.replace(" " + mal, " " + bien)
    return limpiar(t)


SIGLAS = {
    "unc", "unf", "unj", "bsw", "npt", "rp", "ri", "rt", "pt", "hss", "jis",
    "sae", "iso", "din", "astm", "sds", "pvc", "b7", "2h", "inox", "led",
}


def _capitalizar_palabra(p):
    """Respeta unidades, grados y designaciones tecnicas al pasar a minusculas."""
    if re.fullmatch(r"m\d+", p):                       # m16 -> M16
        return p.upper()
    if p in SIGLAS:
        return p.upper()
    if re.fullmatch(r"\d+[.,]\d+", p) or re.fullmatch(r"\d+", p):
        return p
    if re.fullmatch(r"[\d./\-\"']+", p):               # 1.1/2  5/8"  20mm
        return p
    if re.fullmatch(r"\d+(mm|pt|un|pc)", p):
        return p
    if re.fullmatch(r"\d[a-z]\d{4}|\d{2}[a-z]\d{6,8}", p):   # numero de parte OEM
        return p.upper()
    if re.fullmatch(r"st\d{4,6}[a-z]{0,2}", p):        # referencia Sata
        return p.upper()
    return p


def titulo(texto):
    """'TOR HEX MM CL10.9 RP' -> 'Tornillo hex mm clase 10.9 RP' con inicial mayuscula."""
    t = corregir(texto)
    palabras = [_capitalizar_palabra(p) for p in t.split(" ")]
    t = " ".join(palabras)
    return t[:1].upper() + t[1:] if t else t


def base_comercial(sublinea):
    """Convierte la sublinea del ERP en el nombre base del producto, sin datos repetidos."""
    t = corregir(sublinea)
    t = re.sub(r"\bgrado\s+\d\b", "", t)
    t = re.sub(r"\bclase\s+[\d.,]+\b", "", t)
    t = re.sub(r"\bcl\s*[\d.,]+\b", "", t)
    palabras = [p for p in t.split(" ") if p and p not in REDUNDANTES]
    t = limpiar(" ".join(palabras))
    if t in RENOMBRES:
        t = RENOMBRES[t]
    else:
        t = titulo(t)
    # Singulariza los plurales mas comunes de las sublineas del ERP.
    if t.lower().startswith("tornillos "):
        t = "Tornillo " + t[10:]
    elif t.lower().startswith("tuercas "):
        t = "Tuerca " + t[8:]
    elif t.lower().startswith("arandelas "):
        t = "Arandela " + t[10:]
    return t or "Producto"


def slug(texto):
    """Genera un identificador de URL sin acentos ni caracteres raros."""
    t = unicodedata.normalize("NFKD", limpiar(texto).lower())
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = t.replace('"', "").replace("/", "-").replace(".", "-")
    t = re.sub(r"[^a-z0-9]+", "-", t)
    return t.strip("-")


def moneda_cop(valor):
    """Formato colombiano: $1.234.567"""
    if valor is None:
        return "A confirmar"
    return "$" + f"{round(valor):,}".replace(",", ".")
