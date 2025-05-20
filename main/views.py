import uuid
from django.db import connection
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegisterIndividuForm, RegisterFrontDeskForm, RegisterDokterForm, RegisterPerawatForm, RegisterPerusahaanForm
import datetime
import re
from datetime import *

EMAIL_REGEX         = re.compile(r'^[\w\.-]+@[\w\.-]+\.[A-Za-z]{2,}$')
PHONE_REGEX         = re.compile(r'^0\d{9,14}$')  
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
        email = request.POST.get('email')
        password = request.POST.get('password')

        with connection.cursor() as cursor:
            cursor.execute("SET search_path TO pet_clinic;")

            # Cek apakah email ada dan password cocok
            print(email)
            cursor.execute("""
                SELECT email, password
                FROM "USER"
                WHERE email = %s
            """, (email,))
            user = cursor.fetchone()
            # print(user['email'])
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
                    # return redirect('dashboard_klien', id_klien=klien[0])
                    return redirect('dashboard_klien')


                else:
                    messages.error(request, "Akun tidak dikenali sebagai Dokter, Perawat, Frontdesk, atau Klien.")
                    return redirect('login')

            else:
                # Email/password tidak cocok
                messages.error(request, "Email atau Password salah.")
                return redirect('login')

    return render(request, 'login.html')

def landing_page(request):
    return render(request, 'landing.html')

def register_view(request):
    return render(request, 'register.html')

def register_individu(request):
    errors = {}
    data = {}

    if request.method == 'POST':
        # Ambil data
        data['email']          = request.POST.get('email', '').strip()
        data['nama_depan']     = request.POST.get('nama_depan', '').strip()
        data['nama_tengah']    = request.POST.get('nama_tengah', '').strip()
        data['nama_belakang']  = request.POST.get('nama_belakang', '').strip()
        data['password']       = request.POST.get('password', '')
        data['nomor_telepon']  = request.POST.get('nomor_telepon', '').strip()
        data['alamat']         = request.POST.get('alamat', '').strip()

        # Validasi email
        if not data['email']:
            errors['email'] = 'Email wajib diisi'
        elif not EMAIL_REGEX.match(data['email']):
            errors['email'] = 'Format email tidak valid'
      

        # Validasi nama
        if not data['nama_depan']:
            errors['nama_depan'] = 'Nama depan wajib diisi'
        if not data['nama_belakang']:
            errors['nama_belakang'] = 'Nama belakang wajib diisi'

        # Validasi password
        if not data['password']:
            errors['password'] = 'Password wajib diisi'
        elif not PASSWORD_REGEX.match(data['password']):
            errors['password'] = (
                'Password minimal 8 karakter, '
                'mengandung huruf besar, huruf kecil, angka, dan simbol'
            )

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

        # Validasi alamat
        if not data['alamat']:
            errors['alamat'] = 'Alamat wajib diisi'

        # Jika tidak ada error, simpan
        if not errors:
            id_klien = uuid.uuid4()
            today = date.today()

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

    return render(request, 'register_individu.html', {
        'errors': errors,
        'data': data
    })

def register_perusahaan(request):
    data = {}
    errors = {}
    days = ['Senin','Selasa','Rabu','Kamis','Jumat','Sabtu','Minggu']

    if request.method == 'POST':
        data['email'] = request.POST.get('email', '').strip()
        data['nama_perusahaan'] = request.POST.get('nama_perusahaan', '').strip()
        data['password'] = request.POST.get('password', '')
        data['nomor_telepon'] = request.POST.get('nomor_telepon', '').strip()
        data['alamat'] = request.POST.get('alamat', '').strip()


        # Validasi Nama Perusahaan
        if not data['nama_perusahaan']:
            errors['nama_perusahaan'] = 'Nama perusahaan wajib diisi'

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
    return render(request, 'register_perusahaan.html', {
        'data': data,
        'errors': errors,
        'days' : days
    })


