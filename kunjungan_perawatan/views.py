from django.shortcuts import render
from django.shortcuts import render
from django.db import connection
from django.shortcuts import render, redirect
from django.db import connection
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.db import connection
from django.http import Http404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db import connection, transaction, IntegrityError
from psycopg2           import errors as pg_err    
from psycopg2.errors import CheckViolation
from psycopg2 import errors as pg_err   # import semua mapping error psycopg2



def daftar_perawatan(request):
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

        # Cek apakah no_pegawai ini ada di tabel dokter_hewan
        cursor.execute("SELECT 1 FROM dokter_hewan WHERE no_dokter_hewan = %s", [no_pegawai])
        is_dokter = cursor.fetchone()
        if not is_dokter:
            # Jika no_pegawai tidak ada di dokter_hewan, redirect login
            return redirect('login')

    with connection.cursor() as cursor:
        # Set search_path ke schema yang tepat
        cursor.execute("SET search_path TO pet_clinic;")

        # Ambil data dari tabel kunjungan_keperawatan
        cursor.execute("""
            SELECT
                k.id_kunjungan,
                k.nama_hewan,
                k.no_identitas_klien,
                k.no_front_desk,
                k.no_perawat_hewan,
                k.no_dokter_hewan,
                k.kode_perawatan,
                p.nama_perawatan,
                -- Ambil email dari tabel pegawai yang sesuai dengan perawat_hewan
                (SELECT email_user FROM pegawai WHERE no_pegawai = k.no_perawat_hewan LIMIT 1) AS perawat_email,
                -- Ambil email dari tabel pegawai yang sesuai dengan dokter_hewan
                (SELECT email_user FROM pegawai WHERE no_pegawai = k.no_dokter_hewan LIMIT 1) AS dokter_email,
                -- Ambil email dari tabel pegawai yang sesuai dengan front_desk
                (SELECT email_user FROM pegawai WHERE no_pegawai = k.no_front_desk LIMIT 1) AS fdo_email
            FROM KUNJUNGAN_KEPERAWATAN k
            LEFT JOIN PERAWATAN p ON k.kode_perawatan = p.kode_perawatan
            ORDER BY k.id_kunjungan
        """)

        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()

    treatments = []
    for row in rows:
        treatment = dict(zip(columns, row))

        # Fungsi untuk menghapus titik dan @example.com dari email
        def clean_email(email):
            if email:
                return email.split('@')[0].replace('.', ' ')  # Hapus titik dan ambil sebelum '@'
            return email

        # Format email untuk dokter agar diawali dengan "dr."
        if treatment['dokter_email']:
            treatment['dokter_email'] = "dr." + clean_email(treatment['dokter_email']).capitalize()

        # Format email untuk perawat dan fdo agar diawali dengan huruf kapital
        if treatment['perawat_email']:
            treatment['perawat_email'] = clean_email(treatment['perawat_email']).capitalize()
        
        if treatment['fdo_email']:
            treatment['fdo_email'] = clean_email(treatment['fdo_email']).capitalize()

        treatments.append(treatment)

    return render(request, 'daftar_perawatan.html', {
        'treatments': treatments
    })
    
