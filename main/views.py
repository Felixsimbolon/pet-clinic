from django.contrib import messages
from .forms import RegisterIndividuForm, RegisterFrontDeskForm, RegisterDokterForm, RegisterPerawatForm, RegisterPerusahaanForm
from datetime import *
import uuid, re
from datetime import datetime, time
from django.shortcuts import render, redirect
from django.db import connection, transaction, IntegrityError
from psycopg2           import errors as pg_err          # akses kelas-kelas error PG



EMAIL_REGEX         = re.compile(r'^[\w\.-]+@[\w\.-]+\.[A-Za-z]{2,}$')
PHONE_REGEX         = re.compile(r'^0\d{1,15}$')  
DATE_REGEX          = re.compile(r'^\d{4}-\d{2}-\d{2}$')
PASSWORD_REGEX      = re.compile(
    r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
)
# Alamat: huruf, angka, spasi, koma, titik, strip, slash
ALAMAT_REGEX        = re.compile(r'^[\w0-9\s\.,\-\/]+$')

def landing_page(request):
    return render(request, 'landing.html')

def login_view(request):
    
    if request.method == 'POST':
        email = request.POST.get('email').strip().lower()
        password = request.POST.get('password')

        with connection.cursor() as cursor:
            cursor.execute("SET search_path TO pet_clinic;")

            # Cek apakah email ada dan password cocok
            cursor.execute("""
                SELECT email, password
                FROM "USER"
                WHERE email = %s
            """, (email,))
            user = cursor.fetchone()
            
            if user :
                request.session['user_email'] = email  # simpan user identifier di session
                request.session.set_expiry(60 * 60 * 24 * 365 * 10)  # session tahan lama (10 tahun)
                # Email dan password cocok
                # Sekarang cek role pengguna
                cursor.execute("SET search_path TO pet_clinic;")
                cursor.execute("""
                    SELECT no_dokter_hewan
                    FROM DOKTER_HEWAN
                    WHERE no_dokter_hewan = (
                        SELECT no_pegawai FROM PEGAWAI WHERE email_user = %s
                    )
                """, [email])
                dokter = cursor.fetchone()

                if dokter:
                    # Kalau dokter
                    
                    return redirect('dashboard_dokter')
                
                cursor.execute("SET search_path TO pet_clinic;")
                cursor.execute("""
                    SELECT no_perawat_hewan
                    FROM PERAWAT_HEWAN
                    WHERE no_perawat_hewan = (
                        SELECT no_pegawai FROM PEGAWAI WHERE email_user = %s
                    )
                """, [email])
                perawat = cursor.fetchone()

                if perawat:
                    # Kalau perawat
                    return redirect('dashboard_perawat')

                cursor.execute("SET search_path TO pet_clinic;")
                cursor.execute("""
                    SELECT no_front_desk
                    FROM FRONT_DESK
                    WHERE no_front_desk = (
                        SELECT no_pegawai FROM PEGAWAI WHERE email_user = %s
                    )
                """, [email])
                frontdesk = cursor.fetchone()

                if frontdesk:
                    # Kalau front-desk
                    return redirect('dashboard_frontdesk')

                # Kalau bukan PEGAWAI, berarti KLIEN
                cursor.execute("SET search_path TO pet_clinic;")
                cursor.execute("""
                    SELECT no_identitas
                    FROM KLIEN
                    WHERE email = %s
                """, [email])
                klien = cursor.fetchone()

                if klien:
                    return redirect('dashboard_klien')

                else:
                    messages.error(request, "Akun tidak dikenali sebagai Dokter, Perawat, Frontdesk, atau Klien.")
                    return redirect('login')

            else:
                # Email/password tidak cocok
                messages.error(request, "Email atau Password salah.")
                return redirect('login')

    return render(request, 'login.html')

def register_view(request):
    return render(request, 'register.html')

