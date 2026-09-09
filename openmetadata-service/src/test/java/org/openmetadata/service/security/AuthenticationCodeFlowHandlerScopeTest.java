package org.openmetadata.service.security;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.util.LinkedHashMap;
import java.util.Map;
import org.junit.jupiter.api.Test;
import org.pac4j.oidc.config.OidcConfiguration;

class AuthenticationCodeFlowHandlerScopeTest {

  @Test
  void toAuthorizationQueryString_omitsScopeWhenNotConfigured() {
    Map<String, String> params = new LinkedHashMap<>();
    params.put(OidcConfiguration.CLIENT_ID, "test-client");
    params.put(OidcConfiguration.RESPONSE_TYPE, "code");
    params.put(OidcConfiguration.REDIRECT_URI, "https://example.com/callback");
    params.put(OidcConfiguration.STATE, "abc123");

    String query = AuthenticationCodeFlowHandler.toAuthorizationQueryString(params);

    assertFalse(query.contains("scope="));
    assertTrue(query.contains("client_id=test-client"));
    assertTrue(query.contains("response_type=code"));
  }

  @Test
  void toAuthorizationQueryString_includesScopeWhenConfigured() {
    Map<String, String> params = new LinkedHashMap<>();
    params.put(OidcConfiguration.SCOPE, "openid email profile");
    params.put(OidcConfiguration.CLIENT_ID, "test-client");
    params.put(OidcConfiguration.RESPONSE_TYPE, "code");
    params.put(OidcConfiguration.REDIRECT_URI, "https://example.com/callback");

    String query = AuthenticationCodeFlowHandler.toAuthorizationQueryString(params);

    assertTrue(query.contains("scope=openid"));
  }
}
