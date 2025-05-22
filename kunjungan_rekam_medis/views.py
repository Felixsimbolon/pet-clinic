from django.shortcuts import render
from django.shortcuts import render
from django.db import connection
from django.shortcuts import render, redirect
from django.db import connection
    
from django.shortcuts import render, get_object_or_404, redirect
from django.db import connection
    
from django.shortcuts import render, redirect
from django.db import connection
from django.http import Http404

from django.shortcuts import render
from django.db import connection
from django.shortcuts import render, redirect
from django.db import connection
from django.contrib import messages
import uuid
from datetime import datetime, time



    
def daftar_kunjungan_fdo(request):
    with connection.cursor() as cursor:
        cursor.execute("SET search_path TO pet_clinic;")
        cursor.execute("""
            SELECT
                id_kunjungan,
                no_identitas_klien,
                nama_hewan,
                tipe_kunjungan,
                no_front_desk,
                no_dokter_hewan,
                no_perawat_hewan,
                timestamp_awal,
                timestamp_akhir
            FROM kunjungan
            ORDER BY timestamp_awal DESC
        """)
        kunjungan_rows = cursor.fetchall()

        # Check if 'suhu' and 'berat_badan' are null in rekam_medis for each kunjungan
        for i, row in enumerate(kunjungan_rows):
            id_kunjungan = row[0]
            cursor.execute("""
                SELECT suhu, berat_badan
                FROM kunjungan
                WHERE id_kunjungan = %s
            """, [id_kunjungan])
            rekam_medis_data = cursor.fetchone()

            # Check if both suhu and berat_badan are null
            suhu_null = rekam_medis_data[0] is None
            berat_badan_null = rekam_medis_data[1] is None

            # Add flag for modal display if both are null
            kunjungan_rows[i] = (*row, suhu_null, berat_badan_null)

    columns = ['id_kunjungan', 'no_identitas_klien', 'nama_hewan', 'tipe_kunjungan','no_front_desk','no_dokter_hewan','no_perawat_hewan', 'waktu_mulai', 'waktu_selesai', 'suhu_null', 'berat_badan_null']
    data = [dict(zip(columns, row)) for row in kunjungan_rows]

    return render(request, 'daftar_kunjungan_fdo.html', {
        'kunjungan_list': data
    })
    
def daftar_kunjungan_perawat(request):
    with connection.cursor() as cursor:
        cursor.execute("SET search_path TO pet_clinic;")
        cursor.execute("""
            SELECT
                id_kunjungan,
                no_identitas_klien,
                nama_hewan,
                tipe_kunjungan,
                timestamp_awal,
                timestamp_akhir
            FROM kunjungan
            ORDER BY timestamp_awal DESC
        """)
        kunjungan_rows = cursor.fetchall()

        # Check if 'suhu' and 'berat_badan' are null in rekam_medis for each kunjungan
        for i, row in enumerate(kunjungan_rows):
            id_kunjungan = row[0]
            cursor.execute("""
                SELECT suhu, berat_badan
                FROM kunjungan
                WHERE id_kunjungan = %s
            """, [id_kunjungan])
            rekam_medis_data = cursor.fetchone()

            # Check if both suhu and berat_badan are null
            suhu_null = rekam_medis_data[0] is None
            berat_badan_null = rekam_medis_data[1] is None

            # Add flag for modal display if both are null
            kunjungan_rows[i] = (*row, suhu_null, berat_badan_null)

    columns = ['id_kunjungan', 'no_identitas_klien', 'nama_hewan', 'tipe_kunjungan', 'waktu_mulai', 'waktu_selesai', 'suhu_null', 'berat_badan_null']
    data = [dict(zip(columns, row)) for row in kunjungan_rows]

    return render(request, 'daftar_kunjungan_perawat.html', {
        'kunjungan_list': data
    })   
    
    
    
    
def daftar_kunjungan_klien(request):
    with connection.cursor() as cursor:
        cursor.execute("SET search_path TO pet_clinic;")
        cursor.execute("""
            SELECT
                id_kunjungan,
                no_identitas_klien,
                nama_hewan,
                tipe_kunjungan,
                timestamp_awal,
                timestamp_akhir
            FROM kunjungan
            ORDER BY timestamp_awal DESC
        """)
        kunjungan_rows = cursor.fetchall()

        # Check if 'suhu' and 'berat_badan' are null in rekam_medis for each kunjungan
        for i, row in enumerate(kunjungan_rows):
            id_kunjungan = row[0]
            cursor.execute("""
                SELECT suhu, berat_badan
                FROM kunjungan
                WHERE id_kunjungan = %s
            """, [id_kunjungan])
            rekam_medis_data = cursor.fetchone()

            # Check if both suhu and berat_badan are null
            suhu_null = rekam_medis_data[0] is None
            berat_badan_null = rekam_medis_data[1] is None

            # Add flag for modal display if both are null
            kunjungan_rows[i] = (*row, suhu_null, berat_badan_null)

    columns = ['id_kunjungan', 'no_identitas_klien', 'nama_hewan', 'tipe_kunjungan', 'waktu_mulai', 'waktu_selesai', 'suhu_null', 'berat_badan_null']
    data = [dict(zip(columns, row)) for row in kunjungan_rows]

    return render(request, 'daftar_kunjungan_klien.html', {
        'kunjungan_list': data
    })
    
    
