CREATE SCHEMA PET_CLINIC;

SET SEARCH_PATH TO PET_CLINIC;

-- Enable UUID generation (pgcrypto extension)
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- 1. USER
CREATE TABLE "USER" (
  email           VARCHAR(50)   PRIMARY KEY,
  password        VARCHAR(100)  NOT NULL,
  alamat          TEXT          NOT NULL,
  nomor_telepon   VARCHAR(15)   NOT NULL
);

-- 2. PEGAWAI
CREATE TABLE PEGAWAI (
  no_pegawai          UUID      PRIMARY KEY DEFAULT gen_random_uuid(),
  tanggal_mulai_kerja DATE      NOT NULL,
  tanggal_akhir_kerja DATE,
  email_user          VARCHAR(50) NOT NULL,
  CONSTRAINT fk_pegawai_user
    FOREIGN KEY (email_user) REFERENCES "USER"(email) ON UPDATE CASCADE ON DELETE CASCADE
);

-- 3. KLIEN
CREATE TABLE KLIEN (
  no_identitas        UUID      PRIMARY KEY DEFAULT gen_random_uuid(),
  tanggal_registrasi  DATE      NOT NULL,
  email               VARCHAR(50) NOT NULL,
  CONSTRAINT fk_klien_user
    FOREIGN KEY (email) REFERENCES "USER"(email) ON UPDATE CASCADE ON DELETE CASCADE
);

-- 4. INDIVIDU
CREATE TABLE INDIVIDU (
  no_identitas_klien  UUID      PRIMARY KEY,
  nama_depan          VARCHAR(50) NOT NULL,
  nama_tengah         VARCHAR(50),
  nama_belakang       VARCHAR(50) NOT NULL,
  CONSTRAINT fk_individu_klien
    FOREIGN KEY (no_identitas_klien) REFERENCES KLIEN(no_identitas) ON UPDATE CASCADE ON DELETE CASCADE
);

-- 5. PERUSAHAAN
CREATE TABLE PERUSAHAAN (
  no_identitas_klien  UUID      PRIMARY KEY,
  nama_perusahaan     VARCHAR(100) NOT NULL,
  CONSTRAINT fk_perusahaan_klien
    FOREIGN KEY (no_identitas_klien) REFERENCES KLIEN(no_identitas) ON UPDATE CASCADE ON DELETE CASCADE
);

-- 6. FRONT_DESK
CREATE TABLE FRONT_DESK (
  no_front_desk       UUID      PRIMARY KEY,
  CONSTRAINT fk_frontdesk_pegawai
    FOREIGN KEY (no_front_desk) REFERENCES PEGAWAI(no_pegawai) ON UPDATE CASCADE ON DELETE CASCADE
);

-- 7. TENAGA_MEDIS
CREATE TABLE TENAGA_MEDIS (
  no_tenaga_medis     UUID      PRIMARY KEY,
  no_izin_praktik     VARCHAR(20) UNIQUE NOT NULL,
  CONSTRAINT fk_tenagamedis_pegawai
    FOREIGN KEY (no_tenaga_medis) REFERENCES PEGAWAI(no_pegawai) ON UPDATE CASCADE ON DELETE CASCADE
);

-- 8. PERAWAT_HEWAN
CREATE TABLE PERAWAT_HEWAN (
  no_perawat_hewan    UUID      PRIMARY KEY,
  CONSTRAINT fk_perawathewan_tenagamedis
    FOREIGN KEY (no_perawat_hewan) REFERENCES TENAGA_MEDIS(no_tenaga_medis) ON UPDATE CASCADE ON DELETE CASCADE
);

-- 9. DOKTER_HEWAN
CREATE TABLE DOKTER_HEWAN (
  no_dokter_hewan     UUID      PRIMARY KEY,
  CONSTRAINT fk_dokterhewan_tenagamedis
    FOREIGN KEY (no_dokter_hewan) REFERENCES TENAGA_MEDIS(no_tenaga_medis) ON UPDATE CASCADE ON DELETE CASCADE
);

--10. SERTIFIKAT_KOMPETENSI
CREATE TABLE SERTIFIKAT_KOMPETENSI (
  no_sertifikat_kompetensi VARCHAR(10) NOT NULL,
  no_tenaga_medis          UUID        NOT NULL,
  nama_sertifikat          VARCHAR(100) NOT NULL,
  PRIMARY KEY (no_sertifikat_kompetensi, no_tenaga_medis),
  CONSTRAINT fk_sertifikasi_pegawai
    FOREIGN KEY (no_tenaga_medis) REFERENCES TENAGA_MEDIS(no_tenaga_medis) ON UPDATE CASCADE ON DELETE CASCADE
);

-- 11. JADWAL_PRAKTIK
CREATE TABLE JADWAL_PRAKTIK (
  no_dokter_hewan     UUID      NOT NULL,
  hari                 VARCHAR(10) NOT NULL,
  jam                  VARCHAR(20) NOT NULL,
  PRIMARY KEY (no_dokter_hewan, hari, jam),
  CONSTRAINT fk_jadwal_dokter
    FOREIGN KEY (no_dokter_hewan) REFERENCES DOKTER_HEWAN(no_dokter_hewan) ON UPDATE CASCADE ON DELETE CASCADE
);

-- 14. JENIS_HEWAN
CREATE TABLE JENIS_HEWAN (
  id                  UUID      PRIMARY KEY DEFAULT gen_random_uuid(),
  nama_jenis          VARCHAR(50) NOT NULL
);

-- 18. OBAT
CREATE TABLE OBAT (
  kode                VARCHAR(10) PRIMARY KEY,
  nama                VARCHAR(100) NOT NULL,
  harga               INT         NOT NULL,
  stok                INT         NOT NULL,
  dosis               TEXT        NOT NULL
);

-- 19. VAKSIN
CREATE TABLE VAKSIN (
  kode                VARCHAR(6) PRIMARY KEY,
  nama                VARCHAR(50) NOT NULL,
  harga               INT        NOT NULL,
  stok                INT        NOT NULL
);

-- 16. PERAWATAN
CREATE TABLE PERAWATAN (
  kode_perawatan      VARCHAR(10) PRIMARY KEY,
  nama_perawatan      VARCHAR(100) NOT NULL,
  biaya_perawatan     INT         NOT NULL
);

-- 17. PERAWATAN_OBAT
CREATE TABLE PERAWATAN_OBAT (
  kode_perawatan      VARCHAR(10) NOT NULL,
  kode_obat           VARCHAR(10) NOT NULL,
  kuantitas_obat      INT         NOT NULL,
  PRIMARY KEY (kode_perawatan, kode_obat),
  CONSTRAINT fk_po_perawatan
    FOREIGN KEY (kode_perawatan) REFERENCES PERAWATAN(kode_perawatan) ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT fk_po_obat
    FOREIGN KEY (kode_obat) REFERENCES OBAT(kode) ON UPDATE CASCADE ON DELETE CASCADE
);

-- 13. HEWAN
CREATE TABLE HEWAN (
  nama                VARCHAR(50)   NOT NULL,
  no_identitas_klien  UUID          NOT NULL,
  tanggal_lahir       DATE          NOT NULL,
  id_jenis            UUID          NOT NULL,
  url_foto            VARCHAR(255)  NOT NULL,
  PRIMARY KEY (nama, no_identitas_klien),
  CONSTRAINT fk_hewan_klien
    FOREIGN KEY (no_identitas_klien) REFERENCES KLIEN(no_identitas) ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT fk_hewan_jenis
    FOREIGN KEY (id_jenis) REFERENCES JENIS_HEWAN(id) ON UPDATE CASCADE ON DELETE CASCADE
);

-- 12. KUNJUNGAN
CREATE TABLE KUNJUNGAN (
  id_kunjungan        UUID          NOT NULL,
  nama_hewan          VARCHAR(50)   NOT NULL,
  no_identitas_klien  UUID          NOT NULL,
  no_front_desk       UUID          NOT NULL,
  no_perawat_hewan    UUID          NOT NULL,
  no_dokter_hewan     UUID          NOT NULL,
  kode_vaksin         VARCHAR(6),
  tipe_kunjungan      VARCHAR(10)   NOT NULL,
  timestamp_awal      TIMESTAMP     NOT NULL,
  timestamp_akhir     TIMESTAMP,
  suhu                INT,
  berat_badan         NUMERIC(5,2),
  catatan             TEXT,
  PRIMARY KEY (
    id_kunjungan,
    nama_hewan,
    no_identitas_klien,
    no_front_desk,
    no_perawat_hewan,
    no_dokter_hewan
  ),
  CONSTRAINT fk_kunj_hewan
    FOREIGN KEY (nama_hewan, no_identitas_klien) REFERENCES HEWAN(nama, no_identitas_klien) ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT fk_kunj_frontdesk
    FOREIGN KEY (no_front_desk) REFERENCES FRONT_DESK(no_front_desk) ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT fk_kunj_perawat
    FOREIGN KEY (no_perawat_hewan) REFERENCES PERAWAT_HEWAN(no_perawat_hewan) ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT fk_kunj_dokter
    FOREIGN KEY (no_dokter_hewan) REFERENCES DOKTER_HEWAN(no_dokter_hewan) ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT fk_kunj_vaksin
    FOREIGN KEY (kode_vaksin) REFERENCES VAKSIN(kode) ON UPDATE CASCADE ON DELETE CASCADE
);

