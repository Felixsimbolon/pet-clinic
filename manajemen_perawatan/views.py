from django.shortcuts import render, redirect
from django.db import connection
import re

def list_treatment_types(request):
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