def daftar_kunjungan(request):
    with connection.cursor() as cursor:
        cursor.execute("SET search_path TO pet_clinic;")
        cursor.execute("""
            SELECT
                id_kunjungan,
                no_identitas_klien,
                nama_hewan,
                tipe_kunjungan,
                timestamp_awal,
                timestamp_akhir
            FROM kunjungan
            ORDER BY timestamp_awal DESC
        """)
        kunjungan_rows = cursor.fetchall()

        # Check if 'suhu' and 'berat_badan' are null in rekam_medis for each kunjungan
        for i, row in enumerate(kunjungan_rows):
            id_kunjungan = row[0]
            cursor.execute("""
                SELECT suhu, berat_badan
                FROM kunjungan
                WHERE id_kunjungan = %s
            """, [id_kunjungan])
            rekam_medis_data = cursor.fetchone()

            # Check if both suhu and berat_badan are null
            suhu_null = rekam_medis_data[0] is None
            berat_badan_null = rekam_medis_data[1] is None


            # Add flag for modal display if both are null
            kunjungan_rows[i] = (*row, suhu_null, berat_badan_null)

    columns = ['id_kunjungan', 'no_identitas_klien', 'nama_hewan', 'tipe_kunjungan', 'waktu_mulai', 'waktu_selesai', 'suhu_null', 'berat_badan_null']
    data = [dict(zip(columns, row)) for row in kunjungan_rows]

    return render(request, 'daftar_kunjungan.html', {
        'kunjungan_list': data
    }) 
