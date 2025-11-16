"""
Scoring Service for GovernAI
Handles risk scoring, compliance scoring, and validation
"""
import re
from typing import Dict, List, Optional


class ScoringService:
    """Service for calculating and validating scores"""
    
    @staticmethod
    def calculate_risk_score(
        risk_factors: List[str] = None,
        risks: List[Dict] = None,
        contract_value: float = None,
        expiration_date: str = None,
        has_penalties: bool = False,
        has_auto_renewal: bool = False,
        ai_risk_score: float = None
    ) -> float:
        """
        Calculate risk score (0-100) based on multiple factors
        Lower score = lower risk, Higher score = higher risk
        """
        base_score = 0.0
        risk_factors = risk_factors or []
        risks = risks or []
        
        # Start with AI-provided score if available (weighted 40%)
        if ai_risk_score is not None:
            try:
                ai_score = float(ai_risk_score)
                if 0 <= ai_score <= 100:
                    base_score = ai_score * 0.4
            except (ValueError, TypeError):
                pass
        
        # Factor 1: Risk factors count (weighted 20%)
        risk_factor_score = min(len(risk_factors) * 5, 20)
        base_score += risk_factor_score * 0.2
        
        # Factor 2: Risk severity (weighted 25%)
        if risks:
            severity_weights = {
                'critical': 25,
                'high': 15,
                'medium': 10,
                'low': 5,
                'minor': 2
            }
            severity_score = 0
            for risk in risks:
                severity = risk.get('severity', 'low').lower()
                severity_score += severity_weights.get(severity, 5)
            severity_score = min(severity_score / len(risks), 25)
            base_score += severity_score * 0.25
        else:
            # If no risks identified, reduce score
            base_score += 5 * 0.25
        
        # Factor 3: Contract value risk (weighted 10%)
        if contract_value:
            # Higher value = higher risk
            if contract_value > 1000000:  # > $1M
                base_score += 10 * 0.1
            elif contract_value > 100000:  # > $100K
                base_score += 7 * 0.1
            elif contract_value > 10000:  # > $10K
                base_score += 4 * 0.1
            else:
                base_score += 2 * 0.1
        
        # Factor 4: Penalty clauses (weighted 5%)
        if has_penalties:
            base_score += 10 * 0.05
        
        # Factor 5: Auto-renewal risk (weighted 5%)
        if has_auto_renewal:
            base_score += 8 * 0.05
        
        # Factor 6: Expiration date proximity (weighted 5%)
        if expiration_date:
            # This would require date parsing - simplified for now
            # Contracts expiring soon are higher risk
            base_score += 5 * 0.05
        
        # Ensure score is between 0 and 100
        final_score = max(0.0, min(100.0, base_score))
        
        # Round to 1 decimal place
        return round(final_score, 1)
    
    @staticmethod
    def validate_risk_score(score: float) -> float:
        """Validate and normalize risk score to 0-100 range"""
        try:
            score = float(score)
            return max(0.0, min(100.0, round(score, 1)))
        except (ValueError, TypeError):
            return 50.0  # Default medium risk
    
    @staticmethod
    def calculate_compliance_score(
        status: str,
        last_assessment_date: str = None,
        total_requirements: int = 0,
        met_requirements: int = 0,
        ai_compliance_score: int = None
    ) -> int:
        """
        Calculate compliance score (0-100) based on status and requirements
        Higher score = better compliance
        """
        # Start with status-based score
        status_scores = {
            'compliant': 90,
            'at_risk': 60,
            'non_compliant': 30,
            'pending': 50,
            'under_review': 50
        }
        base_score = status_scores.get(status.lower(), 50)
        
        # If requirements data is available, calculate based on that
        if total_requirements > 0 and met_requirements >= 0:
            requirement_score = int((met_requirements / total_requirements) * 100)
            # Weight: 70% requirements, 30% status
            base_score = (requirement_score * 0.7) + (base_score * 0.3)
        
        # Use AI score if provided (weighted 20%)
        if ai_compliance_score is not None:
            try:
                ai_score = int(ai_compliance_score)
                if 0 <= ai_score <= 100:
                    base_score = (base_score * 0.8) + (ai_score * 0.2)
            except (ValueError, TypeError):
                pass
        
        # Ensure score is between 0 and 100
        final_score = max(0, min(100, int(round(base_score))))
        return final_score
    
    @staticmethod
    def validate_compliance_score(score: int) -> int:
        """Validate and normalize compliance score to 0-100 range"""
        try:
            score = int(score)
            return max(0, min(100, score))
        except (ValueError, TypeError):
            return 50  # Default medium compliance
    
    @staticmethod
    def extract_risk_factors_from_text(text: str) -> List[str]:
        """Extract risk indicators from contract text"""
        risk_factors = []
        text_lower = text.lower()
        
        # Check for penalty clauses
        if any(word in text_lower for word in ['penalty', 'penalties', 'liquidated damages', 'breach fee']):
            risk_factors.append('Contains penalty clauses')
        
        # Check for auto-renewal
        if any(word in text_lower for word in ['auto-renew', 'automatic renewal', 'evergreen']):
            risk_factors.append('Auto-renewal clause present')
        
        # Check for termination clauses
        if any(word in text_lower for word in ['termination', 'early termination', 'terminate']):
            risk_factors.append('Termination clauses present')
        
        # Check for compliance requirements
        if any(word in text_lower for word in ['gdpr', 'hipaa', 'sox', 'compliance', 'regulatory']):
            risk_factors.append('Regulatory compliance requirements')
        
        # Check for data privacy
        if any(word in text_lower for word in ['data privacy', 'personal data', 'pii', 'confidential']):
            risk_factors.append('Data privacy obligations')
        
        # Check for liability
        if any(word in text_lower for word in ['liability', 'indemnification', 'hold harmless']):
            risk_factors.append('Liability clauses present')
        
        return risk_factors
    
    @staticmethod
    def get_risk_level(risk_score: float) -> str:
        """Get risk level category from score"""
        if risk_score >= 75:
            return 'critical'
        elif risk_score >= 50:
            return 'high'
        elif risk_score >= 25:
            return 'medium'
        else:
            return 'low'
    
    @staticmethod
    def get_compliance_level(compliance_score: int) -> str:
        """Get compliance level category from score"""
        if compliance_score >= 90:
            return 'excellent'
        elif compliance_score >= 75:
            return 'good'
        elif compliance_score >= 50:
            return 'fair'
        elif compliance_score >= 25:
            return 'poor'
        else:
            return 'critical'

