from django.shortcuts import redirect, render
from django.urls import reverse
from django.db import connection
from django.http import Http404
from django.http import HttpResponse
from django.contrib import messages

def index(request):
    """View untuk halaman utama aplikasi merah"""
    # Data dummy untuk dashboard
    context = {
        'total_vaksin': 28,  
        'total_stok': 75,   
        'total_klien': 42,   
    }
    return render(request, 'merah/index.html', context)

def vaksinasi_hewan(request):
    """View untuk halaman vaksinasi hewan"""
    # Ambil data kunjungan vaksinasi hewan dari database
    with connection.cursor() as cursor:
        cursor.execute("SET search_path TO pet_clinic;")
        cursor.execute("""
            SELECT id_kunjungan, nama_hewan, no_identitas_klien, kode_vaksin, tipe_kunjungan, timestamp_awal, timestamp_akhir
            FROM kunjungan
            ORDER BY id_kunjungan;
        """)
        rows = cursor.fetchall()
        vaksinasi_list = [
            {
                'id_kunjungan': id_kunjungan,
                'nama_hewan': nama_hewan,
                'no_identitas_klien': no_identitas_klien,
                'kode_vaksin': kode_vaksin,
                'tipe_kunjungan': tipe_kunjungan,
                'timestamp_awal': timestamp_awal,
                'timestamp_akhir': timestamp_akhir,
            }
            for id_kunjungan, nama_hewan, no_identitas_klien, kode_vaksin, tipe_kunjungan, timestamp_awal, timestamp_akhir in rows
        ]
        
        # Ambil data stok vaksin untuk dropdown
        cursor.execute("""
            SELECT kode, nama, harga, stok
            FROM vaksin
            ORDER BY kode;
        """)
        vaksin_rows = cursor.fetchall()
        stok_vaksin = [
            {
                'kode': kode,
                'nama': nama,
                'harga': harga,
                'stok': stok,
            }
            for kode, nama, harga, stok in vaksin_rows
        ]
        
        # Ambil data kunjungan untuk dropdown
        cursor.execute("""
            SELECT DISTINCT id_kunjungan
            FROM kunjungan
            ORDER BY id_kunjungan;
        """)
        kunjungan_rows = cursor.fetchall()
        kunjungan_list = [
            {
                'id_kunjungan': id_kunjungan,
            }
            for (id_kunjungan,) in kunjungan_rows
        ]
    
    context = {
        'vaksinasi_list': vaksinasi_list,
        'stok_vaksin': stok_vaksin,
        'kunjungan_list': kunjungan_list
    }
    return render(request, 'merah/vaksinasi_hewan.html', context)

def create_vaksinasi(request):
    """View untuk membuat vaksinasi baru"""
    if request.method == 'POST':
        kunjungan_id = request.POST.get('kunjungan_id')
        vaksin_id = request.POST.get('vaksin_id')
        
        # Update data di database
        with connection.cursor() as cursor:
            cursor.execute("SET search_path TO pet_clinic;")
            cursor.execute("""
                UPDATE kunjungan
                SET kode_vaksin = %s
                WHERE id_kunjungan = %s;
            """, [vaksin_id, kunjungan_id])
            
            # Kurangi stok vaksin
            cursor.execute("""
                UPDATE vaksin
                SET stok = stok - 1
                WHERE kode = %s AND stok > 0;
            """, [vaksin_id])
        
        messages.success(request, f'Vaksinasi berhasil dibuat untuk kunjungan {kunjungan_id}')
    
    return redirect('merah:vaksinasi_hewan')

