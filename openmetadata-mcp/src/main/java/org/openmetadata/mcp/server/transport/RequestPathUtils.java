package org.openmetadata.mcp.server.transport;

import jakarta.servlet.http.HttpServletRequest;

public final class RequestPathUtils {
  private RequestPathUtils() {}

  /**
   * Returns the request path relative to the servlet context path.
   * Example: contextPath=/openmetadata, requestURI=/openmetadata/mcp → /mcp
   */
  public static String relativeRequestPath(HttpServletRequest request) {
    String uri = request.getRequestURI();
    if (uri == null) {
      return "";
    }
    String contextPath = request.getContextPath();
    if (contextPath == null || contextPath.isEmpty() || "/".equals(contextPath)) {
      return uri;
    }
    if (uri.startsWith(contextPath)) {
      String relative = uri.substring(contextPath.length());
      return relative.isEmpty() ? "/" : relative;
    }
    return uri;
  }
}
