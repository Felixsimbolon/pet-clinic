import uuid
from django.db import connection
from django.shortcuts import redirect, render
from django.contrib import messages
from .forms import RegisterIndividuForm, RegisterFrontDeskForm, RegisterDokterForm, RegisterPerawatForm, RegisterPerusahaanForm

def landing_page(request):
    return render(request, 'landing.html')

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        with connection.cursor() as cursor:
            # Cek apakah email ada dan password cocok
            cursor.execute("""
                SELECT email, password
                FROM "USER"
                WHERE email = %s
            """, [email])
            user = cursor.fetchone()

            if user and user[1] == password:
                # Email dan password cocok
                # Sekarang cek role pengguna
                cursor.execute("""
                    SELECT no_dokter_hewan
                    FROM DOKTER_HEWAN
                    WHERE no_dokter_hewan = (
                        SELECT no_pegawai FROM PEGAWAI WHERE email_user = %s
                    )
                """, [email])
                dokter = cursor.fetchone()

                if dokter:
                    # Kalau dokter
                    return redirect('dashboard_dokter', id_dokter=dokter[0])

                cursor.execute("""
                    SELECT no_perawat_hewan
                    FROM PERAWAT_HEWAN
                    WHERE no_perawat_hewan = (
                        SELECT no_pegawai FROM PEGAWAI WHERE email_user = %s
                    )
                """, [email])
                perawat = cursor.fetchone()

                if perawat:
                    # Kalau perawat
                    return redirect('dashboard_perawat', id_perawat=perawat[0])

                cursor.execute("""
                    SELECT no_front_desk
                    FROM FRONT_DESK
                    WHERE no_front_desk = (
                        SELECT no_pegawai FROM PEGAWAI WHERE email_user = %s
                    )
                """, [email])
                frontdesk = cursor.fetchone()

                if frontdesk:
                    # Kalau front-desk
                    return redirect('dashboard_frontdesk', id_frontdesk=frontdesk[0])

                # Kalau bukan PEGAWAI, berarti KLIEN
                cursor.execute("""
                    SELECT no_identitas
                    FROM KLIEN
                    WHERE email = %s
                """, [email])
                klien = cursor.fetchone()

                if klien:
                    return redirect('dashboard_klien', id_klien=klien[0])

                else:
                    messages.error(request, "Akun tidak dikenali sebagai Dokter, Perawat, Frontdesk, atau Klien.")
                    return redirect('login')

            else:
                # Email/password tidak cocok
                messages.error(request, "Email atau Password salah.")
                return redirect('login')

    return render(request, 'login.html')

def register_view(request):
    return render(request, 'register.html')

def register_individu(request):
    if request.method == 'POST':
        form = RegisterIndividuForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = RegisterIndividuForm()
    return render(request, 'register_individu.html', {'form': form})

def register_perusahaan(request):
    if request.method == 'POST':
        form = RegisterPerusahaanForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = RegisterPerusahaanForm()
    return render(request, 'register_perusahaan.html', {'form': form})

def register_frontdesk(request):
    if request.method == 'POST':
        form = RegisterFrontDeskForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = RegisterFrontDeskForm()
    return render(request, 'register_frontdesk.html', {'form': form})

def register_dokter(request):
    if request.method == 'POST':
        form = RegisterDokterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = RegisterDokterForm()
    return render(request, 'register_dokter.html', {'form': form})

def register_perawat(request):
    if request.method == 'POST':
        form = RegisterPerawatForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = RegisterPerawatForm()
    return render(request, 'register_perawat.html', {'form': form})

