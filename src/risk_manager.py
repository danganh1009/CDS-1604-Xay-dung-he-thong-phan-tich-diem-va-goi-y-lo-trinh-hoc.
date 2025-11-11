import json
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from models import Student, RiskAlert
from analytics import RiskAnalyzer


class RiskManager:
    def __init__(self, db_session: Session):
        self.session = db_session
        self.analyzer = RiskAnalyzer(db_session)

    def generate_alert_for_student(self, student: Student, semester: int, year: int) -> RiskAlert:
        features = self.analyzer.compute_student_features(student)
        result = self.analyzer.compute_risk_score(features)

        alert = RiskAlert(
            student_id=student.id,
            semester=semester,
            year=year,
            risk_score=result["score"],
            risk_level=result["level"],
            factors=json.dumps({"factors": result["factors"], "features": features}, ensure_ascii=False),
        )
        self.session.add(alert)
        self.session.commit()
        return alert

    def regenerate_alerts(self, semester: int, year: int) -> List[RiskAlert]:
        # Delete existing alerts for term
        self.session.query(RiskAlert).filter_by(semester=semester, year=year).delete()
        self.session.commit()

        alerts: List[RiskAlert] = []
        for student in self.session.query(Student).all():
            alerts.append(self.generate_alert_for_student(student, semester, year))
        return alerts

    def list_alerts(self, semester: Optional[int] = None, year: Optional[int] = None) -> List[RiskAlert]:
        query = self.session.query(RiskAlert)
        if semester is not None:
            query = query.filter(RiskAlert.semester == semester)
        if year is not None:
            query = query.filter(RiskAlert.year == year)
        return query.order_by(RiskAlert.risk_score.desc()).all()

    def get_student_latest_alert(self, student_id: str) -> Optional[Dict[str, Any]]:
        student = self.session.query(Student).filter_by(student_id=student_id).first()
        if not student:
            return None
        alert = (
            self.session.query(RiskAlert)
            .filter(RiskAlert.student_id == student.id)
            .order_by(RiskAlert.year.desc(), RiskAlert.semester.desc(), RiskAlert.id.desc())
            .first()
        )
        if not alert:
            return None
        payload = {
            "student_id": student.student_id,
            "name": student.name,
            "risk_score": alert.risk_score,
            "risk_level": alert.risk_level,
            "semester": alert.semester,
            "year": alert.year,
            "factors": json.loads(alert.factors) if alert.factors else {},
        }
        return payload


