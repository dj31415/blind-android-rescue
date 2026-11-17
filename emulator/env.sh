# Sourced by the emulator scripts: SDK location, adb on PATH, emulator PIN.
SDK=${ANDROID_HOME:-${ANDROID_SDK_ROOT:-$HOME/Android/Sdk}}
export PATH="$SDK/platform-tools:$PATH"
EPIN=${EPIN:-1234}   # PIN set on the emulator by eboot.sh; never use a real one here
