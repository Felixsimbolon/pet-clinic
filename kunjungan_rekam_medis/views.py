from django.shortcuts import render
from django.shortcuts import render
from django.db import connection
from django.shortcuts import render, redirect
from django.db import connection
    
from django.shortcuts import render, get_object_or_404, redirect
from django.db import connection
    
from django.shortcuts import render, redirect
from django.db import connection
from django.http import Http404

from django.shortcuts import render
from django.db import connection
from django.shortcuts import render, redirect
from django.db import connection
from django.contrib import messages
import uuid
from datetime import datetime, time
from django.db import connection, transaction, IntegrityError
from psycopg2           import errors as pg_err    
from psycopg2.errors import CheckViolation
from psycopg2 import errors as pg_err   # import semua mapping error psycopg2




    
def daftar_kunjungan_fdo(request):
    if 'user_email' not in request.session:
        return redirect('login')

    user_email = request.session['user_email']

    with connection.cursor() as cursor:
        # Cari no_pegawai dari email
        cursor.execute("SET SEARCH_PATH TO PET_CLINIC;")

        cursor.execute("SELECT no_pegawai FROM pegawai WHERE email_user = %s", [user_email])
        result = cursor.fetchone()
        if not result:
            # Email tidak ditemukan di pegawai
            return redirect('login')

        no_pegawai = result[0]

        # Cek apakah no_pegawai ini ada di tabel front_desk
        cursor.execute("SELECT 1 FROM front_desk WHERE no_front_desk = %s", [no_pegawai])
        is_fdo = cursor.fetchone()
        if not is_fdo:
            # Jika no_pegawai tidak ada di front_desk, redirect login
            return redirect('login')
    with connection.cursor() as cursor:
        cursor.execute("SET search_path TO pet_clinic;")
        cursor.execute("""
            SELECT
                id_kunjungan,
                no_identitas_klien,
                nama_hewan,
                tipe_kunjungan,
                no_front_desk,
                no_dokter_hewan,
                no_perawat_hewan,
                timestamp_awal,
                timestamp_akhir
            FROM kunjungan
            ORDER BY timestamp_awal DESC
        """)
        kunjungan_rows = list(cursor.fetchall())

        for i, row in enumerate(kunjungan_rows):
            (
                id_kunjungan,
                no_identitas_klien,
                nama_hewan,
                tipe_kunjungan,
                no_front_desk,
                no_dokter_hewan,
                no_perawat_hewan,
                timestamp_awal,
                timestamp_akhir
            ) = row

            # Cek apakah kunjungan keperawatan ada catatan (menggunakan PK gabungan)
            cursor.execute("""
                SELECT EXISTS (
                    SELECT 1 FROM kunjungan
                    WHERE id_kunjungan = %s
                      AND no_identitas_klien = %s
                      AND nama_hewan = %s
                      AND no_front_desk = %s
                      AND no_dokter_hewan = %s
                      AND no_perawat_hewan = %s
                      AND catatan IS NOT NULL
                      AND catatan <> ''
                )
            """, [
                id_kunjungan,
                no_identitas_klien,
                nama_hewan,
                no_front_desk,
                no_dokter_hewan,
                no_perawat_hewan,
            ])
            punya_catatan = cursor.fetchone()[0]

            # Cek apakah suhu dan berat badan ada di rekam medis (menggunakan PK gabungan)
            cursor.execute("""
                SELECT EXISTS (
                    SELECT 1 FROM kunjungan
                    WHERE id_kunjungan = %s
                      AND no_identitas_klien = %s
                      AND nama_hewan = %s
                      AND no_front_desk = %s
                      AND no_dokter_hewan = %s
                      AND no_perawat_hewan = %s
                      AND suhu IS NOT NULL
                      AND berat_badan IS NOT NULL
                )
            """, [
                id_kunjungan,
                no_identitas_klien,
                nama_hewan,
                no_front_desk,
                no_dokter_hewan,
                no_perawat_hewan,
            ])
            punya_rekam_medis = cursor.fetchone()[0]

            # Tambahkan flag ke tuple
            kunjungan_rows[i] = (*row, punya_catatan, punya_rekam_medis)

    columns = [
        'id_kunjungan', 'no_identitas_klien', 'nama_hewan', 'tipe_kunjungan',
        'no_front_desk', 'no_dokter_hewan', 'no_perawat_hewan', 
        'timestamp_awal', 'timestamp_akhir', 'punya_catatan', 'punya_rekam_medis'
    ]
    data = [dict(zip(columns, row)) for row in kunjungan_rows]

    return render(request, 'daftar_kunjungan_fdo.html', {
        'kunjungan_list': data
    })

    
def daftar_kunjungan_perawat(request):
    if 'user_email' not in request.session:
        return redirect('login')

    user_email = request.session['user_email']

    with connection.cursor() as cursor:
        # Cari no_pegawai dari email
        cursor.execute("SET SEARCH_PATH TO PET_CLINIC;")

        cursor.execute("SELECT no_pegawai FROM pegawai WHERE email_user = %s", [user_email])
        result = cursor.fetchone()
        if not result:
            # Email tidak ditemukan di pegawai
            return redirect('login')

        no_pegawai = result[0]

        # Cek apakah no_pegawai ini ada di tabel perawat_hewan
        cursor.execute("SELECT 1 FROM perawat_hewan WHERE no_perawat_hewan = %s", [no_pegawai])
        is_dokter = cursor.fetchone()
        if not is_dokter:
            # Jika no_pegawai tidak ada di perawat_hewan, redirect login
            return redirect('login')
        
    with connection.cursor() as cursor:
        cursor.execute("SET search_path TO pet_clinic;")
        cursor.execute("""
            SELECT
                id_kunjungan,
                no_identitas_klien,
                nama_hewan,
                tipe_kunjungan,
                no_front_desk,
                no_dokter_hewan,
                no_perawat_hewan,
                timestamp_awal,
                timestamp_akhir
            FROM kunjungan
            ORDER BY timestamp_awal DESC
        """)
        kunjungan_rows = list(cursor.fetchall())

        for i, row in enumerate(kunjungan_rows):
            (
                id_kunjungan,
                no_identitas_klien,
                nama_hewan,
                tipe_kunjungan,
                no_front_desk,
                no_dokter_hewan,
                no_perawat_hewan,
                timestamp_awal,
                timestamp_akhir
            ) = row

            # Cek apakah kunjungan keperawatan ada catatan (menggunakan PK gabungan)
            cursor.execute("""
                SELECT EXISTS (
                    SELECT 1 FROM kunjungan
                    WHERE id_kunjungan = %s
                      AND no_identitas_klien = %s
                      AND nama_hewan = %s
                      AND no_front_desk = %s
                      AND no_dokter_hewan = %s
                      AND no_perawat_hewan = %s
                      AND catatan IS NOT NULL
                      AND catatan <> ''
                )
            """, [
                id_kunjungan,
                no_identitas_klien,
                nama_hewan,
                no_front_desk,
                no_dokter_hewan,
                no_perawat_hewan,
            ])
            punya_catatan = cursor.fetchone()[0]

            # Cek apakah suhu dan berat badan ada di rekam medis (menggunakan PK gabungan)
            cursor.execute("""
                SELECT EXISTS (
                    SELECT 1 FROM kunjungan
                    WHERE id_kunjungan = %s
                      AND no_identitas_klien = %s
                      AND nama_hewan = %s
                      AND no_front_desk = %s
                      AND no_dokter_hewan = %s
                      AND no_perawat_hewan = %s
                      AND suhu IS NOT NULL
                      AND berat_badan IS NOT NULL
                )
            """, [
                id_kunjungan,
                no_identitas_klien,
                nama_hewan,
                no_front_desk,
                no_dokter_hewan,
                no_perawat_hewan,
            ])
            punya_rekam_medis = cursor.fetchone()[0]

            # Tambahkan flag ke tuple
            kunjungan_rows[i] = (*row, punya_catatan, punya_rekam_medis)

    columns = [
        'id_kunjungan', 'no_identitas_klien', 'nama_hewan', 'tipe_kunjungan',
        'no_front_desk', 'no_dokter_hewan', 'no_perawat_hewan', 
        'timestamp_awal', 'timestamp_akhir', 'punya_catatan', 'punya_rekam_medis'
    ]
    data = [dict(zip(columns, row)) for row in kunjungan_rows]

    return render(request, 'daftar_kunjungan_perawat.html', {
        'kunjungan_list': data
    })   
    
    
    
    