def register_frontdesk(request):
    errors = {}
    data = {}
    if request.method == 'POST':
        data['email']            = request.POST.get('email', '').strip()
        data['nomor_telepon']    = request.POST.get('nomor_telepon', '').strip()
        data['tanggal_diterima'] = request.POST.get('tanggal_diterima', '').strip()
        data['password']         = request.POST.get('password', '')
        data['alamat']           = request.POST.get('alamat', '').strip()

        # Validasi email
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


        # Validasi tanggal diterima
        if not data['tanggal_diterima']:
            errors['tanggal_diterima'] = 'Tanggal diterima wajib diisi'
        elif not DATE_REGEX.match(data['tanggal_diterima']):
            errors['tanggal_diterima'] = 'Format tanggal harus YYYY-MM-DD'
        else:
            try:
                datetime.strptime(data['tanggal_diterima'], '%Y-%m-%d')
            except ValueError:
                errors['tanggal_diterima'] = 'Tanggal tidak valid'

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

        # Jika valid, simpan
        if not errors:
            id_pegawai = uuid.uuid4()
            tgl_diterima = data['tanggal_diterima'] 

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

            return redirect('register_success')

    return render(request, 'register_frontdesk.html', {
        'errors': errors,
        'data': data
    })



# views.py

import uuid
import re
from datetime import datetime, date

from django.shortcuts import render, redirect
from django.db import connection
from django.contrib.auth.hashers import make_password

# Regex patterns untuk validasi
EMAIL_REGEX = re.compile(r'^[\w\.-]+@[\w\.-]+\.[A-Za-z]{2,}$')
PHONE_REGEX = re.compile(r'^0\d{9,14}$')

