from django.shortcuts import redirect, render
from django.urls import reverse
from django.db import connection
from django.http import Http404
from django.contrib import messages

def index(request):
    """Redirect langsung ke halaman vaksinasi hewan"""
    return redirect('manajemen_vaksinasi:vaksinasi_hewan')

def index2(request):
    """Redirect langsung ke halaman vaksinasi hewan klien side"""
    return redirect('manajemen_vaksinasi:vaksinasi_hewan_klien')

def vaksinasi_hewan_klien(request):
    """View untuk halaman vaksinasi hewan klien side"""
    # Get filter parameters
    pet_filter = request.GET.get('pet', None)
    vaksin_filter = request.GET.get('vaksin', None)
    
    # Base query for vaccination list
    base_query = """
        SELECT k.id_kunjungan, k.nama_hewan, k.no_identitas_klien, k.kode_vaksin,
        v.nama as nama_vaksin, v.harga, k.tipe_kunjungan, k.timestamp_awal, k.timestamp_akhir
        FROM kunjungan k
        LEFT JOIN vaksin v ON k.kode_vaksin = v.kode
        WHERE k.kode_vaksin IS NOT NULL
    """
    
    # Apply filters if present
    params = []
    if pet_filter:
        base_query += " AND k.nama_hewan = %s"
        params.append(pet_filter)
    
    if vaksin_filter:
        base_query += " AND k.kode_vaksin = %s"
        params.append(vaksin_filter)
    
    base_query += " ORDER BY k.timestamp_awal DESC;"
    
    # Ambil data kunjungan vaksinasi hewan dari database
    with connection.cursor() as cursor:
        cursor.execute("SET search_path TO pet_clinic;")
        cursor.execute(base_query, params)
        rows = cursor.fetchall()
        
        vaksinasi_list = [
            {
                'id_kunjungan': row[0],
                'nama_hewan': row[1],
                'no_identitas_klien': row[2],
                'kode_vaksin': row[3],
                'nama_vaksin': row[4] if row[4] else '-',
                'harga': row[5] if row[5] else 0,
                'tipe_kunjungan': row[6],
                'timestamp_awal': row[7],
                'timestamp_akhir': row[8],
            }
            for row in rows
        ]
    
    # Get unique pets for filter dropdown
    with connection.cursor() as cursor:
        cursor.execute("SET search_path TO pet_clinic;")
        cursor.execute("""
            SELECT DISTINCT nama_hewan
            FROM kunjungan
            WHERE kode_vaksin IS NOT NULL
            ORDER BY nama_hewan;
        """)
        pet_rows = cursor.fetchall()
        pet_list = [{'nama_hewan': row[0]} for row in pet_rows]
    
    # Get unique vaccines for filter dropdown
    with connection.cursor() as cursor:
        cursor.execute("SET search_path TO pet_clinic;")
        cursor.execute("""
            SELECT DISTINCT v.kode, v.nama
            FROM vaksin v
            JOIN kunjungan k ON v.kode = k.kode_vaksin
            ORDER BY v.nama;
        """)
        vaksin_rows = cursor.fetchall()
        vaksin_list = [
            {
                'kode': row[0],
                'nama': row[1],
            }
            for row in vaksin_rows
        ]
    
    context = {
        'vaksinasi_list': vaksinasi_list,
        'pet_list': pet_list,
        'vaksin_list': vaksin_list
    }
    
    return render(request, 'manajemen_vaksinasi/vaksinasi_hewan_klien.html', context)

def data_stok_vaksin(request):
    """View untuk halaman data stok vaksin"""
    # Ambil data stok vaksin dari database
    with connection.cursor() as cursor:
        cursor.execute("SET search_path TO pet_clinic;")
        cursor.execute("""
            SELECT kode, nama, harga, stok
            FROM vaksin
            ORDER BY kode;
        """)
        rows = cursor.fetchall()
        
    stok_list = [
        {
            'no': idx,
            'kode': row[0],
            'nama': row[1],
            'harga': f"Rp{row[2]:,.0f}".replace(',', '.'),
            'stok': row[3],
        }
        for idx, row in enumerate(rows, 1)
    ]
    
    context = {
        'stok_list': stok_list
    }
    return render(request, 'manajemen_vaksinasi/data_stok_vaksin.html', context)