def daftar_kunjungan_klien(request):
    if 'user_email' not in request.session:
        return redirect('login')
 
    user_email = request.session['user_email']

    with connection.cursor() as cursor:
        # Cari no_pegawai dari email
        cursor.execute("SET SEARCH_PATH TO PET_CLINIC;")

        cursor.execute("SELECT no_identitas FROM klien WHERE email = %s", [user_email])
        result = cursor.fetchone()
        if not result:
            # Email tidak ditemukan di pegawai
            return redirect('login')
    with connection.cursor() as cursor:
        cursor.execute("SET search_path TO pet_clinic;")
        cursor.execute("""
            SELECT
                id_kunjungan,
                no_identitas_klien,
                nama_hewan,
                tipe_kunjungan,
                no_front_desk,
                no_dokter_hewan,
                no_perawat_hewan,
                timestamp_awal,
                timestamp_akhir
            FROM kunjungan where no_identitas_klien = (select no_identitas from klien where email = %s)
            ORDER BY timestamp_awal DESC
        """,[request.session['user_email']])
        kunjungan_rows = list(cursor.fetchall())

        for i, row in enumerate(kunjungan_rows):
            (
                id_kunjungan,
                no_identitas_klien,
                nama_hewan,
                tipe_kunjungan,
                no_front_desk,
                no_dokter_hewan,
                no_perawat_hewan,
                timestamp_awal,
                timestamp_akhir
            ) = row

            # Cek apakah kunjungan keperawatan ada catatan (menggunakan PK gabungan)
            cursor.execute("""
                SELECT EXISTS (
                    SELECT 1 FROM kunjungan
                    WHERE id_kunjungan = %s
                      AND no_identitas_klien = %s
                      AND nama_hewan = %s
                      AND no_front_desk = %s
                      AND no_dokter_hewan = %s
                      AND no_perawat_hewan = %s
                      AND catatan IS NOT NULL
                      AND catatan <> ''
                )
            """, [
                id_kunjungan,
                no_identitas_klien,
                nama_hewan,
                no_front_desk,
                no_dokter_hewan,
                no_perawat_hewan,
            ])
            punya_catatan = cursor.fetchone()[0]

            # Cek apakah suhu dan berat badan ada di rekam medis (menggunakan PK gabungan)
            cursor.execute("""
                SELECT EXISTS (
                    SELECT 1 FROM kunjungan
                    WHERE id_kunjungan = %s
                      AND no_identitas_klien = %s
                      AND nama_hewan = %s
                      AND no_front_desk = %s
                      AND no_dokter_hewan = %s
                      AND no_perawat_hewan = %s
                      AND suhu IS NOT NULL
                      AND berat_badan IS NOT NULL
                )
            """, [
                id_kunjungan,
                no_identitas_klien,
                nama_hewan,
                no_front_desk,
                no_dokter_hewan,
                no_perawat_hewan,
            ])
            punya_rekam_medis = cursor.fetchone()[0]

            # Tambahkan flag ke tuple
            kunjungan_rows[i] = (*row, punya_catatan, punya_rekam_medis)

    columns = [
        'id_kunjungan', 'no_identitas_klien', 'nama_hewan', 'tipe_kunjungan',
        'no_front_desk', 'no_dokter_hewan', 'no_perawat_hewan', 
        'timestamp_awal', 'timestamp_akhir', 'punya_catatan', 'punya_rekam_medis'
    ]
    data = [dict(zip(columns, row)) for row in kunjungan_rows]

    

    return render(request, 'daftar_kunjungan_klien.html', {
        'kunjungan_list': data
    })
    
    
def daftar_kunjungan(request):
    if 'user_email' not in request.session:
        return redirect('login')

    user_email = request.session['user_email']

    with connection.cursor() as cursor:
        # Cari no_pegawai dari email
        cursor.execute("SET SEARCH_PATH TO PET_CLINIC;")

        cursor.execute("SELECT no_pegawai FROM pegawai WHERE email_user = %s", [user_email])
        result = cursor.fetchone()
        if not result:
            # Email tidak ditemukan di pegawai
            return redirect('login')

        no_pegawai = result[0]

        # Cek apakah no_pegawai ini ada di tabel front_desk
        cursor.execute("SELECT 1 FROM dokter_hewan WHERE no_dokter_hewan = %s", [no_pegawai])
        is_fdo = cursor.fetchone()
        if not is_fdo:
            # Jika no_pegawai tidak ada di front_desk, redirect login
            return redirect('login')
        
    with connection.cursor() as cursor:
        cursor.execute("SET search_path TO pet_clinic;")
        cursor.execute("""
            SELECT
                id_kunjungan,
                no_identitas_klien,
                nama_hewan,
                tipe_kunjungan,
                no_front_desk,
                no_dokter_hewan,
                no_perawat_hewan,
                timestamp_awal,
                timestamp_akhir
            FROM kunjungan
            ORDER BY timestamp_awal DESC
        """)
        kunjungan_rows = list(cursor.fetchall())

        for i, row in enumerate(kunjungan_rows):
            (
                id_kunjungan,
                no_identitas_klien,
                nama_hewan,
                tipe_kunjungan,
                no_front_desk,
                no_dokter_hewan,
                no_perawat_hewan,
                timestamp_awal,
                timestamp_akhir
            ) = row

            # Cek apakah kunjungan keperawatan ada catatan (menggunakan PK gabungan)
            cursor.execute("""
                SELECT EXISTS (
                    SELECT 1 FROM kunjungan
                    WHERE id_kunjungan = %s
                      AND no_identitas_klien = %s
                      AND nama_hewan = %s
                      AND no_front_desk = %s
                      AND no_dokter_hewan = %s
                      AND no_perawat_hewan = %s
                      AND catatan IS NOT NULL
                      AND catatan <> ''
                )
            """, [
                id_kunjungan,
                no_identitas_klien,
                nama_hewan,
                no_front_desk,
                no_dokter_hewan,
                no_perawat_hewan,
            ])
            punya_catatan = cursor.fetchone()[0]

            # Cek apakah suhu dan berat badan ada di rekam medis (menggunakan PK gabungan)
            cursor.execute("""
                SELECT EXISTS (
                    SELECT 1 FROM kunjungan
                    WHERE id_kunjungan = %s
                      AND no_identitas_klien = %s
                      AND nama_hewan = %s
                      AND no_front_desk = %s
                      AND no_dokter_hewan = %s
                      AND no_perawat_hewan = %s
                      AND suhu IS NOT NULL
                      AND berat_badan IS NOT NULL
                )
            """, [
                id_kunjungan,
                no_identitas_klien,
                nama_hewan,
                no_front_desk,
                no_dokter_hewan,
                no_perawat_hewan,
            ])
            punya_rekam_medis = cursor.fetchone()[0]

            # Tambahkan flag ke tuple
            kunjungan_rows[i] = (*row, punya_catatan, punya_rekam_medis)

    columns = [
        'id_kunjungan', 'no_identitas_klien', 'nama_hewan', 'tipe_kunjungan',
        'no_front_desk', 'no_dokter_hewan', 'no_perawat_hewan', 
        'timestamp_awal', 'timestamp_akhir', 'punya_catatan', 'punya_rekam_medis'
    ]
    data = [dict(zip(columns, row)) for row in kunjungan_rows]

    return render(request, 'daftar_kunjungan.html', {
        'kunjungan_list': data
    }) 
