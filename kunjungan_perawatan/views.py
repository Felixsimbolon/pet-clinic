from django.shortcuts import render
from django.shortcuts import render
from django.db import connection

def daftar_perawatan(request):
    # ambil semua kolom dari tabel kunjungan_keperawatan
    with connection.cursor() as cursor:
        cursor.execute("SET search_path TO pet_clinic;")

        cursor.execute("""
            SELECT
                id_kunjungan,
                nama_hewan,
                no_identitas_klien,
                no_front_desk,
                no_perawat_hewan,
                no_dokter_hewan,
                KUNJUNGAN_KEPERAWATAN.kode_perawatan,
                catatan,
                nama_perawatan
            FROM KUNJUNGAN_KEPERAWATAN,PERAWATAN 
            WHERE KUNJUNGAN_KEPERAWATAN.kode_perawatan = PERAWATAN.kode_perawatan
            ORDER BY id_kunjungan
        """)
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()

    # ubah ke list of dict
    treatments = [
        dict(zip(columns, row))
        for row in rows
    ]

    return render(request, 'daftar_perawatan.html', {
        'treatments': treatments
    })

# Create your views here.
