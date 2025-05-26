from database.DB_connect import DBConnect
from model.state import State
from model.sighting import Sighting

class DAO:

    def __init__(self):
        pass

    @staticmethod
    def get_all_states():
        cnx = DBConnect.get_connection()
        result = []
        if cnx is None:
            print("Connessione fallita")
        else:
            cursor = cnx.cursor(dictionary=True)
            query = """select * 
                    from state s"""
            cursor.execute(query)

            for row in cursor:
                result.append(
                    State(row["id"],
                          row["Name"],
                          row["Capital"],
                          row["Lat"],
                          row["Lng"],
                          row["Area"],
                          row["Population"],
                          row["Neighbors"]))

            cursor.close()
            cnx.close()
        return result

    @staticmethod
    def get_all_sightings():
        cnx = DBConnect.get_connection()
        result = []
        if cnx is None:
            print("Connessione fallita")
        else:
            cursor = cnx.cursor(dictionary=True)
            query = """select * 
                    from sighting s 
                    order by `datetime` asc """
            cursor.execute(query)

            for row in cursor:
                result.append(Sighting(**row))
            cursor.close()
            cnx.close()
        return result

    @staticmethod
    def get_years():
        cnx = DBConnect.get_connection()
        result = []
        if cnx is None:
            print("Connessione fallita")
        else:
            cursor = cnx.cursor(dictionary=True)
            query = """SELECT DISTINCT YEAR(datetime) as anno 
                    FROM sighting s 
                    ORDER BY anno DESC"""
            cursor.execute(query)

            for row in cursor:
                result.append(row["anno"])

            cursor.close()
            cnx.close()
        return result

    @staticmethod
    def get_shapes_year(anno: int):
        cnx = DBConnect.get_connection()
        result = []
        if cnx is None:
            print("Connessione fallita")
        else:
            cursor = cnx.cursor(dictionary=True)
            query = """SELECT DISTINCT s.shape
                        FROM sighting s 
                        WHERE YEAR(s.datetime)=%s
                        ORDER BY shape ASC"""
            cursor.execute(query, (anno,))

            for row in cursor:
                if row["shape"] != "":
                    result.append(row["shape"])

            cursor.close()
            cnx.close()
        return result


    @staticmethod
    def get_nodes(year: int, shape: str):
        cnx = DBConnect.get_connection()
        result = []
        if cnx is None:
            print("Connessione fallita")
        else:
            cursor = cnx.cursor(dictionary=True)
            query = """SELECT *
                        FROM sighting s 
                        WHERE Year(s.datetime)=%s AND s.shape =%s
                        ORDER BY s.longitude ASC"""
            cursor.execute(query, (year, shape,))

            for row in cursor:
                result.append(Sighting(**row))

            cursor.close()
            cnx.close()
        return result


    @staticmethod
    def getEdges(year, shape, idMap):
        conn = DBConnect.get_connection()

        result = []

        cursor = conn.cursor(dictionary=True)
        query = """select t1.id as id1, abs(t1.longitude) as l1, t2.id as id2, abs(t2.longitude) as d2
                    from (select * from sighting s where YEAR(`datetime`) = %s and shape = %s) t1 ,
                    (select * from sighting s where YEAR(`datetime`) = %s and shape = %s) t2
                    where t1.state = t2.state and abs(t1.longitude) < abs(t2.longitude)
                    order by t1.longitude, t2.longitude"""

        cursor.execute(query, (year, shape, year, shape))

        for row in cursor:
            result.append((idMap[row['id1']], idMap[row['id2']]))

        cursor.close()
        conn.close()
        return result


    @staticmethod
    def getAllShapes():
        conn = DBConnect.get_connection()

        result = []

        cursor = conn.cursor(dictionary=True)
        query = """select distinct shape from sighting s 
                   where shape != "" """

        cursor.execute(query)

        for row in cursor:
            result.append(row['shape'])

        cursor.close()
        conn.close()
        return result