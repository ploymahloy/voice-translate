import languageEntries from '../../../shared/languages.json';

type LanguageEntry = { code: string; label: string };

const entries = languageEntries as LanguageEntry[];

export const SUPPORTED_LANGUAGES = entries.map((entry) => entry.code);

export type SupportedLanguage = string;

export const LANGUAGE_LABELS: Record<string, string> = Object.fromEntries(
	entries.map((entry) => [entry.code, entry.label]),
);

export const ALLOWED_AUDIO_EXTENSIONS = ['.wav', '.mp3'] as const;

export const ACCEPT_AUDIO_TYPES = ALLOWED_AUDIO_EXTENSIONS.map(ext => `audio/*${ext.slice(1)}`).join(',');

export const DEFAULT_MAX_UPLOAD_BYTES = 25 * 1024 * 1024;

export const CONTACT_EMAIL =
	import.meta.env.PUBLIC_CONTACT_EMAIL?.trim() || 'patrick.mahloy@gmail.com';
