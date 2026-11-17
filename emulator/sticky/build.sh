#!/bin/bash
# Build sticky/classes.dex from Sticky.java (needs a JDK and the SDK's cmdline-tools d8).
cd "$(dirname "$0")"; . ../env.sh
javac --release 11 Sticky.java && "$SDK/cmdline-tools/latest/bin/d8" --min-api 30 --output . Sticky.class && rm -f Sticky.class && echo built classes.dex
