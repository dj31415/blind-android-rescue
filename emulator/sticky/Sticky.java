import java.lang.reflect.*;
/** Root-only (app_process): send a sticky USB_STATE broadcast. Args: connected unlocked */
public class Sticky {
  public static void main(String[] a) throws Exception {
    Class<?> I = Class.forName("android.content.Intent");
    Object intent = I.getConstructor(String.class).newInstance("android.hardware.usb.action.USB_STATE");
    Method pe = I.getMethod("putExtra", String.class, boolean.class);
    boolean c = Boolean.parseBoolean(a[0]);
    pe.invoke(intent, "connected", c); pe.invoke(intent, "configured", c);
    pe.invoke(intent, "mtp", true); pe.invoke(intent, "unlocked", Boolean.parseBoolean(a[1]));
    I.getMethod("addFlags", int.class).invoke(intent, 0x20000000 | 0x10000000);
    Object am = Class.forName("android.app.ActivityManager").getMethod("getService").invoke(null);
    Method m = null;
    for (Method x : am.getClass().getMethods()) if (x.getName().equals("broadcastIntentWithFeature")) m = x;
    Class<?>[] p = m.getParameterTypes();
    Object[] args = new Object[p.length];
    int nb = 0, ni = 0, intCount = 0;
    for (Class<?> t : p) if (t == int.class) intCount++;
    for (int i = 0; i < p.length; i++) {
      if (p[i] == I) args[i] = intent;
      else if (p[i] == boolean.class) args[i] = (nb++ == 1);           // serialized=false, sticky=true
      else if (p[i] == int.class) { ni++; args[i] = ni == 1 ? 0 : -1; } // resultCode=0, appOp=-1, userId=USER_ALL
    }
    System.out.println(m + " -> " + m.invoke(am, args));
  }
}