def create_kunjungan(request):
    # Retrieve all available ID Klien and Nama Hewan from the database
    errors = {}
    with connection.cursor() as cursor:
        cursor.execute("SET search_path TO pet_clinic;")
        
        # 1) Get all ID Klien
        cursor.execute("SELECT no_identitas FROM klien ORDER BY no_identitas;")
        klien_list = [row[0] for row in cursor.fetchall()]
        
        
        
        # 2) Get all Nama Hewan for the selected ID Klien
        cursor.execute("""
            SELECT id_jenis, nama FROM hewan ORDER BY nama;
        """)
        hewan_list = []
        for row in cursor.fetchall():
            hewan_list.append({
                'id': row[0],
                'nama': row[1],
            })

        # 3) Get available metode_kunjungan options
        cursor.execute("""
            SELECT DISTINCT tipe_kunjungan FROM kunjungan ORDER BY tipe_kunjungan;
        """)
        tipe_kunjungan_list = [row[0] for row in cursor.fetchall()]

        # 4) Get all available dokter_hewan with their emails and formatted names
        cursor.execute("""
            SELECT 
                k.no_dokter_hewan,
                p.email_user,
                'dr. ' || REPLACE(SUBSTRING(p.email_user FROM 1 FOR POSITION('@' IN p.email_user) - 1), '.', ' ')
            FROM pegawai p
            JOIN dokter_hewan k ON p.no_pegawai = k.no_dokter_hewan
            ORDER BY 3;
            """)
        # Extract and format the doctor list correctly
        dokter_list = []
        for row in cursor.fetchall():
            dokter_list.append({
                'id': row[0],
                'email': row[1],
                'name': row[2]
            })

        # 5) Get all available perawat_hewan with their emails and formatted names
        cursor.execute("""
            SELECT 
                k.no_perawat_hewan,
                p.email_user,
                REPLACE(SUBSTRING(p.email_user FROM 1 FOR POSITION('@' IN p.email_user) - 1), '.', '          ')
            FROM pegawai p
            JOIN perawat_hewan k ON p.no_pegawai = k.no_perawat_hewan
            ORDER BY 3;
            """)
        # Extract and format the nurse list correctly
        perawat_list = []
        for row in cursor.fetchall():
            perawat_list.append({
                'id': row[0],
                'email': row[1],
                'name': row[2]
            })
            
        cursor.execute("""
            SELECT 
                k.no_front_desk,
                p.email_user,
                REPLACE(SUBSTRING(p.email_user FROM 1 FOR POSITION('@' IN p.email_user) - 1), '.', '          ')
            FROM pegawai p
            JOIN front_desk k ON p.no_pegawai = k.no_front_desk
            ORDER BY 3;
            """)
        # Extract and format the nurse list correctly
        front_desk_list = []
        for row in cursor.fetchall():
            front_desk_list.append({
                'id': row[0],
                'email': row[1],
                'name': row[2]
            })
        
    if request.method == "POST":
        # Get the data from form
        id_klien        = request.POST.get('id_klien', '').strip()
        nama_hewan      = request.POST.get('nama_hewan', '').strip()
        metode_kunjungan= request.POST.get('metode_kunjungan', '').strip()
        waktu_mulai_penanganan= request.POST.get('timestamp_awal', '').strip()
        waktu_selesai_penanganan = request.POST.get('timestamp_akhir', '').strip()
        dokter_email    = request.POST.get('dokter_hewan', '').strip()
        perawat_email   = request.POST.get('perawat_hewan', '').strip()
        front_desk_email= request.POST.get('front_desk', '').strip()
        print(waktu_selesai_penanganan == "")
        
        
        id_kunjungan = uuid.uuid4()

        # timestamp_awal = datetime.strptime(waktu_mulai_penanganan, "%Y-%m-%dT%H:%M:%S")
        # timestamp_akhir = datetime.strptime(waktu_selesai_penanganan, "%Y-%m-%dT%H:%M:%S")
        
        required_drop = {
            'id_klien':            id_klien,
            'nama_hewan':          nama_hewan,
            'metode_kunjungan':    metode_kunjungan,
            'dokter_hewan':        dokter_email,
            'perawat_hewan':       perawat_email,
            'front_desk':          front_desk_email,
        }

        for field, value in required_drop.items():
            if not value:                              # ''  atau None
                errors[field] = f'{field.replace("_", " ").title()} wajib dipilih'

        # ----------- VALIDASI WAKTU --------------- #
        if not waktu_mulai_penanganan:
            errors['timestamp_awal'] = 'Waktu mulai harus diisi'
        

        dt_awal = dt_akhir = None
        if 'timestamp_awal' not in errors:
            try:
                timestamp_awal = datetime.strptime(waktu_mulai_penanganan, "%Y-%m-%dT%H:%M:%S")
            except ValueError:
                errors['timestamp_awal'] = 'Format waktu mulai tidak valid'

        if 'timestamp_akhir' not in errors and waktu_selesai_penanganan != '':
            try:
                timestamp_akhir = datetime.strptime(waktu_selesai_penanganan, "%Y-%m-%dT%H:%M:%S")
            except ValueError:
                errors['timestamp_akhir'] = 'Format waktu selesai tidak valid'
                
        with connection.cursor() as cursor:
            cursor.execute("SET search_path TO pet_clinic;")
            cursor.execute("""
                SELECT 1 FROM hewan
                WHERE no_identitas_klien = %s AND nama = %s
            """, [id_klien, nama_hewan])
            cek_hewan = cursor.fetchone()

        if not cek_hewan:
            errors['nama_hewan'] = f'Hewan dengan nama "{nama_hewan}" untuk klien ini tidak ditemukan.'



        # ---------- jika ada error, render ulang form ----------
        if errors:
            return render(request, 'create_kunjungan.html', {
                'errors': errors,
                'data':   request.POST,          # supaya nilai dropdown tetap terpilih
                'klien_list':          klien_list,
                'hewan_list':          hewan_list,
                'tipe_kunjungan_list': tipe_kunjungan_list,
                'dokter_list':         dokter_list,
                'perawat_list':        perawat_list,
                'front_desk_list':     front_desk_list,
            })

        with connection.cursor() as cursor:
            cursor.execute("SET search_path TO pet_clinic;")
            def pegawai_id_by_email(email):
                cursor.execute('SELECT no_pegawai FROM pegawai WHERE email_user = %s',
                            [email])
                row = cursor.fetchone()
                return row[0] if row else None
 
            no_perawat   = pegawai_id_by_email(perawat_email)
            no_dokter    = pegawai_id_by_email(dokter_email)
            no_front_desk= pegawai_id_by_email(front_desk_email)
            if  waktu_selesai_penanganan == "":
                cursor.execute("""
                    INSERT INTO kunjungan
                        (id_kunjungan, no_identitas_klien,nama_hewan, tipe_kunjungan, timestamp_awal, no_dokter_hewan, no_perawat_hewan,no_front_desk)
                    VALUES (%s, %s, %s, %s, %s, %s, %s,%s)
                """, [id_kunjungan,id_klien, nama_hewan, metode_kunjungan, timestamp_awal, no_dokter, no_perawat,no_front_desk])
            else:
                     cursor.execute("""
                    INSERT INTO kunjungan
                        (id_kunjungan, no_identitas_klien,nama_hewan, tipe_kunjungan, timestamp_awal, timestamp_akhir, no_dokter_hewan, no_perawat_hewan,no_front_desk)
                    VALUES (%s, %s, %s, %s, %s, %s, %s,%s, %s)
                """, [id_kunjungan,id_klien, nama_hewan, metode_kunjungan, timestamp_awal, timestamp_akhir, no_dokter, no_perawat,no_front_desk])

        # Redirect after saving the kunjungan data
        return redirect('daftar_kunjungan_fdo')

    return render(request, 'create_kunjungan.html', {
        'klien_list': klien_list,
        'hewan_list': hewan_list,
        'tipe_kunjungan_list': tipe_kunjungan_list,
        'dokter_list': dokter_list,  # Pass dokter list for dropdown
        'perawat_list': perawat_list,  # Pass perawat list for dropdown
        'front_desk_list': front_desk_list,
    })


