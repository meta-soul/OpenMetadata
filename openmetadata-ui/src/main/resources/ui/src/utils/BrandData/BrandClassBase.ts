/*
 *  Copyright 2023 Collate.
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
import { createElement, FC, ImgHTMLAttributes } from 'react';
import LogoSrc from '../../assets/img/lakeinsight/logo.png';
import MonogramSrc from '../../assets/img/lakeinsight/monogram.png';
import WelcomeScreenSrc from '../../assets/img/welcome-screen.png';
import { LAKEINSIGHT_BRANDING } from '../../constants/LakeInsightBranding.constants';

const BrandImg: FC<ImgHTMLAttributes<HTMLImageElement>> = (props) =>
  createElement('img', {
    alt: props.alt ?? LAKEINSIGHT_BRANDING.pageTitle,
    ...props,
  });

class BrandClassBase {
  public getMonogram() {
    return {
      // Bundled import is the reliable offline fallback; public URL is preferred when set.
      src: MonogramSrc || LAKEINSIGHT_BRANDING.monogramUrl,
      svg: BrandImg,
    };
  }

  public getLogo() {
    return {
      src: LogoSrc || LAKEINSIGHT_BRANDING.logoUrl,
      svg: BrandImg,
    };
  }

  /**
   * Brand logo for the expanded app-mode (AI) sidebar header. Defaults
   * to the standard wordmark; a downstream build (e.g. Collate) overrides this
   * to show its sidebar-specific full logo without affecting the NavBar/login
   * brand from `getLogo()`.
   */
  public getSidebarLogo() {
    return this.getLogo();
  }

  /**
   * Compact brand mark for the collapsed app-mode (AI) sidebar rail.
   * Defaults to the standard monogram; overridable per build independently of
   * `getMonogram()`.
   */
  public getSidebarMonogram() {
    return this.getMonogram();
  }

  public getPageTitle() {
    return LAKEINSIGHT_BRANDING.pageTitle;
  }

  public getReleaseLink(version: string) {
    const versionWithV = 'v' + version;

    return `https://open-metadata.org/product-updates#${versionWithV}`;
  }

  public getBlogLink(_version: string) {
    // Since medium doens't follow any fixed structure we will just return the blog link
    return 'https://blog.open-metadata.org/announcing-openmetadata-1-13-123d66609468';
  }

  public getWelcomeScreenImg() {
    return WelcomeScreenSrc;
  }
}

const brandClassBase = new BrandClassBase();

export default brandClassBase;
export { BrandClassBase };
