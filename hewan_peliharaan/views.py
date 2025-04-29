from django.shortcuts import render, redirect
from django.db import connection
from django.contrib import messages

# List hewan
def list_hewan(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT h.nama, k.email, jh.nama_jenis, h.tanggal_lahir, h.url_foto, h.no_identitas_klien
            FROM HEWAN h
            JOIN KLIEN k ON h.no_identitas_klien = k.no_identitas
            JOIN JENIS_HEWAN jh ON h.id_jenis = jh.id
            ORDER BY k.email ASC, jh.nama_jenis ASC, h.nama ASC
        """)
        rows = cursor.fetchall()

    hewan_list = [
        {
            'nama': row[0],
            'pemilik': row[1],
            'jenis_hewan': row[2],
            'tanggal_lahir': row[3],
            'url_foto': row[4],
            'no_identitas_klien': row[5],
        }
        for row in rows
    ]
    return render(request, 'hewan/list.html', {'hewan_list': hewan_list})

# Create hewan
def create_hewan(request):
    if request.method == 'POST':
        nama = request.POST['nama']
        no_identitas_klien = request.POST['no_identitas_klien']
        tanggal_lahir = request.POST['tanggal_lahir']
        id_jenis = request.POST['id_jenis']
        url_foto = request.POST['url_foto']

        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO HEWAN (nama, no_identitas_klien, tanggal_lahir, id_jenis, url_foto)
                VALUES (%s, %s, %s, %s, %s)
            """, [nama, no_identitas_klien, tanggal_lahir, id_jenis, url_foto])

        messages.success(request, 'Data hewan berhasil ditambahkan!')
        return redirect('list_hewan')

    # Get data klien dan jenis_hewan buat dropdown
    with connection.cursor() as cursor:
        cursor.execute('SELECT no_identitas, email FROM KLIEN')
        klien = cursor.fetchall()

        cursor.execute('SELECT id, nama_jenis FROM JENIS_HEWAN')
        jenis_hewan = cursor.fetchall()

    return render(request, 'hewan/create.html', {'klien': klien, 'jenis_hewan': jenis_hewan})

# Update hewan
def update_hewan(request, nama, no_identitas_klien):
    if request.method == 'POST':
        nama_hewan = request.POST['nama']
        tanggal_lahir = request.POST['tanggal_lahir']
        id_jenis = request.POST['id_jenis']
        url_foto = request.POST['url_foto']

        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE HEWAN
                SET tanggal_lahir=%s, id_jenis=%s, url_foto=%s
                WHERE nama=%s AND no_identitas_klien=%s
            """, [tanggal_lahir, id_jenis, url_foto, nama, no_identitas_klien])

        messages.success(request, 'Data hewan berhasil diupdate!')
        return redirect('list_hewan')

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT nama, tanggal_lahir, id_jenis, url_foto
            FROM HEWAN
            WHERE nama=%s AND no_identitas_klien=%s
        """, [nama, no_identitas_klien])
        hewan = cursor.fetchone()

        cursor.execute('SELECT id, nama_jenis FROM JENIS_HEWAN')
        jenis_hewan = cursor.fetchall()

    return render(request, 'hewan/update.html', {'hewan': hewan, 'jenis_hewan': jenis_hewan})

# Delete hewan
def delete_hewan(request, nama, no_identitas_klien):
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute("""
                DELETE FROM HEWAN
                WHERE nama=%s AND no_identitas_klien=%s
            """, [nama, no_identitas_klien])

        messages.success(request, 'Data hewan berhasil dihapus!')
        return redirect('list_hewan')

    return render(request, 'hewan/delete.html', {'nama': nama})