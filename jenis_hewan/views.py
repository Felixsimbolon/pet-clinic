from django.shortcuts import render, redirect
from django.db import connection
from django.contrib import messages
from django.http import HttpResponseForbidden


def get_user_role(email_user):
    with connection.cursor() as cursor:
        # Cek apakah email ini adalah dokter
        cursor.execute("""
            SELECT 1
            FROM pet_clinic.dokter_hewan dh
            JOIN pet_clinic.tenaga_medis tm ON dh.no_dokter_hewan = tm.no_tenaga_medis
            JOIN pet_clinic.pegawai p ON tm.no_tenaga_medis = p.no_pegawai
            WHERE p.email_user = %s
        """, [email_user])
        if cursor.fetchone():
            return 'dokter'

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

# List semua Jenis Hewan
def list_jenis_hewan(request):
    # Cek apakah user login
    if 'user_email' not in request.session:
        return redirect('login')

    email_user = request.session['user_email']
    role = get_user_role(email_user)

    if role not in ['frontdesk', 'dokter']:
        return HttpResponseForbidden("Hanya front desk atau dokter yang boleh mengakses halaman ini.")

    # Cek role: dokter atau front desk
    with connection.cursor() as cursor:
        # Ambil data jenis hewan
        cursor.execute("SELECT id, nama_jenis FROM pet_clinic.jenis_hewan ORDER BY id")
        hasil = cursor.fetchall()

    jenis_list = [
        {
            'no': i+1,
            'id_jenis': row[0],
            'nama_jenis': row[1]
        } for i, row in enumerate(hasil)
    ]

    context = {
        'jenis_list': jenis_list,
        'role': role,
    }
    return render(request, 'list_jenis_hewan.html', context)

# Create Jenis Hewan
def create_jenis_hewan(request):
    if 'user_email' not in request.session:
        return redirect('login')

    email_user = request.session['user_email']
    role = get_user_role(email_user)

    if role != 'frontdesk':
        return HttpResponseForbidden("Hanya front desk yang boleh melakukan aksi ini.")

    if request.method == 'POST':
        nama_jenis = request.POST.get('nama_jenis')

        if not nama_jenis:
            return render(request, 'jenis_hewan/create_jenis_hewan.html', {
                'error': 'Nama jenis tidak boleh kosong.'
            })

        with connection.cursor() as cursor:
            try:
                cursor.execute("SET search_path TO pet_clinic;")
                cursor.execute("""
                    INSERT INTO jenis_hewan (nama_jenis)
                    VALUES (%s)
                """, [nama_jenis])
                return redirect('list_jenis_hewan')
            except Exception as e:
                messages.error(request, str(e))

    return render(request, 'create_jenis_hewan.html')

# Update Jenis Hewan
def update_jenis_hewan(request, id_jenis):
    if 'user_email' not in request.session:
        return redirect('login')

    email_user = request.session['user_email']
    role = get_user_role(email_user)
    
    if role != 'frontdesk':
        return HttpResponseForbidden("Hanya front desk yang boleh melakukan aksi ini.")
    
    with connection.cursor() as cursor:
        # Ambil data jenis hewan berdasarkan ID
        cursor.execute("SELECT id, nama_jenis FROM pet_clinic.jenis_hewan WHERE id = %s", [id_jenis])
        result = cursor.fetchone()
        if not result:
            return redirect('list_jenis_hewan')  # Kalau tidak ada, balik ke list

        if request.method == 'POST':
            nama_jenis_baru = request.POST.get('nama_jenis')
            cursor.execute(
                "UPDATE pet_clinic.jenis_hewan SET nama_jenis = %s WHERE id = %s",
                [nama_jenis_baru, id_jenis]
            )
            return redirect('list_jenis_hewan')

    jenis = {
        'id': result[0],
        'nama': result[1]
    }

    return render(request, 'update_jenis_hewan.html', {'jenis': jenis})

# Delete Jenis Hewan
def delete_jenis_hewan(request, id_jenis):
    if 'user_email' not in request.session:
        return redirect('login')

    email_user = request.session['user_email']
    role = get_user_role(email_user)
    
    if role != 'frontdesk':
        return HttpResponseForbidden("Hanya front desk yang boleh melakukan aksi ini.")
        
    with connection.cursor() as cursor:
        # Ambil data jenis untuk ditampilkan saat konfirmasi
        cursor.execute("SELECT id, nama_jenis FROM pet_clinic.jenis_hewan WHERE id = %s", [id_jenis])
        row = cursor.fetchone()
        if not row:
            return redirect('list_jenis_hewan')  # kalau tidak ditemukan, balik ke list

        jenis = {
            'id': row[0],
            'nama': row[1]
        }

        if request.method == 'POST':
            cursor.execute("DELETE FROM pet_clinic.jenis_hewan WHERE id = %s", [id_jenis])
            return redirect('list_jenis_hewan')

    return render(request, 'delete_jenis_hewan.html', {'jenis': jenis})