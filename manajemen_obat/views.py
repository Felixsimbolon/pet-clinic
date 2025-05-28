import re
from django.shortcuts import render, redirect
from django.db import connection

def list_medicines(request):
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
        
    q = request.GET.get('q', '').strip()

    with connection.cursor() as cursor:
        cursor.execute("SET search_path TO pet_clinic,public;")

        if q:
            cursor.execute("""
                SELECT kode, nama, harga, stok, dosis
                FROM obat
                WHERE nama ILIKE %s
                ORDER BY kode;
            """, [f'%{q}%'])
        else:
            cursor.execute("""
                SELECT kode, nama, harga, stok, dosis
                FROM obat
                ORDER BY kode;
            """)

        rows = cursor.fetchall()

    medicines = []
    for kode, nama, harga, stok, dosis in rows:
        medicines.append({
            'kode':      kode,
            'nama':      nama,
            'harga_str': f"Rp{harga:,.0f}".replace(',', '.'),
            'stok':      stok,
            'dosis':     dosis,
        })

    return render(request, 'list_medicines.html', {
        'medicines': medicines,
        'q':         q,              
    })

def list_medicines_perawat(request):
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
        
    q = request.GET.get('q', '').strip()

    with connection.cursor() as cursor:
        cursor.execute("SET search_path TO pet_clinic,public;")

        if q:
            cursor.execute("""
                SELECT kode, nama, harga, stok, dosis
                FROM obat
                WHERE nama ILIKE %s
                ORDER BY kode;
            """, [f'%{q}%'])
        else:
            cursor.execute("""
                SELECT kode, nama, harga, stok, dosis
                FROM obat
                ORDER BY kode;
            """)

        rows = cursor.fetchall()

    medicines = []
    for kode, nama, harga, stok, dosis in rows:
        medicines.append({
            'kode':      kode,
            'nama':      nama,
            'harga_str': f"Rp{harga:,.0f}".replace(',', '.'),
            'stok':      stok,
            'dosis':     dosis,
        })

    return render(request, 'list_medicines_perawat.html', {
        'medicines': medicines,
        'q':         q,              
    })

def create_medicine(request):
    error = None
    if request.method == 'POST':
        nama  = request.POST.get('nama', '').strip()
        harga = request.POST.get('harga', '').strip()
        dosis = request.POST.get('dosis', '').strip()
        stok  = request.POST.get('stok', '').strip()

        if not nama or not harga.isdigit() or not stok.isdigit():
            error = "Nama harus diisi; Harga dan Stok harus bilangan bulat"
        else:
            harga, stok = int(harga), int(stok)
            with connection.cursor() as cursor:
                cursor.execute("SET search_path TO pet_clinic,public;")
                cursor.execute("""
                    SELECT kode
                    FROM obat
                    ORDER BY kode DESC
                    LIMIT 1;
                """)
                last = cursor.fetchone()
                if last:
                    m = re.search(r'MED(\d+)', last[0])
                    num = int(m.group(1)) + 1 if m else 1
                else:
                    num = 1
                kode_baru = f"MED{num:03d}"

                cursor.execute("""
                    INSERT INTO obat (kode, nama, harga, stok, dosis)
                    VALUES (%s, %s, %s, %s, %s);
                """, [kode_baru, nama, harga, stok, dosis])

            return redirect('medicine_list')

    return render(request, 'create_medicine.html', {
        'error': error
    })

def create_medicine_perawat(request):
    error = None
    if request.method == 'POST':
        nama  = request.POST.get('nama', '').strip()
        harga = request.POST.get('harga', '').strip()
        dosis = request.POST.get('dosis', '').strip()
        stok  = request.POST.get('stok', '').strip()

        if not nama or not harga.isdigit() or not stok.isdigit():
            error = "Nama harus diisi; Harga dan Stok harus bilangan bulat"
        else:
            harga, stok = int(harga), int(stok)
            with connection.cursor() as cursor:
                cursor.execute("SET search_path TO pet_clinic,public;")
                cursor.execute("""
                    SELECT kode
                    FROM obat
                    ORDER BY kode DESC
                    LIMIT 1;
                """)
                last = cursor.fetchone()
                if last:
                    m = re.search(r'MED(\d+)', last[0])
                    num = int(m.group(1)) + 1 if m else 1
                else:
                    num = 1
                kode_baru = f"MED{num:03d}"

                cursor.execute("""
                    INSERT INTO obat (kode, nama, harga, stok, dosis)
                    VALUES (%s, %s, %s, %s, %s);
                """, [kode_baru, nama, harga, stok, dosis])

            return redirect('medicine_list_perawat')

    return render(request, 'create_medicine_perawat.html', {
        'error': error
    })

