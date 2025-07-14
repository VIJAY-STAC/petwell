from jose import jwt
from datetime import datetime, timedelta
from django.conf import settings


def generate_jwt_token(id, user_type, roles=None):
	expire_at = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRATION_MINUTES)
	payload = {
		'user_id': id,
		'exp': expire_at,
		'user_type': user_type,
		'roles': roles
	}

	token = jwt.encode(payload, settings.JWT_SECRET)
	return token

def validate_jwt_token(token):
	try:
		payload = jwt.decode(
			token,
			settings.JWT_SECRET
		)
		return payload
	except:
		return None