def dashboard_dokter(request):
    # dokter_info = {}
    # daftar_sertifikat = []
    # daftar_jadwal = []

    # with connection.cursor() as cursor:
    #     # --- Ambil info dokter
    #     cursor.execute("""
    #         SELECT 
    #             dh.no_dokter_hewan,
    #             tm.no_izin_praktik, 
    #             u.email, 
    #             u.alamat, 
    #             u.nomor_telepon, 
    #             p.tanggal_mulai_kerja, 
    #             p.tanggal_akhir_kerja
    #         FROM DOKTER_HEWAN dh
    #         JOIN TENAGA_MEDIS tm ON dh.no_dokter_hewan = tm.no_tenaga_medis
    #         JOIN PEGAWAI p ON tm.no_tenaga_medis = p.no_pegawai
    #         JOIN "USER" u ON p.email_user = u.email
    #         WHERE dh.no_dokter_hewan = %s
    #     """, [str(id_dokter)])
    #     row = cursor.fetchone()
    #     if row:
    #         dokter_info = {
    #             'no_dokter_hewan': row[0],
    #             'no_izin_praktik': row[1],
    #             'email': row[2],
    #             'alamat': row[3],
    #             'nomor_telepon': row[4],
    #             'tanggal_mulai_kerja': row[5].strftime('%d %B %Y') if row[5] else '-',
    #             'tanggal_akhir_kerja': row[6].strftime('%d %B %Y') if row[6] else '-'
    #         }

    #     # --- Ambil daftar sertifikat dokter
    #     cursor.execute("""
    #         SELECT sk.no_sertifikat_kompetensi, sk.nama_sertifikat
    #         FROM SERTIFIKAT_KOMPETENSI sk
    #         WHERE sk.no_tenaga_medis = %s
    #     """, [str(id_dokter)])
    #     rows = cursor.fetchall()
    #     daftar_sertifikat = [{'nomor_sertifikat': r[0], 'nama_sertifikat': r[1]} for r in rows]

    #     # --- Ambil daftar jadwal praktik dokter
    #     cursor.execute("""
    #         SELECT hari, jam
    #         FROM JADWAL_PRAKTIK
    #         WHERE no_dokter_hewan = %s
    #         ORDER BY 
    #             CASE
    #                 WHEN lower(hari) = 'senin' THEN 1
    #                 WHEN lower(hari) = 'selasa' THEN 2
    #                 WHEN lower(hari) = 'rabu' THEN 3
    #                 WHEN lower(hari) = 'kamis' THEN 4
    #                 WHEN lower(hari) = 'jumat' THEN 5
    #                 WHEN lower(hari) = 'sabtu' THEN 6
    #                 WHEN lower(hari) = 'minggu' THEN 7
    #                 ELSE 8
    #             END, jam ASC
    #     """, [str(id_dokter)])
    #     rows = cursor.fetchall()
    #     daftar_jadwal = [{'hari': r[0], 'jam': r[1]} for r in rows]

    return render(request, 'dashboard_dokter.html')

def dashboard_perawat(request):
    # perawat_info = {}
    # daftar_sertifikat = []

    # with connection.cursor() as cursor:
    #     # --- Ambil info perawat
    #     cursor.execute("""
    #         SELECT 
    #             ph.no_perawat_hewan,
    #             tm.no_izin_praktik,
    #             u.email,
    #             u.alamat,
    #             u.nomor_telepon,
    #             p.tanggal_mulai_kerja,
    #             p.tanggal_akhir_kerja
    #         FROM PERAWAT_HEWAN ph
    #         JOIN TENAGA_MEDIS tm ON ph.no_perawat_hewan = tm.no_tenaga_medis
    #         JOIN PEGAWAI p ON tm.no_tenaga_medis = p.no_pegawai
    #         JOIN "USER" u ON p.email_user = u.email
    #         WHERE ph.no_perawat_hewan = %s
    #     """, [str(id_perawat)])
    #     row = cursor.fetchone()
    #     if row:
    #         perawat_info = {
    #             'no_perawat_hewan': row[0],
    #             'no_izin_praktik': row[1],
    #             'email': row[2],
    #             'alamat': row[3],
    #             'nomor_telepon': row[4],
    #             'tanggal_mulai_kerja': row[5].strftime('%d %B %Y') if row[5] else '-',
    #             'tanggal_akhir_kerja': row[6].strftime('%d %B %Y') if row[6] else '-'
    #         }

    #     # --- Ambil daftar sertifikat kompetensi perawat
    #     cursor.execute("""
    #         SELECT sk.no_sertifikat_kompetensi, sk.nama_sertifikat
    #         FROM SERTIFIKAT_KOMPETENSI sk
    #         WHERE sk.no_tenaga_medis = %s
    #     """, [str(id_perawat)])
    #     rows = cursor.fetchall()
    #     daftar_sertifikat = [{'nomor_sertifikat': r[0], 'nama_sertifikat': r[1]} for r in rows]

    return render(request, 'dashboard_perawat.html')

