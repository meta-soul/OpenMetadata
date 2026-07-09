package org.openmetadata.service.security;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;

import org.junit.jupiter.api.Test;
import org.openmetadata.schema.api.security.AuthenticationConfiguration;
import org.openmetadata.schema.api.security.AuthorizerConfiguration;
import org.openmetadata.schema.api.security.ClientType;
import org.openmetadata.schema.security.client.OidcClientConfig;
import org.openmetadata.schema.services.connections.metadata.AuthProvider;

class AuthenticationCodeFlowHandlerManualTest {

  @Test
  void validateConfig_manualMode_includesAuthorizationEndpointInProviderMetadata() {
    OidcClientConfig oidcConfig = new OidcClientConfig();
    oidcConfig.setDiscoveryMode(OidcClientConfig.DiscoveryMode.MANUAL);
    oidcConfig.setType("custom");
    oidcConfig.setId("test-client-id");
    oidcConfig.setSecret("test-client-secret");
    oidcConfig.setTenant("");
    oidcConfig.setIssuer("https://easiu-casdoor.dmetasoul.com");
    oidcConfig.setAuthorizationEndpoint(
        "https://easiu-casdoor.dmetasoul.com/login/oauth/authorize");
    oidcConfig.setTokenEndpoint("https://easiu-casdoor.dmetasoul.com/api/login/oauth/access_token");
    oidcConfig.setUserInfoEndpoint("https://easiu-casdoor.dmetasoul.com/api/userinfo");
    oidcConfig.setJwksUri("https://easiu-casdoor.dmetasoul.com/.well-known/jwks");
    oidcConfig.setCallbackUrl("http://localhost:8585/callback");
    oidcConfig.setServerUrl("http://localhost:8585");

    AuthenticationConfiguration authConfig = new AuthenticationConfiguration();
    authConfig.setProvider(AuthProvider.CUSTOM_OIDC);
    authConfig.setClientType(ClientType.CONFIDENTIAL);
    authConfig.setOidcConfiguration(oidcConfig);

    AuthorizerConfiguration authzConfig = new AuthorizerConfiguration();
    authzConfig.setPrincipalDomain("open-metadata.org");

    assertDoesNotThrow(() -> AuthenticationCodeFlowHandler.validateConfig(authConfig, authzConfig));
  }
}