def daftar_perawatan_fdo(request):
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
        # Set search_path ke schema yang tepat
        cursor.execute("SET search_path TO pet_clinic;")

        # Ambil data dari tabel kunjungan_keperawatan
        cursor.execute("""
            SELECT
                k.id_kunjungan,
                k.nama_hewan,
                k.no_identitas_klien,
                k.no_front_desk,
                k.no_perawat_hewan,
                k.no_dokter_hewan,
                k.kode_perawatan,
                p.nama_perawatan,
                -- Ambil email dari tabel pegawai yang sesuai dengan perawat_hewan
                (SELECT email_user FROM pegawai WHERE no_pegawai = k.no_perawat_hewan LIMIT 1) AS perawat_email,
                -- Ambil email dari tabel pegawai yang sesuai dengan dokter_hewan
                (SELECT email_user FROM pegawai WHERE no_pegawai = k.no_dokter_hewan LIMIT 1) AS dokter_email,
                -- Ambil email dari tabel pegawai yang sesuai dengan front_desk
                (SELECT email_user FROM pegawai WHERE no_pegawai = k.no_front_desk LIMIT 1) AS fdo_email
            FROM KUNJUNGAN_KEPERAWATAN k
            LEFT JOIN PERAWATAN p ON k.kode_perawatan = p.kode_perawatan
            ORDER BY k.id_kunjungan
        """)

        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()

    treatments = []
    for row in rows:
        treatment = dict(zip(columns, row))

        # Fungsi untuk menghapus titik dan @example.com dari email
        def clean_email(email):
            if email:
                return email.split('@')[0].replace('.', ' ')  # Hapus titik dan ambil sebelum '@'
            return email

        # Format email untuk dokter agar diawali dengan "dr."
        if treatment['dokter_email']:
            treatment['dokter_email'] = "dr." + clean_email(treatment['dokter_email']).capitalize()

        # Format email untuk perawat dan fdo agar diawali dengan huruf kapital
        if treatment['perawat_email']:
            treatment['perawat_email'] = clean_email(treatment['perawat_email']).capitalize()
        
        if treatment['fdo_email']:
            treatment['fdo_email'] = clean_email(treatment['fdo_email']).capitalize()

        treatments.append(treatment)

    return render(request, 'daftar_perawatan_fdo.html', {
        'treatments': treatments
    })
    
    
def daftar_perawatan_perawat(request):
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
        # Set search_path ke schema yang tepat
        cursor.execute("SET search_path TO pet_clinic;")

        # Ambil data dari tabel kunjungan_keperawatan
        cursor.execute("""
            SELECT
                k.id_kunjungan,
                k.nama_hewan,
                k.no_identitas_klien,
                k.no_front_desk,
                k.no_perawat_hewan,
                k.no_dokter_hewan,
                k.kode_perawatan,
                p.nama_perawatan,
                -- Ambil email dari tabel pegawai yang sesuai dengan perawat_hewan
                (SELECT email_user FROM pegawai WHERE no_pegawai = k.no_perawat_hewan LIMIT 1) AS perawat_email,
                -- Ambil email dari tabel pegawai yang sesuai dengan dokter_hewan
                (SELECT email_user FROM pegawai WHERE no_pegawai = k.no_dokter_hewan LIMIT 1) AS dokter_email,
                -- Ambil email dari tabel pegawai yang sesuai dengan front_desk
                (SELECT email_user FROM pegawai WHERE no_pegawai = k.no_front_desk LIMIT 1) AS fdo_email
            FROM KUNJUNGAN_KEPERAWATAN k
            LEFT JOIN PERAWATAN p ON k.kode_perawatan = p.kode_perawatan
            ORDER BY k.id_kunjungan
        """)

        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()

    treatments = []
    for row in rows:
        treatment = dict(zip(columns, row))

        # Fungsi untuk menghapus titik dan @example.com dari email
        def clean_email(email):
            if email:
                return email.split('@')[0].replace('.', ' ')  # Hapus titik dan ambil sebelum '@'
            return email

        # Format email untuk dokter agar diawali dengan "dr."
        if treatment['dokter_email']:
            treatment['dokter_email'] = "dr." + clean_email(treatment['dokter_email']).capitalize()

        # Format email untuk perawat dan fdo agar diawali dengan huruf kapital
        if treatment['perawat_email']:
            treatment['perawat_email'] = clean_email(treatment['perawat_email']).capitalize()
        
        if treatment['fdo_email']:
            treatment['fdo_email'] = clean_email(treatment['fdo_email']).capitalize()

        treatments.append(treatment)

    return render(request, 'daftar_perawatan_perawat.html', {
        'treatments': treatments
    })

    
