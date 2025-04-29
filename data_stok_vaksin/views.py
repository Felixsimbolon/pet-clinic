from django.shortcuts import redirect, render
from django.urls import reverse
from django.db import connection
from django.http import Http404
from django.contrib import messages

def index(request):
    """View untuk halaman utama aplikasi data stok vaksin"""
    # Data dummy untuk dashboard
    context = {
        'total_vaksin': 28,
        'total_stok': 75,
    }
    return render(request, 'data_stok_vaksin/index.html', context)

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

    return render(request, 'data_stok_vaksin/data_stok_vaksin.html', context)

def create_vaccine(request):
    """View untuk menambahkan vaksin baru"""
    if request.method == 'POST':
        # Ambil data form
        nama = request.POST.get('nama')
        harga = request.POST.get('harga')
        stok_awal = request.POST.get('stokAwal')
        
        # Validasi input data
        if not all([nama, harga, stok_awal]):
            return redirect('data_stok_vaksin:data_stok_vaksin')

        # Masukkan data ke dalam database
        with connection.cursor() as cursor:
            cursor.execute("SET search_path TO pet_clinic;")
            cursor.execute("""
                INSERT INTO vaksin (nama, harga, stok)
                VALUES (%s, %s, %s)
            """, [nama, harga, stok_awal])

        return redirect('data_stok_vaksin:data_stok_vaksin')

    # Jika bukan POST, redirect ke daftar vaksin
    return redirect('data_stok_vaksin:data_stok_vaksin')

def add_vaccine_stock(request):
    """View untuk menambahkan stok vaksin"""
    if request.method == 'POST':
        # Get form data
        kode_vaksin = request.POST.get('kode_vaksin')
        jumlah = request.POST.get('jumlah')
        
        # Validate input data
        if not all([kode_vaksin, jumlah]):
            # Redirect back with error message
            return redirect('data_stok_vaksin:data_stok_vaksin')
    
        return redirect('data_stok_vaksin:data_stok_vaksin')
    
    return redirect('data_stok_vaksin:data_stok_vaksin')

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
            return redirect('data_stok_vaksin:data_stok_vaksin')
        
        return redirect('data_stok_vaksin:data_stok_vaksin')
    
    # If not POST request, just redirect to the vaccine list
    return redirect('data_stok_vaksin:data_stok_vaksin')

def delete_vaccine(request, kode):
    """View untuk menghapus data vaksin"""
    if request.method == 'POST':
        # Perform deletion for vaccine by 'kode'
        with connection.cursor() as cursor:
            cursor.execute("SET search_path TO pet_clinic;")
            cursor.execute("DELETE FROM vaksin WHERE kode = %s", [kode])
        
        return redirect('data_stok_vaksin:data_stok_vaksin')
    
    # If not POST request, just redirect to the vaccine list
    return redirect('data_stok_vaksin:data_stok_vaksin')