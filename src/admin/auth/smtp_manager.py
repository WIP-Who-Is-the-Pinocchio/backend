import logging

from email.message import EmailMessage
from smtplib import SMTP_SSL, SMTPAuthenticationError, SMTPException

from pydantic import EmailStr

from config import settings

logger = logging.getLogger("uvicorn")


class SmtpManager:
    smtp_server: str = "smtp.gmail.com"
    sender_email: EmailStr = settings.sender_gmail
    gmail_password: str = settings.gmail_password
    smtp = SMTP_SSL(smtp_server, 465)

    def send_auth_num(self, requested_email: str, auth_num: int):
        try:
            message = EmailMessage()
            message["Subject"] = "W.I.P 관리자 가입 인증번호 안내 메일"
            message["From"] = self.sender_email
            message["To"] = requested_email
            message.set_content(f"인증번호: {auth_num}\n가입 페이지에서 3분 이내로 입력하시기 바랍니다.")

            self.smtp.login(self.sender_email, self.gmail_password)
            self.smtp.send_message(message)
            logger.info(f"Send auth number to {requested_email}")
        except SMTPAuthenticationError as e:
            logger.error(f"SMTP email authentication Error: {e}")
        except SMTPException as e:
            logger.error(f"SMTP Exception: {e}")
        except Exception as e:
            logger.error(f"Other error occurred when sending email: {e}")
        finally:
            self.smtp.quit()
            logger.info(f"SMTP closed")

    def send_login_alarm(self, requested_email: str, nickname: str):
        try:
            message = EmailMessage()
            message["Subject"] = "W.I.P 관리자 로그인 알림"
            message["From"] = self.sender_email
            message["To"] = requested_email
            message.set_content(f"{nickname}님이 W.I.P 관리자 페이지에 로그인했습니다.")

            self.smtp.login(self.sender_email, self.gmail_password)
            self.smtp.send_message(message)
            logger.info(f"Send login alarm to {requested_email}")
            self.smtp.quit()
        except SMTPAuthenticationError as e:
            logger.error(f"SMTP email authentication Error: {e}")
        except SMTPException as e:
            logger.error(f"SMTP Exception: {e}")
        except Exception as e:
            logger.error(f"Other error occurred when sending email: {e}")
        finally:
            self.smtp.quit()
            logger.info(f"SMTP closed")
