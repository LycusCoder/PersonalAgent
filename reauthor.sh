#!/bin/sh

# =========================================================================
# WARNING: LAKUKAN BACKUP REPO TERLEBIH DAHULU SEBELUM MENJALANKAN SCRIPT INI!
# Script ini akan menimpa seluruh history Git, dan kamu harus FORCE PUSH.
# =========================================================================

# --- 1. Konfigurasi Nama dan Email Baru ---
# Ganti ini dengan Nama dan Email yang kamu mau (misalnya nama kamu)
NEW_NAME="LycusCoder"
NEW_EMAIL="richard.huawei08@gmail.com"

echo "➡️ Akan mengganti semua kontributor menjadi: $NEW_NAME <$NEW_EMAIL>"
echo "Memulai proses rewriting history..."

# --- 2. Proses Filter-Branch ---
# --env-filter akan mengubah environment variables GIT_AUTHOR_NAME/EMAIL
# dan GIT_COMMITTER_NAME/EMAIL untuk SETIAP commit.
git filter-branch --env-filter "
    # Set Author Info
    export GIT_AUTHOR_NAME='$NEW_NAME'
    export GIT_AUTHOR_EMAIL='$NEW_EMAIL'
    
    # Set Committer Info (biasanya sama dengan Author)
    export GIT_COMMITTER_NAME='$NEW_NAME'
    export GIT_COMMITTER_EMAIL='$NEW_EMAIL'
" --tag-name-filter cat -- --branches --tags

# --- 3. Pembersihan (Cleanup) ---
# Menghapus refs/original/ yang dibuat oleh filter-branch untuk menghemat ruang
echo "Membersihkan metadata lama dan merepack objek..."
git for-each-ref --format="delete %(refname)" refs/original | git update-ref --stdin
git reflog expire --expire=now --all
git gc --prune=now
git repack -Ad

echo "✅ Proses selesai! Semua history sudah diubah secara lokal."

# --- 4. Langkah Akhir (WAJIB) ---
echo ""
echo "========================================================"
echo "⚠️ LANGKAH TERAKHIR (DANGER ZONE):"
echo "1. Cek hasilnya: git log -5"
echo "2. Jika sudah benar, paksa push ke remote:"
echo "   git push --force --all"
echo "   git push --force --tags"
echo "========================================================"