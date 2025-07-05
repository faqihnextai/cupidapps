// static/js/script.js

/**
 * File JavaScript ini menangani interaktivitas di sisi klien untuk proyek "Instagram Cupit Series".
 * Fokus utama adalah navigasi form multi-step dan validasi input sederhana.
 */

document.addEventListener('DOMContentLoaded', function() {
    // === Bagian untuk Admin: Generate OTP ===
    const generateOtpBtn = document.getElementById('generate-otp-btn');
    const otpDisplay = document.getElementById('otp-display');

    if (generateOtpBtn && otpDisplay) {
        generateOtpBtn.addEventListener('click', function() {
            // Mengirim permintaan ke backend untuk menghasilkan OTP
            fetch('/admin/generate_otp', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.otp_code) {
                    otpDisplay.textContent = data.otp_code;
                    // Opsional: Tampilkan pesan sukses atau waktu kedaluwarsa
                } else if (data.error) {
                    otpDisplay.textContent = 'Error: ' + data.error;
                }
            })
            .catch(error => {
                console.error('Error fetching OTP:', error);
                otpDisplay.textContent = 'Gagal menghasilkan OTP.';
            });
        });
    }

    // === Bagian untuk User: Form Multi-Step ===
    const formSteps = document.querySelectorAll('.form-step'); // Setiap div langkah form memiliki kelas 'form-step'
    const nextButtons = document.querySelectorAll('.next-step');
    const prevButtons = document.querySelectorAll('.prev-step');
    const formContainer = document.querySelector('.form-container'); // Kontainer utama form jika ada

    let currentStep = 0; // Mulai dari langkah pertama (indeks 0)

    /**
     * Menampilkan langkah form yang sesuai dan menyembunyikan yang lain.
     * Menggunakan kelas 'hidden' dari CSS untuk menyembunyikan/menampilkan.
     */
    function showStep(stepIndex) {
        formSteps.forEach((step, index) => {
            if (index === stepIndex) {
                step.classList.remove('hidden', 'fade-out'); // Pastikan tidak ada kelas tersembunyi/fade-out
                step.classList.add('fade-in'); // Tambahkan animasi fade-in
            } else {
                step.classList.add('hidden'); // Sembunyikan langkah lainnya
                step.classList.remove('fade-in', 'fade-out');
            }
        });
        currentStep = stepIndex;
        // Opsional: Scroll ke atas halaman saat pindah langkah
        if (formContainer) {
            formContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
        } else {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }
    }

    /**
     * Melakukan validasi sederhana untuk input username Instagram.
     * @param {string} username - Username yang akan divalidasi.
     * @returns {boolean} - True jika valid, false jika tidak.
     */
    function validateInstagramUsername(username) {
        // Regex sederhana: hanya huruf, angka, titik, dan underscore.
        // Tidak boleh dimulai dengan titik atau underscore.
        // Panjang minimal 1 karakter.
        const regex = /^(?!.*\.\.)(?!.*\._)(?!.*_\.)(?!.*__)(?!.*\.$)(?!.*_$)[a-zA-Z0-9._]{1,30}$/;
        return regex.test(username);
    }

    /**
     * Memvalidasi input di langkah form saat ini sebelum berpindah ke langkah berikutnya.
     * @param {number} stepIndex - Indeks langkah form saat ini.
     * @returns {boolean} - True jika validasi sukses, false jika tidak.
     */
    function validateCurrentStep(stepIndex) {
        let isValid = true;
        let errorMessage = '';

        const currentForm = formSteps[stepIndex];

        if (stepIndex === 0) { // Validasi untuk form_step1 (username IG)
            const usernameInput = currentForm.querySelector('input[name="instagram_username"]');
            if (usernameInput) {
                const username = usernameInput.value.trim();
                if (username === '') {
                    errorMessage = 'Username Instagram tidak boleh kosong.';
                    isValid = false;
                } else if (!validateInstagramUsername(username)) {
                    errorMessage = 'Format username Instagram tidak valid. Contoh: user_name123';
                    isValid = false;
                }
            }
        } else if (stepIndex === 1) { // Validasi untuk form_step2 (gender)
            const genderRadios = currentForm.querySelectorAll('input[name="gender"]');
            let genderSelected = false;
            genderRadios.forEach(radio => {
                if (radio.checked) {
                    genderSelected = true;
                }
            });
            if (!genderSelected) {
                errorMessage = 'Silakan pilih gender Anda.';
                isValid = false;
            }
        } else if (stepIndex === 2) { // Validasi untuk form_step3 (age_range)
            const ageRangeSelect = currentForm.querySelector('select[name="age_range"]');
            if (ageRangeSelect && ageRangeSelect.value === '') {
                errorMessage = 'Silakan pilih rentang usia Anda.';
                isValid = false;
            }
        }

        const errorDisplay = currentForm.querySelector('.error-message');
        if (errorDisplay) {
            if (!isValid) {
                errorDisplay.textContent = errorMessage;
                errorDisplay.classList.remove('hidden');
            } else {
                errorDisplay.classList.add('hidden');
                errorDisplay.textContent = '';
            }
        }

        return isValid;
    }


    // Menambahkan event listener untuk tombol "Lanjut"
    nextButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Pastikan ini hanya dipanggil pada tombol di langkah form
            const parentStep = this.closest('.form-step');
            const stepIndex = Array.from(formSteps).indexOf(parentStep);

            if (validateCurrentStep(stepIndex)) {
                // Jika validasi sukses, pindah ke langkah berikutnya
                if (stepIndex < formSteps.length - 1) {
                    showStep(stepIndex + 1);
                }
                // Jika ini langkah terakhir, biarkan form disubmit oleh Flask
            }
        });
    });

    // Menambahkan event listener untuk tombol "Kembali"
    prevButtons.forEach(button => {
        button.addEventListener('click', function() {
            const parentStep = this.closest('.form-step');
            const stepIndex = Array.from(formSteps).indexOf(parentStep);

            if (stepIndex > 0) {
                showStep(stepIndex - 1);
            }
        });
    });

    // Inisialisasi: Tampilkan langkah pertama saat halaman dimuat
    if (formSteps.length > 0) {
        showStep(0);
    }
});

