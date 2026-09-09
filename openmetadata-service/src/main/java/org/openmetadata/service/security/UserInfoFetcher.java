package org.openmetadata.service.security;

import static org.openmetadata.common.utils.CommonUtil.nullOrEmpty;

import com.fasterxml.jackson.databind.JsonNode;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.extern.slf4j.Slf4j;
import org.openmetadata.schema.api.security.UserInfoFieldMapping;
import org.openmetadata.schema.security.client.OidcClientConfig;
import org.openmetadata.schema.utils.JsonUtils;

@Slf4j
public class UserInfoFetcher {

  private static final int CONNECT_TIMEOUT_MS = 10_000;
  private static final int READ_TIMEOUT_MS = 30_000;

  public UserInfoResult fetchUserInfo(
      String accessToken, OidcClientConfig oidcConfig, UserInfoFieldMapping mapping) {
    if (nullOrEmpty(accessToken) || nullOrEmpty(oidcConfig.getUserInfoEndpoint())) {
      LOG.warn("Cannot fetch userinfo - missing access_token or userInfoEndpoint");
      return null;
    }

    String headerType =
        oidcConfig.getUserInfoTokenHeaderType() != null
            ? oidcConfig.getUserInfoTokenHeaderType().value()
            : "bearer";
    String authHeader = "raw".equalsIgnoreCase(headerType) ? accessToken : "Bearer " + accessToken;
    String userNameField =
        mapping != null && !nullOrEmpty(mapping.getUserNameField())
            ? mapping.getUserNameField()
            : "username";
    String emailField =
        mapping != null && !nullOrEmpty(mapping.getEmailField())
            ? mapping.getEmailField()
            : "email";
    String displayNameField = mapping != null ? mapping.getDisplayNameField() : null;
    String userIdField = mapping != null ? mapping.getUserIdField() : null;

    HttpURLConnection conn = null;
    try {
      URL url = new URL(oidcConfig.getUserInfoEndpoint());
      conn = (HttpURLConnection) url.openConnection();
      conn.setRequestMethod("GET");
      conn.setRequestProperty("Authorization", authHeader);
      conn.setRequestProperty("Accept", "application/json");
      conn.setConnectTimeout(CONNECT_TIMEOUT_MS);
      conn.setReadTimeout(READ_TIMEOUT_MS);

      int status = conn.getResponseCode();
      if (status != 200) {
        LOG.warn("Userinfo endpoint returned non-200 status: {}", status);
        return null;
      }

      String body = readResponse(conn);
      JsonNode userinfo = JsonUtils.readTree(body);
      String userName = textOrNull(userinfo, userNameField);
      String email = textOrNull(userinfo, emailField);
      String displayName =
          nullOrEmpty(displayNameField) ? null : textOrNull(userinfo, displayNameField);
      String userId = nullOrEmpty(userIdField) ? null : textOrNull(userinfo, userIdField);

      LOG.debug(
          "Fetched userinfo - userName: {}, email: {}, displayName: {}, userId: {}",
          userName,
          email,
          displayName,
          userId);
      return new UserInfoResult(userName, email, displayName, userId);
    } catch (IOException e) {
      LOG.error("Failed to fetch userinfo endpoint: {}", e.getMessage(), e);
      return null;
    } catch (Exception e) {
      LOG.error("Failed to parse userinfo response: {}", e.getMessage(), e);
      return null;
    } finally {
      if (conn != null) {
        conn.disconnect();
      }
    }
  }

  private static String textOrNull(JsonNode node, String field) {
    if (nullOrEmpty(field)) {
      return null;
    }
    JsonNode value = node.get(field);
    if (value == null || value.isNull()) {
      return null;
    }
    return value.asText();
  }

  private static String readResponse(HttpURLConnection conn) throws IOException {
    try (BufferedReader reader =
        new BufferedReader(new InputStreamReader(conn.getInputStream(), StandardCharsets.UTF_8))) {
      StringBuilder sb = new StringBuilder();
      String line;
      while ((line = reader.readLine()) != null) {
        sb.append(line);
      }
      return sb.toString();
    }
  }

  @Getter
  @AllArgsConstructor
  public static class UserInfoResult {
    private final String userName;
    private final String email;
    private final String displayName;
    private final String userId;
  }
}
