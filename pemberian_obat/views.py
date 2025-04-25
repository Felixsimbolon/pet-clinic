# views.py
from django.shortcuts import render, redirect
from django.db import connection

def list_prescriptions(request):
    with connection.cursor() as cursor:
        cursor.execute("SET search_path TO pet_clinic;")

        cursor.execute("""
            SELECT
              po.kode_perawatan,
              po.kode_obat,
              po.kuantitas_obat,
              o.harga
            FROM perawatan_obat po
            JOIN obat o
              ON po.kode_obat = o.kode
            ORDER BY po.kode_perawatan, po.kode_obat
        """)
        rows = cursor.fetchall()

    prescriptions = []
    for kode_prw, kode_ob, qty, harga in rows:
        prescriptions.append({
            'kode_perawatan': kode_prw,
            'kode_obat':      kode_ob,
            'kuantitas':      qty,
            'total_str':      f"Rp{qty*harga:,.0f}".replace(',', '.'),
        })

    return render(request, 'list_prescriptions.html', {
        'prescriptions': prescriptions
    })


def create_prescription(request):
    if request.method == 'POST':
        kode_perawatan = request.POST['perawatan']
        kode_obat      = request.POST['obat']
        qty            = int(request.POST['quantity'])

        with connection.cursor() as cursor:
            cursor.execute("SET search_path TO pet_clinic;")

            cursor.execute("""
                INSERT INTO perawatan_obat (kode_perawatan, kode_obat, kuantitas_obat)
                VALUES (%s, %s, %s)
            """, [kode_perawatan, kode_obat, qty])

        return redirect('prescription_list')

    # GET: ambil daftar perawatan & obat
    with connection.cursor() as cursor:
        cursor.execute("SET search_path TO pet_clinic;")

        cursor.execute("""
            SELECT kode_perawatan, nama_perawatan
            FROM perawatan
            ORDER BY kode_perawatan
        """)
        treatments = cursor.fetchall()   

        cursor.execute("""
            SELECT kode, nama, stok
            FROM obat
            ORDER BY kode
        """)
        medicines = cursor.fetchall()    

    return render(request, 'create_prescription.html', {
        'treatments': treatments,
        'medicines':  medicines,
    })


def delete_prescription(request):
    kode_p = request.GET['kode_perawatan']
    kode_o = request.GET['kode_obat']

    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute("SET search_path TO pet_clinic;")

            cursor.execute(
                "DELETE FROM perawatan_obat WHERE kode_perawatan=%s AND kode_obat=%s",
                [kode_p, kode_o]
            )
        return redirect('prescription_list')

    return render(request, 'confirm_delete.html', {
        'treatment_code': kode_p,
        'medicine_code':  kode_o,
    })