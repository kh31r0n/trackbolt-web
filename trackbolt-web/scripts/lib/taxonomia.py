"""Traduce la clasificacion del ERP (Tipo > Linea > Sublinea) a lineas de producto
entendibles por el cliente, al estilo de boltdepot.com.

La tabla es explicita a proposito: si el ERP agrega una linea nueva, cae en 'otros'
y el reporte lo avisa, en vez de desaparecer del sitio en silencio.
"""

LINEAS = [
    {
        "slug": "rodaje-zapata-cuchilla",
        "nombre": "Rodaje: zapata y cuchilla",
        "corto": "Rodaje",
        "descripcion": "Tornillería de tren de rodaje para excavadora, bulldozer y cargador: "
                       "tornillos de zapata de oruga, de cuchilla y carriage, en clase 12.9 y 13.9.",
        "destacada": True,
        "imagen": "/img/lineas/rodaje.jpg",
    },
    {
        "slug": "tornillos-hexagonales",
        "nombre": "Tornillos hexagonales",
        "corto": "Hexagonales",
        "descripcion": "La línea más amplia del inventario: tornillos de cabeza hexagonal métricos "
                       "y en pulgadas, clases 8.8, 10.9 y 12.9, grados SAE 2, 5 y 8, y en acero inoxidable.",
        "destacada": True,
        "imagen": "/img/lineas/hexagonales.jpg",
    },
    {
        "slug": "tornillos-flange",
        "nombre": "Tornillos flange",
        "corto": "Flange",
        "descripcion": "Cabeza hexagonal con arandela integrada: reparten la carga y no requieren "
                       "arandela suelta. Clase 8.8 y 10.9, rosca parcial y total.",
        "destacada": False,
        "imagen": "/img/lineas/flange.jpg",
    },
    {
        "slug": "tornillos-bristol",
        "nombre": "Tornillos Bristol (Allen)",
        "corto": "Bristol",
        "descripcion": "Tornillos de hueco hexagonal interior: cabeza cilíndrica, avellanada, "
                       "botón y prisioneros sin cabeza. Clase 12.9 en negro y en inoxidable.",
        "destacada": True,
        "imagen": "/img/lineas/bristol.jpg",
    },
    {
        "slug": "tuercas",
        "nombre": "Tuercas",
        "corto": "Tuercas",
        "descripcion": "Hexagonales, de seguridad con nylon, stover, flange, cónicas, altas, "
                       "de zapata y de perno de rueda. Métricas y en pulgadas.",
        "destacada": True,
        "imagen": "/img/lineas/tuercas.jpg",
    },
    {
        "slug": "arandelas",
        "nombre": "Arandelas y wasas",
        "corto": "Arandelas",
        "descripcion": "Arandelas planas, de presión (wasas), de sillín, cónicas, de sello, "
                       "mogolla y de estructura F-436 a F-458.",
        "destacada": True,
        "imagen": "/img/lineas/arandelas.jpg",
    },
    {
        "slug": "pernos-rueda",
        "nombre": "Pernos y espárragos de rueda",
        "corto": "Pernos de rueda",
        "descripcion": "Pernos y espárragos de rueda para camión, bus, tractor y maquinaria, "
                       "por marca de vehículo, con sus tuercas cónicas.",
        "destacada": True,
        "imagen": "/img/lineas/pernos.jpg",
    },
    {
        "slug": "esparragos-varillas",
        "nombre": "Espárragos y varillas roscadas",
        "corto": "Espárragos",
        "descripcion": "Espárragos métricos 8.8, espárragos B7 para alta temperatura y varilla "
                       "roscada por metro en zinc, inoxidable y B7.",
        "destacada": False,
        "imagen": "/img/lineas/esparragos.jpg",
    },
    {
        "slug": "tornillos-especiales",
        "nombre": "Tornillos especiales, lámina y estufa",
        "corto": "Especiales",
        "descripcion": "Tornillos de cabeza central, de lámina con punta broca, de estufa "
                       "y JIS de cabeza cilíndrica y plana.",
        "destacada": False,
        "imagen": "/img/lineas/especiales.jpg",
    },
    {
        "slug": "pines-remaches",
        "nombre": "Pines, remaches y chazos",
        "corto": "Pines y remaches",
        "descripcion": "Pines chaveta y seguer, remaches pop estándar y de ala ancha, "
                       "y chazos plásticos de fijación.",
        "destacada": False,
        "imagen": "/img/lineas/pines.jpg",
    },
    {
        "slug": "herramienta",
        "nombre": "Herramienta",
        "corto": "Herramienta",
        "descripcion": "Herramienta manual profesional Sata, Stanley, Force y Truper: copas, "
                       "ratchets, llaves, destornilladores, brocas, machos de roscar y discos de corte.",
        "destacada": True,
        "imagen": "/img/lineas/herramienta.jpg",
    },
    {
        "slug": "otros",
        "nombre": "Otros productos",
        "corto": "Otros",
        "descripcion": "Referencias que aún no tienen línea asignada.",
        "destacada": False,
        "imagen": "/img/lineas/otros.jpg",
    },
]

