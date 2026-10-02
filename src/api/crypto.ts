export type EncryptedPayload = {
  algorithm: "RSA-OAEP-256+A256GCM";
  ciphertext: string;
  encryptedKey: string;
  iv: string;
};

function base64(bytes: ArrayBuffer | Uint8Array) {
  const values = new Uint8Array(bytes);
  let binary = "";
  values.forEach((value) => (binary += String.fromCharCode(value)));
  return btoa(binary);
}

function pemToArrayBuffer(pem: string) {
  const normalized = pem
    .replace(/\\n/g, "\n")
    .replace(/-----BEGIN PUBLIC KEY-----|-----END PUBLIC KEY-----|\s/g, "");
  const binary = atob(normalized);
  const bytes = Uint8Array.from(binary, (character) => character.charCodeAt(0));
  return bytes.buffer;
}

/**
 * Encrypts JSON with a one-time AES-GCM key, then encrypts that key with the
 * API's RSA public key. The backend decrypts encryptedKey first, then uses iv
 * and ciphertext to recover the JSON.
 */
export async function encryptForApi(payload: unknown): Promise<EncryptedPayload> {
  const pem = import.meta.env.VITE_AUTH_PUBLIC_KEY;
  if (!pem) {
    throw new Error(
      "Login encryption is not configured. Set VITE_AUTH_PUBLIC_KEY to the backend RSA public key.",
    );
  }

  const publicKey = await crypto.subtle.importKey(
    "spki",
    pemToArrayBuffer(pem),
    { name: "RSA-OAEP", hash: "SHA-256" },
    false,
    ["encrypt"],
  );
  const sessionKey = await crypto.subtle.generateKey(
    { name: "AES-GCM", length: 256 },
    true,
    ["encrypt"],
  );
  const iv = crypto.getRandomValues(new Uint8Array(12));
  const plaintext = new TextEncoder().encode(JSON.stringify(payload));
  const ciphertext = await crypto.subtle.encrypt(
    { name: "AES-GCM", iv },
    sessionKey,
    plaintext,
  );
  const rawKey = await crypto.subtle.exportKey("raw", sessionKey);
  const encryptedKey = await crypto.subtle.encrypt(
    { name: "RSA-OAEP" },
    publicKey,
    rawKey,
  );
  return {
    algorithm: "RSA-OAEP-256+A256GCM",
    ciphertext: base64(ciphertext),
    encryptedKey: base64(encryptedKey),
    iv: base64(iv),
  };
}
