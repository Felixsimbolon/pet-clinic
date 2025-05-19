import datetime
import uuid
from django import forms
from django.db import connection

# Form Klien Individu
class RegisterIndividuForm(forms.Form):
    email = forms.EmailField()
    alamat = forms.CharField(widget=forms.Textarea)
    nomor_telepon = forms.CharField(max_length=15)
    nama_depan = forms.CharField(max_length=50)
    nama_tengah = forms.CharField(max_length=50, required=False)
    nama_belakang = forms.CharField(max_length=50)

    def save(self):
        email = self.cleaned_data['email']
        alamat = self.cleaned_data['alamat']
        nomor_telepon = self.cleaned_data['nomor_telepon']
        nama_depan = self.cleaned_data['nama_depan']
        nama_tengah = self.cleaned_data['nama_tengah']
        nama_belakang = self.cleaned_data['nama_belakang']

        tanggal_registrasi = datetime.date.today()  # << otomatis hari ini

        id_klien = uuid.uuid4()

        with connection.cursor() as cursor:
            # Insert USER
            cursor.execute("""
                INSERT INTO "USER" (email, password, alamat, nomor_telepon)
                VALUES (%s, %s, %s, %s)
            """, [email, 'defaultpassword', alamat, nomor_telepon])

            # Insert KLIEN
            cursor.execute("""
                INSERT INTO KLIEN (no_identitas, tanggal_registrasi, email)
                VALUES (%s, %s, %s)
            """, [str(id_klien), tanggal_registrasi, email])

            # Insert INDIVIDU
            cursor.execute("""
                INSERT INTO INDIVIDU (no_identitas_klien, nama_depan, nama_tengah, nama_belakang)
                VALUES (%s, %s, %s, %s)
            """, [str(id_klien), nama_depan, nama_tengah, nama_belakang])

# Form Klien Perusahaan
class RegisterPerusahaanForm(forms.Form):
    nama = forms.CharField(
        label="Nama Lengkap",
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nama Lengkap',
            'id': 'nama',
            'required': True
        })
    )
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email',
            'id': 'email',
            'required': True
        })
    )
    nomor_telepon = forms.CharField(
        label="Nomor Telepon",
        max_length=15,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contoh: 081234567890',
            'id': 'nomor_telepon',
            'required': True
        })
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password',
            'id': 'password',
            'required': True
        })
    )

    def save(self):
        email = self.cleaned_data['email']
        alamat = self.cleaned_data['alamat']
        nomor_telepon = self.cleaned_data['nomor_telepon']
        nama_perusahaan = self.cleaned_data['nama_perusahaan']

        tanggal_registrasi = datetime.date.today()  # << otomatis hari ini

        id_klien = uuid.uuid4()

        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO "USER" (email, password, alamat, nomor_telepon)
                VALUES (%s, %s, %s, %s)
            """, [email, 'defaultpassword', alamat, nomor_telepon])

            cursor.execute("""
                INSERT INTO KLIEN (no_identitas, tanggal_registrasi, email)
                VALUES (%s, %s, %s)
            """, [str(id_klien), tanggal_registrasi, email])

            cursor.execute("""
                INSERT INTO PERUSAHAAN (no_identitas_klien, nama_perusahaan)
                VALUES (%s, %s)
            """, [str(id_klien), nama_perusahaan])

# Form Front-Desk Officer
class RegisterFrontDeskForm(forms.Form):
    email = forms.EmailField()
    alamat = forms.CharField(widget=forms.Textarea)
    nomor_telepon = forms.CharField(max_length=15)
    tanggal_mulai_kerja = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    def save(self):
        email = self.cleaned_data['email']
        alamat = self.cleaned_data['alamat']
        nomor_telepon = self.cleaned_data['nomor_telepon']
        tanggal_mulai_kerja = self.cleaned_data['tanggal_mulai_kerja']

        id_pegawai = uuid.uuid4()

        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO "USER" (email, password, alamat, nomor_telepon)
                VALUES (%s, %s, %s, %s)
            """, [email, 'defaultpassword', alamat, nomor_telepon])

            cursor.execute("""
                INSERT INTO PEGAWAI (no_pegawai, tanggal_mulai_kerja, email_user)
                VALUES (%s, %s, %s)
            """, [str(id_pegawai), tanggal_mulai_kerja, email])

            cursor.execute("""
                INSERT INTO FRONT_DESK (no_front_desk)
                VALUES (%s)
            """, [str(id_pegawai)])