LINEAS_POR_SLUG = {l["slug"]: l for l in LINEAS}

# Colecciones transversales: no duplican datos, filtran por especificacion.
COLECCIONES = [
    {"slug": "inoxidable", "nombre": "Acero inoxidable", "filtro": {"acabado": "Inoxidable"},
     "descripcion": "Tornillería en acero inoxidable A2 (304) para ambientes corrosivos, "
                    "industria de alimentos, costa y exteriores."},
    {"slug": "clase-10-9", "nombre": "Clase 10.9", "filtro": {"grado": "Clase 10.9"},
     "descripcion": "Alta resistencia: 1.000 MPa de resistencia a la tracción. El estándar "
                    "de la maquinaria pesada moderna."},
    {"slug": "clase-12-9", "nombre": "Clase 12.9", "filtro": {"grado": "Clase 12.9"},
     "descripcion": "La clase más alta de uso común: 1.200 MPa. Rodaje, cuchillas y uniones críticas."},
    {"slug": "metrico", "nombre": "Sistema métrico", "filtro": {"sistema": "metrico"},
     "descripcion": "Referencias en milímetros, con paso normal y paso fino."},
    {"slug": "pulgadas", "nombre": "Sistema en pulgadas", "filtro": {"sistema": "pulgadas"},
     "descripcion": "Referencias en pulgadas con rosca UNC y UNF, grados SAE 2, 5 y 8."},
]


# Lineas del ERP que el cliente decidio no publicar, y los tipos que se descartan enteros.
# El filtro va sobre la clasificacion del ERP, no sobre la linea publica: asi 'PERNOS DE RUEDA
# REX' y 'TORNILLO CARIAJE REX' se quedan aunque sus equivalentes nacionales salgan.
LINEAS_EXCLUIDAS = {
    "CHAZOS",
    "ESPARRAGOS / VARILLAS",
    "MANUAL",
    "PERNOS",
    "PINES",
    "REMACHES",
    "TORNILLOS CABEZA CENTRAL",
    "TORNILLOS CARRIAGE",
    "TORNILLOS ESTUFA",
    "TORNILLOS LAMINA",
}

TIPOS_EXCLUIDOS = {"HERRAMIENTA"}


def _t(texto):
    return (texto or "").strip().upper()


def _clave(texto):
    """Como _t pero sin espacios repetidos: el ERP escribe 'TUERCAS ' y 'ESPARRAGOS  / VARILLAS'."""
    return " ".join(_t(texto).split())


def excluida(tipo, linea):
    """True si la referencia no debe llegar al catalogo."""
    return _clave(tipo) in TIPOS_EXCLUIDOS or _clave(linea) in LINEAS_EXCLUIDAS


def clasificar(tipo, linea, sublinea, descripcion):
    """Devuelve el slug de la linea publica. El orden de las reglas importa."""
    tp, ln, sl = _t(tipo), _t(linea), _t(sublinea)
    todo = f"{ln} {sl} {_t(descripcion)}"

    if tp == "HERRAMIENTA":
        return "herramienta"

    # Las tuercas primero: 'TUERCA FLANGE' y 'TUERCA ZAPATA' son tuercas, no flange ni rodaje.
    if "TUERCA" in ln:
        return "tuercas"

    if ln in {"ARANDELAS", "WASAS", "ARANDELAS REX"}:
        return "arandelas"

    if ln in {"PERNOS", "PERNOS DE RUEDA REX"}:
        return "pernos-rueda"

    if ln == "ESPARRAGOS / VARILLAS":
        return "esparragos-varillas"

    if "BRISTOL" in ln:
        return "tornillos-bristol"

    if ln in {"PINES", "REMACHES", "CHAZOS"}:
        return "pines-remaches"

    if ln in {"TORNILLOS ESTUFA", "TORNILLOS LAMINA", "TORNILLOS CABEZA CENTRAL"}:
        return "tornillos-especiales"

    # Rodaje: zapata, cuchilla y carriage, vengan de TORNILLERIA o de REX.
    if any(k in todo for k in ("ZAPATA", "CUCHILLA", "CARRIAGE", "CARRIAJE", "CARIAJE")):
        return "rodaje-zapata-cuchilla"

    if "FLANGE" in todo:
        return "tornillos-flange"

    if ln in {"TORNILLOS CABEZA HEXAGONAL", "TORNILLO HEXAGONAL REX"}:
        return "tornillos-hexagonales"

    return "otros"


