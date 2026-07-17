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

/**
 * LakeInsight offline branding assets under public/assets/img/lakeinsight.
 * Paths use the /assets/ prefix so they match Vite hashed static routes that
 * ingress/gateways typically allow (plain /img/* may be blocked and 404).
 */
export const LAKEINSIGHT_BRANDING = {
  pageTitle: 'LakeInsight',
  logoUrl: '/assets/img/lakeinsight/logo.png',
  monogramUrl: '/assets/img/lakeinsight/monogram.png',
  faviconUrl: '/assets/img/lakeinsight/favicon.ico',
} as const;

/** Remap legacy /img/lakeinsight/* settings to the /assets/ prefix. */
export const normalizeLakeInsightAssetUrl = (url?: string): string => {
  if (!url) {
    return '';
  }

  if (url.startsWith('/img/lakeinsight/')) {
    return url.replace('/img/lakeinsight/', '/assets/img/lakeinsight/');
  }

  return url;
};
