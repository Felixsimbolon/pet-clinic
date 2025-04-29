from django.shortcuts import redirect, render
from django.urls import reverse
from django.db import connection
from django.http import Http404, HttpResponse
from django.contrib import messages

def index(request):
    return redirect('data_klien_hewan') 

def index2(request):
    return redirect('data_klien_hewan_klien') 

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
        'search_nama': search_nama,
    }

    return render(request, 'data_klien_hewan/data_klien_hewan.html', context)

def data_klien_hewan_klien(request):
    """View untuk halaman data klien hewan ROLE KLIEN"""
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
        'search_nama': search_nama,
    }

    return render(request, 'data_klien_hewan/data_klien_hewan_klien.html', context)

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
        
        return render(request, 'data_klien_hewan/detail_client.html', context)
    
def detail_client_klien(request, no_identitas):
    """View untuk menampilkan detail client dan hewan peliharaannya ROLE KLIEN"""
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
        
        return render(request, 'data_klien_hewan/detail_client_klien.html', context)