-- 15. KUNJUNGAN_KEPERAWATAN
CREATE TABLE KUNJUNGAN_KEPERAWATAN (
  id_kunjungan        UUID          NOT NULL,
  nama_hewan          VARCHAR(50)   NOT NULL,
  no_identitas_klien  UUID          NOT NULL,
  no_front_desk       UUID          NOT NULL,
  no_perawat_hewan    UUID          NOT NULL,
  no_dokter_hewan     UUID          NOT NULL,
  kode_perawatan      VARCHAR(10)   NOT NULL,

  PRIMARY KEY (
    id_kunjungan,
    nama_hewan,
    no_identitas_klien,
    no_front_desk,
    no_perawat_hewan,
    no_dokter_hewan,
    kode_perawatan
  ),
  CONSTRAINT fk_kkp_kunj
    FOREIGN KEY (id_kunjungan,nama_hewan,no_identitas_klien,no_front_desk,no_perawat_hewan,no_dokter_hewan) REFERENCES KUNJUNGAN(id_kunjungan,nama_hewan,no_identitas_klien,no_front_desk,no_perawat_hewan,no_dokter_hewan) ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT fk_kkp_perawatan
    FOREIGN KEY (kode_perawatan) REFERENCES PERAWATAN(kode_perawatan) ON UPDATE CASCADE ON DELETE CASCADE
);

INSERT INTO "USER" (email, password, alamat, nomor_telepon) VALUES
('jeremi.felix1@example.com', 'password123', 'Jl. Raya No.1', '081234567890'),
('jeremi.felix2@example.com', 'password123', 'Jl. Raya No.2', '081234567891'),
('jeremi.felix3@example.com', 'password123', 'Jl. Raya No.3', '081234567892'),
('jeremi.felix4@example.com', 'password123', 'Jl. Raya No.4', '081234567893'),
('jeremi.felix5@example.com', 'password123', 'Jl. Raya No.5', '081234567894'),
('jeremi.felix6@example.com', 'password123', 'Jl. Raya No.6', '081234567895'),
('jeremi.felix7@example.com', 'password123', 'Jl. Raya No.7', '081234567896'),
('jeremi.felix8@example.com', 'password123', 'Jl. Raya No.8', '081234567897'),
('jeremi.felix9@example.com', 'password123', 'Jl. Raya No.9', '081234567898'),
('jeremi.felix10@example.com', 'password123', 'Jl. Raya No.10', '081234567899'),
('jeremi.felix11@example.com', 'password123', 'Jl. Raya No.11', '081234568000'),
('jeremi.felix12@example.com', 'password123', 'Jl. Raya No.12', '081234568001'),
('jeremi.felix13@example.com', 'password123', 'Jl. Raya No.13', '081234568002'),
('jeremi.felix14@example.com', 'password123', 'Jl. Raya No.14', '081234568003'),
('jeremi.felix15@example.com', 'password123', 'Jl. Raya No.15', '081234568004'),
('jeremi.felix16@example.com', 'password123', 'Jl. Raya No.16', '081234568005'),
('jeremi.felix17@example.com', 'password123', 'Jl. Raya No.17', '081234568006'),
('jeremi.felix18@example.com', 'password123', 'Jl. Raya No.18', '081234568007'),
('jeremi.felix19@example.com', 'password123', 'Jl. Raya No.19', '081234568008'),
('jeremi.felix20@example.com', 'password123', 'Jl. Raya No.20', '081234568009'),
('jeremi.felix21@example.com', 'password123', 'Jl. Raya No.21', '081234568010'),
('jeremi.felix22@example.com', 'password123', 'Jl. Raya No.22', '081234568011'),
('jeremi.felix23@example.com', 'password123', 'Jl. Raya No.23', '081234568012'),
('jeremi.felix24@example.com', 'password123', 'Jl. Raya No.24', '081234568013'),
('jeremi.felix25@example.com', 'password123', 'Jl. Raya No.25', '081234568014'),
('jeremi.felix26@example.com', 'password123', 'Jl. Raya No.26', '081234568015'),
('jeremi.felix27@example.com', 'password123', 'Jl. Raya No.27', '081234568016'),
('jeremi.felix28@example.com', 'password123', 'Jl. Raya No.28', '081234568017'),
('jeremi.felix29@example.com', 'password123', 'Jl. Raya No.29', '081234568018'),
('jeremi.felix30@example.com', 'password123', 'Jl. Raya No.30', '081234568019'),
('jeremi.felix31@example.com', 'password123', 'Jl. Raya No.31', '081234568020'),
('jeremi.felix32@example.com', 'password123', 'Jl. Raya No.32', '081234568021'),
('jeremi.felix33@example.com', 'password123', 'Jl. Raya No.33', '081234568022'),
('jeremi.felix34@example.com', 'password123', 'Jl. Raya No.34', '081234568023'),
('jeremi.felix35@example.com', 'password123', 'Jl. Raya No.35', '081234568024');


INSERT INTO PEGAWAI (no_pegawai, tanggal_mulai_kerja, tanggal_akhir_kerja, email_user) VALUES
('abecf843-b862-4740-b520-54433acc7290', '2023-01-01', '2025-01-01', 'jeremi.felix1@example.com'),
('6a47b49e-90de-403f-822f-6ae3d6f1ee30', '2023-01-01', '2025-01-01', 'jeremi.felix2@example.com'),
('6ae5d2df-70d0-45f6-9bcb-83ffcf56486b', '2023-01-01', '2025-01-01', 'jeremi.felix3@example.com'),
('9ac67a80-b8c4-428b-872c-a1bb629e1f37', '2023-01-01', '2025-01-01', 'jeremi.felix4@example.com'),
('04c58d7a-98e9-48a7-8b3e-0e9f79a34115', '2023-01-01', '2025-01-01', 'jeremi.felix5@example.com'),
('fd83e600-4cec-4bef-b12d-2134d0bddfe8', '2023-01-01', '2025-01-01', 'jeremi.felix6@example.com'),
('ae9181bc-c622-4e03-9191-fbd8ef0abbca', '2023-01-01', '2025-01-01', 'jeremi.felix7@example.com'),
('b2abc557-ac64-4aa7-bdc3-c6c118aa10ce', '2023-01-01', '2025-01-01', 'jeremi.felix8@example.com'),
('6004e686-8e75-4351-ac76-f640b6da80ad', '2023-01-01', '2025-01-01', 'jeremi.felix9@example.com'),
('c49e3e56-b699-4f2a-9613-3e96756c0ef0', '2023-01-01', '2025-01-01', 'jeremi.felix10@example.com'),
('1b6edf86-07e8-4363-8982-72809df2872e', '2023-01-01', '2025-01-01', 'jeremi.felix11@example.com'),
('b29fb55e-2c30-40eb-8c78-17b8338d4497', '2023-01-01', '2025-01-01', 'jeremi.felix12@example.com'),
('b7cd7031-3a74-4e21-aa96-f4f5db4ab423', '2023-01-01', '2025-01-01', 'jeremi.felix13@example.com'),
('6d492eca-0368-4407-b6cb-8694a998a838', '2023-01-01', '2025-01-01', 'jeremi.felix14@example.com'),
('8f59cb77-0371-41e6-b045-87d221262156', '2023-01-01', '2025-01-01', 'jeremi.felix15@example.com');

