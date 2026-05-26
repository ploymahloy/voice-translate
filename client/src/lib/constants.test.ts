import { describe, expect, it } from 'vitest';

import { ALLOWED_AUDIO_EXTENSIONS, SUPPORTED_LANGUAGES } from './constants';

describe('constants', () => {
  it('matches backend supported languages', () => {
    expect([...SUPPORTED_LANGUAGES].sort()).toEqual(['de', 'en', 'es', 'fr']);
  });

  it('matches backend allowed audio extensions', () => {
    expect([...ALLOWED_AUDIO_EXTENSIONS].sort()).toEqual([
      '.m4a',
      '.mp3',
      '.ogg',
      '.wav',
      '.webm',
    ]);
  });
});
