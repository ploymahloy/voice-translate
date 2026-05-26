export type ApiEnv = {
  DEV?: boolean;
  PUBLIC_API_BASE_URL?: string;
};

export type TranslateOptions = {
  apiKey?: string;
  signal?: AbortSignal;
  env?: ApiEnv;
};

export type TranslateResult = {
  blob: Blob;
  contentType: string;
};

export function resolveApiBaseUrl(env: ApiEnv = import.meta.env): string {
  const raw = env.PUBLIC_API_BASE_URL?.trim() ?? '';
  return raw.replace(/\/$/, '');
}

export function buildTranslateUrl(base: string): string {
  const normalized = base.replace(/\/$/, '');
  if (!normalized) {
    return '/api/translate';
  }
  return `${normalized}/translate`;
}

export async function parseApiError(response: Response): Promise<string> {
  const contentType = response.headers.get('content-type') ?? '';
  if (contentType.includes('application/json')) {
    try {
      const body = (await response.json()) as { detail?: unknown };
      const detail = body.detail;
      if (typeof detail === 'string') {
        return detail;
      }
      if (Array.isArray(detail)) {
        return detail.map((item) => String(item)).join(' ');
      }
    } catch {
      // fall through to generic message
    }
  }
  return `Request failed (${response.status})`;
}

export function formatFetchError(error: unknown, apiUrl: string): string {
  if (error instanceof Error && error.name === 'AbortError') {
    return 'Translation cancelled.';
  }
  if (
    error instanceof TypeError &&
    (error.message === 'Failed to fetch' || error.message.includes('NetworkError'))
  ) {
    return `Cannot reach the API at ${apiUrl}. Start the server with "make run" (port 8000) and keep the client dev server running.`;
  }
  if (error instanceof Error) {
    return error.message;
  }
  return 'Translation failed.';
}

export async function translateAudio(
  file: File,
  targetLanguage: string,
  options?: TranslateOptions,
): Promise<TranslateResult> {
  const env = options?.env ?? import.meta.env;
  const url = buildTranslateUrl(resolveApiBaseUrl(env));
  const formData = new FormData();
  formData.append('target_language', targetLanguage);
  formData.append('source_audio', file, file.name);

  const headers: Record<string, string> = {};
  if (options?.apiKey) {
    headers['X-API-Key'] = options.apiKey;
  }

  let response: Response;
  try {
    response = await fetch(url, {
      method: 'POST',
      body: formData,
      headers,
      signal: options?.signal,
    });
  } catch (error) {
    throw new Error(formatFetchError(error, url));
  }

  if (!response.ok) {
    throw new Error(await parseApiError(response));
  }

  const blob = await response.blob();
  const contentType =
    response.headers.get('content-type') ?? 'application/octet-stream';
  return { blob, contentType };
}

export function resolveDevApiKey(env: ApiEnv = import.meta.env): string | undefined {
  if (!env.DEV) {
    return undefined;
  }
  const key = (env as ApiEnv & { PUBLIC_DEV_API_KEY?: string }).PUBLIC_DEV_API_KEY;
  const trimmed = key?.trim();
  return trimmed || undefined;
}
