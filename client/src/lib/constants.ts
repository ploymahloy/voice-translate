export const SUPPORTED_LANGUAGES = ['en', 'es', 'fr', 'de'] as const;

export type SupportedLanguage = (typeof SUPPORTED_LANGUAGES)[number];

export const LANGUAGE_LABELS: Record<SupportedLanguage, string> = {
  en: 'English',
  es: 'Spanish',
  fr: 'French',
  de: 'German',
};

export const ALLOWED_AUDIO_EXTENSIONS = [
  '.wav',
  '.mp3',
  '.m4a',
  '.ogg',
  '.webm',
] as const;

export const ACCEPT_AUDIO_TYPES = ALLOWED_AUDIO_EXTENSIONS.map(
  (ext) => `audio/*${ext.slice(1)}`,
).join(',');

export const DEFAULT_MAX_UPLOAD_BYTES = 25 * 1024 * 1024;

export const MAX_UPLOAD_LABEL = '25 MB';
