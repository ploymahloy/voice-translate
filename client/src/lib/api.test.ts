import { afterEach, describe, expect, it, vi } from 'vitest';

import {
  buildTranslateUrl,
  formatFetchError,
  parseApiError,
  resolveApiBaseUrl,
  translateAudio,
} from './api';

describe('resolveApiBaseUrl', () => {
  it('returns empty string when env is unset', () => {
    expect(resolveApiBaseUrl({})).toBe('');
  });

  it('strips trailing slash from PUBLIC_API_BASE_URL', () => {
    expect(
      resolveApiBaseUrl({ PUBLIC_API_BASE_URL: 'https://api.example.com/' }),
    ).toBe('https://api.example.com');
  });
});

describe('buildTranslateUrl', () => {
  it('uses dev proxy path when base is empty', () => {
    expect(buildTranslateUrl('')).toBe('/translate');
  });

  it('joins base and translate path', () => {
    expect(buildTranslateUrl('https://api.example.com')).toBe(
      'https://api.example.com/translate',
    );
  });
});

describe('parseApiError', () => {
  it('extracts detail from FastAPI JSON body', async () => {
    const response = new Response(JSON.stringify({ detail: 'Bad language' }), {
      status: 422,
      headers: { 'content-type': 'application/json' },
    });
    await expect(parseApiError(response)).resolves.toBe('Bad language');
  });

  it('falls back when body is not JSON', async () => {
    const response = new Response('upstream error', {
      status: 503,
      headers: { 'content-type': 'text/plain' },
    });
    await expect(parseApiError(response)).resolves.toBe('Request failed (503)');
  });
});

describe('formatFetchError', () => {
  it('suggests starting the API on network failure', () => {
    expect(formatFetchError(new TypeError('Failed to fetch'), '/translate')).toContain(
      'make run',
    );
  });
});

describe('translateAudio', () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('posts multipart form and returns blob on success', async () => {
    const audioBytes = new Uint8Array([0xff, 0xfb]);
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(audioBytes, {
        status: 200,
        headers: { 'content-type': 'audio/mpeg' },
      }),
    );
    vi.stubGlobal('fetch', fetchMock);

    const file = new File([audioBytes], 'clip.wav', { type: 'audio/wav' });
    const result = await translateAudio(file, 'spa', { env: {} });

    expect(fetchMock).toHaveBeenCalledOnce();
    const [url, init] = fetchMock.mock.calls[0] as [string, RequestInit];
    expect(url).toBe('/translate');
    expect(init.method).toBe('POST');
    expect(init.body).toBeInstanceOf(FormData);
    const form = init.body as FormData;
    expect(form.get('target_language')).toBe('spa');
    expect(result.contentType).toBe('audio/mpeg');
    expect(result.blob).toBeInstanceOf(Blob);
  });

  it('wraps network failures with a helpful message', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockRejectedValue(new TypeError('Failed to fetch')),
    );

    const file = new File([new Uint8Array(1)], 'clip.wav', { type: 'audio/wav' });
    await expect(translateAudio(file, 'en', { env: {} })).rejects.toThrow(/make run/);
  });

  it('throws with parsed detail on error status', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(
        new Response(JSON.stringify({ detail: 'Invalid or missing API key' }), {
          status: 401,
          headers: { 'content-type': 'application/json' },
        }),
      ),
    );

    const file = new File([new Uint8Array(1)], 'clip.wav', { type: 'audio/wav' });
    await expect(translateAudio(file, 'en', { env: {} })).rejects.toThrow(
      'Invalid or missing API key',
    );
  });

  it('sends X-API-Key when apiKey option is set', async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(new Uint8Array([1]), {
        status: 200,
        headers: { 'content-type': 'audio/wav' },
      }),
    );
    vi.stubGlobal('fetch', fetchMock);

    const file = new File([new Uint8Array(1)], 'clip.wav', { type: 'audio/wav' });
    await translateAudio(file, 'fr', { apiKey: 'secret', env: {} });

    const [, init] = fetchMock.mock.calls[0] as [string, RequestInit];
    expect((init.headers as Record<string, string>)['X-API-Key']).toBe('secret');
  });
});