-- Mengambil email dari PEGAWAI dengan email_user dari jeremi.felix16@example.com sampai jeremi.felix35@example.com
-- dan menambahkan nomor identitas yang unik (UUID)
INSERT INTO KLIEN (no_identitas, tanggal_registrasi, email) 
VALUES
('aac96c9e-3b3a-42d2-a692-532cb843e69c', '2023-01-01', 'jeremi.felix16@example.com'),
('29d70f98-01cc-4991-93a6-9056b3821764', '2023-01-02', 'jeremi.felix17@example.com'),
('60170261-060c-426b-a03b-d81f47570672', '2023-01-03', 'jeremi.felix18@example.com'),
('bc987b0d-31b9-483f-bf27-8fe53406415e', '2023-01-04', 'jeremi.felix19@example.com'),
('ae83ba4f-643b-42b3-9145-3e2c03ade2a9', '2023-01-05', 'jeremi.felix20@example.com'),
('ac963391-a959-4f2c-9743-40e48b57fffa', '2023-01-06', 'jeremi.felix21@example.com'),
('8f50c31f-34c3-4cf3-b75a-7ea879a35a4e', '2023-01-07', 'jeremi.felix22@example.com'),
('f72e51f3-1461-48b6-abbe-3bd035144e3f', '2023-01-08', 'jeremi.felix23@example.com'),
('21fa96b2-4478-4762-af51-a724439ab5a7', '2023-01-09', 'jeremi.felix24@example.com'),
('2185f18d-dcf1-4ba0-8635-4053cb82f3da', '2023-01-10', 'jeremi.felix25@example.com'),
('f3fb20dd-3d22-41ad-83dc-e9dcbd7e0571', '2023-01-11', 'jeremi.felix26@example.com'),
('c1aeba6d-edab-4955-b72d-492b62ddc04b', '2023-01-12', 'jeremi.felix27@example.com'),
('5d7883ea-8b71-418d-9389-ab1ca95929ea', '2023-01-13', 'jeremi.felix28@example.com'),
('db4d6b4a-46aa-42bd-b732-29029456539d', '2023-01-14', 'jeremi.felix29@example.com'),
('30619d42-1cf1-4116-9860-02bb427fe8cf', '2023-01-15', 'jeremi.felix30@example.com'),
('49794bc3-08e4-4ffd-a298-78f1119bf579', '2023-01-16', 'jeremi.felix31@example.com'),
('1245646a-9821-4cd8-95f3-1729be8936ed', '2023-01-17', 'jeremi.felix32@example.com'),
('2549db55-f55d-4446-a5b3-662da7a2aa94', '2023-01-18', 'jeremi.felix33@example.com'),
('3842c3c7-b2ae-4a8e-8581-1b82faebb05a', '2023-01-19', 'jeremi.felix34@example.com'),
('3d4e7fd3-1a67-4930-8785-04675b72bce7', '2023-01-20', 'jeremi.felix35@example.com');

-- Mengambil no_identitas dari tabel KLIEN dengan email_user dari jeremi.felix16@example.com sampai jeremi.felix25@example.com
-- dan menambahkan data nama depan, tengah, dan belakang
INSERT INTO INDIVIDU (no_identitas_klien, nama_depan, nama_tengah, nama_belakang) 
VALUES
((SELECT no_identitas FROM KLIEN WHERE email = 'jeremi.felix16@example.com' LIMIT 1), 'Jeremi', 'Felix', 'Santosa'),
((SELECT no_identitas FROM KLIEN WHERE email = 'jeremi.felix17@example.com' LIMIT 1), 'Jeremi', 'Felix', 'Santoso'),
((SELECT no_identitas FROM KLIEN WHERE email = 'jeremi.felix18@example.com' LIMIT 1), 'Jeremi', 'Felix', 'Santose'),
((SELECT no_identitas FROM KLIEN WHERE email = 'jeremi.felix19@example.com' LIMIT 1), 'Jeremi', 'Felix', 'Santosi'),
((SELECT no_identitas FROM KLIEN WHERE email = 'jeremi.felix20@example.com' LIMIT 1), 'Jeremi', 'Felix', 'Santosu'),
((SELECT no_identitas FROM KLIEN WHERE email = 'jeremi.felix21@example.com' LIMIT 1), 'Jeremi', 'Felix', 'Sentosa'),
((SELECT no_identitas FROM KLIEN WHERE email = 'jeremi.felix22@example.com' LIMIT 1), 'Jeremi', 'Felix', 'Sontosa'),
((SELECT no_identitas FROM KLIEN WHERE email = 'jeremi.felix23@example.com' LIMIT 1), 'Jeremi', 'Felix', 'Suntosa'),
((SELECT no_identitas FROM KLIEN WHERE email = 'jeremi.felix24@example.com' LIMIT 1), 'Jeremi', 'Felix', 'Sintosa'),
((SELECT no_identitas FROM KLIEN WHERE email = 'jeremi.felix25@example.com' LIMIT 1), 'Jeremi', 'Felix', 'Sentosa');

-- Mengambil no_identitas dari tabel KLIEN dengan email_user dari jeremi.felix26@example.com sampai jeremi.felix35@example.com
-- dan menambahkan nama_perusahaan
INSERT INTO PERUSAHAAN (no_identitas_klien, nama_perusahaan) 
VALUES
((SELECT no_identitas FROM KLIEN WHERE email = 'jeremi.felix26@example.com' LIMIT 1), 'Perusahaan A'),
((SELECT no_identitas FROM KLIEN WHERE email = 'jeremi.felix27@example.com' LIMIT 1), 'Perusahaan B'),
((SELECT no_identitas FROM KLIEN WHERE email = 'jeremi.felix28@example.com' LIMIT 1), 'Perusahaan C'),
((SELECT no_identitas FROM KLIEN WHERE email = 'jeremi.felix29@example.com' LIMIT 1), 'Perusahaan D'),
((SELECT no_identitas FROM KLIEN WHERE email = 'jeremi.felix30@example.com' LIMIT 1), 'Perusahaan E'),
((SELECT no_identitas FROM KLIEN WHERE email = 'jeremi.felix31@example.com' LIMIT 1), 'Perusahaan F'),
((SELECT no_identitas FROM KLIEN WHERE email = 'jeremi.felix32@example.com' LIMIT 1), 'Perusahaan G'),
((SELECT no_identitas FROM KLIEN WHERE email = 'jeremi.felix33@example.com' LIMIT 1), 'Perusahaan H'),
((SELECT no_identitas FROM KLIEN WHERE email = 'jeremi.felix34@example.com' LIMIT 1), 'Perusahaan I'),
((SELECT no_identitas FROM KLIEN WHERE email = 'jeremi.felix35@example.com' LIMIT 1), 'Perusahaan J');


-- Pastikan no_front_desk diambil dari tabel PEGAWAI.no_pegawai
INSERT INTO FRONT_DESK (no_front_desk) VALUES
((SELECT no_pegawai FROM PEGAWAI WHERE email_user = 'jeremi.felix1@example.com' LIMIT 1)),
((SELECT no_pegawai FROM PEGAWAI WHERE email_user = 'jeremi.felix2@example.com' LIMIT 1)),
((SELECT no_pegawai FROM PEGAWAI WHERE email_user = 'jeremi.felix3@example.com' LIMIT 1)),
((SELECT no_pegawai FROM PEGAWAI WHERE email_user = 'jeremi.felix4@example.com' LIMIT 1)),
((SELECT no_pegawai FROM PEGAWAI WHERE email_user = 'jeremi.felix5@example.com' LIMIT 1));

-- Mengambil no_pegawai dari tabel PEGAWAI dengan email_user dari jeremi.felix6@example.com sampai jeremi.felix15@example.com
-- dan menambahkan nomor_izin_praktik yang unik
INSERT INTO TENAGA_MEDIS (no_tenaga_medis, no_izin_praktik) 
VALUES
((SELECT no_pegawai FROM PEGAWAI WHERE email_user = 'jeremi.felix6@example.com' LIMIT 1), 'IZIN006'),
((SELECT no_pegawai FROM PEGAWAI WHERE email_user = 'jeremi.felix7@example.com' LIMIT 1), 'IZIN007'),
((SELECT no_pegawai FROM PEGAWAI WHERE email_user = 'jeremi.felix8@example.com' LIMIT 1), 'IZIN008'),
((SELECT no_pegawai FROM PEGAWAI WHERE email_user = 'jeremi.felix9@example.com' LIMIT 1), 'IZIN009'),
((SELECT no_pegawai FROM PEGAWAI WHERE email_user = 'jeremi.felix10@example.com' LIMIT 1), 'IZIN010'),
((SELECT no_pegawai FROM PEGAWAI WHERE email_user = 'jeremi.felix11@example.com' LIMIT 1), 'IZIN011'),
((SELECT no_pegawai FROM PEGAWAI WHERE email_user = 'jeremi.felix12@example.com' LIMIT 1), 'IZIN012'),
((SELECT no_pegawai FROM PEGAWAI WHERE email_user = 'jeremi.felix13@example.com' LIMIT 1), 'IZIN013'),
((SELECT no_pegawai FROM PEGAWAI WHERE email_user = 'jeremi.felix14@example.com' LIMIT 1), 'IZIN014'),
((SELECT no_pegawai FROM PEGAWAI WHERE email_user = 'jeremi.felix15@example.com' LIMIT 1), 'IZIN015');




