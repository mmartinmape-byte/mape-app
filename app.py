from flask import Flask, request, jsonify, render_template
from decimal import Decimal
import os, json

app = Flask(__name__)

DATABASE_URL = os.environ.get('DATABASE_URL', '')
USE_PG = bool(DATABASE_URL and 'postgres' in DATABASE_URL)


# ── DB helpers ────────────────────────────────────────────────────────────────

def fix(row):
    """Convierte Decimal a float para que jsonify serialice correctamente."""
    return {k: float(v) if isinstance(v, Decimal) else v for k, v in row.items()}

def get_conn():
    if USE_PG:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        conn = psycopg2.connect(DATABASE_URL)
        return conn, '%s', True
    else:
        import sqlite3
        conn = sqlite3.connect('mape.db')
        conn.row_factory = sqlite3.Row
        return conn, '?', False

def q(sql, params=None, fetch='all'):
    conn, ph, pg = get_conn()
    sql = sql.replace('?', ph)
    try:
        if pg:
            from psycopg2.extras import RealDictCursor
            cur = conn.cursor(cursor_factory=RealDictCursor)
        else:
            cur = conn.cursor()
        cur.execute(sql, params or ())
        if fetch == 'all':
            result = [fix(dict(r)) for r in cur.fetchall()]
        elif fetch == 'one':
            r = cur.fetchone()
            result = fix(dict(r)) if r else None
        elif fetch == 'id':
            if pg:
                r = cur.fetchone()
                result = dict(r)['id'] if r else None
            else:
                result = cur.lastrowid
        else:
            result = None
        conn.commit()
        return result
    finally:
        conn.close()

def run(sql, params=None):
    q(sql, params, fetch=None)


# ── Schema & seed ─────────────────────────────────────────────────────────────

PRODUCTS_SEED = [
    ("MESA PRINT",75325.26),("MESA FLAT",88096.53),("RESPALDO",63086),
    ("MESA RATONA FLAT SIMPLE",50843.58),("MESA RATONA FLAT DOBLE",69472.20),
    ("BARRA FLAT",90353.63),("BARRA PRINT 120",80724),("BARRA PRINT 140",85952),
    ("BANCO FLAT",45630.89),("BIBLIOTECA PRINT",100574.37),("RACK LCD FLAT",79532.67),
    ("RACK LCD DOBLE",120022),("BIBLIOTECA FLAT",108140.37),("MESA ENTRADA MATE SIMPLE",75049.89),
    ("BASE CRUZ",74778.80),("BASE CUBO 140",50518.40),("BASE CUBO 100",45174),
    ("ESCRITORIO FLAT 120",62844.80),("ESCRITORIO FLAT 140",64958.80),("ESCRITORIO PENCIL",64671.20),
    ("MESA RATONA MATE",70867.90),("MESA RATONA IRON",70867.90),("MESA ARRIME CHAPA LOW",34633.60),
    ("MESA ENTRADA MATE DOBLE",84774.80),("MESA DE LUZ MATE",71462),("BIBLIOTECA SLIM",86065.60),
    ("MESA DE ENTRADA WOOD",54122),("MESA RATONA BORDE",32329.60),("PERCHERO LISBOA",38058.40),
    ("MESA DE ARRIME MADERA",29456.80),("ESPEJO DE PIE AMADORA",44993.60),("MESA DE LUZ BLINK",32267.20),
    ("BIBLIOTECA SELVA",55358),("BASE RACK PANDORA",40473.60),("ZAPATERO TUBO",16078.80),
    ("PERCHERO SELVA",58430),("MESA CANDEL",101944),("MESA LITE 260x90",228748.80),
    ("BOTINERO WOOD 70X25X90H",66270.40),("BIBLIOTECA MATE",120387.20),("RACK MATE",166417),
    ("ZAPATERO LINE",15584),("VAJILLERO WOOD 74X32X180H",74976),("MESA DE ENTRADA NAZCA",75440.20),
    ("BIBLIOTECA LOCK",258972),("ESCRITORIO MIDLE 120X60X78H",76525.20),("ESCRITORIO CANDEL 140X60X75H",78144),
    ("PECHERO STAIR 50X160H",29105.68),("TOALLERO GROUND 60X25X100H",37986.40),("MESA RATONA CHAPA LOW",46581.40),
    ("MESA ENTRADA CHAPA LOW SIMPLE",42602.50),("MESA RATONA ROMA",26617.60),("MESA ARRIME ROMA",26560),
    ("MESA ENTRADA CHAPA LOW DOBLE",56584),("ZAPATERO ROMA",41442),("TOALLERO BANO IRON",35844),
    ("BIBLIOTECA ROMA",54664),("BASE SOMMIER IRON 80",71354),("BASE SOMMIER IRON 140",77769.60),
    ("BASE SOMMIER IRON 160",86842.40),("BASE SOMMIER IRON 180",89968),("BASE SOMMIER IRON 200",93754.40),
    ("ESTACION DE CAFE",42548),("ESCRITORIO ROMA 120X60",50262),
]

