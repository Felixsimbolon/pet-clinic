from django.shortcuts import render, redirect
from django.db import connection
from django.shortcuts import render, redirect
from django.db import connection, DatabaseError


def list_prescriptions(request):
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
        
    error         = None
    selected_tr   = None
    selected_med  = None
    entered_qty   = None

    if request.method == 'POST':
        selected_tr  = request.POST.get('perawatan')
        selected_med = request.POST.get('obat')
        entered_qty  = request.POST.get('quantity')

        try:
            qty = int(entered_qty)
            with connection.cursor() as cursor:
                if connection.vendor == 'postgresql':
                    cursor.execute("SET search_path TO pet_clinic;")

                cursor.execute("""
                    INSERT INTO perawatan_obat
                      (kode_perawatan, kode_obat, kuantitas_obat)
                    VALUES (%s, %s, %s)
                """, [selected_tr, selected_med, qty])

            return redirect('prescription_list')

        except (DatabaseError, ValueError) as e:
            raw = str(e)
            if 'CONTEXT:' in raw:
                error = raw.split('CONTEXT:')[0].strip()
            else:
                error = raw

    with connection.cursor() as cursor:
        if connection.vendor == 'postgresql':
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
        'treatments':   treatments,
        'medicines':    medicines,
        'error':        error,
        'selected_tr':  selected_tr,
        'selected_med': selected_med,
        'entered_qty':  entered_qty,
    })


def delete_prescription(request):
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
        
    kode_p = request.GET.get('kode_perawatan')
    kode_o = request.GET.get('kode_obat')

    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute("SET search_path TO pet_clinic;")
            cursor.execute("""
                DELETE FROM perawatan_obat
                WHERE kode_perawatan = %s AND kode_obat = %s
            """, [kode_p, kode_o])
        return redirect('prescription_list')

    return render(request, 'confirm_delete.html', {
        'treatment_code': kode_p,
        'medicine_code':  kode_o,
    })