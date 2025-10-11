from app import SurveyResponse

def test_model_fields():
	fields = [c.name for c in SurveyResponse.__table__.columns]
	assert "name" in fields