def update_kunjungan(request, id_kunjungan,no_dokter_hewan,no_perawat_hewan,no_front_desk,nama_hewan,no_identitas_klien):
    # Fetch the current Kunjungan data based on the ID
    errors = {}
    with connection.cursor() as cursor:
        cursor.execute("SET search_path TO pet_clinic;")
        
        cursor.execute("""
            SELECT email_user
            FROM kunjungan join pegawai on no_dokter_hewan = no_pegawai
            WHERE id_kunjungan = %s
            AND no_identitas_klien = %s
            AND nama_hewan = %s
            AND no_dokter_hewan = %s
            AND no_perawat_hewan = %s
            AND no_front_desk = %s
""", [id_kunjungan, no_identitas_klien, nama_hewan, no_dokter_hewan, no_perawat_hewan, no_front_desk])
        
        email_dokter_hewan = cursor.fetchone()[0]
         
        cursor.execute("""
            SELECT email_user
            FROM kunjungan join pegawai on no_perawat_hewan = no_pegawai
            WHERE id_kunjungan = %s
            AND no_identitas_klien = %s
            AND nama_hewan = %s
            AND no_dokter_hewan = %s
            AND no_perawat_hewan = %s
            AND no_front_desk = %s
""", [id_kunjungan, no_identitas_klien, nama_hewan, no_dokter_hewan, no_perawat_hewan, no_front_desk])
        
        email_perawat_hewan = cursor.fetchone()[0]

        cursor.execute("""
            SELECT email_user
            FROM kunjungan join pegawai on no_front_desk = no_pegawai
            WHERE id_kunjungan = %s
            AND no_identitas_klien = %s
            AND nama_hewan = %s
            AND no_dokter_hewan = %s
            AND no_perawat_hewan = %s
            AND no_front_desk = %s
""", [id_kunjungan, no_identitas_klien, nama_hewan, no_dokter_hewan, no_perawat_hewan, no_front_desk])
        
        email_front_desk = cursor.fetchone()[0]

        
        # Get the details for the given kunjungan
        cursor.execute("""
            SELECT no_identitas_klien, nama_hewan, tipe_kunjungan, timestamp_awal, timestamp_akhir
            FROM kunjungan
            WHERE id_kunjungan = %s
            AND no_identitas_klien = %s
            AND nama_hewan = %s
            AND no_dokter_hewan = %s
            AND no_perawat_hewan = %s
            AND no_front_desk = %s
    """, [id_kunjungan, no_identitas_klien, nama_hewan, no_dokter_hewan, no_perawat_hewan, no_front_desk])
        
        kunjungan_data = cursor.fetchone()
        current_klien = kunjungan_data[0]
        current_nama_hewan = kunjungan_data[1]
        current_tipe_kunjungan = kunjungan_data[2]
        current_waktu_mulai = kunjungan_data[3]
        current_waktu_selesai = kunjungan_data[4]
        fmt  = "%Y-%m-%dT%H:%M:%S"                   # titik dua di tengah = ISO

        current_waktu_mulai_iso = current_waktu_mulai.strftime(fmt) if current_waktu_mulai else ''
        current_waktu_selesai_iso = current_waktu_selesai.strftime(fmt) if current_waktu_selesai else ''


        # Get list of available klien, hewan, and metode kunjungan
        cursor.execute("SET search_path TO pet_clinic;")
        
        # 1) Get all ID Klien
        cursor.execute("SELECT no_identitas FROM klien ORDER BY no_identitas;")
        klien_list = [row[0] for row in cursor.fetchall()]
        
        
        
        # 2) Get all Nama Hewan for the selected ID Klien
        cursor.execute("""
            SELECT id_jenis, nama FROM hewan ORDER BY nama;
        """)
        hewan_list = []
        for row in cursor.fetchall():
            hewan_list.append({
                'id': row[0],
                'nama': row[1],
            })

        # 3) Get available metode_kunjungan options
        cursor.execute("""
            SELECT DISTINCT tipe_kunjungan FROM kunjungan ORDER BY tipe_kunjungan;
        """)
        tipe_kunjungan_list = ['Janji Temu','Walk-In','Darurat']

        # 4) Get all available dokter_hewan with their emails and formatted names
        cursor.execute("""
            SELECT 
                k.no_dokter_hewan,
                p.email_user,
                'dr. ' || REPLACE(SUBSTRING(p.email_user FROM 1 FOR POSITION('@' IN p.email_user) - 1), '.', ' ')
            FROM pegawai p
            JOIN dokter_hewan k ON p.no_pegawai = k.no_dokter_hewan
            ORDER BY 3;
            """)
        # Extract and format the doctor list correctly
        dokter_list = []
        for row in cursor.fetchall():
            dokter_list.append({
                'id': row[0],
                'email': row[1],
                'name': row[2]
            })

        # 5) Get all available perawat_hewan with their emails and formatted names
        cursor.execute("""
            SELECT 
                k.no_perawat_hewan,
                p.email_user,
                REPLACE(SUBSTRING(p.email_user FROM 1 FOR POSITION('@' IN p.email_user) - 1), '.', '          ')
            FROM pegawai p
            JOIN perawat_hewan k ON p.no_pegawai = k.no_perawat_hewan
            ORDER BY 3;
            """)
        # Extract and format the nurse list correctly
        perawat_list = []
        for row in cursor.fetchall():
            perawat_list.append({
                'id': row[0],
                'email': row[1],
                'name': row[2]
            })

        cursor.execute("""
            SELECT 
                k.no_front_desk,
                p.email_user,
                REPLACE(SUBSTRING(p.email_user FROM 1 FOR POSITION('@' IN p.email_user) - 1), '.', '          ')
            FROM pegawai p
            JOIN front_desk k ON p.no_pegawai = k.no_front_desk
            ORDER BY 3;
            """)
        # Extract and format the nurse list correctly
        front_desk_list = []
        for row in cursor.fetchall():
            front_desk_list.append({
                'id': row[0],
                'email': row[1],
                'name': row[2]
            })
            
        
    if request.method == "POST":
        # Get the data from form
        input_id_klien        = request.POST.get('id_klien', '').strip()
        input_nama_hewan      = request.POST.get('nama_hewan', '').strip()
        input_metode_kunjungan= request.POST.get('metode_kunjungan', '').strip()
        input_waktu_mulai_penanganan= request.POST.get('timestamp_awal', '').strip()
        input_waktu_selesai_penanganan = request.POST.get('timestamp_akhir', '').strip()
        input_dokter_email    = request.POST.get('dokter_hewan', '').strip()
        input_perawat_email   = request.POST.get('perawat_hewan', '').strip()
        input_front_desk_email= request.POST.get('front_desk', '').strip()

        
        # timestamp_awal = datetime.strptime(waktu_mulai_penanganan, "%Y-%m-%dT%H:%M:%S")
        # timestamp_akhir = datetime.strptime(waktu_selesai_penanganan, "%Y-%m-%dT%H:%M:%S")
        
        required_drop = {
            'id_klien':            input_id_klien,
            'nama_hewan':          input_nama_hewan,
            'metode_kunjungan':    input_metode_kunjungan,
            'dokter_hewan':        input_dokter_email,
            'perawat_hewan':       input_perawat_email,
            'front_desk':          input_front_desk_email,
        }

        for field, value in required_drop.items():
            if not value:                              # ''  atau None
                errors[field] = f'{field.replace("_", " ").title()} wajib dipilih'

        # ----------- VALIDASI WAKTU --------------- #
        if not input_waktu_mulai_penanganan:
            errors['timestamp_awal'] = 'Waktu mulai harus diisi'
        

        dt_awal = dt_akhir = None
        if 'timestamp_awal' not in errors:
            try:
                timestamp_awal = datetime.strptime(input_waktu_mulai_penanganan, "%Y-%m-%dT%H:%M:%S")
            except ValueError:
                errors['timestamp_awal'] = 'Format waktu mulai tidak valid'

        if 'timestamp_akhir' not in errors and input_waktu_selesai_penanganan != '':
            try:
                timestamp_akhir = datetime.strptime(input_waktu_selesai_penanganan, "%Y-%m-%dT%H:%M:%S")
            except ValueError:
                errors['timestamp_akhir'] = 'Format waktu selesai tidak valid'
        with connection.cursor() as cursor:
            cursor.execute("SET search_path TO pet_clinic;")
            cursor.execute("""
                SELECT 1 FROM hewan
                WHERE no_identitas_klien = %s AND nama = %s
            """, [input_id_klien, input_nama_hewan])
            cek_hewan = cursor.fetchone()

        if not cek_hewan:
            errors['nama_hewan'] = f'Hewan dengan nama "{input_nama_hewan}" untuk klien ini tidak ditemukan.'


        # ---------- jika ada error, render ulang form ----------
        if errors:
            return render(request, 'update_kunjungan.html', {
                'errors': errors,
                'id_kunjungan': id_kunjungan,
                'klien_list': klien_list,
                'hewan_list': hewan_list,
                'dokter_list': dokter_list,
                'perawat_list': perawat_list,
                'front_desk_list': front_desk_list,
                'tipe_kunjungan_list': tipe_kunjungan_list,
                'current_klien': current_klien,
                'current_nama_hewan': current_nama_hewan,
                'current_tipe_kunjungan': current_tipe_kunjungan,
                'current_waktu_mulai':   current_waktu_mulai_iso,
                'current_waktu_selesai': current_waktu_selesai_iso,
                'email_dokter_hewan' : email_dokter_hewan,
                'email_perawat_hewan' : email_perawat_hewan,
                'email_front_desk' : email_front_desk,
            })

        with connection.cursor() as cursor:
            cursor.execute("SET search_path TO pet_clinic;")

            cursor.execute("""
                SELECT no_pegawai
                FROM PEGAWAI where email_user = %s 
    """, [input_dokter_email])
             
            input_no_dokter_hewan = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT no_pegawai
                FROM PEGAWAI where email_user = %s
    """, [input_perawat_email])
            
            input_no_perawat_hewan = cursor.fetchone()[0]

            cursor.execute("""
                SELECT no_pegawai
                FROM PEGAWAI where email_user = %s              
    """, [input_front_desk_email])
            
            input_no_front_desk = cursor.fetchone()[0]
            
            if input_waktu_selesai_penanganan !="":
            
                cursor.execute("""
                    UPDATE kunjungan
                    SET no_identitas_klien = %s,
                    nama_hewan = %s,
                    tipe_kunjungan = %s,
                    timestamp_awal = %s,
                    timestamp_akhir = %s,
                    no_dokter_hewan = %s,
                    no_perawat_hewan = %s,
                    no_front_desk = %s
                    WHERE id_kunjungan = %s
                    AND no_identitas_klien = %s
                    AND nama_hewan = %s
                    AND no_dokter_hewan = %s
                    AND no_perawat_hewan = %s
                    AND no_front_desk = %s
                """, [
                    input_id_klien,
                    input_nama_hewan,
                    input_metode_kunjungan,
                    timestamp_awal,
                    timestamp_akhir,
                    input_no_dokter_hewan,
                    input_no_perawat_hewan,
                    input_no_front_desk,
                    id_kunjungan, no_identitas_klien, nama_hewan, no_dokter_hewan, no_perawat_hewan, no_front_desk
                    
                ])
            else:
                cursor.execute("""
                    UPDATE kunjungan
                    SET no_identitas_klien = %s,
                    nama_hewan = %s,
                    tipe_kunjungan = %s,
                    timestamp_awal = %s,
                    timestamp_akhir = null,
                    no_dokter_hewan = %s,
                    no_perawat_hewan = %s,
                    no_front_desk = %s
                    WHERE id_kunjungan = %s
                    AND no_identitas_klien = %s
                    AND nama_hewan = %s
                    AND no_dokter_hewan = %s
                    AND no_perawat_hewan = %s
                    AND no_front_desk = %s
                """, [
                    input_id_klien,
                    input_nama_hewan,
                    input_metode_kunjungan,
                    timestamp_awal,
                    input_no_dokter_hewan,
                    input_no_perawat_hewan,
                    input_no_front_desk,
                    id_kunjungan, no_identitas_klien, nama_hewan, no_dokter_hewan, no_perawat_hewan, no_front_desk
                    
                ])
                

        # Redirect after saving the kunjungan data
        return redirect('daftar_kunjungan_fdo')

    # Fetch the existing values to populate the form
    
    return render(request, 'update_kunjungan.html', {
        'id_kunjungan': id_kunjungan,
        'klien_list': klien_list,
        'hewan_list': hewan_list,
        'dokter_list': dokter_list,
        'perawat_list': perawat_list,
        'front_desk_list': front_desk_list,
        'tipe_kunjungan_list': tipe_kunjungan_list,
        'current_klien': current_klien,
        'current_nama_hewan': current_nama_hewan,
        'current_tipe_kunjungan': current_tipe_kunjungan,
        'current_waktu_mulai':   current_waktu_mulai_iso,
        'current_waktu_selesai': current_waktu_selesai_iso,
        'email_dokter_hewan' : email_dokter_hewan,
        'email_perawat_hewan' : email_perawat_hewan,
        'email_front_desk' : email_front_desk,
    })


def delete_kunjungan(request, id_kunjungan,no_dokter_hewan,no_perawat_hewan,no_front_desk,nama_hewan,no_identitas_klien):
    # Check if the Kunjungan exists
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute("SET search_path TO pet_clinic;")                   
            cursor.execute("""
                DELETE FROM kunjungan
                    WHERE id_kunjungan = %s
                    AND no_identitas_klien = %s
                    AND nama_hewan = %s
                    AND no_dokter_hewan = %s
                    AND no_perawat_hewan = %s
                    AND no_front_desk = %s
            """, [id_kunjungan, no_identitas_klien, nama_hewan, no_dokter_hewan, no_perawat_hewan, no_front_desk])
        return redirect('daftar_kunjungan_fdo')

    # If the method is GET, return a confirmation page or the same template
    return redirect('daftar_kunjungan_fdo')




def create_rekam_medis(request, id_kunjungan):
    # Get the relevant kunjungan data based on id_kunjungan
    with connection.cursor() as cursor:
        cursor.execute("SET search_path TO pet_clinic;")
        cursor.execute("""
            SELECT id_kunjungan, no_identitas_klien, nama_hewan
            FROM kunjungan
            WHERE id_kunjungan = %s
        """, [id_kunjungan])
        kunjungan_data = cursor.fetchone()

    if request.method == "POST":
        suhu = request.POST.get('suhu')
        berat_badan = request.POST.get('berat_badan')
        kode_perawatan = request.POST.get('jenis_perawatan')
        catatan = request.POST.get('catatan', '')

        # Insert the data into rekam_medis
        # with connection.cursor() as cursor:
        #     cursor.execute("SET search_path TO pet_clinic;")
        #     cursor.execute("""
        #         UPDATE kunjungan
        #         SET suhu = %s, berat_badan = %s
        #         WHERE id_kunjungan = %s
        #     """, [suhu, berat_badan, id_kunjungan])
        # with connection.cursor() as cursor:
        #     cursor.execute("SET search_path TO pet_clinic;")
        #     cursor.execute("""
        #         UPDATE kunjungan_keperawatan
        #         SET kode_perawatan = %s, catatan = %s
        #         WHERE id_kunjungan = %s
        #     """, [kode_perawatan,catatan, id_kunjungan])

        # rekam_medis_context = {
        #     'suhu': suhu,
        #     'berat_badan': berat_badan,
        #     'jenis_perawatan': jenis_perawatan,
        #     'catatan': catatan,
        #     'id_kunjungan': id_kunjungan
        # }

        # # Success message
        # messages.success(request, 'Rekam medis berhasil dibuat!')

        # Render the same page (view_rekam_medis) with the updated Rekam Medis data
        return render(request, 'rekam_medis_view_dummy.html')

    # Get the list of jenis perawatan
    with connection.cursor() as cursor:
        cursor.execute("SET search_path TO pet_clinic;")
        cursor.execute("""
            SELECT kode_perawatan, nama_perawatan FROM perawatan
            ORDER BY kode_perawatan
        """)
        jenis_perawatan_list = cursor.fetchall()

    return render(request, 'create_rekam_medis.html', {
        'id_kunjungan': id_kunjungan,
        'kunjungan_data': kunjungan_data,
        'jenis_perawatan_list': jenis_perawatan_list
    })