-- INSERT data ke tabel PERAWAT_HEWAN dengan mengambil no_tenaga_medis dari email_user 6-10
INSERT INTO PERAWAT_HEWAN (no_perawat_hewan) 
VALUES
('fd83e600-4cec-4bef-b12d-2134d0bddfe8'),
('ae9181bc-c622-4e03-9191-fbd8ef0abbca'),
('b2abc557-ac64-4aa7-bdc3-c6c118aa10ce'),
('6004e686-8e75-4351-ac76-f640b6da80ad'),
('c49e3e56-b699-4f2a-9613-3e96756c0ef0');


-- INSERT data ke tabel DOKTER_HEWAN dengan mengambil no_tenaga_medis dari email_user 11-15
INSERT INTO DOKTER_HEWAN (no_dokter_hewan) 
VALUES
('1b6edf86-07e8-4363-8982-72809df2872e'),
('b29fb55e-2c30-40eb-8c78-17b8338d4497'),
('b7cd7031-3a74-4e21-aa96-f4f5db4ab423'),
('6d492eca-0368-4407-b6cb-8694a998a838'),
('8f59cb77-0371-41e6-b045-87d221262156');

-- Mengambil no_tenaga_medis dari TENAGA_MEDIS berdasarkan email_user 6-15
-- dan menambahkan nama_sertifikat yang unik
INSERT INTO SERTIFIKAT_KOMPETENSI (no_sertifikat_kompetensi, no_tenaga_medis, nama_sertifikat) 
VALUES
('1000000006', 'fd83e600-4cec-4bef-b12d-2134d0bddfe8', 'Sertifikat F'),
('1000000007', 'ae9181bc-c622-4e03-9191-fbd8ef0abbca', 'Sertifikat G'),
('1000000008', 'b2abc557-ac64-4aa7-bdc3-c6c118aa10ce', 'Sertifikat H'),
('1000000009', '6004e686-8e75-4351-ac76-f640b6da80ad', 'Sertifikat I'),
('1000000010', 'c49e3e56-b699-4f2a-9613-3e96756c0ef0', 'Sertifikat J'),
('1000000011', '1b6edf86-07e8-4363-8982-72809df2872e', 'Sertifikat K'),
('1000000012', 'b29fb55e-2c30-40eb-8c78-17b8338d4497', 'Sertifikat L'),
('1000000013', 'b7cd7031-3a74-4e21-aa96-f4f5db4ab423', 'Sertifikat M'),
('1000000014', '6d492eca-0368-4407-b6cb-8694a998a838', 'Sertifikat N'),
('1000000015', '8f59cb77-0371-41e6-b045-87d221262156', 'Sertifikat O');

-- Mengambil 2 jadwal untuk masing-masing no_dokter_hewan
INSERT INTO JADWAL_PRAKTIK (no_dokter_hewan, hari, jam) 
VALUES
('1b6edf86-07e8-4363-8982-72809df2872e', 'Senin', '09:00-12:00'),
('1b6edf86-07e8-4363-8982-72809df2872e', 'Senin', '13:00-16:00'),
('6d492eca-0368-4407-b6cb-8694a998a838', 'Selasa', '09:00-12:00'),
('6d492eca-0368-4407-b6cb-8694a998a838', 'Selasa', '13:00-16:00'),
('8f59cb77-0371-41e6-b045-87d221262156', 'Rabu', '09:00-12:00'),
('8f59cb77-0371-41e6-b045-87d221262156', 'Rabu', '13:00-16:00'),
('b29fb55e-2c30-40eb-8c78-17b8338d4497', 'Kamis', '09:00-12:00'),
('b29fb55e-2c30-40eb-8c78-17b8338d4497', 'Kamis', '13:00-16:00'),
('b7cd7031-3a74-4e21-aa96-f4f5db4ab423', 'Jumat', '09:00-12:00'),
('b7cd7031-3a74-4e21-aa96-f4f5db4ab423', 'Jumat', '13:00-16:00'),
('1b6edf86-07e8-4363-8982-72809df2872e', 'selasa', '09:00-12:00'),
('1b6edf86-07e8-4363-8982-72809df2872e', 'selasa', '13:00-16:00'),
('6d492eca-0368-4407-b6cb-8694a998a838', 'rabu', '09:00-12:00'),
('6d492eca-0368-4407-b6cb-8694a998a838', 'rabu', '13:00-16:00'),
('8f59cb77-0371-41e6-b045-87d221262156', 'kamis', '09:00-12:00'),
('8f59cb77-0371-41e6-b045-87d221262156', 'kamis', '13:00-16:00'),
('b29fb55e-2c30-40eb-8c78-17b8338d4497', 'jumat', '09:00-12:00'),
('b29fb55e-2c30-40eb-8c78-17b8338d4497', 'jumat', '13:00-16:00'),
('b7cd7031-3a74-4e21-aa96-f4f5db4ab423', 'senin', '09:00-12:00'),
('b7cd7031-3a74-4e21-aa96-f4f5db4ab423', 'senin', '13:00-16:00');


INSERT INTO JENIS_HEWAN (id, nama_jenis) 
VALUES
('53f6ac39-e535-4d3f-8ab3-b663d69a4572', 'Anjing'),
('55be9e2b-2460-4c49-a463-c41a8130c942', 'Kucing'),
('3e286793-2a05-41d8-8654-6f23d5867f96', 'Burung'),
('0cef2d58-5ea1-4e80-a4ea-e8dce914e969', 'Ikan'),
('0191bce9-2f65-4e59-b713-898729d754c0', 'Hamster');

-- Menambahkan 10 data ke tabel OBAT
INSERT INTO OBAT (kode, nama, harga, stok, dosis) 
VALUES
('OBT001', 'Obat A', 50000, 100, '1 tablet sehari'),
('OBT002', 'Obat B', 60000, 150, '2 tablet sehari'),
('OBT003', 'Obat C', 75000, 200, '1 tablet dua kali sehari'),
('OBT004', 'Obat D', 80000, 80, '1 tablet setiap makan'),
('OBT005', 'Obat E', 95000, 120, '1 tablet sebelum tidur'),
('OBT006', 'Obat F', 40000, 90, '2 tablet sehari'),
('OBT007', 'Obat G', 55000, 130, '1 tablet setelah makan'),
('OBT008', 'Obat H', 45000, 110, '1 tablet di pagi hari'),
('OBT009', 'Obat I', 35000, 180, '1 tablet sehari'),
('OBT010', 'Obat J', 30000, 160, '1 tablet tiga kali sehari');

-- Menambahkan 10 data ke tabel VAKSIN
INSERT INTO VAKSIN (kode, nama, harga, stok) 
VALUES
('VKS001', 'Vaksin A', 150000, 50),
('VKS002', 'Vaksin B', 180000, 60),
('VKS003', 'Vaksin C', 120000, 70),
('VKS004', 'Vaksin D', 160000, 80),
('VKS005', 'Vaksin E', 140000, 90),
('VKS006', 'Vaksin F', 130000, 100),
('VKS007', 'Vaksin G', 170000, 110),
('VKS008', 'Vaksin H', 200000, 120),
('VKS009', 'Vaksin I', 210000, 130),
('VKS010', 'Vaksin J', 220000, 140);

-- Menambahkan 5 data ke tabel PERAWATAN
INSERT INTO PERAWATAN (kode_perawatan, nama_perawatan, biaya_perawatan) 
VALUES
('PRW0000001', 'Perawatan A', 200000),
('PRW0000002', 'Perawatan B', 300000),
('PRW0000003', 'Perawatan C', 250000),
('PRW0000004', 'Perawatan D', 350000),
('PRW0000005', 'Perawatan E', 400000);

INSERT INTO PERAWATAN_OBAT (kode_perawatan, kode_obat, kuantitas_obat) 
VALUES
('PRW0000001', 'OBT001', 5),
('PRW0000001', 'OBT002', 2),
('PRW0000002', 'OBT003', 1),
('PRW0000002', 'OBT004', 3),
('PRW0000003', 'OBT005', 4),
('PRW0000003', 'OBT006', 2),
('PRW0000004', 'OBT007', 2),
('PRW0000004', 'OBT008', 2),
('PRW0000005', 'OBT009', 2),
('PRW0000005', 'OBT010', 2);