def register_individu(request):
    errors = {}
    data = {}

    if request.method == 'POST':
        # Ambil data
        data['email']          = request.POST.get('email', '').strip().lower()
        data['nama_depan']     = request.POST.get('nama_depan', '').strip()
        data['nama_tengah']    = request.POST.get('nama_tengah', '').strip()
        data['nama_belakang']  = request.POST.get('nama_belakang', '').strip()
        data['password']       = request.POST.get('password', '')
        data['nomor_telepon']  = request.POST.get('nomor_telepon', '').strip()
        data['alamat']         = request.POST.get('alamat', '').strip()

        #----------- EMAIL ------------------
        if not data['email']:
            errors['email'] = 'Email wajib diisi'
        elif not EMAIL_REGEX.match(data['email']):
            errors['email'] = 'Format email tidak valid'
        elif len(data['email']) > 50:
            errors['email'] = 'Email maksimal 50 karakter'
      

        # Validasi nama
        if not data['nama_depan']:
            errors['nama_depan'] = 'Nama depan wajib diisi'
        elif len(data['nama_depan']) > 50:
            errors['nama_depan'] = 'Nama depan Maksimal 50 Karakter'
            
        if data['nama_tengah'] and len(data['nama_tengah']) > 50:
            errors['nama_tengah'] = 'Nama tengah Maksimal 50 Karakter'
            
        if not data['nama_belakang']:
            errors['nama_belakang'] = 'Nama belakang wajib diisi'
        elif len(data['nama_belakang']) > 50:
            errors['nama_belakang'] = 'Nama belakang Maksimal 50 Karakter'

        #----------- PASSWORD ------------------
        if not data['password']:
            errors['password'] = 'Password wajib diisi'
        elif len(data['password']) > 100:
            errors['password'] = 'Password maksimal 100 karakter'

        #----------- Nomor Telpon ------------------
        if not data['nomor_telepon']:
            errors['nomor_telepon'] = 'Nomor telepon wajib diisi'
        elif not PHONE_REGEX.match(data['nomor_telepon']):
            errors['nomor_telepon'] = 'Format nomor telepon tidak valid'
        elif len(data['nomor_telepon']) > 15:
            errors['nomor_telepon'] = 'Nomor telepon maksimal 15 digit'

        # Validasi alamat
        if not data['alamat']:
            errors['alamat'] = 'Alamat wajib diisi'

        # Jika tidak ada error, simpan
        if not errors:
            id_klien = uuid.uuid4()
            today = date.today()
            try:
                with transaction.atomic():
                    with connection.cursor() as cursor:
                        # Simpan ke tabel USER
                        cursor.execute("SET search_path TO pet_clinic;")
                        cursor.execute(
                            '''
                            INSERT INTO "USER"
                            (email, password, nomor_telepon, alamat)
                            VALUES (%s, %s, %s, %s)
                            ''',
                            [
                                data['email'], data['password'], data['nomor_telepon'],
                                data['alamat']
                            ]
                        )

                        # Simpan ke tabel KLIEN_INDIVIDU
                        cursor.execute(
                            '''
                            INSERT INTO KLIEN
                            (no_identitas, tanggal_registrasi, email)
                            VALUES (%s, %s, %s)
                            ''',
                            [str(id_klien), today,data['email']]
                        )
                        cursor.execute(
                            '''
                            INSERT INTO INDIVIDU
                            (no_identitas_klien, nama_depan, nama_tengah,nama_belakang)
                            VALUES (%s, %s, %s, %s)
                            ''',
                            [str(id_klien), data['nama_depan'] , data['nama_tengah'],data['nama_belakang']  ]
                        )

                    return redirect('login')
            except IntegrityError as exc:
                root = exc.__cause__
                if isinstance(root, pg_err.UniqueViolation) and 'email' in str(root):
                    # pesan dikirim dari trigger PL/pgSQL
                    errors['email'] = str(root).split('CONTEXT:')[0].strip()
                else:
                    errors['db'] = 'Terjadi kesalahan database, coba lagi.'

    return render(request, 'register_individu.html', {
        'errors': errors,
        'data': data
    })

