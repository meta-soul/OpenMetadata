package org.openmetadata.mcp.server.transport;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import jakarta.servlet.http.HttpServletRequest;
import org.junit.jupiter.api.Test;

class RequestPathUtilsTest {

  @Test
  void stripsNonRootContextPath() {
    HttpServletRequest req = mock(HttpServletRequest.class);
    when(req.getRequestURI()).thenReturn("/openmetadata/mcp");
    when(req.getContextPath()).thenReturn("/openmetadata");
    assertEquals("/mcp", RequestPathUtils.relativeRequestPath(req));
  }

  @Test
  void stripsContextPathForNestedMcpRoutes() {
    HttpServletRequest req = mock(HttpServletRequest.class);
    when(req.getRequestURI()).thenReturn("/openmetadata/mcp/token");
    when(req.getContextPath()).thenReturn("/openmetadata");
    assertEquals("/mcp/token", RequestPathUtils.relativeRequestPath(req));
  }

  @Test
  void leavesPathUnchangedWhenContextPathEmpty() {
    HttpServletRequest req = mock(HttpServletRequest.class);
    when(req.getRequestURI()).thenReturn("/mcp");
    when(req.getContextPath()).thenReturn("");
    assertEquals("/mcp", RequestPathUtils.relativeRequestPath(req));
  }

  @Test
  void leavesPathUnchangedWhenContextPathIsSlash() {
    HttpServletRequest req = mock(HttpServletRequest.class);
    when(req.getRequestURI()).thenReturn("/mcp");
    when(req.getContextPath()).thenReturn("/");
    assertEquals("/mcp", RequestPathUtils.relativeRequestPath(req));
  }

  @Test
  void stripsContextPathForWellKnownRoutes() {
    HttpServletRequest req = mock(HttpServletRequest.class);
    when(req.getRequestURI())
        .thenReturn("/openmetadata/.well-known/oauth-authorization-server/mcp");
    when(req.getContextPath()).thenReturn("/openmetadata");
    assertEquals(
        "/.well-known/oauth-authorization-server/mcp", RequestPathUtils.relativeRequestPath(req));
  }
}
