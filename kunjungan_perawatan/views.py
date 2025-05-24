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
                k.catatan,
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
                k.catatan,
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
                k.catatan,
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
                k.catatan,
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

    return render(request, 'daftar_perawatan_klien.html', {
        'treatments': treatments
    })

# your_app/views.py


def create_treatment(request):
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
        cursor.execute("SELECT DISTINCT id_kunjungan FROM kunjungan ORDER BY id_kunjungan;")
        kunjungan_list = [row[0] for row in cursor.fetchall()]
        cursor.execute("SELECT DISTINCT NAMA_HEWAN FROM KUNJUNGAN;")
        hewan_list = [row[0] for row in cursor.fetchall()]
        cursor.execute("SELECT DISTINCT email_user FROM KUNJUNGAN JOIN PEGAWAI ON no_pegawai = no_dokter_hewan;")
        dokter_list = [row[0] for row in cursor.fetchall()]
        cursor.execute("SELECT DISTINCT no_identitas_klien FROM KUNJUNGAN;")
        klien_list = [row[0] for row in cursor.fetchall()]
        cursor.execute("SELECT DISTINCT email_user FROM KUNJUNGAN JOIN PEGAWAI ON no_pegawai = no_front_desk;")
        front_desk_list = [row[0] for row in cursor.fetchall()]
        cursor.execute("SELECT DISTINCT email_user FROM KUNJUNGAN JOIN PEGAWAI ON no_pegawai = no_perawat_hewan;")
        perawat_list = [row[0] for row in cursor.fetchall()]
        cursor.execute("SELECT kode_perawatan, nama_perawatan FROM perawatan ORDER BY kode_perawatan;")
        jenis_list = cursor.fetchall()

    if request.method == "POST":
        kunjungan = request.POST.get('kunjungan', '').strip()
        hewan = request.POST.get('hewan', '').strip()
        klien = request.POST.get('klien', '').strip()
        front_desk = request.POST.get('front_desk', '').strip()
        dokter = request.POST.get('dokter', '').strip()
        perawat = request.POST.get('perawat', '').strip()
        jenis = request.POST.get('jenis_perawatan', '').split(" - ")[0].strip()
        catatan = request.POST.get('catatan', '').strip()
        
        required_drop = {
            'kunjungan':kunjungan,
            'klien':klien,
            'hewan':hewan,
            'dokter':dokter,
            'perawat':perawat,
            'front_desk':front_desk,
            'jenis_perawatan':jenis,
        }

        for field, value in required_drop.items():
            if not value:                              # ''  atau None
                errors[field] = f'{field.replace("_", " ").title()} wajib dipilih'
        if errors:
            return render(request, 'create_treatment.html', {
                'kunjungan_list': kunjungan_list,
                'hewan_list': hewan_list,
                'dokter_list': dokter_list,
                'klien_list': klien_list,
                'front_desk_list': front_desk_list,
                'perawat_list': perawat_list,
                'jenis_list': jenis_list,
                'errors': errors,
            })
        with connection.cursor() as cursor:
            cursor.execute("SET search_path TO pet_clinic;")

            # Cek apakah ada record dengan kombinasi yang sama
            # cursor.execute("""
            #     SELECT 1 FROM kunjungan
            #     WHERE id_kunjungan = %s
            #       AND no_identitas_klien = %s
            #       AND nama_hewan = %s
            #       AND no_dokter_hewan = (
            #           SELECT no_pegawai FROM pegawai WHERE email_user = %s
            #       )
            #       AND no_perawat_hewan = (
            #           SELECT no_pegawai FROM pegawai WHERE email_user = %s
            #       )
            #       AND no_front_desk = (
            #           SELECT no_pegawai FROM pegawai WHERE email_user = %s
            #       )
            # """, [kunjungan, klien, hewan, dokter, perawat, front_desk])

            # exists = cursor.fetchone()

            # if exists:
            cursor.execute("""
            SELECT no_perawat_hewan FROM kunjungan
            WHERE id_kunjungan = %s
                AND no_identitas_klien = %s
                AND nama_hewan = %s
                AND no_dokter_hewan = (
                    SELECT no_pegawai FROM pegawai WHERE email_user = %s
                )
                AND no_perawat_hewan = (
                    SELECT no_pegawai FROM pegawai WHERE email_user = %s
                )
                AND no_front_desk = (
                    SELECT no_pegawai FROM pegawai WHERE email_user = %s
                )
        """, [kunjungan, klien, hewan, dokter, perawat, front_desk])
            
            no_perawat = cursor.fetchone()
            cursor.execute("""
            SELECT no_dokter_hewan FROM kunjungan
            WHERE id_kunjungan = %s
                AND no_identitas_klien = %s
                AND nama_hewan = %s
                AND no_dokter_hewan = (
                    SELECT no_pegawai FROM pegawai WHERE email_user = %s
                )
                AND no_perawat_hewan = (
                    SELECT no_pegawai FROM pegawai WHERE email_user = %s
                )
                AND no_front_desk = (
                    SELECT no_pegawai FROM pegawai WHERE email_user = %s
                )
        """, [kunjungan, klien, hewan, dokter, perawat, front_desk])
            
            no_dokter = cursor.fetchone()
            cursor.execute("""
            SELECT no_front_desk FROM kunjungan
            WHERE id_kunjungan = %s
                AND no_identitas_klien = %s
                AND nama_hewan = %s
                AND no_dokter_hewan = (
                    SELECT no_pegawai FROM pegawai WHERE email_user = %s
                )
                AND no_perawat_hewan = (
                    SELECT no_pegawai FROM pegawai WHERE email_user = %s
                )
                AND no_front_desk = (
                    SELECT no_pegawai FROM pegawai WHERE email_user = %s
                )
        """, [kunjungan, klien, hewan, dokter, perawat, front_desk])
            no_front_desk = cursor.fetchone()
            # Jika sudah ada, langsung insert ke kunjungan_keperawatan
            try:
                if catatan.strip() == "":
                    cursor.execute("""
                        INSERT INTO kunjungan_keperawatan
                        (id_kunjungan,NAMA_HEWAN,no_dokter_hewan,no_perawat_hewan,no_front_desk,no_identitas_klien, kode_perawatan)
                        VALUES (%s, %s, %s,%s, %s, %s,%s)
                    """, [kunjungan,hewan,no_dokter,no_perawat,no_front_desk,klien, jenis])
                else:
                        cursor.execute("""
                        INSERT INTO kunjungan_keperawatan
                        (id_kunjungan,NAMA_HEWAN,no_dokter_hewan,no_perawat_hewan,no_front_desk,no_identitas_klien, kode_perawatan, catatan)
                        VALUES (%s, %s, %s,%s, %s, %s,%s, %s)
                    """, [kunjungan,hewan,no_dokter,no_perawat,no_front_desk,klien, jenis, catatan])
                        
                        
            except IntegrityError as exc:
                root = exc.__cause__
                msg    = str(root).split('CONTEXT:')[0].strip()
                pgcode = getattr(root, 'pgcode', '')  # contoh '23514'
                if pgcode == '23514' or isinstance(root,(pg_err.CheckViolation, pg_err.RaiseException)):

                        if msg.startswith('ERROR: Hewan'):  # trigger hewan-klien
                            errors['hewan'] = msg
                        else:                                 # pesan lain dari trigger yg sama
                            errors.setdefault('db', msg)
                        return render(request, 'create_treatment.html', {
                            'kunjungan_list': kunjungan_list,
                            'hewan_list': hewan_list,
                            'dokter_list': dokter_list,
                            'klien_list': klien_list,
                            'front_desk_list': front_desk_list,
                            'perawat_list': perawat_list,
                            'jenis_list': jenis_list,
                            'errors': errors,
                            'data': request.POST,
                        })

                else:
                    errors['db'] = 'Terjadi kesalahan database, coba lagi.'
                    return render(request, 'create_treatment.html', {
                        'kunjungan_list': kunjungan_list,
                        'hewan_list': hewan_list,
                        'dokter_list': dokter_list,
                        'klien_list': klien_list,
                        'front_desk_list': front_desk_list,
                        'perawat_list': perawat_list,
                        'jenis_list': jenis_list,
                        'errors': errors,
                        'data': request.POST,
                    })
            # else:
            #     # Jika tidak ada, bisa tambahkan pesan error atau logika lain
            #     # Contoh: tampilkan error (bisa dihandle di template)
            #     errors = {'kombinasi': 'Kombinasi kunjungan, klien, hewan, dokter, perawat, dan front desk tidak ditemukan.'}
            #     return render(request, 'create_treatment.html', {
            #         'kunjungan_list': kunjungan_list,
            #         'hewan_list': hewan_list,
            #         'dokter_list': dokter_list,
            #         'klien_list': klien_list,
            #         'front_desk_list': front_desk_list,
            #         'perawat_list': perawat_list,
            #         'jenis_list': jenis_list,
            #         'errors': errors,
            #         'data': request.POST,
            #     })

        return redirect('daftar_perawatan')

    return render(request, 'create_treatment.html', {
        'kunjungan_list': kunjungan_list,
        'hewan_list': hewan_list,
        'dokter_list': dokter_list,
        'klien_list': klien_list,
        'front_desk_list': front_desk_list,
        'perawat_list': perawat_list,
        'jenis_list': jenis_list,
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
        
    with connection.cursor() as cursor:
        cursor.execute("SET search_path TO pet_clinic;")
        # 1) ambil data existing
        cursor.execute("""
            SELECT id_kunjungan, kode_perawatan, catatan
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

        _, current_kode, current_catatan = row

        # 2) ambil list jenis perawatan untuk dropdown
        cursor.execute("""
            SELECT kode_perawatan, nama_perawatan
            FROM perawatan
            ORDER BY kode_perawatan
        """)
        jenis_list = cursor.fetchall()

    if request.method == "POST":
        new_kode = request.POST.get('jenis_perawatan','').strip()
        new_catatan = request.POST.get('catatan', '').strip()

        with connection.cursor() as cursor:
            cursor.execute("SET search_path TO pet_clinic;")
            cursor.execute("""
                UPDATE kunjungan_keperawatan
                SET kode_perawatan = %s, catatan = %s
                WHERE id_kunjungan = %s
                AND no_identitas_klien = %s
                AND nama_hewan = %s
                AND no_dokter_hewan = %s
                AND no_perawat_hewan = %s
                AND no_front_desk = %s
                AND kode_perawatan = %s
            """, [new_kode, new_catatan,id_kunjungan, no_identitas_klien, nama_hewan, no_dokter_hewan, no_perawat_hewan, no_front_desk,kode_perawatan ])

        return redirect('daftar_perawatan')

    return render(request, 'edit_treatment.html', {
        'id_kunjungan': id_kunjungan,
        'current_kode': current_kode,
        'current_catatan': current_catatan or '',
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