def register_perusahaan(request):
    data = {}
    errors = {}
    days = ['Senin','Selasa','Rabu','Kamis','Jumat','Sabtu','Minggu']

    if request.method == 'POST':
        data['email'] = request.POST.get('email', '').strip().lower()
        data['nama_perusahaan'] = request.POST.get('nama_perusahaan', '').strip()
        data['password'] = request.POST.get('password', '')
        data['nomor_telepon'] = request.POST.get('nomor_telepon', '').strip()
        data['alamat'] = request.POST.get('alamat', '').strip()


        # Validasi Nama Perusahaan
        if not data['nama_perusahaan']:
            errors['nama_perusahaan'] = 'Nama perusahaan wajib diisi'
        elif len(data['nama_perusahaan']) > 100:
            errors['nama_perusahaan'] = 'Nama perusahaan maksimal 100 karakter'
            
        #----------- Nomor Telpon ------------------
        if not data['nomor_telepon']:
            errors['nomor_telepon'] = 'Nomor telepon wajib diisi'
        elif not PHONE_REGEX.match(data['nomor_telepon']):
            errors['nomor_telepon'] = 'Format nomor telepon tidak valid'
        elif len(data['nomor_telepon']) > 15:
            errors['nomor_telepon'] = 'Nomor telepon maksimal 15 digit'
       
        #----------- EMAIL ------------------
        if not data['email']:
            errors['email'] = 'Email wajib diisi'
        elif not EMAIL_REGEX.match(data['email']):
            errors['email'] = 'Format email tidak valid'
        elif len(data['email']) > 50:
            errors['email'] = 'Email maksimal 50 karakter'

        #----------- PASSWORD ------------------
        if not data['password']:
            errors['password'] = 'Password wajib diisi'
        elif len(data['password']) > 100:
            errors['password'] = 'Password maksimal 100 karakter'

        #----------- ALAMAT  ------------------
        if not data['alamat']:
            errors['alamat'] = 'Alamat wajib diisi'


        # Validasi Password
        if not data['email']:
            errors['email'] = 'Email wajib diisi'
        elif not EMAIL_REGEX.match(data['email']):
            errors['email'] = 'Format email tidak valid'

        # Validasi nomor telepon
        if not data['nomor_telepon']:
            errors['nomor_telepon'] = 'Nomor telepon wajib diisi' 
        elif not PHONE_REGEX.match(data['nomor_telepon']):
            errors['nomor_telepon'] = 'Nomor telepon harus diawali 0 dan 10–15 digit'
        if 'nomor_telepon' not in errors:
            with connection.cursor() as cursor:
                cursor.execute("SET search_path TO pet_clinic;")
                cursor.execute(
                    'SELECT COUNT(*) FROM "USER" WHERE nomor_telepon = %s',
                    [data['nomor_telepon']]
                )
                count = cursor.fetchone()[0]
            if count:
                errors['nomor_telepon'] = 'Nomor telepon sudah terdaftar'
                
        # Validasi password
        if not data['password']:
            errors['password'] = 'Password wajib diisi'
        elif not PASSWORD_REGEX.match(data['password']):
            errors['password'] = (
                'Password minimal 8 karakter, '
                'mengandung huruf besar, huruf kecil, angka, dan simbol'
            )

        # Validasi alamat
        if not data['alamat']:
            errors['alamat'] = 'Alamat wajib diisi'
            
        elif not ALAMAT_REGEX.match(data['alamat']):
            errors['alamat'] = 'Alamat mengandung karakter tidak diperbolehkan'
        
        if not errors:
            today = date.today()
            no_identitas_klien = uuid.uuid4()
            try:
                with transaction.atomic():
                    with connection.cursor() as cursor:
                        cursor.execute("SET search_path TO pet_clinic;")
                        # Simpan USER
                        cursor.execute(
                            '''INSERT INTO "USER" ( email, password, alamat,nomor_telepon)
                            VALUES (%s, %s, %s, %s)''',
                            [data['email'], data['password'],data['alamat'], data['nomor_telepon']]
                        )

                        # Simpan KLIEN (dengan tanggal_mulai_kerja = hari ini, dan tanggal_diterima)
                        cursor.execute(
                            '''
                            INSERT INTO KLIEN
                            (no_identitas, tanggal_registrasi, email)
                            VALUES (%s, %s, %s)
                            ''',
                            [str(no_identitas_klien), today,data['email']]
                        )

                        # Simpan FRONT_DESK
                        cursor.execute(
                            '''INSERT INTO PERUSAHAAN (no_identitas_klien,nama_perusahaan)
                            VALUES (%s,%s)''',
                            [str(no_identitas_klien),data['nama_perusahaan']]
                        )
                return redirect('login')
            except IntegrityError as exc:
                root = exc.__cause__
                if isinstance(root, pg_err.UniqueViolation) and 'email' in str(root):
                    # pesan dikirim dari trigger PL/pgSQL
                    errors['email'] = str(root).split('CONTEXT:')[0].strip()
                else:
                    errors['db'] = 'Terjadi kesalahan database, coba lagi.'

    return render(request, 'register_perusahaan.html', {
        'data': data,
        'errors': errors,
        'days' : days
    })