import json
def create_kunjungan(request):
    # Retrieve all available ID Klien and Nama Hewan from the database
    if 'user_email' not in request.session:
        return redirect('login')

    user_email = request.session['user_email']

    with connection.cursor() as cursor:
        # Cari no_pegawai dari email
        cursor.execute("SET SEARCH_PATH TO PET_CLINIC;")

        cursor.execute("SELECT no_pegawai FROM pegawai WHERE email_user = %s", [user_email])
        result = cursor.fetchone()
        if not result:
            # Email tidak ditemukan di pegawai
            return redirect('login')

        no_pegawai = result[0]

        # Cek apakah no_pegawai ini ada di tabel front_desk
        cursor.execute("SELECT 1 FROM front_desk WHERE no_front_desk = %s", [no_pegawai])
        is_fdo = cursor.fetchone()
        if not is_fdo:
            # Jika no_pegawai tidak ada di front_desk, redirect login
            return redirect('login')
    errors = {}
    with connection.cursor() as cursor:
        cursor.execute("SET search_path TO pet_clinic;")
        
        # 1) Get all ID Klien
        cursor.execute("SELECT no_identitas FROM klien ORDER BY no_identitas;")
        klien_list = [row[0] for row in cursor.fetchall()]

        # mapping id_klien → list hewan
        cursor.execute("""
            SELECT no_identitas_klien, nama
            FROM hewan
            ORDER BY nama
        """)
        hewan_map = {}
        for idc, nama in cursor.fetchall():
            hewan_map.setdefault(str(idc), []).append(nama)
            
        cursor.execute("""
            SELECT id_jenis, nama FROM hewan ORDER BY nama;
        """)
        hewan_list = []
        for row in cursor.fetchall():
            hewan_list.append({
                'id': row[0],
                'nama': row[1],
            })

        # 3) Get available metode_kunjungan options
        cursor.execute("""
            SELECT DISTINCT tipe_kunjungan FROM kunjungan ORDER BY tipe_kunjungan;
        """)
        tipe_kunjungan_list = [row[0] for row in cursor.fetchall()]

        # 4) Get all available dokter_hewan with their emails and formatted names
        cursor.execute("""
            SELECT 
                k.no_dokter_hewan,
                p.email_user,
                'dr. ' || REPLACE(SUBSTRING(p.email_user FROM 1 FOR POSITION('@' IN p.email_user) - 1), '.', ' ')
            FROM pegawai p
            JOIN dokter_hewan k ON p.no_pegawai = k.no_dokter_hewan
            ORDER BY 3;
            """)
        # Extract and format the doctor list correctly
        dokter_list = []
        for row in cursor.fetchall():
            dokter_list.append({
                'id': row[0],
                'email': row[1],
                'name': row[2]
            })

        # 5) Get all available perawat_hewan with their emails and formatted names
        cursor.execute("""
            SELECT 
                k.no_perawat_hewan,
                p.email_user,
                REPLACE(SUBSTRING(p.email_user FROM 1 FOR POSITION('@' IN p.email_user) - 1), '.', '          ')
            FROM pegawai p
            JOIN perawat_hewan k ON p.no_pegawai = k.no_perawat_hewan
            ORDER BY 3;
            """)
        # Extract and format the nurse list correctly
        perawat_list = []
        for row in cursor.fetchall():
            perawat_list.append({
                'id': row[0],
                'email': row[1],
                'name': row[2]
            })
            
        cursor.execute("""
            SELECT 
                k.no_front_desk,
                p.email_user,
                REPLACE(SUBSTRING(p.email_user FROM 1 FOR POSITION('@' IN p.email_user) - 1), '.', '          ')
            FROM pegawai p
            JOIN front_desk k ON p.no_pegawai = k.no_front_desk
            ORDER BY 3;
            """)
        # Extract and format the nurse list correctly
        front_desk_list = []
        for row in cursor.fetchall():
            front_desk_list.append({
                'id': row[0],
                'email': row[1],
                'name': row[2]
            })
        
    if request.method == "POST":
        # Get the data from form
        id_klien        = request.POST.get('id_klien', '').strip()
        nama_hewan      = request.POST.get('nama_hewan', '').strip()
        metode_kunjungan= request.POST.get('metode_kunjungan', '').strip()
        waktu_mulai_penanganan= request.POST.get('timestamp_awal', '').strip()
        waktu_selesai_penanganan = request.POST.get('timestamp_akhir', '').strip()
        dokter_email    = request.POST.get('dokter_hewan', '').strip()
        perawat_email   = request.POST.get('perawat_hewan', '').strip()
        front_desk_email= request.POST.get('front_desk', '').strip()
        
        
        id_kunjungan = uuid.uuid4()

        # timestamp_awal = datetime.strptime(waktu_mulai_penanganan, "%Y-%m-%dT%H:%M:%S")
        # timestamp_akhir = datetime.strptime(waktu_selesai_penanganan, "%Y-%m-%dT%H:%M:%S")
        
        required_drop = {
            'id_klien':            id_klien,
            'nama_hewan':          nama_hewan,
            'metode_kunjungan':    metode_kunjungan,
            'dokter_hewan':        dokter_email,
            'perawat_hewan':       perawat_email,
            'front_desk':          front_desk_email,
        }

        for field, value in required_drop.items():
            if not value:                              # ''  atau None
                errors[field] = f'{field.replace("_", " ").title()} wajib dipilih'

        # ----------- VALIDASI WAKTU --------------- #
        if not waktu_mulai_penanganan:
            errors['timestamp_awal'] = 'Waktu mulai harus diisi'
        

        dt_awal = dt_akhir = None
        if 'timestamp_awal' not in errors:
            try:
                timestamp_awal = datetime.strptime(waktu_mulai_penanganan, "%Y-%m-%dT%H:%M:%S")
            except ValueError:
                errors['timestamp_awal'] = 'Format waktu mulai tidak valid'

        if 'timestamp_akhir' not in errors and waktu_selesai_penanganan != '':
            try:
                timestamp_akhir = datetime.strptime(waktu_selesai_penanganan, "%Y-%m-%dT%H:%M:%S")
            except ValueError:
                errors['timestamp_akhir'] = 'Format waktu selesai tidak valid'
                

        # ---------- jika ada error, render ulang form ----------
        if errors:
            return render(request, 'create_kunjungan.html', {
                'errors': errors,
                'data':   request.POST,          # supaya nilai dropdown tetap terpilih
                'klien_list':          klien_list,
                'hewan_list':          hewan_list,
                'tipe_kunjungan_list': tipe_kunjungan_list,
                'dokter_list':         dokter_list,
                'perawat_list':        perawat_list,
                'front_desk_list':     front_desk_list,
                "hewan_map_json": json.dumps(hewan_map),   # ← penting!

            })

        with connection.cursor() as cursor:
            cursor.execute("SET search_path TO pet_clinic;")
            def pegawai_id_by_email(email):
                cursor.execute('SELECT no_pegawai FROM pegawai WHERE email_user = %s',
                            [email])
                row = cursor.fetchone()
                return row[0] if row else None
 
            no_perawat   = pegawai_id_by_email(perawat_email)
            no_dokter    = pegawai_id_by_email(dokter_email)
            no_front_desk= pegawai_id_by_email(front_desk_email)
            try:
                if  waktu_selesai_penanganan == "":
                    cursor.execute("""
                        INSERT INTO kunjungan
                            (id_kunjungan, no_identitas_klien,nama_hewan, tipe_kunjungan, timestamp_awal, no_dokter_hewan, no_perawat_hewan,no_front_desk)
                        VALUES (%s, %s, %s, %s, %s, %s, %s,%s)
                    """, [id_kunjungan,id_klien, nama_hewan, metode_kunjungan, timestamp_awal, no_dokter, no_perawat,no_front_desk])
                else:
                        cursor.execute("""
                        INSERT INTO kunjungan
                            (id_kunjungan, no_identitas_klien,nama_hewan, tipe_kunjungan, timestamp_awal, timestamp_akhir, no_dokter_hewan, no_perawat_hewan,no_front_desk)
                        VALUES (%s, %s, %s, %s, %s, %s, %s,%s, %s)
                    """, [id_kunjungan,id_klien, nama_hewan, metode_kunjungan, timestamp_awal, timestamp_akhir, no_dokter, no_perawat,no_front_desk])
                return redirect('daftar_kunjungan_fdo')

            except IntegrityError as exc:
                root = exc.__cause__
                msg    = str(root).split('CONTEXT:')[0].strip()
                pgcode = getattr(root, 'pgcode', '')  # contoh '23514'
                if isinstance(root, pg_err.UniqueViolation) :
                    # pesan dikirim dari trigger PL/pgSQL
                    errors['timestamp_akhir'] = str(root).split('CONTEXT:')[0].strip()
                    return render(request, 'create_kunjungan.html', {
                        'klien_list': klien_list,
                        "hewan_map_json": json.dumps(hewan_map),   # ← penting!

                        'hewan_list': hewan_list,
                        'tipe_kunjungan_list': tipe_kunjungan_list,
                        'dokter_list': dokter_list,  # Pass dokter list for dropdown
                        'perawat_list': perawat_list,  # Pass perawat list for dropdown
                        'front_desk_list': front_desk_list,
                        'errors': errors,
                    })
                elif pgcode == '23514' or isinstance(root,(pg_err.CheckViolation, pg_err.RaiseException)):

                        if 'Timestamp akhir' in msg:          # trigger waktu
                            errors['timestamp_akhir']= msg

                        elif msg.startswith('ERROR: Hewan'):  # trigger hewan-klien
                            errors['nama_hewan'] = msg

                        else:                                 # pesan lain dari trigger yg sama
                            errors.setdefault('db', msg)
                        return render(request, 'create_kunjungan.html', {
                            'klien_list': klien_list,
                            "hewan_map_json": json.dumps(hewan_map),   # ← penting!

                            'hewan_list': hewan_list,
                            'tipe_kunjungan_list': tipe_kunjungan_list,
                            'dokter_list': dokter_list,  # Pass dokter list for dropdown
                            'perawat_list': perawat_list,  # Pass perawat list for dropdown
                            'front_desk_list': front_desk_list,
                            'errors': errors,
                        })

                else:
                    errors['db'] = 'Terjadi kesalahan database, coba lagi.'
                    return render(request, 'create_kunjungan.html', {
                        'klien_list': klien_list,
                        "hewan_map_json": json.dumps(hewan_map),   # ← penting!

                        'hewan_list': hewan_list,
                        'tipe_kunjungan_list': tipe_kunjungan_list,
                        'dokter_list': dokter_list,  # Pass dokter list for dropdown
                        'perawat_list': perawat_list,  # Pass perawat list for dropdown
                        'front_desk_list': front_desk_list,
                        'errors': errors,
                    })

        # Redirect after saving the kunjungan data

    return render(request, 'create_kunjungan.html', {
        'klien_list': klien_list,
        "hewan_map_json": json.dumps(hewan_map),   # ← penting!

        'hewan_list': hewan_list,
        'tipe_kunjungan_list': tipe_kunjungan_list,
        'dokter_list': dokter_list,  # Pass dokter list for dropdown
        'perawat_list': perawat_list,  # Pass perawat list for dropdown
        'front_desk_list': front_desk_list,
        'errors': errors,
    })