def register_dokter(request):
    # Daftar hari untuk dropdown
    days = ['Senin','Selasa','Rabu','Kamis','Jumat','Sabtu','Minggu']

    errors = {}
    data = {}

    if request.method == 'POST':
        # --- Ambil field umum ---
        data['izin_praktik']     = request.POST.get('izin_praktik', '').strip()
        data['nomor_telepon']    = request.POST.get('nomor_telepon', '').strip()
        data['email']            = request.POST.get('email', '').strip()
        data['password']         = request.POST.get('password', '')
        data['tanggal_diterima'] = request.POST.get('tanggal_diterima', '').strip()
        data['alamat']           = request.POST.get('alamat', '').strip()

        # --- Ambil dynamic lists ---
        nos       = request.POST.getlist('nomor_sertifikat')
        nms       = request.POST.getlist('nama_sertifikat')
        hari_list = request.POST.getlist('hari_praktik')
        jm_mulai  = request.POST.getlist('jam_mulai')
        jm_selesai= request.POST.getlist('jam_selesai')

        # --- Buat list-of-dicts untuk template ---
        certificates = []
        for no, nm in zip(nos, nms):
            if no.strip() or nm.strip():
                certificates.append({
                    'nomor': no.strip(),
                    'nama':  nm.strip()
                })
        if not certificates:
            certificates = [{}]

        schedules = []
        for h, jm1, jm2 in zip(hari_list, jm_mulai, jm_selesai):
            if h.strip() or jm1.strip() or jm2.strip():
                schedules.append({
                    'hari':        h.strip(),
                    'jam_mulai':   jm1.strip(),
                    'jam_selesai': jm2.strip()
                })
        if not schedules:
            schedules = [{}]

        data.update({
            'certificates': certificates,
            'schedules':    schedules
        })

        # --- Validasi field umum ---
        if not data['izin_praktik']:
            errors['izin_praktik'] = 'Nomor izin praktik wajib diisi'

        if not data['nomor_telepon']:
            errors['nomor_telepon'] = 'Nomor telepon wajib diisi'
        elif not PHONE_REGEX.match(data['nomor_telepon']):
            errors['nomor_telepon'] = 'Format nomor telepon tidak valid'

        if not data['email']:
            errors['email'] = 'Email wajib diisi'
        elif not EMAIL_REGEX.match(data['email']):
            errors['email'] = 'Format email tidak valid'

        if not data['password']:
            errors['password'] = 'Password wajib diisi'
        elif len(data['password']) < 6:
            errors['password'] = 'Password minimal 6 karakter'

        if not data['tanggal_diterima']:
            errors['tanggal_diterima'] = 'Tanggal diterima wajib diisi'
        else:
            try:
                datetime.strptime(data['tanggal_diterima'], '%Y-%m-%d')
            except ValueError:
                errors['tanggal_diterima'] = 'Format tanggal tidak valid'

        if not data['alamat']:
            errors['alamat'] = 'Alamat wajib diisi'

        # --- Validasi dynamic sertifikat ---
        if not certificates or all(not c.get('nomor') and not c.get('nama') for c in certificates):
            errors['sertifikat'] = 'Tambahkan minimal satu sertifikat'
        else:
            # cek tiap entry lengkap
            for c in certificates:
                if bool(c.get('nomor')) ^ bool(c.get('nama')):
                    errors['sertifikat'] = 'Setiap sertifikat harus punya nomor & nama'
                    break

        # --- Validasi dynamic jadwal ---
        if not schedules or all(not s.get('hari') and not s.get('jam_mulai') and not s.get('jam_selesai') for s in schedules):
            errors['jadwal'] = 'Tambahkan minimal satu jadwal praktik'
        else:
            for s in schedules:
                print(s.get('hari'),s.get('jam_mulai') ,s.get('jam_selesai'))
                if not bool(s.get('hari')) ^ bool(s.get('jam_mulai')) ^ bool(s.get('jam_selesai')):
                    errors['jadwal'] = 'Setiap jadwal harus lengkap (hari, jam mulai & selesai)'
                    break 

        # --- Simpan jika valid ---
        if not errors:
            no_doc = str(uuid.uuid4())
            hashed_pw = make_password(data['password'])
            tgl_diterima = datetime.strptime(data['tanggal_diterima'], '%Y-%m-%d').date()

            with connection.cursor() as cursor:
                # 1. Tabel USER
                cursor.execute(
                    '''INSERT INTO "USER" 
                       (email, password, nomor_telepon, alamat)
                       VALUES (%s, %s, %s, %s)''',
                    [data['email'], hashed_pw, data['nomor_telepon'], data['alamat']]
                )

                # 2. Tabel DOKTER_HEWAN
                cursor.execute(
                    '''INSERT INTO DOKTER_HEWAN
                       (no_dokter, nomor_izin, tanggal_diterima, email_user)
                       VALUES (%s, %s, %s, %s)''',
                    [no_doc, data['izin_praktik'], tgl_diterima, data['email']]
                )

                # 3. Tabel SERTIFIKAT_DOKTER
                for cert in certificates:
                    cursor.execute(
                        '''INSERT INTO SERTIFIKAT_DOKTER
                           (no_dokter, nomor_sertifikat, nama_sertifikat)
                           VALUES (%s, %s, %s)''',
                        [no_doc, cert['nomor'], cert['nama']]
                    )

                # 4. Tabel JADWAL_PRAKTIK
                for sched in schedules:
                    cursor.execute(
                        '''INSERT INTO JADWAL_PRAKTIK
                           (no_dokter, hari_praktik, jam_mulai, jam_selesai)
                           VALUES (%s, %s, %s, %s)''',
                        [no_doc, sched['hari'], sched['jam_mulai'], sched['jam_selesai']]
                    )

            return redirect('register_dokter_hewan_success')

    else:
        # Kalau GET: bikin satu slot kosong
        data['certificates'] = [{}]
        data['schedules']    = [{}]

    return render(request, 'register_dokter.html', {
        'errors': errors,
        'data':   data,
        'days':   days,
    })


def register_perawat(request):
    if request.method == 'POST':
        form = RegisterPerawatForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = RegisterPerawatForm()
    return render(request, 'register_perawat.html', {'form': form})