INSERT INTO HEWAN(nama, no_identitas_klien,tanggal_lahir,id_jenis,url_foto) 
VALUES
('Anjing 1', 'f72e51f3-1461-48b6-abbe-3bd035144e3f','2025-01-01','53f6ac39-e535-4d3f-8ab3-b663d69a4572','https://www.google.com/fotoanjing'),
('Anjing 2', 'f72e51f3-1461-48b6-abbe-3bd035144e3f','2025-01-01','53f6ac39-e535-4d3f-8ab3-b663d69a4572','https://www.google.com/fotoanjing'),
('Anjing 3', 'f72e51f3-1461-48b6-abbe-3bd035144e3f','2025-01-01','53f6ac39-e535-4d3f-8ab3-b663d69a4572','https://www.google.com/fotoanjing'),
('Anjing 4', 'f72e51f3-1461-48b6-abbe-3bd035144e3f','2025-01-01','53f6ac39-e535-4d3f-8ab3-b663d69a4572','https://www.google.com/fotoanjing'),
('Anjing 5', 'f72e51f3-1461-48b6-abbe-3bd035144e3f','2025-01-01','53f6ac39-e535-4d3f-8ab3-b663d69a4572','https://www.google.com/fotoanjing'),
('Anjing 6', 'f72e51f3-1461-48b6-abbe-3bd035144e3f','2025-01-01','53f6ac39-e535-4d3f-8ab3-b663d69a4572','https://www.google.com/fotoanjing'),
('Anjing 7', 'f72e51f3-1461-48b6-abbe-3bd035144e3f','2025-01-01','53f6ac39-e535-4d3f-8ab3-b663d69a4572','https://www.google.com/fotoanjing'),
('Anjing 8', 'f72e51f3-1461-48b6-abbe-3bd035144e3f','2025-01-01','53f6ac39-e535-4d3f-8ab3-b663d69a4572','https://www.google.com/fotoanjing'),
('Anjing 9', 'f72e51f3-1461-48b6-abbe-3bd035144e3f','2025-01-01','53f6ac39-e535-4d3f-8ab3-b663d69a4572','https://www.google.com/fotoanjing'),
('Anjing 10', 'f72e51f3-1461-48b6-abbe-3bd035144e3f','2025-01-01','53f6ac39-e535-4d3f-8ab3-b663d69a4572','https://www.google.com/fotoanjing'),
('Anjing 11', 'f72e51f3-1461-48b6-abbe-3bd035144e3f','2025-01-01','53f6ac39-e535-4d3f-8ab3-b663d69a4572','https://www.google.com/fotoanjing'),
('Anjing 12', 'f72e51f3-1461-48b6-abbe-3bd035144e3f','2025-01-01','53f6ac39-e535-4d3f-8ab3-b663d69a4572','https://www.google.com/fotoanjing'),
('Anjing 13', 'f72e51f3-1461-48b6-abbe-3bd035144e3f','2025-01-01','53f6ac39-e535-4d3f-8ab3-b663d69a4572','https://www.google.com/fotoanjing'),
('Anjing 14', 'f72e51f3-1461-48b6-abbe-3bd035144e3f','2025-01-01','53f6ac39-e535-4d3f-8ab3-b663d69a4572','https://www.google.com/fotoanjing'),
('Anjing 15', 'f72e51f3-1461-48b6-abbe-3bd035144e3f','2025-01-01','53f6ac39-e535-4d3f-8ab3-b663d69a4572','https://www.google.com/fotoanjing'),
('Anjing 16', 'f72e51f3-1461-48b6-abbe-3bd035144e3f','2025-01-01','53f6ac39-e535-4d3f-8ab3-b663d69a4572','https://www.google.com/fotoanjing'),
('Anjing 17', 'f72e51f3-1461-48b6-abbe-3bd035144e3f','2025-01-01','53f6ac39-e535-4d3f-8ab3-b663d69a4572','https://www.google.com/fotoanjing'),
('Anjing 18', 'f72e51f3-1461-48b6-abbe-3bd035144e3f','2025-01-01','53f6ac39-e535-4d3f-8ab3-b663d69a4572','https://www.google.com/fotoanjing'),
('Anjing 19', 'f72e51f3-1461-48b6-abbe-3bd035144e3f','2025-01-01','53f6ac39-e535-4d3f-8ab3-b663d69a4572','https://www.google.com/fotoanjing'),
('Anjing 20', 'f72e51f3-1461-48b6-abbe-3bd035144e3f','2025-01-01','53f6ac39-e535-4d3f-8ab3-b663d69a4572','https://www.google.com/fotoanjing'),
('Anjing 21', 'f72e51f3-1461-48b6-abbe-3bd035144e3f','2025-01-01','53f6ac39-e535-4d3f-8ab3-b663d69a4572','https://www.google.com/fotoanjing'),
('Anjing 22', 'f72e51f3-1461-48b6-abbe-3bd035144e3f','2025-01-01','53f6ac39-e535-4d3f-8ab3-b663d69a4572','https://www.google.com/fotoanjing'),
('Anjing 23', 'f72e51f3-1461-48b6-abbe-3bd035144e3f','2025-01-01','53f6ac39-e535-4d3f-8ab3-b663d69a4572','https://www.google.com/fotoanjing'),
('Anjing 24', 'f72e51f3-1461-48b6-abbe-3bd035144e3f','2025-01-01','53f6ac39-e535-4d3f-8ab3-b663d69a4572','https://www.google.com/fotoanjing'),
('Anjing 25', 'f72e51f3-1461-48b6-abbe-3bd035144e3f','2025-01-01','53f6ac39-e535-4d3f-8ab3-b663d69a4572','https://www.google.com/fotoanjing'),
('Anjing 26', 'f72e51f3-1461-48b6-abbe-3bd035144e3f','2025-01-01','53f6ac39-e535-4d3f-8ab3-b663d69a4572','https://www.google.com/fotoanjing'),
('Anjing 27', 'f72e51f3-1461-48b6-abbe-3bd035144e3f','2025-01-01','53f6ac39-e535-4d3f-8ab3-b663d69a4572','https://www.google.com/fotoanjing'),
('Anjing 28', 'f72e51f3-1461-48b6-abbe-3bd035144e3f','2025-01-01','53f6ac39-e535-4d3f-8ab3-b663d69a4572','https://www.google.com/fotoanjing'),
('Anjing 29', 'f72e51f3-1461-48b6-abbe-3bd035144e3f','2025-01-01','53f6ac39-e535-4d3f-8ab3-b663d69a4572','https://www.google.com/fotoanjing'),
('Anjing 30', 'f72e51f3-1461-48b6-abbe-3bd035144e3f','2025-01-01','53f6ac39-e535-4d3f-8ab3-b663d69a4572','https://www.google.com/fotoanjing'),
('Anjing 31', 'f72e51f3-1461-48b6-abbe-3bd035144e3f','2025-01-01','53f6ac39-e535-4d3f-8ab3-b663d69a4572','https://www.google.com/fotoanjing'),
('Anjing 32', 'f72e51f3-1461-48b6-abbe-3bd035144e3f','2025-01-01','53f6ac39-e535-4d3f-8ab3-b663d69a4572','https://www.google.com/fotoanjing'),
('Anjing 33', 'f72e51f3-1461-48b6-abbe-3bd035144e3f','2025-01-01','53f6ac39-e535-4d3f-8ab3-b663d69a4572','https://www.google.com/fotoanjing'),
('Anjing 34', 'f72e51f3-1461-48b6-abbe-3bd035144e3f','2025-01-01','53f6ac39-e535-4d3f-8ab3-b663d69a4572','https://www.google.com/fotoanjing'),
('Anjing 35', 'f72e51f3-1461-48b6-abbe-3bd035144e3f','2025-01-01','53f6ac39-e535-4d3f-8ab3-b663d69a4572','https://www.google.com/fotoanjing'),
('Anjing 36', 'f72e51f3-1461-48b6-abbe-3bd035144e3f','2025-01-01','53f6ac39-e535-4d3f-8ab3-b663d69a4572','https://www.google.com/fotoanjing'),
('Anjing 37', 'f72e51f3-1461-48b6-abbe-3bd035144e3f','2025-01-01','53f6ac39-e535-4d3f-8ab3-b663d69a4572','https://www.google.com/fotoanjing'),
('Anjing 38', 'f72e51f3-1461-48b6-abbe-3bd035144e3f','2025-01-01','53f6ac39-e535-4d3f-8ab3-b663d69a4572','https://www.google.com/fotoanjing'),
('Anjing 39', 'f72e51f3-1461-48b6-abbe-3bd035144e3f','2025-01-01','53f6ac39-e535-4d3f-8ab3-b663d69a4572','https://www.google.com/fotoanjing'),
('Anjing 40', 'f72e51f3-1461-48b6-abbe-3bd035144e3f','2025-01-01','53f6ac39-e535-4d3f-8ab3-b663d69a4572','https://www.google.com/fotoanjing');





