import psycopg2
from django.contrib.sessions.backends.base import SessionBase, CreateError
import json
from datetime import datetime, timedelta

DB_CONFIG = {
    "host": "ep-winter-wildflower-a4ox1ffc-pooler.us-east-1.aws.neon.tech",
    "port": 5432,
    "dbname": "petclinic-b-07",
    "user": "neondb_owner",
    "password": "npg_wNGaE2ZkHv7M"
}
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'petclinic-b-07',  # Now working with a string
#         'USER': 'neondb_owner',
#         'PASSWORD': 'npg_wNGaE2ZkHv7M',
#         'HOST': 'ep-winter-wildflower-a4ox1ffc-pooler.us-east-1.aws.neon.tech',
#         'PORT': 5432,
#         'OPTIONS': {
#             'sslmode': 'require'
#         }
#     }
# }

def get_conn():
    return psycopg2.connect(**DB_CONFIG)

class SessionStore(SessionBase):
    def load(self):
        try:
            conn = get_conn()
            cur = conn.cursor()
            cur.execute("SET search_path TO pet_clinic;")

            cur.execute("SELECT session_data, expire_date FROM django_session WHERE session_key = %s", (self.session_key,))
            row = cur.fetchone()
            if row:
                session_data, expire_date = row
                if expire_date > datetime.now():
                    return self.decode(session_data)
            return {}
        finally:
            cur.close()
            conn.close()

    def create(self):
        while True:
            self._session_key = self._get_new_session_key()
            try:
                self.save(must_create=True)
            except CreateError:
                # collision, try again
                continue
            self.modified = True
            return

    def save(self, must_create=False):
        if not self.session_key:
            self._session_key = self._get_new_session_key()  # generate session_key baru
        
        session_data = self.encode(self._get_session(no_load=must_create))
        expire_date = datetime.now() + timedelta(seconds=self.get_expiry_age())

        conn = get_conn()
        cur = conn.cursor()
        try:
            cur.execute("SET search_path TO pet_clinic;")

            if must_create:
                cur.execute("INSERT INTO django_session (session_key, session_data, expire_date) VALUES (%s, %s, %s)",
                            (self.session_key, session_data, expire_date))
            else:
                cur.execute("""
                    INSERT INTO django_session (session_key, session_data, expire_date)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (session_key) DO UPDATE SET session_data = EXCLUDED.session_data, expire_date = EXCLUDED.expire_date
                """, (self.session_key, session_data, expire_date))
            conn.commit()
        finally:
            cur.close()
            conn.close()

    def exists(self, session_key):
        conn = get_conn()
        cur = conn.cursor()
        try:
            cur.execute("SET search_path TO pet_clinic;")
            cur.execute("SELECT 1 FROM django_session WHERE session_key = %s", (session_key,))
            return cur.fetchone() is not None
        finally:
            cur.close()
            conn.close()

    def delete(self, session_key=None):
        if session_key is None:
            session_key = self.session_key
        conn = get_conn()
        cur = conn.cursor()
        try:            
            cur.execute("SET search_path TO pet_clinic;")
            cur.execute("DELETE FROM django_session WHERE session_key = %s", (session_key,))
            conn.commit()
        finally:
            cur.close()
            conn.close()