def daftar_perawatan_klien(request):
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
        # Set search_path ke schema yang tepat
        cursor.execute("SET search_path TO pet_clinic;")

        # Ambil data dari tabel kunjungan_keperawatan
        cursor.execute("""
            SELECT
                k.id_kunjungan,
                k.nama_hewan,
                k.no_identitas_klien,
                k.no_front_desk,
                k.no_perawat_hewan,
                k.no_dokter_hewan,
                k.kode_perawatan,
                p.nama_perawatan,
                -- Ambil email dari tabel pegawai yang sesuai dengan perawat_hewan
                (SELECT email_user FROM pegawai WHERE no_pegawai = k.no_perawat_hewan LIMIT 1) AS perawat_email,
                -- Ambil email dari tabel pegawai yang sesuai dengan dokter_hewan
                (SELECT email_user FROM pegawai WHERE no_pegawai = k.no_dokter_hewan LIMIT 1) AS dokter_email,
                -- Ambil email dari tabel pegawai yang sesuai dengan front_desk
                (SELECT email_user FROM pegawai WHERE no_pegawai = k.no_front_desk LIMIT 1) AS fdo_email
            FROM KUNJUNGAN_KEPERAWATAN k LEFT JOIN PERAWATAN p ON k.kode_perawatan = p.kode_perawatan where no_identitas_klien = (select no_identitas from klien where email = %s)        
            ORDER BY k.id_kunjungan
        """,[request.session['user_email']]) 

        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()

    treatments = []
    for row in rows:
        treatment = dict(zip(columns, row))

        # Fungsi untuk menghapus titik dan @example.com dari email
        def clean_email(email):
            if email:
                return email.split('@')[0].replace('.', ' ')  # Hapus titik dan ambil sebelum '@'
            return email

        # Format email untuk dokter agar diawali dengan "dr."
        if treatment['dokter_email']:
            treatment['dokter_email'] = "dr." + clean_email(treatment['dokter_email']).capitalize()

        # Format email untuk perawat dan fdo agar diawali dengan huruf kapital
        if treatment['perawat_email']:
            treatment['perawat_email'] = clean_email(treatment['perawat_email']).capitalize()
        
        if treatment['fdo_email']:
            treatment['fdo_email'] = clean_email(treatment['fdo_email']).capitalize()

        treatments.append(treatment)

    return render(request, 'daftar_perawatan_klien.html', {
        'treatments': treatments
    })

# your_app/views.py


import psycopg2.errors as pg_err
from django.shortcuts import render, redirect
from django.db import connection, IntegrityError

import psycopg2.errors as pg_err
from django.shortcuts import render, redirect
from django.db import connection, IntegrityError