def register_frontdesk(request):
    errors = {}
    data = {}
    if request.method == 'POST':
        data['email']            = request.POST.get('email', '').strip().lower()
        data['nomor_telepon']    = request.POST.get('nomor_telepon', '').strip()
        data['tanggal_diterima'] = request.POST.get('tanggal_diterima', '').strip()
        data['password']         = request.POST.get('password', '')
        data['alamat']           = request.POST.get('alamat', '').strip()

        #----------- EMAIL ------------------
        if not data['email']:
            errors['email'] = 'Email wajib diisi'
        elif not EMAIL_REGEX.match(data['email']):
            errors['email'] = 'Format email tidak valid'
        elif len(data['email']) > 50:
            errors['email'] = 'Email maksimal 50 karakter'
    

        #----------- PASSWORD ------------------
        if not data['password']:
            errors['password'] = 'Password wajib diisi'
        elif len(data['password']) > 100:
            errors['password'] = 'Password maksimal 100 karakter'

        #----------- Nomor Telpon ------------------
        if not data['nomor_telepon']:
            errors['nomor_telepon'] = 'Nomor telepon wajib diisi'
        elif not PHONE_REGEX.match(data['nomor_telepon']):
            errors['nomor_telepon'] = 'Format nomor telepon tidak valid'
        elif len(data['nomor_telepon']) > 15:
            errors['nomor_telepon'] = 'Nomor telepon maksimal 15 digit'

        # Validasi alamat
        if not data['alamat']:
            errors['alamat'] = 'Alamat wajib diisi'


        # Validasi tanggal diterima
        if not data['tanggal_diterima']:
            errors['tanggal_diterima'] = 'Tanggal diterima wajib diisi'
        try:
            tgl_diterima = datetime.strptime(data['tanggal_diterima'], '%Y-%m-%d').date()
        except (ValueError, TypeError):
            errors['tanggal_diterima'] = 'Tanggal diterima wajib & formatnya yyyy-mm-dd'

        # Validasi password

        # Jika valid, simpan
        if not errors:
            id_pegawai = uuid.uuid4()
            tgl_diterima = data['tanggal_diterima'] 
            
            try:
                with transaction.atomic():

                    with connection.cursor() as cursor:
                        cursor.execute("SET search_path TO pet_clinic;")
        
                        # Simpan USER
                        cursor.execute(
                            '''INSERT INTO "USER" ( email, password, alamat,nomor_telepon)
                            VALUES (%s, %s, %s, %s)''',
                            [data['email'], data['password'],data['alamat'], data['nomor_telepon']]
                        )

                        # Simpan PEGAWAI (dengan tanggal_mulai_kerja = hari ini, dan tanggal_diterima)
                        cursor.execute(
                            '''INSERT INTO PEGAWAI
                            (no_pegawai, tanggal_mulai_kerja, email_user)
                            VALUES (%s, %s, %s)''',
                            [str(id_pegawai),  tgl_diterima, data['email']]
                        )

                        # Simpan FRONT_DESK
                        cursor.execute(
                            '''INSERT INTO FRONT_DESK (no_front_desk)
                            VALUES (%s)''',
                            [str(id_pegawai)]
                        )
                            
                return redirect('login')

            except IntegrityError as exc:
                root = exc.__cause__
                if isinstance(root, pg_err.UniqueViolation) and 'email' in str(root):
                    # pesan dikirim dari trigger PL/pgSQL
                    errors['email'] = str(root).split('CONTEXT:')[0].strip()
                else:
                    errors['db'] = 'Terjadi kesalahan database, coba lagi.'


    return render(request, 'register_frontdesk.html', {
        'errors': errors,
        'data': data
    })




from django.contrib.auth.hashers import make_password