def update_medicine(request, kode):
    error = None
    if request.method == 'POST':
        nama  = request.POST.get('nama', '').strip()
        harga = request.POST.get('harga', '').strip()
        dosis = request.POST.get('dosis', '').strip()

        if not nama or not harga.isdigit():
            error = "Nama harus diisi dan Harga harus bilangan bulat"
        else:
            harga = int(harga)
            with connection.cursor() as cursor:
                cursor.execute("SET search_path TO pet_clinic,public;")
                cursor.execute("""
                    UPDATE obat
                    SET nama=%s, harga=%s, dosis=%s
                    WHERE kode=%s;
                """, [nama, harga, dosis, kode])
            return redirect('medicine_list')
    else:
        with connection.cursor() as cursor:
            cursor.execute("SET search_path TO pet_clinic,public;")
            cursor.execute("""
                SELECT nama, harga, dosis
                FROM obat
                WHERE kode=%s;
            """, [kode])
            row = cursor.fetchone()
        if row:
            nama, harga, dosis = row
        else:
            nama, harga, dosis = '', 0, ''

    return render(request, 'update_medicine.html', {
        'kode': kode,
        'nama': nama,
        'harga': harga,
        'dosis': dosis,
        'error': error
    })

def update_medicine_perawat(request, kode):
    error = None
    if request.method == 'POST':
        nama  = request.POST.get('nama', '').strip()
        harga = request.POST.get('harga', '').strip()
        dosis = request.POST.get('dosis', '').strip()

        if not nama or not harga.isdigit():
            error = "Nama harus diisi dan Harga harus bilangan bulat"
        else:
            harga = int(harga)
            with connection.cursor() as cursor:
                cursor.execute("SET search_path TO pet_clinic,public;")
                cursor.execute("""
                    UPDATE obat
                    SET nama=%s, harga=%s, dosis=%s
                    WHERE kode=%s;
                """, [nama, harga, dosis, kode])
            return redirect('medicine_list_perawat')
    else:
        with connection.cursor() as cursor:
            cursor.execute("SET search_path TO pet_clinic,public;")
            cursor.execute("""
                SELECT nama, harga, dosis
                FROM obat
                WHERE kode=%s;
            """, [kode])
            row = cursor.fetchone()
        if row:
            nama, harga, dosis = row
        else:
            nama, harga, dosis = '', 0, ''

    return render(request, 'update_medicine_perawat.html', {
        'kode': kode,
        'nama': nama,
        'harga': harga,
        'dosis': dosis,
        'error': error
    })

def update_medicine_stock(request, kode):
    error = None
    if request.method == 'POST':
        stok = request.POST.get('stok', '').strip()
        if not stok.isdigit():
            error = "Stok harus bilangan bulat"
        else:
            stok = int(stok)
            with connection.cursor() as cursor:
                cursor.execute("SET search_path TO pet_clinic,public;")
                cursor.execute("""
                    UPDATE obat
                    SET stok=%s
                    WHERE kode=%s;
                """, [stok, kode])
            return redirect('medicine_list')
    else:
        with connection.cursor() as cursor:
            cursor.execute("SET search_path TO pet_clinic,public;")
            cursor.execute("""
                SELECT nama, stok
                FROM obat
                WHERE kode=%s;
            """, [kode])
            row = cursor.fetchone()
        if row:
            nama, stok = row
        else:
            nama, stok = '', 0

    return render(request, 'update_medicine_stock.html', {
        'kode': kode,
        'nama': nama,
        'stok': stok,
        'error': error
    })

def update_medicine_stock_perawat(request, kode):
    error = None
    if request.method == 'POST':
        stok = request.POST.get('stok', '').strip()
        if not stok.isdigit():
            error = "Stok harus bilangan bulat"
        else:
            stok = int(stok)
            with connection.cursor() as cursor:
                cursor.execute("SET search_path TO pet_clinic,public;")
                cursor.execute("""
                    UPDATE obat
                    SET stok=%s
                    WHERE kode=%s;
                """, [stok, kode])
            return redirect('medicine_list_perawat')
    else:
        with connection.cursor() as cursor:
            cursor.execute("SET search_path TO pet_clinic,public;")
            cursor.execute("""
                SELECT nama, stok
                FROM obat
                WHERE kode=%s;
            """, [kode])
            row = cursor.fetchone()
        if row:
            nama, stok = row
        else:
            nama, stok = '', 0

    return render(request, 'update_medicine_stock_perawat.html', {
        'kode': kode,
        'nama': nama,
        'stok': stok,
        'error': error
    })

def delete_medicine(request, kode):
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute("SET search_path TO pet_clinic,public;")
            cursor.execute("DELETE FROM obat WHERE kode=%s;", [kode])
        return redirect('medicine_list')

    with connection.cursor() as cursor:
        cursor.execute("SET search_path TO pet_clinic,public;")
        cursor.execute("SELECT nama FROM obat WHERE kode=%s;", [kode])
        row = cursor.fetchone()
    nama = row[0] if row else ''

    return render(request, 'confirm_delete_medicine.html', {
        'kode': kode,
        'nama': nama
    })

def delete_medicine_perawat(request, kode):
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute("SET search_path TO pet_clinic,public;")
            cursor.execute("DELETE FROM obat WHERE kode=%s;", [kode])
        return redirect('medicine_list_perawat')

    with connection.cursor() as cursor:
        cursor.execute("SET search_path TO pet_clinic,public;")
        cursor.execute("SELECT nama FROM obat WHERE kode=%s;", [kode])
        row = cursor.fetchone()
    nama = row[0] if row else ''

    return render(request, 'confirm_delete_medicine_perawat.html', {
        'kode': kode,
        'nama': nama
    })