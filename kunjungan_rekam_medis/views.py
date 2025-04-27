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

def daftar_kunjungan(request):
    with connection.cursor() as cursor:
        cursor.execute("SET search_path TO pet_clinic;")
        cursor.execute("""
            SELECT
                id_kunjungan,
                no_identitas_klien,
                nama_hewan,
                tipe_kunjungan,
                TO_CHAR(timestamp_awal, 'DD-MM-YYYY HH24:MI:SS') as waktu_mulai,
                TO_CHAR(timestamp_akhir, 'DD-MM-YYYY HH24:MI:SS') as waktu_selesai
            FROM kunjungan
            ORDER BY timestamp_awal DESC
        """)
        kunjungan_rows = cursor.fetchall()

        # Check if 'suhu' and 'berat_badan' are null in rekam_medis for each kunjungan
        for i, row in enumerate(kunjungan_rows):
            id_kunjungan = row[0]
            cursor.execute("""
                SELECT suhu, berat_badan
                FROM kunjungan
                WHERE id_kunjungan = %s
            """, [id_kunjungan])
            rekam_medis_data = cursor.fetchone()

            # Check if both suhu and berat_badan are null
            suhu_null = rekam_medis_data[0] is None
            berat_badan_null = rekam_medis_data[1] is None

            # Add flag for modal display if both are null
            kunjungan_rows[i] = (*row, suhu_null, berat_badan_null)

    columns = ['id_kunjungan', 'no_identitas_klien', 'nama_hewan', 'tipe_kunjungan', 'waktu_mulai', 'waktu_selesai', 'suhu_null', 'berat_badan_null']
    data = [dict(zip(columns, row)) for row in kunjungan_rows]

    return render(request, 'daftar_kunjungan.html', {
        'kunjungan_list': data
    })

    


def create_kunjungan(request):
    # Retrieve all available ID Klien and Nama Hewan from the database
    with connection.cursor() as cursor:
        cursor.execute("SET search_path TO pet_clinic;")
        
        # 1) Get all ID Klien
        cursor.execute("SELECT no_identitas FROM klien ORDER BY no_identitas;")
        klien_list = [row[0] for row in cursor.fetchall()]
        
        # 2) Get all Nama Hewan for the selected ID Klien (based on your design assumption)
        cursor.execute("""
            SELECT id_jenis, nama FROM hewan ORDER BY nama;
        """)
        hewan_list = cursor.fetchall()

        # 3) Get available metode_kunjungan options
        cursor.execute("""
            SELECT DISTINCT tipe_kunjungan FROM kunjungan ORDER BY tipe_kunjungan;
        """)
        tipe_kunjungan_list = cursor.fetchall()

    if request.method == "POST":
        # Get the data from form
        id_klien = request.POST['id_klien']
        nama_hewan = request.POST['nama_hewan']
        metode_kunjungan = request.POST['metode_kunjungan']
        waktu_mulai_penanganan = request.POST['waktu_mulai_penanganan']
        waktu_selesai_penanganan = request.POST['waktu_selesai_penanganan']

        # Insert data into kunjungan table
        with connection.cursor() as cursor:
            cursor.execute("SET search_path TO pet_clinic;")
            cursor.execute("""
                INSERT INTO kunjungan
                    (no_identitas_klien, nama_hewan, tipe_kunjungan, timestamp_awal, timestamp_akhir)
                VALUES (%s, %s, %s, %s, %s)
            """, [id_klien, nama_hewan, metode_kunjungan, waktu_mulai_penanganan, waktu_selesai_penanganan])

        # Redirect after saving the kunjungan data
        return redirect('daftar_kunjungan')

    return render(request, 'create_kunjungan.html', {
        'klien_list': klien_list,
        'hewan_list': hewan_list,
        'tipe_kunjungan_list': tipe_kunjungan_list,
    })


