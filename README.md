# TextBelt SMS Plugin for Apprise

This plugin enables SMS notifications through [TextBelt](https://textbelt.com/) for use with Apprise and changedetection.io.

## Features

- Send SMS notifications via TextBelt API
- Support for international phone numbers
- Automatic message truncation for SMS limits
- Debug logging for troubleshooting
- Compatible with changedetection.io

## Installation

1. **Create the plugin file:**
```bash
cd /var/lib/apprise/plugins
# Create NotifyTextBelt.py with the plugin code
```

2. **Install to system Apprise:**
```bash
cp NotifyTextBelt.py /usr/local/lib/python3.11/dist-packages/apprise/plugins/
```

3. **Add to Apprise plugin registry:**
```bash
echo "from .NotifyTextBelt import NotifyTextBelt" >> /usr/local/lib/python3.11/dist-packages/apprise/plugins/__init__.py
```

4. **Test installation:**
```bash
python3 -c "from apprise.plugins.NotifyTextBelt import NotifyTextBelt; print('TextBelt plugin installed successfully!')"
```

## Usage

### URL Format

```
textbelt://API_KEY:PHONE_NUMBER
```

or

```
textbelt://API_KEY@PHONE_NUMBER
```

### Parameters

- **API_KEY**: Your TextBelt API key (get from https://textbelt.com/)
- **PHONE_NUMBER**: Target phone number (with or without + prefix)

### Examples

**Basic usage:**
```bash
apprise "textbelt://your_api_key:18005551234" -t "Alert" -b "Your message here"
```

**International number:**
```bash
apprise "textbelt://your_api_key:+441234567890" -t "Alert" -b "International SMS"
```

**With changedetection.io:**
```
textbelt://your_api_key:18005551234
```

## TextBelt Setup

1. **Get API Key:**
   - Visit https://textbelt.com/
   - Purchase credits or use free tier
   - Get your API key

2. **Test API Key:**
```bash
curl -X POST https://textbelt.com/text \
  --data-urlencode phone="5551234567" \
  --data-urlencode message="Hello from TextBelt" \
  --data-urlencode key="your_api_key"
```

## changedetection.io Integration

### Configuration

1. **In changedetection.io notification settings, add:**
```
textbelt://your_api_key:your_phone_number
```

2. **Notification body examples:**
```
Change detected: {{watch_url}}
{{current_snapshot|truncate(100)}}
```

```
{{title}}
New content found:
{{diff|truncate(120)}}
```

### Message Limits

- SMS messages are automatically truncated to 160 characters
- Use `|truncate(N)` filter to limit snapshot content
- Consider message length when using `{{current_snapshot}}` or `{{diff}}`

## Troubleshooting

### Enable Debug Logging

```bash
apprise "textbelt://your_api_key:phone" -t "Test" -b "Debug message" -vv
```

### Common Issues

**"Out of quota" error:**
- Check your TextBelt account balance
- Verify API key is correct

**"Invalid phone number" error:**
- Ensure phone number includes country code
- Use format: +1234567890 or 1234567890

**Plugin not found:**
- Verify plugin is copied to correct location
- Check __init__.py was updated
- Restart changedetection.io container

**URL parsing errors:**
- Check URL format: `textbelt://apikey:phone`
- Avoid special characters in API key
- Use colon (:) or @ as separator

### Debug Output

The plugin logs detailed information:
```
TextBelt DEBUG: Raw URL received: 'textbelt://key:phone'
TextBelt DEBUG: Strategy 2 success - apikey=1c50322479..., phone=+18037678004
TextBelt: Sending to +18037678004
TextBelt: SMS sent successfully to +18037678004
```

## File Structure

```
/var/lib/apprise/plugins/
├── NotifyTextBelt.py          # Plugin source
└── README.md                  # This file

/usr/local/lib/python3.11/dist-packages/apprise/plugins/
├── NotifyTextBelt.py          # Installed plugin
└── __init__.py               # Updated with import
```

## API Reference

### NotifyTextBelt Class

```python
class NotifyTextBelt(NotifyBase):
    def __init__(self, apikey, targets, **kwargs)
    def send(self, body, title='', notify_type=NotifyType.INFO, **kwargs)
    @staticmethod
    def parse_url(url)
```

### URL Templates

```python
templates = (
    '{schema}://{apikey}@{targets}',
    '{schema}://{apikey}:{targets}',
)
```

## License

This plugin is provided as-is for use with Apprise and changedetection.io.

## Support

- TextBelt API: https://textbelt.com/
- Apprise: https://github.com/caronc/apprise
- changedetection.io: https://github.com/dgtlmoon/changedetection.io