def create_vaccine(request):
    """View untuk menambahkan vaksin baru"""
    if request.method == 'POST':
        # Ambil data form
        nama = request.POST.get('nama')
        harga = request.POST.get('harga')
        stok_awal = request.POST.get('stokAwal')
        
        # Validasi input data
        if not all([nama, harga, stok_awal]):
            messages.error(request, 'Semua field harus diisi')
            return redirect('manajemen_vaksinasi:data_stok_vaksin')
            
        # Masukkan data ke dalam database
        with connection.cursor() as cursor:
            cursor.execute("SET search_path TO pet_clinic;")
            cursor.execute("""
                INSERT INTO vaksin (nama, harga, stok)
                VALUES (%s, %s, %s)
            """, [nama, harga, stok_awal])
            
        messages.success(request, 'Vaksin berhasil ditambahkan')
        return redirect('manajemen_vaksinasi:data_stok_vaksin')
        
    # Jika bukan POST, redirect ke daftar vaksin
    return redirect('manajemen_vaksinasi:data_stok_vaksin')

def add_vaccine_stock(request):
    """View untuk menambahkan stok vaksin"""
    if request.method == 'POST':
        # Get form data
        kode_vaksin = request.POST.get('kode_vaksin')
        jumlah = request.POST.get('jumlah')
        
        # Validate input data
        if not all([kode_vaksin, jumlah]):
            messages.error(request, 'Semua field harus diisi')
            return redirect('manajemen_vaksinasi:data_stok_vaksin')
            
        try:
            jumlah = int(jumlah)
            if jumlah <= 0:
                messages.error(request, 'Jumlah stok harus lebih dari 0')
                return redirect('manajemen_vaksinasi:data_stok_vaksin')
                
            # Update stok vaksin
            with connection.cursor() as cursor:
                cursor.execute("SET search_path TO pet_clinic;")
                cursor.execute("""
                    UPDATE vaksin
                    SET stok = stok + %s
                    WHERE kode = %s
                """, [jumlah, kode_vaksin])
                
            messages.success(request, f'Stok vaksin berhasil ditambahkan')
            return redirect('manajemen_vaksinasi:data_stok_vaksin')
            
        except ValueError:
            messages.error(request, 'Jumlah stok harus berupa angka')
            return redirect('manajemen_vaksinasi:data_stok_vaksin')
            
    return redirect('manajemen_vaksinasi:data_stok_vaksin')

def edit_vaccine(request, kode):
    """View untuk mengedit data vaksin"""
    if request.method == 'POST':
        # Get form data
        nama_vaksin = request.POST.get('nama_vaksin')
        harga = request.POST.get('harga')
        stok = request.POST.get('stok')
        
        # Validate input data
        if not all([nama_vaksin, harga, stok]):
            messages.error(request, 'Semua field harus diisi')
            return redirect('manajemen_vaksinasi:data_stok_vaksin')
            
        try:
            harga = float(harga)
            stok = int(stok)
            
            # Update data vaksin
            with connection.cursor() as cursor:
                cursor.execute("SET search_path TO pet_clinic;")
                cursor.execute("""
                    UPDATE vaksin
                    SET nama = %s, harga = %s, stok = %s
                    WHERE kode = %s
                """, [nama_vaksin, harga, stok, kode])
                
            messages.success(request, 'Data vaksin berhasil diperbarui')
            return redirect('manajemen_vaksinasi:data_stok_vaksin')
            
        except ValueError:
            messages.error(request, 'Format data tidak valid')
            return redirect('manajemen_vaksinasi:data_stok_vaksin')
            
    # If not POST request, just redirect to the vaccine list
    return redirect('manajemen_vaksinasi:data_stok_vaksin')

