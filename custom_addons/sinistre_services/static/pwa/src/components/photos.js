/**
 * photos.js — Capture, compression et upload des photos
 * Photos AVANT (obligatoires pour démarrer) et APRÈS (pour clôturer)
 */

window.Photos = (() => {
    let _currentMissionId = null;
    let _pendingType = null;        // 'avant' | 'apres'
    let _localPhotos = [];          // photos en mémoire avant upload

    const cameraInput  = document.getElementById('cameraInput');
    const galleryInput = document.getElementById('galleryInput');

    /* ── Capture photo ── */
    function capture(type) {
        _pendingType = type;

        // iOS : la caméra et galerie sont le même input
        // On présente un choix simple
        if (window.innerWidth < 768) {
            cameraInput.click();   // déclenche la caméra sur mobile
        } else {
            galleryInput.click();  // sur desktop = galerie
        }
    }

    /* ── Traitement après sélection ── */
    async function handleFile(file, type) {
        if (!file || !file.type.startsWith('image/')) {
            Toast.show('Format invalide — JPEG, PNG ou WebP uniquement', 'error');
            return;
        }

        Toast.show('🖼 Traitement de la photo…');

        try {
            // Compression
            const compressed = await compressImage(file, CONFIG.PHOTO_MAX_SIZE_KB, CONFIG.PHOTO_QUALITY);
            const base64 = compressed.split(',')[1]; // retirer le data:url prefix

            // Stocker localement
            _localPhotos.push({ type, base64, preview: compressed, uploaded: false });

            // Afficher immédiatement dans l'UI
            MissionDetail.addPhotoThumb({ type, preview: compressed });

            // Upload en ligne ou en queue
            const missionId = _currentMissionId;
            const result = await Offline.tryOrQueue(
                'UPLOAD_PHOTO',
                () => API.uploadPhoto(missionId, type, base64),
                { missionId, photoType: type, base64 }
            );

            if (!result?.queued) {
                Toast.show(`📸 Photo ${type} enregistrée`, 'success');
                MissionDetail.refreshPhotoCounts();
                if (result.photo_id) {
                    MissionDetail.addPhotoThumb({ type, preview: compressed, id: result.photo_id });
                }
            }
        } catch (err) {
            Toast.show('Erreur upload photo: ' + err.message, 'error');
        }
    }

    /* ── Compression canvas ── */
    function compressImage(file, maxKB, quality) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = (e) => {
                const img = new Image();
                img.onload = () => {
                    const canvas = document.createElement('canvas');
                    let { width, height } = img;

                    // Limiter à 1600px max
                    const MAX_DIM = 1600;
                    if (width > MAX_DIM || height > MAX_DIM) {
                        if (width > height) {
                            height = Math.round((height * MAX_DIM) / width);
                            width = MAX_DIM;
                        } else {
                            width = Math.round((width * MAX_DIM) / height);
                            height = MAX_DIM;
                        }
                    }

                    canvas.width = width;
                    canvas.height = height;
                    const ctx = canvas.getContext('2d');
                    ctx.drawImage(img, 0, 0, width, height);

                    // Compresser itérativement jusqu'au target size
                    let q = quality;
                    let dataUrl = canvas.toDataURL('image/jpeg', q);
                    while (dataUrl.length / 1024 > maxKB * 1.37 && q > 0.3) {
                        q -= 0.05;
                        dataUrl = canvas.toDataURL('image/jpeg', q);
                    }

                    resolve(dataUrl);
                };
                img.onerror = reject;
                img.src = e.target.result;
            };
            reader.onerror = reject;
            reader.readAsDataURL(file);
        });
    }

    /* ── Event listeners sur inputs file ── */
    cameraInput.addEventListener('change', (e) => {
        handleFile(e.target.files[0], _pendingType);
        cameraInput.value = '';
    });
    galleryInput.addEventListener('change', (e) => {
        handleFile(e.target.files[0], _pendingType);
        galleryInput.value = '';
    });

    /* ── API publique ── */
    return {
        setMission(id) { _currentMissionId = id; _localPhotos = []; },
        capture,
        getLocalPhotos: () => _localPhotos,
        clearLocal: () => { _localPhotos = []; },
        compressImage,
    };
})();
