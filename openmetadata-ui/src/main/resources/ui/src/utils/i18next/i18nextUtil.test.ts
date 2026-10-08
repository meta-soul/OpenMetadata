/*
 *  Copyright 2022 Collate.
 *  Licensed under the Apache License, Version 2.0 (the "License");
 *  you may not use this file except in compliance with the License.
 *  You may obtain a copy of the License at
 *  http://www.apache.org/licenses/LICENSE-2.0
 *  Unless required by applicable law or agreed to in writing, software
 *  distributed under the License is distributed on an "AS IS" BASIS,
 *  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *  See the License for the specific language governing permissions and
 *  limitations under the License.
 */
import { getInitOptions, resolveLanguageFromQuery } from './i18nextUtil';
import { SupportedLocales } from './LocalUtil.interface';

describe('getInitOptions', () => {
  it('does not set lng so LanguageDetector can read querystring', () => {
    expect(getInitOptions().lng).toBeUndefined();
  });
});

describe('resolveLanguageFromQuery', () => {
  it('resolves canonical locales from lng', () => {
    expect(resolveLanguageFromQuery('?lng=en-US')).toBe(
      SupportedLocales.English
    );
    expect(resolveLanguageFromQuery('?lng=zh-CN')).toBe(
      SupportedLocales.简体中文
    );
  });

  it('maps short language codes', () => {
    expect(resolveLanguageFromQuery('?lng=en')).toBe(SupportedLocales.English);
    expect(resolveLanguageFromQuery('?lng=EN')).toBe(SupportedLocales.English);
    expect(resolveLanguageFromQuery('?lng=zh')).toBe(SupportedLocales.简体中文);
    expect(resolveLanguageFromQuery('?lng=ZH')).toBe(SupportedLocales.简体中文);
    expect(resolveLanguageFromQuery('?lng=en-us')).toBe(
      SupportedLocales.English
    );
  });

  it('returns undefined when lng is missing or unsupported', () => {
    expect(resolveLanguageFromQuery('')).toBeUndefined();
    expect(resolveLanguageFromQuery('?foo=bar')).toBeUndefined();
    expect(resolveLanguageFromQuery('?lng=')).toBeUndefined();
    expect(resolveLanguageFromQuery('?lng=not-a-locale')).toBeUndefined();
  });
});
