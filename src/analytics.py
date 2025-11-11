from typing import Dict, Any, List
from sqlalchemy.orm import Session
from models import Student, Grade, Attendance


class RiskAnalyzer:
    def __init__(self, session: Session):
        self.session = session

    def compute_student_features(self, student: Student) -> Dict[str, Any]:
        grades: List[Grade] = student.grades
        grades = [g for g in grades if g.average_grade is not None]

        # GPA overall and last-semester average
        overall_gpa = student.gpa

        # GPA trend (difference last semester vs. previous)
        by_term: Dict[str, Dict[str, float]] = {}
        for g in grades:
            key = f"{g.year}-{g.semester}"
            if key not in by_term:
                by_term[key] = {"weighted": 0.0, "credits": 0}
            by_term[key]["weighted"] += g.average_grade * g.course.credits
            by_term[key]["credits"] += g.course.credits

        sorted_terms = sorted(by_term.keys())
        term_gpas: List[float] = []
        for t in sorted_terms:
            c = by_term[t]
            term_gpas.append(c["weighted"] / c["credits"] if c["credits"] > 0 else 0.0)

        last_gpa = term_gpas[-1] if term_gpas else 0.0
        prev_gpa = term_gpas[-2] if len(term_gpas) >= 2 else last_gpa
        gpa_trend = last_gpa - prev_gpa

        # Failed courses and failed credits
        failed = [g for g in grades if g.average_grade < 5.0]
        failed_count = len(failed)
        failed_credits = sum(g.course.credits for g in failed)

        # Attendance: compute overall attendance rate
        attendances: List[Attendance] = student.attendances
        total_sessions = len(attendances)
        present_or_late = len([a for a in attendances if a.status in ("present", "late")])
        attendance_rate = (present_or_late / total_sessions * 100.0) if total_sessions > 0 else 100.0

        # Current study load: credits in latest term
        latest_term_credits = 0
        if grades:
            latest_year = max(g.year for g in grades)
            latest_semesters = [g.semester for g in grades if g.year == latest_year]
            if latest_semesters:
                latest_sem = max(latest_semesters)
                latest_term_credits = sum(
                    g.course.credits for g in grades if g.year == latest_year and g.semester == latest_sem
                )

        return {
            "overall_gpa": overall_gpa,
            "last_gpa": last_gpa,
            "gpa_trend": gpa_trend,
            "failed_count": failed_count,
            "failed_credits": failed_credits,
            "attendance_rate": attendance_rate,
            "latest_term_credits": latest_term_credits,
        }

    def compute_risk_score(self, features: Dict[str, Any]) -> Dict[str, Any]:
        # Rule-based baseline score 0-100
        score = 0.0
        factors: List[str] = []

        # Low GPA risk
        if features["overall_gpa"] < 5.5:
            delta = (5.5 - features["overall_gpa"]) * 6  # up to ~33
            score += delta
            factors.append(f"GPA thấp ({features['overall_gpa']:.2f})")

        # Negative trend risk
        if features["gpa_trend"] < -0.3:
            score += min(15.0, abs(features["gpa_trend"]) * 20)
            factors.append(f"Xu hướng giảm GPA ({features['gpa_trend']:.2f})")

        # Failed courses risk
        if features["failed_count"] > 0:
            score += min(20.0, features["failed_count"] * 6 + features["failed_credits"])
            factors.append(
                f"{features['failed_count']} môn không đạt ({features['failed_credits']} tín chỉ)"
            )

        # Attendance risk
        if features["attendance_rate"] < 75.0:
            score += min(20.0, (75.0 - features["attendance_rate"]) * 0.4)
            factors.append(f"Chuyên cần thấp ({features['attendance_rate']:.1f}%)")

        # High course load risk
        if features["latest_term_credits"] >= 20:
            score += 8.0
            factors.append(f"Khối lượng tín chỉ cao ({features['latest_term_credits']})")

        score = max(0.0, min(100.0, score))
        if score >= 60:
            level = "high"
        elif score >= 35:
            level = "medium"
        else:
            level = "low"

        return {"score": score, "level": level, "factors": factors}


