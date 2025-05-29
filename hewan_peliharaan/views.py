from django.shortcuts import render, redirect
from django.db import connection
from django.contrib import messages
from django.http import HttpResponseForbidden

def get_user_role(email_user):
    with connection.cursor() as cursor:
        # Cek apakah email ini adalah klien (individu atau perusahaan)
        cursor.execute("""
            SELECT 1
            FROM pet_clinic.klien
            WHERE email = %s
        """, [email_user])
        if cursor.fetchone():
            return 'klien'

        # Cek apakah email ini adalah front desk
        cursor.execute("""
            SELECT 1
            FROM pet_clinic.front_desk fd
            JOIN pet_clinic.pegawai p ON fd.no_front_desk = p.no_pegawai
            WHERE p.email_user = %s
        """, [email_user])
        if cursor.fetchone():
            return 'frontdesk'

    return None  # Kalau bukan keduanya

# List hewan
def list_hewan(request):
    if 'user_email' not in request.session:
        return redirect('login')

    if 'user_email' not in request.session:
        return redirect('login')

    email_user = request.session['user_email']
    role = get_user_role(email_user)

    if role not in ['frontdesk', 'klien']:
        return HttpResponseForbidden("Hanya front desk atau klien yang boleh mengakses halaman ini.")
    
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                h.nama,
                h.no_identitas_klien,
                COALESCE(i.nama_depan || ' ' || COALESCE(i.nama_tengah, '') || ' ' || i.nama_belakang, p.nama_perusahaan) AS nama_pemilik,
                jh.nama_jenis,
                TO_CHAR(h.tanggal_lahir, 'DD FMMonth YYYY') AS tanggal_lahir,
                h.url_foto
            FROM pet_clinic.hewan h
            JOIN pet_clinic.jenis_hewan jh ON h.id_jenis = jh.id
            LEFT JOIN pet_clinic.individu i ON h.no_identitas_klien = i.no_identitas_klien
            LEFT JOIN pet_clinic.perusahaan p ON h.no_identitas_klien = p.no_identitas_klien
            ORDER BY h.nama;
        """)
        hasil = cursor.fetchall()

    hewan_list = [
    {
        'no': i + 1,
        'nama': row[0],                     # h.nama
        'no_identitas_klien': row[1],       # h.no_identitas_klien
        'pemilik': row[2],                  # nama lengkap pemilik
        'jenis': row[3],                    # nama_jenis
        'tanggal_lahir': row[4],
        'foto_url': row[5]
    }
    for i, row in enumerate(hasil)
    ]

    return render(request, 'list_hewan.html', {'hewan_list': hewan_list, 'role': role})

# Update hewan
def update_hewan(request, nama, no_identitas_klien):
    if 'user_email' not in request.session:
        return redirect('login')

    email_user = request.session['user_email']
    role = get_user_role(email_user)

    if role not in ['frontdesk', 'klien']:
        return HttpResponseForbidden("Hanya front desk atau klien yang boleh mengakses halaman ini.")

    with connection.cursor() as cursor:
        # Ambil data hewan
        cursor.execute("""
            SELECT h.nama, h.no_identitas_klien,
                COALESCE(
                    i.nama_depan || ' ' || COALESCE(i.nama_tengah, '') || ' ' || i.nama_belakang,
                    p.nama_perusahaan
                ) AS nama_pemilik,
                jh.id, jh.nama_jenis, h.tanggal_lahir, h.url_foto
            FROM pet_clinic.hewan h
            JOIN pet_clinic.jenis_hewan jh ON h.id_jenis = jh.id
            LEFT JOIN pet_clinic.individu i ON h.no_identitas_klien = i.no_identitas_klien
            LEFT JOIN pet_clinic.perusahaan p ON h.no_identitas_klien = p.no_identitas_klien
            WHERE h.nama = %s AND h.no_identitas_klien = %s;
        """, [nama, no_identitas_klien])
        data = cursor.fetchone()

        if not data:
            return redirect('list_hewan')

        cursor.execute("SELECT id, nama_jenis FROM pet_clinic.jenis_hewan")
        jenis_list = cursor.fetchall()

    if request.method == 'POST':
        nama_baru = request.POST.get('nama_hewan')
        tanggal_lahir = request.POST.get('tanggal_lahir')
        foto_url = request.POST.get('foto_url')
        id_jenis = request.POST.get('jenis_hewan')

        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE pet_clinic.hewan
                SET nama = %s, tanggal_lahir = %s, url_foto = %s, id_jenis = %s
                WHERE nama = %s AND no_identitas_klien = %s
            """, [nama_baru, tanggal_lahir, foto_url, id_jenis, nama, no_identitas_klien])

        return redirect('list_hewan')

    context = {
        'nama': data[0],
        'no_identitas_klien': data[1],
        'nama_klien': data[2],
        'id_jenis': data[3],
        'nama_jenis': data[4],
        'tanggal_lahir': data[5].strftime('%Y-%m-%d'),
        'foto_url': data[6],
        'jenis_list': jenis_list,
        'role': role,
    }

    return render(request, 'update_hewan.html', context)