# Form Dokter Hewan
class RegisterDokterForm(forms.Form):
    nomor_izin_praktik = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    nomor_telepon = forms.CharField(required=True)
    tanggal_diterima = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=True)
    alamat = forms.CharField(widget=forms.Textarea, required=True)
    nomor_sertifikat = forms.CharField(required=True)
    nama_sertifikat = forms.CharField(required=True)
    hari_praktik = forms.ChoiceField(choices=[
        ('Senin', 'Senin'),
        ('Selasa', 'Selasa'),
        ('Rabu', 'Rabu'),
        ('Kamis', 'Kamis'),
        ('Jumat', 'Jumat'),
        ('Sabtu', 'Sabtu'),
        ('Minggu', 'Minggu')
    ], required=True)
    jam_praktik = forms.CharField(required=True)

    def save(self):
        email = self.cleaned_data['email']
        password = self.cleaned_data['password']
        alamat = self.cleaned_data['alamat']
        nomor_telepon = self.cleaned_data['nomor_telepon']
        tanggal_diterima = self.cleaned_data['tanggal_diterima']
        no_izin_praktik = self.cleaned_data['nomor_izin_praktik']
        nomor_sertifikat = self.cleaned_data['nomor_sertifikat']
        nama_sertifikat = self.cleaned_data['nama_sertifikat']
        hari_praktik = self.cleaned_data['hari_praktik']
        jam_praktik = self.cleaned_data['jam_praktik']

        id_pegawai = uuid.uuid4()
        id_tenaga_medis = id_pegawai
        id_dokter = id_tenaga_medis

        with connection.cursor() as cursor:
            # USER
            cursor.execute("""
                INSERT INTO "USER" (email, password, alamat, nomor_telepon)
                VALUES (%s, %s, %s, %s)
            """, [email, password, alamat, nomor_telepon])

            # PEGAWAI
            cursor.execute("""
                INSERT INTO PEGAWAI (no_pegawai, tanggal_mulai_kerja, email_user)
                VALUES (%s, %s, %s)
            """, [str(id_pegawai), tanggal_diterima, email])

            # TENAGA_MEDIS
            cursor.execute("""
                INSERT INTO TENAGA_MEDIS (no_tenaga_medis, no_izin_praktik)
                VALUES (%s, %s)
            """, [str(id_tenaga_medis), no_izin_praktik])

            # DOKTER_HEWAN
            cursor.execute("""
                INSERT INTO DOKTER_HEWAN (no_dokter_hewan)
                VALUES (%s)
            """, [str(id_dokter)])

            # SERTIFIKAT_KOMPETENSI
            cursor.execute("""
                INSERT INTO SERTIFIKAT_KOMPETENSI (no_sertifikat_kompetensi, no_tenaga_medis, nama_sertifikat)
                VALUES (%s, %s, %s)
            """, [nomor_sertifikat, str(id_tenaga_medis), nama_sertifikat])

            # JADWAL_PRAKTIK
            cursor.execute("""
                INSERT INTO JADWAL_PRAKTIK (no_dokter_hewan, hari, jam)
                VALUES (%s, %s, %s)
            """, [str(id_dokter), hari_praktik, jam_praktik])

# Form Perawat Hewan
class RegisterPerawatForm(forms.Form):
    nomor_izin_praktik = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    nomor_telepon = forms.CharField(required=True)
    tanggal_diterima = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=True)
    alamat = forms.CharField(widget=forms.Textarea, required=True)
    nomor_sertifikat = forms.CharField(required=True)
    nama_sertifikat = forms.CharField(required=True)

    def save(self):
        email = self.cleaned_data['email']
        password = self.cleaned_data['password']
        alamat = self.cleaned_data['alamat']
        nomor_telepon = self.cleaned_data['nomor_telepon']
        tanggal_diterima = self.cleaned_data['tanggal_diterima']
        no_izin_praktik = self.cleaned_data['nomor_izin_praktik']
        nomor_sertifikat = self.cleaned_data['nomor_sertifikat']
        nama_sertifikat = self.cleaned_data['nama_sertifikat']

        id_pegawai = uuid.uuid4()
        id_tenaga_medis = id_pegawai
        id_perawat = id_tenaga_medis

        with connection.cursor() as cursor:
            # USER
            cursor.execute("""
                INSERT INTO "USER" (email, password, alamat, nomor_telepon)
                VALUES (%s, %s, %s, %s)
            """, [email, password, alamat, nomor_telepon])

            # PEGAWAI
            cursor.execute("""
                INSERT INTO PEGAWAI (no_pegawai, tanggal_mulai_kerja, email_user)
                VALUES (%s, %s, %s)
            """, [str(id_pegawai), tanggal_diterima, email])

            # TENAGA_MEDIS
            cursor.execute("""
                INSERT INTO TENAGA_MEDIS (no_tenaga_medis, no_izin_praktik)
                VALUES (%s, %s)
            """, [str(id_tenaga_medis), no_izin_praktik])

            # PERAWAT_HEWAN
            cursor.execute("""
                INSERT INTO PERAWAT_HEWAN (no_perawat_hewan)
                VALUES (%s)
            """, [str(id_perawat)])

            # SERTIFIKAT_KOMPETENSI
            cursor.execute("""
                INSERT INTO SERTIFIKAT_KOMPETENSI (no_sertifikat_kompetensi, no_tenaga_medis, nama_sertifikat)
                VALUES (%s, %s, %s)
            """, [nomor_sertifikat, str(id_tenaga_medis), nama_sertifikat])