def update_vaksinasi(request, id_kunjungan):
    """View untuk mengupdate vaksinasi"""
    if request.method == 'POST':
        vaksin_id = request.POST.get('vaksin_id')
        
        # Get current vaccine code
        with connection.cursor() as cursor:
            cursor.execute("SET search_path TO pet_clinic;")
            cursor.execute("""
                SELECT kode_vaksin
                FROM kunjungan
                WHERE id_kunjungan = %s;
            """, [id_kunjungan])
            current_vaksin = cursor.fetchone()[0]
            
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
                WHERE kode = %s AND stok > 0;
            """, [vaksin_id])
        
        messages.success(request, f'Vaksinasi berhasil diupdate untuk kunjungan {id_kunjungan}')
    
    return redirect('merah:vaksinasi_hewan')

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
            current_vaksin = cursor.fetchone()[0]
            
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
    
    return redirect('merah:vaksinasi_hewan')



# DATA KLIEN HEWAN
def data_klien_hewan(request):
    """View untuk halaman data klien hewan"""
    with connection.cursor() as cursor:
        cursor.execute("SET search_path TO pet_clinic;")
        
        # Periksa apakah ada parameter pencarian
        search_nama = request.GET.get('search_nama', '')
        
        if search_nama:
            # Query untuk mencari berdasarkan nama dari individu
            cursor.execute("""
                SELECT k.no_identitas, k.tanggal_registrasi, k.email
                FROM klien k
                LEFT JOIN individu i ON k.no_identitas = i.no_identitas_klien
                LEFT JOIN perusahaan p ON k.no_identitas = p.no_identitas_klien
                WHERE 
                    CONCAT(i.nama_depan, ' ', COALESCE(i.nama_tengah, ''), ' ', i.nama_belakang) ILIKE %s
                    OR p.nama_perusahaan ILIKE %s
                ORDER BY k.tanggal_registrasi DESC;
            """, [f'%{search_nama}%', f'%{search_nama}%'])
        else:
            # Ambil semua klien jika tidak ada pencarian
            cursor.execute("""
                SELECT k.no_identitas, k.tanggal_registrasi, k.email
                FROM klien k
                ORDER BY k.tanggal_registrasi DESC;
            """)
        
        klien_rows = cursor.fetchall()

        klien_list = []
        for no, (no_identitas, tanggal_registrasi, email) in enumerate(klien_rows, 1):
            # Cek apakah dia individu
            cursor.execute("""
                SELECT nama_depan, nama_tengah, nama_belakang
                FROM individu
                WHERE no_identitas_klien = %s;
            """, [no_identitas])
            individu = cursor.fetchone()

            if individu:
                nama_depan, nama_tengah, nama_belakang = individu
                nama_parts = [nama_depan]
                if nama_tengah:
                    nama_parts.append(nama_tengah)
                nama_parts.append(nama_belakang)
                nama_pemilik = " ".join(nama_parts)
                jenis_pemilik = 'Individu'
            else:
                # Kalau tidak ada di individu, cek di perusahaan
                cursor.execute("""
                    SELECT nama_perusahaan
                    FROM perusahaan
                    WHERE no_identitas_klien = %s;
                """, [no_identitas])
                perusahaan = cursor.fetchone()
                if perusahaan:
                    nama_pemilik = perusahaan[0]
                    jenis_pemilik = 'Perusahaan'
                else:
                    # Kalau tidak ada di dua-duanya
                    nama_pemilik = "Tidak Diketahui"
                    jenis_pemilik = "Unknown"

            klien_list.append({
                'no': no,
                'no_identitas': no_identitas,
                'tanggal_registrasi': tanggal_registrasi,
                'email': email,
                'nama_pemilik': nama_pemilik,
                'jenis_pemilik': jenis_pemilik,
            })

    context = {
        'klien_list': klien_list,
        'search_nama': search_nama,  # Mengirim nilai pencarian ke template
    }

    return render(request, 'merah/data_klien_hewan.html', context)

def detail_client(request, no_identitas):
    """View untuk menampilkan detail client dan hewan peliharaannya"""
    with connection.cursor() as cursor:
        cursor.execute("SET search_path TO pet_clinic;")
        
        # Ambil data klien
        cursor.execute("""
            SELECT k.no_identitas, k.email
            FROM klien k
            WHERE k.no_identitas = %s;
        """, [no_identitas])
        client_data = cursor.fetchone()
        
        if not client_data:
            return HttpResponse("Client tidak ditemukan", status=404)
        
        no_identitas, email = client_data
        
        # Cek apakah klien individu atau perusahaan
        cursor.execute("""
            SELECT nama_depan, nama_tengah, nama_belakang
            FROM individu
            WHERE no_identitas_klien = %s;
        """, [no_identitas])
        individu = cursor.fetchone()
        
        cursor.execute("""
            SELECT nama_perusahaan
            FROM perusahaan
            WHERE no_identitas_klien = %s;
        """, [no_identitas])
        perusahaan = cursor.fetchone()
        
        # Ambil alamat dan nomor telepon dari tabel "USER"
        cursor.execute("""
            SELECT alamat, nomor_telepon
            FROM "USER"
            WHERE email = %s;
        """, [email])
        user_data = cursor.fetchone()
        
        alamat = user_data[0] if user_data else ""
        nomor_telepon = user_data[1] if user_data else ""
        
        # Ambil daftar hewan peliharaan
        cursor.execute("""
            SELECT h.nama, jh.nama_jenis, h.tanggal_lahir
            FROM hewan h
            JOIN jenis_hewan jh ON h.id_jenis = jh.id
            WHERE h.no_identitas_klien = %s
            ORDER BY h.tanggal_lahir DESC;
        """, [no_identitas])
        
        hewan_records = cursor.fetchall()
        hewan_list = [
            {
                'no': idx + 1,
                'nama': nama,
                'jenis': jenis,
                'tanggal_lahir': tanggal_lahir
            }
            for idx, (nama, jenis, tanggal_lahir) in enumerate(hewan_records)
        ]
        
        # Siapkan context untuk template
        context = {
            'no_identitas': no_identitas,
            'email': email,
            'alamat': alamat,
            'nomor_telepon': nomor_telepon,
            'hewan_list': hewan_list,
        }
        
        if individu:
            nama_depan, nama_tengah, nama_belakang = individu
            nama_parts = [nama_depan]
            if nama_tengah:
                nama_parts.append(nama_tengah)
            nama_parts.append(nama_belakang)
            context['nama'] = " ".join(nama_parts)
            context['jenis_klien'] = 'Individu'
        
        elif perusahaan:
            context['nama'] = perusahaan[0]
            context['jenis_klien'] = 'Perusahaan'
        
        else:
            context['nama'] = "Tidak Diketahui"
            context['jenis_klien'] = "Unknown"
        
        return render(request, 'merah/detail_client.html', context)

# DATA STOK
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

    return render(request, 'merah/data_stok_vaksin.html', context)

def create_vaccine(request):
    """View untuk menambahkan vaksin baru"""
    if request.method == 'POST':
        # Ambil data form
        nama = request.POST.get('nama')
        harga = request.POST.get('harga')
        stok_awal = request.POST.get('stokAwal')
        
        # Validasi input data
        if not all([nama, harga, stok_awal]):
            return redirect('data_stok_vaksin')

        # Masukkan data ke dalam database
        with connection.cursor() as cursor:
            cursor.execute("SET search_path TO pet_clinic;")
            cursor.execute("""
                INSERT INTO vaksin (nama, harga, stok)
                VALUES (%s, %s, %s)
            """, [nama, harga, stok_awal])

        return redirect('data_stok_vaksin')

    # Jika bukan POST, redirect ke daftar vaksin
    return redirect('data_stok_vaksin')

def add_vaccine_stock(request):
    """View untuk menambahkan stok vaksin"""
    if request.method == 'POST':
        # Get form data
        kode_vaksin = request.POST.get('kode_vaksin')
        jumlah = request.POST.get('jumlah')
        
        # Validate input data
        if not all([kode_vaksin, jumlah]):
            # Redirect back with error message
            return redirect('data_stok_vaksin')
    
        return redirect('data_stok_vaksin')
    
    return redirect('data_stok_vaksin')

def edit_vaccine(request, kode):
    """View untuk mengedit data vaksin"""
    if request.method == 'POST':
        # Get form data
        nama_vaksin = request.POST.get('nama_vaksin')
        harga = request.POST.get('harga')
        stok = request.POST.get('stok')
        
        # Validate input data
        if not all([nama_vaksin, harga, stok]):
            # Redirect back with error message
            return redirect('data_stok_vaksin')
        
        return redirect('data_stok_vaksin')
    
    # If not POST request, just redirect to the vaccine list
    return redirect('data_stok_vaksin')

def delete_vaccine(request, kode):
    """View untuk menghapus data vaksin"""
    if request.method == 'POST':
        # Perform deletion for vaccine by 'kode'
        with connection.cursor() as cursor:
            cursor.execute("SET search_path TO pet_clinic;")
            cursor.execute("DELETE FROM vaksin WHERE kode = %s", [kode])
        
        return redirect('data_stok_vaksin')
    
    # If not POST request, just redirect to the vaccine list
    return redirect('data_stok_vaksin')
