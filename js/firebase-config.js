// Configuração do Firebase - KINK Platform
const firebaseConfig = {
  apiKey: "AIzaSyCcm1K246-uRdxJGNMwy2ak0uqsPCeFoGg",
  authDomain: "kink-is-not-kahoot.firebaseapp.com",
  projectId: "kink-is-not-kahoot",
  storageBucket: "kink-is-not-kahoot.firebasestorage.app",
  messagingSenderId: "1035302376218",
  appId: "1:1035302376218:web:9b1b6a0fb8eb53ccdcd2a3",
  measurementId: "G-WM76QF6DV1"
};

// Verificar se Firebase já foi inicializado
if (!firebase.apps.length) {
    firebase.initializeApp(firebaseConfig);
    console.log("🔥 Firebase inicializado com sucesso!");
} else {
    console.log("🔥 Firebase já estava inicializado");
}

// Inicializar serviços
const auth = firebase.auth();
const db = firebase.firestore();
const storage = firebase.storage();

// Configuração de cache do Firestore
db.settings({
    cacheSizeBytes: firebase.firestore.CACHE_SIZE_UNLIMITED
});

// Habilitar persistência offline
db.enablePersistence()
    .catch((err) => {
        console.log("⚠️ Persistência offline não disponível:", err);
    });

// Utilitário para gerar código de sala
function generateRoomCode() {
    const prefixes = ['K', 'NK', 'INK'];
    const randomPart = Math.random().toString(36).substring(2, 6).toUpperCase();
    const prefix = prefixes[Math.floor(Math.random() * prefixes.length)];
    return (prefix + randomPart).substring(0, 6);
}

// Utilitário para validar código
function isValidRoomCode(code) {
    return /^[A-Z0-9]{6}$/.test(code);
}

// Exportar para uso global
window.firebase = firebase;
window.auth = auth;
window.db = db;
window.storage = storage;
window.generateRoomCode = generateRoomCode;
window.isValidRoomCode = isValidRoomCode;

// Verificar se os serviços foram inicializados
console.log("✅ Serviços Firebase inicializados:");
console.log("   Auth:", !!auth);
console.log("   Firestore:", !!db);
console.log("   Storage:", !!storage);

// Console branding
console.log("%c🔥 KINK is not Kahoot 🔥", "color: #ff6b6b; font-size: 16px; font-weight: bold;");
console.log("%cThe rebellious quiz platform is ready!", "color: #4ecdc4; font-size: 12px;");