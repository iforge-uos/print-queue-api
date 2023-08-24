from datetime import datetime

from print_api.models import db


class BlacklistedToken(db.Model):
    __tablename__ = "blacklisted_tokens"
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(120), nullable=False)
    blacklisted_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __init__(self, jti):
        self.jti = jti

    def __repr__(self):
        return f"<BlacklistedToken {self.jti}>"

    def to_dict(self):
        return {
            "id": self.id,
            "jti": self.jti,
            "blacklisted_at": self.blacklisted_at,
        }

    def add(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def is_blacklisted(jti) -> bool:
        blacklisted_token = BlacklistedToken.query.filter_by(jti=jti).first()
        if blacklisted_token:
            return True
        return False
