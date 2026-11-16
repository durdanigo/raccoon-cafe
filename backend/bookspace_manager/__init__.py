# ============================================================
# Compatibilidad del conector MySQL (Fase 2)
# ------------------------------------------------------------
# Django usa por defecto el conector 'mysqlclient' (modulo MySQLdb).
# Si en Windows con Python 3.14 no se puede instalar mysqlclient,
# se instala PyMySQL y este bloque lo hace pasar por MySQLdb.
# Mientras se trabaja con SQLite (Fase 1) este bloque no hace nada.
# ============================================================
try:
    import MySQLdb  # noqa: F401  (mysqlclient disponible)
except ImportError:
    try:
        import pymysql

        pymysql.install_as_MySQLdb()
    except ImportError:
        pass
