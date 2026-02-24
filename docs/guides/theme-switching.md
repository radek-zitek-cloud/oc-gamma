# Theme Switching User Guide

A comprehensive guide for using the theme switching feature in the application.

## Table of Contents

- [Overview](#overview)
- [How to Change Your Theme](#how-to-change-your-theme)
- [Understanding Theme Modes](#understanding-theme-modes)
- [Theme Persistence](#theme-persistence)
- [Troubleshooting](#troubleshooting)

## Overview

The application supports three theme modes to match your visual preferences:

- **Light Theme** - Clean, bright interface ideal for well-lit environments
- **Dark Theme** - Reduced eye strain in low-light conditions
- **System** - Automatically matches your operating system setting

Your theme preference is saved to your account and will be restored when you log in from any device.

## How to Change Your Theme

### Using the Theme Toggle

1. **Locate the Theme Toggle** in the application header (top-right corner)
2. **Click the toggle** to open the dropdown menu
3. **Select your preferred theme:**
   - ☀️ **Light** - Always use light mode
   - 🌙 **Dark** - Always use dark mode
   - 🖥️ **System** - Follow your OS preference

### Visual Indicators

- A **checkmark** appears next to your currently active theme
- The toggle icon changes based on the current theme:
  - ☀️ Sun icon for light mode
  - 🌙 Moon icon for dark mode  
  - 🖥️ Monitor icon for system mode

### Keyboard Navigation

The theme toggle is fully keyboard accessible:

| Key | Action |
|-----|--------|
| `Tab` | Focus the theme toggle button |
| `Enter` or `Space` | Open the theme menu |
| `↑` / `↓` | Navigate between theme options |
| `Enter` | Select highlighted theme |
| `Esc` | Close the menu without changing |

## Understanding Theme Modes

### Light Mode

**Best for:**
- Well-lit office environments
- Daytime usage
- Users who prefer high-contrast interfaces

**Characteristics:**
- White background
- Dark text for readability
- Gold accent colors for interactive elements

### Dark Mode

**Best for:**
- Low-light or nighttime usage
- Reducing eye strain during extended use
- Users who prefer darker interfaces

**Characteristics:**
- Dark background (near-black)
- Light text for readability
- Consistent gold accent colors

### System Mode

**Best for:**
- Users who switch between light and dark environments
- Maintaining consistency with other applications
- Automatic adaptation throughout the day

**How it works:**
- The application listens to your operating system's theme preference
- On Windows: Settings → Personalization → Colors → Choose your mode
- On macOS: System Preferences → General → Appearance
- On Linux: Varies by desktop environment

**Automatic Switching:**
- If your OS switches from light to dark (or vice versa), the application updates automatically
- No page refresh required
- Change happens instantly

## Theme Persistence

### While Logged In

When you change your theme:

1. **Immediate update** - The UI changes instantly
2. **Local storage** - Your choice is saved locally in your browser
3. **Server sync** - The preference is saved to your account (within seconds)
4. **Cross-device sync** - Your theme will be the same on all devices when you log in

### Across Sessions

Your theme preference follows you:

| Scenario | Behavior |
|----------|----------|
| Log in on a new device | Your saved theme is restored from your account |
| Log out and back in | Theme preference persists |
| Clear browser data | Theme resets to system preference until you log in |
| Use incognito/private mode | Theme resets on each session |

### Guest/Anonymous Users

If you're not logged in:

- Theme preference is stored only in your browser's localStorage
- The preference persists across page refreshes
- **Note:** Theme will reset to system default if you clear browser data

## Troubleshooting

### Theme Doesn't Change Immediately

**Problem:** Clicking a theme option doesn't update the UI.

**Solutions:**
1. Wait a moment - server sync may be in progress
2. Refresh the page and try again
3. Check your internet connection
4. Verify you're logged in (if expecting cross-device sync)

### Theme Resets After Login

**Problem:** Your theme preference isn't remembered when you log in.

**Possible Causes:**
- **Cause:** Theme changed while logged out
- **Solution:** The server preference takes precedence. Change theme while logged in to save permanently.

- **Cause:** Account was created before theme feature
- **Solution:** Default is "system" for new accounts. Set your preferred theme once.

### System Mode Not Working

**Problem:** "System" mode doesn't follow OS theme changes.

**Check:**
1. Your browser supports `matchMedia` API (all modern browsers do)
2. Browser permissions aren't blocking theme detection
3. Try refreshing the page after changing OS theme

**Browser Support:**
| Browser | Minimum Version |
|---------|-----------------|
| Chrome | 76+ |
| Firefox | 67+ |
| Safari | 13+ |
| Edge | 79+ |

### Flash of Wrong Theme (FOUT)

**Problem:** You briefly see the wrong theme when the page loads.

**This is normal** and happens because:
1. Browser renders initial HTML before JavaScript loads
2. Theme is then applied via JavaScript
3. Gap between these events causes brief flash

**Mitigation:**
- The application minimizes this using inline theme detection
- Occurrence should be very brief (<100ms)

### Rate Limiting

**Problem:** Error message "Rate limit exceeded" when changing theme.

**Explanation:** To prevent abuse, theme changes are limited to 10 per minute.

**Solution:** Wait 60 seconds before changing theme again.

### Theme Not Syncing Across Devices

**Problem:** Theme is different on phone vs computer.

**Check:**
1. Are you logged into the same account on both devices?
2. Did you change theme while logged out on one device?
3. Try logging out and back in to force a sync

**Note:** The server preference always takes precedence for logged-in users.

## Frequently Asked Questions

**Q: Does the theme affect functionality?**  
A: No, theme is purely cosmetic. All features work identically in light and dark modes.

**Q: Can I set different themes for different workspaces/projects?**  
A: Currently, theme is a global user preference. Per-project themes are not supported.

**Q: Will the theme affect exports/prints?**  
A: Printed content uses a print-optimized stylesheet regardless of your theme setting.

**Q: Does dark mode save battery?**  
A: On OLED displays (modern smartphones, some laptops), dark mode can reduce power consumption. On traditional LCD displays, the difference is negligible.

**Q: Can I schedule automatic theme changes?**  
A: Use "System" mode and configure your OS to change themes automatically (e.g., macOS Auto, Windows Night Light).

## Getting Help

If you continue to experience issues with theme switching:

1. Check the browser console for error messages (F12 → Console)
2. Try clearing browser cache and cookies
3. Test in an incognito/private window
4. Contact support with your browser version and operating system

## Related Documentation

- [Theme Development Guide](./theme-development.md) - For developers extending theme functionality
- [Theme API Documentation](../api/theme.md) - API reference for theme operations
- [Accessibility Guidelines](../architecture/accessibility.md) - Theme accessibility considerations