INSERT INTO KUNJUNGAN (id_kunjungan,nama_hewan,no_identitas_klien,no_front_desk,no_perawat_hewan,no_dokter_hewan,kode_vaksin,tipe_kunjungan,timestamp_awal,timestamp_akhir)
VALUES
('dcec9499-172e-43b3-aa48-3981aee98825','Anjing 1','f72e51f3-1461-48b6-abbe-3bd035144e3f','04c58d7a-98e9-48a7-8b3e-0e9f79a34115','6004e686-8e75-4351-ac76-f640b6da80ad','1b6edf86-07e8-4363-8982-72809df2872e','VKS001','Darurat','2025-04-24 11:00:00','2025-04-24 13:00:00'),
('a1018e26-fcce-489e-8491-5017740323d5','Anjing 2','f72e51f3-1461-48b6-abbe-3bd035144e3f','04c58d7a-98e9-48a7-8b3e-0e9f79a34115','6004e686-8e75-4351-ac76-f640b6da80ad','1b6edf86-07e8-4363-8982-72809df2872e','VKS001','Darurat','2025-04-24 11:00:00','2025-04-24 13:00:00'),
('f3a4a119-8209-467b-86fc-94a028a3ac65','Anjing 3','f72e51f3-1461-48b6-abbe-3bd035144e3f','04c58d7a-98e9-48a7-8b3e-0e9f79a34115','6004e686-8e75-4351-ac76-f640b6da80ad','1b6edf86-07e8-4363-8982-72809df2872e','VKS001','Darurat','2025-04-24 11:00:00','2025-04-24 13:00:00'),
('b4d7bf57-1530-451a-8e3c-075b2b06e89e','Anjing 4','f72e51f3-1461-48b6-abbe-3bd035144e3f','04c58d7a-98e9-48a7-8b3e-0e9f79a34115','6004e686-8e75-4351-ac76-f640b6da80ad','1b6edf86-07e8-4363-8982-72809df2872e','VKS001','Darurat','2025-04-24 11:00:00','2025-04-24 13:00:00'),
('86145138-cef1-4973-8157-4e3bb9a97f09','Anjing 5','f72e51f3-1461-48b6-abbe-3bd035144e3f','04c58d7a-98e9-48a7-8b3e-0e9f79a34115','6004e686-8e75-4351-ac76-f640b6da80ad','1b6edf86-07e8-4363-8982-72809df2872e','VKS001','Darurat','2025-04-24 11:00:00','2025-04-24 13:00:00'),
('efb7808a-3e20-46a4-8576-3d1ab4e53400','Anjing 6','f72e51f3-1461-48b6-abbe-3bd035144e3f','04c58d7a-98e9-48a7-8b3e-0e9f79a34115','6004e686-8e75-4351-ac76-f640b6da80ad','1b6edf86-07e8-4363-8982-72809df2872e','VKS001','Darurat','2025-04-24 11:00:00','2025-04-24 13:00:00'),
('f80333e0-8fac-4ea4-abdb-bda5d03d9c72','Anjing 7','f72e51f3-1461-48b6-abbe-3bd035144e3f','04c58d7a-98e9-48a7-8b3e-0e9f79a34115','6004e686-8e75-4351-ac76-f640b6da80ad','1b6edf86-07e8-4363-8982-72809df2872e','VKS001','Darurat','2025-04-24 11:00:00','2025-04-24 13:00:00'),
('bb73717c-9d08-4add-a55c-29c3d74edf64','Anjing 8','f72e51f3-1461-48b6-abbe-3bd035144e3f','04c58d7a-98e9-48a7-8b3e-0e9f79a34115','6004e686-8e75-4351-ac76-f640b6da80ad','1b6edf86-07e8-4363-8982-72809df2872e','VKS001','Darurat','2025-04-24 11:00:00','2025-04-24 13:00:00'),
('491fc472-0605-48c5-afbb-180ecce1d50a','Anjing 9','f72e51f3-1461-48b6-abbe-3bd035144e3f','04c58d7a-98e9-48a7-8b3e-0e9f79a34115','6004e686-8e75-4351-ac76-f640b6da80ad','1b6edf86-07e8-4363-8982-72809df2872e','VKS001','Darurat','2025-04-24 11:00:00','2025-04-24 13:00:00'),
('b9a954a7-01fd-4be9-8b45-e928b006ede3','Anjing 10','f72e51f3-1461-48b6-abbe-3bd035144e3f','04c58d7a-98e9-48a7-8b3e-0e9f79a34115','6004e686-8e75-4351-ac76-f640b6da80ad','1b6edf86-07e8-4363-8982-72809df2872e','VKS001','Darurat','2025-04-24 11:00:00','2025-04-24 13:00:00'),
('fe3df490-576d-48f6-a297-7b2cddb5cae5','Anjing 11','f72e51f3-1461-48b6-abbe-3bd035144e3f','04c58d7a-98e9-48a7-8b3e-0e9f79a34115','6004e686-8e75-4351-ac76-f640b6da80ad','1b6edf86-07e8-4363-8982-72809df2872e','VKS001','Darurat','2025-04-24 11:00:00','2025-04-24 13:00:00'),
('4ef85b4d-f910-46be-926a-7daeb62870d0','Anjing 12','f72e51f3-1461-48b6-abbe-3bd035144e3f','04c58d7a-98e9-48a7-8b3e-0e9f79a34115','6004e686-8e75-4351-ac76-f640b6da80ad','1b6edf86-07e8-4363-8982-72809df2872e','VKS001','Darurat','2025-04-24 11:00:00','2025-04-24 13:00:00'),
('e615902b-70a6-4b49-8f94-c03a0708b4a3','Anjing 13','f72e51f3-1461-48b6-abbe-3bd035144e3f','04c58d7a-98e9-48a7-8b3e-0e9f79a34115','6004e686-8e75-4351-ac76-f640b6da80ad','1b6edf86-07e8-4363-8982-72809df2872e','VKS001','Darurat','2025-04-24 11:00:00','2025-04-24 13:00:00'),
('23b6b785-8c4a-4653-9df4-6e0bf32a4792','Anjing 14','f72e51f3-1461-48b6-abbe-3bd035144e3f','04c58d7a-98e9-48a7-8b3e-0e9f79a34115','6004e686-8e75-4351-ac76-f640b6da80ad','1b6edf86-07e8-4363-8982-72809df2872e','VKS001','Darurat','2025-04-24 11:00:00','2025-04-24 13:00:00'),
('f28683c0-7f1d-4192-b753-ae393765c859','Anjing 15','f72e51f3-1461-48b6-abbe-3bd035144e3f','04c58d7a-98e9-48a7-8b3e-0e9f79a34115','6004e686-8e75-4351-ac76-f640b6da80ad','1b6edf86-07e8-4363-8982-72809df2872e','VKS001','Darurat','2025-04-24 11:00:00','2025-04-24 13:00:00'),
('72185e24-fb78-4412-86dc-2e71bc789b1d','Anjing 16','f72e51f3-1461-48b6-abbe-3bd035144e3f','04c58d7a-98e9-48a7-8b3e-0e9f79a34115','6004e686-8e75-4351-ac76-f640b6da80ad','1b6edf86-07e8-4363-8982-72809df2872e','VKS001','Darurat','2025-04-24 11:00:00','2025-04-24 13:00:00'),
('04b7082d-26d0-42d9-b788-e75b189152ca','Anjing 17','f72e51f3-1461-48b6-abbe-3bd035144e3f','04c58d7a-98e9-48a7-8b3e-0e9f79a34115','6004e686-8e75-4351-ac76-f640b6da80ad','1b6edf86-07e8-4363-8982-72809df2872e','VKS001','Darurat','2025-04-24 11:00:00','2025-04-24 13:00:00'),
('3d7e73d8-13ec-4c2e-8cf0-b6336a502ed5','Anjing 18','f72e51f3-1461-48b6-abbe-3bd035144e3f','04c58d7a-98e9-48a7-8b3e-0e9f79a34115','6004e686-8e75-4351-ac76-f640b6da80ad','1b6edf86-07e8-4363-8982-72809df2872e','VKS001','Darurat','2025-04-24 11:00:00','2025-04-24 13:00:00'),
('ea175ff5-4da5-4000-8b5e-8a40dc17cb0d','Anjing 19','f72e51f3-1461-48b6-abbe-3bd035144e3f','04c58d7a-98e9-48a7-8b3e-0e9f79a34115','6004e686-8e75-4351-ac76-f640b6da80ad','1b6edf86-07e8-4363-8982-72809df2872e','VKS001','Darurat','2025-04-24 11:00:00','2025-04-24 13:00:00'),
('e49b68e7-af32-44a0-b190-93803deef0fa','Anjing 20','f72e51f3-1461-48b6-abbe-3bd035144e3f','04c58d7a-98e9-48a7-8b3e-0e9f79a34115','6004e686-8e75-4351-ac76-f640b6da80ad','1b6edf86-07e8-4363-8982-72809df2872e','VKS001','Darurat','2025-04-24 11:00:00','2025-04-24 13:00:00');

