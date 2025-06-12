from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, DecimalField, IntegerField, BooleanField, SubmitField, SelectMultipleField
from wtforms.validators import DataRequired, Email, Optional, NumberRange, Length, URL
from wtforms.widgets import CheckboxInput, ListWidget

class MultiCheckboxField(SelectMultipleField):
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()

class ExpertForm(FlaskForm):
    name = StringField('Expert Name', validators=[DataRequired(), Length(min=2, max=100)])
    expertise = StringField('Expertise', validators=[DataRequired(), Length(min=5, max=500)])
    bio = TextAreaField('Professional Bio', validators=[Optional(), Length(max=1000)])
    about = TextAreaField('Background/About', validators=[Optional(), Length(max=1000)])
    
    # Categories
    categories = MultiCheckboxField('Categories', coerce=int)
    
    # Contact Information
    contact = StringField('Email', validators=[Optional(), Email(), Length(max=100)])
    phone_number = StringField('Phone Number', validators=[Optional(), Length(max=20)])
    
    # Social Media Links
    portfolio_link = StringField('Portfolio URL', validators=[Optional(), URL(), Length(max=255)])
    linkedin_profile = StringField('LinkedIn Profile', validators=[Optional(), URL(), Length(max=255)])
    twitter_profile = StringField('Twitter/X Profile', validators=[Optional(), URL(), Length(max=255)])
    instagram_profile = StringField('Instagram Profile', validators=[Optional(), URL(), Length(max=255)])
    
    # Professional Details
    hourly_rate = DecimalField('Hourly Rate (₹)', validators=[Optional(), NumberRange(min=0, max=99999)])
    rating = DecimalField('Rating', validators=[Optional(), NumberRange(min=0, max=5)])
    reviews_count = IntegerField('Reviews Count', validators=[Optional(), NumberRange(min=0)])
    
    # Status
    is_available = BooleanField('Available for Consultation')
    is_verified = BooleanField('Verified Expert')
    
    # Profile Picture
    profile_picture = FileField('Profile Picture', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')
    ])
    
    submit = SubmitField('Save Expert')