def create_rekam_medis(request, id_kunjungan):
    # Get the relevant kunjungan data based on id_kunjungan
    with connection.cursor() as cursor:
        cursor.execute("SET search_path TO pet_clinic;")
        cursor.execute("""
            SELECT id_kunjungan, no_identitas_klien, nama_hewan
            FROM kunjungan
            WHERE id_kunjungan = %s
        """, [id_kunjungan])
        kunjungan_data = cursor.fetchone()

    if request.method == "POST":
        suhu = request.POST.get('suhu')
        berat_badan = request.POST.get('berat_badan')
        kode_perawatan = request.POST.get('jenis_perawatan')
        catatan = request.POST.get('catatan', '')

        # Insert the data into rekam_medis
        # with connection.cursor() as cursor:
        #     cursor.execute("SET search_path TO pet_clinic;")
        #     cursor.execute("""
        #         UPDATE kunjungan
        #         SET suhu = %s, berat_badan = %s
        #         WHERE id_kunjungan = %s
        #     """, [suhu, berat_badan, id_kunjungan])
        # with connection.cursor() as cursor:
        #     cursor.execute("SET search_path TO pet_clinic;")
        #     cursor.execute("""
        #         UPDATE kunjungan_keperawatan
        #         SET kode_perawatan = %s, catatan = %s
        #         WHERE id_kunjungan = %s
        #     """, [kode_perawatan,catatan, id_kunjungan])

        # rekam_medis_context = {
        #     'suhu': suhu,
        #     'berat_badan': berat_badan,
        #     'jenis_perawatan': jenis_perawatan,
        #     'catatan': catatan,
        #     'id_kunjungan': id_kunjungan
        # }

        # # Success message
        # messages.success(request, 'Rekam medis berhasil dibuat!')

        # Render the same page (view_rekam_medis) with the updated Rekam Medis data
        return render(request, 'rekam_medis_view_dummy.html')

    # Get the list of jenis perawatan
    with connection.cursor() as cursor:
        cursor.execute("SET search_path TO pet_clinic;")
        cursor.execute("""
            SELECT kode_perawatan, nama_perawatan FROM perawatan
            ORDER BY kode_perawatan
        """)
        jenis_perawatan_list = cursor.fetchall()

    return render(request, 'create_rekam_medis.html', {
        'id_kunjungan': id_kunjungan,
        'kunjungan_data': kunjungan_data,
        'jenis_perawatan_list': jenis_perawatan_list
    })
