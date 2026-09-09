package org.openmetadata.service.security.auth.validator;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.openmetadata.schema.api.security.AuthenticationConfiguration;
import org.openmetadata.schema.api.security.ClientType;
import org.openmetadata.schema.security.client.OidcClientConfig;
import org.openmetadata.schema.services.connections.metadata.AuthProvider;
import org.openmetadata.schema.system.FieldError;

public class CustomOidcManualValidatorTest {
  private CustomOidcValidator validator;
  private AuthenticationConfiguration authConfig;
  private OidcClientConfig oidcConfig;

  @BeforeEach
  void setUp() {
    validator = new CustomOidcValidator();
    authConfig = new AuthenticationConfiguration();
    authConfig.setClientType(ClientType.CONFIDENTIAL);
    authConfig.setProvider(AuthProvider.CUSTOM_OIDC);
    authConfig.setClientId("test-client-id");
    oidcConfig = new OidcClientConfig();
    oidcConfig.setDiscoveryMode(OidcClientConfig.DiscoveryMode.MANUAL);
    oidcConfig.setId("test-client-id");
    oidcConfig.setSecret("test-client-secret");
    oidcConfig.setTenant("");
    oidcConfig.setAuthorizationEndpoint("https://sso.example.com/auth/api/oauth2/authorize");
    oidcConfig.setTokenEndpoint("https://sso.example.com/auth/api/oauth2/token");
    oidcConfig.setUserInfoEndpoint("https://sso.example.com/auth/api/oauth2/userinfo");
  }

  @Test
  void testManualMode_AllEndpointsPresent_ReturnsSuccess() {
    FieldError result = validator.validateCustomOidcConfiguration(authConfig, oidcConfig);
    assertNull(result, "Manual mode with all endpoints should pass validation");
  }

  @Test
  void testManualMode_MissingAuthorizationEndpoint_ReturnsError() {
    oidcConfig.setAuthorizationEndpoint(null);
    FieldError result = validator.validateCustomOidcConfiguration(authConfig, oidcConfig);
    assertNotNull(result, "Missing authorizationEndpoint should fail");
    assertTrue(result.getError().contains("Authorization endpoint"));
  }

  @Test
  void testManualMode_MissingTokenEndpoint_ReturnsError() {
    oidcConfig.setTokenEndpoint(null);
    FieldError result = validator.validateCustomOidcConfiguration(authConfig, oidcConfig);
    assertNotNull(result, "Missing tokenEndpoint should fail");
    assertTrue(result.getError().contains("Token endpoint"));
  }

  @Test
  void testManualMode_MissingUserInfoEndpoint_ReturnsError() {
    oidcConfig.setUserInfoEndpoint(null);
    FieldError result = validator.validateCustomOidcConfiguration(authConfig, oidcConfig);
    assertNotNull(result, "Missing userInfoEndpoint should fail");
    assertTrue(result.getError().contains("Userinfo endpoint"));
  }

  @Test
  void testManualMode_MissingClientId_ReturnsError() {
    oidcConfig.setId(null);
    FieldError result = validator.validateCustomOidcConfiguration(authConfig, oidcConfig);
    assertNotNull(result, "Missing client id should fail");
    assertTrue(result.getError().contains("Client ID"));
  }

  @Test
  void testManualMode_MissingClientSecret_ReturnsError() {
    oidcConfig.setSecret(null);
    FieldError result = validator.validateCustomOidcConfiguration(authConfig, oidcConfig);
    assertNotNull(result, "Missing client secret should fail");
    assertTrue(result.getError().contains("Client Secret"));
  }

  @Test
  void testManualMode_AutoMode_FallsBackToDiscoveryValidation() {
    // When discoveryMode is auto (default), manual branch should be skipped
    oidcConfig.setDiscoveryMode(OidcClientConfig.DiscoveryMode.AUTO);
    oidcConfig.setDiscoveryUri("");
    FieldError result = validator.validateCustomOidcConfiguration(authConfig, oidcConfig);
    // Auto mode without discoveryUri should report discovery URI error
    assertNotNull(result, "Auto mode without discoveryUri should fail");
    assertTrue(result.getError().contains("Discovery URI"));
  }

  @Test
  void testManualMode_DefaultDiscoveryMode_TreatedAsAuto() {
    // When discoveryMode is null (default), should be treated as auto
    oidcConfig.setDiscoveryMode(null);
    oidcConfig.setDiscoveryUri("");
    FieldError result = validator.validateCustomOidcConfiguration(authConfig, oidcConfig);
    assertNotNull(result, "Null discoveryMode should be treated as auto and require discoveryUri");
    assertTrue(result.getError().contains("Discovery URI"));
  }

  @Test
  void testManualMode_PublicClient_AlsoValidatesManualEndpoints() {
    authConfig.setClientType(ClientType.PUBLIC);
    FieldError result = validator.validateCustomOidcConfiguration(authConfig, oidcConfig);
    assertNull(result, "Public client in manual mode with all endpoints should pass");
  }

  @Test
  void testManualMode_PublicClient_SecretNotRequired() {
    authConfig.setClientType(ClientType.PUBLIC);
    oidcConfig.setSecret(null);
    FieldError result = validator.validateCustomOidcConfiguration(authConfig, oidcConfig);
    assertNull(result, "Public client in manual mode should not require a client secret");
  }

  @Test
  void testManualMode_WithFieldMappingConfig_DoesNotAffectEndpointValidation() {
    org.openmetadata.schema.api.security.UserInfoFieldMapping mapping =
        new org.openmetadata.schema.api.security.UserInfoFieldMapping();
    mapping.setUserNameField("name");
    mapping.setDisplayNameField("nickname");
    mapping.setEmailField("email");
    mapping.setUserIdField("sub");
    authConfig.setUserInfoFieldMapping(mapping);
    FieldError result = validator.validateCustomOidcConfiguration(authConfig, oidcConfig);
    assertNull(result, "Field mapping should not affect manual endpoint validation");
  }

  @Test
  void testDisplayNameFromNicknameClaim() {
    // Verify SecurityUtil.extractDisplayNameFromClaims supports nickname
    java.util.Map<String, Object> claims = new java.util.HashMap<>();
    claims.put("nickname", "ChageeUser");
    String displayName =
        org.openmetadata.service.security.SecurityUtil.extractDisplayNameFromClaims(claims);
    assertEquals("ChageeUser", displayName);
  }

  @Test
  void testDisplayNameFromConfiguredClaim() {
    // Configured displayNameClaim takes precedence over the default claim order
    java.util.Map<String, Object> claims = new java.util.HashMap<>();
    claims.put("name", "c6a8b673");
    claims.put("custom_display", "渠道领航-鲁迅");
    String displayName =
        org.openmetadata.service.security.SecurityUtil.extractDisplayNameFromClaims(
            claims, "custom_display");
    assertEquals("渠道领航-鲁迅", displayName);
  }

  @Test
  void testDisplayNameFromConfiguredClaim_FallsBackWhenMissing() {
    java.util.Map<String, Object> claims = new java.util.HashMap<>();
    claims.put("nickname", "ChageeUser");
    String displayName =
        org.openmetadata.service.security.SecurityUtil.extractDisplayNameFromClaims(
            claims, "not_present");
    assertEquals("ChageeUser", displayName);
  }
}