INSERT INTO KUNJUNGAN_KEPERAWATAN (id_kunjungan,nama_hewan,no_identitas_klien,no_front_desk,no_perawat_hewan,no_dokter_hewan,kode_perawatan)
VALUES
('dcec9499-172e-43b3-aa48-3981aee98825','Anjing 1','f72e51f3-1461-48b6-abbe-3bd035144e3f','04c58d7a-98e9-48a7-8b3e-0e9f79a34115','6004e686-8e75-4351-ac76-f640b6da80ad','1b6edf86-07e8-4363-8982-72809df2872e','PRW0000001'),
('a1018e26-fcce-489e-8491-5017740323d5','Anjing 2','f72e51f3-1461-48b6-abbe-3bd035144e3f','04c58d7a-98e9-48a7-8b3e-0e9f79a34115','6004e686-8e75-4351-ac76-f640b6da80ad','1b6edf86-07e8-4363-8982-72809df2872e','PRW0000002'),
('f3a4a119-8209-467b-86fc-94a028a3ac65','Anjing 3','f72e51f3-1461-48b6-abbe-3bd035144e3f','04c58d7a-98e9-48a7-8b3e-0e9f79a34115','6004e686-8e75-4351-ac76-f640b6da80ad','1b6edf86-07e8-4363-8982-72809df2872e','PRW0000003'),
('b4d7bf57-1530-451a-8e3c-075b2b06e89e','Anjing 4','f72e51f3-1461-48b6-abbe-3bd035144e3f','04c58d7a-98e9-48a7-8b3e-0e9f79a34115','6004e686-8e75-4351-ac76-f640b6da80ad','1b6edf86-07e8-4363-8982-72809df2872e','PRW0000004'),
('86145138-cef1-4973-8157-4e3bb9a97f09','Anjing 5','f72e51f3-1461-48b6-abbe-3bd035144e3f','04c58d7a-98e9-48a7-8b3e-0e9f79a34115','6004e686-8e75-4351-ac76-f640b6da80ad','1b6edf86-07e8-4363-8982-72809df2872e','PRW0000005'),
('efb7808a-3e20-46a4-8576-3d1ab4e53400','Anjing 6','f72e51f3-1461-48b6-abbe-3bd035144e3f','04c58d7a-98e9-48a7-8b3e-0e9f79a34115','6004e686-8e75-4351-ac76-f640b6da80ad','1b6edf86-07e8-4363-8982-72809df2872e','PRW0000001'),
('f80333e0-8fac-4ea4-abdb-bda5d03d9c72','Anjing 7','f72e51f3-1461-48b6-abbe-3bd035144e3f','04c58d7a-98e9-48a7-8b3e-0e9f79a34115','6004e686-8e75-4351-ac76-f640b6da80ad','1b6edf86-07e8-4363-8982-72809df2872e','PRW0000002'),
('bb73717c-9d08-4add-a55c-29c3d74edf64','Anjing 8','f72e51f3-1461-48b6-abbe-3bd035144e3f','04c58d7a-98e9-48a7-8b3e-0e9f79a34115','6004e686-8e75-4351-ac76-f640b6da80ad','1b6edf86-07e8-4363-8982-72809df2872e','PRW0000003'),
('491fc472-0605-48c5-afbb-180ecce1d50a','Anjing 9','f72e51f3-1461-48b6-abbe-3bd035144e3f','04c58d7a-98e9-48a7-8b3e-0e9f79a34115','6004e686-8e75-4351-ac76-f640b6da80ad','1b6edf86-07e8-4363-8982-72809df2872e','PRW0000004'),
('b9a954a7-01fd-4be9-8b45-e928b006ede3','Anjing 10','f72e51f3-1461-48b6-abbe-3bd035144e3f','04c58d7a-98e9-48a7-8b3e-0e9f79a34115','6004e686-8e75-4351-ac76-f640b6da80ad','1b6edf86-07e8-4363-8982-72809df2872e','PRW0000005'),
('fe3df490-576d-48f6-a297-7b2cddb5cae5','Anjing 11','f72e51f3-1461-48b6-abbe-3bd035144e3f','04c58d7a-98e9-48a7-8b3e-0e9f79a34115','6004e686-8e75-4351-ac76-f640b6da80ad','1b6edf86-07e8-4363-8982-72809df2872e','PRW0000001'),
('4ef85b4d-f910-46be-926a-7daeb62870d0','Anjing 12','f72e51f3-1461-48b6-abbe-3bd035144e3f','04c58d7a-98e9-48a7-8b3e-0e9f79a34115','6004e686-8e75-4351-ac76-f640b6da80ad','1b6edf86-07e8-4363-8982-72809df2872e','PRW0000002'),
('e615902b-70a6-4b49-8f94-c03a0708b4a3','Anjing 13','f72e51f3-1461-48b6-abbe-3bd035144e3f','04c58d7a-98e9-48a7-8b3e-0e9f79a34115','6004e686-8e75-4351-ac76-f640b6da80ad','1b6edf86-07e8-4363-8982-72809df2872e','PRW0000003'),
('23b6b785-8c4a-4653-9df4-6e0bf32a4792','Anjing 14','f72e51f3-1461-48b6-abbe-3bd035144e3f','04c58d7a-98e9-48a7-8b3e-0e9f79a34115','6004e686-8e75-4351-ac76-f640b6da80ad','1b6edf86-07e8-4363-8982-72809df2872e','PRW0000004'),
('f28683c0-7f1d-4192-b753-ae393765c859','Anjing 15','f72e51f3-1461-48b6-abbe-3bd035144e3f','04c58d7a-98e9-48a7-8b3e-0e9f79a34115','6004e686-8e75-4351-ac76-f640b6da80ad','1b6edf86-07e8-4363-8982-72809df2872e','PRW0000005'),
('72185e24-fb78-4412-86dc-2e71bc789b1d','Anjing 16','f72e51f3-1461-48b6-abbe-3bd035144e3f','04c58d7a-98e9-48a7-8b3e-0e9f79a34115','6004e686-8e75-4351-ac76-f640b6da80ad','1b6edf86-07e8-4363-8982-72809df2872e','PRW0000001'),
('04b7082d-26d0-42d9-b788-e75b189152ca','Anjing 17','f72e51f3-1461-48b6-abbe-3bd035144e3f','04c58d7a-98e9-48a7-8b3e-0e9f79a34115','6004e686-8e75-4351-ac76-f640b6da80ad','1b6edf86-07e8-4363-8982-72809df2872e','PRW0000002'),
('3d7e73d8-13ec-4c2e-8cf0-b6336a502ed5','Anjing 18','f72e51f3-1461-48b6-abbe-3bd035144e3f','04c58d7a-98e9-48a7-8b3e-0e9f79a34115','6004e686-8e75-4351-ac76-f640b6da80ad','1b6edf86-07e8-4363-8982-72809df2872e','PRW0000003'),
('ea175ff5-4da5-4000-8b5e-8a40dc17cb0d','Anjing 19','f72e51f3-1461-48b6-abbe-3bd035144e3f','04c58d7a-98e9-48a7-8b3e-0e9f79a34115','6004e686-8e75-4351-ac76-f640b6da80ad','1b6edf86-07e8-4363-8982-72809df2872e','PRW0000004'),
('e49b68e7-af32-44a0-b190-93803deef0fa','Anjing 20','f72e51f3-1461-48b6-abbe-3bd035144e3f','04c58d7a-98e9-48a7-8b3e-0e9f79a34115','6004e686-8e75-4351-ac76-f640b6da80ad','1b6edf86-07e8-4363-8982-72809df2872e','PRW0000005'),
('dcec9499-172e-43b3-aa48-3981aee98825','Anjing 1','f72e51f3-1461-48b6-abbe-3bd035144e3f','04c58d7a-98e9-48a7-8b3e-0e9f79a34115','6004e686-8e75-4351-ac76-f640b6da80ad','1b6edf86-07e8-4363-8982-72809df2872e','PRW0000005'),
('a1018e26-fcce-489e-8491-5017740323d5','Anjing 2','f72e51f3-1461-48b6-abbe-3bd035144e3f','04c58d7a-98e9-48a7-8b3e-0e9f79a34115','6004e686-8e75-4351-ac76-f640b6da80ad','1b6edf86-07e8-4363-8982-72809df2872e','PRW0000005'),
('f3a4a119-8209-467b-86fc-94a028a3ac65','Anjing 3','f72e51f3-1461-48b6-abbe-3bd035144e3f','04c58d7a-98e9-48a7-8b3e-0e9f79a34115','6004e686-8e75-4351-ac76-f640b6da80ad','1b6edf86-07e8-4363-8982-72809df2872e','PRW0000005'),
('b4d7bf57-1530-451a-8e3c-075b2b06e89e','Anjing 4','f72e51f3-1461-48b6-abbe-3bd035144e3f','04c58d7a-98e9-48a7-8b3e-0e9f79a34115','6004e686-8e75-4351-ac76-f640b6da80ad','1b6edf86-07e8-4363-8982-72809df2872e','PRW0000005'),
('86145138-cef1-4973-8157-4e3bb9a97f09','Anjing 5','f72e51f3-1461-48b6-abbe-3bd035144e3f','04c58d7a-98e9-48a7-8b3e-0e9f79a34115','6004e686-8e75-4351-ac76-f640b6da80ad','1b6edf86-07e8-4363-8982-72809df2872e','PRW0000004'),
('efb7808a-3e20-46a4-8576-3d1ab4e53400','Anjing 6','f72e51f3-1461-48b6-abbe-3bd035144e3f','04c58d7a-98e9-48a7-8b3e-0e9f79a34115','6004e686-8e75-4351-ac76-f640b6da80ad','1b6edf86-07e8-4363-8982-72809df2872e','PRW0000004'),
('f80333e0-8fac-4ea4-abdb-bda5d03d9c72','Anjing 7','f72e51f3-1461-48b6-abbe-3bd035144e3f','04c58d7a-98e9-48a7-8b3e-0e9f79a34115','6004e686-8e75-4351-ac76-f640b6da80ad','1b6edf86-07e8-4363-8982-72809df2872e','PRW0000004'),
('bb73717c-9d08-4add-a55c-29c3d74edf64','Anjing 8','f72e51f3-1461-48b6-abbe-3bd035144e3f','04c58d7a-98e9-48a7-8b3e-0e9f79a34115','6004e686-8e75-4351-ac76-f640b6da80ad','1b6edf86-07e8-4363-8982-72809df2872e','PRW0000004'),
('491fc472-0605-48c5-afbb-180ecce1d50a','Anjing 9','f72e51f3-1461-48b6-abbe-3bd035144e3f','04c58d7a-98e9-48a7-8b3e-0e9f79a34115','6004e686-8e75-4351-ac76-f640b6da80ad','1b6edf86-07e8-4363-8982-72809df2872e','PRW0000005'),
('b9a954a7-01fd-4be9-8b45-e928b006ede3','Anjing 10','f72e51f3-1461-48b6-abbe-3bd035144e3f','04c58d7a-98e9-48a7-8b3e-0e9f79a34115','6004e686-8e75-4351-ac76-f640b6da80ad','1b6edf86-07e8-4363-8982-72809df2872e','PRW0000004');

