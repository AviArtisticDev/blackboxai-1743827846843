import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from twilio.rest import Client
import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

class AlertSystem:
    def __init__(self, config_path: str = 'alert_config.json'):
        self.logger = logging.getLogger(__name__)
        self.config = self._load_config(config_path)
        self.twilio_client = None
        
        if self.config.get('twilio'):
            self._init_twilio()

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load alert configuration"""
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Alert config file not found: {config_path}")
        return json.loads(config_file.read_text())

    def _init_twilio(self):
        """Initialize Twilio SMS client"""
        twilio_config = self.config['twilio']
        self.twilio_client = Client(
            twilio_config['account_sid'],
            twilio_config['auth_token']
        )

    def send_email_alert(self, match_data: Dict[str, Any], image_data: bytes) -> bool:
        """Send email alert with match details and captured image"""
        if not self.config.get('email'):
            self.logger.warning("Email alerts not configured")
            return False

        try:
            email_config = self.config['email']
            msg = MIMEMultipart()
            msg['From'] = email_config['sender']
            msg['To'] = ', '.join(email_config['recipients'])
            msg['Subject'] = f"[ALERT] Criminal Match: {match_data['name']}"

            # Create HTML email body
            html = f"""
            <html>
                <body>
                    <h2>Criminal Match Alert</h2>
                    <p><strong>Name:</strong> {match_data['name']}</p>
                    <p><strong>Confidence:</strong> {match_data['score']:.2%}</p>
                    <p><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <p><strong>Location:</strong> {match_data.get('location', 'Unknown')}</p>
                    <img src="cid:captured_face" width="400">
                </body>
            </html>
            """
            msg.attach(MIMEText(html, 'html'))

            # Attach captured image
            img = MIMEImage(image_data)
            img.add_header('Content-ID', '<captured_face>')
            msg.attach(img)

            # Send email
            with smtplib.SMTP(
                host=email_config['smtp_host'],
                port=email_config['smtp_port']
            ) as server:
                if email_config.get('smtp_tls'):
                    server.starttls()
                server.login(
                    email_config['smtp_user'],
                    email_config['smtp_password']
                )
                server.send_message(msg)

            return True
        except Exception as e:
            self.logger.error(f"Email alert failed: {e}")
            return False

    def send_sms_alert(self, match_data: Dict[str, Any]) -> bool:
        """Send SMS alert via Twilio"""
        if not self.twilio_client:
            self.logger.warning("SMS alerts not configured")
            return False

        try:
            message = self.twilio_client.messages.create(
                body=f"Criminal Alert: {match_data['name']} detected (Confidence: {match_data['score']:.2%})",
                from_=self.config['twilio']['from_number'],
                to=self.config['twilio']['to_number']
            )
            return message.sid is not None
        except Exception as e:
            self.logger.error(f"SMS alert failed: {e}")
            return False

    def log_detection(self, match_data: Dict[str, Any], image_path: Optional[str] = None):
        """Log detection to file and database"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'match': match_data,
            'image_path': image_path
        }
        
        # Write to JSON log file
        log_file = Path('detections.log')
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')

def send_alert(match_data: Dict[str, Any], image_data: bytes) -> bool:
    """Global alert function (singleton pattern)"""
    if not hasattr(send_alert, 'alert_system'):
        send_alert.alert_system = AlertSystem()
    
    # Try email first, fall back to SMS
    success = send_alert.alert_system.send_email_alert(match_data, image_data)
    if not success:
        success = send_alert.alert_system.send_sms_alert(match_data)
    
    # Log regardless of success
    send_alert.alert_system.log_detection(match_data)
    return success