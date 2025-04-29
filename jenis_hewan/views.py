from django.shortcuts import render, redirect
from django.db import connection
from django.contrib import messages

# List semua Jenis Hewan
def list_jenis_hewan(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, nama_jenis
            FROM JENIS_HEWAN
            ORDER BY id ASC
        """)
        rows = cursor.fetchall()

    jenis_list = [{'id': row[0], 'nama_jenis': row[1]} for row in rows]
    user_role = request.session.get('role')  # 'dokter' atau 'frontdesk'
    return render(request, 'list.html', {'jenis_list': jenis_list, 'user_role': user_role})

# Create Jenis Hewan
def create_jenis_hewan(request):
    if request.method == 'POST':
        nama_jenis = request.POST.get('nama_jenis')

        if nama_jenis:
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO JENIS_HEWAN (id, nama_jenis)
                    VALUES (gen_random_uuid(), %s)
                """, [nama_jenis])
            messages.success(request, "Jenis Hewan berhasil ditambahkan.")
            return redirect('list_jenis_hewan')

    return render(request, 'create.html')

# Update Jenis Hewan
def update_jenis_hewan(request, id):
    if request.method == 'POST':
        nama_jenis = request.POST.get('nama_jenis')
        if nama_jenis:
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE JENIS_HEWAN
                    SET nama_jenis = %s
                    WHERE id = %s
                """, [nama_jenis, id])
            messages.success(request, "Jenis Hewan berhasil diupdate.")
            return redirect('list_jenis_hewan')

    with connection.cursor() as cursor:
        cursor.execute("SELECT id, nama_jenis FROM JENIS_HEWAN WHERE id = %s", [id])
        jenis = cursor.fetchone()

    return render(request, 'update.html', {'jenis': {'id': jenis[0], 'nama_jenis': jenis[1]}})

# Delete Jenis Hewan
def delete_jenis_hewan(request, id):
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM JENIS_HEWAN WHERE id = %s", [id])
        messages.success(request, "Jenis Hewan berhasil dihapus.")
        return redirect('list_jenis_hewan')

    with connection.cursor() as cursor:
        cursor.execute("SELECT id, nama_jenis FROM JENIS_HEWAN WHERE id = %s", [id])
        jenis = cursor.fetchone()

    return render(request, 'delete.html', {'jenis': {'id': jenis[0], 'nama_jenis': jenis[1]}})