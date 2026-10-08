package org.openmetadata.service.security;

import static org.junit.jupiter.api.Assertions.assertEquals;

import java.util.HashMap;
import java.util.Map;
import org.junit.jupiter.api.Test;
import org.openmetadata.schema.auth.ServiceTokenType;

class AuthenticationCodeFlowHandlerOmJwtTest {

  @Test
  void casdoorTokenWithAccessTokenTypeShouldNotBeTreatedAsOmJwt() {
    Map<String, Object> claims = new HashMap<>();
    claims.put("sub", "b3e9b135-0049-425d-807b-8d0ba2b6d77e");
    claims.put("name", "lakeadmin");
    claims.put("email", "lakeadmin@lakeinsight.com");
    claims.put("tokenType", "access-token");

    boolean isOm = AuthenticationCodeFlowHandler.isOmIssuedJwt(claims);
    assertEquals(false, isOm);
  }

  @Test
  void omUserTokenShouldBeTreatedAsOmJwt() {
    Map<String, Object> claims = new HashMap<>();
    claims.put("sub", "lakeadmin");
    claims.put("tokenType", ServiceTokenType.OM_USER.value());

    boolean isOm = AuthenticationCodeFlowHandler.isOmIssuedJwt(claims);
    assertEquals(true, isOm);
  }

  @Test
  void omBotTokenShouldBeTreatedAsOmJwt() {
    Map<String, Object> claims = new HashMap<>();
    claims.put("sub", "ingestion-bot");
    claims.put("tokenType", ServiceTokenType.BOT.value());

    boolean isOm = AuthenticationCodeFlowHandler.isOmIssuedJwt(claims);
    assertEquals(true, isOm);
  }

  @Test
  void tokenWithoutTokenTypeShouldNotBeTreatedAsOmJwt() {
    Map<String, Object> claims = new HashMap<>();
    claims.put("sub", "lakeadmin");

    boolean isOm = AuthenticationCodeFlowHandler.isOmIssuedJwt(claims);
    assertEquals(false, isOm);
  }
}
