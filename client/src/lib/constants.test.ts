import { describe, expect, it } from 'vitest';

import languageEntries from '../../../shared/languages.json';

import { ALLOWED_AUDIO_EXTENSIONS, LANGUAGE_LABELS, SUPPORTED_LANGUAGES } from './constants';

describe('constants', () => {
  it('matches shared languages.json', () => {
    const expectedCodes = (languageEntries as { code: string }[])
      .map((entry) => entry.code)
      .sort();
    expect([...SUPPORTED_LANGUAGES].sort()).toEqual(expectedCodes);
    expect(SUPPORTED_LANGUAGES).toHaveLength(74);
  });

  it('has a label for every supported language', () => {
    for (const code of SUPPORTED_LANGUAGES) {
      const entry = (languageEntries as { code: string; label: string }[]).find(
        (e) => e.code === code,
      );
      expect(LANGUAGE_LABELS[code]).toBe(entry?.label);
    }
  });

  it('exposes allowed audio extensions for the file input', () => {
    expect([...ALLOWED_AUDIO_EXTENSIONS].sort()).toEqual(['.mp3', '.wav']);
  });
});
