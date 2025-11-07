import re
import numpy as np
from collections import Counter
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class CareerPathPredictor:
    def __init__(self):
        self.career_paths = []
        
        # Domain-specific skills for reference (not used in extraction anymore)
        self.domain_skills = {
            'Engineering': [
                'programming', 'cad', 'engineering design', 'mechanical', 'electrical', 'civil',
                'structural analysis', 'thermodynamics', 'circuit design', 'manufacturing',
                'project management', 'technical documentation', 'solidworks', 'autocad',
                'matlab', 'simulation', 'prototyping', 'quality control', 'safety standards'
            ],
            'Information Technology': [
                'python', 'javascript', 'java', 'sql', 'react', 'node.js', 'aws', 'docker',
                'kubernetes', 'linux', 'networking', 'cybersecurity', 'devops', 'ci/cd',
                'database', 'api', 'web development', 'mobile development', 'cloud computing',
                'troubleshooting', 'system administration', 'it support'
            ],
            'Healthcare': [
                'patient care', 'medical knowledge', 'healthcare', 'nursing', 'medical terminology',
                'emergency response', 'medical documentation', 'healthcare administration',
                'clinical skills', 'patient assessment', 'medication administration',
                'healthcare regulations', 'medical research', 'laboratory techniques'
            ],
            'Education': [
                'teaching', 'curriculum development', 'classroom management', 'lesson planning',
                'student assessment', 'educational technology', 'instructional design',
                'student counseling', 'educational leadership', 'training', 'mentoring',
                'academic advising', 'education policy'
            ],
            'Finance': [
                'financial analysis', 'accounting', 'excel', 'financial modeling', 'budgeting',
                'forecasting', 'investment', 'banking', 'taxation', 'auditing', 'risk management',
                'financial reporting', 'quickbooks', 'sap', 'compliance', 'portfolio management'
            ],
            'Marketing': [
                'digital marketing', 'seo', 'social media', 'content creation', 'brand management',
                'market research', 'analytics', 'advertising', 'campaign management',
                'email marketing', 'content strategy', 'public relations', 'customer acquisition',
                'google analytics', 'marketing automation'
            ],
            'Design': [
                'ui/ux design', 'graphic design', 'adobe creative suite', 'figma', 'sketch',
                'typography', 'layout design', 'brand identity', 'web design', 'print design',
                'motion graphics', '3d modeling', 'user research', 'prototyping', 'wireframing'
            ],
            'Sales': [
                'sales', 'negotiation', 'customer relationship', 'account management',
                'business development', 'lead generation', 'client acquisition', 'presentation',
                'persuasion', 'closing deals', 'sales strategy', 'territory management',
                'customer service', 'relationship building'
            ],
            'Legal': [
                'legal research', 'contract law', 'litigation', 'legal writing', 'compliance',
                'corporate law', 'intellectual property', 'legal documentation', 'case management',
                'regulatory compliance', 'dispute resolution', 'legal advice', 'paralegal'
            ],
            'Operations / Management': [
                'operations management', 'project management', 'process improvement',
                'supply chain', 'logistics', 'team leadership', 'strategic planning',
                'budget management', 'performance management', 'quality assurance',
                'inventory management', 'six sigma', 'lean manufacturing', 'business operations'
            ]
        }
        
        self.soft_skills = [
            'communication', 'leadership', 'teamwork', 'problem solving', 'critical thinking',
            'creativity', 'adaptability', 'time management', 'project management',
            'analytical skills', 'research', 'presentation', 'negotiation', 'collaboration'
        ]

    def load_career_paths(self, career_paths_data):
        """Load career paths data"""
        self.career_paths = career_paths_data

    def calculate_skill_match(self, user_skills, career_requirements, user_domain, career_domain):
        """Calculate match percentage with domain consideration"""
        if not career_requirements:
            return 0
        
        # Domain match bonus
        domain_match_bonus = 1.2 if user_domain == career_domain else 1.0
        
        # Convert skills to text for simple comparison
        user_skills_text = " ".join([f"{skill['name']} {skill['proficiency']}" for skill in user_skills])
        career_skills_text = " ".join([f"{skill} {level}" for skill, level in career_requirements.items()])
        
        # Simple text-based similarity (removed embedding dependency)
        user_words = set(user_skills_text.lower().split())
        career_words = set(career_skills_text.lower().split())
        
        if not career_words:
            return 0
        
        # Calculate Jaccard similarity
        intersection = len(user_words.intersection(career_words))
        union = len(user_words.union(career_words))
        
        if union == 0:
            return 0
            
        similarity = intersection / union
        base_score = similarity * 100
        
        # Apply domain match bonus
        final_score = base_score * domain_match_bonus
        
        return min(final_score, 100)  # Cap at 100%

    def predict_career_paths(self, user_skills, user_domain, user_experience_years=2):
        """Predict suitable career paths based on domain"""
        recommendations = []
        
        for career in self.career_paths:
            # Only consider careers in the same domain or closely related
            career_domain = career.get('domain', '')
            
            match_percentage = self.calculate_skill_match(
                user_skills, 
                career.get('required_skills', {}),
                user_domain,
                career_domain
            )
            
            # Adjust match based on experience
            experience_match = self._calculate_experience_match(user_experience_years, career.get('experience_level', ''))
            adjusted_match = match_percentage * experience_match
            
            if adjusted_match > 15:  # Show paths with at least 15% match
                missing_skills = self._identify_missing_skills(user_skills, career.get('required_skills', {}))
                
                recommendations.append({
                    'career_path': career,
                    'match_percentage': round(adjusted_match, 1),
                    'missing_skills': missing_skills,
                    'estimated_salary': self._calculate_salary_estimate(career, user_experience_years),
                    'domain_match': user_domain == career_domain
                })
        
        # Sort by match percentage
        recommendations.sort(key=lambda x: x['match_percentage'], reverse=True)
        return recommendations[:6]  # Return top 6 recommendations

    def _calculate_experience_match(self, user_experience, required_level):
        """Calculate experience level match"""
        experience_mapping = {
            'entry': (0, 2),
            'mid': (2, 5),
            'senior': (5, 50)
        }
        
        if required_level.lower() in experience_mapping:
            min_exp, max_exp = experience_mapping[required_level.lower()]
            if min_exp <= user_experience <= max_exp:
                return 1.0
            elif user_experience < min_exp:
                return 0.7
            else:
                return 0.9
        return 0.8

    def _identify_missing_skills(self, user_skills, required_skills):
        """Identify skills user needs to develop"""
        missing = []
        user_skill_names = [skill['name'].lower() for skill in user_skills]
        
        for skill, level in required_skills.items():
            if skill.lower() not in user_skill_names:
                missing.append({
                    'skill': skill,
                    'required_level': level,
                    'current_level': 'None'
                })
        
        return missing

    def _calculate_salary_estimate(self, career, user_experience):
        """Calculate salary estimate based on career and experience"""
        base_min = career.get('average_salary_min', 50000)
        base_max = career.get('average_salary_max', 100000)
        
        # Adjust based on experience
        experience_multiplier = 1 + (user_experience * 0.08)  # 8% increase per year
        
        adjusted_min = int(base_min * experience_multiplier)
        adjusted_max = int(base_max * experience_multiplier)
        
        return {
            'min': adjusted_min,
            'max': adjusted_max,
            'currency': 'USD'
        }