def dashboard_frontdesk(request):
    # officer_info = {}

    # with connection.cursor() as cursor:
    #     # --- Ambil info Front-Desk Officer
    #     cursor.execute("""
    #         SELECT 
    #             fd.no_front_desk,
    #             u.email,
    #             p.tanggal_mulai_kerja,
    #             p.tanggal_akhir_kerja,
    #             u.alamat,
    #             u.nomor_telepon
    #         FROM FRONT_DESK fd
    #         JOIN PEGAWAI p ON fd.no_front_desk = p.no_pegawai
    #         JOIN "USER" u ON p.email_user = u.email
    #         WHERE fd.no_front_desk = %s
    #     """, [str(id_frontdesk)])
    #     row = cursor.fetchone()
    #     if row:
    #         officer_info = {
    #             'nomor_identitas': row[0],
    #             'email': row[1],
    #             'tanggal_diterima': row[2].strftime('%d %B %Y') if row[2] else '-',
    #             'tanggal_akhir_kerja': row[3].strftime('%d %B %Y') if row[3] else '-',
    #             'alamat': row[4],
    #             'nomor_telepon': row[5],
    #         }

    return render(request, 'dashboard_frontdesk.html')

def dashboard_klien(request):
    # klien_info = {}

    # with connection.cursor() as cursor:
    #     # Cek apakah dia Individu atau Perusahaan
    #     cursor.execute("""
    #         SELECT 
    #             k.no_identitas,
    #             u.email,
    #             k.tanggal_registrasi,
    #             u.alamat,
    #             u.nomor_telepon,
    #             i.nama_depan,
    #             i.nama_tengah,
    #             i.nama_belakang,
    #             p.nama_perusahaan
    #         FROM KLIEN k
    #         JOIN "USER" u ON k.email = u.email
    #         LEFT JOIN INDIVIDU i ON k.no_identitas = i.no_identitas_klien
    #         LEFT JOIN PERUSAHAAN p ON k.no_identitas = p.no_identitas_klien
    #         WHERE k.no_identitas = %s
    #     """, [str(id_klien)])
        
    #     row = cursor.fetchone()
    #     if row:
    #         nama = ""
    #         if row[5]:  # Ada nama_depan => Individu
    #             nama_parts = [row[5]]  # nama_depan
    #             if row[6]:  # nama_tengah
    #                 nama_parts.append(row[6])
    #             nama_parts.append(row[7])  # nama_belakang
    #             nama = " ".join(nama_parts)
    #         elif row[8]:  # Ada nama_perusahaan
    #             nama = row[8]
    #         else:
    #             nama = "-"

    #         klien_info = {
    #             'nomor_identitas': row[0],
    #             'email': row[1],
    #             'tanggal_pendaftaran': row[2].strftime('%d %B %Y') if row[2] else '-',
    #             'alamat': row[3],
    #             'nomor_telepon': row[4],
    #             'nama': nama,
    #         }

    return render(request, 'dashboard_klien.html')

def update_password(request):
    return render(request, 'update_password.html')
def update_profile(request):
    return render(request, 'update_profile.html')
