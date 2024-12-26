# Module Imports
import mariadb
import sys
#한글 지원 방법
import os
class mariadb_conn():
    def __init__(self):
        os.putenv('NLS_LANG', '.UTF8')
# Connect to MariaDB Platform
        try:
            self.conn = mariadb.connect(
                        user="yeogak2024",
                        password="hanbisw",
                        host="43.202.210.216",
                        port=3306,
                        database="yeogak_db"
            # self.conn = mariadb.connect(
            #             user="yeogak2024",
            #             password="yeogak2024",
            #             host="192.168.0.20",
            #             port=3306,
            #             database="yeogak_db"

            )
        except mariadb.Error as e:
            print(f"Error connecting to MariaDB Platform: {e}")
            sys.exit(1)