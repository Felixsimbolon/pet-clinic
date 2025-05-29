from django.shortcuts import redirect, render
from django.urls import reverse
from django.db import connection, transaction
from django.http import Http404, JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
import psycopg2
import logging

# Setup logging
logger = logging.getLogger(__name__)

def index(request):
    """Redirect langsung ke halaman vaksinasi hewan"""
    return redirect('manajemen_vaksinasi:vaksinasi_hewan')

def index2(request):
    """Redirect langsung ke halaman vaksinasi hewan klien side"""
    return redirect('manajemen_vaksinasi:vaksinasi_hewan_klien')

# VIEWS CRUD data dan stok vaksin (perawat)
# udh bener
@require_GET
def check_vaccine_usage(request, kode):
    """API endpoint untuk mengecek apakah vaksin sedang digunakan"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SET search_path TO pet_clinic;")
            
            # Cek apakah vaksin exists
            cursor.execute("SELECT nama, stok FROM vaksin WHERE kode = %s", [kode])
            vaccine_result = cursor.fetchone()
            
            if not vaccine_result:
                return JsonResponse({
                    'success': False,
                    'error': 'Vaksin tidak ditemukan'
                }, status=404)
            
            nama_vaksin, stok = vaccine_result
            
            # Hitung penggunaan vaksin
            cursor.execute("""
                SELECT COUNT(*) FROM kunjungan 
                WHERE kode_vaksin = %s
            """, [kode])
            usage_count = cursor.fetchone()[0]
            
            return JsonResponse({
                'success': True,
                'vaccine_code': kode,
                'vaccine_name': nama_vaksin,
                'stock': stok,
                'usage_count': usage_count,
                'can_delete': usage_count == 0
            })
            
    except Exception as e:
        logger.error(f"Error in check_vaccine_usage: {e}")
        return JsonResponse({
            'success': False,
            'error': f'Terjadi kesalahan: {str(e)}'
        }, status=500)

# udah bener
def data_stok_vaksin(request):
    """View untuk halaman data stok vaksin dengan pencarian"""
    # untuk role PERAWAT
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
    keyword = request.GET.get('q', '').strip().lower()

    try:
        with connection.cursor() as cursor:
            cursor.execute("SET search_path TO pet_clinic;")
            if keyword:
                cursor.execute("""
                    SELECT kode, nama, harga, stok
                    FROM vaksin
                    WHERE LOWER(kode) LIKE %s OR LOWER(nama) LIKE %s
                    ORDER BY kode;
                """, [f"%{keyword}%", f"%{keyword}%"])
            else:
                cursor.execute("""
                    SELECT kode, nama, harga, stok
                    FROM vaksin
                    ORDER BY kode;
                """)

            rows = cursor.fetchall()

        stok_list = [
            {
                'kode': row[0],
                'nama': row[1],
                'harga': f"Rp{row[2]:,.0f}".replace(',', '.'),
                'harga_raw': row[2], 
                'stok': row[3],
            }
            for row in rows
        ]
    except Exception as e:
        logger.error(f"Error in data_stok_vaksin: {e}")
        messages.error(request, f'Terjadi kesalahan: {str(e)}')
        stok_list = []

    return render(request, 'manajemen_vaksinasi/data_stok_vaksin.html', {
        'stok_list': stok_list,
        'query': keyword
    })


# udah bener
@require_POST
def create_vaccine(request):
    """View untuk menambahkan vaksin baru - AUTO GENERATE KODE"""
    try:
        # Ambil data form
        nama = request.POST.get('nama', '').strip()
        harga = request.POST.get('harga', '').strip()
        stok_awal = request.POST.get('stokAwal', '').strip()
        
        logger.info(f"=== CREATE VACCINE DEBUG ===")
        logger.info(f"POST data: {dict(request.POST)}")
        logger.info(f"Nama: '{nama}', Harga: '{harga}', Stok: '{stok_awal}'")
        
        # Validasi input
        if not all([nama, harga, stok_awal]):
            messages.error(request, 'Semua field harus diisi')
            return redirect('manajemen_vaksinasi:data_stok_vaksin')
        
        try:
            harga_int = int(harga)
            stok_int = int(stok_awal)

            if harga_int < 0 or stok_int < 0:
                messages.error(request, 'Harga dan stok tidak boleh negatif')
                return redirect('manajemen_vaksinasi:data_stok_vaksin')
        except ValueError:
            messages.error(request, 'Format harga atau stok tidak valid')
            return redirect('manajemen_vaksinasi:data_stok_vaksin')
        
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("SET search_path TO pet_clinic;")
                
                # Cek duplikasi nama
                cursor.execute("SELECT COUNT(*) FROM vaksin WHERE LOWER(nama) = LOWER(%s)", [nama])
                if cursor.fetchone()[0] > 0:
                    messages.error(request, f'Vaksin dengan nama "{nama}" sudah ada')
                    return redirect('manajemen_vaksinasi:data_stok_vaksin')
                
                # Ambil kode terakhir
                cursor.execute("""
                    SELECT kode FROM vaksin
                    WHERE kode ~ '^VKS[0-9]{3}$'
                    ORDER BY kode DESC
                    LIMIT 1
                """)
                last_kode_row = cursor.fetchone()
                if last_kode_row:
                    last_kode = last_kode_row[0]  # e.g., 'VKS009'
                    last_number = int(last_kode[3:])  # Ambil angka: 9
                    new_number = last_number + 1
                else:
                    new_number = 1  # Kalau belum ada, mulai dari 1
                
                new_kode = f"VKS{new_number:03d}"  # Format jadi VKS001, VKS002, ...
                
                # Simpan ke DB
                cursor.execute("""
                    INSERT INTO vaksin (kode, nama, harga, stok)
                    VALUES (%s, %s, %s, %s)
                """, [new_kode, nama, harga_int, stok_int])
                
                if cursor.rowcount == 0:
                    raise Exception("Insert failed - no rows affected")
                
                logger.info(f"Insert successful: {new_kode} - {nama}")
        
        messages.success(request, f'Vaksin "{nama}" berhasil ditambahkan dengan kode {new_kode} dan stok {stok_int}')
        
    except Exception as e:
        logger.error(f"Unexpected error in create_vaccine: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        messages.error(request, f'Terjadi kesalahan sistem: {str(e)}')
        
    return redirect('manajemen_vaksinasi:data_stok_vaksin')

# udh bener
@require_POST
def add_vaccine_stock(request,kode):
    """View untuk memperbarui stok vaksin dengan nilai baru"""
    
    print(kode+"jembut")
    
    try:
        kode_vaksin = request.POST.get('kode_vaksin', '').strip()
        stok_baru = request.POST.get('stok', '').strip()
        
        if not kode_vaksin or not stok_baru:
            messages.error(request, 'Kode vaksin dan stok harus diisi')
            return redirect('manajemen_vaksinasi:data_stok_vaksin')
        
        try:
            stok_baru_int = int(stok_baru)
            if stok_baru_int < 0:
                messages.error(request, 'Stok tidak boleh negatif')
                return redirect('manajemen_vaksinasi:data_stok_vaksin')
        except ValueError:
            messages.error(request, 'Jumlah stok harus berupa angka valid')
            return redirect('manajemen_vaksinasi:data_stok_vaksin')
        
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("SET search_path TO pet_clinic;")
                
                # Check if vaccine exists
                cursor.execute("SELECT nama, stok FROM vaksin WHERE kode = %s", [kode_vaksin])
                row = cursor.fetchone()
                
                if not row:
                    messages.error(request, f'Vaksin dengan kode "{kode_vaksin}" tidak ditemukan')
                    return redirect('manajemen_vaksinasi:data_stok_vaksin')
                
                nama_vaksin, stok_lama = row
                
                # Update stock
                cursor.execute("UPDATE vaksin SET stok = %s WHERE kode = %s", [stok_baru_int, kode_vaksin])
                
                if cursor.rowcount == 0:
                    messages.error(request, 'Gagal memperbarui stok vaksin')
                    return redirect('manajemen_vaksinasi:data_stok_vaksin')
                
                messages.success(request, f'Stok vaksin "{nama_vaksin}" berhasil diperbarui dari {stok_lama} menjadi {stok_baru_int}')
                
    except Exception as e:
        logger.error(f"Error in add_vaccine_stock: {e}")
        messages.error(request, 'Terjadi kesalahan sistem')
    
    return redirect('manajemen_vaksinasi:data_stok_vaksin')

# udh bener
@require_POST  
def edit_vaccine(request, kode):
    """View untuk mengedit data vaksin"""
    print(f"Kode vaksin yang diterima: {kode}")
    try:
        nama_vaksin = request.POST.get('nama_vaksin', '').strip()
        harga = request.POST.get('harga', '').strip()
        
        if not nama_vaksin or not harga:
            messages.error(request, 'Nama vaksin dan harga harus diisi')
            return redirect('manajemen_vaksinasi:data_stok_vaksin')
            
        try:
            harga_float = float(harga)
            if harga_float < 0:
                messages.error(request, 'Harga tidak boleh negatif')
                return redirect('manajemen_vaksinasi:data_stok_vaksin')
        except ValueError:
            messages.error(request, 'Format harga tidak valid')
            return redirect('manajemen_vaksinasi:data_stok_vaksin')
        
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("SET search_path TO pet_clinic;")
                
                # Check if vaccine exists
                cursor.execute("SELECT nama FROM vaksin WHERE kode = %s", [kode])
                if not cursor.fetchone():
                    messages.error(request, f'Vaksin dengan kode "{kode}" tidak ditemukan')
                    return redirect('manajemen_vaksinasi:data_stok_vaksin')
                
                # Check for duplicate name (excluding current record)
                cursor.execute("""
                    SELECT COUNT(*) FROM vaksin 
                    WHERE LOWER(TRIM(nama)) = LOWER(TRIM(%s)) AND kode != %s
                """, [nama_vaksin, kode])
                
                if cursor.fetchone()[0] > 0:
                    messages.error(request, f'Nama vaksin "{nama_vaksin}" sudah digunakan')
                    return redirect('manajemen_vaksinasi:data_stok_vaksin')
                
                # Update vaccine data
                cursor.execute("""
                    UPDATE vaksin SET nama = %s, harga = %s WHERE kode = %s
                """, [nama_vaksin, harga_float, kode])
                
                if cursor.rowcount == 0:
                    messages.error(request, 'Gagal memperbarui data vaksin')
                    return redirect('manajemen_vaksinasi:data_stok_vaksin')
                
                messages.success(request, f'Data vaksin "{nama_vaksin}" berhasil diperbarui')
                
    except Exception as e:
        logger.error(f"Error in edit_vaccine: {e}")
        messages.error(request, 'Terjadi kesalahan sistem')
    
    return redirect('manajemen_vaksinasi:data_stok_vaksin')

@require_POST
def delete_vaccine(request, kode):
    """View untuk menghapus data vaksin dengan trigger database"""
    try:
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("SET search_path TO pet_clinic;")
                
                # Check if vaccine exists dan ambil nama untuk pesan
                cursor.execute("SELECT nama FROM vaksin WHERE kode = %s", [kode])
                result = cursor.fetchone()
                
                if not result:
                    messages.error(request, 'Vaksin tidak ditemukan')
                    return redirect('manajemen_vaksinasi:data_stok_vaksin')
                
                nama_vaksin = result[0]
                
                # Trigger database akan otomatis mengecek penggunaan vaksin
                # dan memberikan error jika vaksin sedang digunakan
                cursor.execute("DELETE FROM vaksin WHERE kode = %s", [kode])
                
                affected_rows = cursor.rowcount
                if affected_rows == 0:
                    messages.error(request, 'Gagal menghapus vaksin')
                    return redirect('manajemen_vaksinasi:data_stok_vaksin')
                
                messages.success(request, f'Vaksin {nama_vaksin} berhasil dihapus')
                logger.info(f"Vaksin berhasil dihapus: {kode}")
                
    except psycopg2.IntegrityError as e:
        logger.error(f"Integrity error in delete_vaccine: {e}")
        error_message = str(e)
        
        # Cek apakah error dari trigger kita
        if "telah digunakan untuk vaksinasi" in error_message:
            messages.error(request, 'Vaksin tidak dapat dihapus dikarenakan telah digunakan untuk vaksinasi')
        else:
            messages.error(request, 'Vaksin tidak dapat dihapus karena masih memiliki relasi dengan data lain')
            
    except Exception as e:
        logger.error(f"Error in delete_vaccine: {e}")
        error_message = str(e)
        
        # Cek apakah error dari trigger kita
        if "telah digunakan untuk vaksinasi" in error_message:
            messages.error(request, 'Vaksin tidak dapat dihapus dikarenakan telah digunakan untuk vaksinasi')
        else:
            messages.error(request, f'Terjadi kesalahan: {error_message}')
    
    return redirect('manajemen_vaksinasi:data_stok_vaksin')

# VIEWS CRUD MANAJEMEN VAKSIN (dokter)
# udh bener
def vaksinasi_hewan_klien(request):
    """View untuk halaman vaksinasi hewan klien side"""
    # untuk role KLIEN
    if 'user_email' not in request.session:
        return redirect('login')

    user_email = request.session['user_email']

    with connection.cursor() as cursor:
        # Cari no_pegawai dari email
        cursor.execute("SET SEARCH_PATH TO PET_CLINIC;")

        cursor.execute("SELECT no_identitas FROM klien WHERE email = %s", [user_email])
        result = cursor.fetchone()
        if not result:
            # Email tidak ditemukan di pegawai
            return redirect('login')
        
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
        order by k.id_kunjungan
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
    
    try:
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
    except Exception as e:
        logger.error(f"Error in vaksinasi_hewan_klien: {e}")
        messages.error(request, f'Terjadi kesalahan saat mengambil data: {str(e)}')
        vaksinasi_list = []
        pet_list = []
        vaksin_list = []
    
    context = {
        'vaksinasi_list': vaksinasi_list,
        'pet_list': pet_list,
        'vaksin_list': vaksin_list
    }
    
    return render(request, 'manajemen_vaksinasi/vaksinasi_hewan_klien.html', context)

# udh bener
def vaksinasi_hewan(request):
    """View untuk halaman vaksinasi hewan - menampilkan semua vaksin terlepas dari stok"""
    # untuk role dokter
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
        
    try:
        # Ambil data kunjungan vaksinasi hewan dari database
        with connection.cursor() as cursor:
            cursor.execute("SET search_path TO pet_clinic;")
            cursor.execute("""
                SELECT k.id_kunjungan, k.nama_hewan, k.no_identitas_klien, k.kode_vaksin,
                       k.tipe_kunjungan, k.timestamp_awal, k.timestamp_akhir, v.nama as nama_vaksin
                FROM kunjungan k
                LEFT JOIN vaksin v ON k.kode_vaksin = v.kode
                WHERE k.kode_vaksin IS NOT NULL
                ORDER BY k.timestamp_awal DESC, k.id_kunjungan DESC;
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

        # UPDATED: Ambil SEMUA vaksin tanpa filter stok (menampilkan semua termasuk stok 0)
        with connection.cursor() as cursor:
            cursor.execute("SET search_path TO pet_clinic;")
            cursor.execute("""
                SELECT kode, nama, harga, stok
                FROM vaksin
                ORDER BY nama;
            """)
            vaksin_rows = cursor.fetchall()
            
            stok_vaksin = [
                {
                    'kode': row[0],
                    'nama': row[1],
                    'harga': row[2],
                    'stok': row[3],
                    'display_text': f"{row[1]} (Stok: {row[3]})" + (" - HABIS" if row[3] == 0 else "")
                }
                for row in vaksin_rows
            ]

        # Ambil data kunjungan untuk dropdown (yang belum ada vaksinnya)
        with connection.cursor() as cursor:
            cursor.execute("SET search_path TO pet_clinic;")
            cursor.execute("""
                SELECT id_kunjungan, nama_hewan, no_identitas_klien, timestamp_awal
                FROM kunjungan
                WHERE kode_vaksin IS NULL
                ORDER BY timestamp_awal DESC;
            """)
            kunjungan_rows = cursor.fetchall()
            
            kunjungan_list = [
                {
                    'id_kunjungan': row[0],
                    'nama_hewan': row[1],
                    'no_identitas_klien': row[2],
                    'timestamp_awal': row[3],
                }
                for row in kunjungan_rows
            ]

    except Exception as e:
        logger.error(f"Error in vaksinasi_hewan: {e}")
        messages.error(request, f'Terjadi kesalahan saat mengambil data: {str(e)}')
        vaksinasi_list = []
        stok_vaksin = []
        kunjungan_list = []

    context = {
        'vaksinasi_list': vaksinasi_list,
        'stok_vaksin': stok_vaksin,
        'kunjungan_list': kunjungan_list
    }
    
    return render(request, 'manajemen_vaksinasi/vaksinasi_hewan.html', context)