# Nombre de grupo legible para las sublineas mas frecuentes.
# Lo que no este aqui usa la sublinea normalizada tal cual.
GRUPOS = {
    "TORNILLO HEXAGONAL MILIMETRICO 10.9": "Métrico clase 10.9",
    "TORNILLO HEXAGONAL MILIMETRICO 10.9 ": "Métrico clase 10.9",
    "TORNILLO HEXAGONAL MILIMETRICO 8.8": "Métrico clase 8.8",
    "TORNILLO HEXAGONAL MILIMETRICO 8.8 ROSCA TOTAL": "Métrico clase 8.8 rosca total",
    "TORNILLO HEXAGONAL GRADO 8 NEGRO": "Pulgadas grado 8",
    "TORNILLO HEXAGONAL GRADO 5 NEGRO": "Pulgadas grado 5",
    "TORNILLO HEXAGONAL GRADO 2 ZINC": "Pulgadas grado 2 zincado",
    "TORNILLO HEX INOX PULGADAS": "Inoxidable en pulgadas",
    "TORNILLO HEX INOX MILIMETRICO": "Inoxidable métrico",
    "TORNILLO HEXAGONA ESPECIALES": "Especiales",
    "TORNILLO HEXAGONAL FLANGE 8.8 / 10.9": "Flange clase 8.8 y 10.9",
    "TORNILLO HEXAGONAL FLANGE 10,9 REX": "Flange clase 10.9",
    "TORNILLO HEXAGONAL ZAPATA": "Tornillo de zapata",
    "TORNILLO PARA ZAPATA REX": "Tornillo de zapata",
    "TORNILLO CUCHILLA": "Tornillo de cuchilla",
    "TORNILLO HEXAGONAL CUCHILLA REX": "Tornillo de cuchilla",
    "TORNILLO CARRIAGE ZINC": "Carriage zincado",
    "TORNILLO CARRIAJE PULGADAS REX": "Carriage en pulgadas",
    "TORNILLO HEXAGONAL MM 10,9 REX": "Métrico clase 10.9",
    "TORNILLO HEXAGONAL MM 8.8  REX": "Métrico clase 8.8",
    "TORNILLO HEXAGONAL EN PULGADAS GR 8": "Pulgadas grado 8",
    "TORNILLO CON CABEZA BRISTOL  REX": "Cabeza cilíndrica",
    "TORNILLO AVELLAN BRISTOL REX": "Cabeza avellanada",
    "TORNILLO BRISTOL CON CABEZA MILIMETRICO NEGRO": "Cabeza cilíndrica métrico negro",
    "TORNILLO BRISTOL CON CABEZA NEGRO": "Cabeza cilíndrica en pulgadas",
    "TORNILLO BRISTOL SIN CABEZA NEGRO": "Prisionero en pulgadas",
    "TORNILLO BRISTOL SIN CABEZA MILIMERICO NEGRO": "Prisionero métrico",
    "TORNILLO BRISTOL AVELLAN MILIMETRICO NEGRO": "Avellanado métrico negro",
    "TORNILLO BRISTOL AVELLAN NEGRO": "Avellanado en pulgadas",
    "TORNILLO BRISTOL BUTON MILIMETRICO NEGRO": "Botón métrico negro",
    "TORNILLO PRISIONERO CABEZA CUADRADA": "Prisionero de cabeza cuadrada",
    "TUERCA DE SEGURIDAD NYLON": "Seguridad con nylon",
    "TUERCA SEGURIDAD STOVER": "Seguridad stover",
    "TUERCA SEGURIDAD FLANGE STOVER": "Seguridad flange stover",
    "TUERCA HEXAGONAL ALTA": "Hexagonal alta",
    "TUERCA HEXAGONAL CONICA": "Cónica de rueda",
    "TUERCA ZAPATA": "De zapata",
    "TUERCA CUADRADA ZAPATA REX": "Cuadrada de zapata",
    "TUERCA CONO FORJADO": "Cono forjado",
    "TUERCA ARANDELA MOVIL": "Con arandela móvil",
    "TUERCA 2H NEGRA": "2H de alta temperatura",
    "ARANDELA PLANA REX": "Plana",
    "ARANDELA MOGOLLA": "Mogolla",
    "ARANDELA SILLIN": "De sillín",
    "ARANDELA PARA SELLO": "De sello",
    "ARANDELA ESPECIAL BICRO": "Especial bicromatada",
    "ARANDELA SUPER GRUESA": "Súper gruesa",
    "CONOS": "Cónica",
    "WASA NEGRA": "De presión negra",
    "WASA ZINC": "De presión zincada",
    "WASA INOX": "De presión inoxidable",
    "PERNOS": "Por vehículo",
    "PERNO DE RUEDA REX": "Perno de rueda",
    "TUERCA PERNO DE RUEDA REX": "Tuerca de perno de rueda",
    "ESPARRAGO MILIMETRICO 8.8": "Métrico clase 8.8",
    "ESPARRAGO B7": "B7 alta temperatura",
    "VARILLA B7 POR METRO": "Varilla B7 por metro",
    "VARILLA POR METRO ZINC": "Varilla zincada por metro",
    "VARILLA POR 3 METROS ZINC": "Varilla zincada por 3 metros",
    "VARILLA POR METRO INOX": "Varilla inoxidable por metro",
    "CENTRAL": "Cabeza central",
    "TORNILLO JISS CABEZA CILINDRICA": "JIS cabeza cilíndrica",
    "TORNILLO JISS CABEZA PLANA": "JIS cabeza plana",
    "TORNILLOS ESTUFA CABEZA PLANA": "Estufa cabeza plana",
    "TORNILLO LAMINA CABEZA CILINDRICA PAVONADO": "Lámina cabeza cilíndrica",
    "TORNILLO LAMINA CABEZA HEXAGONAL PUNTA BROCA": "Lámina punta broca",
    "PIN CHAVETA": "Pin chaveta",
    "PIN SEGUER": "Pin seguer",
    "REMACHE POP": "Remache pop",
    "REMACHE POP ALA ANCHA": "Remache pop ala ancha",
    "CHAZO PLASTICO": "Chazo plástico",
    "HERRAMIENTA SATA": "Sata",
    "STANLEY": "Stanley",
    "FORCE": "Force",
    "TRUPER/PRETUL/PEGANTES": "Truper y Pretul",
    "BROCAS": "Brocas",
    "MACHOS": "Machos de roscar",
    "DISCOS DE CORTE": "Discos de corte",
    "TUERCAS HEXAGONAL MM CL 10 REX": "Métrica clase 10",
    "TUERCAS HEXAGONAL MM CL 8 REX": "Métrica clase 8",
    "TUERCA HEXAGONAL PULGADAS GR 2": "Pulgadas grado 2",
    "TUERCA HEXAGONAL PULGADAS GR 5": "Pulgadas grado 5",
    "TUERCA HEXAGONAL PULGADAS GR 8": "Pulgadas grado 8",
    "TUERCA HEX NYLON": "Seguridad con nylon",
    "TUERCA SEG STOVER REX": "Seguridad stover",
    "TUERCA HEXAGONAL ALTA REX": "Hexagonal alta",
    "TUERCA FLANGE REX": "Flange",
    "TUERCA FLANGE STOVER REX": "Flange stover",
    "TUERCA HEXAGONAL MILIMETRICA CLASE 8": "Métrica clase 8",
    "TUERCA HEXAGONAL MILIMETRICA CLASE 10.9": "Métrica clase 10",
    "TUERCA HEXAGONAL MILIMETRICA CLASE 6": "Métrica clase 6",
    "TUERCA HEXAGONAL GRADO 2 ZINC": "Pulgadas grado 2 zincada",
    "TUERCA HEXAGONAL GRADO 5 NEGRA": "Pulgadas grado 5",
    "TUERCA HEXAGONAL GRADO 8 NEGRA": "Pulgadas grado 8",
    "TUERCA HEXAGONAL INOX": "Inoxidable",
}


def grupo(sublinea, normalizador):
    """Nombre de grupo legible dentro de una linea."""
    clave = _t(sublinea)
    if clave in GRUPOS:
        return GRUPOS[clave]
    return normalizador(sublinea)