def register_dokter(request):
    days   = ['Senin','Selasa','Rabu','Kamis','Jumat','Sabtu','Minggu']
    errors = {}
    data   = {}

    if request.method == 'POST':
        # ---------- FIELD UMUM ----------
        for f in ['izin_praktik','nomor_telepon','email','password',
                  'tanggal_diterima','alamat']:
            if f == 'email':
                data[f] = request.POST.get(f,'').strip().lower()
            else:
                data[f] = request.POST.get(f,'').strip()
        # ---------- FIELD DINAMIS ----------
        nos   = request.POST.getlist('nomor_sertifikat[]')
        nms   = request.POST.getlist('nama_sertifikat[]')
        hari  = request.POST.getlist('hari_praktik[]')
        jm1   = request.POST.getlist('jam_mulai[]')
        jm2   = request.POST.getlist('jam_selesai[]')

        certificates = [
            {'nomor': n.strip(), 'nama': m.strip()}
            for n, m in zip(nos, nms) if n.strip() or m.strip()
        ] or [{}]

        schedules = [
            {'hari': h.strip(), 'jam_mulai': j1.strip(), 'jam_selesai': j2.strip()}
            for h, j1, j2 in zip(hari, jm1, jm2) if h.strip() or j1.strip() or j2.strip()
        ] or [{}]

        data.update({'certificates': certificates, 'schedules': schedules})

        # ---------- VALIDASI FIELD UMUM ----------------------------
        #----------- IZIN PRAKTIK ------------------
        if not data['izin_praktik']:
            errors['izin_praktik'] = 'Nomor izin praktik wajib diisi'
        elif len(data['izin_praktik']) > 20:
            errors['izin_praktik'] = 'No. izin praktik maksimal 20 karakter'
        else:
            with connection.cursor() as cur:
                
                cur.execute("SET search_path TO pet_clinic;")
                cur.execute('SELECT 1 FROM TENAGA_MEDIS WHERE no_izin_praktik = %s',
                            [data['izin_praktik']])
                if cur.fetchone():
                    errors['izin_praktik'] = 'Nomor izin praktik sudah terpakai'
            
        #----------- Nomor Telpon ------------------
        if not data['nomor_telepon']:
            errors['nomor_telepon'] = 'Nomor telepon wajib diisi'
        elif not PHONE_REGEX.match(data['nomor_telepon']):
            errors['nomor_telepon'] = 'Format nomor telepon tidak valid'
        elif len(data['nomor_telepon']) > 15:
            errors['nomor_telepon'] = 'Nomor telepon maksimal 15 digit'
       
        #----------- EMAIL ------------------
        if not data['email']:
            errors['email'] = 'Email wajib diisi'
        elif not EMAIL_REGEX.match(data['email']):
            errors['email'] = 'Format email tidak valid'
        elif len(data['email']) > 50:
            errors['email'] = 'Email maksimal 50 karakter'

        #----------- PASSWORD ------------------
        if not data['password']:
            errors['password'] = 'Password wajib diisi'
        elif len(data['password']) > 100:
            errors['password'] = 'Password maksimal 100 karakter'
            
        #----------- TANGGAL DITERIMA ------------------
        if not data['tanggal_diterima']:
            errors['tanggal_diterima'] = 'Tanggal diterima wajib diisi'
        try:
            tgl_diterima = datetime.strptime(data['tanggal_diterima'], '%Y-%m-%d').date()
        except (ValueError, TypeError):
            errors['tanggal_diterima'] = 'Tanggal diterima wajib & formatnya yyyy-mm-dd'
        #----------- ALAMAT  ------------------
        if not data['alamat']:
            errors['alamat'] = 'Alamat wajib diisi'

        # ---------- VALIDASI SERTIFIKAT ----------
        seen_cert = set()

        if not certificates or all(not c.get('nomor') and not c.get('nama') for c in certificates):
            errors['sertifikat'] = 'Tambahkan minimal satu sertifikat'
        else:
            for c in certificates:
                if not (c.get('nomor') and c.get('nama')):
                    errors['sertifikat'] = 'Setiap sertifikat harus berisi nomor & nama'
                    break
                else:
                    if len(c['nomor']) > 10:
                        errors['sertifikat'] = 'Nomor sertifikat max 10 karakter'
                        break
                    if len(c['nama']) > 100:
                        errors['sertifikat'] = 'Nama sertifikat max 100 karakter'
                        break
                    tup = (c['nomor'])
                    if tup in seen_cert:
                        errors['sertifikat'] = 'Duplikasi sertifikat pada form'
                        break
                    seen_cert.add(tup)

        # ---------- VALIDASI JADWAL ----------
        seen_slot = set()
        if not schedules or all(not s.get('hari') and not s.get('jam_mulai') and not s.get('jam_selesai') for s in schedules):
            errors['jadwal'] = 'Tambahkan minimal satu jadwal praktik'
        else:
            for s in schedules:
                print(s.get('hari'),s.get('jam_mulai') ,s.get('jam_selesai'))
                if not (s.get('hari') and s.get('jam_mulai') and s.get('jam_selesai')):
                    errors['jadwal'] = 'Setiap jadwal harus lengkap (hari, jam mulai, jam selesai)'
                    break
                if s.get('jam_selesai') <= s.get('jam_mulai'):
                    errors['jadwal'] = 'Jam selesai harus setelah jam mulai'
                    break
                else:
                    if s['hari'] not in days:
                        errors['jadwal'] = 'Hari praktik tidak valid'
                        break
                    slot_key = (s['hari'], s['jam_mulai'], s['jam_selesai'])
                    if slot_key in seen_slot:
                        errors['jadwal'] = 'Duplikasi jadwal di form'
                        break
                    seen_slot.add(slot_key)
                
 
        # ---------- SIMPAN ----------
        if not errors:
            no_doc   = str(uuid.uuid4())
            try:
                with transaction.atomic():
                    with connection.cursor() as cur:
                        cur.execute("SET search_path TO pet_clinic;")

                        # USER
                        cur.execute("""
                            INSERT INTO "USER"(email,password,nomor_telepon,alamat)
                            VALUES (%s,%s,%s,%s)
                        """, [data['email'], data['password'], data['nomor_telepon'], data['alamat']])
                        
                        cur.execute("""
                            INSERT INTO PEGAWAI(no_pegawai,tanggal_mulai_kerja,email_user)
                            VALUES (%s,%s,%s)
                        """, [no_doc, tgl_diterima, data['email']])
                        
                        # TENAGA_MEDIS
                        cur.execute("""
                            INSERT INTO TENAGA_MEDIS(no_tenaga_medis,no_izin_praktik)
                            VALUES (%s,%s)
                        """, [no_doc, data['izin_praktik']])
                        
                        # DOKTER_HEWAN
                        cur.execute("""
                            INSERT INTO DOKTER_HEWAN(no_dokter_hewan)
                            VALUES (%s)
                        """, [no_doc])

                        # SERTIFIKAT
                        for c in certificates:
                            cur.execute("""
                                INSERT INTO SERTIFIKAT_KOMPETENSI(no_tenaga_medis,no_sertifikat_kompetensi,nama_sertifikat)
                                VALUES (%s,%s,%s)
                            """, [no_doc, c['nomor'], c['nama']])

                        # JADWAL
                        for s in schedules:
                            cur.execute("""
                                INSERT INTO JADWAL_PRAKTIK(no_dokter_hewan,hari,jam)
                                VALUES (%s,%s,%s)
                            """, [no_doc, s['hari'], s['jam_mulai'] + "-" +s['jam_selesai']])


                    return redirect('login')   # sukses
            except IntegrityError as exc:
                root = exc.__cause__
                if isinstance(root, pg_err.UniqueViolation) and 'email' in str(root):
                    # pesan dikirim dari trigger PL/pgSQL
                    errors['email'] = str(root).split('CONTEXT:')[0].strip()
                else:
                    errors['db'] = 'Terjadi kesalahan database, coba lagi.'

    else:
        data['certificates'] = [{}]
        data['schedules']    = [{}]

    return render(request, 'register_dokter.html', {
        'data': data, 'errors': errors, 'days': days,
    })