def delete_vaccine(request, kode):
    """View untuk menghapus data vaksin"""
    if request.method == 'POST':
        # Check if vaccine is used in any vaccinations
        with connection.cursor() as cursor:
            cursor.execute("SET search_path TO pet_clinic;")
            cursor.execute("""
                SELECT COUNT(*) FROM kunjungan
                WHERE kode_vaksin = %s
            """, [kode])
            count = cursor.fetchone()[0]
            
            if count > 0:
                messages.error(request, 'Vaksin tidak dapat dihapus karena sedang digunakan')
                return redirect('manajemen_vaksinasi:data_stok_vaksin')
                
            # Perform deletion for vaccine by 'kode'
            cursor.execute("DELETE FROM vaksin WHERE kode = %s", [kode])
            
        messages.success(request, 'Vaksin berhasil dihapus')
        return redirect('manajemen_vaksinasi:data_stok_vaksin')
        
    # If not POST request, just redirect to the vaccine list
    return redirect('manajemen_vaksinasi:data_stok_vaksin')

def vaksinasi_hewan(request):
    """View untuk halaman vaksinasi hewan"""
    # Ambil data kunjungan vaksinasi hewan dari database
    with connection.cursor() as cursor:
        cursor.execute("SET search_path TO pet_clinic;")
        cursor.execute("""
            SELECT k.id_kunjungan, k.nama_hewan, k.no_identitas_klien, k.kode_vaksin, 
                   k.tipe_kunjungan, k.timestamp_awal, k.timestamp_akhir, v.nama as nama_vaksin
            FROM kunjungan k
            LEFT JOIN vaksin v ON k.kode_vaksin = v.kode
            ORDER BY k.id_kunjungan;
        """)
        rows = cursor.fetchall()
        
    vaksinasi_list = [
        {
            'id_kunjungan': row[0],
            'nama_hewan': row[1],
            'no_identitas_klien': row[2],
            'kode_vaksin': row[3],
            'nama_vaksin': row[7] if row[7] else '-',
            'tipe_kunjungan': row[4],
            'timestamp_awal': row[5],
            'timestamp_akhir': row[6],
        }
        for row in rows
    ]
    
    # Ambil data stok vaksin untuk dropdown
    with connection.cursor() as cursor:
        cursor.execute("SET search_path TO pet_clinic;")
        cursor.execute("""
            SELECT kode, nama, harga, stok
            FROM vaksin
            WHERE stok > 0
            ORDER BY kode;
        """)
        vaksin_rows = cursor.fetchall()
        
    stok_vaksin = [
        {
            'kode': row[0],
            'nama': row[1],
            'harga': row[2],
            'stok': row[3],
        }
        for row in vaksin_rows
    ]
    
    # Ambil data kunjungan untuk dropdown
    with connection.cursor() as cursor:
        cursor.execute("SET search_path TO pet_clinic;")
        cursor.execute("""
            SELECT DISTINCT id_kunjungan
            FROM kunjungan
            WHERE kode_vaksin IS NULL
            ORDER BY id_kunjungan;
        """)
        kunjungan_rows = cursor.fetchall()
        
    kunjungan_list = [
        {
            'id_kunjungan': row[0],
        }
        for row in kunjungan_rows
    ]
    
    context = {
        'vaksinasi_list': vaksinasi_list,
        'stok_vaksin': stok_vaksin,
        'kunjungan_list': kunjungan_list
    }
    return render(request, 'manajemen_vaksinasi/vaksinasi_hewan.html', context)

def create_vaksinasi(request):
    """View untuk membuat vaksinasi baru"""
    if request.method == 'POST':
        kunjungan_id = request.POST.get('kunjungan_id')
        vaksin_id = request.POST.get('vaksin_id')
        
        if not all([kunjungan_id, vaksin_id]):
            messages.error(request, 'Semua field harus diisi')
            return redirect('manajemen_vaksinasi:vaksinasi_hewan')
            
        # Periksa stok vaksin
        with connection.cursor() as cursor:
            cursor.execute("SET search_path TO pet_clinic;")
            cursor.execute("""
                SELECT stok FROM vaksin
                WHERE kode = %s
            """, [vaksin_id])
            result = cursor.fetchone()
            
            if not result or result[0] <= 0:
                messages.error(request, 'Stok vaksin tidak mencukupi')
                return redirect('manajemen_vaksinasi:vaksinasi_hewan')
                
            # Update data di database
            cursor.execute("""
                UPDATE kunjungan
                SET kode_vaksin = %s
                WHERE id_kunjungan = %s;
            """, [vaksin_id, kunjungan_id])
            
            # Kurangi stok vaksin
            cursor.execute("""
                UPDATE vaksin
                SET stok = stok - 1
                WHERE kode = %s;
            """, [vaksin_id])
            
        messages.success(request, f'Vaksinasi berhasil dibuat untuk kunjungan {kunjungan_id}')
        return redirect('manajemen_vaksinasi:vaksinasi_hewan')
        
    return redirect('manajemen_vaksinasi:vaksinasi_hewan')

