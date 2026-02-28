/**
 * File upload utilities — validation, encoding, and MIME detection.
 *
 * Used by ChatInput to process files before sending to the backend.
 * All files are base64-encoded client-side and sent as JSON.
 */

// ── Allowed types ──────────────────────────────────────────────

export const ALLOWED_IMAGE_TYPES = [
  'image/jpeg',
  'image/png',
  'image/gif',
  'image/webp',
] as const;

export const ALLOWED_DOC_TYPES = [
  'application/pdf',
  'text/plain',
  'text/csv',
  'text/markdown',
] as const;

export const ALL_ALLOWED_TYPES: readonly string[] = [
  ...ALLOWED_IMAGE_TYPES,
  ...ALLOWED_DOC_TYPES,
];

/** Accept string for <input type="file"> */
export const ALLOWED_EXTENSIONS = '.jpg,.jpeg,.png,.gif,.webp,.pdf,.txt,.csv,.md';

// ── Limits ─────────────────────────────────────────────────────

export const MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024; // 10 MB
export const MAX_FILES_PER_MESSAGE = 5;

// ── Helpers ────────────────────────────────────────────────────

const EXT_TO_MIME: Record<string, string> = {
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.png': 'image/png',
  '.gif': 'image/gif',
  '.webp': 'image/webp',
  '.pdf': 'application/pdf',
  '.txt': 'text/plain',
  '.csv': 'text/csv',
  '.md': 'text/markdown',
};

export function isImageType(contentType: string): boolean {
  return (ALLOWED_IMAGE_TYPES as readonly string[]).includes(contentType);
}

/**
 * Resolve MIME type from File object, falling back to extension lookup
 * when the browser doesn't report a type (common for .md and .csv).
 */
export function getMimeType(file: File): string {
  if (file.type && ALL_ALLOWED_TYPES.includes(file.type)) return file.type;
  const ext = '.' + (file.name.split('.').pop()?.toLowerCase() ?? '');
  return EXT_TO_MIME[ext] ?? 'application/octet-stream';
}

// ── Validation ─────────────────────────────────────────────────

export interface FileValidationError {
  filename: string;
  error: string;
}

export function validateFile(file: File): FileValidationError | null {
  const mime = getMimeType(file);
  if (!ALL_ALLOWED_TYPES.includes(mime)) {
    return {
      filename: file.name,
      error: `Unsupported file type: ${file.type || file.name.split('.').pop()}`,
    };
  }
  if (file.size > MAX_FILE_SIZE_BYTES) {
    return {
      filename: file.name,
      error: `File exceeds 10 MB limit (${(file.size / 1024 / 1024).toFixed(1)} MB)`,
    };
  }
  return null;
}

// ── Base64 encoding ────────────────────────────────────────────

/**
 * Read a File as base64 (without the `data:...;base64,` prefix).
 */
export function readFileAsBase64(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      const result = reader.result as string;
      // Strip the data URI prefix: "data:image/png;base64,iVBOR..." → "iVBOR..."
      const base64 = result.split(',')[1] ?? '';
      resolve(base64);
    };
    reader.onerror = () => reject(new Error(`Failed to read ${file.name}`));
    reader.readAsDataURL(file);
  });
}

/** Human-readable file size. */
export function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}