@require_POST
def create_vaksinasi(request):
    """View untuk membuat vaksinasi baru - disederhanakan karena trigger mengelola stok"""
    try:
        # Ambil data dari form
        kunjungan_id = request.POST.get('kunjungan_id', '').strip()
        vaksin_id = request.POST.get('vaksin_id', '').strip()
        
        logger.info(f"=== CREATE VAKSINASI ===")
        logger.info(f"Kunjungan ID: {kunjungan_id}")
        logger.info(f"Vaksin ID: {vaksin_id}")
        
        if not all([kunjungan_id, vaksin_id]):
            messages.error(request, 'Semua field harus diisi')
            return redirect('manajemen_vaksinasi:vaksinasi_hewan')

        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("SET search_path TO pet_clinic;")
                
                # Check kunjungan exists dan belum ada vaksin
                cursor.execute("""
                    SELECT id_kunjungan, nama_hewan, kode_vaksin
                    FROM kunjungan 
                    WHERE id_kunjungan = %s
                """, [kunjungan_id])
                kunjungan_result = cursor.fetchone()
                
                if not kunjungan_result:
                    messages.error(request, f'Kunjungan dengan ID {kunjungan_id} tidak ditemukan')
                    return redirect('manajemen_vaksinasi:vaksinasi_hewan')
                
                id_kunjungan, nama_hewan, current_vaksin = kunjungan_result
                
                if current_vaksin is not None:
                    messages.error(request, f'Kunjungan {kunjungan_id} sudah memiliki vaksinasi')
                    return redirect('manajemen_vaksinasi:vaksinasi_hewan')
                
                cursor.execute("""
                    UPDATE kunjungan
                    SET kode_vaksin = %s
                    WHERE id_kunjungan = %s AND kode_vaksin IS NULL
                """, [vaksin_id, kunjungan_id])
                
                affected_rows = cursor.rowcount
                if affected_rows == 0:
                    messages.error(request, f'Gagal mengupdate kunjungan {kunjungan_id}')
                    return redirect('manajemen_vaksinasi:vaksinasi_hewan')
                
                # Ambil nama vaksin untuk pesan sukses
                cursor.execute("SELECT nama FROM vaksin WHERE kode = %s", [vaksin_id])
                vaksin_nama = cursor.fetchone()[0]
                
                messages.success(request, f'Vaksinasi berhasil dibuat untuk kunjungan {kunjungan_id} dengan vaksin {vaksin_nama}')
                logger.info(f"Vaksinasi berhasil dibuat")

    except Exception as e:
        logger.error(f"Error in create_vaksinasi: {e}")
        error_message = str(e)
        
        # Cek apakah error dari trigger kita
        if "tidak mencukupi untuk vaksinasi" in error_message:
            # Extract vaccine name from error message
            start = error_message.find('"') + 1
            end = error_message.find('"', start)
            vaccine_name = error_message[start:end] if start > 0 and end > start else "vaksin"
            messages.error(request, f'Stok vaksin {vaccine_name} tidak mencukupi untuk vaksinasi')
        else:
            messages.error(request, f'Terjadi kesalahan: {error_message}')
            
    return redirect('manajemen_vaksinasi:vaksinasi_hewan')