def update_kunjungan(request, id_kunjungan):
    # Fetch the current Kunjungan data based on the ID
    with connection.cursor() as cursor:
        cursor.execute("SET search_path TO pet_clinic;")
        
        # Get the details for the given kunjungan
        cursor.execute("""
            SELECT no_identitas_klien, nama_hewan, tipe_kunjungan, timestamp_awal, timestamp_akhir
            FROM kunjungan
            WHERE id_kunjungan = %s
        """, [id_kunjungan])
        kunjungan_data = cursor.fetchone()

        # Get list of available klien, hewan, and metode kunjungan
        cursor.execute("SELECT no_identitas FROM klien ORDER BY no_identitas;")
        klien_list = [row[0] for row in cursor.fetchall()]

        cursor.execute("""
            SELECT id_jenis, nama FROM hewan ORDER BY nama;
        """)
        hewan_list = cursor.fetchall()

        cursor.execute("""
            SELECT DISTINCT tipe_kunjungan FROM kunjungan ORDER BY tipe_kunjungan;
        """)
        tipe_kunjungan_list = cursor.fetchall()

    if request.method == "POST":
        # Handle form submission to update kunjungan
        id_klien = request.POST['id_klien']
        nama_hewan = request.POST['nama_hewan']
        tipe_kunjungan = request.POST['tipe_kunjungan']
        waktu_mulai_penanganan = request.POST['waktu_mulai_penanganan']
        waktu_selesai_penanganan = request.POST['waktu_selesai_penanganan']

        # Update the kunjungan record
        with connection.cursor() as cursor:
            cursor.execute("SET search_path TO pet_clinic;")
            cursor.execute("""
                UPDATE kunjungan
                SET id_klien = %s, nama_hewan = %s, tipe_kunjungan = %s,
                    waktu_mulai_penanganan = %s, waktu_selesai_penanganan = %s
                WHERE id_kunjungan = %s
            """, [id_klien, nama_hewan, tipe_kunjungan, waktu_mulai_penanganan, waktu_selesai_penanganan, id_kunjungan])

        # Redirect after updating the kunjungan
        return redirect('daftar_kunjungan')

    # Fetch the existing values to populate the form
    current_klien = kunjungan_data[0]
    current_nama_hewan = kunjungan_data[1]
    current_tipe_kunjungan = kunjungan_data[2]
    current_waktu_mulai = kunjungan_data[3]
    current_waktu_selesai = kunjungan_data[4]

    return render(request, 'update_kunjungan.html', {
        'id_kunjungan': id_kunjungan,
        'klien_list': klien_list,
        'hewan_list': hewan_list,
        'tipe_kunjungan_list': tipe_kunjungan_list,
        'current_klien': current_klien,
        'current_nama_hewan': current_nama_hewan,
        'current_tipe_kunjungan': current_tipe_kunjungan,
        'current_waktu_mulai': current_waktu_mulai,
        'current_waktu_selesai': current_waktu_selesai,
    })


def delete_kunjungan(request, id_kunjungan):
    # Check if the Kunjungan exists
    with connection.cursor() as cursor:
        cursor.execute("SET search_path TO pet_clinic;")
        cursor.execute("SELECT id_kunjungan FROM kunjungan WHERE id_kunjungan = %s", [id_kunjungan])
        kunjungan_exists = cursor.fetchone()

    if not kunjungan_exists:
        raise Http404("Kunjungan not found.")

    # Proceed to delete the Kunjungan if it exists
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute("SET search_path TO pet_clinic;")
            cursor.execute("DELETE FROM kunjungan WHERE id_kunjungan = %s", [id_kunjungan])
        
        # Redirect to the list of kunjungan after deletion
        return redirect('daftar_kunjungan')

    # If the method is GET, return a confirmation page or the same template
    return redirect('daftar_kunjungan')




