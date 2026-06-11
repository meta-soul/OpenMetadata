 package org.openmetadata.service.security;

 public class AuthServeletHandlerRegistry {
   private static volatile AuthServeletHandler currentHandler =
       NoopAuthServeletHandler.getInstance();
  private static volatile AuthServeletHandler basicAuthHandler = null;

   public static AuthServeletHandler getHandler() {
     return currentHandler;
   }

   public static void setHandler(AuthServeletHandler handler) {
     currentHandler = handler;
   }

  public static AuthServeletHandler getBasicAuthHandler() {
    return basicAuthHandler;
  }

  public static void setBasicAuthHandler(AuthServeletHandler handler) {
    basicAuthHandler = handler;
  }
 }