# Delete hewan
def delete_hewan(request, nama, no_identitas_klien):
    # Autentikasi pengguna
    if 'user_email' not in request.session:
        return redirect('login')

    email_user = request.session['user_email']
    role = get_user_role(email_user)

    if role != 'frontdesk':
        return HttpResponseForbidden("Hanya front desk yang boleh mengakses halaman ini.")

    with connection.cursor() as cursor:
        # Ambil data hewan dan nama pemilik untuk konfirmasi
        cursor.execute("""
            SELECT h.nama,
                COALESCE(
                    i.nama_depan || ' ' || COALESCE(i.nama_tengah, '') || ' ' || i.nama_belakang,
                    p.nama_perusahaan
                ) AS nama_pemilik
            FROM pet_clinic.hewan h
            LEFT JOIN pet_clinic.individu i ON h.no_identitas_klien = i.no_identitas_klien
            LEFT JOIN pet_clinic.perusahaan p ON h.no_identitas_klien = p.no_identitas_klien
            WHERE h.nama = %s AND h.no_identitas_klien = %s
        """, [nama, no_identitas_klien])
        result = cursor.fetchone()

        if not result:
            return redirect('list_hewan')

        nama_hewan, nama_pemilik = result

        with connection.cursor() as cursor:
            if request.method == 'POST':
                try:
                    cursor.execute("SET search_path TO pet_clinic;")
                    cursor.execute("""
                        DELETE FROM hewan
                        WHERE nama = %s AND no_identitas_klien = %s
                    """, [nama, no_identitas_klien])
                    return redirect('list_hewan')
                except Exception as e:
                    messages.error(request, str(e))

    context = {
        'nama_hewan': nama_hewan,
        'nama_pemilik': nama_pemilik,
        'role': role
    }

    return render(request, 'delete_hewan.html', context)

def create_hewan(request):
    # Cek login
    if 'user_email' not in request.session:
        return redirect('login')

    # Cek role
    email_user = request.session['user_email']
    role = get_user_role(email_user)
    
    if role not in ['frontdesk', 'klien']:
        return HttpResponseForbidden("Hanya front desk atau klien yang boleh mengakses halaman ini.")
    
    # Ambil daftar klien dan jenis hewan untuk dropdown
    with connection.cursor() as cursor:
        cursor.execute("""SELECT k.no_identitas,
                COALESCE(
                    i.nama_depan || ' ' || COALESCE(i.nama_tengah, '') || ' ' || i.nama_belakang,
                    p.nama_perusahaan
                ) AS nama_klien
            FROM pet_clinic.klien k
            LEFT JOIN pet_clinic.individu i ON k.no_identitas = i.no_identitas_klien
            LEFT JOIN pet_clinic.perusahaan p ON k.no_identitas = p.no_identitas_klien
            ORDER BY nama_klien""")
        klien_list = cursor.fetchall()

        cursor.execute("SELECT id, nama_jenis FROM pet_clinic.jenis_hewan ORDER BY nama_jenis")
        jenis_list = cursor.fetchall()

    if request.method == 'POST':
        pemilik_id = request.POST.get('pemilik')
        jenis_id = request.POST.get('jenis_hewan')
        nama_hewan = request.POST.get('nama_hewan')
        tanggal_lahir = request.POST.get('tanggal_lahir')
        foto_url = request.POST.get('foto_url')

        # Validasi sederhana
        if not all([pemilik_id, jenis_id, nama_hewan, tanggal_lahir, foto_url]):
            return render(request, 'create_hewan.html', {
                'klien_list': klien_list,
                'jenis_list': jenis_list,
                'error': 'Semua field wajib diisi.'
            })

        # Insert ke database (pastikan kolomnya sesuai: url_foto bukan foto)
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO pet_clinic.hewan (
                    no_identitas_klien, id_jenis, nama, tanggal_lahir, url_foto
                ) VALUES (%s, %s, %s, %s, %s)
            """, [pemilik_id, jenis_id, nama_hewan, tanggal_lahir, foto_url])

        return redirect('list_hewan')

    # Render form kosong
    context = {
        'klien_list': klien_list,
        'jenis_list': jenis_list,
        'role': role,
    }
    return render(request, 'create_hewan.html', context)