def create_rekam_medis(request, id_kunjungan):
    # Get the relevant kunjungan data based on id_kunjungan
    with connection.cursor() as cursor:
        cursor.execute("SET search_path TO pet_clinic;")
        cursor.execute("""
            SELECT id_kunjungan, no_identitas_klien, nama_hewan
            FROM kunjungan
            WHERE id_kunjungan = %s
        """, [id_kunjungan])
        kunjungan_data = cursor.fetchone()

    if request.method == "POST":
        suhu = request.POST.get('suhu')
        berat_badan = request.POST.get('berat_badan')
        kode_perawatan = request.POST.get('jenis_perawatan')
        catatan = request.POST.get('catatan', '')

        # Insert the data into rekam_medis
        with connection.cursor() as cursor:
            cursor.execute("SET search_path TO pet_clinic;")
            cursor.execute("""
                UPDATE kunjungan
                SET suhu = %s, berat_badan = %s
                WHERE id_kunjungan = %s
            """, [suhu, berat_badan, id_kunjungan])
        with connection.cursor() as cursor:
            cursor.execute("SET search_path TO pet_clinic;")
            cursor.execute("""
                UPDATE kunjungan_keperawatan
                SET kode_perawatan = %s, catatan = %s
                WHERE id_kunjungan = %s
            """, [catatan, id_kunjungan])

        rekam_medis_context = {
            'suhu': suhu,
            'berat_badan': berat_badan,
            'jenis_perawatan': jenis_perawatan,
            'catatan': catatan,
            'id_kunjungan': id_kunjungan
        }

        # Success message
        messages.success(request, 'Rekam medis berhasil dibuat!')

        # Render the same page (view_rekam_medis) with the updated Rekam Medis data
        return render(request, 'view_rekam_medis.html', rekam_medis_context)

    # Get the list of jenis perawatan
    with connection.cursor() as cursor:
        cursor.execute("SET search_path TO pet_clinic;")
        cursor.execute("""
            SELECT kode_perawatan, nama_perawatan FROM perawatan
            ORDER BY kode_perawatan
        """)
        jenis_perawatan_list = cursor.fetchall()

    return render(request, 'create_rekam_medis.html', {
        'id_kunjungan': id_kunjungan,
        'kunjungan_data': kunjungan_data,
        'jenis_perawatan_list': jenis_perawatan_list
    })



from django.shortcuts import render, redirect
from django.db import connection
from django.contrib import messages

def update_rekam_medis(request, id_kunjungan):
    if request.method == "POST":
        suhu = request.POST.get('suhu')
        berat_badan = request.POST.get('berat_badan')
        jenis_perawatan = request.POST.get('jenis_perawatan')
        catatan = request.POST.get('catatan', '')

        # Update the rekam medis for this kunjungan
        with connection.cursor() as cursor:
            cursor.execute("SET search_path TO pet_clinic;")
            cursor.execute("""
                UPDATE kunjungan
                SET suhu = %s, berat_badan = %s
                WHERE id_kunjungan = %s
            """, [suhu, berat_badan, id_kunjungan])
        with connection.cursor() as cursor:
            cursor.execute("SET search_path TO pet_clinic;")
            cursor.execute("""
                UPDATE kunjungan_keperawatan
                SET catatan = %s
                WHERE id_kunjungan = %s
            """, [catatan, id_kunjungan])
        
        # Redirect to view the updated rekam medis (render view instead of redirect)
        rekam_medis_context = {
            'suhu': suhu,
            'berat_badan': berat_badan,
            'jenis_perawatan': jenis_perawatan,
            'catatan': catatan,
            'id_kunjungan': id_kunjungan
        }

        # Success message
        messages.success(request, 'Rekam medis berhasil dibuat!')

        # Render the same page (view_rekam_medis) with the updated Rekam Medis data
        return render(request, 'view_rekam_medis.html', rekam_medis_context)
    # If the method is GET, fetch the current rekam medis data to populate the form
    with connection.cursor() as cursor:
        cursor.execute("SET search_path TO pet_clinic;")
        cursor.execute("""
            SELECT
                k.id_kunjungan,
                k.no_identitas_klien,
                k.nama_hewan,
                k.tipe_kunjungan,
                k.suhu,
                k.berat_badan,
                r.kode_perawatan,
                r.catatan
            FROM kunjungan k
            LEFT JOIN kunjungan_keperawatan r ON k.id_kunjungan = r.id_kunjungan
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

    return render(request, 'update_rekam_medis.html', {
        'id_kunjungan': id_kunjungan,
        'no_identitas_klien': kunjungan_data[1],
        'nama_hewan': kunjungan_data[2],
        'tipe_kunjungan': kunjungan_data[3],
        'suhu': kunjungan_data[4],  # Suhu from rekam medis
        'berat_badan': kunjungan_data[5],  # Berat badan from rekam medis
        'jenis_perawatan': kunjungan_data[6],  # Jenis perawatan from rekam medis
        'catatan': kunjungan_data[7],  # Catatan from rekam medis
        'jenis_perawatan_list': jenis_perawatan_list
    })