def register_perawat(request):
    errors = {}
    data   = {}

    if request.method == 'POST':
        # ---------- FIELD UMUM ----------
        for f in ['izin_praktik','nomor_telepon','email','password',
                  'tanggal_diterima','alamat']:
            if f == 'email':
                data[f] = request.POST.get(f,'').strip().lower()
            else:
                data[f] = request.POST.get(f,'').strip()

        # ---------- FIELD DINAMIS ----------
        nos   = request.POST.getlist('nomor_sertifikat[]')
        nms   = request.POST.getlist('nama_sertifikat[]')

        certificates = [
            {'nomor': n.strip(), 'nama': m.strip()}
            for n, m in zip(nos, nms) if n.strip() or m.strip()
        ] or [{}]

        data.update({'certificates': certificates})

        # ---------- VALIDASI FIELD UMUM ----------------------------
        #----------- IZIN PRAKTIK ------------------
        if not data['izin_praktik']:
            errors['izin_praktik'] = 'Nomor izin praktik wajib diisi'
        elif len(data['izin_praktik']) > 20:
            errors['izin_praktik'] = 'No. izin praktik maksimal 20 karakter'
        else:
            with connection.cursor() as cur:
                
                cur.execute("SET search_path TO pet_clinic;")
                cur.execute('SELECT 1 FROM TENAGA_MEDIS WHERE no_izin_praktik = %s',
                            [data['izin_praktik']])
                if cur.fetchone():
                    errors['izin_praktik'] = 'Nomor izin praktik sudah terpakai'
            
        #----------- Nomor Telpon ------------------
        if not data['nomor_telepon']:
            errors['nomor_telepon'] = 'Nomor telepon wajib diisi'
        elif not PHONE_REGEX.match(data['nomor_telepon']):
            errors['nomor_telepon'] = 'Format nomor telepon tidak valid'
        elif len(data['nomor_telepon']) > 15:
            errors['nomor_telepon'] = 'Nomor telepon maksimal 15 digit'
       
        #----------- EMAIL ------------------
        if not data['email']:
            errors['email'] = 'Email wajib diisi'
        elif not EMAIL_REGEX.match(data['email']):
            errors['email'] = 'Format email tidak valid'
        elif len(data['email']) > 50:
            errors['email'] = 'Email maksimal 50 karakter'

        #----------- PASSWORD ------------------
        if not data['password']:
            errors['password'] = 'Password wajib diisi'
        elif len(data['password']) > 100:
            errors['password'] = 'Password maksimal 100 karakter'
            
        #----------- TANGGAL DITERIMA ------------------
        if not data['tanggal_diterima']:
            errors['tanggal_diterima'] = 'Tanggal diterima wajib diisi'
        try:
            tgl_diterima = datetime.strptime(data['tanggal_diterima'], '%Y-%m-%d').date()
        except (ValueError, TypeError):
            errors['tanggal_diterima'] = 'Tanggal diterima wajib & formatnya yyyy-mm-dd'
        #----------- ALAMAT  ------------------
        if not data['alamat']:
            errors['alamat'] = 'Alamat wajib diisi'

        # ---------- VALIDASI SERTIFIKAT ----------
        seen_cert = set()

        if not certificates or all(not c.get('nomor') and not c.get('nama') for c in certificates):
            errors['sertifikat'] = 'Tambahkan minimal satu sertifikat'
        else:
            for c in certificates:
                if not (c.get('nomor') and c.get('nama')):
                    errors['sertifikat'] = 'Setiap sertifikat harus berisi nomor & nama'
                    break
                else:
                    if len(c['nomor']) > 10:
                        errors['sertifikat'] = 'Nomor sertifikat max 10 karakter'
                        break
                    if len(c['nama']) > 100:
                        errors['sertifikat'] = 'Nama sertifikat max 100 karakter'
                        break
                    tup = (c['nomor'])
                    if tup in seen_cert:
                        errors['sertifikat'] = 'Duplikasi sertifikat pada form'
                        break
                    seen_cert.add(tup)
 
        # ---------- SIMPAN ----------
        if not errors:
            no_perawat   = str(uuid.uuid4())
            try:
                with transaction.atomic():
                    with connection.cursor() as cur:
                        cur.execute("SET search_path TO pet_clinic;")

                        # USER
                        cur.execute("""
                            INSERT INTO "USER"(email,password,nomor_telepon,alamat)
                            VALUES (%s,%s,%s,%s)
                        """, [data['email'], data['password'], data['nomor_telepon'], data['alamat']])
                        
                        cur.execute("""
                            INSERT INTO PEGAWAI(no_pegawai,tanggal_mulai_kerja,email_user)
                            VALUES (%s,%s,%s)
                        """, [no_perawat, tgl_diterima, data['email']])
                        
                        # TENAGA_MEDIS
                        cur.execute("""
                            INSERT INTO TENAGA_MEDIS(no_tenaga_medis,no_izin_praktik)
                            VALUES (%s,%s)
                        """, [no_perawat, data['izin_praktik']])
                        
                        # PERAWAT
                        cur.execute("""
                            INSERT INTO PERAWAT_HEWAN(no_perawat_hewan)
                            VALUES (%s)
                        """, [no_perawat])

                        # SERTIFIKAT
                        for c in certificates:
                            cur.execute("""
                                INSERT INTO SERTIFIKAT_KOMPETENSI(no_tenaga_medis,no_sertifikat_kompetensi,nama_sertifikat)
                                VALUES (%s,%s,%s)
                            """, [no_perawat, c['nomor'], c['nama']])
                    return redirect('login')   # sukses
                
            except IntegrityError as exc:
                root = exc.__cause__
                if isinstance(root, pg_err.UniqueViolation) and 'email' in str(root):
                    # pesan dikirim dari trigger PL/pgSQL
                    errors['email'] = str(root).split('CONTEXT:')[0].strip()
                else:
                    errors['db'] = 'Terjadi kesalahan database, coba lagi.'


    else:
        data['certificates'] = [{}]
        
    return render(request, 'register_perawat.html', {
        'data': data, 'errors': errors
    })