def update_rekam_medis_dummy(request):
    return render(request,'update_rekam_medis_dummy.html')




def create_rekam_medis_dummy_fdo(request):
    # Get the relevant kunjungan data based on id_kunjungan

    return render(request, 'rekam_medis_view_dummy_fdo.html')

def create_rekam_medis_dummy_perawat(request):
    # Get the relevant kunjungan data based on id_kunjungan

    return render(request, 'rekam_medis_view_dummy_perawat.html')

def create_rekam_medis_dummy_klien(request):
    # Get the relevant kunjungan data based on id_kunjungan

    return render(request, 'rekam_medis_view_dummy_klien.html')

def create_rekam_medis_dummy(request):
    # Get the relevant kunjungan data based on id_kunjungan

    return render(request, 'rekam_medis_view_dummy.html')



    # Get the list of 


from django.shortcuts import render, redirect
from django.db import connection
from django.contrib import messages

def update_rekam_medis(request, id_kunjungan):
    if request.method == "POST":
        suhu = request.POST.get('suhu')
        berat_badan = request.POST.get('berat_badan')
        jenis_perawatan = request.POST.get('jenis_perawatan')
        catatan = request.POST.get('catatan', '')

        # Update the rekam medis for this kunjungan
        with connection.cursor() as cursor:
            cursor.execute("SET search_path TO pet_clinic;")
            cursor.execute("""
                UPDATE kunjungan
                SET suhu = %s, berat_badan = %s
                WHERE id_kunjungan = %s
            """, [suhu, berat_badan, id_kunjungan])
        with connection.cursor() as cursor:
            cursor.execute("SET search_path TO pet_clinic;")
            cursor.execute("""
                UPDATE kunjungan_keperawatan
                SET catatan = %s
                WHERE id_kunjungan = %s
            """, [catatan, id_kunjungan])
        
        # Redirect to view the updated rekam medis (render view instead of redirect)
        rekam_medis_context = {
            'suhu': suhu,
            'berat_badan': berat_badan,
            'jenis_perawatan': jenis_perawatan,
            'catatan': catatan,
            'id_kunjungan': id_kunjungan
        }

        # Success message
        messages.success(request, 'Rekam medis berhasil dibuat!')

        # Render the same page (view_rekam_medis) with the updated Rekam Medis data
        return render(request, 'rekam_medis_view.html', rekam_medis_context)
    # If the method is GET, fetch the current rekam medis data to populate the form
    with connection.cursor() as cursor:
        cursor.execute("SET search_path TO pet_clinic;")
        cursor.execute("""
            SELECT
                k.id_kunjungan,
                k.no_identitas_klien,
                k.nama_hewan,
                k.tipe_kunjungan,
                k.suhu,
                k.berat_badan,
                r.kode_perawatan,
                r.catatan
            FROM kunjungan k
            LEFT JOIN kunjungan_keperawatan r ON k.id_kunjungan = r.id_kunjungan
            WHERE k.id_kunjungan = %s
        """, [id_kunjungan])
        kunjungan_data = cursor.fetchone()

    # Get the list of jenis perawatan for the dropdown menu
    with connection.cursor() as cursor:
        cursor.execute("SET search_path TO pet_clinic;")
        cursor.execute("""
            SELECT kode_perawatan, nama_perawatan FROM perawatan
            ORDER BY kode_perawatan
        """)
        jenis_perawatan_list = cursor.fetchall()

    return render(request, 'update_rekam_medis.html', {
        'id_kunjungan': id_kunjungan,
        'no_identitas_klien': kunjungan_data[1],
        'nama_hewan': kunjungan_data[2],
        'tipe_kunjungan': kunjungan_data[3],
        'suhu': kunjungan_data[4],  # Suhu from rekam medis
        'berat_badan': kunjungan_data[5],  # Berat badan from rekam medis
        'jenis_perawatan': kunjungan_data[6],  # Jenis perawatan from rekam medis
        'catatan': kunjungan_data[7],  # Catatan from rekam medis
        'jenis_perawatan_list': jenis_perawatan_list
    })
    
# views.py
from django.shortcuts import render
from django.db import connection

def rekam_medis_view(request, id_kunjungan):
    with connection.cursor() as cursor:
        cursor.execute("SET search_path TO pet_clinic;")
        
        # Query to fetch suhu and berat_badan from kunjungan
        cursor.execute("""
            SELECT suhu, berat_badan
            FROM kunjungan
            WHERE id_kunjungan = %s
        """, [id_kunjungan])
        kunjungan_data = cursor.fetchone()

        # Query to fetch catatan from kunjungan_keperawatan
        cursor.execute("""
            SELECT catatan
            FROM kunjungan_keperawatan
            WHERE id_kunjungan = %s
        """, [id_kunjungan])
        catatan_data = cursor.fetchone()

    # Prepare data to pass to the template
    if kunjungan_data and catatan_data:
        suhu, berat_badan = kunjungan_data
        catatan = catatan_data[0]
    else:
        suhu = berat_badan = catatan = None  # If no data found

    return render(request, 'rekam_medis_view.html', {
        'suhu': suhu,
        'berat_badan': berat_badan,
        'catatan': catatan,
        'id_kunjungan':id_kunjungan
    })