ORDERS_SEED = [
    ("2025-10-02","OC 14008 RESPALDO CAMA HIERRO 60X20 NEGRO 145X120",1,1,0,115000,None,""),
    ("2025-10-02","OC 14012 BASE ROCCO NEGRA",2,2,0,53854,None,""),
    ("2025-10-02","OC 14025 BASE ESCRITORIO PENCIL NEGRA",1,1,0,60442,None,""),
    ("2025-10-06","Banco armado",1,1,0,140000,None,""),
    ("2025-10-09","Base mesa de luz blink 50x35x40h Negro",2,2,0,89968,None,""),
    ("2025-10-09","Base cubo 140x40x20h Negro",1,1,0,38058.4,None,""),
    ("2025-10-09","Base cubo 100x40x20h Negro",1,1,0,44993.6,None,""),
    ("2025-10-09","Mesa de arrime madera Blanco",1,1,0,54664,None,""),
    ("2025-10-09","Mesa ratona chapa low Negro",10,10,0,0,None,""),
    ("2025-10-09","Mesa entrada chapa low doble Blanco",4,4,0,0,None,""),
    ("2025-10-09","Mesa entrada chapa low doble Negro",6,6,0,0,None,""),
    ("2025-10-14","Zapatero line Blanco",15,15,0,14261,None,""),
    ("2025-10-14","Zapatero line Negro",15,15,0,14261,None,""),
    ("2025-10-14","Mesa entrada chapa low Negro",5,5,0,38413,None,""),
    ("2025-10-30","Mesa print 135x80x75h Negro",2,2,0,75325.26,None,""),
    ("2025-10-30","Mesa print 135x80x75h Blanco",1,1,0,75325.26,None,""),
    ("2025-10-30","Estructura a medida 79x23x62h",1,1,0,38000,None,""),
    ("2025-10-30","Mesa arrime roma Negro",5,5,0,0,None,""),
    ("2025-10-30","Mesa ratona flat doble Negro",1,1,0,79532.67,None,""),
    ("2025-10-30","Escritorio flat 140x60x75h Blanco",1,1,0,16078.8,None,""),
    ("2025-10-30","Escritorio flat 140x60x75h Negro",1,1,0,16078.8,None,""),
    ("2025-10-30","Mesa de arrime madera Blanco",4,4,0,54664,None,""),
    ("2025-10-30","Mesa de arrime madera Negro",4,4,0,54664,None,""),
    ("2025-10-30","Mesa de entrada wood Negro",1,1,0,26617.6,None,""),
    ("2025-10-30","Mesa ratona borde Negro",5,5,0,56584,None,""),
    ("2025-10-30","Mesa ratona iron Negro",3,3,0,15584,None,""),
    ("2025-10-30","Base rocco Negro",4,4,0,26927.2,None,""),
    ("2025-10-30","Zapatero line triple Blanco",3,3,0,18000,None,""),
    ("2025-10-31","Zapatero line Negro",30,30,0,14261,None,""),
    ("2025-11-03","Porton 290x220",1,1,0,160000,None,""),
    ("2025-11-11","Zapatero line Blanco",15,15,0,14261,None,""),
    ("2025-11-11","Biblioteca slim Negra",2,2,0,151251.6,None,""),
    ("2025-11-11","Base cubo rack Negra",2,2,0,47160.4,None,""),
    ("2025-11-11","Base cubo rack 200x40x20h Negra",1,1,0,52000,None,""),
    ("2025-11-13","Mesa ratona low chapa Negra",14,14,0,51908.36,None,""),
    ("2025-11-13","Mesa ratona low chapa Blanca",12,12,0,51908.36,None,""),
    ("2025-11-20","Mesa de luz mate 45x30x50h Blanco",2,2,0,52400,None,""),
    ("2025-11-20","Mesa ratona mate Negro",6,6,0,68338,None,""),
    ("2025-11-20","Ratona iron low 50x50x40h Negra",1,1,0,40000,None,""),
    ("2025-11-21","Muestra organizaro toallas Negro",1,1,0,33500,None,""),
    ("2025-11-22","Muestra zapatero 66x25x60h Negro",1,1,0,35000,None,""),
    ("2025-11-22","Muestra zapatero 66x25x60h Blanco",1,1,0,35000,None,""),
    ("2025-12-01","Mesa arrime roma Negro",16,16,0,22096,None,""),
    ("2025-12-01","Mesa arrime roma Blanco",8,8,0,22096,None,""),
    ("2025-12-01","Base rocco Negro",4,4,0,26927.2,None,""),
    ("2025-12-01","Biblioteca selva Negro",2,2,0,80889,None,""),
    ("2025-12-01","Biblioteca selva Blanco",1,1,0,80889,None,""),
    ("2025-12-01","Escritorio flat 140 Negro",1,1,0,104764.8,None,""),
    ("2025-12-01","Zapatero line Negro",20,20,0,14261,None,""),
    ("2025-12-01","Mesa arrime chapa Negra",16,16,0,30942,None,""),
    ("2025-12-01","Mesa entrada chapa low doble Negro",4,4,0,51908.36,None,""),
    ("2025-12-01","Mesa entrada chapa low doble Blanco",4,4,0,51908.36,None,""),
    ("2025-12-16","Zapatero line blanco",20,20,0,14261,None,""),
    ("2025-12-16","Mesa arrime chapa Negra",16,16,0,30942,None,""),
    ("2025-12-16","Mesa arrime chapa Blanca",8,8,0,30942,None,""),
    ("2025-12-16","Mesa ratona chapa low Negro",10,10,0,42725,None,""),
    ("2025-12-16","Mesa ratona low chapa Blanca",5,5,0,42725,None,""),
    ("2025-12-16","Carro con 160x80",1,1,0,90000,None,""),
    ("2025-12-18","Biblioteca print Blanca 45cm distancia entre estantes",1,1,0,158000,None,""),
    ("2025-12-24","14527 Respaldo 140 N",1,1,0,101639,None,""),
    ("2025-12-24","Barra flat Negra",1,1,0,104685,None,""),
    ("2025-12-26","Base biblioteca roma Negra",1,1,0,52000,None,""),
    ("2025-12-29","Mesa ratona low chapa",20,20,0,42218,None,""),
    ("2025-12-29","Organizaro toallas Negro",10,10,0,33500,None,""),
    ("2025-12-29","Organizaro toallas Blanco",5,5,0,33500,None,""),
    ("2025-12-31","14564 Rack mate 210x30x60h Negro",1,1,0,200000,None,""),
    ("2025-12-31","14587 Toallero Ground negro",1,1,0,36740,None,""),
    ("2026-01-02","Estructura biblioteca roma negra",3,3,0,52000,None,""),
    ("2026-01-02","Estructura biblioteca roma blanca",3,3,0,52000,None,""),
    ("2026-01-07","Base cubo comoda blanca",2,2,0,42725,None,""),
    ("2026-01-07","Base cruz negra",2,2,0,74489.8,None,""),
    ("2026-01-07","Base cubo comoda negra",1,1,0,42725,None,""),
    ("2026-01-14","Base blink negra",6,6,0,26927,None,""),
    ("2026-01-14","Biblioteca selva negra",4,4,0,80889,None,""),
    ("2026-01-14","14636 Base para candel de 180x80 negra",1,1,0,110000,None,""),
    ("2026-01-14","146xx Perchero stair blanco",1,1,0,35000,None,""),
    ("2026-01-21","14643 Perchero stair negro",1,1,0,35000,None,""),
    ("2026-01-21","Biblioteca slim Negra",1,1,0,151251.6,None,""),
    ("2026-01-21","Biblioteca slim Blanca",1,1,0,151251.6,None,""),
    ("2026-01-21","14669 Base sommier iron negra",1,1,0,85000,None,""),
    ("2026-01-21","Zapatero line",20,20,0,14300,None,""),
    ("2026-01-21","Mesa ratona low",15,15,0,42218,None,""),
    ("2026-01-21","Mesa entrada low doble Negra",1,1,0,51908.36,None,""),
    ("2026-01-21","Mesa entrada low simple Negra",2,2,0,38413,None,""),
    ("2026-01-21","Mesa ratona low iron negra",3,2,1,37880,None,""),
    ("2026-01-21","Mesa ratona low iron blanca",2,2,0,37880,None,""),
    ("2026-02-11","Zapatero roma 66x25x62h Negro",2,2,0,35000,None,""),
    ("2026-02-11","Zapatero roma 66x25x62h Blanco",2,2,0,35000,None,""),
    (None,"Base mesa glass 130 Negra",1,1,0,25000,None,"xxxxx"),
    ("2026-02-11","14728 Mesa print 110x80x75h Negra",1,1,0,116900,None,""),
    ("2026-02-11","Base cruz negra",3,3,0,74489,None,""),
    ("2026-02-11","Base cruz blanca",3,3,0,74489,None,""),
    ("2026-02-11","Biblioteca print blanca",1,1,0,158054,None,""),
    ("2026-02-11","Biblioteca selva Blanco",1,1,0,80889,None,""),
    ("2026-02-11","Biblioteca slim Blanca",2,2,0,151251,None,""),
    ("2026-02-11","Mesa entrada mate negra",4,4,0,80998,None,""),
    ("2026-02-11","Base mesa candel Negra",1,1,0,85000,None,""),
    ("2026-02-11","Zapatero line",20,20,0,14300,None,""),
    (None,"Mesa entrada wood Negra",1,1,0,73977,None,"xxxx"),
    (None,"Base cubo rack Negra",1,1,0,47160.4,None,"xxxx"),
    ("2026-02-20","Base rocco Negro",4,4,0,26927,None,""),
    ("2026-02-24","14765 14767 Base sommier iron negro",2,2,0,85000,None,""),
    ("2026-02-24","Biblioteca slim blanca",1,1,0,151251,None,""),
    ("2026-02-24","Zapatero line",40,20,20,14300,None,""),
    ("2026-02-24","Mesa arrime low",15,15,0,30942,None,""),
    ("2026-02-24","Mesa entrada low simple Negra",2,2,0,38413,None,""),
    ("2026-02-24","Mesa ratona mate Negro",4,4,0,68338,None,""),
    ("2026-02-24","Estructura biblioteca roma negra",2,2,0,52000,None,""),
    ("2026-02-24","Juego patas mesa ratona roma Negra",8,4,4,22096,None,""),
    ("2026-02-24","Juego patas mesa ratona roma Blanca",7,5,2,22096,None,""),
    ("2026-02-24","Perchero toallero de pie Blanco",5,5,0,33500,None,""),
    ("2026-02-24","Perchero toallero de pie Negro",5,5,0,33500,None,""),
    ("2026-02-24","Perchero toallero de pie",10,10,0,33500,None,""),
    ("2026-03-12","Mesa ratona low",41,26,15,42218,None,""),
    ("2026-03-12","Zapatero triple line negro",3,0,3,18500,None,""),
    ("2026-03-12","Banco flat blanco",1,1,0,65225,None,""),
    ("2026-03-12","Barra flat negra",1,1,0,88500,None,""),
    ("2026-03-12","Base cruz negra",2,2,0,74489,None,""),
    ("2026-03-12","Base rocco Negro",4,4,0,26927,None,""),
    ("2026-03-12","Rack mate negro",1,1,0,175400,None,""),
    ("2026-03-16","Mesa print Negro",1,1,0,116981,None,""),
    ("2026-03-16","Escritorio flat 140 Negro",1,1,0,104764,None,""),
    ("2026-03-16","Mesa flat Negro",2,2,0,131259.77,None,""),
    ("2026-03-16","Mesa flat Blanco",2,2,0,131259.77,None,""),
    ("2026-03-16","Banco flat blanco",3,3,0,65225.99,None,""),
    ("2026-03-16","Banco flat negro",3,3,0,65225.99,None,""),
    ("2026-03-26","Mesa arrime low 77h Negro",1,1,0,30942,None,""),
    ("2026-03-26","Zapatero roma 66x25x62h Negro",4,4,0,34630,None,""),
    ("2026-03-26","Mesa entrada low simple Negra",5,5,0,38413,None,""),
    ("2026-03-26","Mesa entrada low simple Blanca",3,3,0,38413,None,""),
    ("2026-03-26","Perchero toallero de pie",20,20,0,33500,None,""),
    ("2026-03-26","Mesa arrime low",32,32,0,30942,None,""),
    ("2026-03-26","Biblioteca slim blanca",2,2,0,151251,None,""),
    ("2026-03-26","Rack LCD simple Blanco",1,1,0,121797,None,""),
    ("2026-03-26","Base cama iron 140x190 negra",1,1,0,85000,None,""),
    ("2026-03-26","Base cama iron 80x190 negra",2,2,0,75000,None,""),
    ("2026-04-06","Perchero stair 50x160h Negro",1,1,0,31778,None,""),
    ("2026-04-06","Perchero stair 50x160h Blanco",1,1,0,31778,None,""),
    ("2026-04-06","Mesa flat Negro",3,1,2,131259,None,""),
    ("2026-04-06","Mesa flat Blanco",1,1,0,131259,None,""),
    ("2026-04-06","Mesa candel Blanca",1,1,0,174024,None,""),
    ("2026-04-06","Mesa candel Negra",1,1,0,174024,None,""),
    ("2026-04-06","Mesa entrada mate negra",3,3,0,80998,None,""),
    ("2026-04-06","14898 Mesa ratona flat doble negra",1,1,0,121500,None,""),
    ("2026-04-06","14898 Mesa ratona flat doble 50x50x60h negra",1,1,0,100000,None,""),
    ("2026-04-12","14924 Mesa entrada mate doble 100x20x75h negra",1,1,0,80000,None,""),
    ("2026-04-12","14931 Mesa de luz mate 45x30x55h negra",10,10,0,52762,None,""),
    ("2026-04-12","14931 Mesa entrada mate doble 100x45x75h negra",5,5,0,82569,None,""),
    ("2026-04-12","Estructura estacion de cafe",2,2,0,35000,None,""),
    ("2026-04-22","14951 Mesa ratona flat doble Negro",1,1,0,64000,None,""),
    ("2026-04-22","14959 Mesa flat 150x80 Negro",1,1,0,84000,None,""),
    ("2026-04-22","14959 Mesa ratona flat simple 80x45 Negra",1,1,0,47300,None,""),
    ("2026-04-22","14963 Base Candel Negro",1,0,1,0,None,""),
    ("2026-04-22","14963 Base Candel Blanco",1,1,0,0,None,""),
    ("2026-04-22","14966 Biblioteca Roma 55x25x190h Negro",1,1,0,52000,None,""),
    ("2026-04-30","14978 Base escritorio Midel Negro",1,1,0,0,"2026-05-15",""),
    ("2026-04-30","14981 Mesa ratona mate Negro",5,5,0,0,None,""),
    ("2026-04-30","14982 Botinero wood Negro",1,1,0,0,"2026-05-15",""),
    ("2026-04-30","14989 Base cama iron 160x200 Negra",1,1,0,94000,"2026-05-15",""),
    ("2026-04-30","14991 Escritorio flat 180x60 Negro",1,1,0,85000,"2026-05-15",""),
    ("2026-04-30","14998 Escritorio flat 150x60 Negro",1,1,0,80000,"2026-05-15",""),
    ("2026-05-04","Base estacion de cafe Blancas",2,2,0,35000,None,""),
    ("2026-05-14","15019 Biblioteca print 100x30x210h Negras ver tamy",2,0,2,0,None,""),
    ("2026-05-14","15026 Biblioteca flat 55x30x180h (55cm) Negra",1,0,1,0,None,""),
    ("2026-05-14","15028 Toallero Ground Blanco",1,0,1,0,None,""),
    ("2026-05-14","15042 Mesa flat Negra",2,0,2,0,None,""),
    ("2026-05-14","15047 Barra flat 110x30x100h Blanca",1,0,1,0,None,""),
    ("2026-05-14","15049 Estructura estacion de cafe negra",2,0,2,0,None,""),
    ("2026-05-14","15051 Mesa print 150x80 Negra",1,0,1,0,None,""),
    ("2026-05-20","15069 Mesa ratona borde 150x50x54h Negro",1,0,1,0,None,""),
    ("2026-05-20","15070 Mesa print 100x70x75h Negro",1,0,1,0,None,""),
    ("2026-05-20","15070 Banco flat 92x35x45h Negro",1,0,1,0,None,""),
    ("2026-05-20","15073 Biblioteca lock 50x30x180h Negro",1,0,1,0,None,""),
    ("2026-05-20","15074 Mesa print Negro",1,0,1,0,None,""),
    ("2026-06-01","Estructura estacion de cafe negro",2,0,2,0,None,""),
    ("2026-06-01","15097 Rack LCD simple Negro",1,0,1,0,None,""),
    ("2026-06-01","15101 Base candel ver modelo con tamy Negro",1,0,1,0,None,""),
    ("2026-06-01","Zapatero roma Negro",6,0,6,0,None,""),
    ("2026-06-01","Zapatero roma Blanco",4,0,4,0,None,""),
    ("2026-06-01","Mesa arrime roma",10,0,10,0,None,""),
    ("2026-06-01","Base mesas 91x45 Negra",6,0,6,29500,None,""),
    ("2026-06-01","Base mesas 91x45 Blanca",4,0,4,29500,None,""),
    ("2026-06-01","Mesa arrime chapa",36,0,36,0,None,""),
]