@require_POST  
def update_vaksinasi(request, id_kunjungan):
    """View untuk mengupdate vaksinasi - disederhanakan karena trigger mengelola stok"""
    try:
        vaksin_id = request.POST.get('vaksin_id', '').strip()
        logger.info(f"=== UPDATE VAKSINASI ===")
        logger.info(f"ID Kunjungan: {id_kunjungan}")
        logger.info(f"Vaksin ID: {vaksin_id}")
        
        if not vaksin_id:
            messages.error(request, 'Vaksin harus dipilih')
            return redirect('manajemen_vaksinasi:vaksinasi_hewan')

        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("SET search_path TO pet_clinic;")
                
                # Ambil vaksin lama
                cursor.execute("""
                    SELECT kode_vaksin FROM kunjungan WHERE id_kunjungan = %s
                """, [id_kunjungan])
                result = cursor.fetchone()
                
                if not result:
                    messages.error(request, 'Kunjungan tidak ditemukan')
                    return redirect('manajemen_vaksinasi:vaksinasi_hewan')
                
                current_vaksin = result[0]
                
                # Jika vaksin sama, tidak perlu update
                if current_vaksin == vaksin_id:
                    messages.info(request, 'Vaksin yang dipilih sama dengan yang sudah ada')
                    return redirect('manajemen_vaksinasi:vaksinasi_hewan')
                
                cursor.execute("""
                    UPDATE kunjungan SET kode_vaksin = %s WHERE id_kunjungan = %s
                """, [vaksin_id, id_kunjungan])
                
                messages.success(request, f'Vaksinasi berhasil diupdate untuk kunjungan {id_kunjungan}')
                logger.info("Update vaksinasi berhasil")

    except Exception as e:
        logger.error(f"Error in update_vaksinasi: {e}")
        error_message = str(e)
        
        # Cek apakah error dari trigger kita
        if "tidak mencukupi untuk vaksinasi" in error_message:
            # Extract vaccine name from error message
            start = error_message.find('"') + 1
            end = error_message.find('"', start)
            vaccine_name = error_message[start:end] if start > 0 and end > start else "vaksin"
            messages.error(request, f'Stok vaksin {vaccine_name} tidak mencukupi untuk vaksinasi')
        else:
            messages.error(request, f'Terjadi kesalahan: {error_message}')

    return redirect('manajemen_vaksinasi:vaksinasi_hewan')