def dashboard_dokter(request):
    # dokter_info = {}
    # daftar_sertifikat = []
    # daftar_jadwal = []

    # with connection.cursor() as cursor:
    #     # --- Ambil info dokter
    #     cursor.execute("""
    #         SELECT 
    #             dh.no_dokter_hewan,
    #             tm.no_izin_praktik, 
    #             u.email, 
    #             u.alamat, 
    #             u.nomor_telepon, 
    #             p.tanggal_mulai_kerja, 
    #             p.tanggal_akhir_kerja
    #         FROM DOKTER_HEWAN dh
    #         JOIN TENAGA_MEDIS tm ON dh.no_dokter_hewan = tm.no_tenaga_medis
    #         JOIN PEGAWAI p ON tm.no_tenaga_medis = p.no_pegawai
    #         JOIN "USER" u ON p.email_user = u.email
    #         WHERE dh.no_dokter_hewan = %s
    #     """, [str(id_dokter)])
    #     row = cursor.fetchone()
    #     if row:
    #         dokter_info = {
    #             'no_dokter_hewan': row[0],
    #             'no_izin_praktik': row[1],
    #             'email': row[2],
    #             'alamat': row[3],
    #             'nomor_telepon': row[4],
    #             'tanggal_mulai_kerja': row[5].strftime('%d %B %Y') if row[5] else '-',
    #             'tanggal_akhir_kerja': row[6].strftime('%d %B %Y') if row[6] else '-'
    #         }

    #     # --- Ambil daftar sertifikat dokter
    #     cursor.execute("""
    #         SELECT sk.no_sertifikat_kompetensi, sk.nama_sertifikat
    #         FROM SERTIFIKAT_KOMPETENSI sk
    #         WHERE sk.no_tenaga_medis = %s
    #     """, [str(id_dokter)])
    #     rows = cursor.fetchall()
    #     daftar_sertifikat = [{'nomor_sertifikat': r[0], 'nama_sertifikat': r[1]} for r in rows]

    #     # --- Ambil daftar jadwal praktik dokter
    #     cursor.execute("""
    #         SELECT hari, jam
    #         FROM JADWAL_PRAKTIK
    #         WHERE no_dokter_hewan = %s
    #         ORDER BY 
    #             CASE
    #                 WHEN lower(hari) = 'senin' THEN 1
    #                 WHEN lower(hari) = 'selasa' THEN 2
    #                 WHEN lower(hari) = 'rabu' THEN 3
    #                 WHEN lower(hari) = 'kamis' THEN 4
    #                 WHEN lower(hari) = 'jumat' THEN 5
    #                 WHEN lower(hari) = 'sabtu' THEN 6
    #                 WHEN lower(hari) = 'minggu' THEN 7
    #                 ELSE 8
    #             END, jam ASC
    #     """, [str(id_dokter)])
    #     rows = cursor.fetchall()
    #     daftar_jadwal = [{'hari': r[0], 'jam': r[1]} for r in rows]

    return render(request, 'dashboard_dokter.html')