def dashboard_dokter(request):
    dokter_info = {}
    daftar_sertifikat = []
    daftar_jadwal = []

    if 'user_email' not in request.session:
        return redirect('login')
    
    user_email = request.session['user_email']

    with connection.cursor() as cursor:
        cursor.execute("SET search_path TO pet_clinic;")

        # --- Ambil data profil dokter
        cursor.execute("""
            SELECT 
                dh.no_dokter_hewan,
                tm.no_izin_praktik, 
                u.email, 
                u.alamat, 
                u.nomor_telepon, 
                p.tanggal_mulai_kerja, 
                p.tanggal_akhir_kerja
            FROM dokter_hewan dh
            JOIN tenaga_medis tm ON dh.no_dokter_hewan = tm.no_tenaga_medis
            JOIN pegawai p ON tm.no_tenaga_medis = p.no_pegawai
            JOIN "USER" u ON p.email_user = u.email
            WHERE u.email = %s
        """, [user_email])

        row = cursor.fetchone()
        id_dokter = row[0] if row else None

        if row:
            dokter_info = {
                'no_dokter_hewan': row[0],
                'no_izin_praktik': row[1],
                'email': row[2],
                'alamat': row[3],
                'nomor_telepon': row[4],
                'tanggal_mulai_kerja': row[5].strftime('%d %B %Y') if row[5] else '-',
                'tanggal_akhir_kerja': row[6].strftime('%d %B %Y') if row[6] else '-'
            }

            #--- Ambil daftar sertifikat dokter
            cursor.execute("""
                SELECT no_tenaga_medis
                FROM tenaga_medis
                WHERE no_tenaga_medis = %s
            """, [str(id_dokter)])
            tenaga_medis = cursor.fetchone()

            if tenaga_medis:
                no_tenaga_medis = tenaga_medis[0]
                cursor.execute("""
                SELECT sk.no_sertifikat_kompetensi, sk.nama_sertifikat
                FROM sertifikat_kompetensi sk
                WHERE sk.no_tenaga_medis = %s
                """, [str(no_tenaga_medis)])
                rows = cursor.fetchall()
                daftar_sertifikat = [
                    {'no': i+1, 'nomor_sertifikat': r[0], 'nama_sertifikat': r[1]}
                    for i, r in enumerate(rows)
                ]

            #--- Ambil daftar jadwal praktik dokter
            cursor.execute("""
                SELECT hari, jam
                FROM jadwal_praktik
                WHERE no_dokter_hewan = %s
                ORDER BY 
                    CASE
                        WHEN lower(hari) = 'senin' THEN 1
                        WHEN lower(hari) = 'selasa' THEN 2
                        WHEN lower(hari) = 'rabu' THEN 3
                        WHEN lower(hari) = 'kamis' THEN 4
                        WHEN lower(hari) = 'jumat' THEN 5
                        WHEN lower(hari) = 'sabtu' THEN 6
                        WHEN lower(hari) = 'minggu' THEN 7
                        ELSE 8
                    END, jam ASC
            """, [str(id_dokter)])
            rows = cursor.fetchall()
            daftar_jadwal = [
                {'no': i + 1, 'hari': r[0], 'jam': r[1]}
                for i, r in enumerate(rows)
            ]

    return render(request, 'dashboard_dokter.html', {
        'dokter': dokter_info,
        'sertifikat': daftar_sertifikat,
        'jadwal': daftar_jadwal
    })

def dashboard_perawat(request):
    if 'user_email' not in request.session:
        return redirect('login')
    
    perawat_info = {}
    daftar_sertifikat = []
    user_email = request.session['user_email']

    with connection.cursor() as cursor:
        cursor.execute("SET search_path TO pet_clinic;")

        # --- Ambil info perawat
        cursor.execute("""
            SELECT 
                ph.no_perawat_hewan,
                tm.no_izin_praktik,
                u.email,
                u.alamat,
                u.nomor_telepon,
                p.tanggal_mulai_kerja,
                p.tanggal_akhir_kerja
            FROM perawat_hewan ph
            JOIN tenaga_medis tm ON ph.no_perawat_hewan = tm.no_tenaga_medis
            JOIN pegawai p ON tm.no_tenaga_medis = p.no_pegawai
            JOIN "USER" u ON p.email_user = u.email
            WHERE u.email = %s
        """, [user_email])

        row = cursor.fetchone()
        id_perawat = row[0] if row else None

        if row:
            perawat_info = {
                'no_perawat_hewan': row[0],
                'no_izin_praktik': row[1],
                'email': row[2],
                'alamat': row[3],
                'nomor_telepon': row[4],
                'tanggal_mulai_kerja': row[5].strftime('%d %B %Y') if row[5] else '-',
                'tanggal_akhir_kerja': row[6].strftime('%d %B %Y') if row[6] else '-'
            }

        # --- Ambil daftar sertifikat perawat
        cursor.execute("""
            SELECT sk.no_sertifikat_kompetensi, sk.nama_sertifikat
            FROM sertifikat_kompetensi sk
            WHERE sk.no_tenaga_medis = %s
        """, [str(id_perawat)])

        rows = cursor.fetchall()
        daftar_sertifikat = [
            {'no': i+1, 'nomor_sertifikat': r[0], 'nama_sertifikat': r[1]}
            for i, r in enumerate(rows)
        ]

    return render(request, 'dashboard_perawat.html', {
        'perawat': perawat_info,
        'sertifikat': daftar_sertifikat
    })