def update_kunjungan(request, id_kunjungan,no_dokter_hewan,no_perawat_hewan,no_front_desk,nama_hewan,no_identitas_klien):
    # Fetch the current Kunjungan data based on the ID
    if 'user_email' not in request.session:
        return redirect('login')

    user_email = request.session['user_email']

    with connection.cursor() as cursor:
        # Cari no_pegawai dari email
        cursor.execute("SET SEARCH_PATH TO PET_CLINIC;")

        cursor.execute("SELECT no_pegawai FROM pegawai WHERE email_user = %s", [user_email])
        result = cursor.fetchone()
        if not result:
            # Email tidak ditemukan di pegawai
            return redirect('login')

        no_pegawai = result[0]

        # Cek apakah no_pegawai ini ada di tabel front_desk
        cursor.execute("SELECT 1 FROM front_desk WHERE no_front_desk = %s", [no_pegawai])
        is_fdo = cursor.fetchone()
        if not is_fdo:
            # Jika no_pegawai tidak ada di front_desk, redirect login
            return redirect('login')
        
    errors = {}
    with connection.cursor() as cursor:
        cursor.execute("SET search_path TO pet_clinic;")
        
        cursor.execute("""
            SELECT email_user
            FROM kunjungan join pegawai on no_dokter_hewan = no_pegawai
            WHERE id_kunjungan = %s
            AND no_identitas_klien = %s
            AND nama_hewan = %s
            AND no_dokter_hewan = %s
            AND no_perawat_hewan = %s
            AND no_front_desk = %s
""", [id_kunjungan, no_identitas_klien, nama_hewan, no_dokter_hewan, no_perawat_hewan, no_front_desk])
        
        email_dokter_hewan = cursor.fetchone()[0]
         
        cursor.execute("""
            SELECT email_user
            FROM kunjungan join pegawai on no_perawat_hewan = no_pegawai
            WHERE id_kunjungan = %s
            AND no_identitas_klien = %s
            AND nama_hewan = %s
            AND no_dokter_hewan = %s
            AND no_perawat_hewan = %s
            AND no_front_desk = %s
""", [id_kunjungan, no_identitas_klien, nama_hewan, no_dokter_hewan, no_perawat_hewan, no_front_desk])
        
        email_perawat_hewan = cursor.fetchone()[0]

        cursor.execute("""
            SELECT email_user
            FROM kunjungan join pegawai on no_front_desk = no_pegawai
            WHERE id_kunjungan = %s
            AND no_identitas_klien = %s
            AND nama_hewan = %s
            AND no_dokter_hewan = %s
            AND no_perawat_hewan = %s
            AND no_front_desk = %s
""", [id_kunjungan, no_identitas_klien, nama_hewan, no_dokter_hewan, no_perawat_hewan, no_front_desk])
        
        email_front_desk = cursor.fetchone()[0]

        
        # Get the details for the given kunjungan
        cursor.execute("""
            SELECT no_identitas_klien, nama_hewan, tipe_kunjungan, timestamp_awal, timestamp_akhir
            FROM kunjungan
            WHERE id_kunjungan = %s
            AND no_identitas_klien = %s
            AND nama_hewan = %s
            AND no_dokter_hewan = %s
            AND no_perawat_hewan = %s
            AND no_front_desk = %s
    """, [id_kunjungan, no_identitas_klien, nama_hewan, no_dokter_hewan, no_perawat_hewan, no_front_desk])
        
        kunjungan_data = cursor.fetchone()
        current_klien = kunjungan_data[0]
        current_nama_hewan = kunjungan_data[1]
        current_tipe_kunjungan = kunjungan_data[2]
        current_waktu_mulai = kunjungan_data[3]
        current_waktu_selesai = kunjungan_data[4]
        fmt  = "%Y-%m-%dT%H:%M:%S"                   # titik dua di tengah = ISO

        current_waktu_mulai_iso = current_waktu_mulai.strftime(fmt) if current_waktu_mulai else ''
        current_waktu_selesai_iso = current_waktu_selesai.strftime(fmt) if current_waktu_selesai else ''


        # Get list of available klien, hewan, and metode kunjungan
        cursor.execute("SET search_path TO pet_clinic;")
        
        # 1) Get all ID Klien
        cursor.execute("SELECT no_identitas FROM klien ORDER BY no_identitas;")
        klien_list = [row[0] for row in cursor.fetchall()]
        
        
        
        # 2) Get all Nama Hewan for the selected ID Klien
        cursor.execute("""
            SELECT id_jenis, nama FROM hewan ORDER BY nama;
        """)
        hewan_list = []
        for row in cursor.fetchall():
            hewan_list.append({
                'id': row[0],
                'nama': row[1],
            })

        # 3) Get available metode_kunjungan options
        cursor.execute("""
            SELECT DISTINCT tipe_kunjungan FROM kunjungan ORDER BY tipe_kunjungan;
        """)
        tipe_kunjungan_list = ['Janji Temu','Walk-In','Darurat']

        # 4) Get all available dokter_hewan with their emails and formatted names
        cursor.execute("""
            SELECT 
                k.no_dokter_hewan,
                p.email_user,
                'dr. ' || REPLACE(SUBSTRING(p.email_user FROM 1 FOR POSITION('@' IN p.email_user) - 1), '.', ' ')
            FROM pegawai p
            JOIN dokter_hewan k ON p.no_pegawai = k.no_dokter_hewan
            ORDER BY 3;
            """)
        # Extract and format the doctor list correctly
        dokter_list = []
        for row in cursor.fetchall():
            dokter_list.append({
                'id': row[0],
                'email': row[1],
                'name': row[2]
            })

        # 5) Get all available perawat_hewan with their emails and formatted names
        cursor.execute("""
            SELECT 
                k.no_perawat_hewan,
                p.email_user,
                REPLACE(SUBSTRING(p.email_user FROM 1 FOR POSITION('@' IN p.email_user) - 1), '.', '          ')
            FROM pegawai p
            JOIN perawat_hewan k ON p.no_pegawai = k.no_perawat_hewan
            ORDER BY 3;
            """)
        # Extract and format the nurse list correctly
        perawat_list = []
        for row in cursor.fetchall():
            perawat_list.append({
                'id': row[0],
                'email': row[1],
                'name': row[2]
            })

        cursor.execute("""
            SELECT 
                k.no_front_desk,
                p.email_user,
                REPLACE(SUBSTRING(p.email_user FROM 1 FOR POSITION('@' IN p.email_user) - 1), '.', '          ')
            FROM pegawai p
            JOIN front_desk k ON p.no_pegawai = k.no_front_desk
            ORDER BY 3;
            """)
        # Extract and format the nurse list correctly
        front_desk_list = []
        for row in cursor.fetchall():
            front_desk_list.append({
                'id': row[0],
                'email': row[1],
                'name': row[2]
            })
            
        
    if request.method == "POST":
        # Get the data from form
        input_id_klien        = request.POST.get('id_klien', '').strip()
        input_nama_hewan      = request.POST.get('nama_hewan', '').strip()
        input_metode_kunjungan= request.POST.get('metode_kunjungan', '').strip()
        input_waktu_mulai_penanganan= request.POST.get('timestamp_awal', '').strip()
        input_waktu_selesai_penanganan = request.POST.get('timestamp_akhir', '').strip()
        input_dokter_email    = request.POST.get('dokter_hewan', '').strip()
        input_perawat_email   = request.POST.get('perawat_hewan', '').strip()
        input_front_desk_email= request.POST.get('front_desk', '').strip()

        
        # timestamp_awal = datetime.strptime(waktu_mulai_penanganan, "%Y-%m-%dT%H:%M:%S")
        # timestamp_akhir = datetime.strptime(waktu_selesai_penanganan, "%Y-%m-%dT%H:%M:%S")
        
        required_drop = {
            'id_klien':            input_id_klien,
            'nama_hewan':          input_nama_hewan,
            'metode_kunjungan':    input_metode_kunjungan,
            'dokter_hewan':        input_dokter_email,
            'perawat_hewan':       input_perawat_email,
            'front_desk':          input_front_desk_email,
        }

        for field, value in required_drop.items():
            if not value:                              # ''  atau None
                errors[field] = f'{field.replace("_", " ").title()} wajib dipilih'

        # ----------- VALIDASI WAKTU --------------- #
        if not input_waktu_mulai_penanganan:
            errors['timestamp_awal'] = 'Waktu mulai harus diisi'
        

        dt_awal = dt_akhir = None
        if 'timestamp_awal' not in errors:
            try:
                timestamp_awal = datetime.strptime(input_waktu_mulai_penanganan, "%Y-%m-%dT%H:%M:%S")
            except ValueError:
                errors['timestamp_awal'] = 'Format waktu mulai tidak valid'

        if 'timestamp_akhir' not in errors and input_waktu_selesai_penanganan != '':
            try:
                timestamp_akhir = datetime.strptime(input_waktu_selesai_penanganan, "%Y-%m-%dT%H:%M:%S")
            except ValueError:
                errors['timestamp_akhir'] = 'Format waktu selesai tidak valid'
        


        # ---------- jika ada error, render ulang form ----------
        if errors:
            return render(request, 'update_kunjungan.html', {
                'errors': errors,
                'id_kunjungan': id_kunjungan,
                'klien_list': klien_list,
                'hewan_list': hewan_list,
                'dokter_list': dokter_list,
                'perawat_list': perawat_list,
                'front_desk_list': front_desk_list,
                'tipe_kunjungan_list': tipe_kunjungan_list,
                'current_klien': current_klien,
                'current_nama_hewan': current_nama_hewan,
                'current_tipe_kunjungan': current_tipe_kunjungan,
                'current_waktu_mulai':   current_waktu_mulai_iso,
                'current_waktu_selesai': current_waktu_selesai_iso,
                'email_dokter_hewan' : email_dokter_hewan,
                'email_perawat_hewan' : email_perawat_hewan,
                'email_front_desk' : email_front_desk,
            })

        with connection.cursor() as cursor:
            cursor.execute("SET search_path TO pet_clinic;")

            cursor.execute("""
                SELECT no_pegawai
                FROM PEGAWAI where email_user = %s 
    """, [input_dokter_email])
             
            input_no_dokter_hewan = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT no_pegawai
                FROM PEGAWAI where email_user = %s
    """, [input_perawat_email])
            
            input_no_perawat_hewan = cursor.fetchone()[0]

            cursor.execute("""
                SELECT no_pegawai
                FROM PEGAWAI where email_user = %s              
    """, [input_front_desk_email])
            
            input_no_front_desk = cursor.fetchone()[0]
            try:
                if input_waktu_selesai_penanganan !="":
                
                    cursor.execute("""
                        UPDATE kunjungan
                        SET no_identitas_klien = %s,
                        nama_hewan = %s,
                        tipe_kunjungan = %s,
                        timestamp_awal = %s,
                        timestamp_akhir = %s,
                        no_dokter_hewan = %s,
                        no_perawat_hewan = %s,
                        no_front_desk = %s
                        WHERE id_kunjungan = %s
                        AND no_identitas_klien = %s
                        AND nama_hewan = %s
                        AND no_dokter_hewan = %s
                        AND no_perawat_hewan = %s
                        AND no_front_desk = %s
                    """, [
                        input_id_klien,
                        input_nama_hewan,
                        input_metode_kunjungan,
                        timestamp_awal,
                        timestamp_akhir,
                        input_no_dokter_hewan,
                        input_no_perawat_hewan,
                        input_no_front_desk,
                        id_kunjungan, no_identitas_klien, nama_hewan, no_dokter_hewan, no_perawat_hewan, no_front_desk
                        
                    ])
                else:
                    cursor.execute("""
                        UPDATE kunjungan
                        SET no_identitas_klien = %s,
                        nama_hewan = %s,
                        tipe_kunjungan = %s,
                        timestamp_awal = %s,
                        timestamp_akhir = null,
                        no_dokter_hewan = %s,
                        no_perawat_hewan = %s,
                        no_front_desk = %s
                        WHERE id_kunjungan = %s
                        AND no_identitas_klien = %s
                        AND nama_hewan = %s
                        AND no_dokter_hewan = %s
                        AND no_perawat_hewan = %s
                        AND no_front_desk = %s
                    """, [
                        input_id_klien,
                        input_nama_hewan,
                        input_metode_kunjungan,
                        timestamp_awal,
                        input_no_dokter_hewan,
                        input_no_perawat_hewan,
                        input_no_front_desk,
                        id_kunjungan, no_identitas_klien, nama_hewan, no_dokter_hewan, no_perawat_hewan, no_front_desk
                        
                    ])
                    # Redirect after saving the kunjungan data
                return redirect('daftar_kunjungan_fdo')
            
            except IntegrityError as exc:
                    root   = exc.__cause__                # psycopg2 error instance
                    msg    = str(root).split('CONTEXT:')[0].strip()
                    pgcode = getattr(root, 'pgcode', '')  # contoh '23514'

                    if isinstance(root, pg_err.UniqueViolation) :
                        errors['timestamp_akhir'] = msg
                        
                        return render(request, 'update_kunjungan.html', {
                            'id_kunjungan': id_kunjungan,
                            'klien_list': klien_list,
                            'hewan_list': hewan_list,
                            'dokter_list': dokter_list,
                            'perawat_list': perawat_list,
                            'front_desk_list': front_desk_list,
                            'tipe_kunjungan_list': tipe_kunjungan_list,
                            'current_klien': current_klien,
                            'current_nama_hewan': current_nama_hewan,
                            'current_tipe_kunjungan': current_tipe_kunjungan,
                            'current_waktu_mulai':   current_waktu_mulai_iso,
                            'current_waktu_selesai': current_waktu_selesai_iso,
                            'email_dokter_hewan' : email_dokter_hewan,
                            'email_perawat_hewan' : email_perawat_hewan,
                            'email_front_desk' : email_front_desk,
                            'errors' : errors,
                        })
                    elif pgcode == '23514' or isinstance(root,
                        (pg_err.CheckViolation, pg_err.RaiseException)):

                        if 'Timestamp akhir' in msg:          # trigger waktu
                            errors['timestamp_akhir']= msg

                        elif msg.startswith('ERROR: Hewan'):  # trigger hewan-klien
                            errors['nama_hewan'] = msg

                        else:                                 # pesan lain dari trigger yg sama
                            errors.setdefault('db', msg)
                        return render(request, 'update_kunjungan.html', {
                            'id_kunjungan': id_kunjungan,
                            'klien_list': klien_list,
                            'hewan_list': hewan_list,
                            'dokter_list': dokter_list,
                            'perawat_list': perawat_list,
                            'front_desk_list': front_desk_list,
                            'tipe_kunjungan_list': tipe_kunjungan_list,
                            'current_klien': current_klien,
                            'current_nama_hewan': current_nama_hewan,
                            'current_tipe_kunjungan': current_tipe_kunjungan,
                            'current_waktu_mulai':   current_waktu_mulai_iso,
                            'current_waktu_selesai': current_waktu_selesai_iso,
                            'email_dokter_hewan' : email_dokter_hewan,
                            'email_perawat_hewan' : email_perawat_hewan,
                            'email_front_desk' : email_front_desk,
                            'errors' : errors,
                        })

                    else:
                        errors['db'] = 'Terjadi kesalahan database, coba lagi.'
                        return render(request, 'update_kunjungan.html', {
                            'id_kunjungan': id_kunjungan,
                            'klien_list': klien_list,
                            'hewan_list': hewan_list,
                            'dokter_list': dokter_list,
                            'perawat_list': perawat_list,
                            'front_desk_list': front_desk_list,
                            'tipe_kunjungan_list': tipe_kunjungan_list,
                            'current_klien': current_klien,
                            'current_nama_hewan': current_nama_hewan,
                            'current_tipe_kunjungan': current_tipe_kunjungan,
                            'current_waktu_mulai':   current_waktu_mulai_iso,
                            'current_waktu_selesai': current_waktu_selesai_iso,
                            'email_dokter_hewan' : email_dokter_hewan,
                            'email_perawat_hewan' : email_perawat_hewan,
                            'email_front_desk' : email_front_desk,
                            'errors' : errors,

                        })


    # Fetch the existing values to populate the form
    
    return render(request, 'update_kunjungan.html', {
        'id_kunjungan': id_kunjungan,
        'klien_list': klien_list,
        'hewan_list': hewan_list,
        'dokter_list': dokter_list,
        'perawat_list': perawat_list,
        'front_desk_list': front_desk_list,
        'tipe_kunjungan_list': tipe_kunjungan_list,
        'current_klien': current_klien,
        'current_nama_hewan': current_nama_hewan,
        'current_tipe_kunjungan': current_tipe_kunjungan,
        'current_waktu_mulai':   current_waktu_mulai_iso,
        'current_waktu_selesai': current_waktu_selesai_iso,
        'email_dokter_hewan' : email_dokter_hewan,
        'email_perawat_hewan' : email_perawat_hewan,
        'email_front_desk' : email_front_desk,
        'errors' : errors,

    })


def delete_kunjungan(request, id_kunjungan,no_dokter_hewan,no_perawat_hewan,no_front_desk,nama_hewan,no_identitas_klien):
    # Check if the Kunjungan exists
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute("SET search_path TO pet_clinic;")                   
            cursor.execute("""
                DELETE FROM kunjungan
                    WHERE id_kunjungan = %s
                    AND no_identitas_klien = %s
                    AND nama_hewan = %s
                    AND no_dokter_hewan = %s
                    AND no_perawat_hewan = %s
                    AND no_front_desk = %s
            """, [id_kunjungan, no_identitas_klien, nama_hewan, no_dokter_hewan, no_perawat_hewan, no_front_desk])
        return redirect('daftar_kunjungan_fdo')

    # If the method is GET, return a confirmation page or the same template
    return redirect('daftar_kunjungan_fdo')





def create_rekam_medis(request, id_kunjungan, no_dokter_hewan, no_perawat_hewan, no_front_desk, nama_hewan, no_identitas_klien):
    # Get the relevant kunjungan data based on id_kunjungan
    errors ={}
    if 'user_email' not in request.session:
        return redirect('login')

    user_email = request.session['user_email']

    with connection.cursor() as cursor:
        # Cari no_pegawai dari email
        cursor.execute("SET SEARCH_PATH TO PET_CLINIC;")

        cursor.execute("SELECT no_pegawai FROM pegawai WHERE email_user = %s", [user_email])
        result = cursor.fetchone()
        if not result:
            # Email tidak ditemukan di pegawai
            return redirect('login')

        no_pegawai = result[0]

        # Cek apakah no_pegawai ini ada di tabel front_desk
        cursor.execute("SELECT 1 FROM dokter_hewan WHERE no_dokter_hewan = %s", [no_pegawai])
        is_fdo = cursor.fetchone()
        if not is_fdo:
            # Jika no_pegawai tidak ada di front_desk, redirect login
            return redirect('login')
        
    if request.method == "POST":
        suhu = request.POST.get('suhu').strip().strip()
        berat_badan = request.POST.get('berat_badan').strip()
        catatan = request.POST.get('catatan', '').strip()
        print(catatan)

        # Insert the data into rekam_medis
        if (suhu != '' and suhu is not None) and (berat_badan != '' and berat_badan is not None):
            print("hello")
            with connection.cursor() as cursor:
                cursor.execute("SET search_path TO pet_clinic;")
                cursor.execute("""
                    UPDATE kunjungan
                    SET suhu = %s, berat_badan = %s
                    WHERE id_kunjungan = %s
                    AND no_dokter_hewan = %s
                    AND no_perawat_hewan = %s
                    AND no_front_desk = %s
                    AND nama_hewan = %s
                    AND no_identitas_klien = %s
                """, [suhu, berat_badan, id_kunjungan, no_dokter_hewan, no_perawat_hewan, no_front_desk, nama_hewan, no_identitas_klien])
                
        elif (suhu != '' and suhu is not None) and (berat_badan == '' or berat_badan is  None):
            print("halikosng")
            with connection.cursor() as cursor:
                cursor.execute("SET search_path TO pet_clinic;")
                cursor.execute("""
                    UPDATE kunjungan
                    SET suhu = %s
                    WHERE id_kunjungan = %s
                    AND no_dokter_hewan = %s
                    AND no_perawat_hewan = %s
                    AND no_front_desk = %s
                    AND nama_hewan = %s
                    AND no_identitas_klien = %s
                """, [suhu, id_kunjungan, no_dokter_hewan, no_perawat_hewan, no_front_desk, nama_hewan, no_identitas_klien])
                
        elif (berat_badan != '' and berat_badan is not None) and (suhu == '' or suhu is  None):
            print("yohoo")
            with connection.cursor() as cursor:
                cursor.execute("SET search_path TO pet_clinic;")
                cursor.execute("""
                    UPDATE kunjungan
                    SET berat_badan = %s
                    WHERE id_kunjungan = %s
                    AND no_dokter_hewan = %s
                    AND no_perawat_hewan = %s
                    AND no_front_desk = %s
                    AND nama_hewan = %s
                    AND no_identitas_klien = %s
                """, [ berat_badan, id_kunjungan, no_dokter_hewan, no_perawat_hewan, no_front_desk, nama_hewan, no_identitas_klien])
        else:
            if catatan != '' and catatan is not None:
                print("ololololol")
                with connection.cursor() as cursor:
                    cursor.execute("SET search_path TO pet_clinic;")
                    cursor.execute("""
                        UPDATE kunjungan
                        SET  catatan = %s, berat_badan = null, suhu = null
                        WHERE id_kunjungan = %s
                        AND no_dokter_hewan = %s
                        AND no_perawat_hewan = %s
                        AND no_front_desk = %s
                        AND nama_hewan = %s
                        AND no_identitas_klien = %s
                    """, [catatan, id_kunjungan, no_dokter_hewan, no_perawat_hewan, no_front_desk, nama_hewan, no_identitas_klien])
                    
                messages.success(request, 'Rekam medis berhasil dibuat!')
                return redirect('rekam_medis_view' ,id_kunjungan, no_dokter_hewan, no_perawat_hewan, no_front_desk, nama_hewan, no_identitas_klien )
            else:

                errors['error'] = 'Harus mengisi setidaknya salah satu dari ketiga field !'
                return render(request, 'create_rekam_medis.html', {
                    'errors': errors,
                })
                
        if catatan != '' and catatan is not None:
            with connection.cursor() as cursor:
                cursor.execute("SET search_path TO pet_clinic;")
                cursor.execute("""
                    UPDATE kunjungan
                    SET  catatan = %s
                    WHERE id_kunjungan = %s
                    AND no_dokter_hewan = %s
                    AND no_perawat_hewan = %s
                    AND no_front_desk = %s
                    AND nama_hewan = %s
                    AND no_identitas_klien = %s
                """, [catatan, id_kunjungan, no_dokter_hewan, no_perawat_hewan, no_front_desk, nama_hewan, no_identitas_klien])
        else:
           with connection.cursor() as cursor:
                cursor.execute("SET search_path TO pet_clinic;")
                cursor.execute("""
                    UPDATE kunjungan
                    SET  catatan = null
                    WHERE id_kunjungan = %s
                    AND no_dokter_hewan = %s
                    AND no_perawat_hewan = %s
                    AND no_front_desk = %s
                    AND nama_hewan = %s
                    AND no_identitas_klien = %s
                """, [ id_kunjungan, no_dokter_hewan, no_perawat_hewan, no_front_desk, nama_hewan, no_identitas_klien]) 
        # Success message
        messages.success(request, 'Rekam medis berhasil dibuat!')

        # Render the same page (view_rekam_medis) with the updated Rekam Medis data
        return redirect('rekam_medis_view' ,id_kunjungan, no_dokter_hewan, no_perawat_hewan, no_front_desk, nama_hewan, no_identitas_klien )
    # Get the list of jenis perawatan
    with connection.cursor() as cursor:
        cursor.execute("SET search_path TO pet_clinic;")
        cursor.execute("""
            SELECT kode_perawatan, nama_perawatan FROM perawatan
            ORDER BY kode_perawatan
        """)
        jenis_perawatan_list = cursor.fetchall()

    return render(request, 'create_rekam_medis.html')








from django.shortcuts import render, redirect
from django.db import connection
from django.contrib import messages

def update_rekam_medis(request, id_kunjungan, no_dokter_hewan, no_perawat_hewan, no_front_desk, nama_hewan, no_identitas_klien):
    if 'user_email' not in request.session:
        return redirect('login')

    user_email = request.session['user_email']

    with connection.cursor() as cursor:
        # Cari no_pegawai dari email
        cursor.execute("SET SEARCH_PATH TO PET_CLINIC;")

        cursor.execute("SELECT no_pegawai FROM pegawai WHERE email_user = %s", [user_email])
        result = cursor.fetchone()
        if not result:
            # Email tidak ditemukan di pegawai
            return redirect('login')

        no_pegawai = result[0]

        # Cek apakah no_pegawai ini ada di tabel front_desk
        cursor.execute("SELECT 1 FROM dokter_hewan WHERE no_dokter_hewan = %s", [no_pegawai])
        is_fdo = cursor.fetchone()
        if not is_fdo:
            # Jika no_pegawai tidak ada di front_desk, redirect login
            return redirect('login')
    
    errors ={}
    if request.method == "POST":
        suhu = request.POST.get('suhu')
        berat_badan = request.POST.get('berat_badan')
        catatan = request.POST.get('catatan', '').strip()
        print(catatan)

        # Update the rekam medis for this kunjungan
        if (suhu != '' and suhu is not None) and (berat_badan != '' and berat_badan is not None):
            with connection.cursor() as cursor:
                cursor.execute("SET search_path TO pet_clinic;")
                cursor.execute("""
                    UPDATE kunjungan
                    SET suhu = %s, berat_badan = %s
                    WHERE id_kunjungan = %s
                    AND no_dokter_hewan = %s
                    AND no_perawat_hewan = %s
                    AND no_front_desk = %s
                    AND nama_hewan = %s
                    AND no_identitas_klien = %s
                """, [suhu, berat_badan, id_kunjungan, no_dokter_hewan, no_perawat_hewan, no_front_desk, nama_hewan, no_identitas_klien])
                
        elif (suhu != '' and suhu is not None) and (berat_badan == '' or berat_badan is  None):
            with connection.cursor() as cursor:
                cursor.execute("SET search_path TO pet_clinic;")
                cursor.execute("""
                    UPDATE kunjungan
                    SET suhu = %s,berat_badan = null
                    WHERE id_kunjungan = %s
                    AND no_dokter_hewan = %s
                    AND no_perawat_hewan = %s
                    AND no_front_desk = %s
                    AND nama_hewan = %s
                    AND no_identitas_klien = %s
                """, [suhu, id_kunjungan, no_dokter_hewan, no_perawat_hewan, no_front_desk, nama_hewan, no_identitas_klien])
                
        elif (berat_badan != '' and berat_badan is not None) and (suhu == '' or suhu is  None):
            with connection.cursor() as cursor:
                cursor.execute("SET search_path TO pet_clinic;")
                cursor.execute("""
                    UPDATE kunjungan
                    SET berat_badan = %s, suhu = null
                    WHERE id_kunjungan = %s
                    AND no_dokter_hewan = %s
                    AND no_perawat_hewan = %s
                    AND no_front_desk = %s
                    AND nama_hewan = %s
                    AND no_identitas_klien = %s
                """, [ berat_badan, id_kunjungan, no_dokter_hewan, no_perawat_hewan, no_front_desk, nama_hewan, no_identitas_klien])
        else:
            if catatan != '' and catatan is not None:
                with connection.cursor() as cursor:
                    cursor.execute("SET search_path TO pet_clinic;")
                    cursor.execute("""
                        UPDATE kunjungan
                        SET  catatan = %s , berat_badan = null, suhu = null
                        WHERE id_kunjungan = %s
                        AND no_dokter_hewan = %s
                        AND no_perawat_hewan = %s
                        AND no_front_desk = %s
                        AND nama_hewan = %s
                        AND no_identitas_klien = %s
                    """, [catatan, id_kunjungan, no_dokter_hewan, no_perawat_hewan, no_front_desk, nama_hewan, no_identitas_klien])
                    
                messages.success(request, 'Rekam medis berhasil dibuat!')
                return redirect('rekam_medis_view' ,id_kunjungan, no_dokter_hewan, no_perawat_hewan, no_front_desk, nama_hewan, no_identitas_klien )
            else:
                errors['error'] = 'Harus mengisi setidaknya salah satu dari ketiga field !'
                with connection.cursor() as cursor:
                    cursor.execute("SET search_path TO pet_clinic;")
                    cursor.execute("""
                        SELECT
                            k.id_kunjungan,
                            k.no_identitas_klien,
                            k.no_dokter_hewan,
                            k.no_perawat_hewan,
                            k.no_front_desk,
                            k.nama_hewan,
                            k.tipe_kunjungan,
                            k.suhu,
                            k.berat_badan,
                            r.kode_perawatan,
                            k.catatan
                        FROM kunjungan k
                        LEFT JOIN kunjungan_keperawatan r ON k.id_kunjungan = r.id_kunjungan 
                        and k.no_identitas_klien = r.no_identitas_klien
                        and k.nama_hewan = r.nama_hewan
                        and k.no_perawat_hewan = r.no_perawat_hewan
                        and k.no_dokter_hewan = r.no_dokter_hewan
                        and k.no_front_desk = r.no_front_desk
                        WHERE k.id_kunjungan = %s
                    """, [id_kunjungan])
                    kunjungan_data = cursor.fetchone()

                # Get the list of jenis perawatan for the dropdown menu
                with connection.cursor() as cursor:
                    cursor.execute("SET search_path TO pet_clinic;")
                    cursor.execute("""
                        SELECT kode_perawatan, nama_perawatan FROM perawatan
                        ORDER BY kode_perawatan
                    """)
                    jenis_perawatan_list = cursor.fetchall()
                    
                if kunjungan_data[10] is None:
                    catatan = ''
                else:
                    catatan = kunjungan_data[10]

                return render(request, 'update_rekam_medis.html', {
                    'id_kunjungan': id_kunjungan,
                    'no_identitas_klien': kunjungan_data[1],
                    'no_dokter_hewan': kunjungan_data[2],
                    'no_perawat_hewan': kunjungan_data[3],
                    'no_front_desk': kunjungan_data[4],
                    'nama_hewan': kunjungan_data[5],
                    'suhu': kunjungan_data[7],  # Suhu from rekam medis
                    'berat_badan': kunjungan_data[8],  # Berat badan from rekam medis
                    'catatan': catatan,  # Catatan from rekam medis
                    'jenis_perawatan_list': jenis_perawatan_list,
                    'errors':errors,
                })
                            
        if catatan != '' and catatan is not None:
            with connection.cursor() as cursor:
                cursor.execute("SET search_path TO pet_clinic;")
                cursor.execute("""
                    UPDATE kunjungan
                    SET  catatan = %s
                    WHERE id_kunjungan = %s
                    AND no_dokter_hewan = %s
                    AND no_perawat_hewan = %s
                    AND no_front_desk = %s
                    AND nama_hewan = %s
                    AND no_identitas_klien = %s
                """, [catatan, id_kunjungan, no_dokter_hewan, no_perawat_hewan, no_front_desk, nama_hewan, no_identitas_klien])
        else:
           with connection.cursor() as cursor:
                cursor.execute("SET search_path TO pet_clinic;")
                cursor.execute("""
                    UPDATE kunjungan
                    SET  catatan = null
                    WHERE id_kunjungan = %s
                    AND no_dokter_hewan = %s
                    AND no_perawat_hewan = %s
                    AND no_front_desk = %s
                    AND nama_hewan = %s
                    AND no_identitas_klien = %s
                """, [ id_kunjungan, no_dokter_hewan, no_perawat_hewan, no_front_desk, nama_hewan, no_identitas_klien]) 
        
        # Redirect to view the updated rekam medis (render view instead of redirect)
        rekam_medis_context = {
            'suhu': suhu,
            'berat_badan': berat_badan,
            'catatan': catatan,
            'id_kunjungan': id_kunjungan
        }

        # Success message
        messages.success(request, 'Rekam medis berhasil dibuat!')

        # Render the same page (view_rekam_medis) with the updated Rekam Medis data
        return redirect('rekam_medis_view' ,id_kunjungan, no_dokter_hewan, no_perawat_hewan, no_front_desk, nama_hewan, no_identitas_klien )
    # If the method is GET, fetch the current rekam medis data to populate the form
    with connection.cursor() as cursor:
        cursor.execute("SET search_path TO pet_clinic;")
        cursor.execute("""
            SELECT
                k.id_kunjungan,
                k.no_identitas_klien,
                k.no_dokter_hewan,
                k.no_perawat_hewan,
                k.no_front_desk,
                k.nama_hewan,
                k.tipe_kunjungan,
                k.suhu,
                k.berat_badan,
                r.kode_perawatan,
                k.catatan
            FROM kunjungan k
            LEFT JOIN kunjungan_keperawatan r ON k.id_kunjungan = r.id_kunjungan 
            and k.no_identitas_klien = r.no_identitas_klien
            and k.nama_hewan = r.nama_hewan
            and k.no_perawat_hewan = r.no_perawat_hewan
            and k.no_dokter_hewan = r.no_dokter_hewan
            and k.no_front_desk = r.no_front_desk
            WHERE k.id_kunjungan = %s
        """, [id_kunjungan])
        kunjungan_data = cursor.fetchone()

    # Get the list of jenis perawatan for the dropdown menu
    with connection.cursor() as cursor:
        cursor.execute("SET search_path TO pet_clinic;")
        cursor.execute("""
            SELECT kode_perawatan, nama_perawatan FROM perawatan
            ORDER BY kode_perawatan
        """)
        jenis_perawatan_list = cursor.fetchall()
        
    if kunjungan_data[10] is None:
        catatan = ''
    else:
        catatan = kunjungan_data[10]

    return render(request, 'update_rekam_medis.html', {
        'id_kunjungan': id_kunjungan,
        'no_identitas_klien': kunjungan_data[1],
        'no_dokter_hewan': kunjungan_data[2],
        'no_perawat_hewan': kunjungan_data[3],
        'no_front_desk': kunjungan_data[4],
        'nama_hewan': kunjungan_data[5],
        'suhu': kunjungan_data[7],  # Suhu from rekam medis
        'berat_badan': kunjungan_data[8],  # Berat badan from rekam medis
        'catatan': catatan,  # Catatan from rekam medis
        'jenis_perawatan_list': jenis_perawatan_list
    })
    


def rekam_medis_view(request, id_kunjungan, no_dokter_hewan, no_perawat_hewan, no_front_desk, nama_hewan, no_identitas_klien):
    if 'user_email' not in request.session:
        return redirect('login')

    user_email = request.session['user_email']

    with connection.cursor() as cursor:
        # Cari no_pegawai dari email
        cursor.execute("SET SEARCH_PATH TO PET_CLINIC;")

        cursor.execute("SELECT no_pegawai FROM pegawai WHERE email_user = %s", [user_email])
        result = cursor.fetchone()
        if not result:
            # Email tidak ditemukan di pegawai
            return redirect('login')

        no_pegawai = result[0]

        # Cek apakah no_pegawai ini ada di tabel front_desk
        cursor.execute("SELECT 1 FROM dokter_hewan WHERE no_dokter_hewan = %s", [no_pegawai])
        is_fdo = cursor.fetchone()
        if not is_fdo:
            # Jika no_pegawai tidak ada di front_desk, redirect login
            return redirect('login')
        
    with connection.cursor() as cursor:
        cursor.execute("SET search_path TO pet_clinic;")
        
        # Ambil suhu dan berat badan dari kunjungan berdasarkan composite PK
        cursor.execute("""
            SELECT suhu, berat_badan
            FROM kunjungan
            WHERE id_kunjungan = %s
              AND no_dokter_hewan = %s
              AND no_perawat_hewan = %s
              AND no_front_desk = %s
              AND nama_hewan = %s
              AND no_identitas_klien = %s
        """, [id_kunjungan, no_dokter_hewan, no_perawat_hewan, no_front_desk, nama_hewan, no_identitas_klien])
        kunjungan_data = cursor.fetchone()

        # Ambil catatan dari kunjungan_keperawatan berdasarkan id_kunjungan (biasanya cukup id_kunjungan sebagai FK)
        cursor.execute("""
            SELECT catatan
            FROM kunjungan
             WHERE id_kunjungan = %s
              AND no_dokter_hewan = %s
              AND no_perawat_hewan = %s
              AND no_front_desk = %s
              AND nama_hewan = %s
              AND no_identitas_klien = %s
             
        """, [id_kunjungan, no_dokter_hewan, no_perawat_hewan, no_front_desk, nama_hewan, no_identitas_klien])
        catatan_data = cursor.fetchone()
        print(catatan_data)

    # Inisialisasi variabel hasil dengan format sesuai request
    suhu = berat_badan = catatan = None

    if kunjungan_data:
        suhu = kunjungan_data[0] if kunjungan_data[0] is not None else "-"
        berat_badan = kunjungan_data[1] if kunjungan_data[1] is not None else "-"

    if catatan_data:
        catatan = catatan_data[0] if catatan_data[0] is not None else ""

    return render(request, 'rekam_medis_view.html', {
        'suhu': suhu,
        'berat_badan': berat_badan,
        'catatan': catatan,
        'id_kunjungan': id_kunjungan,
        'no_dokter_hewan':no_dokter_hewan, 
        'no_perawat_hewan':no_perawat_hewan, 
        'no_front_desk':no_front_desk, 
        'nama_hewan':nama_hewan, 
        'no_identitas_klien':no_identitas_klien
    })
    
def rekam_medis_view_klien(request, id_kunjungan, no_dokter_hewan, no_perawat_hewan, no_front_desk, nama_hewan, no_identitas_klien):
    if 'user_email' not in request.session:
        return redirect('login')

    user_email = request.session['user_email']

    with connection.cursor() as cursor:
        # Cari no_pegawai dari email
        cursor.execute("SET SEARCH_PATH TO PET_CLINIC;")

        cursor.execute("SELECT no_identitas FROM klien WHERE email = %s", [user_email])
        result = cursor.fetchone()
        if not result:
            # Email tidak ditemukan di pegawai
            return redirect('login')
        
    with connection.cursor() as cursor:
        cursor.execute("SET search_path TO pet_clinic;")
        
        # Ambil suhu dan berat badan dari kunjungan berdasarkan composite PK
        cursor.execute("""
            SELECT suhu, berat_badan
            FROM kunjungan
            WHERE id_kunjungan = %s
              AND no_dokter_hewan = %s
              AND no_perawat_hewan = %s
              AND no_front_desk = %s
              AND nama_hewan = %s
              AND no_identitas_klien = %s
        """, [id_kunjungan, no_dokter_hewan, no_perawat_hewan, no_front_desk, nama_hewan, no_identitas_klien])
        kunjungan_data = cursor.fetchone()

        # Ambil catatan dari kunjungan_keperawatan berdasarkan id_kunjungan (biasanya cukup id_kunjungan sebagai FK)
        cursor.execute("""
            SELECT catatan
            FROM kunjungan
             WHERE id_kunjungan = %s
              AND no_dokter_hewan = %s
              AND no_perawat_hewan = %s
              AND no_front_desk = %s
              AND nama_hewan = %s
              AND no_identitas_klien = %s
              LIMIT 1
        """, [id_kunjungan, no_dokter_hewan, no_perawat_hewan, no_front_desk, nama_hewan, no_identitas_klien])
        catatan_data = cursor.fetchone()
        print(catatan_data)

    # Inisialisasi variabel hasil dengan format sesuai request
    suhu = berat_badan = catatan = None

    if kunjungan_data:
        suhu = kunjungan_data[0] if kunjungan_data[0] is not None else "-"
        berat_badan = kunjungan_data[1] if kunjungan_data[1] is not None else "-"

    if catatan_data:
        catatan = catatan_data[0] if catatan_data[0] is not None else ""

    return render(request, 'rekam_medis_view_klien.html', {
        'suhu': suhu,
        'berat_badan': berat_badan,
        'catatan': catatan,
        'id_kunjungan': id_kunjungan,
        'no_dokter_hewan':no_dokter_hewan, 
        'no_perawat_hewan':no_perawat_hewan, 
        'no_front_desk':no_front_desk, 
        'nama_hewan':nama_hewan, 
        'no_identitas_klien':no_identitas_klien
    })
    
def rekam_medis_view_perawat(request, id_kunjungan, no_dokter_hewan, no_perawat_hewan, no_front_desk, nama_hewan, no_identitas_klien):
    if 'user_email' not in request.session:
        return redirect('login')

    user_email = request.session['user_email']

    with connection.cursor() as cursor:
        # Cari no_pegawai dari email
        cursor.execute("SET SEARCH_PATH TO PET_CLINIC;")

        cursor.execute("SELECT no_pegawai FROM pegawai WHERE email_user = %s", [user_email])
        result = cursor.fetchone()
        if not result:
            # Email tidak ditemukan di pegawai
            return redirect('login')

        no_pegawai = result[0]

        # Cek apakah no_pegawai ini ada di tabel perawat_hewan
        cursor.execute("SELECT 1 FROM perawat_hewan WHERE no_perawat_hewan = %s", [no_pegawai])
        is_dokter = cursor.fetchone()
        if not is_dokter:
            # Jika no_pegawai tidak ada di perawat_hewan, redirect login
            return redirect('login')
        
    with connection.cursor() as cursor:
        cursor.execute("SET search_path TO pet_clinic;")
        
        # Ambil suhu dan berat badan dari kunjungan berdasarkan composite PK
        cursor.execute("""
            SELECT suhu, berat_badan
            FROM kunjungan
            WHERE id_kunjungan = %s
              AND no_dokter_hewan = %s
              AND no_perawat_hewan = %s
              AND no_front_desk = %s
              AND nama_hewan = %s
              AND no_identitas_klien = %s
        """, [id_kunjungan, no_dokter_hewan, no_perawat_hewan, no_front_desk, nama_hewan, no_identitas_klien])
        kunjungan_data = cursor.fetchone()

        # Ambil catatan dari kunjungan_keperawatan berdasarkan id_kunjungan (biasanya cukup id_kunjungan sebagai FK)
        cursor.execute("""
            SELECT catatan
            FROM kunjungan
             WHERE id_kunjungan = %s
              AND no_dokter_hewan = %s
              AND no_perawat_hewan = %s
              AND no_front_desk = %s
              AND nama_hewan = %s
              AND no_identitas_klien = %s
              LIMIT 1
        """, [id_kunjungan, no_dokter_hewan, no_perawat_hewan, no_front_desk, nama_hewan, no_identitas_klien])
        catatan_data = cursor.fetchone()
        print(catatan_data)

    # Inisialisasi variabel hasil dengan format sesuai request
    suhu = berat_badan = catatan = None

    if kunjungan_data:
        suhu = kunjungan_data[0] if kunjungan_data[0] is not None else "-"
        berat_badan = kunjungan_data[1] if kunjungan_data[1] is not None else "-"

    if catatan_data:
        catatan = catatan_data[0] if catatan_data[0] is not None else ""

    return render(request, 'rekam_medis_view_perawat.html', {
        'suhu': suhu,
        'berat_badan': berat_badan,
        'catatan': catatan,
        'id_kunjungan': id_kunjungan,
        'no_dokter_hewan':no_dokter_hewan, 
        'no_perawat_hewan':no_perawat_hewan, 
        'no_front_desk':no_front_desk, 
        'nama_hewan':nama_hewan, 
        'no_identitas_klien':no_identitas_klien
    })
    
def rekam_medis_view_fdo(request, id_kunjungan, no_dokter_hewan, no_perawat_hewan, no_front_desk, nama_hewan, no_identitas_klien):
    if 'user_email' not in request.session:
        return redirect('login')

    user_email = request.session['user_email']

    with connection.cursor() as cursor:
        # Cari no_pegawai dari email
        cursor.execute("SET SEARCH_PATH TO PET_CLINIC;")

        cursor.execute("SELECT no_pegawai FROM pegawai WHERE email_user = %s", [user_email])
        result = cursor.fetchone()
        if not result:
            # Email tidak ditemukan di pegawai
            return redirect('login')

        no_pegawai = result[0]

        # Cek apakah no_pegawai ini ada di tabel front_desk
        cursor.execute("SELECT 1 FROM front_desk WHERE no_front_desk = %s", [no_pegawai])
        is_fdo = cursor.fetchone()
        if not is_fdo:
            # Jika no_pegawai tidak ada di front_desk, redirect login
            return redirect('login')
        
    with connection.cursor() as cursor:
        cursor.execute("SET search_path TO pet_clinic;")
        
        # Ambil suhu dan berat badan dari kunjungan berdasarkan composite PK
        cursor.execute("""
            SELECT suhu, berat_badan
            FROM kunjungan
            WHERE id_kunjungan = %s
              AND no_dokter_hewan = %s
              AND no_perawat_hewan = %s
              AND no_front_desk = %s
              AND nama_hewan = %s
              AND no_identitas_klien = %s
        """, [id_kunjungan, no_dokter_hewan, no_perawat_hewan, no_front_desk, nama_hewan, no_identitas_klien])
        kunjungan_data = cursor.fetchone()

        # Ambil catatan dari kunjungan_keperawatan berdasarkan id_kunjungan (biasanya cukup id_kunjungan sebagai FK)
        cursor.execute("""
            SELECT catatan
            FROM kunjungan
             WHERE id_kunjungan = %s
              AND no_dokter_hewan = %s
              AND no_perawat_hewan = %s
              AND no_front_desk = %s
              AND nama_hewan = %s
              AND no_identitas_klien = %s
              LIMIT 1
        """, [id_kunjungan, no_dokter_hewan, no_perawat_hewan, no_front_desk, nama_hewan, no_identitas_klien])
        catatan_data = cursor.fetchone()
        print(catatan_data)

    # Inisialisasi variabel hasil dengan format sesuai request
    suhu = berat_badan = catatan = None

    if kunjungan_data:
        suhu = kunjungan_data[0] if kunjungan_data[0] is not None else "-"
        berat_badan = kunjungan_data[1] if kunjungan_data[1] is not None else "-"

    if catatan_data:
        catatan = catatan_data[0] if catatan_data[0] is not None else ""

    return render(request, 'rekam_medis_view_fdo.html', {
        'suhu': suhu,
        'berat_badan': berat_badan,
        'catatan': catatan,
        'id_kunjungan': id_kunjungan,
        'no_dokter_hewan':no_dokter_hewan, 
        'no_perawat_hewan':no_perawat_hewan, 
        'no_front_desk':no_front_desk, 
        'nama_hewan':nama_hewan, 
        'no_identitas_klien':no_identitas_klien
    })