ACCOUNT_SEED = [
    ("2025-10-09","Entregas fecha 9/10",None,200442),
    ("2025-10-18","Entregas fecha 18/10",None,115000),
    ("2025-10-20","Tender + set adhesivo bano negro",55000,None),
    ("2025-10-22","5 Placas paraiso",543906,None),
    ("2025-10-29","Entregas fecha 29/10",None,836118),
    ("2025-10-16","Transferencia",278100,None),
    ("2025-10-16","Transferencia",507680,None),
    ("2025-10-22","Entregas fecha 22/10",None,213915),
    ("2025-10-24","Entregas fecha 24/10",None,89885),
    ("2025-11-10","Pago a Matias Martin",2500000,None),
    ("2025-11-07","Entrega 7/11",None,160000),
    ("2025-11-10","Entregas 10/11",None,464689),
    ("2025-11-10","Pago Claro BHD",51311,None),
    ("2025-11-12","Silla escritorio",99000,None),
    ("2025-11-12","Cantos 2x22",70000,None),
    ("2025-11-17","Entrega 17/11",None,1865660),
    ("2025-11-18","Entrega 18/11",None,666859),
    ("2025-11-14","Entrega 14/11",None,116981),
    ("2025-11-25","Entrega 25/11",None,278308),
    ("2025-12-03","Entregas 3/12",None,447878),
    ("2025-12-04","Entrega 4/12",None,68338),
    ("2025-12-05","Pago a Matias Martin",2500000,None),
    ("2025-12-11","Entregas 11/12",None,68500),
    ("2025-12-16","Entrega 12/12",None,158338),
    ("2025-12-19","Entregas 19/12",None,567839),
    ("2025-12-22","Entregas 22/12",None,1105049),
    ("2025-12-26","Entregas 26/12",None,1201144),
    ("2025-12-30","Claro",26646,None),
    ("2025-12-30","Entregas 30/12",None,318720),
    ("2026-01-06","Pago a Matias Martin",2500000,None),
    ("2026-01-09","Entregas 9/1",None,296379),
    ("2026-01-13","Entregas 13/1",None,415264),
    ("2026-01-15","Gastos obra tigre MAPE",None,318000),
    ("2026-01-16","Entregas 16/1",None,1092250),
    ("2026-01-21","Pago Plegador",45000,None),
    ("2026-01-24","Entregas 24/1",None,1499965),
    ("2026-01-28","Claro",27675,None),
    ("2026-01-29","Entregas 29/1",None,145000),
    ("2026-01-31","Entregas 31/1",None,684757),
    ("2026-02-05","Entregas 5/2",None,1030124),
    ("2026-02-09","Pago Matias Martin",2500000,None),
    ("2026-02-11","Entregas 11/2",None,1322170),
    ("2026-02-24","Entregas 19/2",None,335000),
    ("2026-02-24","Entregas 24/2",None,981464),
    ("2026-02-27","Entregas 27/2",None,434662),
    ("2026-02-26","Transferencias clientes",100000,None),
    ("2026-02-28","Transferencias clientes",100000,None),
    ("2026-02-28","Transferencias clientes",50000,None),
    ("2026-03-02","Transferencias clientes",200000,None),
    ("2026-03-02","Transferencias clientes",50000,None),
    ("2026-03-02","Transferencias clientes",50000,None),
    ("2026-03-03","Sueldo Mati",2500000,None),
    ("2026-03-03","Cuenta Mati",450000,None),
    ("2026-03-05","Claro",59105,None),
    ("2026-03-03","Transferencias clientes",81438,None),
    ("2026-03-03","Transferencias clientes",15000,None),
    ("2026-03-03","Transferencias clientes",50000,None),
    ("2026-03-04","Transferencias clientes",1382500,None),
    ("2026-03-04","Transferencias clientes",50000,None),
    ("2026-03-04","Transferencias clientes",520000,None),
    ("2026-03-04","Entregas 4/3",None,456000),
    ("2026-03-10","Entregas 10/3",None,362929),
    ("2026-03-14","Entregas 14/3",None,102400),
    ("2026-03-18","Entregas 18/3",None,67600),
    ("2026-03-19","Entregas 19/3",None,502542),
    ("2026-03-19","Entregas 19/3 (2)",None,524308),
    ("2026-03-21","Entregas 21/3",None,196484),
    ("2026-03-23","Entregas 23/3",None,664593),
    ("2026-03-30","Cortes gustavo",14000,None),
    ("2026-04-06","Pago Matias Martin",2500000,None),
    ("2026-04-01","Entrega 1/4",None,484263),
    ("2026-04-02","Entrega 2/4",None,153609),
    ("2026-04-06","Entrega 6/4",None,517704),
    ("2026-04-14","Cortes gustavo",14000,None),
    ("2026-04-10","Entregas 10/4",None,410400),
    ("2026-04-13","Entregas 13/4",None,476468),
    ("2026-04-13","Transferencias clientes",150000,None),
    ("2026-04-13","Transferencias clientes",100000,None),
    ("2026-04-13","Transferencias clientes",100000,None),
    ("2026-04-14","Transferencias clientes",25860,None),
    ("2026-04-15","Transferencias clientes",230000,None),
    ("2026-04-15","Transferencias clientes",150000,None),
    ("2026-04-21","Entregas 21/4",None,377564),
    ("2026-04-25","Entregas 25/4",None,221500),
    ("2026-04-17","Transferencias clientes",50000,None),
    ("2026-04-18","Transferencias clientes",100000,None),
    ("2026-04-21","Transferencias clientes",100000,None),
    ("2026-04-24","Transferencias clientes",148826,None),
    ("2026-04-27","Entregas 27/4",None,492313),
    ("2026-04-27","Entregas 27/4 (2)",None,131259),
    ("2026-05-04","Entregas 4/5",None,496270),
    ("2026-05-07","Pago Matias Martin",3000000,None),
    ("2026-05-07","Placas pedidas a gustavo",229982,None),
    ("2026-05-11","Entregas 11/5",None,2472531),
    ("2026-05-11","Canto 1x22",33525,None),
    ("2026-05-15","Entregas 15/5",None,442300),
    ("2026-05-20","Entregas 20/5",None,1222652),
    ("2026-05-21","Entregas 21/5",None,844868),
    ("2026-05-28","Entregas 28/5",None,1060062),
    ("2026-05-22","Transferencias clientes",100000,None),
    ("2026-05-22","Transferencias clientes",100000,None),
    ("2026-05-22","Transferencias clientes",945000,None),
    ("2026-06-01","Compra Juan",179960,None),
]

