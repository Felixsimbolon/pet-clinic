from django.shortcuts import redirect, render
from django.urls import reverse
from django.db import connection
from django.http import Http404
from django.contrib import messages

def index(request):
    """View untuk halaman utama aplikasi vaksinasi hewan"""
    context = {
        'total_vaksinasi': 0,  # Ganti dengan data sesuai kebutuhan
    }
    return render(request, 'vaksinasi_hewan/index.html', context)

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
    return render(request, 'vaksinasi_hewan/vaksinasi_hewan.html', context)

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
    
    return redirect('vaksinasi_hewan:vaksinasi_hewan')

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
    
    return redirect('vaksinasi_hewan:vaksinasi_hewan')

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
    
    return redirect('vaksinasi_hewan:vaksinasi_hewan')