def dashboard_frontdesk(request):
    if 'user_email' not in request.session:
        return redirect('login')
    
    officer_info = {}
    user_email = request.session['user_email']

    with connection.cursor() as cursor:
        cursor.execute("SET search_path TO pet_clinic;")
        
        # --- Ambil info Front-Desk Officer
        cursor.execute("""
            SELECT 
                fd.no_front_desk,
                u.email,
                p.tanggal_mulai_kerja,
                p.tanggal_akhir_kerja,
                u.alamat,
                u.nomor_telepon
            FROM FRONT_DESK fd
            JOIN PEGAWAI p ON fd.no_front_desk = p.no_pegawai
            JOIN "USER" u ON p.email_user = u.email
            WHERE u.email = %s
        """, [user_email])
        
        row = cursor.fetchone()
        
        if row:
            officer_info = {
                'nomor_identitas': row[0],
                'email': row[1],
                'tanggal_diterima': row[2].strftime('%d %B %Y') if row[2] else '-',
                'tanggal_akhir_kerja': row[3].strftime('%d %B %Y') if row[3] else '-',
                'alamat': row[4],
                'nomor_telepon': row[5],
            }

    return render(request, 'dashboard_frontdesk.html', {
        'officer': officer_info
    })

def dashboard_klien(request):
    klien_info = {}

    if 'user_email' not in request.session:
        return redirect('login')
    
    user_email = request.session['user_email']
    
    with connection.cursor() as cursor:
        cursor.execute("SET search_path TO pet_clinic;")

        # Ambil data klien + deteksi apakah individu atau perusahaan
        cursor.execute("""
            SELECT 
                k.no_identitas,
                u.email,
                k.tanggal_registrasi,
                u.alamat,
                u.nomor_telepon,
                i.nama_depan,
                i.nama_tengah,
                i.nama_belakang,
                p.nama_perusahaan
            FROM klien k
            JOIN "USER" u ON k.email = u.email
            LEFT JOIN individu i ON k.no_identitas = i.no_identitas_klien
            LEFT JOIN perusahaan p ON k.no_identitas = p.no_identitas_klien
            WHERE u.email = %s
        """, [user_email])
        
        row = cursor.fetchone()
        
        if row:
            # Tentukan nama berdasarkan tipe klien
            if row[5]:  # Individu
                nama_parts = [row[5]]
                if row[6]: nama_parts.append(row[6])
                if row[7]: nama_parts.append(row[7])
                nama = " ".join(nama_parts)
                update_profile_url_name = 'klien_update_profile_individu'
            elif row[8]:  # Perusahaan
                nama = row[8]
                update_profile_url_name = 'klien_update_profile_perusahaan'
            else:
                nama = "-"

            klien_info = {
                'nomor_identitas': row[0],
                'email': row[1],
                'tanggal_pendaftaran': row[2].strftime('%d %B %Y') if row[2] else '-',
                'alamat': row[3],
                'nomor_telepon': row[4],
                'nama': nama,
            }

    return render(request, 'dashboard_klien.html', {
        'klien': klien_info,
        'update_profile_url_name': update_profile_url_name
    })

