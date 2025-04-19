from flask import Blueprint, request, render_template, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app.forms import ResumeForm, ResumeSectionForm, ResumeSkillForm
from app.models import (
    create_resume, get_user_resumes, get_resume, update_resume, delete_resume,
    add_resume_section, add_resume_skill, generate_resume_summary, analyze_resume_ats,
    Resume, ResumeSection, ResumeBullet, ResumeSkill, advanced_ats_analyzer
)
import json
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from app import db
from app.forms import ResumeForm



resume_bp = Blueprint('resume', __name__, url_prefix='/resume')

@resume_bp.route('/')
@login_required
def resume_dashboard():
    """
    Resume builder dashboard showing all user resumes
    """
    resumes = get_user_resumes(current_user.id)
    return render_template('resume/dashboard.html', resumes=resumes)

@resume_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """
    Create a new resume
    """
    form = ResumeForm()
    
    if form.validate_on_submit():
        resume_id = create_resume(
            user_id=current_user.id,
            title=form.title.data,
            template=form.template.data
        )
        
        if resume_id:
            flash('Resume created successfully!', 'success')
            return redirect(url_for('resume.edit', resume_id=resume_id))
        else:
            flash('Error creating resume. Please try again.', 'danger')
    
    # Check for validation errors
    if form.errors:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in {field}: {error}", 'danger')
    
    return render_template('resume/create.html', form=form)

