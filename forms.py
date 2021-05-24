from flask_wtf import FlaskForm
from wtforms.validators import DataRequired , Length , NumberRange , EqualTo , ValidationError
from wtforms import DecimalField , IntegerField , SubmitField

class SettingsForm(FlaskForm) :
    lowConThresh = DecimalField(
        'Low Contrast Threshold (Recommended - 0.35)' ,
        validators = [DataRequired() , NumberRange(min=0.2 , max=0.5)]
    )

    earFramePipeline = IntegerField(
        'Max EAR Frame Threshold (Recommended - 30-40)' ,
        validators = [DataRequired() , NumberRange(min=15 , max=60)]
    )

    divFrameThresh = IntegerField(
        'Diversion Frame Threshold (Recommended - 30-40)' ,
        validators = [DataRequired() , NumberRange(min=15 , max=60)]
    )

    restAlertThresh = IntegerField(
        'Rest Alert Threshold  (Recommended - 4)' ,
        validators = [DataRequired() , NumberRange(min=3 , max=10)]
    )

    restAlertFrameThresh = IntegerField(
        'Rest Alert Frame Threshold  (Recommended - 50)' ,
        validators = [DataRequired() , NumberRange(min=40 , max=100)]
    )

    submit = SubmitField('Save Changes')