def update_vaksinasi(request, id_kunjungan):
    """View untuk mengupdate vaksinasi"""
    if request.method == 'POST':
        vaksin_id = request.POST.get('vaksin_id')
        
        if not vaksin_id:
            messages.error(request, 'Vaksin harus dipilih')
            return redirect('manajemen_vaksinasi:vaksinasi_hewan')
            
        # Get current vaccine code
        with connection.cursor() as cursor:
            cursor.execute("SET search_path TO pet_clinic;")
            cursor.execute("""
                SELECT kode_vaksin
                FROM kunjungan
                WHERE id_kunjungan = %s;
            """, [id_kunjungan])
            result = cursor.fetchone()
            
            if not result:
                messages.error(request, 'Kunjungan tidak ditemukan')
                return redirect('manajemen_vaksinasi:vaksinasi_hewan')
                
            current_vaksin = result[0]
            
            # Periksa stok vaksin baru jika berbeda dengan yang lama
            if current_vaksin != vaksin_id:
                cursor.execute("""
                    SELECT stok FROM vaksin
                    WHERE kode = %s
                """, [vaksin_id])
                result = cursor.fetchone()
                
                if not result or result[0] <= 0:
                    messages.error(request, 'Stok vaksin tidak mencukupi')
                    return redirect('manajemen_vaksinasi:vaksinasi_hewan')
            
            # Return the old vaccine to stock
            if current_vaksin:
                cursor.execute("""
                    UPDATE vaksin
                    SET stok = stok + 1
                    WHERE kode = %s;
                """, [current_vaksin])
                
            # Update to new vaccine
            cursor.execute("""
                UPDATE kunjungan
                SET kode_vaksin = %s
                WHERE id_kunjungan = %s;
            """, [vaksin_id, id_kunjungan])
            
            # Reduce stock of new vaccine
            cursor.execute("""
                UPDATE vaksin
                SET stok = stok - 1
                WHERE kode = %s;
            """, [vaksin_id])
            
        messages.success(request, f'Vaksinasi berhasil diupdate untuk kunjungan {id_kunjungan}')
        return redirect('manajemen_vaksinasi:vaksinasi_hewan')
        
    return redirect('manajemen_vaksinasi:vaksinasi_hewan')

def delete_vaksinasi(request, id_kunjungan):
    """View untuk menghapus vaksinasi"""
    if request.method == 'POST':
        # Get current vaccine code
        with connection.cursor() as cursor:
            cursor.execute("SET search_path TO pet_clinic;")
            cursor.execute("""
                SELECT kode_vaksin
                FROM kunjungan
                WHERE id_kunjungan = %s;
            """, [id_kunjungan])
            result = cursor.fetchone()
            
            if not result:
                messages.error(request, 'Kunjungan tidak ditemukan')
                return redirect('manajemen_vaksinasi:vaksinasi_hewan')
                
            current_vaksin = result[0]
            
            # Return the vaccine to stock
            if current_vaksin:
                cursor.execute("""
                    UPDATE vaksin
                    SET stok = stok + 1
                    WHERE kode = %s;
                """, [current_vaksin])
                
                # Set vaccine code to NULL
                cursor.execute("""
                    UPDATE kunjungan
                    SET kode_vaksin = NULL
                    WHERE id_kunjungan = %s;
                """, [id_kunjungan])
                
        messages.success(request, f'Vaksinasi berhasil dihapus untuk kunjungan {id_kunjungan}')
        return redirect('manajemen_vaksinasi:vaksinasi_hewan')
        
    return redirect('manajemen_vaksinasi:vaksinasi_hewan')