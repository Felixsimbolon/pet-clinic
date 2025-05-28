from django.shortcuts import redirect, render
from django.urls import reverse
from django.db import connection, transaction
from django.http import Http404, JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
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
# udah bener
def data_stok_vaksin(request):
    """View untuk halaman data stok vaksin"""
    try:
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
                'harga_raw': row[2],  # Keep raw value for editing
                'stok': row[3],
            }
            for idx, row in enumerate(rows, 1)
        ]
    except Exception as e:
        logger.error(f"Error in data_stok_vaksin: {e}")
        messages.error(request, f'Terjadi kesalahan saat mengambil data: {str(e)}')
        stok_list = []
    
    context = {
        'stok_list': stok_list
    }
    return render(request, 'manajemen_vaksinasi/data_stok_vaksin.html', context)


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

# belom bisa HELPPPP (gak ke update stok vaksin nya)
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

# blm bener (blm keganti data vaksin nya)
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
    
# udah bener
@require_POST
def delete_vaccine(request, kode):
    """View untuk menghapus data vaksin"""
    try:
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("SET search_path TO pet_clinic;")
                
                # Check if vaccine exists
                cursor.execute("SELECT nama FROM vaksin WHERE kode = %s", [kode])
                result = cursor.fetchone()
                
                if not result:
                    messages.error(request, 'Vaksin tidak ditemukan')
                    return redirect('manajemen_vaksinasi:data_stok_vaksin')
                
                nama_vaksin = result[0]
                
                # Check if vaccine is used in any vaccinations
                cursor.execute("""
                    SELECT COUNT(*) FROM kunjungan
                    WHERE kode_vaksin = %s
                """, [kode])
                count = cursor.fetchone()[0]
                
                if count > 0:
                    messages.error(request, f'Vaksin {nama_vaksin} tidak dapat dihapus karena sedang digunakan ({count} kunjungan)')
                    return redirect('manajemen_vaksinasi:data_stok_vaksin')
                    
                # Perform deletion
                cursor.execute("DELETE FROM vaksin WHERE kode = %s", [kode])
                
                affected_rows = cursor.rowcount
                if affected_rows == 0:
                    messages.error(request, 'Gagal menghapus vaksin')
                    return redirect('manajemen_vaksinasi:data_stok_vaksin')
                
        messages.success(request, f'Vaksin {nama_vaksin} berhasil dihapus')
        logger.info(f"Vaksin berhasil dihapus: {kode}")
        
    except psycopg2.IntegrityError as e:
        logger.error(f"Integrity error in delete_vaccine: {e}")
        messages.error(request, 'Vaksin tidak dapat dihapus karena masih memiliki relasi dengan data lain')
    except Exception as e:
        logger.error(f"Error in delete_vaccine: {e}")
        messages.error(request, f'Terjadi kesalahan: {str(e)}')
        
    return redirect('manajemen_vaksinasi:data_stok_vaksin')

# VIEWS CRUD MANAJEMEN VAKSIN (dokter)
# blm bener soalnya blm filter berdasarkan klien
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