def create_treatment(request):
    # --- autentikasi dokter ---
    if 'user_email' not in request.session:
        return redirect('login')
    user_email = request.session['user_email']

    with connection.cursor() as cursor:
        cursor.execute("SET search_path TO pet_clinic;")
        cursor.execute(
            """
            SELECT no_pegawai
            FROM pegawai
            WHERE email_user = %s
            """, [user_email])
        row = cursor.fetchone()
        if not row:
            return redirect('login')
        no_peg = row[0]

        cursor.execute(
            """
            SELECT 1 FROM dokter_hewan WHERE no_dokter_hewan = %s
            """, [no_peg])
        if not cursor.fetchone():
            return redirect('login')

    errors = {}
    data = {}
    selected = {}

    # --- ambil data untuk satu dropdown kunjungan ---
    with connection.cursor() as cursor:
        cursor.execute("SET search_path TO pet_clinic;")
        cursor.execute("""
            SELECT
              k.id_kunjungan::text,
              d.email_user   AS dokter_email,
              n.email_user   AS perawat_email,
              f.email_user   AS front_email,
              k.nama_hewan,
              k.no_identitas_klien
            FROM kunjungan k
            JOIN pegawai d ON d.no_pegawai = k.no_dokter_hewan
            JOIN pegawai n ON n.no_pegawai = k.no_perawat_hewan
            JOIN pegawai f ON f.no_pegawai = k.no_front_desk
            ORDER BY k.timestamp_awal DESC
        """)
        kunjungan_list = [
            {
                'id':     row[0],
                'dokter': row[1],
                'perawat':row[2],
                'front':  row[3],
                'nama':   row[4],
                'klien':  row[5],
            }
            for row in cursor.fetchall()
        ]

        cursor.execute("""
            SELECT kode_perawatan, nama_perawatan
            FROM perawatan
            ORDER BY kode_perawatan
        """)
        jenis_list = cursor.fetchall()

    if request.method == "POST":
        data = request.POST.dict()
        raw = data.get('kunjungan', '').strip()
        if raw:
            try:
                id_kunjungan, dokter_email, perawat_email, front_email, nama_hewan, klien_id = raw.split('|')
                selected = {
                    'id': id_kunjungan,
                    'dokter': dokter_email,
                    'perawat': perawat_email,
                    'front': front_email,
                    'nama': nama_hewan,
                    'klien': klien_id,
                }
            except ValueError:
                errors['kunjungan'] = 'Pilihan kunjungan tidak valid'
        else:
            errors['kunjungan'] = 'Kunjungan wajib dipilih'

        # validasi jenis perawatan
        raw_jenis = data.get('jenis_perawatan', '').split(' – ')[0].strip()
        if not raw_jenis:
            errors['jenis_perawatan'] = 'Jenis perawatan wajib dipilih'
        else:
            # cek duplikasi di database
            with connection.cursor() as cursor:
                cursor.execute("SET search_path TO pet_clinic;")
                cursor.execute(
                    "SELECT 1 FROM kunjungan_keperawatan WHERE id_kunjungan = %s AND kode_perawatan = %s",
                    [selected.get('id'), raw_jenis]
                )
                if cursor.fetchone():
                    errors['jenis_perawatan'] = 'Jenis perawatan ini sudah pernah ditambahkan untuk kunjungan tersebut'


        if errors:
            return render(request, 'create_treatment.html', {
                'errors': errors,
                'kunjungan_list': kunjungan_list,
                'jenis_list': jenis_list,
                'data': data,
                'selected': selected,
            })

        # konversi email → no_pegawai
        with connection.cursor() as cursor:
            cursor.execute("SET search_path TO pet_clinic;")
            def id_by_email(e):
                cursor.execute("SELECT no_pegawai FROM pegawai WHERE email_user = %s", [e])
                r = cursor.fetchone()
                return r[0] if r else None

            no_dokter = id_by_email(selected['dokter'])
            no_perawat = id_by_email(selected['perawat'])
            no_front = id_by_email(selected['front'])

            try:
                
                cursor.execute(
                    """
                    INSERT INTO kunjungan_keperawatan
                        (id_kunjungan, nama_hewan, no_dokter_hewan,
                        no_perawat_hewan, no_front_desk, no_identitas_klien,
                        kode_perawatan)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, [
                        selected['id'], selected['nama'], no_dokter,
                        no_perawat, no_front, selected['klien'],
                        raw_jenis
                    ])
                return redirect('daftar_perawatan')
            except IntegrityError as exc:
                root = exc.__cause__
                msg = str(root).split('CONTEXT:')[0].strip()
                code = getattr(root, 'pgcode', '')
                if code == '23514' or isinstance(root, (pg_err.CheckViolation, pg_err.RaiseException)):
                    errors['db'] = msg
                else:
                    errors['db'] = 'Terjadi kesalahan database, coba lagi.'
                return render(request, 'create_treatment.html', {
                    'errors': errors,
                    'kunjungan_list': kunjungan_list,
                    'jenis_list': jenis_list,
                    'data': data,
                    'selected': selected,
                })

    # GET
    return render(request, 'create_treatment.html', {
        'kunjungan_list': kunjungan_list,
        'jenis_list': jenis_list,
        'errors': errors,
        'data': data,
        'selected': selected,
    })




def edit_treatment(request, id_kunjungan, kode_perawatan,no_dokter_hewan,no_perawat_hewan,no_front_desk,nama_hewan,no_identitas_klien):
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

        # Cek apakah no_pegawai ini ada di tabel dokter_hewan
        cursor.execute("SELECT 1 FROM dokter_hewan WHERE no_dokter_hewan = %s", [no_pegawai])
        is_dokter = cursor.fetchone()
        if not is_dokter:
            # Jika no_pegawai tidak ada di dokter_hewan, redirect login
            return redirect('login')
    errors = {}    
    with connection.cursor() as cursor:
        cursor.execute("SET search_path TO pet_clinic;")
        # 1) ambil data existing
        cursor.execute("""
            SELECT id_kunjungan, kode_perawatan
            FROM kunjungan_keperawatan
            WHERE id_kunjungan = %s
            AND no_identitas_klien = %s
            AND nama_hewan = %s
            AND no_dokter_hewan = %s
            AND no_perawat_hewan = %s
            AND no_front_desk = %s
            AND kode_perawatan = %s
    """, [id_kunjungan, no_identitas_klien, nama_hewan, no_dokter_hewan, no_perawat_hewan, no_front_desk,kode_perawatan])
        row = cursor.fetchone()
        if not row:
            raise Http404("Treatment not found")

        _, current_kode = row

        # 2) ambil list jenis perawatan untuk dropdown
        cursor.execute("""
            SELECT kode_perawatan, nama_perawatan
            FROM perawatan
            ORDER BY kode_perawatan
        """)
        jenis_list = cursor.fetchall()

    if request.method == "POST":
        new_kode = request.POST.get('jenis_perawatan','').strip()

        with connection.cursor() as cursor:
            if new_kode !=current_kode:
                cursor.execute("SET search_path TO pet_clinic;")
                cursor.execute(
                    "SELECT 1 FROM kunjungan_keperawatan WHERE id_kunjungan = %s AND kode_perawatan = %s",
                    [id_kunjungan, current_kode]
                )
                if cursor.fetchone():
                    errors['jenis_perawatan'] = 'Jenis perawatan ini sudah pernah ditambahkan untuk kunjungan tersebut'
                    
                if errors:
                    return render(request, 'edit_treatment.html', {
                        'id_kunjungan': id_kunjungan,
                        'current_kode': current_kode,
                        'jenis_list': jenis_list,
                        'errors':errors,
                    })
                    
                cursor.execute("SET search_path TO pet_clinic;")
                cursor.execute("""
                    UPDATE kunjungan_keperawatan
                    SET kode_perawatan = %s
                    WHERE id_kunjungan = %s
                    AND no_identitas_klien = %s
                    AND nama_hewan = %s
                    AND no_dokter_hewan = %s
                    AND no_perawat_hewan = %s
                    AND no_front_desk = %s
                    AND kode_perawatan = %s
                """, [new_kode,id_kunjungan, no_identitas_klien, nama_hewan, no_dokter_hewan, no_perawat_hewan, no_front_desk,kode_perawatan ])

        return redirect('daftar_perawatan')

    return render(request, 'edit_treatment.html', {
        'id_kunjungan': id_kunjungan,
        'current_kode': current_kode,
        'jenis_list': jenis_list,
    })


def delete_treatment(request, id_kunjungan, kode_perawatan,no_dokter_hewan,no_perawat_hewan,no_front_desk,nama_hewan,no_identitas_klien):
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

        # Cek apakah no_pegawai ini ada di tabel dokter_hewan
        cursor.execute("SELECT 1 FROM dokter_hewan WHERE no_dokter_hewan = %s", [no_pegawai])
        is_dokter = cursor.fetchone()
        if not is_dokter:
            # Jika no_pegawai tidak ada di dokter_hewan, redirect login
            return redirect('login')
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute("SET search_path TO pet_clinic;")                   
            cursor.execute("""
                DELETE FROM kunjungan_keperawatan
                    WHERE id_kunjungan = %s
                    AND no_identitas_klien = %s
                    AND nama_hewan = %s
                    AND no_dokter_hewan = %s
                    AND no_perawat_hewan = %s
                    AND no_front_desk = %s
                    AND kode_perawatan = %s
            """, [id_kunjungan, no_identitas_klien, nama_hewan, no_dokter_hewan, no_perawat_hewan, no_front_desk,kode_perawatan])
        return redirect('daftar_perawatan')
    return JsonResponse({'error': 'Invalid method'}, status=400)