def update_password(request):
    if 'user_email' not in request.session:
        return redirect('login')

    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        user_email = request.session['user_email']

        if new_password != confirm_password:
            messages.error(request, "Konfirmasi password tidak cocok.")
            return redirect('update_password')

        with connection.cursor() as cursor:
            cursor.execute("SET search_path TO pet_clinic;")

            # Ambil password lama dari database
            cursor.execute("""
                SELECT password FROM "USER" WHERE email = %s
            """, [user_email])
            result = cursor.fetchone()

            if result:
                current_password = result[0]

                if old_password != current_password:
                    messages.error(request, "Password lama salah.")
                    return redirect('update_password')

                # Jika semua valid → update password
                cursor.execute("""
                    UPDATE "USER"
                    SET password = %s
                    WHERE email = %s
                """, [new_password, user_email])

                # Cek apakah Dokter
                cursor.execute("""
                    SELECT no_dokter_hewan
                    FROM dokter_hewan
                    WHERE no_dokter_hewan = (
                        SELECT no_pegawai FROM pegawai WHERE email_user = %s
                    )
                """, [user_email])
                if cursor.fetchone():
                    return redirect('dashboard_dokter')

                # Cek apakah Perawat
                cursor.execute("""
                    SELECT no_perawat_hewan
                    FROM perawat_hewan
                    WHERE no_perawat_hewan = (
                        SELECT no_pegawai FROM pegawai WHERE email_user = %s
                    )
                """, [user_email])
                if cursor.fetchone():
                    return redirect('dashboard_perawat')

                # Cek apakah Frontdesk
                cursor.execute("""
                    SELECT no_front_desk
                    FROM front_desk
                    WHERE no_front_desk = (
                        SELECT no_pegawai FROM pegawai WHERE email_user = %s
                    )
                """, [user_email])
                if cursor.fetchone():
                    return redirect('dashboard_frontdesk')

                # Cek apakah Klien
                cursor.execute("""
                    SELECT no_identitas
                    FROM klien
                    WHERE email = %s
                """, [user_email])
                if cursor.fetchone():
                    return redirect('dashboard_klien')

    return render(request, 'update_password.html')

def update_profile(request):
    return render(request, 'update_profile.html')

def update_profile_individu(request):
    if 'user_email' not in request.session:
        return redirect('login')

    user_email = request.session['user_email']

    if request.method == 'POST':
        alamat = request.POST.get('alamat')
        nomor_telepon = request.POST.get('nomor_telepon')
        nama_depan = request.POST.get('nama_depan')
        nama_tengah = request.POST.get('nama_tengah')
        nama_belakang = request.POST.get('nama_belakang')

        with connection.cursor() as cursor:
            cursor.execute("SET search_path TO pet_clinic;")

            # Update USER (alamat & nomor telepon)
            cursor.execute("""
                UPDATE "USER"
                SET alamat = %s, nomor_telepon = %s
                WHERE email = %s
            """, [alamat, nomor_telepon, user_email])

            # Update nama individu
            cursor.execute("""
                UPDATE individu
                SET nama_depan = %s,
                    nama_tengah = %s,
                    nama_belakang = %s
                WHERE no_identitas_klien = (
                    SELECT no_identitas FROM klien WHERE email = %s
                )
            """, [nama_depan, nama_tengah, nama_belakang, user_email])

        messages.success(request, "Profil berhasil diperbarui.")
        return redirect('dashboard_klien')  # ganti sesuai url dashboard klien kamu

    # Ambil data untuk prefill form
    with connection.cursor() as cursor:
        cursor.execute("SET search_path TO pet_clinic;")

        cursor.execute("""
            SELECT u.alamat, u.nomor_telepon,
                   i.nama_depan, i.nama_tengah, i.nama_belakang
            FROM "USER" u
            JOIN klien k ON u.email = k.email
            JOIN individu i ON k.no_identitas = i.no_identitas_klien
            WHERE u.email = %s
        """, [user_email])

        row = cursor.fetchone()

    data = {}
    if row:
        data = {
            'alamat': row[0],
            'nomor_telepon': row[1],
            'nama_depan': row[2],
            'nama_tengah': row[3],
            'nama_belakang': row[4]
        }

    return render(request, 'update_profile_individu.html', data)

