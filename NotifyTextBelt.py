import requests
import json
from apprise.plugins.base import NotifyBase
from apprise.common import NotifyType
from apprise import URLBase

class NotifyTextBelt(NotifyBase):
    """
    A wrapper for TextBelt SMS notifications for Apprise
    """
    
    service_name = 'TextBelt'
    service_url = 'https://textbelt.com/'
    secure_protocol = 'textbelt'
    
    # Define object templates - this is what changedetection.io will use
    templates = (
        '{schema}://{apikey}@{targets}',
        '{schema}://{apikey}:{targets}',
    )
    
    # Define our arguments
    template_tokens = dict(NotifyBase.template_tokens, **{
        'apikey': {
            'name': 'API Key',
            'type': 'string',
            'required': True,
        },
        'targets': {
            'name': 'Phone Number',
            'type': 'string',
            'required': True,
        },
    })
    
    def __init__(self, apikey, targets, **kwargs):
        """
        Initialize TextBelt Object
        """
        super(NotifyTextBelt, self).__init__(**kwargs)
        
        self.apikey = apikey
        self.targets = []
        
        # Handle targets - can be phone numbers
        if isinstance(targets, str):
            targets = [targets]
        elif not isinstance(targets, list):
            targets = [str(targets)]
        
        for target in targets:
            # Clean phone number
            phone = str(target).strip()
            if not phone.startswith('+'):
                phone = '+' + phone
            self.targets.append(phone)
        
        if not self.targets:
            msg = 'No valid phone numbers were specified'
            self.logger.warning(msg)
            raise TypeError(msg)
    
    def send(self, body, title='', notify_type=NotifyType.INFO, **kwargs):
        """
        Perform TextBelt SMS notification
        """
        
        # Debug logging
        self.logger.info(f'TextBelt: Received title="{title}", body length={len(body)}')
        self.logger.debug(f'TextBelt: Full body content: {repr(body[:200])}...')
        
        # Prepare message
        message = body
        if title:
            message = f"{title}: {body}"
        
        # Truncate message if too long (SMS limit)
        if len(message) > 160:
            message = message[:157] + "..."
            self.logger.info(f'TextBelt: Message truncated to {len(message)} chars')
        
        success = True
        
        for target in self.targets:
            payload = {
                'phone': target,
                'message': message,
                'key': self.apikey
            }
            
            try:
                self.logger.info(f'TextBelt: Sending to {target}')
                self.logger.debug(f'TextBelt Payload: {payload}')
                
                response = requests.post(
                    'https://textbelt.com/text',
                    data=payload,
                    timeout=10
                )
                
                result = response.json()
                self.logger.debug(f'TextBelt Response: {result}')
                
                if not result.get('success'):
                    error_msg = result.get('error', 'Unknown error')
                    self.logger.warning(f'Failed to send SMS to {target}: {error_msg}')
                    success = False
                else:
                    self.logger.info(f'SMS sent successfully to {target}')
                    
            except Exception as e:
                self.logger.warning(f'Error sending SMS to {target}: {str(e)}')
                success = False
        
        return success
    
    @staticmethod
    def parse_url(url):
        """
        Parses the URL and returns arguments for instantiation
        """
        import re
        
        # Log the incoming URL for debugging
        print(f"TextBelt DEBUG: Raw URL received: '{url}'")
        
        # Try multiple parsing strategies
        
        # Strategy 1: textbelt://apikey@phonenumber
        match1 = re.match(r'textbelt://([^@]+)@(\+?\d+)', url)
        if match1:
            apikey = match1.group(1)
            phone = match1.group(2)
            if not phone.startswith('+'):
                phone = '+' + phone
            print(f"TextBelt DEBUG: Strategy 1 success - apikey={apikey[:10]}..., phone={phone}")
            return {
                'schema': 'textbelt',
                'apikey': apikey,
                'targets': [phone],
            }
        
        # Strategy 2: textbelt://apikey:phonenumber
        match2 = re.match(r'textbelt://([^:]+):(\+?\d+)', url)
        if match2:
            apikey = match2.group(1)
            phone = match2.group(2)
            if not phone.startswith('+'):
                phone = '+' + phone
            print(f"TextBelt DEBUG: Strategy 2 success - apikey={apikey[:10]}..., phone={phone}")
            return {
                'schema': 'textbelt',
                'apikey': apikey,
                'targets': [phone],
            }
        
        # Strategy 3: Use Apprise's built-in URL parser as fallback
        try:
            results = NotifyBase.parse_url(url, verify_host=False)
            print(f"TextBelt DEBUG: Apprise parser results: {results}")
            
            if results:
                # Extract from different parts
                apikey = results.get('user') or results.get('host', '')
                phone = results.get('host') or results.get('password', '')
                
                # Clean up phone number
                if phone and not phone.startswith('+'):
                    phone = '+' + phone
                    
                if apikey and phone and phone != apikey:
                    print(f"TextBelt DEBUG: Strategy 3 success - apikey={apikey[:10]}..., phone={phone}")
                    return {
                        'schema': 'textbelt',
                        'apikey': apikey,
                        'targets': [phone],
                    }
        except Exception as e:
            print(f"TextBelt DEBUG: Apprise parser failed: {e}")
        
        print(f"TextBelt DEBUG: All parsing strategies failed for URL: {url}")
        return None

###for ChangeDetection.io
    def url(self, privacy=False, *args, **kwargs):
        """
        Returns the URL built dynamically based on specified arguments.
        """
        # Determine Authentication
        auth = ''
        if self.apikey:
            auth = f'{self.apikey}@'
        
        return f'{self.secure_protocol}://{auth}{self.targets[0]}'