# udah bener
def vaksinasi_hewan(request):
    """View untuk halaman vaksinasi hewan"""
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

        # Ambil data stok vaksin untuk dropdown
        with connection.cursor() as cursor:
            cursor.execute("SET search_path TO pet_clinic;")
            cursor.execute("""
                SELECT kode, nama, harga, stok
                FROM vaksin
                WHERE stok > 0
                ORDER BY nama;
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

# udah bener
@require_POST
def create_vaksinasi(request):
    """View untuk membuat vaksinasi baru"""
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
                
                # Check vaksin exists dan stok
                cursor.execute("""
                    SELECT kode, nama, stok FROM vaksin WHERE kode = %s
                """, [vaksin_id])
                vaksin_result = cursor.fetchone()
                
                if not vaksin_result:
                    messages.error(request, f'Vaksin dengan kode {vaksin_id} tidak ditemukan')
                    return redirect('manajemen_vaksinasi:vaksinasi_hewan')
                
                vaksin_kode, vaksin_nama, vaksin_stok = vaksin_result
                
                if vaksin_stok <= 0:
                    messages.error(request, f'Stok vaksin {vaksin_nama} tidak mencukupi')
                    return redirect('manajemen_vaksinasi:vaksinasi_hewan')
                
                logger.info(f"Data valid - akan update kunjungan dan kurangi stok")
                
                # Update kunjungan
                cursor.execute("""
                    UPDATE kunjungan
                    SET kode_vaksin = %s
                    WHERE id_kunjungan = %s AND kode_vaksin IS NULL
                """, [vaksin_id, kunjungan_id])
                
                kunjungan_affected = cursor.rowcount
                logger.info(f"Kunjungan update affected rows: {kunjungan_affected}")
                
                if kunjungan_affected == 0:
                    messages.error(request, f'Gagal mengupdate kunjungan {kunjungan_id}')
                    return redirect('manajemen_vaksinasi:vaksinasi_hewan')
                
                cursor.execute("""
                    select stok from vaksin
                    WHERE kode = %s 
                """, [vaksin_id])
                stok_sekarang = cursor.fetchone()[0]
                # Kurangi stok vaksin
                cursor.execute("""
                    UPDATE vaksin
                    SET stok = %s
                    WHERE kode = %s AND stok > 0
                """, [stok_sekarang,vaksin_id])
                
                vaksin_affected = cursor.rowcount
                logger.info(f"Vaksin update affected rows: {vaksin_affected}")
                
                if vaksin_affected == 0:
                    messages.error(request, f'Gagal mengurangi stok vaksin {vaksin_nama}')
                    return redirect('manajemen_vaksinasi:vaksinasi_hewan')
                
                # Verify hasil
                cursor.execute("SELECT kode_vaksin FROM kunjungan WHERE id_kunjungan = %s", [kunjungan_id])
                verify_kunjungan = cursor.fetchone()[0]
                
                cursor.execute("SELECT stok FROM vaksin WHERE kode = %s", [vaksin_id])
                verify_stok = cursor.fetchone()[0]
                
                logger.info(f"Verifikasi - Vaksin di kunjungan: {verify_kunjungan}, Stok baru: {verify_stok}")
                
                if verify_kunjungan == vaksin_id:
                    messages.success(request, f'Vaksinasi berhasil dibuat untuk kunjungan {kunjungan_id} dengan vaksin {vaksin_nama}')
                    logger.info(f"Vaksinasi berhasil dibuat")
                else:
                    messages.error(request, f'Verifikasi gagal untuk kunjungan {kunjungan_id}')

    except Exception as e:
        logger.error(f"Error in create_vaksinasi: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        messages.error(request, f'Terjadi kesalahan: {str(e)}')
            
    return redirect('manajemen_vaksinasi:vaksinasi_hewan')

# udah bener
@require_POST
def update_vaksinasi(request, id_kunjungan):
    """View untuk mengupdate vaksinasi dengan debug lengkap"""
    try:
        vaksin_id = request.POST.get('vaksin_id', '').strip()
        logger.info(f"=== START UPDATE VAKSINASI ===")
        logger.info(f"ID Kunjungan: {id_kunjungan}")
        logger.info(f"Vaksin ID: {vaksin_id}")
        
        if not vaksin_id:
            messages.error(request, 'Vaksin harus dipilih')
            return redirect('manajemen_vaksinasi:vaksinasi_hewan')

        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("SET search_path TO pet_clinic;")
                
                cursor.execute("SELECT current_schema();")
                current_schema = cursor.fetchone()[0]
                logger.info(f"Current schema: {current_schema}")
                
                # Ambil vaksin lama di kunjungan
                cursor.execute("""
                    SELECT kode_vaksin FROM kunjungan WHERE id_kunjungan = %s
                """, [id_kunjungan])
                result = cursor.fetchone()
                
                if not result:
                    messages.error(request, 'Kunjungan tidak ditemukan')
                    return redirect('manajemen_vaksinasi:vaksinasi_hewan')
                
                current_vaksin = result[0]
                logger.info(f"Current vaksin di kunjungan: {current_vaksin}")

                # Jika vaksin lama dan baru sama, keluar lebih awal
                if current_vaksin == vaksin_id:
                    messages.info(request, 'Vaksin yang dipilih sama dengan yang sudah ada')
                    logger.info("Vaksin lama dan baru sama, proses update dibatalkan")
                    return redirect('manajemen_vaksinasi:vaksinasi_hewan')

                # Ambil data vaksin baru
                cursor.execute("""
                    SELECT kode, nama, stok FROM vaksin WHERE kode = %s
                """, [vaksin_id])
                vaksin_baru = cursor.fetchone()
                
                if not vaksin_baru:
                    messages.error(request, 'Vaksin tidak ditemukan')
                    return redirect('manajemen_vaksinasi:vaksinasi_hewan')
                
                vaksin_baru_kode, vaksin_baru_nama, stok_baru_sebelum = vaksin_baru
                logger.info(f"Vaksin baru - Kode: {vaksin_baru_kode}, Nama: {vaksin_baru_nama}, Stok sebelum: {stok_baru_sebelum}")
                
                if stok_baru_sebelum <= 0:
                    messages.error(request, 'Stok vaksin tidak mencukupi')
                    return redirect('manajemen_vaksinasi:vaksinasi_hewan')

                # Ambil data vaksin lama (jika ada)
                stok_lama_sebelum = None
                stok_lama_sesudah = None
                if current_vaksin:
                    cursor.execute("""
                        SELECT kode, nama, stok FROM vaksin WHERE kode = %s
                    """, [current_vaksin])
                    vaksin_lama = cursor.fetchone()
                    if vaksin_lama:
                        vaksin_lama_kode, vaksin_lama_nama, stok_lama_sebelum = vaksin_lama
                        logger.info(f"Vaksin lama - Kode: {vaksin_lama_kode}, Nama: {vaksin_lama_nama}, Stok sebelum: {stok_lama_sebelum}")

                logger.info("=== MULAI PROSES UPDATE ===")

                # Kembalikan stok vaksin lama hanya jika berbeda dengan vaksin baru
                if current_vaksin and current_vaksin != vaksin_id:
                    logger.info(f"Mengembalikan stok vaksin lama: {current_vaksin}")
                    cursor.execute("""
                        UPDATE vaksin SET stok = stok  WHERE kode = %s
                    """, [current_vaksin])
                    affected_rows = cursor.rowcount
                    logger.info(f"UPDATE vaksin lama - Affected rows: {affected_rows}")
                    
                    cursor.execute("SELECT stok FROM vaksin WHERE kode = %s", [current_vaksin])
                    stok_lama_sesudah = cursor.fetchone()[0]
                    logger.info(f"Stok vaksin lama setelah dikembalikan: {stok_lama_sesudah}")
                else:
                    # Jika vaksin lama sama dengan vaksin baru atau tidak ada vaksin lama
                    stok_lama_sesudah = stok_lama_sebelum

                # Update vaksin di kunjungan
                logger.info(f"Update kunjungan {id_kunjungan} dengan vaksin {vaksin_id}")
                cursor.execute("""
                    UPDATE kunjungan SET kode_vaksin = %s WHERE id_kunjungan = %s
                """, [vaksin_id, id_kunjungan])
                affected_rows = cursor.rowcount
                logger.info(f"UPDATE kunjungan - Affected rows: {affected_rows}")
                
                cursor.execute("SELECT kode_vaksin FROM kunjungan WHERE id_kunjungan = %s", [id_kunjungan])
                vaksin_di_kunjungan = cursor.fetchone()[0]
                logger.info(f"Vaksin di kunjungan setelah update: {vaksin_di_kunjungan}")

                # Kurangi stok vaksin baru
                logger.info(f"Mengurangi stok vaksin baru: {vaksin_id}")
                cursor.execute("""
                    UPDATE vaksin SET stok = stok  WHERE kode = %s
                """, [vaksin_id])
                affected_rows = cursor.rowcount
                logger.info(f"UPDATE vaksin baru - Affected rows: {affected_rows}")

                cursor.execute("SELECT stok FROM vaksin WHERE kode = %s", [vaksin_id])
                stok_baru_sesudah = cursor.fetchone()[0]
                logger.info(f"Stok vaksin baru setelah dikurangi: {stok_baru_sesudah}")

                # Transaction ID untuk debug
                cursor.execute("SELECT txid_current();")
                transaction_id = cursor.fetchone()[0]
                logger.info(f"Transaction ID: {transaction_id}")

                logger.info("=== SELESAI PROSES UPDATE ===")
                logger.info(f"Summary perubahan stok vaksin:")
                logger.info(f"- Vaksin lama ({current_vaksin}): {stok_lama_sebelum} -> {stok_lama_sesudah}")
                logger.info(f"- Vaksin baru ({vaksin_id}): {stok_baru_sebelum} -> {stok_baru_sesudah}")
                
        messages.success(request, f'Vaksinasi berhasil diupdate untuk kunjungan {id_kunjungan}')
        logger.info("=== END UPDATE VAKSINASI ===")

    except Exception as e:
        logger.error(f"ERROR in update_vaksinasi: {str(e)}")
        logger.error(f"Error type: {type(e)}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        messages.error(request, f'Terjadi kesalahan: {str(e)}')

    return redirect('manajemen_vaksinasi:vaksinasi_hewan')

# udah bener
@require_POST
def delete_vaksinasi(request, id_kunjungan):
    """View untuk menghapus vaksinasi"""
    try:
        logger.info(f"Delete vaksinasi - id_kunjungan: {id_kunjungan}")
        
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("SET search_path TO pet_clinic;")
                
                # Get current vaccine code
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
                
                # Return vaccine to stock
                cursor.execute("""
                    UPDATE vaksin SET stok = stok  WHERE kode = %s
                """, [current_vaksin])
                    
                # Set vaccine code to NULL
                cursor.execute("""
                    UPDATE kunjungan SET kode_vaksin = NULL WHERE id_kunjungan = %s
                """, [id_kunjungan])
                
        messages.success(request, f'Vaksinasi berhasil dihapus untuk kunjungan {id_kunjungan}')
        
    except Exception as e:
        logger.error(f"Error in delete_vaksinasi: {e}")
        messages.error(request, f'Terjadi kesalahan: {str(e)}')
            
    return redirect('manajemen_vaksinasi:vaksinasi_hewan')

def check_vaccine_deletable(request, kode):
    """AJAX view untuk mengecek apakah vaksin bisa dihapus"""
    if request.method == 'GET':
        try:
            with connection.cursor() as cursor:
                cursor.execute("SET search_path TO pet_clinic;")
                
                # Check if vaccine is used
                cursor.execute("""
                    SELECT COUNT(*) FROM kunjungan WHERE kode_vaksin = %s
                """, [kode])
                count = cursor.fetchone()[0]
                
                can_delete = count == 0
                message = "Vaksin dapat dihapus" if can_delete else "Vaksin tidak dapat dihapus karena sedang digunakan"
                
                return JsonResponse({
                    'can_delete': can_delete,
                    'message': message
                })
                
        except Exception as e:
            logger.error(f"Error in check_vaccine_deletable: {e}")
            return JsonResponse({
                'can_delete': False,
                'message': f'Terjadi kesalahan: {str(e)}'
            }, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

def vaccination_context_processor(request):
    """Context processor untuk menambahkan context vaccination"""
    return {
        'vaccination_errors': {
            'stock_insufficient': 'ERROR: Stok vaksin tidak mencukupi untuk vaksinasi.',
            'vaccine_in_use': 'ERROR: Vaksin tidak dapat dihapus dikarenakan telah digunakan untuk vaksinasi.'
        }
    }