@resume_bp.route('/<int:resume_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(resume_id):
    """
    Edit a resume
    """
    resume = get_resume(resume_id, current_user.id)
    if not resume:
        flash('Resume not found.', 'danger')
        return redirect(url_for('resume.resume_dashboard'))
    
    form = ResumeForm(obj=resume)
    
    if form.validate_on_submit():
        update_data = {
            'title': form.title.data,
            'template': form.template.data,
            'objective': form.objective.data,
            'primary_color': form.primary_color.data,
            'secondary_color': form.secondary_color.data,
            'font_family': form.font_family.data
        }
        
        if update_resume(resume_id, current_user.id, update_data):
            flash('Resume updated successfully!', 'success')
            return redirect(url_for('resume.edit', resume_id=resume_id))
        else:
            flash('Error updating resume. Please try again.', 'danger')
    
    # Get sections and skills for this resume
    sections = ResumeSection.query.filter_by(resume_id=resume_id).order_by(ResumeSection.order, ResumeSection.id).all()
    skills = ResumeSkill.query.filter_by(resume_id=resume_id).order_by(ResumeSkill.category, ResumeSkill.order).all()
    
    # Organize sections by type
    section_types = {}
    for section in sections:
        section_type = section.type
        if section_type not in section_types:
            section_types[section_type] = []
        section_types[section_type].append(section)
    
    # Group skills by category
    skill_categories = {}
    for skill in skills:
        category = skill.category or 'Other'
        if category not in skill_categories:
            skill_categories[category] = []
        skill_categories[category].append(skill)
    
    return render_template(
        'resume/edit.html', 
        resume=resume, 
        form=form, 
        section_types=section_types,
        skill_categories=skill_categories
    )

@resume_bp.route('/<int:resume_id>/view')
@login_required
def view(resume_id):
    """
    View a resume in preview mode
    """
    resume = get_resume(resume_id, current_user.id)
    if not resume:
        flash('Resume not found.', 'danger')
        return redirect(url_for('resume.resume_dashboard'))
    
    # Get sections and skills for this resume
    sections = ResumeSection.query.filter_by(resume_id=resume_id).order_by(ResumeSection.order, ResumeSection.id).all()
    skills = ResumeSkill.query.filter_by(resume_id=resume_id).order_by(ResumeSkill.category, ResumeSkill.order).all()
    
    # Organize sections by type
    section_types = {}
    for section in sections:
        section_type = section.type
        if section_type not in section_types:
            section_types[section_type] = []
        section_types[section_type].append(section)
    
    # Group skills by category
    skill_categories = {}
    for skill in skills:
        category = skill.category or 'Other'
        if category not in skill_categories:
            skill_categories[category] = []
        skill_categories[category].append(skill)
    
    template_path = f'resume/templates/{resume.template}.html'
    return render_template(
        template_path, 
        resume=resume, 
        user=current_user,
        section_types=section_types,
        skill_categories=skill_categories
    )

@resume_bp.route('/<int:resume_id>/delete', methods=['POST'])
@login_required
def delete(resume_id):
    """
    Delete a resume
    """
    if delete_resume(resume_id, current_user.id):
        flash('Resume deleted successfully!', 'success')
    else:
        flash('Error deleting resume. Please try again.', 'danger')
    
    return redirect(url_for('resume.resume_dashboard'))

@resume_bp.route('/<int:resume_id>/add-section', methods=['GET', 'POST'])
@login_required
def add_section(resume_id):
    """
    Add a section to a resume
    """
    resume = get_resume(resume_id, current_user.id)
    if not resume:
        flash('Resume not found.', 'danger')
        return redirect(url_for('resume.resume_dashboard'))
    
    form = ResumeSectionForm()
    
    if form.validate_on_submit():
        section_data = {
            'type': form.section_type.data,
            'title': form.title.data,
            'organization': form.organization.data,
            'location': form.location.data,
            'start_date': form.start_date.data,
            'end_date': form.end_date.data if not form.is_current.data else None,
            'is_current': form.is_current.data,
            'description': form.description.data,
            'bullets': form.bullets.data.split('\n') if form.bullets.data else []
        }
        
        section_id = add_resume_section(resume_id, current_user.id, section_data)
        
        if section_id:
            flash('Section added successfully!', 'success')
            return redirect(url_for('resume.edit', resume_id=resume_id))
        else:
            flash('Error adding section. Please try again.', 'danger')
    
    return render_template('resume/add_section.html', resume=resume, form=form)

@resume_bp.route('/<int:resume_id>/add-skill', methods=['GET', 'POST'])
@login_required
def add_skill(resume_id):
    """
    Add a skill to a resume
    """
    resume = get_resume(resume_id, current_user.id)
    if not resume:
        flash('Resume not found.', 'danger')
        return redirect(url_for('resume.resume_dashboard'))
    
    form = ResumeSkillForm()
    
    if form.validate_on_submit():
        skill_data = {
            'skill_name': form.skill_name.data,
            'category': form.category.data,
            'proficiency': form.proficiency.data
        }
        
        skill_id = add_resume_skill(resume_id, current_user.id, skill_data)
        
        if skill_id:
            flash('Skill added successfully!', 'success')
            return redirect(url_for('resume.edit', resume_id=resume_id))
        else:
            flash('Error adding skill. Please try again.', 'danger')
    
    return render_template('resume/add_skill.html', resume=resume, form=form)

@resume_bp.route('/<int:resume_id>/generate-summary', methods=['POST'])
@login_required
def generate_summary(resume_id):
    """
    Generate an AI-powered summary for a resume
    """
    if generate_resume_summary(resume_id, current_user.id):
        flash('Resume summary generated successfully!', 'success')
    else:
        flash('Error generating resume summary. Please try again.', 'danger')
    
    return redirect(url_for('resume.edit', resume_id=resume_id))

@resume_bp.route('/<int:resume_id>/analyze', methods=['GET', 'POST'])
@login_required
def analyze(resume_id):
    """
    Analyze a resume against ATS systems
    """
    resume = get_resume(resume_id, current_user.id)
    if not resume:
        flash('Resume not found.', 'danger')
        return redirect(url_for('resume.resume_dashboard'))
    
    job_description = request.form.get('job_description', None)
    industry = request.form.get('industry', None)
    company_size = request.form.get('company_size', None)
    
    # Determine whether to use advanced analysis or basic analysis
    use_advanced = request.form.get('analysis_type') == 'advanced'
    
    if use_advanced:
        # Use advanced ATS analyzer
        result = advanced_ats_analyzer(resume_id, current_user.id, job_description, industry, company_size)
        
        if result:
            return render_template(
                'resume/analysis.html',
                resume=resume,
                score=result['score'],
                feedback=result['metrics']['overall_feedback'],
                job_description=job_description,
                industry=industry,
                company_size=company_size,
                
                # Add all metrics for the template
                contact_score=result['metrics']['contact_score'],
                experience_score=result['metrics']['experience_score'],
                education_score=result['metrics']['education_score'],
                skills_score=result['metrics']['skills_score'],
                extracted_keywords=result['metrics']['extracted_keywords'],
                found_keywords=result['metrics']['found_keywords'],
                
                # Additional metrics for advanced analysis
                content_score=result['metrics']['content_score'],
                keyword_score=result['metrics']['keyword_score'],
                impact_score=result['metrics']['impact_score'],
                format_score=result['metrics']['format_score'],
                action_verb_usage=result['metrics']['action_verb_usage'],
                quantification_score=result['metrics']['quantification_score'],
                achievement_focus=result['metrics']['achievement_focus'],
                readability_score=result['metrics']['readability_score'],
                section_feedback=result['metrics']['section_feedback'],
                improvement_suggestions=result['metrics']['improvement_suggestions'],
                ats_optimization_tips=result['metrics']['ats_optimization_tips'],
                is_advanced=True
            )
        else:
            flash('Error analyzing resume. Please try again.', 'danger')
            return redirect(url_for('resume.edit', resume_id=resume_id))
    else:
        # Use standard ATS analyzer
        result = analyze_resume_ats(resume_id, current_user.id, job_description)
        
        if result:
            # Calculate section scores - these were missing
            contact_score = 85  # Default value or calculate based on user profile completeness
            
            # Get sections for this resume to calculate section scores
            sections = ResumeSection.query.filter_by(resume_id=resume_id).all()
            skills = ResumeSkill.query.filter_by(resume_id=resume_id).all()
            
            # Calculate experience score
            experience_sections = [s for s in sections if s.type == 'experience']
            experience_score = 80 if experience_sections else 30
            
            # Calculate education score
            education_sections = [s for s in sections if s.type == 'education']
            education_score = 80 if education_sections else 30
            
            # Calculate skills score
            skills_score = min(90, len(skills) * 10) if skills else 30
            
            # If job description is provided, extract keywords
            extracted_keywords = []
            found_keywords = []
            
            if job_description:
                # Extract keywords from job description (simple implementation)
                common_keywords = [
                    'Python', 'Java', 'JavaScript', 'C++', 'HTML', 'CSS', 'SQL', 'React',
                    'management', 'leadership', 'communication', 'teamwork', 'problem-solving'
                ]
                
                # Simple keyword extraction - in a real app, use NLP
                for keyword in common_keywords:
                    if keyword.lower() in job_description.lower():
                        extracted_keywords.append(keyword)
                        
                        # Check if keyword is in resume content
                        skill_names = [skill.skill_name.lower() for skill in skills]
                        if keyword.lower() in skill_names:
                            found_keywords.append(keyword)
            
            return render_template(
                'resume/analysis.html', 
                resume=resume, 
                score=result['score'], 
                feedback=result['feedback'],
                job_description=job_description,
                # Add missing variables
                contact_score=contact_score,
                experience_score=experience_score,
                education_score=education_score,
                skills_score=skills_score,
                extracted_keywords=extracted_keywords,
                found_keywords=found_keywords,
                is_advanced=False
            )
        else:
            flash('Error analyzing resume. Please try again.', 'danger')
            return redirect(url_for('resume.edit', resume_id=resume_id))
        


def analyze_resume_ats(resume_id, user_id, job_description=None):
    """
    Analyze a resume against ATS systems and potentially a job description
    """
    try:
        resume = get_resume(resume_id, user_id)
        if not resume:
            return None
            
        # Get resume sections and skills
        sections = ResumeSection.query.filter_by(resume_id=resume_id).all()
        skills = ResumeSkill.query.filter_by(resume_id=resume_id).all()
        
        # Basic checks - these would be more sophisticated in a real implementation
        has_contact = True  # Assume user profile has contact info
        has_experience = any(section.type == 'experience' for section in sections)
        has_education = any(section.type == 'education' for section in sections)
        has_skills = len(skills) > 0
        bullet_count = sum(len(section.bullets) for section in sections)
        has_enough_bullets = bullet_count >= 5
        
        # Calculate basic ATS score - this would be more sophisticated in reality
        base_score = 0
        if has_contact: base_score += 20
        if has_experience: base_score += 25
        if has_education: base_score += 20
        if has_skills: base_score += 15
        if has_enough_bullets: base_score += 20
        
        # Calculate more sophisticated score if job description is provided
        job_match_score = 0
        feedback = []
        
        if job_description:
            # This simulates keyword matching - in a real implementation, 
            # you'd use more sophisticated NLP
            job_description = job_description.lower()
            skill_matches = 0
            
            for skill in skills:
                if skill.skill_name.lower() in job_description:
                    skill_matches += 1
            
            # Calculate match percentage
            if skills:
                match_percentage = (skill_matches / len(skills)) * 100
                job_match_score = min(30, match_percentage * 0.3)  # Max 30 points from keyword matching
            
            # Add feedback based on analysis
            if skill_matches < len(skills) * 0.3:
                feedback.append("Your skills don't strongly match the job description. Consider adding more relevant skills.")
            
            if not has_experience:
                feedback.append("Add professional experience to improve your resume's strength.")
            
            if bullet_count < 10:
                feedback.append("Add more bullet points to detail your experiences.")
        else:
            # General feedback without job description
            if not has_experience:
                feedback.append("Add professional experience to improve your resume's strength.")
            
            if not has_education:
                feedback.append("Add your educational background.")
                
            if not has_skills:
                feedback.append("Add your technical and soft skills.")
                
            if bullet_count < 5:
                feedback.append("Add more details to your experiences with bullet points.")
        
        # Calculate final score
        final_score = min(100, base_score + job_match_score)
        
        # Update resume with score and feedback
        resume.ats_score = final_score
        resume.feedback = "\n".join(feedback) if feedback else "Your resume meets basic ATS requirements."
        db.session.commit()
        
        return {
            'score': final_score,
            'feedback': resume.feedback
        }
    except Exception as e:
        print(f"Error analyzing resume: {type(e).__name__} - {str(e)}")
        db.session.rollback()
        return None
@resume_bp.route('/<int:resume_id>/advanced-analyze', methods=['GET', 'POST'])
@login_required
def advanced_analyze(resume_id):
    """
    Perform advanced ATS analysis on a resume
    """
    resume = get_resume(resume_id, current_user.id)
    if not resume:
        flash('Resume not found.', 'danger')
        return redirect(url_for('resume.resume_dashboard'))
    
    # Get form data
    job_description = request.form.get('job_description', None)
    industry = request.form.get('industry', None)
    company_size = request.form.get('company_size', None)
    
    # Perform advanced analysis
    result = advanced_ats_analyzer(resume_id, current_user.id, job_description, industry, company_size)
    
    if result:
        return render_template(
            'resume/advanced_analysis.html', 
            resume=resume, 
            score=result['score'], 
            metrics=result['metrics'],
            feedback=result['feedback'],
            job_description=job_description,
            industry=industry,
            company_size=company_size
        )
    else:
        flash('Error analyzing resume. Please try again.', 'danger')
        return redirect(url_for('resume.edit', resume_id=resume_id))


@resume_bp.route('/<int:resume_id>/export', methods=['GET'])
@login_required
def export(resume_id):
    """
    Export a resume to PDF
    """
    resume = get_resume(resume_id, current_user.id)
    if not resume:
        flash('Resume not found.', 'danger')
        return redirect(url_for('resume.resume_dashboard'))
    
    # In a real implementation, you would generate a PDF here
    # For now, we'll just redirect to the view page
    flash('PDF export functionality will be available soon!', 'info')
    return redirect(url_for('resume.view', resume_id=resume_id))

@resume_bp.route('/<int:resume_id>/make-primary', methods=['POST'])
@login_required
def make_primary(resume_id):
    """
    Set a resume as the primary resume
    """
    resume = get_resume(resume_id, current_user.id)
    if not resume:
        flash('Resume not found.', 'danger')
        return redirect(url_for('resume.resume_dashboard'))
    
    # Clear existing primary flag
    Resume.query.filter_by(user_id=current_user.id).update({'is_primary': False})
    
    # Set this resume as primary
    resume.is_primary = True
    db.session.commit()
    
    flash('Primary resume updated successfully!', 'success')
    return redirect(url_for('resume.resume_dashboard'))

@resume_bp.route('/<int:resume_id>/import-from-linkedin', methods=['POST'])
@login_required
def import_from_linkedin(resume_id):
    """
    Import data from LinkedIn
    """
    resume = get_resume(resume_id, current_user.id)
    if not resume:
        flash('Resume not found.', 'danger')
        return redirect(url_for('resume.resume_dashboard'))
    
    # In a real implementation, you would integrate with LinkedIn API
    flash('LinkedIn import functionality will be available soon!', 'info')
    return redirect(url_for('resume.edit', resume_id=resume_id))

@resume_bp.route('/templates')
@login_required
def templates():
    """
    View available resume templates
    """
    form = ResumeForm()
    templates = [
        {
            'id': 'modern',
            'name': 'Modern',
            'description': 'A clean, modern design with a focus on readability.',
            'image': 'modern.png'
        },
        {
            'id': 'professional',
            'name': 'Professional',
            'description': 'A traditional design suited for corporate roles.',
            'image': 'professional.png'
        },
        {
            'id': 'creative',
            'name': 'Creative',
            'description': 'A bold design for creative roles.',
            'image': 'creative.png'
        },
        {
            'id': 'minimal',
            'name': 'Minimal',
            'description': 'A minimalist design with a focus on content.',
            'image': 'minimal.png'
        },
        {
            'id': 'tech',
            'name': 'Tech',
            'description': 'A design suited for technical roles.',
            'image': 'tech.png'
        }
    ]
    
    return render_template('resume/templates.html', templates=templates, form=form)

@resume_bp.route('/api/section/<int:section_id>/update-order', methods=['POST'])
@login_required
def update_section_order(section_id):
    """
    Update the order of a section
    """
    section = ResumeSection.query.get(section_id)
    if not section:
        return jsonify({'success': False, 'message': 'Section not found.'}), 404
    
    # Verify owner
    resume = Resume.query.get(section.resume_id)
    if resume.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Not authorized.'}), 403
    
    new_order = request.json.get('order')
    if new_order is None:
        return jsonify({'success': False, 'message': 'Order not provided.'}), 400
    
    section.order = new_order
    db.session.commit()
    
    return jsonify({'success': True})

@resume_bp.route('/api/section/<int:section_id>', methods=['DELETE'])
@login_required
def delete_section(section_id):
    """
    Delete a section
    """
    section = ResumeSection.query.get(section_id)
    if not section:
        return jsonify({'success': False, 'message': 'Section not found.'}), 404
    
    # Verify owner
    resume = Resume.query.get(section.resume_id)
    if resume.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Not authorized.'}), 403
    
    db.session.delete(section)
    db.session.commit()
    
    return jsonify({'success': True})

@resume_bp.route('/api/bullet/<int:bullet_id>', methods=['DELETE'])
@login_required
def delete_bullet(bullet_id):
    """
    Delete a bullet point
    """
    bullet = ResumeBullet.query.get(bullet_id)
    if not bullet:
        return jsonify({'success': False, 'message': 'Bullet not found.'}), 404
    
    # Verify owner by traversing relationships
    section = ResumeSection.query.get(bullet.section_id)
    resume = Resume.query.get(section.resume_id)
    if resume.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Not authorized.'}), 403
    
    db.session.delete(bullet)
    db.session.commit()
    
    return jsonify({'success': True})

@resume_bp.route('/api/skill/<int:skill_id>', methods=['DELETE'])
@login_required
def delete_skill(skill_id):
    """
    Delete a skill
    """
    skill = ResumeSkill.query.get(skill_id)
    if not skill:
        return jsonify({'success': False, 'message': 'Skill not found.'}), 404
    
    # Verify owner
    resume = Resume.query.get(skill.resume_id)
    if resume.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Not authorized.'}), 403
    
    db.session.delete(skill)
    db.session.commit()
    
    return jsonify({'success': True})

@resume_bp.route('/api/bullet/<int:bullet_id>/enhance', methods=['POST'])
@login_required
def enhance_bullet(bullet_id):
    """
    Enhance a bullet point with AI suggestions
    """
    bullet = ResumeBullet.query.get(bullet_id)
    if not bullet:
        return jsonify({'success': False, 'message': 'Bullet not found.'}), 404
    
    # Verify owner by traversing relationships
    section = ResumeSection.query.get(bullet.section_id)
    resume = Resume.query.get(section.resume_id)
    if resume.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Not authorized.'}), 403
    
    # Current content for reference
    current_content = bullet.content
    
    # AI enhancement function call
    enhanced_content = improve_bullet_point(current_content)
    
    # Also update the bullet in the database
    bullet.content = enhanced_content
    db.session.commit()
    
    # Return the enhanced content
    return jsonify({
        'success': True, 
        'original': current_content,
        'enhanced': enhanced_content
    })

@resume_bp.route('/api/section/<int:section_id>/suggest-bullets', methods=['POST'])
@login_required
def suggest_bullets(section_id):
    """
    Suggest bullet points for a section based on its content
    """
    section = ResumeSection.query.get(section_id)
    if not section:
        return jsonify({'success': False, 'message': 'Section not found.'}), 404
    
    # Verify owner
    resume = Resume.query.get(section.resume_id)
    if resume.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Not authorized.'}), 403
    
    # For AI suggestions, we need context
    context = {
        'title': section.title,
        'organization': section.organization,
        'description': section.description,
        'type': section.type,
        'existing_bullets': [bullet.content for bullet in section.bullets]
    }
    
    # In a real implementation, you would call an AI service here
    # For now, we'll simulate AI suggestions
    suggested_bullets = generate_bullet_suggestions(context)
    
    return jsonify({
        'success': True,
        'suggestions': suggested_bullets
    })

@resume_bp.route('/api/resume/<int:resume_id>/keywords', methods=['POST'])
@login_required
def extract_keywords(resume_id):
    """
    Extract keywords from a job description for resume optimization
    """
    resume = get_resume(resume_id, current_user.id)
    if not resume:
        return jsonify({'success': False, 'message': 'Resume not found.'}), 404
    
    job_description = request.json.get('job_description')
    if not job_description:
        return jsonify({'success': False, 'message': 'Job description not provided.'}), 400
    
    # In a real implementation, you would use NLP to extract relevant keywords
    # For now, we'll simulate keyword extraction
    keywords = extract_job_keywords(job_description)
    
    return jsonify({
        'success': True,
        'keywords': keywords
    })

# Helper functions for AI-powered features

def improve_bullet_point(bullet_text):
    """
    Enhance a bullet point to be more impactful
    """
    # Simple rule-based improvements
    bullet = bullet_text.strip()
    
    # Add action verb at beginning if not present
    action_verbs = ['Developed', 'Implemented', 'Created', 'Managed', 'Led', 'Designed', 
                    'Coordinated', 'Achieved', 'Improved', 'Increased', 'Reduced']
    
    words = bullet.split()
    if not words:
        return "Accomplished significant improvements in efficiency and effectiveness"
    
    if words[0] not in action_verbs:
        # Add random action verb
        import random
        bullet = f"{random.choice(action_verbs)} {bullet[0].lower() + bullet[1:]}"
    
    # Add quantifiable result if not present
    if not any(x in bullet.lower() for x in ['%', 'percent', 'increased', 'decreased', 'reduced', 'improved']):
        if not bullet.endswith('.'):
            bullet += ','
        bullet += " resulting in a 15% improvement in efficiency"
    
    return bullet

def generate_bullet_suggestions(context):
    """
    Generate bullet point suggestions based on section context
    This is a placeholder for actual AI implementation
    """
    title = context.get('title', '').lower()
    org = context.get('organization', '').lower()
    section_type = context.get('type', '').lower()
    
    suggestions = []
    
    if section_type == 'experience':
        suggestions = [
            f"Developed innovative solutions for {org} that increased efficiency by 20%",
            f"Led a team of 5 members to successfully complete projects under tight deadlines",
            f"Implemented new processes that reduced operational costs by 15%",
            f"Collaborated with cross-functional teams to improve product quality and user satisfaction",
            f"Created comprehensive documentation that streamlined onboarding processes"
        ]
    elif section_type == 'education':
        suggestions = [
            f"Achieved GPA of 3.8 while participating in extracurricular activities",
            f"Conducted research on emerging technologies and presented findings at conferences",
            f"Completed capstone project focused on innovative solutions in the industry",
            f"Elected as student representative to facilitate communication between students and faculty",
            f"Organized study groups that improved average test scores by 10%"
        ]
    elif section_type == 'project':
        suggestions = [
            f"Designed and implemented a scalable architecture that improved system performance by 30%",
            f"Utilized agile methodologies to ensure on-time delivery and high-quality results",
            f"Created user-friendly interfaces that received positive feedback from stakeholders",
            f"Integrated third-party APIs to enhance functionality and streamline operations",
            f"Performed thorough testing to identify and resolve potential issues before deployment"
        ]
    
    return suggestions

def extract_job_keywords(job_description):
    """
    Extract relevant keywords from a job description
    This is a placeholder for actual NLP implementation
    """
    # For now, we'll just look for some common skill keywords
    common_skills = [
        'Python', 'Java', 'JavaScript', 'C++', 'HTML', 'CSS', 'SQL', 'React', 'Angular', 'Vue',
        'Node.js', 'Django', 'Flask', 'Spring', 'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes',
        'Machine Learning', 'Data Analysis', 'Project Management', 'Agile', 'Scrum', 'Leadership',
        'Communication', 'Problem Solving', 'Critical Thinking', 'Teamwork', 'Creativity'
    ]
    
    found_keywords = []
    job_desc_lower = job_description.lower()
    
    for skill in common_skills:
        if skill.lower() in job_desc_lower:
            found_keywords.append(skill)
    
    # Add some role-specific keywords
    if 'manager' in job_desc_lower or 'management' in job_desc_lower:
        found_keywords.extend(['Leadership', 'Team Management', 'Strategic Planning'])
    
    if 'developer' in job_desc_lower or 'engineer' in job_desc_lower:
        found_keywords.extend(['Software Development', 'Code Review', 'Debugging'])
    
    if 'data' in job_desc_lower and ('analyst' in job_desc_lower or 'scientist' in job_desc_lower):
        found_keywords.extend(['Data Visualization', 'Statistical Analysis', 'SQL'])
    
    return list(set(found_keywords))  # Remove duplicates