def update_profile_perusahaan(request):
    if 'user_email' not in request.session:
        return redirect('login')

    user_email = request.session['user_email']

    if request.method == 'POST':
        alamat = request.POST.get('alamat')
        nomor_telepon = request.POST.get('nomor_telepon')
        nama_perusahaan = request.POST.get('nama_perusahaan')

        if not nama_perusahaan or nama_perusahaan.strip() == "":
            messages.error(request, "Nama perusahaan tidak boleh kosong.")
            return redirect('klien_update_profile_perusahaan')

        with connection.cursor() as cursor:
            cursor.execute("SET search_path TO pet_clinic;")

            # Update tabel USER
            cursor.execute("""
                UPDATE "USER"
                SET alamat = %s, nomor_telepon = %s
                WHERE email = %s
            """, [alamat, nomor_telepon, user_email])

            # Update nama perusahaan
            cursor.execute("""
                UPDATE perusahaan
                SET nama_perusahaan = %s
                WHERE no_identitas_klien = (
                    SELECT no_identitas FROM klien WHERE email = %s
                )
            """, [nama_perusahaan, user_email])

        messages.success(request, "Profil perusahaan berhasil diperbarui.")
        return redirect('dashboard_klien')

    # Ambil data untuk prefill form
    with connection.cursor() as cursor:
        cursor.execute("SET search_path TO pet_clinic;")

        cursor.execute("""
            SELECT u.alamat, u.nomor_telepon, p.nama_perusahaan
            FROM "USER" u
            JOIN klien k ON u.email = k.email
            JOIN perusahaan p ON k.no_identitas = p.no_identitas_klien
            WHERE u.email = %s
        """, [user_email])

        row = cursor.fetchone()

    data = {}
    if row:
        data = {
            'alamat': row[0],
            'nomor_telepon': row[1],
            'nama_perusahaan': row[2]
        }

    return render(request, 'update_profile_perusahaan.html', data)

def update_profile_frontdesk(request):
    if 'user_email' not in request.session:
        return redirect('login')

    user_email = request.session['user_email']

    if request.method == 'POST':
        alamat = request.POST.get('alamat')
        nomor_telepon = request.POST.get('nomor_telepon')
        tanggal_akhir_kerja = request.POST.get('tanggal_akhir_kerja')

        if not alamat or not nomor_telepon or not tanggal_akhir_kerja:
            messages.error(request, "Semua field wajib diisi.")
            return redirect('frontdesk_update_profile')

        with connection.cursor() as cursor:
            cursor.execute("SET search_path TO pet_clinic;")

            # Update alamat & nomor telepon
            cursor.execute("""
                UPDATE "USER"
                SET alamat = %s, nomor_telepon = %s
                WHERE email = %s
            """, [alamat, nomor_telepon, user_email])

            # Update tanggal akhir kerja
            cursor.execute("""
                UPDATE PEGAWAI
                SET tanggal_akhir_kerja = %s
                WHERE email_user = %s
            """, [tanggal_akhir_kerja, user_email])

        messages.success(request, "Profil berhasil diperbarui.")
        return redirect('dashboard_frontdesk')

    # GET method → prefill form
    data = {}
    with connection.cursor() as cursor:
        cursor.execute("SET search_path TO pet_clinic;")
        cursor.execute("""
            SELECT u.alamat, u.nomor_telepon, p.tanggal_akhir_kerja
            FROM "USER" u
            JOIN PEGAWAI p ON u.email = p.email_user
            JOIN FRONT_DESK f ON f.no_front_desk = p.no_pegawai
            WHERE u.email = %s
        """, [user_email])

        row = cursor.fetchone()
        if row:
            data = {
                'alamat': row[0],
                'nomor_telepon': row[1],
                'tanggal_akhir_kerja': row[2].strftime('%Y-%m-%d') if row[2] else ''
            }

    return render(request, 'update_profile_frontdesk.html', data)