CREATE TABLE django_session (
    session_key varchar(40) PRIMARY KEY,
    session_data text NOT NULL,
    expire_date timestamp NOT NULL
);
CREATE INDEX django_session_expire_date_idx ON django_session(expire_date);

CREATE OR REPLACE FUNCTION prevent_duplicate_email()
RETURNS trigger AS $$
BEGIN
    IF EXISTS (SELECT 1 FROM "USER" WHERE email = NEW.email) THEN
        RAISE EXCEPTION 'Email % sudah terdaftar.', NEW.email
              USING ERRCODE = '23505';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_prevent_duplicate_email ON "USER";

CREATE TRIGGER trg_prevent_duplicate_email
BEFORE INSERT ON "USER"
FOR EACH ROW
EXECUTE FUNCTION prevent_duplicate_email();

-- Fungsi validasi timestamp akhir tidak boleh lebih kecil dari timestamp awal
CREATE OR REPLACE FUNCTION validate_timestamp_akhir()
RETURNS trigger AS
$$
BEGIN
    IF TG_OP = 'INSERT' THEN
        IF NEW.timestamp_akhir IS NOT NULL AND NEW.timestamp_akhir < NEW.timestamp_awal THEN
            RAISE EXCEPTION 'ERROR: Timestamp akhir kunjungan tidak boleh lebih awal dari timestamp awal saat INSERT.'
            USING ERRCODE = '23505';
        END IF;
        RETURN NEW;

    ELSIF TG_OP = 'UPDATE' THEN
        IF NEW.timestamp_akhir IS NOT NULL AND NEW.timestamp_akhir < NEW.timestamp_awal THEN
            RAISE EXCEPTION 'ERROR: Timestamp akhir kunjungan tidak boleh lebih awal dari timestamp awal saat UPDATE.'
            USING ERRCODE = '23505';
        END IF;
        RETURN NEW;
    END IF;
END;
$$
LANGUAGE plpgsql;


-- Trigger yang memanggil fungsi validasi sebelum INSERT atau UPDATE pada tabel kunjungan
CREATE TRIGGER trg_validate_timestamp_akhir
BEFORE INSERT OR UPDATE ON kunjungan
FOR EACH ROW EXECUTE FUNCTION validate_timestamp_akhir();

/* ──────────────────────────────────────────────────────────
   1.  FUNCTION
   ──────────────────────────────────────────────────────────*/
CREATE OR REPLACE FUNCTION validate_hewan_milik_klien()
RETURNS trigger
AS
$$
DECLARE
    nama_pemilik text;
BEGIN
    -----------------------------------------------------------------
    -- 1) Cari di INDIVIDU
    -----------------------------------------------------------------
    SELECT concat_ws(' ',
                     i.nama_depan,
                     coalesce(i.nama_tengah, ''),
                     i.nama_belakang)
      INTO nama_pemilik
      FROM individu i
     WHERE i.no_identitas_klien = NEW.no_identitas_klien;

    -----------------------------------------------------------------
    -- 2) Jika NULL, cari di PERUSAHAAN
    -----------------------------------------------------------------
    IF nama_pemilik IS NULL THEN
        SELECT p.nama_perusahaan
          INTO nama_pemilik
          FROM perusahaan p
         WHERE p.no_identitas_klien = NEW.no_identitas_klien;
    END IF;

    nama_pemilik := coalesce(nama_pemilik, '(tidak ditemukan)');

    -----------------------------------------------------------------
    -- 3) Validasi kepemilikan hewan
    -----------------------------------------------------------------
    IF NOT EXISTS (
        SELECT 1
          FROM hewan h
         WHERE h.no_identitas_klien = NEW.no_identitas_klien
           AND h.nama               = NEW.nama_hewan
    ) THEN
        RAISE EXCEPTION
          'ERROR: Hewan "%s" tidak terdaftar atas nama pemilik "%s".',
          NEW.nama_hewan, nama_pemilik
          USING ERRCODE = '23514';          -- check_violation
    END IF;

    RETURN NEW;
END;
$$
LANGUAGE plpgsql;


/* ──────────────────────────────────────────────────────────
   2.  TRIGGER
   ──────────────────────────────────────────────────────────*/
DROP TRIGGER IF EXISTS trg_validate_hewan_milik_klien ON kunjungan;

CREATE TRIGGER trg_validate_hewan_milik_klien
BEFORE INSERT OR UPDATE ON kunjungan
FOR EACH ROW
EXECUTE FUNCTION validate_hewan_milik_klien();

CREATE TRIGGER trg_validate_hewan_milik_klien_kunjungan_keperawatan
BEFORE INSERT OR UPDATE ON KUNJUNGAN_KEPERAWATAN
FOR EACH ROW
EXECUTE FUNCTION validate_hewan_milik_klien();


-- INSERT INTO "USER" (email, password, alamat, nomor_telepon) VALUES
-- ('jeremi.felix67@example.com', 'password123', 'Jl. Raya No.67', '099934567890');
-- INSERT INTO KLIEN (no_identitas, tanggal_registrasi, email) VALUES
-- ('fff96c9e-3b3a-42d2-a692-532cb843e69e', '2025-01-01', 'jeremi.felix67@example.com');
-- INSERT INTO PERUSAHAAN (no_identitas_klien, nama_perusahaan) 
-- VALUES
-- ('fff96c9e-3b3a-42d2-a692-532cb843e69e', 'Perusahaan Z');
-- INSERT INTO KUNJUNGAN (id_kunjungan,nama_hewan,no_identitas_klien,no_front_desk,no_perawat_hewan,no_dokter_hewan,kode_vaksin,tipe_kunjungan,timestamp_awal,timestamp_akhir)
-- VALUES
-- ('dcec9499-172e-43b3-aa48-3981aee98825','Anjing 1','fff96c9e-3b3a-42d2-a692-532cb843e69e','04c58d7a-98e9-48a7-8b3e-0e9f79a34115','6004e686-8e75-4351-ac76-f640b6da80ad','1b6edf86-07e8-4363-8982-72809df2872e','VKS001','Darurat','2025-04-24 11:00:00','2025-04-24 13:00:00');
-- INSERT INTO HEWAN(nama, no_identitas_klien,tanggal_lahir,id_jenis,url_foto) 
-- VALUES
-- ('Anjing 1', 'fff96c9e-3b3a-42d2-a692-532cb843e69e','2025-01-01','53f6ac39-e535-4d3f-8ab3-b663d69a4572','https://www.google.com/fotoanjing');