# udah bener
@require_POST
def delete_vaksinasi(request, id_kunjungan):
    """View untuk menghapus vaksinasi - disederhanakan karena trigger mengelola stok"""
    try:
        logger.info(f"Delete vaksinasi - id_kunjungan: {id_kunjungan}")
        
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("SET search_path TO pet_clinic;")
                
                # Cek apakah kunjungan ada dan memiliki vaksinasi
                cursor.execute("""
                    SELECT kode_vaksin FROM kunjungan WHERE id_kunjungan = %s
                """, [id_kunjungan])
                result = cursor.fetchone()
                
                if not result:
                    messages.error(request, 'Kunjungan tidak ditemukan')
                    return redirect('manajemen_vaksinasi:vaksinasi_hewan')
                    
                current_vaksin = result[0]
                
                if not current_vaksin:
                    messages.error(request, 'Kunjungan tidak memiliki vaksinasi')
                    return redirect('manajemen_vaksinasi:vaksinasi_hewan')
                
                # Trigger database akan otomatis mengembalikan stok vaksin
                cursor.execute("""
                    UPDATE kunjungan SET kode_vaksin = NULL WHERE id_kunjungan = %s
                """, [id_kunjungan])
                
        messages.success(request, f'Vaksinasi berhasil dihapus untuk kunjungan {id_kunjungan}')
        
    except Exception as e:
        logger.error(f"Error in delete_vaksinasi: {e}")
        messages.error(request, f'Terjadi kesalahan: {str(e)}')
            
    return redirect('manajemen_vaksinasi:vaksinasi_hewan')