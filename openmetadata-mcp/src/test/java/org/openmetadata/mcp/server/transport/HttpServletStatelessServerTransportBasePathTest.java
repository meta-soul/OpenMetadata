package org.openmetadata.mcp.server.transport;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import jakarta.servlet.http.HttpServletRequest;
import org.junit.jupiter.api.Test;

class HttpServletStatelessServerTransportBasePathTest {

  @Test
  void relativePathEqualsMcpEndpointUnderBasePath() {
    HttpServletRequest req = mock(HttpServletRequest.class);
    when(req.getRequestURI()).thenReturn("/openmetadata/mcp");
    when(req.getContextPath()).thenReturn("/openmetadata");
    assertEquals("/mcp", RequestPathUtils.relativeRequestPath(req));
    assertTrue(RequestPathUtils.relativeRequestPath(req).equals("/mcp"));
  }
}
