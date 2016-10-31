# Quick Emulators

Launch your Android emulators (Genymotion and AVDs) via Spotlight: ⌘ + Space

![Finding Genymotion Emulator](https://raw.github.com/dvoiss/quick-emulators/master/screenshots/find-genymotion.png)

## Use

```bash
brew tap dvoiss/tap
brew install quick-emulators
brew services start dvoiss/tap/quick-emulators
```

## How does it work?

The process started by `brew services` will create `.app` files under the directory: `~/Applications/Quick Emulators/` (see screenshot below). These empty app files are indexed by Spotlight. They contain a shell script that launches one of these commands:

1. For Android Virtual Devices:

    `PATH_TO_ANDROID_SDK/tools/emulator -avd <name-of-emulator>`

2. For Genymotion Virtual Machines:

    `/Applications/Genymotion.app/Contents/MacOS/player.app/Contents/MacOS/player --vm-name <name-of-emulator>`

For AVDs an `ANDROID_SDK` or `ANDROID_HOME` environment variable must be set. For Genymotion the Genymotion app must be at the default path above.

The background daemon watches for changes in the default locations that AVDs and Genymotion virtual machines are installed to: `~/.android/avd/` and `~/.Genymobile/Genymotion/deployed/`. When you add or remove a new emulator the generated folder containing the .app files gets re-written. For more information see the `plist` method in the [Homebrew formula for Quick Emulators](https://github.com/dvoiss/homebrew-tap/blob/master/quick-emulators.rb).

![Generated App files](https://raw.github.com/dvoiss/quick-emulators/master/screenshots/app-folder.png)

The generated app files are tagged with "Emulator" and either "AVD" or "Genymotion". These tags can be used in Spotlight as well:

![Finding AVD by Tag](https://raw.github.com/dvoiss/quick-emulators/master/screenshots/find-avd.png)