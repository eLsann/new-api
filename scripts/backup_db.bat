@echo off
echo ===================================================
echo      Backup Database Lokal (Absensi)
echo ===================================================
echo.
echo Pastikan Laragon/XAMPP/MySQL lokal Anda SUDAH MENYALA.
echo.

set /p MYSQL_USER="Masukkan Username MySQL Lokal (Default: root): " || set MYSQL_USER=root
set /p MYSQL_PASS="Masukkan Password MySQL Lokal (Default: kosong): " || set MYSQL_PASS=
set /p DB_NAME="Masukkan Nama Database (Default: absensi): " || set DB_NAME=absensi

echo.
echo Sedang melakukan backup '$DB_NAME' ke 'init.sql'...

:: Cek apakah mysqldump ada di PATH
where mysqldump >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] 'mysqldump' tidak ditemukan. 
    echo Pastikan folder bin MySQL (ex: C:\laragon\bin\mysql\mysql-8.x\bin) sudah masuk Environment Variable PATH.
    echo Atau jalankan script ini di Terminal Laragon.
    pause
    exit /b
)

:: Prepare password arg only if not empty
if "%MYSQL_PASS%"=="" (
    mysqldump -u %MYSQL_USER% %DB_NAME% > init.sql
) else (
    mysqldump -u %MYSQL_USER% -p%MYSQL_PASS% %DB_NAME% > init.sql
)

if %errorlevel% equ 0 (
    echo.
    echo [SUKSES] File backup telah tersimpan sebagai: init.sql
    echo.
    echo Pindahkan file ini ke folder 'mysql_init' jika ingin di-load otomatis oleh Docker.
) else (
    echo.
    echo [GAGAL] Terjadi kesalahan saat backup. Cek kredensial Anda.
)

pause
