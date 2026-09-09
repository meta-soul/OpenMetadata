/*
 *  Copyright 2026 Collate.
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

import { getBasePath } from '../utils/HistoryUtils';

/**
 * LakeInsight offline branding assets under public/assets/img/lakeinsight.
 * Stored paths are app-root relative (no deployment basePath); callers must
 * resolve them with {@link resolveBrandingAssetUrl} for subpath installs.
 */
export const LAKEINSIGHT_BRANDING = {
  pageTitle: 'LakeInsight',
  logoUrl: '/assets/img/lakeinsight/logo.png',
  monogramUrl: '/assets/img/lakeinsight/monogram.png',
  faviconUrl: '/assets/img/lakeinsight/favicon.ico',
} as const;

/**
 * Remap legacy /img/lakeinsight/* paths and prefix the runtime BASE_PATH
 * (e.g. /openmetadata) so assets load on subpath deployments.
 */
export const resolveBrandingAssetUrl = (url?: string): string => {
  if (!url) {
    return '';
  }

  if (
    url.startsWith('http://') ||
    url.startsWith('https://') ||
    url.startsWith('data:') ||
    url.startsWith('blob:')
  ) {
    return url;
  }

  let path = url;
  if (path.startsWith('/img/lakeinsight/')) {
    path = path.replace('/img/lakeinsight/', '/assets/img/lakeinsight/');
  }

  // Already a relative Vite asset URL (no leading slash) — leave as-is.
  if (!path.startsWith('/')) {
    return path;
  }

  const basePath = getBasePath();
  if (!basePath) {
    return path;
  }

  if (path === basePath || path.startsWith(`${basePath}/`)) {
    return path;
  }

  return `${basePath}${path}`;
};

/** @deprecated use resolveBrandingAssetUrl */
export const normalizeLakeInsightAssetUrl = resolveBrandingAssetUrl;