def dashboard_perawat(request):
    # perawat_info = {}
    # daftar_sertifikat = []

    # with connection.cursor() as cursor:
    #     # --- Ambil info perawat
    #     cursor.execute("""
    #         SELECT 
    #             ph.no_perawat_hewan,
    #             tm.no_izin_praktik,
    #             u.email,
    #             u.alamat,
    #             u.nomor_telepon,
    #             p.tanggal_mulai_kerja,
    #             p.tanggal_akhir_kerja
    #         FROM PERAWAT_HEWAN ph
    #         JOIN TENAGA_MEDIS tm ON ph.no_perawat_hewan = tm.no_tenaga_medis
    #         JOIN PEGAWAI p ON tm.no_tenaga_medis = p.no_pegawai
    #         JOIN "USER" u ON p.email_user = u.email
    #         WHERE ph.no_perawat_hewan = %s
    #     """, [str(id_perawat)])
    #     row = cursor.fetchone()
    #     if row:
    #         perawat_info = {
    #             'no_perawat_hewan': row[0],
    #             'no_izin_praktik': row[1],
    #             'email': row[2],
    #             'alamat': row[3],
    #             'nomor_telepon': row[4],
    #             'tanggal_mulai_kerja': row[5].strftime('%d %B %Y') if row[5] else '-',
    #             'tanggal_akhir_kerja': row[6].strftime('%d %B %Y') if row[6] else '-'
    #         }

    #     # --- Ambil daftar sertifikat kompetensi perawat
    #     cursor.execute("""
    #         SELECT sk.no_sertifikat_kompetensi, sk.nama_sertifikat
    #         FROM SERTIFIKAT_KOMPETENSI sk
    #         WHERE sk.no_tenaga_medis = %s
    #     """, [str(id_perawat)])
    #     rows = cursor.fetchall()
    #     daftar_sertifikat = [{'nomor_sertifikat': r[0], 'nama_sertifikat': r[1]} for r in rows]

    return render(request, 'dashboard_perawat.html')

def dashboard_frontdesk(request):
    # officer_info = {}

    # with connection.cursor() as cursor:
    #     # --- Ambil info Front-Desk Officer
    #     cursor.execute("""
    #         SELECT 
    #             fd.no_front_desk,
    #             u.email,
    #             p.tanggal_mulai_kerja,
    #             p.tanggal_akhir_kerja,
    #             u.alamat,
    #             u.nomor_telepon
    #         FROM FRONT_DESK fd
    #         JOIN PEGAWAI p ON fd.no_front_desk = p.no_pegawai
    #         JOIN "USER" u ON p.email_user = u.email
    #         WHERE fd.no_front_desk = %s
    #     """, [str(id_frontdesk)])
    #     row = cursor.fetchone()
    #     if row:
    #         officer_info = {
    #             'nomor_identitas': row[0],
    #             'email': row[1],
    #             'tanggal_diterima': row[2].strftime('%d %B %Y') if row[2] else '-',
    #             'tanggal_akhir_kerja': row[3].strftime('%d %B %Y') if row[3] else '-',
    #             'alamat': row[4],
    #             'nomor_telepon': row[5],
    #         }

    return render(request, 'dashboard_frontdesk.html')

def dashboard_klien(request):
    # klien_info = {}

    # with connection.cursor() as cursor:
    #     # Cek apakah dia Individu atau Perusahaan
    #     cursor.execute("""
    #         SELECT 
    #             k.no_identitas,
    #             u.email,
    #             k.tanggal_registrasi,
    #             u.alamat,
    #             u.nomor_telepon,
    #             i.nama_depan,
    #             i.nama_tengah,
    #             i.nama_belakang,
    #             p.nama_perusahaan
    #         FROM KLIEN k
    #         JOIN "USER" u ON k.email = u.email
    #         LEFT JOIN INDIVIDU i ON k.no_identitas = i.no_identitas_klien
    #         LEFT JOIN PERUSAHAAN p ON k.no_identitas = p.no_identitas_klien
    #         WHERE k.no_identitas = %s
    #     """, [str(id_klien)])
        
    #     row = cursor.fetchone()
    #     if row:
    #         nama = ""
    #         if row[5]:  # Ada nama_depan => Individu
    #             nama_parts = [row[5]]  # nama_depan
    #             if row[6]:  # nama_tengah
    #                 nama_parts.append(row[6])
    #             nama_parts.append(row[7])  # nama_belakang
    #             nama = " ".join(nama_parts)
    #         elif row[8]:  # Ada nama_perusahaan
    #             nama = row[8]
    #         else:
    #             nama = "-"

    #         klien_info = {
    #             'nomor_identitas': row[0],
    #             'email': row[1],
    #             'tanggal_pendaftaran': row[2].strftime('%d %B %Y') if row[2] else '-',
    #             'alamat': row[3],
    #             'nomor_telepon': row[4],
    #             'nama': nama,
    #         }

    return render(request, 'dashboard_klien.html')

def update_password(request):
    return render(request, 'update_password.html')
def update_profile(request):
    return render(request, 'update_profile.html')
