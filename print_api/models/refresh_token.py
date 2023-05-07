from datetime import datetime
from print_api.extensions import db


class refresh_token(db.Model):
    """
    Revoked Refresh Token Model
    Used to invalidate refresh tokens upon logout
    """

    __tablename__ = "refresh_tokens"
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(120), nullable=False)
    user_uid = db.Column(db.String(120), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)

    def __init__(self, jti, uid, expires_at):
        """
        Class constructor
        """
        self.jti = jti
        self.user_uid = uid
        self.expires_at = expires_at

    def add(self):
        """
        Save Object Function
        """
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def revoke(jti):
        revoked_token = refresh_token.query.filter_by(jti=jti).first()
        if revoked_token:
            db.session.delete(revoked_token)
            db.session.commit()
            return True
        return False

    @staticmethod
    def is_revoked(jti):
        revoked_token = refresh_token.query.filter_by(jti=jti).first()
        if revoked_token:
            if datetime.utcnow() > revoked_token.expires_at:
                refresh_token.revoke(jti)
                return True
            return False
        return True