def init_db():
    conn, ph, pg = get_conn()
    try:
        cur = conn.cursor()
        if pg:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS mape_products (
                    id SERIAL PRIMARY KEY,
                    nombre TEXT NOT NULL,
                    precio NUMERIC DEFAULT 0
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS mape_orders (
                    id SERIAL PRIMARY KEY,
                    fecha TEXT,
                    producto TEXT NOT NULL,
                    cantidad INTEGER NOT NULL DEFAULT 1,
                    entregado INTEGER DEFAULT 0,
                    pendiente INTEGER DEFAULT 0,
                    precio NUMERIC DEFAULT 0,
                    urgencia TEXT,
                    notas TEXT DEFAULT '',
                    fecha_esperada TEXT,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS mape_account (
                    id SERIAL PRIMARY KEY,
                    fecha TEXT NOT NULL,
                    detalle TEXT NOT NULL,
                    debita NUMERIC,
                    acredita NUMERIC,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
        else:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS mape_products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    precio REAL DEFAULT 0
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS mape_orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fecha TEXT,
                    producto TEXT NOT NULL,
                    cantidad INTEGER NOT NULL DEFAULT 1,
                    entregado INTEGER DEFAULT 0,
                    pendiente INTEGER DEFAULT 0,
                    precio REAL DEFAULT 0,
                    urgencia TEXT,
                    notas TEXT DEFAULT '',
                    fecha_esperada TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS mape_account (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fecha TEXT NOT NULL,
                    detalle TEXT NOT NULL,
                    debita REAL,
                    acredita REAL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
        conn.commit()

        # Seed if empty
        cur.execute("SELECT COUNT(*) FROM mape_products")
        r = cur.fetchone()
        count = r[0]
        if count == 0:
            for nombre, precio in PRODUCTS_SEED:
                cur.execute(f"INSERT INTO mape_products (nombre, precio) VALUES ({ph},{ph})", (nombre, precio))
            for row in ORDERS_SEED:
                cur.execute(f"""
                    INSERT INTO mape_orders (fecha,producto,cantidad,entregado,pendiente,precio,fecha_esperada,notas)
                    VALUES ({ph},{ph},{ph},{ph},{ph},{ph},{ph},{ph})
                """, row)
            for fecha, detalle, debita, acredita in ACCOUNT_SEED:
                cur.execute(f"INSERT INTO mape_account (fecha,detalle,debita,acredita) VALUES ({ph},{ph},{ph},{ph})",
                            (fecha, detalle, debita, acredita))
            conn.commit()
    finally:
        conn.close()


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')


# Products
@app.route('/api/products', methods=['GET'])
def get_products():
    return jsonify(q("SELECT * FROM mape_products ORDER BY nombre"))

@app.route('/api/products', methods=['POST'])
def create_product():
    d = request.json
    ph = '%s' if USE_PG else '?'
    rid = q(f"INSERT INTO mape_products (nombre, precio) VALUES ({ph},{ph}) {'RETURNING id' if USE_PG else ''}",
            (d['nombre'], d['precio']), fetch='id')
    return jsonify(q(f"SELECT * FROM mape_products WHERE id={ph}", (rid,), fetch='one'))

@app.route('/api/products/<int:pid>', methods=['PUT'])
def update_product(pid):
    d = request.json
    ph = '%s' if USE_PG else '?'
    run(f"UPDATE mape_products SET nombre={ph}, precio={ph} WHERE id={ph}", (d['nombre'], d['precio'], pid))
    return jsonify(q(f"SELECT * FROM mape_products WHERE id={ph}", (pid,), fetch='one'))

@app.route('/api/products/<int:pid>', methods=['DELETE'])
def delete_product(pid):
    ph = '%s' if USE_PG else '?'
    run(f"DELETE FROM mape_products WHERE id={ph}", (pid,))
    return jsonify({'ok': True})


# Orders
@app.route('/api/orders', methods=['GET'])
def get_orders():
    return jsonify(q("SELECT * FROM mape_orders ORDER BY id"))

@app.route('/api/orders', methods=['POST'])
def create_order():
    d = request.json
    ph = '%s' if USE_PG else '?'
    cantidad = d['cantidad']
    rid = q(f"""
        INSERT INTO mape_orders (fecha,producto,cantidad,entregado,pendiente,precio,urgencia,notas,fecha_esperada)
        VALUES ({ph},{ph},{ph},{ph},{ph},{ph},{ph},{ph},{ph}) {'RETURNING id' if USE_PG else ''}
    """, (d.get('fecha'), d['producto'], cantidad, 0, cantidad,
          d.get('precio', 0), d.get('urgencia'), d.get('notas',''), d.get('fechaEsperada')),
         fetch='id')
    return jsonify(q(f"SELECT * FROM mape_orders WHERE id={ph}", (rid,), fetch='one'))

@app.route('/api/orders/<int:oid>', methods=['PUT'])
def update_order(oid):
    d = request.json
    ph = '%s' if USE_PG else '?'
    cant = d['cantidad']
    entregado = d['entregado']
    pendiente = max(0, cant - entregado)
    run(f"""
        UPDATE mape_orders SET fecha={ph},producto={ph},cantidad={ph},entregado={ph},pendiente={ph},
        precio={ph},urgencia={ph},notas={ph},fecha_esperada={ph} WHERE id={ph}
    """, (d.get('fecha'), d['producto'], cant, entregado, pendiente,
          d.get('precio', 0), d.get('urgencia'), d.get('notas',''), d.get('fechaEsperada'), oid))
    return jsonify(q(f"SELECT * FROM mape_orders WHERE id={ph}", (oid,), fetch='one'))

@app.route('/api/orders/<int:oid>', methods=['DELETE'])
def delete_order(oid):
    ph = '%s' if USE_PG else '?'
    run(f"DELETE FROM mape_orders WHERE id={ph}", (oid,))
    return jsonify({'ok': True})


# Account
@app.route('/api/account', methods=['GET'])
def get_account():
    return jsonify(q("SELECT * FROM mape_account ORDER BY id"))

@app.route('/api/account', methods=['POST'])
def create_account():
    d = request.json
    ph = '%s' if USE_PG else '?'
    rid = q(f"INSERT INTO mape_account (fecha,detalle,debita,acredita) VALUES ({ph},{ph},{ph},{ph}) {'RETURNING id' if USE_PG else ''}",
            (d['fecha'], d['detalle'], d.get('debita'), d.get('acredita')), fetch='id')
    return jsonify(q(f"SELECT * FROM mape_account WHERE id={ph}", (rid,), fetch='one'))

@app.route('/api/account/<int:aid>', methods=['DELETE'])
def delete_account(aid):
    ph = '%s' if USE_PG else '?'
    run(f"DELETE FROM mape_account WHERE id={ph}", (aid,))
    return jsonify({'ok': True})


# Remito (composite)
@app.route('/api/remito', methods=['POST'])
def register_remito():
    d = request.json
    ph = '%s' if USE_PG else '?'
    items = d.get('items', [])  # [{orderId, cantidad}]
    fecha = d['fecha']
    monto = d.get('monto', 0)
    detalle = d.get('detalle', f"Entrega {fecha}")

    for item in items:
        oid = item['orderId']
        qty = item['cantidad']
        order = q(f"SELECT * FROM mape_orders WHERE id={ph}", (oid,), fetch='one')
        if not order:
            continue
        real = min(qty, order['pendiente'])
        new_entregado = order['entregado'] + real
        new_pendiente = max(0, order['pendiente'] - real)
        run(f"UPDATE mape_orders SET entregado={ph}, pendiente={ph} WHERE id={ph}",
            (new_entregado, new_pendiente, oid))

    if monto > 0:
        q(f"INSERT INTO mape_account (fecha,detalle,acredita) VALUES ({ph},{ph},{ph}) {'RETURNING id' if USE_PG else ''}",
          (fecha, detalle, monto), fetch='id')

    return jsonify({'ok': True})


if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5002)

init_db()
