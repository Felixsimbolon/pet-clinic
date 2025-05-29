from django.shortcuts import render, redirect
from django.db import connection
import re

def list_treatment_types(request):
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
        cursor.execute("""
            SELECT kode_perawatan, nama_perawatan, biaya_perawatan
            FROM perawatan
            ORDER BY kode_perawatan;
        """)
        rows = cursor.fetchall()

    treatments = [
        {
            'kode': kode,
            'nama': nama,
            'biaya_str': f"Rp{biaya:,.0f}".replace(',', '.'),
        }
        for kode, nama, biaya in rows
    ]

    return render(request, 'list_treatment_types.html', {
        'treatments': treatments
    })


def create_treatment_type(request):
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
        
    error = None
    if request.method == 'POST':
        nama  = request.POST['nama']
        biaya = request.POST['biaya']

        if not nama or not biaya.isdigit():
            error = "Nama harus diisi dan Biaya harus angka bulat"
        else:
            biaya = int(biaya)
            with connection.cursor() as cursor:
                cursor.execute("SET search_path TO pet_clinic;")
                
                cursor.execute("""
                    SELECT kode_perawatan
                    FROM perawatan
                    ORDER BY kode_perawatan DESC
                    LIMIT 1
                """)
                last = cursor.fetchone()
                if last:
                    m = re.search(r'TRM(\d+)', last[0])
                    num = int(m.group(1)) + 1 if m else 1
                else:
                    num = 1
                kode_baru = f"TRM{num:03d}"

                cursor.execute("""
                    INSERT INTO perawatan (kode_perawatan, nama_perawatan, biaya_perawatan)
                    VALUES (%s, %s, %s)
                """, [kode_baru, nama, biaya])

            return redirect('treatment_list')

    return render(request, 'create_treatment_type.html', {
        'error': error
    })


def update_treatment_type(request, kode):
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
        
    error = None
    if request.method == 'POST':
        nama  = request.POST['nama']
        biaya = request.POST['biaya']

        if not nama or not biaya.isdigit():
            error = "Nama harus diisi dan Biaya harus angka bulat"
        else:
            biaya = int(biaya)
            with connection.cursor() as cursor:
                cursor.execute("SET search_path TO pet_clinic;")

                cursor.execute("""
                    UPDATE perawatan
                    SET nama_perawatan = %s, biaya_perawatan = %s
                    WHERE kode_perawatan = %s
                """, [nama, biaya, kode])
            return redirect('treatment_list')

    else:
        with connection.cursor() as cursor:
            cursor.execute("SET search_path TO pet_clinic;")

            cursor.execute("""
                SELECT nama_perawatan, biaya_perawatan
                FROM perawatan
                WHERE kode_perawatan = %s
            """, [kode])
            row = cursor.fetchone()
        if row:
            nama, biaya = row
        else:
            nama, biaya = '', 0

    return render(request, 'update_treatment_type.html', {
        'kode': kode,
        'nama': nama,
        'biaya': biaya,
        'error': error
    })


def delete_treatment_type(request, kode):
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
                DELETE FROM perawatan
                WHERE kode_perawatan = %s
            """, [kode])
        return redirect('treatment_list')

    with connection.cursor() as cursor:
        cursor.execute("SET search_path TO pet_clinic;")

        cursor.execute("""
            SELECT nama_perawatan
            FROM perawatan
            WHERE kode_perawatan = %s
        """, [kode])
        row = cursor.fetchone()
    nama = row[0] if row else ''

    return render(request, 'confirm_delete_treatment_type.html', {
        'kode': kode,
        'nama': nama
    })

def list_treatment_types_perawat(request):
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
            SELECT kode_perawatan, nama_perawatan, biaya_perawatan
            FROM perawatan
            ORDER BY kode_perawatan;
        """)
        rows = cursor.fetchall()

    treatments = [
        {
            'kode': kode,
            'nama': nama,
            'biaya_str': f"Rp{biaya:,.0f}".replace(',', '.'),
        }
        for kode, nama, biaya in rows
    ]

    return render(request, 'list_treatment_types_perawat.html', {
        'treatments': treatments
    })


def create_treatment_type_perawat(request):
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
        
    error = None
    if request.method == 'POST':
        nama  = request.POST['nama']
        biaya = request.POST['biaya']

        if not nama or not biaya.isdigit():
            error = "Nama harus diisi dan Biaya harus angka bulat"
        else:
            biaya = int(biaya)
            with connection.cursor() as cursor:
                cursor.execute("SET search_path TO pet_clinic;")
                
                cursor.execute("""
                    SELECT kode_perawatan
                    FROM perawatan
                    ORDER BY kode_perawatan DESC
                    LIMIT 1
                """)
                last = cursor.fetchone()
                if last:
                    m = re.search(r'TRM(\d+)', last[0])
                    num = int(m.group(1)) + 1 if m else 1
                else:
                    num = 1
                kode_baru = f"TRM{num:03d}"

                cursor.execute("""
                    INSERT INTO perawatan (kode_perawatan, nama_perawatan, biaya_perawatan)
                    VALUES (%s, %s, %s)
                """, [kode_baru, nama, biaya])

            return redirect('treatment_list_perawat')

    return render(request, 'create_treatment_type_perawat.html', {
        'error': error
    })


def update_treatment_type_perawat(request, kode):
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
        
    error = None
    if request.method == 'POST':
        nama  = request.POST['nama']
        biaya = request.POST['biaya']

        if not nama or not biaya.isdigit():
            error = "Nama harus diisi dan Biaya harus angka bulat"
        else:
            biaya = int(biaya)
            with connection.cursor() as cursor:
                cursor.execute("SET search_path TO pet_clinic;")

                cursor.execute("""
                    UPDATE perawatan
                    SET nama_perawatan = %s, biaya_perawatan = %s
                    WHERE kode_perawatan = %s
                """, [nama, biaya, kode])
            return redirect('treatment_list_perawat')

    else:
        with connection.cursor() as cursor:
            cursor.execute("SET search_path TO pet_clinic;")

            cursor.execute("""
                SELECT nama_perawatan, biaya_perawatan
                FROM perawatan
                WHERE kode_perawatan = %s
            """, [kode])
            row = cursor.fetchone()
        if row:
            nama, biaya = row
        else:
            nama, biaya = '', 0

    return render(request, 'update_treatment_type_perawat.html', {
        'kode': kode,
        'nama': nama,
        'biaya': biaya,
        'error': error
    })


def delete_treatment_type_perawat(request, kode):
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
        
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute("SET search_path TO pet_clinic;")

            cursor.execute("""
                DELETE FROM perawatan
                WHERE kode_perawatan = %s
            """, [kode])
        return redirect('treatment_list_perawat')

    with connection.cursor() as cursor:
        cursor.execute("SET search_path TO pet_clinic;")

        cursor.execute("""
            SELECT nama_perawatan
            FROM perawatan
            WHERE kode_perawatan = %s
        """, [kode])
        row = cursor.fetchone()
    nama = row[0] if row else ''

    return render(request, 'confirm_delete_treatment_type_perawat.html', {
        'kode': kode,
        'nama': nama
    })